import json
import logging
import re

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ...core.connection_manager import ConnectionManager

router = APIRouter(tags=["websockets"])
logger = logging.getLogger(__name__)


def validate_conversation_id(conversation_id: str) -> bool:
    """Validate conversation_id format - supports UUID4 format"""
    if not conversation_id:
        return False
    return (
        re.match(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$", conversation_id) is not None
    )


@router.websocket("/ws/{conversation_id}")
async def websocket_endpoint(websocket: WebSocket, conversation_id: str):
    """
    WebSocket endpoint for subscribing to trace updates for a specific conversation.
    Clients can connect and receive JSON data related to their conversation_id.
    """
    from ...core.state import conversation_managers

    # Security: validate format before accepting connection to prevent resource abuse
    if not validate_conversation_id(conversation_id):
        await websocket.close(code=4400, reason="Invalid conversation_id format")
        logger.warning(f"Rejected WebSocket connection due to invalid conversation_id: {conversation_id}")
        return

    # Create manager for this conversation_id if it doesn't exist
    if conversation_id not in conversation_managers:
        conversation_managers[conversation_id] = ConnectionManager(conversation_id)

    manager = conversation_managers[conversation_id]
    await manager.connect(websocket)
    try:
        try:
            welcome_message = json.dumps(
                {
                    "type": "connection_established",
                    "conversation_id": conversation_id,
                    "message": f"Connected to conversation {conversation_id}",
                }
            )
            await websocket.send_text(welcome_message)
        except (TypeError, ValueError) as e:
            logger.exception(f"JSON serialization error for welcome message: {e}")
            await websocket.close(code=4500, reason="Internal server error")
            return

        # Keep connection alive by waiting for client disconnect
        while True:
            try:
                await websocket.receive_text()  # Blocks until message or disconnect
            except WebSocketDisconnect:
                break

    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)

        # Clean up empty managers
        if len(manager.active_connections) == 0:
            del conversation_managers[conversation_id]


@router.websocket("/ws")
async def websocket_global_endpoint(websocket: WebSocket):
    """
    Global WebSocket endpoint for subscribing to all trace updates across all conversations.
    Clients can connect and receive JSON data for all events regardless of conversation_id.
    """
    from ...core.state import global_manager

    await global_manager.connect(websocket)
    try:
        try:
            global_welcome_message = json.dumps(
                {"type": "global_connection_established", "message": "Connected to global event stream"}
            )
            await websocket.send_text(global_welcome_message)
        except (TypeError, ValueError) as e:
            logger.exception(f"JSON serialization error for global welcome message: {e}")
            await websocket.close(code=4500, reason="Internal server error")
            return

        # Keep connection alive by waiting for client disconnect
        while True:
            try:
                await websocket.receive_text()  # Blocks until message or disconnect
            except WebSocketDisconnect:
                break

    except WebSocketDisconnect:
        pass
    finally:
        global_manager.disconnect(websocket)
