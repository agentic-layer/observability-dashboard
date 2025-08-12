import json
import logging
import re

from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect, status
from opentelemetry.proto.collector.trace.v1 import trace_service_pb2

from .connection_manager import ConnectionManager
from .span_preprocessor import preprocess_spans

app = FastAPI(
    title="Agent Communication Dashboard Backend",
    description="Backend service for receiving and processing tracing data and sending them out via websocket",
)

logger = logging.getLogger(__name__)
manager = ConnectionManager()


@app.post("/v1/traces")
async def receive_traces(request: Request):
    """
    OTLP/HTTP endpoint for receiving trace data.
    Accepts protobuf-encoded trace data from OpenTelemetry collectors/exporters.
    """
    try:
        body = await request.body()
        export_request = trace_service_pb2.ExportTraceServiceRequest()
        export_request.ParseFromString(body)
        events = preprocess_spans(export_request)

        if events:
            logger.debug(f"Created {len(events)} communication events")

            # Broadcast events to both conversation-specific and global WebSocket connections
            for event in events:
                event_data = event.to_dict()
                await manager.send_message_for_conversation(event.conversation_id, event_data)
                await manager.send_message_to_all(event_data)
                logger.info(
                    f"Sent event: {event.event_type} from {event.acting_agent} to conversation {event.conversation_id}"
                )
        else:
            logger.debug("No relevant communication events found")

        response = trace_service_pb2.ExportTraceServiceResponse()
        return Response(
            content=response.SerializeToString(), media_type="application/x-protobuf", status_code=status.HTTP_200_OK
        )

    except Exception as e:
        logger.error(f"Error processing traces: {e}", exc_info=True)
        return Response(status_code=status.HTTP_400_BAD_REQUEST, content=f"Error processing traces: {str(e)}")


def validate_conversation_id(conversation_id: str) -> bool:
    """Validate conversation_id format - supports UUID4 format (alphanumeric + hyphens), max 100 chars"""
    if not conversation_id:
        return False
    return re.match(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$", conversation_id) is not None # match conversation_id to uuid4 format


@app.websocket("/ws/{conversation_id}")
async def websocket_endpoint(websocket: WebSocket, conversation_id: str):
    """
    WebSocket endpoint for subscribing to trace updates for a specific conversation.
    Clients can connect and receive JSON data related to their conversation_id.
    """
    # Security: validate format before accepting connection to prevent resource abuse
    if not validate_conversation_id(conversation_id):
        await websocket.close(code=4400, reason="Invalid conversation_id format")
        logger.warning(f"Rejected WebSocket connection due to invalid conversation_id: {conversation_id}")
        return

    await manager.connect(websocket, conversation_id)
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
            logger.error(f"JSON serialization error for welcome message: {e}")
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
        manager.disconnect(websocket, conversation_id)


@app.websocket("/ws")
async def websocket_global_endpoint(websocket: WebSocket):
    """
    Global WebSocket endpoint for subscribing to all trace updates across all conversations.
    Clients can connect and receive JSON data for all events regardless of conversation_id.
    """
    await manager.connect_global(websocket)
    try:
        try:
            global_welcome_message = json.dumps(
                {"type": "global_connection_established", "message": "Connected to global event stream"}
            )
            await websocket.send_text(global_welcome_message)
        except (TypeError, ValueError) as e:
            logger.error(f"JSON serialization error for global welcome message: {e}")
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
        manager.disconnect_global(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
