import json
import logging
from typing import Any, Dict

from ..models.events import (
    AgentEvent,
    InvokeAgentEndEvent,
    InvokeAgentStartEvent,
    LLMCallEndEvent,
    LLMCallErrorEvent,
    LLMCallStartEvent,
    ToolCallEndEvent,
    ToolCallErrorEvent,
    ToolCallStartEvent,
)
from .extractors import (
    extract_invoked_agent,
    extract_llm_request_content,
    extract_llm_response_content,
    extract_tool_call,
    extract_tool_response,
    extract_usage_metadata,
)

logger = logging.getLogger(__name__)


def create_agent_start_event(
    acting_agent: str, conversation_id: str, timestamp: str, attributes: Dict[str, Any]
) -> AgentEvent:
    """Create an AgentEvent for agent start from span attributes."""
    return AgentEvent(
        acting_agent=acting_agent,
        conversation_id=conversation_id,
        timestamp=timestamp,
        event_type="agent_start",
        invocation_id=attributes.get("invocation_id", ""),
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
        invocation_id=attributes.get("invocation_id", ""),
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
        invocation_id=attributes.get("invocation_id", ""),
        model=attributes.get("model", ""),
        content=extract_llm_request_content(attributes),
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
        invocation_id=attributes.get("invocation_id", ""),
        content=extract_llm_response_content(attributes),
        usage_metadata=extract_usage_metadata(attributes),
    )


def _is_agent_tool_call(attributes: Dict[str, Any]) -> bool:
    """Check if the tool call is an agent invocation.

    Uses a heuristic based on argument patterns:
    - AgentTool calls (sub-agent invocations) have only 'args.request' as their argument
    - transfer_to_agent is the legacy agent invocation method
    """
    # transfer_to_agent is the legacy agent invocation (transfer interaction type)
    if attributes.get("tool_name") == "transfer_to_agent":
        return True

    # AgentTool heuristic: only has args.request, no other args
    args_keys = [k for k in attributes if k.startswith("args.")]
    if args_keys == ["args.request"]:
        return True

    return False


def create_tool_call_start_event(
    acting_agent: str, conversation_id: str, timestamp: str, attributes: Dict[str, Any]
) -> ToolCallStartEvent:
    """Create a ToolCallStartEvent from span attributes."""
    invocation_id = attributes.get("invocation_id", "")
    tool_call = extract_tool_call(attributes)
    if _is_agent_tool_call(attributes):
        return InvokeAgentStartEvent(
            acting_agent=acting_agent,
            conversation_id=conversation_id,
            timestamp=timestamp,
            event_type="invoke_agent_start",
            invocation_id=invocation_id,
            tool_call=tool_call,
            invoked_agent=extract_invoked_agent(attributes),
        )
    return ToolCallStartEvent(
        acting_agent=acting_agent,
        conversation_id=conversation_id,
        timestamp=timestamp,
        event_type="tool_call_start",
        invocation_id=invocation_id,
        tool_call=tool_call,
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
        invocation_id=attributes.get("invocation_id", ""),
        model=attributes.get("model", ""),
        content=extract_llm_request_content(attributes),
        error=attributes.get("error", ""),
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
        invocation_id=attributes.get("invocation_id", ""),
        tool_call=extract_tool_call(attributes),
        error=attributes.get("error", ""),
    )


def create_tool_call_end_event(
    acting_agent: str, conversation_id: str, timestamp: str, attributes: Dict[str, Any]
) -> ToolCallEndEvent:
    """Create a ToolCallEndEvent from span attributes."""
    invocation_id = attributes.get("invocation_id", "")
    tool_call = extract_tool_call(attributes)
    response = extract_tool_response(attributes)
    if response is not None:
        if isinstance(response.get("text"), str):
            try:
                response["text"] = json.loads(response["text"])
            except json.JSONDecodeError:
                logger.debug("Failed to parse tool response text as JSON: %s", response["text"], exc_info=True)
                pass
    if _is_agent_tool_call(attributes):
        return InvokeAgentEndEvent(
            acting_agent=acting_agent,
            conversation_id=conversation_id,
            timestamp=timestamp,
            event_type="invoke_agent_end",
            invocation_id=invocation_id,
            tool_call=tool_call,
            response=response,
            invoked_agent=extract_invoked_agent(attributes),
        )
    return ToolCallEndEvent(
        acting_agent=acting_agent,
        conversation_id=conversation_id,
        timestamp=timestamp,
        event_type="tool_call_end",
        invocation_id=invocation_id,
        tool_call=tool_call,
        response=response,
    )
