from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Union

from .content import LlmRequestContent, LlmResponseContent, ToolCall, UsageMetadata


@dataclass
class BaseEvent:
    """
    Base class for all communication events.

    Attributes:
        acting_agent (str): The agent that is acting in this event.
        conversation_id (str): Unique identifier for the conversation in UUID4 format.
        timestamp (str): ISO 8601 timestamp in UTC (e.g., "2024-01-15T10:30:00Z").
        event_type (str): Event type discriminator. Possible values:
            - "agent_start": Agent begins execution
            - "agent_end": Agent completes execution
            - "llm_call_start": LLM request initiated
            - "llm_call_end": LLM response received
            - "llm_call_error": LLM call failed
            - "tool_call_start": Tool invocation begins
            - "tool_call_end": Tool invocation completes
            - "tool_call_error": Tool invocation failed
            - "invoke_agent_start": Agent-to-agent call begins
            - "invoke_agent_end": Agent-to-agent call completes
        invocation_id (str): Optional identifier for one agent invocation.
        workforce_name (str | None): The workforce name from resource attributes (agentic_layer.workforce).
            Used for filtering events by workforce. None if not specified.
    """

    acting_agent: str
    conversation_id: str
    timestamp: str
    event_type: str
    invocation_id: str = ""
    workforce_name: str | None = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to JSON-serializable dictionary."""
        return asdict(self)


@dataclass
class AgentEvent(BaseEvent):
    """Event fired for agent lifecycle changes (start/end)."""


@dataclass
class LLMCallStartEvent(BaseEvent):
    """
    Event fired when an LLM call begins.

    Attributes:
        model (str): The LLM model being called.
        content (LlmRequestContent): The content of the LLM request.
    """

    model: str = ""
    content: LlmRequestContent = field(default_factory=LlmRequestContent)


@dataclass
class LLMCallEndEvent(BaseEvent):
    """
    Event fired when an LLM call completes.

    Attributes:
        content (LlmResponseContent): The content of the LLM response.
        usage_metadata (UsageMetadata): Metadata about the token usage of the LLM call.
    """

    content: LlmResponseContent = field(default_factory=LlmResponseContent)
    usage_metadata: UsageMetadata = field(default_factory=UsageMetadata)


@dataclass
class LLMCallErrorEvent(BaseEvent):
    """
    Event fired when an LLM call encounters an error.

    Attributes:
        model (str): The LLM model that was called.
        content (LlmRequestContent): The content of the LLM request that caused the error.
        error (str): The error message encountered during the LLM call.
    """

    model: str = ""
    content: LlmRequestContent = field(default_factory=LlmRequestContent)
    error: str = ""


@dataclass
class ToolCallStartEvent(BaseEvent):
    """
    Event fired when a tool call begins.

    Attributes:
        tool_call (ToolCall): The details of the tool call being made.
    """

    tool_call: ToolCall = field(default_factory=ToolCall)


@dataclass
class ToolCallErrorEvent(BaseEvent):
    """
    Event fired when a tool call encounters an error.

    Attributes:
        tool_call (ToolCall): The details of the tool call that encountered an error.
        error (str): The error message encountered during the tool call.
    """

    tool_call: ToolCall = field(default_factory=ToolCall)
    error: str = ""


@dataclass
class InvokeAgentStartEvent(ToolCallStartEvent):
    """
    Event fired when an agent is invoked by a tool call.

    Attributes:
        invoked_agent (str): The name of the agent being invoked.
    """

    invoked_agent: str = ""


@dataclass
class ToolCallEndEvent(BaseEvent):
    """
    Event fired when a tool call completes.

    Attributes:
        tool_call (ToolCall): The details of the tool call that was made.
        response ([Dict[str, Any]]): The response from the tool call, if applicable.
    """

    tool_call: ToolCall = field(default_factory=ToolCall)
    response: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InvokeAgentEndEvent(ToolCallEndEvent):
    """
    Event fired when an agent invocation by a tool call ends.

    Attributes:
        invoked_agent (str): The name of the agent that was invoked.
    """

    invoked_agent: str = ""


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
