export class GraphState {
    agents: Agent[];
    a2aCalls: A2aCall[];

    constructor() {
        this.agents = [];
        this.a2aCalls = [];
    }

    getOrCreateAgent(id: string) {
        return this.getAgent(id) || this.createAgent(id);
    }

    getOrCreateA2aCall(sourceId: string, targetId: string) {
        return this.getA2aCall(sourceId, targetId) || this.createA2aCall(sourceId, targetId);
    }

    private getAgent(id: string): Agent | undefined {
        return this.agents.find(agent => agent.id === id)
    }

    private getA2aCall(source_id: string, target_id: string): A2aCall | undefined {
        return this.a2aCalls.find(a2aCall => a2aCall.source_id === source_id && a2aCall.target_id === target_id)
    }

    private createAgent(id: string) {
        const newAgent = new Agent(id)
        this.agents.push(newAgent);
        return newAgent;
    }

    private createA2aCall(sourceId: string, targetId: string) {
        const newA2aCall = new A2aCall(sourceId, targetId);
        this.a2aCalls.push(newA2aCall);
        return newA2aCall;
    }
}

export class Agent {
    id: string;
    running: boolean;
    llmCalls: LlmCall[];
    toolCalls: ToolCall[];

    constructor(id: string)  {
        this.id = id
        this.running = false
        this.llmCalls = []
        this.toolCalls = []
    }
}

export class A2aCall {
    id: string;
    running: boolean;
    source_id: string;
    target_id: string;

    constructor(sourceId: string, targetId: string)  {
        this.id = `${sourceId}-${targetId}`
        this.source_id = sourceId
        this.target_id = targetId
        this.running = false
    }
}

export type State = "incoming" | "outgoing" | "error"

export interface LlmCall {
    state: State;
    text: string;
}

export interface ToolCall {
    state: State;
    name: string;
}