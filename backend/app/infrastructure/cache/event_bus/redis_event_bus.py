from typing import Dict, List, Callable, Any, Type
import json
import asyncio
from redis.asyncio import Redis
from app.infrastructure.cache.redis import redis_client
from app.domain.events.domain_events import DomainEvent
import structlog

logger = structlog.get_logger()


class RedisEventBus:
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
        self._pubsub = None
        self._listener_task = None

    async def init(self):
        self._pubsub = redis_client.client.pubsub()
        # No subscriptions yet; we can subscribe to channels dynamically
        self._listener_task = asyncio.create_task(self._listen())
        logger.info("Redis event bus initialized")

    async def close(self):
        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass
        if self._pubsub:
            await self._pubsub.close()
        logger.info("Redis event bus closed")

    async def publish(self, event: DomainEvent):
        event_type = event.__class__.__name__
        channel = f"events:{event_type}"
        message = json.dumps({
            "type": event_type,
            "data": self._event_to_dict(event),
        })
        await redis_client.client.publish(channel, message)
        logger.debug("Event published", channel=channel, event=event_type)

    def subscribe(self, event_class: Type[DomainEvent], handler: Callable):
        event_type = event_class.__name__
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

        # Subscribe to channel if not already
        if self._pubsub:
            channel = f"events:{event_type}"
            self._pubsub.subscribe(channel)

    async def _listen(self):
        while True:
            try:
                message = await self._pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message:
                    await self._handle_message(message)
                await asyncio.sleep(0.01)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Event bus listener error", error=e)

    async def _handle_message(self, message):
        channel = message["channel"].decode()
        data = json.loads(message["data"])
        event_type = data["type"]
        handlers = self._handlers.get(event_type, [])
        for handler in handlers:
            try:
                event = self._dict_to_event(event_type, data["data"])
                asyncio.create_task(handler(event))
            except Exception as e:
                logger.exception("Event handler failed", event_type=event_type, error=e)

    def _event_to_dict(self, event: DomainEvent) -> dict:
        # Convert event to dict (could use dataclasses.asdict)
        import dataclasses
        return dataclasses.asdict(event)

    def _dict_to_event(self, event_type: str, data: dict) -> DomainEvent:
        # Dynamically import event classes
        import app.domain.events.domain_events as events
        event_class = getattr(events, event_type)
        return event_class(**data)
