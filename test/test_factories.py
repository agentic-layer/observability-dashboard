"""Unit tests for factory functions and extractors."""

from app.utils.extractors import extract_invoked_agent
from app.utils.factories import _is_agent_tool_call


class TestIsAgentToolCall:
    """Tests for the _is_agent_tool_call heuristic."""

    def test_agent_tool_with_only_args_request(self) -> None:
        """AgentTool calls have only args.request as their argument."""
        attrs = {
            "tool_name": "cross_selling_agent",
            "args.request": "Analyze customer cust001",
        }
        assert _is_agent_tool_call(attrs) is True

    def test_legacy_transfer_to_agent(self) -> None:
        """Legacy transfer_to_agent is always an agent invocation."""
        attrs = {
            "tool_name": "transfer_to_agent",
            "args.agent_name": "weather-agent",
        }
        assert _is_agent_tool_call(attrs) is True

    def test_mcp_tool_with_multiple_args(self) -> None:
        """MCP tools with multiple args are not agent calls."""
        attrs = {
            "tool_name": "send_email",
            "args.customer_id": "cust001",
            "args.subject": "Test",
            "args.body": "Hello",
        }
        assert _is_agent_tool_call(attrs) is False

    def test_regular_tool_with_single_non_request_arg(self) -> None:
        """Tools with a single arg that isn't 'request' are not agent calls."""
        attrs = {
            "tool_name": "get_weather",
            "args.city": "Munich",
        }
        assert _is_agent_tool_call(attrs) is False

    def test_empty_attributes(self) -> None:
        """Empty attributes should not match as agent call."""
        assert _is_agent_tool_call({}) is False

    def test_no_args(self) -> None:
        """Tool with no args should not match as agent call."""
        attrs = {"tool_name": "some_tool"}
        assert _is_agent_tool_call(attrs) is False


class TestExtractInvokedAgent:
    """Tests for extracting invoked agent name from tool call attributes."""

    def test_agent_tool_uses_tool_name(self) -> None:
        """For AgentTool calls, the tool_name IS the agent name."""
        attrs = {
            "tool_name": "cross_selling_agent",
            "args.request": "Analyze customer",
        }
        assert extract_invoked_agent(attrs) == "cross_selling_agent"

    def test_transfer_to_agent_uses_args_agent_name(self) -> None:
        """For transfer_to_agent, agent name comes from args.agent_name."""
        attrs = {
            "tool_name": "transfer_to_agent",
            "args.agent_name": "weather-agent",
        }
        assert extract_invoked_agent(attrs) == "weather-agent"

    def test_missing_tool_name_returns_empty_string(self) -> None:
        """Missing tool_name should return empty string."""
        assert extract_invoked_agent({}) == ""

    def test_transfer_without_agent_name_returns_empty_string(self) -> None:
        """transfer_to_agent without args.agent_name returns empty string."""
        attrs = {"tool_name": "transfer_to_agent"}
        assert extract_invoked_agent(attrs) == ""
