from fastapi import WebSocket
from typing import Dict, List
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections per workflow_id."""

    def __init__(self):
        self.active: Dict[str, List[WebSocket]] = {}

    async def connect(self, workflow_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active.setdefault(workflow_id, []).append(websocket)

    def disconnect(self, workflow_id: str, websocket: WebSocket):
        if workflow_id in self.active:
            self.active[workflow_id] = [
                ws for ws in self.active[workflow_id] if ws != websocket
            ]

    async def broadcast(self, workflow_id: str, payload: dict):
        """Send a JSON message to all clients watching this workflow."""
        connections = self.active.get(workflow_id, [])
        dead = []
        for ws in connections:
            try:
                await ws.send_text(json.dumps(payload))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(workflow_id, ws)


manager = ConnectionManager()
