from redis.asyncio import Redis, ConnectionPool
from typing import Optional, Any
from app.config import settings
import json
import structlog

logger = structlog.get_logger()


class RedisClient:
    def __init__(self):
        self._pool: Optional[ConnectionPool] = None
        self._client: Optional[Redis] = None

    async def initialize(self):
        self._pool = ConnectionPool.from_url(
            str(settings.REDIS_URL),
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            decode_responses=True,
        )
        self._client = Redis(connection_pool=self._pool)
        logger.info("Redis client initialized")

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None
        if self._pool:
            await self._pool.disconnect()
            self._pool = None
        logger.info("Redis client closed")

    @property
    def client(self) -> Redis:
        if self._client is None:
            raise Exception("Redis client not initialized")
        return self._client

    async def get(self, key: str) -> Optional[Any]:
        value = await self.client.get(key)
        if value:
            try:
                return json.loads(value)
            except:
                return value
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        if ttl:
            await self.client.setex(key, ttl, value)
        else:
            await self.client.set(key, value)

    async def delete(self, key: str) -> None:
        await self.client.delete(key)

    async def exists(self, key: str) -> bool:
        return await self.client.exists(key) > 0

    async def incr(self, key: str) -> int:
        return await self.client.incr(key)

    async def expire(self, key: str, ttl: int) -> None:
        await self.client.expire(key, ttl)


redis_client = RedisClient()
