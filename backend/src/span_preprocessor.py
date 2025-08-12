import logging
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Union

from opentelemetry.proto.collector.trace.v1 import trace_service_pb2
from opentelemetry.proto.common.v1 import common_pb2
from opentelemetry.proto.trace.v1 import trace_pb2

from .events import (
    CommunicationEvent,
    create_agent_end_event,
    create_agent_start_event,
    create_llm_call_end_event,
    create_llm_call_error_event,
    create_llm_call_start_event,
    create_tool_call_end_event,
    create_tool_call_error_event,
    create_tool_call_start_event,
)

logger = logging.getLogger(__name__)


def _extract_attribute_value(attr_value: common_pb2.AnyValue) -> Union[str, int, float, bool, None]:
    """Extract the actual value from an OTEL attribute value."""
    try:
        value_type = attr_value.WhichOneof("value")
        if not value_type:
            return None

        if value_type == "string_value":
            return attr_value.string_value
        elif value_type == "int_value":
            return attr_value.int_value
        elif value_type == "double_value":
            return attr_value.double_value
        elif value_type == "bool_value":
            return attr_value.bool_value
        else:
            logger.debug(f"Unknown attribute value type: {value_type}")
            return None
    except (AttributeError, ValueError) as e:
        logger.debug(f"Failed to extract attribute value from type {type(attr_value).__name__}: {e}")
        return None


def _determine_event_type(span_name: str) -> Optional[str]:
    """Determine the event type based on span name and attributes."""
    span_name_lower = span_name.lower()

    if span_name_lower.startswith("before_agent"):
        return "agent_start"
    elif span_name_lower.startswith(("before_model", "before_llm")):
        return "llm_call_start"
    elif span_name_lower.startswith(("after_model", "after_llm")):
        return "llm_call_end"
    elif span_name_lower.startswith("on_model_error"):
        return "llm_call_error"
    elif span_name_lower.startswith("before_tool"):
        return "tool_call_start"
    elif span_name_lower.startswith("after_tool"):
        return "tool_call_end"
    elif span_name_lower.startswith("on_tool_error"):
        return "tool_call_error"
    elif span_name_lower.startswith("after_agent"):
        return "agent_end"

    return None


# Event type to factory function mapping
EVENT_FACTORY_MAP: Dict[str, Callable[[str, str, str, Dict[str, Any]], CommunicationEvent]] = {
    "agent_start": create_agent_start_event,
    "agent_end": create_agent_end_event,
    "llm_call_start": create_llm_call_start_event,
    "llm_call_end": create_llm_call_end_event,
    "llm_call_error": create_llm_call_error_event,
    "tool_call_start": create_tool_call_start_event,
    "tool_call_end": create_tool_call_end_event,
    "tool_call_error": create_tool_call_error_event,
}


def _create_communication_event(
    event_type: str, agent_name: str, conversation_id: str, attributes: Dict[str, Any], start_time: str
) -> CommunicationEvent:
    """Create a CommunicationEvent object from span data using the appropriate factory function."""
    factory_func = EVENT_FACTORY_MAP.get(event_type)
    if not factory_func:
        raise ValueError(f"Unknown event type: {event_type}")
    return factory_func(agent_name, conversation_id, start_time, attributes)


def _extract_span_attributes(span: trace_pb2.Span) -> Dict[str, Union[str, int, float, bool]]:
    """Extract all attributes from a span."""
    attributes = {}
    for attr in span.attributes:
        value = _extract_attribute_value(attr.value)
        if value is not None:
            attributes[attr.key] = value
    return attributes


def _convert_timestamp_to_iso(timestamp_nano: int, span_name: str) -> Optional[str]:
    """Convert nanosecond timestamp to ISO format string."""
    try:
        datetime_object = datetime.fromtimestamp(timestamp_nano / 1_000_000_000, tz=timezone.utc)
        return datetime_object.isoformat().replace("+00:00", "Z")
    except (ValueError, OSError, OverflowError) as e:
        logger.warning(f"Invalid timestamp in span '{span_name}': {timestamp_nano}. Error: {e}")
        return None


def _process_single_span(span: trace_pb2.Span) -> Optional[CommunicationEvent]:
    """Process a single span and return a communication event if valid."""
    attributes = _extract_span_attributes(span)

    # Check if span has observability flag
    if not attributes.get("agent_communication_dashboard", False):
        logger.debug(f"Skipping span '{span.name}': missing agent_communication_dashboard flag")
        return None

    # Extract required attributes
    conversation_id = attributes.get("conversation_id")
    agent_name = attributes.get("agent_name")

    if not conversation_id or not agent_name:
        logger.debug(
            f"Skipping span '{span.name}': missing required attributes (conversation_id: {bool(conversation_id)}, agent_name: {bool(agent_name)})"
        )
        return None

    # Determine event type
    event_type = _determine_event_type(span.name)
    if not event_type:
        logger.debug(f"Skipping span '{span.name}': unrecognized communication event pattern")
        return None

    # Convert timestamp
    iso_timestamp = _convert_timestamp_to_iso(span.start_time_unix_nano, span.name)
    if not iso_timestamp:
        return None

    # Create communication event
    event = _create_communication_event(event_type, str(agent_name), str(conversation_id), attributes, iso_timestamp)

    logger.debug(f"Created {event_type} event for agent '{agent_name}' in conversation '{conversation_id}'")
    return event


def preprocess_spans(export_request: trace_service_pb2.ExportTraceServiceRequest) -> List[CommunicationEvent]:
    """
    Preprocess incoming spans to create communication events.
    Only processes spans with observability flag and required attributes.
    """
    events = []
    span_count = sum(len(scope.spans) for rs in export_request.resource_spans for scope in rs.scope_spans)
    logger.debug(f"Processing {span_count} spans for communication events")

    for resource_spans in export_request.resource_spans:
        for instrumentation_scope in resource_spans.scope_spans:
            for span in instrumentation_scope.spans:
                event = _process_single_span(span)
                if event:
                    events.append(event)

    logger.debug(f"Generated {len(events)} communication events from {span_count} spans")
    return events
