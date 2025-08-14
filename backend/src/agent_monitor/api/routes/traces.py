import logging
from typing import Dict

from fastapi import APIRouter, Request, Response, status
from opentelemetry.proto.collector.trace.v1 import trace_service_pb2

from ...core.connection_manager import ConnectionManager
from ...core.span_preprocessor import preprocess_spans

router = APIRouter(tags=["traces"])
logger = logging.getLogger(__name__)


async def distribute_events(
    events, conversation_managers: Dict[str, ConnectionManager], global_manager: ConnectionManager
):
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
async def receive_traces(request: Request):
    """
    OTLP/HTTP endpoint for receiving trace data.
    Accepts protobuf-encoded trace data from OpenTelemetry collectors/exporters.
    """
    from ...core.state import conversation_managers, global_manager

    try:
        body = await request.body()
        export_request = trace_service_pb2.ExportTraceServiceRequest()
        export_request.ParseFromString(body)
        events = preprocess_spans(export_request)

        if events:
            logger.debug(f"Created {len(events)} communication events")
            await distribute_events(events, conversation_managers, global_manager)
        else:
            logger.debug("No relevant communication events found")

        response = trace_service_pb2.ExportTraceServiceResponse()
        return Response(
            content=response.SerializeToString(), media_type="application/x-protobuf", status_code=status.HTTP_200_OK
        )

    except Exception as e:
        logger.exception(f"Error processing traces: {e}")
        return Response(status_code=status.HTTP_400_BAD_REQUEST, content=f"Error processing traces: {str(e)}")
