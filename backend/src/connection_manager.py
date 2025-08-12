import json
import logging
from typing import Any, Dict, Set

from fastapi import WebSocket, WebSocketDisconnect


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.global_connections: Set[WebSocket] = set()
        self.logger = logging.getLogger(__name__)

    async def connect(self, websocket: WebSocket, conversation_id: str) -> None:
        await websocket.accept()
        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = set()
        self.active_connections[conversation_id].add(websocket)
        self.logger.info(
            f"Connected websocket to conversation {conversation_id}, total connections: {len(self.active_connections[conversation_id])}"
        )

    def disconnect(self, websocket: WebSocket, conversation_id: str) -> None:
        if conversation_id in self.active_connections:
            self.active_connections[conversation_id].discard(websocket)
            remaining = len(self.active_connections[conversation_id])
            if not self.active_connections[conversation_id]:
                del self.active_connections[conversation_id]
                self.logger.info(f"Disconnected last websocket from conversation {conversation_id}")
            else:
                self.logger.info(
                    f"Disconnected websocket from conversation {conversation_id}, remaining connections: {remaining}"
                )

    async def connect_global(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.global_connections.add(websocket)
        self.logger.info(f"Connected global websocket, total global connections: {len(self.global_connections)}")

    def disconnect_global(self, websocket: WebSocket) -> None:
        self.global_connections.discard(websocket)
        self.logger.info(f"Disconnected global websocket, remaining global connections: {len(self.global_connections)}")

    async def send_message_for_conversation(self, conversation_id: str, data: Dict[str, Any]) -> None:
        if conversation_id in self.active_connections:
            message = json.dumps(data, ensure_ascii=False)
            disconnected = set()
            for websocket in self.active_connections[conversation_id]:
                try:
                    await websocket.send_text(message)
                except (WebSocketDisconnect, ConnectionResetError, Exception) as e:
                    self.logger.warning(
                        f"Failed to send message to websocket in conversation {conversation_id}: {type(e).__name__}: {e}"
                    )
                    disconnected.add(websocket)

            for websocket in disconnected:
                self.disconnect(websocket, conversation_id)

    async def send_message_to_all(self, data: Dict[str, Any]) -> None:
        message = json.dumps(data, ensure_ascii=False)
        disconnected = set()
        for websocket in self.global_connections:
            try:
                await websocket.send_text(message)
            except (WebSocketDisconnect, ConnectionResetError, Exception) as e:
                self.logger.warning(f"Failed to send message to global websocket: {type(e).__name__}: {e}")
                disconnected.add(websocket)

        for websocket in disconnected:
            self.disconnect_global(websocket)
