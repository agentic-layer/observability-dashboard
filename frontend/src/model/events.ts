// Content models

export interface ToolResponse {
  tool_name: string;
  response: Record<string, unknown>;
}

export interface TextContent {
  text: string;
  thought: boolean;
}

export interface LlmRequestContent {
  role: string;
  content: (TextContent | ToolResponse)[];
}

export interface ToolCall {
  tool_name: string;
  arguments: Record<string, string>;
}

export interface LlmResponseContent {
  role: string;
  parts: (TextContent | ToolCall)[];
}

export interface UsageMetadata {
  total_tokens: number;
  prompt_tokens: number;
  candidate_tokens: number;
  thoughts_tokens: number;
  tool_use_prompt_tokens: number;
  cached_content_tokens: number;
}

// Event models

export interface BaseEvent {
  acting_agent: string;
  conversation_id: string;
  timestamp: string;
  event_type: 'agent_start' | 'agent_end' | 'llm_call_start' | 'llm_call_end' | 'llm_call_error' | 'tool_call_start' | 'tool_call_end' | 'tool_call_error' | 'invoke_agent_start' | 'invoke_agent_end';
  invocation_id: string;
}

export type AgentEvent = BaseEvent;

export interface LLMCallStartEvent extends BaseEvent {
  model: string;
  content: LlmRequestContent;
}

export interface LLMCallEndEvent extends BaseEvent {
  content: LlmResponseContent;
  usage_metadata: UsageMetadata;
}

export interface LLMCallErrorEvent extends BaseEvent {
  model: string;
  content: LlmRequestContent;
  error: string;
}

export interface ToolCallStartEvent extends BaseEvent {
  tool_call: ToolCall;
}

export interface ToolCallEndEvent extends BaseEvent {
  tool_call: ToolCall;
  response: Record<string, unknown>;
}

export interface ToolCallErrorEvent extends BaseEvent {
  tool_call: ToolCall;
  error: string;
}

export interface InvokeAgentStartEvent extends ToolCallStartEvent {
  invoked_agent: string;
}

export interface InvokeAgentEndEvent extends ToolCallEndEvent {
  invoked_agent: string;
}

// Union type for all communication events
export type CommunicationEvent =
  | AgentEvent
  | LLMCallStartEvent
  | LLMCallEndEvent
  | LLMCallErrorEvent
  | ToolCallStartEvent
  | ToolCallEndEvent
  | ToolCallErrorEvent
  | InvokeAgentStartEvent
  | InvokeAgentEndEvent;

// Type guards using structural checks
export function isTextContent(content: TextContent | ToolResponse | ToolCall): content is TextContent {
  return 'text' in content && 'thought' in content;
}

export function isToolResponse(content: TextContent | ToolResponse | ToolCall): content is ToolResponse {
  return 'response' in content && 'tool_name' in content;
}

export function isToolCall(content: TextContent | ToolResponse | ToolCall): content is ToolCall {
  return 'arguments' in content && 'tool_name' in content;
}
