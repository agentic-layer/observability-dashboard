import json
import logging
from typing import Any, Dict, List, Tuple

from fastapi import WebSocket, WebSocketDisconnect

from ..models.filters import FilterCriteria


class ConnectionManager:
    """
    Manages WebSocket connections with per-connection filtering.

    Each connection can have its own FilterCriteria that determines
    which events it receives.
    """

    def __init__(self) -> None:
        # Store tuples of (websocket, filter_criteria)
        self.connections: List[Tuple[WebSocket, FilterCriteria]] = []
        self.logger = logging.getLogger(__name__)

    async def connect(self, websocket: WebSocket, filter_criteria: FilterCriteria) -> None:
        """
        Accept a new WebSocket connection with optional filtering.

        Args:
            websocket: The WebSocket connection
            filter_criteria: Filter criteria for this connection
        """
        await websocket.accept()
        self.connections.append((websocket, filter_criteria))

        filter_desc = self._describe_filter(filter_criteria)
        self.logger.info(f"Connected websocket with filter: {filter_desc}. Total connections: {len(self.connections)}")

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection."""
        original_count = len(self.connections)
        self.connections = [(ws, fc) for ws, fc in self.connections if ws != websocket]

        if len(self.connections) < original_count:
            self.logger.info(f"Disconnected websocket. Remaining connections: {len(self.connections)}")

    async def send_message(
        self,
        data: Dict[str, Any],
        event: Any,  # CommunicationEvent (using Any to avoid circular import)
    ) -> None:
        """
        Send a message to all connections whose filters match.

        Args:
            data: The event data to send (already serializable)
            event: The CommunicationEvent object to match against filters
        """
        if not self.connections:
            return

        message = json.dumps(data, ensure_ascii=False)
        disconnected = []
        sent_count = 0

        for websocket, filter_criteria in self.connections:
            # Check if this connection's filter matches the event
            if not filter_criteria.matches(event):
                continue

            try:
                await websocket.send_text(message)
                sent_count += 1
            except (WebSocketDisconnect, ConnectionResetError, Exception) as e:
                self.logger.warning(f"Failed to send message to websocket: {type(e).__name__}: {e}")
                disconnected.append(websocket)

        # Clean up disconnected websockets
        for websocket in disconnected:
            self.disconnect(websocket)

        if disconnected:
            self.logger.info(f"Removed {len(disconnected)} disconnected websockets. Remaining: {len(self.connections)}")

        if sent_count > 0:
            self.logger.debug(f"Sent message to {sent_count}/{len(self.connections)} connections")

    def _describe_filter(self, filter_criteria: FilterCriteria) -> str:
        """Create a human-readable description of filter criteria."""
        if filter_criteria.is_empty():
            return "no filter (all events)"

        parts = []
        if filter_criteria.conversation_id:
            parts.append(f"conversation_id={filter_criteria.conversation_id}")
        if filter_criteria.workforce:
            parts.append(f"workforce={filter_criteria.workforce}")

        return ", ".join(parts) if parts else "no filter"

    @property
    def connection_count(self) -> int:
        """Get the current number of active connections."""
        return len(self.connections)
