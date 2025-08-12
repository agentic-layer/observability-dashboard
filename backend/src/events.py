import json
import logging
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


@dataclass
class BaseEvent:
    """Base class for all communication events."""

    acting_agent: str
    conversation_id: str
    timestamp: str
    event_type: str
    invocation_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to JSON-serializable dictionary."""
        return asdict(self)


@dataclass
class AgentEvent(BaseEvent):
    """Event fired for agent lifecycle changes (start/end)."""


@dataclass
class LLMCallStartEvent(BaseEvent):
    """Event fired when an LLM call begins."""

    model: Optional[str] = None
    contents: Optional[List[Dict[str, Any]]] = None


@dataclass
class LLMCallEndEvent(BaseEvent):
    """Event fired when an LLM call completes."""

    content: Optional[List[Dict[str, Any]]] = None
    usage_metadata: Optional[Dict[str, Any]] = None


@dataclass
class LLMCallErrorEvent(BaseEvent):
    """Event fired when an LLM call encounters an error."""

    model: Optional[str] = None
    contents: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None


@dataclass
class ToolCallStartEvent(BaseEvent):
    """Event fired when a tool call begins."""

    tool_name: Optional[str] = None
    arguments: Optional[Dict[str, Any]] = None


@dataclass
class ToolCallErrorEvent(BaseEvent):
    """Event fired when a tool call encounters an error."""

    tool_name: Optional[str] = None
    arguments: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class InvokeAgentStartEvent(ToolCallStartEvent):
    """Event fired when an agent is invoked by a tool call."""

    invoked_agent: Optional[str] = None


@dataclass
class ToolCallEndEvent(BaseEvent):
    """Event fired when a tool call completes."""

    tool_name: Optional[str] = None
    arguments: Optional[Dict[str, Any]] = None
    response: Optional[Dict[str, Any]] = None


@dataclass
class InvokeAgentEndEvent(ToolCallEndEvent):
    """Event fired when an agent invocation by a tool call ends."""

    invoked_agent: Optional[str] = None


# Union type for all communication events
CommunicationEvent = Union[
    AgentEvent,
    LLMCallStartEvent,
    LLMCallEndEvent,
    LLMCallErrorEvent,
    ToolCallStartEvent,
    ToolCallEndEvent,
    ToolCallErrorEvent,
    InvokeAgentStartEvent,
    InvokeAgentEndEvent,
]


def _extract_invoked_agent(attributes: Dict[str, Any]) -> Optional[str]:
    """Extract invoked agent from tool call attributes."""
    return attributes.get("args.agent_name")


def _extract_arguments(attributes: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Extract arguments from tool call attributes."""
    try:
        arguments = {}
        for key, value in attributes.items():
            if key.startswith("args."):
                new_key = key.removeprefix("args.")
                if new_key:
                    arguments[new_key] = value
        return arguments if arguments else None
    except (AttributeError, TypeError) as e:
        logger.debug(f"Error extracting arguments: {e}")
        return None


def _extract_tool_response(attributes: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Extract tool response from attributes."""
    try:
        response = {}
        for key, value in attributes.items():
            if key.startswith("tool_response."):
                key_parts = key.split(".")
                if len(key_parts) > 1:
                    new_key = key_parts[-1]
                    if new_key:
                        response[new_key] = value
        return response if response else None
    except (AttributeError, TypeError, IndexError) as e:
        logger.debug(f"Error extracting tool response: {e}")
        return None


# Supported LLM content sub-parts from Google GenAI Content types
SUPPORTED_CONTENT_PARTS = {
    "text",
    "function_call",
    "video_metadata",
    "inline_data",
    "file_data",
    "code_execution_result",
    "executable_code",
    "function_response",
}


def _parse_llm_content_key(key: str) -> Optional[tuple[str, str]]:
    """Parse LLM content key to extract prefix and origin part.

    Returns:
        tuple[str, str] | None: Tuple of (prefix, origin) if valid, None otherwise.
    """
    try:
        key_parts = key.split(".")
        if "parts" not in key_parts:
            return None

        parts_index = key_parts.index("parts")
        origin_index = parts_index + 2

        if origin_index >= len(key_parts):
            return None

        origin = key_parts[origin_index]
        if origin not in SUPPORTED_CONTENT_PARTS:
            return None

        prefix = ".".join(key_parts[:origin_index])
        return prefix, origin
    except (ValueError, IndexError):
        return None


def _extract_relevant_llm_contents(attributes: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
    """Extract relevant LLM contents from attributes."""
    relevant_contents = []
    processed_combinations = set()

    try:
        for key in attributes.keys():
            if not key.startswith(("llm_response.content", "llm_request.content")):
                continue

            parsed = _parse_llm_content_key(key)
            if not parsed:
                continue

            prefix, origin = parsed
            if (prefix, origin) in processed_combinations:
                continue

            processed_combinations.add((prefix, origin))

            content: Optional[Dict[str, Any]] = None
            if origin == "text":
                relevant_attributes = {k: v for k, v in attributes.items() if k.startswith(prefix)}
                content = _process_content_text_properties(origin, relevant_attributes)
            else:
                search_prefix = f"{prefix}.{origin}"
                relevant_attributes = {k: v for k, v in attributes.items() if k.startswith(search_prefix)}
                content = _process_content_non_text_properties(prefix, origin, relevant_attributes)

            if content:
                relevant_contents.append(content)

    except Exception as e:
        logger.debug(f"Error extracting LLM contents: {e}")
        return None

    return relevant_contents if relevant_contents else None


def _process_content_text_properties(origin: str, attributes: Dict[str, Any]) -> Dict[str, Any]:
    content = {}
    for key, value in attributes.items():
        if key.endswith(".text"):
            content["text"] = value
            content["origin"] = origin
            content["thought"] = attributes.get(key.replace("text", "thought"), False)
            break
    return content


def _process_content_non_text_properties(
    prefix: str, origin: str, attributes: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    content = {}
    for key, value in attributes.items():
        new_key = key.split(".")[-1]
        content[new_key] = value
    content["origin"] = origin
    return content if content else None


def _extract_usage_metadata(attributes: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Extract usage metadata from attributes."""
    try:
        usage_metadata = {}
        for key, value in attributes.items():
            if key.startswith("llm_response.usage_metadata."):
                new_key = key.removeprefix("llm_response.usage_metadata.")
                if new_key:  # Only add non-empty keys
                    usage_metadata[new_key] = value
        return usage_metadata if usage_metadata else None
    except (AttributeError, TypeError) as e:
        logger.debug(f"Error extracting usage metadata: {e}")
        return None


def create_agent_start_event(
    acting_agent: str, conversation_id: str, timestamp: str, attributes: Dict[str, Any]
) -> AgentEvent:
    """Create an AgentEvent for agent start from span attributes."""
    return AgentEvent(
        acting_agent=acting_agent,
        conversation_id=conversation_id,
        timestamp=timestamp,
        event_type="agent_start",
        invocation_id=attributes.get("invocation_id"),
    )


def create_agent_end_event(
    acting_agent: str, conversation_id: str, timestamp: str, attributes: Dict[str, Any]
) -> AgentEvent:
    """Create an AgentEvent for agent end from span attributes."""
    return AgentEvent(
        acting_agent=acting_agent,
        conversation_id=conversation_id,
        timestamp=timestamp,
        event_type="agent_end",
        invocation_id=attributes.get("invocation_id"),
    )


def create_llm_call_start_event(
    acting_agent: str, conversation_id: str, timestamp: str, attributes: Dict[str, Any]
) -> LLMCallStartEvent:
    """Create an LLMCallStartEvent from span attributes."""
    return LLMCallStartEvent(
        acting_agent=acting_agent,
        conversation_id=conversation_id,
        timestamp=timestamp,
        event_type="llm_call_start",
        invocation_id=attributes.get("invocation_id"),
        model=attributes.get("model"),
        contents=_extract_relevant_llm_contents(attributes),
    )


def create_llm_call_end_event(
    acting_agent: str, conversation_id: str, timestamp: str, attributes: Dict[str, Any]
) -> LLMCallEndEvent:
    """Create an LLMCallEndEvent from span attributes."""
    return LLMCallEndEvent(
        acting_agent=acting_agent,
        conversation_id=conversation_id,
        timestamp=timestamp,
        event_type="llm_call_end",
        invocation_id=attributes.get("invocation_id"),
        content=_extract_relevant_llm_contents(attributes),
        usage_metadata=_extract_usage_metadata(attributes),
    )


def create_tool_call_start_event(
    acting_agent: str, conversation_id: str, timestamp: str, attributes: Dict[str, Any]
) -> ToolCallStartEvent:
    """Create a ToolCallStartEvent from span attributes."""
    invocation_id = attributes.get("invocation_id")
    tool_name = attributes.get("tool_name")
    arguments = _extract_arguments(attributes)
    if tool_name == "send_message":
        return InvokeAgentStartEvent(
            acting_agent=acting_agent,
            conversation_id=conversation_id,
            timestamp=timestamp,
            event_type="invoke_agent_start",
            invocation_id=invocation_id,
            tool_name=tool_name,
            arguments=arguments,
            invoked_agent=_extract_invoked_agent(attributes),
        )
    return ToolCallStartEvent(
        acting_agent=acting_agent,
        conversation_id=conversation_id,
        timestamp=timestamp,
        event_type="tool_call_start",
        invocation_id=invocation_id,
        tool_name=tool_name,
        arguments=arguments,
    )


def create_llm_call_error_event(
    acting_agent: str, conversation_id: str, timestamp: str, attributes: Dict[str, Any]
) -> LLMCallErrorEvent:
    """Create an LLMCallErrorEvent from span attributes."""
    return LLMCallErrorEvent(
        acting_agent=acting_agent,
        conversation_id=conversation_id,
        timestamp=timestamp,
        event_type="llm_call_error",
        invocation_id=attributes.get("invocation_id"),
        model=attributes.get("model"),
        contents=_extract_relevant_llm_contents(attributes),
        error=attributes.get("error"),
    )


def create_tool_call_error_event(
    acting_agent: str, conversation_id: str, timestamp: str, attributes: Dict[str, Any]
) -> ToolCallErrorEvent:
    """Create a ToolCallErrorEvent from span attributes."""
    return ToolCallErrorEvent(
        acting_agent=acting_agent,
        conversation_id=conversation_id,
        timestamp=timestamp,
        event_type="tool_call_error",
        invocation_id=attributes.get("invocation_id"),
        tool_name=attributes.get("tool_name"),
        arguments=_extract_arguments(attributes),
        error=attributes.get("error"),
    )


def create_tool_call_end_event(
    acting_agent: str, conversation_id: str, timestamp: str, attributes: Dict[str, Any]
) -> ToolCallEndEvent:
    """Create a ToolCallEndEvent from span attributes."""
    invocation_id = attributes.get("invocation_id")
    tool_name = attributes.get("tool_name")
    arguments = _extract_arguments(attributes)
    logger.debug(
        f"Processing tool call end event for tool '{tool_name}', invocation_id '{invocation_id}', arguments: {arguments}"
    )
    response = _extract_tool_response(attributes)
    if response is not None:
        if isinstance(response.get("text"), str):
            try:
                response["text"] = json.loads(response["text"])
            except json.JSONDecodeError:
                pass
    if tool_name == "send_message":
        return InvokeAgentEndEvent(
            acting_agent=acting_agent,
            conversation_id=conversation_id,
            timestamp=timestamp,
            event_type="invoke_agent_end",
            invocation_id=invocation_id,
            tool_name=tool_name,
            arguments=arguments,
            response=response,
            invoked_agent=_extract_invoked_agent(attributes),
        )
    return ToolCallEndEvent(
        acting_agent=acting_agent,
        conversation_id=conversation_id,
        timestamp=timestamp,
        event_type="tool_call_end",
        invocation_id=invocation_id,
        tool_name=tool_name,
        arguments=arguments,
        response=response,
    )
