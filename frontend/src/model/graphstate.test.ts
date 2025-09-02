import { describe, it, expect, beforeEach } from 'vitest';
import { GraphState, Agent, A2aCall } from './graphstate';

describe('GraphState', () => {
    let graphState: GraphState;

    beforeEach(() => {
        graphState = new GraphState();
    });

    describe('constructor', () => {
        it('should initialize with empty agents and a2aCalls arrays', () => {
            expect(graphState.agents).toEqual([]);
            expect(graphState.a2aCalls).toEqual([]);
        });
    });

    describe('getOrCreateAgent', () => {
        it('should create a new agent if it does not exist', () => {
            const agent = graphState.getOrCreateAgent('agent-1');
            
            expect(agent).toBeInstanceOf(Agent);
            expect(agent.id).toBe('agent-1');
            expect(graphState.agents).toHaveLength(1);
            expect(graphState.agents[0]).toBe(agent);
        });

        it('should return existing agent if it already exists', () => {
            const firstCall = graphState.getOrCreateAgent('agent-1');
            const secondCall = graphState.getOrCreateAgent('agent-1');
            
            expect(firstCall).toBe(secondCall);
            expect(graphState.agents).toHaveLength(1);
        });

        it('should handle multiple different agents', () => {
            const agent1 = graphState.getOrCreateAgent('agent-1');
            const agent2 = graphState.getOrCreateAgent('agent-2');
            const agent3 = graphState.getOrCreateAgent('agent-3');
            
            expect(graphState.agents).toHaveLength(3);
            expect(agent1.id).toBe('agent-1');
            expect(agent2.id).toBe('agent-2');
            expect(agent3.id).toBe('agent-3');
        });

        it('should preserve agent state when returning existing agent', () => {
            const agent = graphState.getOrCreateAgent('agent-1');
            agent.running = true;
            agent.llmCalls.push({ state: 'outgoing', text: 'test' });
            
            const sameAgent = graphState.getOrCreateAgent('agent-1');
            
            expect(sameAgent.running).toBe(true);
            expect(sameAgent.llmCalls).toHaveLength(1);
            expect(sameAgent.llmCalls[0]).toEqual({ state: 'outgoing', text: 'test' });
        });
    });

    describe('getOrCreateA2aCall', () => {
        it('should create a new A2aCall if it does not exist', () => {
            const a2aCall = graphState.getOrCreateA2aCall('agent-1', 'agent-2');
            
            expect(a2aCall).toBeInstanceOf(A2aCall);
            expect(a2aCall.source_id).toBe('agent-1');
            expect(a2aCall.target_id).toBe('agent-2');
            expect(a2aCall.id).toBe('agent-1-agent-2');
            expect(graphState.a2aCalls).toHaveLength(1);
            expect(graphState.a2aCalls[0]).toBe(a2aCall);
        });

        it('should return existing A2aCall if it already exists', () => {
            const firstCall = graphState.getOrCreateA2aCall('agent-1', 'agent-2');
            const secondCall = graphState.getOrCreateA2aCall('agent-1', 'agent-2');
            
            expect(firstCall).toBe(secondCall);
            expect(graphState.a2aCalls).toHaveLength(1);
        });

        it('should create different A2aCall for different agent pairs', () => {
            const call1 = graphState.getOrCreateA2aCall('agent-1', 'agent-2');
            const call2 = graphState.getOrCreateA2aCall('agent-2', 'agent-3');
            const call3 = graphState.getOrCreateA2aCall('agent-1', 'agent-3');
            
            expect(graphState.a2aCalls).toHaveLength(3);
            expect(call1.id).toBe('agent-1-agent-2');
            expect(call2.id).toBe('agent-2-agent-3');
            expect(call3.id).toBe('agent-1-agent-3');
        });

        it('should treat different order of agents as different A2aCall', () => {
            const call1 = graphState.getOrCreateA2aCall('agent-1', 'agent-2');
            const call2 = graphState.getOrCreateA2aCall('agent-2', 'agent-1');
            
            expect(graphState.a2aCalls).toHaveLength(2);
            expect(call1.id).toBe('agent-1-agent-2');
            expect(call2.id).toBe('agent-2-agent-1');
            expect(call1).not.toBe(call2);
        });

        it('should preserve A2aCall state when returning existing call', () => {
            const a2aCall = graphState.getOrCreateA2aCall('agent-1', 'agent-2');
            a2aCall.running = true;
            
            const sameCall = graphState.getOrCreateA2aCall('agent-1', 'agent-2');
            
            expect(sameCall.running).toBe(true);
        });
    });

    describe('integration scenarios', () => {
        it('should handle complex agent network creation', () => {
            // Create a network of agents with multiple connections
            const agent1 = graphState.getOrCreateAgent('orchestrator');
            const agent2 = graphState.getOrCreateAgent('worker-1');
            const agent3 = graphState.getOrCreateAgent('worker-2');
            
            const call1to2 = graphState.getOrCreateA2aCall('orchestrator', 'worker-1');
            const call1to3 = graphState.getOrCreateA2aCall('orchestrator', 'worker-2');
            const call2to3 = graphState.getOrCreateA2aCall('worker-1', 'worker-2');
            
            // Simulate some activity
            agent1.running = true;
            call1to2.running = true;
            agent2.running = true;
            agent2.llmCalls.push({ state: 'outgoing', text: 'Processing request' });
            call1to2.running = false;
            agent2.running = false;
            
            expect(graphState.agents).toHaveLength(3);
            expect(graphState.a2aCalls).toHaveLength(3);
            expect(agent1.running).toBe(true);
            expect(agent2.running).toBe(false);
            expect(agent2.llmCalls).toHaveLength(1);
        });

        it('should handle agent self-reference', () => {
            const agent = graphState.getOrCreateAgent('recursive-agent');
            const selfCall = graphState.getOrCreateA2aCall('recursive-agent', 'recursive-agent');
            
            expect(graphState.agents).toHaveLength(1);
            expect(graphState.a2aCalls).toHaveLength(1);
            expect(selfCall.source_id).toBe('recursive-agent');
            expect(selfCall.target_id).toBe('recursive-agent');
            expect(selfCall.id).toBe('recursive-agent-recursive-agent');
        });
    });
});

describe('Agent', () => {
    describe('constructor', () => {
        it('should initialize with correct defaults', () => {
            const agent = new Agent('test-agent');
            
            expect(agent.id).toBe('test-agent');
            expect(agent.running).toBe(false);
            expect(agent.llmCalls).toEqual([]);
            expect(agent.toolCalls).toEqual([]);
        });

        it('should handle different agent IDs', () => {
            const agent1 = new Agent('agent-1');
            const agent2 = new Agent('agent-2');
            const agentWithSpecialChars = new Agent('agent_with-special.chars');
            
            expect(agent1.id).toBe('agent-1');
            expect(agent2.id).toBe('agent-2');
            expect(agentWithSpecialChars.id).toBe('agent_with-special.chars');
        });
    });

    describe('state management', () => {
        it('should allow modifying running state', () => {
            const agent = new Agent('test-agent');
            
            expect(agent.running).toBe(false);
            
            agent.running = true;
            expect(agent.running).toBe(true);
            
            agent.running = false;
            expect(agent.running).toBe(false);
        });

        it('should allow adding LLM calls', () => {
            const agent = new Agent('test-agent');
            
            agent.llmCalls.push({ state: 'outgoing', text: 'Query 1' });
            agent.llmCalls.push({ state: 'incoming', text: 'Response 1' });
            agent.llmCalls.push({ state: 'error', text: 'Error occurred' });
            
            expect(agent.llmCalls).toHaveLength(3);
            expect(agent.llmCalls[0]).toEqual({ state: 'outgoing', text: 'Query 1' });
            expect(agent.llmCalls[1]).toEqual({ state: 'incoming', text: 'Response 1' });
            expect(agent.llmCalls[2]).toEqual({ state: 'error', text: 'Error occurred' });
        });

        it('should allow adding tool calls', () => {
            const agent = new Agent('test-agent');
            
            agent.toolCalls.push({ state: 'outgoing', name: 'calculator' });
            agent.toolCalls.push({ state: 'incoming', name: 'calculator' });
            agent.toolCalls.push({ state: 'error', name: 'database_query' });
            
            expect(agent.toolCalls).toHaveLength(3);
            expect(agent.toolCalls[0]).toEqual({ state: 'outgoing', name: 'calculator' });
            expect(agent.toolCalls[1]).toEqual({ state: 'incoming', name: 'calculator' });
            expect(agent.toolCalls[2]).toEqual({ state: 'error', name: 'database_query' });
        });

        it('should maintain separate arrays for llmCalls and toolCalls', () => {
            const agent = new Agent('test-agent');
            
            agent.llmCalls.push({ state: 'outgoing', text: 'LLM query' });
            agent.toolCalls.push({ state: 'outgoing', name: 'tool' });
            
            expect(agent.llmCalls).toHaveLength(1);
            expect(agent.toolCalls).toHaveLength(1);
            expect(agent.llmCalls[0]).toEqual({ state: 'outgoing', text: 'LLM query' });
            expect(agent.toolCalls[0]).toEqual({ state: 'outgoing', name: 'tool' });
        });
    });
});

describe('A2aCall', () => {
    describe('constructor', () => {
        it('should initialize with correct defaults', () => {
            const a2aCall = new A2aCall('source-agent', 'target-agent');
            
            expect(a2aCall.id).toBe('source-agent-target-agent');
            expect(a2aCall.source_id).toBe('source-agent');
            expect(a2aCall.target_id).toBe('target-agent');
            expect(a2aCall.running).toBe(false);
        });

        it('should handle different agent ID combinations', () => {
            const call1 = new A2aCall('agent-1', 'agent-2');
            const call2 = new A2aCall('agent-2', 'agent-1');
            const call3 = new A2aCall('agent-with-long-name', 'another-agent-with-long-name');
            
            expect(call1.id).toBe('agent-1-agent-2');
            expect(call2.id).toBe('agent-2-agent-1');
            expect(call3.id).toBe('agent-with-long-name-another-agent-with-long-name');
        });

        it('should handle self-referential calls', () => {
            const selfCall = new A2aCall('same-agent', 'same-agent');
            
            expect(selfCall.id).toBe('same-agent-same-agent');
            expect(selfCall.source_id).toBe('same-agent');
            expect(selfCall.target_id).toBe('same-agent');
        });
    });

    describe('state management', () => {
        it('should allow modifying running state', () => {
            const a2aCall = new A2aCall('source', 'target');
            
            expect(a2aCall.running).toBe(false);
            
            a2aCall.running = true;
            expect(a2aCall.running).toBe(true);
            
            a2aCall.running = false;
            expect(a2aCall.running).toBe(false);
        });

        it('should maintain independent state for different calls', () => {
            const call1 = new A2aCall('agent-1', 'agent-2');
            const call2 = new A2aCall('agent-2', 'agent-3');
            
            call1.running = true;
            call2.running = false;
            
            expect(call1.running).toBe(true);
            expect(call2.running).toBe(false);
        });
    });

    describe('ID generation', () => {
        it('should generate unique IDs for different agent pairs', () => {
            const call1 = new A2aCall('a', 'b');
            const call2 = new A2aCall('b', 'a');
            const call3 = new A2aCall('a', 'c');
            const call4 = new A2aCall('c', 'b');
            
            const ids = [call1.id, call2.id, call3.id, call4.id];
            const uniqueIds = new Set(ids);
            
            expect(uniqueIds.size).toBe(4);
        });

        it('should handle special characters in agent IDs', () => {
            const call = new A2aCall('agent_with-special.chars', 'another@agent');
            
            expect(call.id).toBe('agent_with-special.chars-another@agent');
            expect(call.source_id).toBe('agent_with-special.chars');
            expect(call.target_id).toBe('another@agent');
        });
    });
});

describe('Type definitions', () => {
    it('State type should accept valid values', () => {
        const validStates: Array<'incoming' | 'outgoing' | 'error'> = ['incoming', 'outgoing', 'error'];
        
        validStates.forEach(state => {
            const llmCall = { state, text: 'test' };
            const toolCall = { state, name: 'test' };
            
            expect(llmCall.state).toBe(state);
            expect(toolCall.state).toBe(state);
        });
    });
});