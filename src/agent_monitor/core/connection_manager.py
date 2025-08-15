import json
import logging
from typing import Any, Dict, Set

from fastapi import WebSocket, WebSocketDisconnect


class ConnectionManager:
    def __init__(self, conversation_id: str) -> None:
        self.conversation_id = conversation_id
        self.active_connections: Set[WebSocket] = set()
        self.logger = logging.getLogger(__name__)

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.add(websocket)
        self.logger.info(
            f"Connected websocket to conversation {self.conversation_id}, total connections: {len(self.active_connections)}"
        )

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.discard(websocket)
        remaining = len(self.active_connections)
        self.logger.info(
            f"Disconnected websocket from conversation {self.conversation_id}, remaining connections: {remaining}"
        )

    async def send_message(self, data: Dict[str, Any]) -> None:
        message = json.dumps(data, ensure_ascii=False)
        disconnected = set()
        for websocket in self.active_connections:
            try:
                await websocket.send_text(message)
            except (WebSocketDisconnect, ConnectionResetError, Exception) as e:
                self.logger.warning(
                    f"Failed to send message to websocket in conversation {self.conversation_id}: {type(e).__name__}: {e}"
                )
                disconnected.add(websocket)

        for websocket in disconnected:
            self.disconnect(websocket)
        if disconnected:
            self.logger.info(
                f"Removed {len(disconnected)} disconnected websockets from conversation {self.conversation_id}, remaining connections: {len(self.active_connections)}"
            )
