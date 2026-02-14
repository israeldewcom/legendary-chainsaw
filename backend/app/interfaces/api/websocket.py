from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Set
import json
import asyncio
from app.infrastructure.cache.redis import redis_client
from app.interfaces.api.dependencies import get_current_user_ws
import structlog

logger = structlog.get_logger()

router = APIRouter()

# Simple connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, user_id: int, message: dict):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass

manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Authentication via token in query param
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return
    # Validate token
    from app.infrastructure.auth.jwt import JWTTokenService
    token_service = JWTTokenService()
    try:
        payload = token_service.verify_token(token)
        user_id = payload.get("sub")
        if not user_id:
            await websocket.close(code=1008)
            return
    except:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, user_id)
    try:
        # Subscribe to user-specific Redis channel for real-time events
        pubsub = redis_client.client.pubsub()
        await pubsub.subscribe(f"user:{user_id}")
        asyncio.create_task(forward_redis_to_websocket(pubsub, websocket, user_id))

        while True:
            # Receive messages from client (if needed)
            data = await websocket.receive_text()
            # Handle client messages if any
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    finally:
        await pubsub.unsubscribe(f"user:{user_id}")
        await pubsub.close()


async def forward_redis_to_websocket(pubsub, websocket: WebSocket, user_id: int):
    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message:
                data = json.loads(message["data"])
                await websocket.send_json(data)
            await asyncio.sleep(0.01)
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.exception("Websocket forward error", user_id=user_id, error=e)
