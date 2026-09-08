import asyncio
import uuid

from fastapi import WebSocket


class ConnectionManager:
    """Broadcasts live rover state to every farmer session subscribed for that farmer."""

    def __init__(self) -> None:
        self._connections: dict[uuid.UUID, list[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, farmer_id: uuid.UUID, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections.setdefault(farmer_id, []).append(websocket)

    async def disconnect(self, farmer_id: uuid.UUID, websocket: WebSocket) -> None:
        async with self._lock:
            conns = self._connections.get(farmer_id, [])
            if websocket in conns:
                conns.remove(websocket)
            if not conns and farmer_id in self._connections:
                del self._connections[farmer_id]

    async def broadcast(self, farmer_id: uuid.UUID, message: dict) -> None:
        async with self._lock:
            conns = list(self._connections.get(farmer_id, []))
        for ws in conns:
            try:
                await ws.send_json(message)
            except Exception:
                await self.disconnect(farmer_id, ws)


manager = ConnectionManager()
