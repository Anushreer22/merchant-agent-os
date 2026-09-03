import asyncio
import json
import logging
from typing import Any
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self._connections: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self._connections.append(ws)

    def disconnect(self, ws: WebSocket):
        self._connections = [c for c in self._connections if c is not ws]

    async def broadcast(self, message: dict[str, Any]):
        dead = []
        for ws in self._connections:
            try:
                await ws.send_text(json.dumps(message))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


manager = ConnectionManager()


def notify(message: dict[str, Any]):
    """Fire-and-forget broadcast from sync code."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(manager.broadcast(message))
        else:
            loop.run_until_complete(manager.broadcast(message))
    except Exception as exc:
        logger.debug("Notification broadcast skipped: %s", exc)
