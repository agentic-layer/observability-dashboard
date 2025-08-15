import logging
import re
from typing import Any, Dict, Optional

from ..models.content import (
    LlmRequestContent,
    LlmResponseContent,
    TextContent,
    ToolCall,
    ToolResponse,
    UsageMetadata,
)

logger = logging.getLogger(__name__)

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

# Compiled regex patterns for better performance
_PATTERN_TEXT_LLM_REQUEST = re.compile(r"llm_request\.content\.parts\.\d+\.text")
_PATTERN_FUNCTION_RESPONSE_LLM_REQUEST = re.compile(r"llm_request\.content\.parts\.(\d+)\.function_response\.name")
_PATTERN_TEXT_LLM_RESPONSE = re.compile(r"llm_response\.content\.parts\.\d+\.text")
_PATTERN_FUNCTION_CALL_LLM_RESPONSE = re.compile(r"llm_response\.content\.parts\.(\d+)\.function_call\.name")


def extract_invoked_agent(attributes: Dict[str, Any]) -> str:
    """Extract invoked agent from tool call attributes."""
    return attributes.get("args.agent_name", "")


def extract_tool_response(attributes: Dict[str, Any]) -> Dict[str, Any]:
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
        return response
    except (AttributeError, TypeError, IndexError) as e:
        logger.exception(f"Error extracting tool response: {e}")
        return {}


def parse_llm_content_key(key: str) -> Optional[tuple[str, str]]:
    """Parse LLM content key to extract prefix and origin part.

    Returns:
        Optional[tuple[str, str]]: Tuple of (prefix, origin) if valid, None otherwise.
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


def extract_llm_request_content(attributes: Dict[str, Any]) -> LlmRequestContent:
    """Extract LLM request content from attributes."""
    try:
        content = LlmRequestContent()
        tool_responses = {}  # Store ToolResponse objects by number
        for key, value in attributes.items():
            if not key.startswith("llm_request.content."):
                continue
            if _PATTERN_TEXT_LLM_REQUEST.fullmatch(key):
                content.content.append(TextContent(text=value, thought=False))
                continue
            match_func = _PATTERN_FUNCTION_RESPONSE_LLM_REQUEST.fullmatch(key)
            if match_func:
                number = match_func.group(1)
                tool_responses[number] = ToolResponse(tool_name=value, response={})
                continue
            if key.endswith(".role"):
                content.role = value
        for number, tool_response in tool_responses.items():
            prefix = f"llm_request.content.parts.{number}.function_response.response."
            for sub_key, sub_value in attributes.items():
                if sub_key.startswith(prefix):
                    new_key = sub_key.removeprefix(prefix)
                    if new_key:
                        tool_response.response[new_key] = sub_value
            content.content.append(tool_response)
        return content
    except (AttributeError, TypeError) as e:
        logger.exception(f"Error extracting LLM request content: {e}")
        return LlmRequestContent()


def extract_llm_response_content(attributes: Dict[str, Any]) -> LlmResponseContent:
    """Extract LLM response content from attributes."""
    try:
        content = None
        tool_calls = {}  # Store ToolCall objects by number
        for key, value in attributes.items():
            if not key.startswith("llm_response.content."):
                continue
            if content is None:
                content = LlmResponseContent()
            if _PATTERN_TEXT_LLM_RESPONSE.fullmatch(key):
                thought = attributes.get(key.replace("text", "thought"), False)
                content.parts.append(TextContent(text=value, thought=thought))
                continue
            match_func = _PATTERN_FUNCTION_CALL_LLM_RESPONSE.fullmatch(key)
            if match_func:
                number = match_func.group(1)
                tool_calls[number] = ToolCall(tool_name=value)
                continue
            if key.endswith(".role"):
                content.role = value
        for number, tool_call in tool_calls.items():
            prefix = f"llm_response.content.parts.{number}.function_call.args."
            for sub_key, sub_value in attributes.items():
                if sub_key.startswith(prefix):
                    new_key = sub_key.removeprefix(prefix)
                    if new_key:
                        tool_call.arguments[new_key] = sub_value
            if content:
                content.parts.append(tool_call)
        return content if content is not None else LlmResponseContent()
    except (AttributeError, TypeError) as e:
        logger.exception(f"Error extracting LLM response content: {e}")
        return LlmResponseContent()


def extract_usage_metadata(attributes: Dict[str, Any]) -> UsageMetadata:
    """Extract usage metadata from attributes."""
    try:
        return UsageMetadata(
            total_tokens=attributes.get("llm_response.usage_metadata.total_token_count", 0),
            prompt_tokens=attributes.get("llm_response.usage_metadata.prompt_token_count", 0),
            candidate_tokens=attributes.get("llm_response.usage_metadata.candidates_token_count", 0),
            thoughts_tokens=attributes.get("llm_response.usage_metadata.thoughts_token_count", 0),
            tool_use_prompt_tokens=attributes.get("llm_response.usage_metadata.tool_use_prompt_token_count", 0),
            cached_content_tokens=attributes.get("llm_response.usage_metadata.cached_content_token_count", 0),
        )
    except (AttributeError, TypeError) as e:
        logger.exception(f"Error extracting usage metadata: {e}")
        return UsageMetadata()


def extract_tool_call(attributes: Dict[str, Any]) -> ToolCall:
    """Extract tool call from attributes."""
    try:
        tool_name = attributes.get("tool_name", "")
        arguments = {}
        for key, value in attributes.items():
            if key.startswith("args."):
                new_key = key.removeprefix("args.")
                if new_key:
                    arguments[new_key] = value
        return ToolCall(tool_name=tool_name, arguments=arguments)
    except (AttributeError, TypeError) as e:
        logger.exception(f"Error extracting tool call: {e}")
        return ToolCall()
