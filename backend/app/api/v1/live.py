import uuid

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from jose import JWTError

from app.core.security import decode_token
from app.ws.manager import manager

router = APIRouter()


@router.websocket("/ws/live")
async def live_rover_feed(websocket: WebSocket, token: str = Query(...)):
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise JWTError("wrong token type")
        farmer_id = uuid.UUID(payload["sub"])
    except (JWTError, ValueError, KeyError):
        await websocket.close(code=4401)
        return

    await manager.connect(farmer_id, websocket)
    try:
        while True:
            await websocket.receive_text()  # client doesn't need to send anything; keeps connection open
    except WebSocketDisconnect:
        await manager.disconnect(farmer_id, websocket)
