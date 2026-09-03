from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from jose import JWTError, jwt
from app.config import settings
from app.services.notification_service import manager

router = APIRouter()


@router.websocket("/notifications")
async def ws_notifications(
    websocket: WebSocket,
    token: str = Query(default=""),
):
    # Validate token (simplified — no DB lookup for WebSocket)
    if token:
        try:
            jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        except JWTError:
            await websocket.close(code=4001)
            return

    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive; client can send pings
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
