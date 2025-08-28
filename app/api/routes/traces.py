import gzip
import logging
from typing import Dict, List

from fastapi import APIRouter, Request, Response, status
from google.protobuf import json_format
from google.protobuf.message import DecodeError
from opentelemetry.proto.collector.trace.v1 import trace_service_pb2

from ...core.connection_manager import ConnectionManager
from ...core.span_preprocessor import preprocess_spans
from ...models.events import CommunicationEvent

router = APIRouter(tags=["traces"])
logger = logging.getLogger(__name__)


async def distribute_events(
    events: List[CommunicationEvent],
    conversation_managers: Dict[str, ConnectionManager],
    global_manager: ConnectionManager,
) -> None:
    """Distribute events to both conversation-specific and global WebSocket connections."""
    for event in events:
        event_data = event.to_dict()

        # Send to conversation-specific manager if it exists
        if event.conversation_id in conversation_managers:
            await conversation_managers[event.conversation_id].send_message(event_data)

        # Send to global manager
        await global_manager.send_message(event_data)

        logger.info(f"Sent event: {event.event_type} from {event.acting_agent} to conversation {event.conversation_id}")


@router.post("/v1/traces")
async def receive_traces(request: Request) -> Response:
    """
    OTLP/HTTP endpoint for receiving trace data.
    Accepts both protobuf-encoded and JSON trace data from OpenTelemetry collectors/exporters.
    """
    from ...core.state import conversation_managers, global_manager

    body = await request.body()
    content_type = request.headers.get("content-type", "").lower()
    content_encoding = request.headers.get("content-encoding", "").lower()

    # Decompress if gzip encoded
    if "gzip" in content_encoding:
        try:
            body = gzip.decompress(body)
        except Exception as e:
            logger.error(f"Failed to decompress gzip data: {e}")
            return Response(content="Invalid gzip data", status_code=status.HTTP_400_BAD_REQUEST)

    export_request = trace_service_pb2.ExportTraceServiceRequest()

    # Parse based on content type
    if "application/json" in content_type:
        json_format.Parse(body.decode("utf-8"), export_request)
    elif "application/x-protobuf" in content_type:
        try:
            export_request.ParseFromString(body)
        except DecodeError:
            logger.exception("Failed to parse protobuf data")
            return Response(content="Invalid protobuf data", status_code=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(
            content="Unsupported Content-Type. Use application/json or application/x-protobuf.",
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        )

    events = preprocess_spans(export_request)

    if events:
        logger.debug(f"Created {len(events)} communication events")
        await distribute_events(events, conversation_managers, global_manager)
    else:
        logger.debug("No relevant communication events found")

    response = trace_service_pb2.ExportTraceServiceResponse()
    if "application/json" in content_type:
        return Response(
            content=json_format.MessageToJson(response), media_type="application/json", status_code=status.HTTP_200_OK
        )
    else:
        return Response(
            content=response.SerializeToString(), media_type="application/x-protobuf", status_code=status.HTTP_200_OK
        )
