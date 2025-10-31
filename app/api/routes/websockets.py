import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ...models.filters import FilterCriteria

router = APIRouter(tags=["websockets"])
logger = logging.getLogger(__name__)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """
    WebSocket endpoint with optional filtering via query parameters.

    Query parameters:
    - conversation_id: Filter to specific conversation (UUID4 format)
    - workforce: Filter by agentic_layer.workforce resource attribute

    Examples:
    - /ws - Receive all events (no filtering)
    - /ws?conversation_id=abc-123 - Only events for conversation abc-123
    - /ws?workforce=foo - Only events with workforce=foo
    - /ws?conversation_id=abc-123&workforce=foo - Both filters applied
    """
    from ...core.state import connection_manager

    # Parse filter criteria from query parameters
    query_params = dict(websocket.query_params)
    filter_criteria = FilterCriteria.from_query_params(query_params)

    # Connect with filter criteria
    await connection_manager.connect(websocket, filter_criteria)

    try:
        # Send welcome message
        welcome_data = {
            "type": "connection_established",
            "message": "Connected to observability dashboard",
            "filters": {
                "conversation_id": filter_criteria.conversation_id,
                "workforce": filter_criteria.workforce,
            },
        }

        try:
            await websocket.send_text(json.dumps(welcome_data))
        except (TypeError, ValueError) as e:
            logger.exception(f"JSON serialization error for welcome message: {e}")
            await websocket.close(code=4500, reason="Internal server error")
            return

        # Keep connection alive by waiting for messages or disconnect
        while True:
            try:
                # We don't expect client messages, but need to detect disconnect
                data = await websocket.receive_text()

                # Optional: Allow clients to update their filters dynamically
                if data.startswith("{"):
                    try:
                        message = json.loads(data)
                        if message.get("type") == "update_filter":
                            # Future enhancement: update filter_criteria in connection_manager
                            logger.info(f"Filter update requested: {message}")
                    except json.JSONDecodeError:
                        pass

            except WebSocketDisconnect:
                break

    except WebSocketDisconnect:
        pass
    finally:
        connection_manager.disconnect(websocket)
