import gzip
import logging
from typing import List

from fastapi import APIRouter, Request, Response, status
from google.protobuf import json_format
from google.protobuf.message import DecodeError
from opentelemetry.proto.collector.trace.v1 import trace_service_pb2

from ...core.span_preprocessor import preprocess_spans
from ...models.events import CommunicationEvent

router = APIRouter(tags=["traces"])
logger = logging.getLogger(__name__)


async def distribute_events(
    events: List[CommunicationEvent],
) -> None:
    """
    Distribute events to WebSocket connections based on their filters.

    Args:
        events: List of CommunicationEvent objects
    """
    from ...core.state import connection_manager, filter_registry

    for event in events:
        # Register filter values for the API
        filter_registry.register_event(event.conversation_id, event.workforce_name)

        event_data = event.to_dict()

        # Send to all connections whose filters match
        await connection_manager.send_message(data=event_data, event=event)

        logger.debug(
            f"Distributed {event.event_type} from {event.acting_agent} in conversation {event.conversation_id}"
        )


@router.post("/v1/traces")
async def receive_traces(request: Request) -> Response:
    """
    OTLP/HTTP endpoint for receiving trace data.
    Accepts both protobuf-encoded and JSON trace data from OpenTelemetry collectors/exporters.
    """
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

    # preprocess_spans returns List[CommunicationEvent]
    events = preprocess_spans(export_request)

    if events:
        logger.debug(f"Created {len(events)} communication events")
        await distribute_events(events)
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
