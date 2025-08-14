from dataclasses import dataclass, field
from typing import Any, Dict, List, Union


@dataclass
class ToolResponse:
    """
    A class representing a response from a tool call.

    Attributes:
        tool_name (str): The name of the tool that was called.
        response (Dict[str, Any]): The response data from the tool call, which can be any JSON-serializable data structure.
    """

    tool_name: str = ""
    response: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TextContent:
    """
    A class representing text content.

    Attributes:
        text (str): The text content.
        thought (bool): Indicates if the text is a thought or not.
    """

    text: str = ""
    thought: bool = False


@dataclass
class LlmRequestContent:
    """
    A class representing the content of an LLM request.

    Attributes:
        role (str): The role of the content (e.g., "user", "model").
        content (List[Union[TextContent, ToolResponse]]): The content of the request.
    """

    role: str = "user"
    content: List[Union[TextContent, ToolResponse]] = field(default_factory=list)


@dataclass
class ToolCall:
    """
    A class representing a tool call.

    Attributes:
        tool_name (str): The name of the tool being called.
        arguments (Dict[str, str]): The arguments for the tool call.
    """

    tool_name: str = ""
    arguments: Dict[str, str] = field(default_factory=dict)


@dataclass
class LlmResponseContent:
    """
    A class representing the content of an LLM response.

    Attributes:
        role (str): The role of the content (e.g., "user", "model").
        parts (List[Union[TextContent, ToolCall]]): The parts of the response, which can include text content or tool calls.
    """

    role: str = "model"
    parts: List[Union[TextContent, ToolCall]] = field(default_factory=list)


@dataclass
class UsageMetadata:
    """
    A class representing usage metadata for an LLM call.

    Attributes:
        total_tokens (int): Total tokens used in the LLM call.
        prompt_tokens (int): Tokens used in the prompt.
        candidate_tokens (int): Tokens used in the candidate response.
        thoughts_tokens (int): Tokens used in thoughts.
        tool_use_prompt_tokens (int): Tokens used in tool use prompts.
        cached_content_tokens (int): Tokens used for cached content.
    """

    total_tokens: int = 0
    prompt_tokens: int = 0
    candidate_tokens: int = 0
    thoughts_tokens: int = 0
    tool_use_prompt_tokens: int = 0
    cached_content_tokens: int = 0
