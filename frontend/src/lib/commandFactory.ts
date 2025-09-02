import {
    CommunicationEvent,
    LLMCallEndEvent,
    LLMCallErrorEvent,
    ToolCallStartEvent,
    ToolCallEndEvent,
    ToolCallErrorEvent,
    InvokeAgentStartEvent,
    LLMCallStartEvent,
    InvokeAgentEndEvent,
    TextContent,
    ToolResponse,
    ToolCall
} from "@/model/events.ts";
import {Command} from "@/model/command.ts";
import {GraphState, LlmCall} from "@/model/graphstate.ts";

type CommandFactory = (event: CommunicationEvent) => (graphState: GraphState) => void;

const createAgentStartCommand: CommandFactory = (event) => {
    return (graphState) => {
            const node = graphState.getOrCreateAgent(event.acting_agent);
            node.running = true
        }
};

const createAgentEndCommand: CommandFactory = (event) => {
    return (graphState) => {
            const node = graphState.getOrCreateAgent(event.acting_agent);
            node.running = false
        }
};

const getText = (message: TextContent | ToolResponse | ToolCall): string => {
    if ('text' in message) {
        return message.text;
    }
    return message.tool_name;
};

const createLlmCallStartCommand: CommandFactory = (event: LLMCallStartEvent) => {
    return (graphState) => {
            const node = graphState.getOrCreateAgent(event.acting_agent);

            node.llmCalls = [
                ...node.llmCalls,
                ...event.content.content.map(message => ({
                    text: getText(message),
                    state: "outgoing"
                } as LlmCall))
            ]
        }
};

const createLlmCallEndCommand: CommandFactory = (event: LLMCallEndEvent) => {
    return(graphState) => {
            const node = graphState.getOrCreateAgent(event.acting_agent);

            node.llmCalls = [
                ...node.llmCalls,
                ...event.content.parts.map(message => ({
                    text: getText(message),
                    state: "incoming"
                } as LlmCall))
            ]
        }
};

const createLlmCallErrorCommand: CommandFactory = (event: LLMCallErrorEvent) => {
    return (graphState) => {
            const node = graphState.getOrCreateAgent(event.acting_agent);

            node.llmCalls = [
                ...node.llmCalls,
                {
                    text: event.error,
                    state: "error"
                }
            ]
        }
};

const createToolCallStartCommand: CommandFactory = (event: ToolCallStartEvent) => {
    return (graphState) => {
            const node = graphState.getOrCreateAgent(event.acting_agent);

            node.toolCalls = [
                ...node.toolCalls,
                {
                    name: event.tool_call.tool_name,
                    state: "outgoing"
                }
            ]
        }
};

const createToolCallEndCommand: CommandFactory = (event: ToolCallEndEvent) => {
    return (graphState) => {
            const node = graphState.getOrCreateAgent(event.acting_agent);

            node.toolCalls = [
                ...node.toolCalls,
                {
                    name: event.tool_call.tool_name,
                    state: "incoming"
                }
            ]
        }
};

const createToolCallErrorCommand: CommandFactory = (event: ToolCallErrorEvent) => {
    return (graphState) => {
            const node = graphState.getOrCreateAgent(event.acting_agent);

            node.toolCalls = [
                ...node.toolCalls,
                {
                    name: event.error,
                    state: "error"
                }
            ]
        }
};

const createInvokeAgentStartCommand: CommandFactory = (event: InvokeAgentStartEvent) => {
    return (graphState) => {
            graphState.getOrCreateAgent(event.acting_agent);
            graphState.getOrCreateAgent(event.invoked_agent);

            const edge = graphState.getOrCreateA2aCall(event.acting_agent, event.invoked_agent);
            edge.running = true;
        }
};

const createInvokeAgentEndCommand: CommandFactory = (event: InvokeAgentEndEvent) => {
    return (graphState) => {
            const edge = graphState.getOrCreateA2aCall(event.acting_agent, event.invoked_agent);
            edge.running = false;
        }
};

// Command factory registry
const commandFactories: Record<string, CommandFactory> = {
    'agent_start': createAgentStartCommand,
    'agent_end': createAgentEndCommand,
    'llm_call_start': createLlmCallStartCommand,
    'llm_call_end': createLlmCallEndCommand,
    'llm_call_error': createLlmCallErrorCommand,
    'tool_call_start': createToolCallStartCommand,
    'tool_call_end': createToolCallEndCommand,
    'tool_call_error': createToolCallErrorCommand,
    'invoke_agent_start': createInvokeAgentStartCommand,
    'invoke_agent_end': createInvokeAgentEndCommand,
};

export const createCommandFromEvent = (event: CommunicationEvent): Command | null => {
    if (!event.event_type) return null;
    const factory = commandFactories[event.event_type];
    if (!factory) {
        console.warn('Unknown event type:', event.event_type);
        return null;
    }
    return new Command(
        event.event_type,
        factory(event)
    );
};