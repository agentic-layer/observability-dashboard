import { describe, it, expect, beforeEach, vi } from 'vitest';
import { createCommandFromEvent } from './commandFactory';
import {
    CommunicationEvent,
    LLMCallStartEvent,
    LLMCallEndEvent,
    LLMCallErrorEvent,
    ToolCallStartEvent,
    ToolCallEndEvent,
    ToolCallErrorEvent,
    InvokeAgentStartEvent,
    InvokeAgentEndEvent
} from '@/model/events';
import { GraphState } from '@/model/graphstate';
import { Command } from '@/model/command';

describe('commandFactory', () => {
    let mockGraphState: GraphState;
    let mockAgent: any;
    let mockEdge: any;

    beforeEach(() => {
        mockAgent = {
            running: false,
            llmCalls: [],
            toolCalls: []
        };
        
        mockEdge = {
            running: false
        };

        mockGraphState = {
            getOrCreateAgent: vi.fn().mockReturnValue(mockAgent),
            getOrCreateA2aCall: vi.fn().mockReturnValue(mockEdge)
        } as any;
    });

    describe('createCommandFromEvent', () => {
        it('should return null for event without event_type', () => {
            const event = {
                acting_agent: 'test-agent',
                conversation_id: 'conv-123',
                timestamp: '2024-01-01T00:00:00Z',
                invocation_id: 'inv-123'
            } as any;

            const command = createCommandFromEvent(event);
            expect(command).toBeNull();
        });

        it('should return null for unknown event type', () => {
            const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
            const event: CommunicationEvent = {
                event_type: 'unknown_event' as any,
                acting_agent: 'test-agent',
                conversation_id: 'conv-123',
                timestamp: '2024-01-01T00:00:00Z',
                invocation_id: 'inv-123'
            };

            const command = createCommandFromEvent(event);
            
            expect(command).toBeNull();
            expect(consoleSpy).toHaveBeenCalledWith('Unknown event type:', 'unknown_event');
            
            consoleSpy.mockRestore();
        });

        it('should create Command instance with correct type and execute function', () => {
            const event: CommunicationEvent = {
                event_type: 'agent_start',
                acting_agent: 'test-agent',
                conversation_id: 'conv-123',
                timestamp: '2024-01-01T00:00:00Z',
                invocation_id: 'inv-123'
            };

            const command = createCommandFromEvent(event);
            
            expect(command).toBeInstanceOf(Command);
            expect(command?.type).toBe('agent_start');
            expect(command?.execute).toBeInstanceOf(Function);
        });
    });

    describe('agent commands', () => {
        it('should handle agent_start event', () => {
            const event: CommunicationEvent = {
                event_type: 'agent_start',
                acting_agent: 'test-agent',
                conversation_id: 'conv-123',
                timestamp: '2024-01-01T00:00:00Z',
                invocation_id: 'inv-123'
            };

            const command = createCommandFromEvent(event);
            command?.execute(mockGraphState);

            expect(mockGraphState.getOrCreateAgent).toHaveBeenCalledWith('test-agent');
            expect(mockAgent.running).toBe(true);
        });

        it('should handle agent_end event', () => {
            const event: CommunicationEvent = {
                event_type: 'agent_end',
                acting_agent: 'test-agent',
                conversation_id: 'conv-123',
                timestamp: '2024-01-01T00:00:00Z',
                invocation_id: 'inv-123'
            };

            mockAgent.running = true;
            const command = createCommandFromEvent(event);
            command?.execute(mockGraphState);

            expect(mockGraphState.getOrCreateAgent).toHaveBeenCalledWith('test-agent');
            expect(mockAgent.running).toBe(false);
        });
    });

    describe('LLM call commands', () => {
        it('should handle llm_call_start event with text content', () => {
            const event: LLMCallStartEvent = {
                event_type: 'llm_call_start',
                acting_agent: 'test-agent',
                conversation_id: 'conv-123',
                timestamp: '2024-01-01T00:00:00Z',
                invocation_id: 'inv-123',
                content: {
                    role: 'user',
                    content: [
                        { text: 'Hello, world!', thought: false }
                    ]
                }
            };

            const command = createCommandFromEvent(event);
            command?.execute(mockGraphState);

            expect(mockGraphState.getOrCreateAgent).toHaveBeenCalledWith('test-agent');
            expect(mockAgent.llmCalls).toEqual([
                { text: 'Hello, world!', state: 'outgoing' }
            ]);
        });

        it('should handle llm_call_start event with tool call content', () => {
            const event: LLMCallStartEvent = {
                event_type: 'llm_call_start',
                acting_agent: 'test-agent',
                conversation_id: 'conv-123',
                timestamp: '2024-01-01T00:00:00Z',
                invocation_id: 'inv-123',
                content: {
                    role: 'user',
                    content: [
                        { 
                            tool_name: 'search_tool',
                            response: { }
                        }
                    ]
                }
            };

            const command = createCommandFromEvent(event);
            command?.execute(mockGraphState);

            expect(mockGraphState.getOrCreateAgent).toHaveBeenCalledWith('test-agent');
            expect(mockAgent.llmCalls).toEqual([
                { text: 'search_tool', state: 'outgoing' }
            ]);
        });

        it('should handle llm_call_end event', () => {
            const event: LLMCallEndEvent = {
                event_type: 'llm_call_end',
                acting_agent: 'test-agent',
                conversation_id: 'conv-123',
                timestamp: '2024-01-01T00:00:00Z',
                invocation_id: 'inv-123',
                content: {
                    role: 'user',
                    parts: [
                        { text: 'Response text', thought: false }
                    ]
                }
            };

            const command = createCommandFromEvent(event);
            command?.execute(mockGraphState);

            expect(mockGraphState.getOrCreateAgent).toHaveBeenCalledWith('test-agent');
            expect(mockAgent.llmCalls).toEqual([
                { text: 'Response text', state: 'incoming' }
            ]);
        });

        it('should handle llm_call_error event', () => {
            const event: LLMCallErrorEvent = {
                event_type: 'llm_call_error',
                acting_agent: 'test-agent',
                conversation_id: 'conv-123',
                timestamp: '2024-01-01T00:00:00Z',
                invocation_id: 'inv-123',
                error: 'API rate limit exceeded'
            };

            const command = createCommandFromEvent(event);
            command?.execute(mockGraphState);

            expect(mockGraphState.getOrCreateAgent).toHaveBeenCalledWith('test-agent');
            expect(mockAgent.llmCalls).toEqual([
                { text: 'API rate limit exceeded', state: 'error' }
            ]);
        });

        it('should append multiple LLM calls', () => {
            mockAgent.llmCalls = [
                { text: 'Existing call', state: 'incoming' }
            ];

            const event: LLMCallStartEvent = {
                event_type: 'llm_call_start',
                acting_agent: 'test-agent',
                conversation_id: 'conv-123',
                timestamp: '2024-01-01T00:00:00Z',
                invocation_id: 'inv-123',
                content: {
                    role: 'user',
                    content: [
                        { text: 'First message', thought: false },
                        { text: 'Second message', thought: false}
                    ]
                }
            };

            const command = createCommandFromEvent(event);
            command?.execute(mockGraphState);

            expect(mockAgent.llmCalls).toEqual([
                { text: 'Existing call', state: 'incoming' },
                { text: 'First message', state: 'outgoing' },
                { text: 'Second message', state: 'outgoing' }
            ]);
        });
    });

    describe('tool call commands', () => {
        it('should handle tool_call_start event', () => {
            const event: ToolCallStartEvent = {
                event_type: 'tool_call_start',
                acting_agent: 'test-agent',
                conversation_id: 'conv-123',
                timestamp: '2024-01-01T00:00:00Z',
                invocation_id: 'inv-123',
                tool_call: {
                    tool_name: 'calculator',
                    arguments: {  }
                }
            };

            const command = createCommandFromEvent(event);
            command?.execute(mockGraphState);

            expect(mockGraphState.getOrCreateAgent).toHaveBeenCalledWith('test-agent');
            expect(mockAgent.toolCalls).toEqual([
                { name: 'calculator', state: 'outgoing' }
            ]);
        });

        it('should handle tool_call_end event', () => {
            const event: ToolCallEndEvent = {
                event_type: 'tool_call_end',
                acting_agent: 'test-agent',
                conversation_id: 'conv-123',
                timestamp: '2024-01-01T00:00:00Z',
                invocation_id: 'inv-123',
                tool_call: {
                    tool_name: 'calculator',
                    arguments: {  }
                },
                response: {
                    tool_name: 'calculator',
                    tool_result: '3'
                }
            };

            const command = createCommandFromEvent(event);
            command?.execute(mockGraphState);

            expect(mockGraphState.getOrCreateAgent).toHaveBeenCalledWith('test-agent');
            expect(mockAgent.toolCalls).toEqual([
                { name: 'calculator', state: 'incoming' }
            ]);
        });

        it('should handle tool_call_error event', () => {
            const event: ToolCallErrorEvent = {
                event_type: 'tool_call_error',
                acting_agent: 'test-agent',
                conversation_id: 'conv-123',
                timestamp: '2024-01-01T00:00:00Z',
                invocation_id: 'inv-123',
                error: 'Tool execution failed'
            };

            const command = createCommandFromEvent(event);
            command?.execute(mockGraphState);

            expect(mockGraphState.getOrCreateAgent).toHaveBeenCalledWith('test-agent');
            expect(mockAgent.toolCalls).toEqual([
                { name: 'Tool execution failed', state: 'error' }
            ]);
        });

        it('should append multiple tool calls', () => {
            mockAgent.toolCalls = [
                { name: 'existing_tool', state: 'incoming' }
            ];

            const event: ToolCallStartEvent = {
                event_type: 'tool_call_start',
                acting_agent: 'test-agent',
                conversation_id: 'conv-123',
                timestamp: '2024-01-01T00:00:00Z',
                invocation_id: 'inv-123',
                tool_call: {
                    tool_name: 'new_tool',
                    arguments: {}
                }
            };

            const command = createCommandFromEvent(event);
            command?.execute(mockGraphState);

            expect(mockAgent.toolCalls).toEqual([
                { name: 'existing_tool', state: 'incoming' },
                { name: 'new_tool', state: 'outgoing' }
            ]);
        });
    });

    describe('invoke agent commands', () => {
        it('should handle invoke_agent_start event', () => {
            const event: InvokeAgentStartEvent = {
                event_type: 'invoke_agent_start',
                acting_agent: 'parent-agent',
                invoked_agent: 'child-agent',
                conversation_id: 'conv-123',
                timestamp: '2024-01-01T00:00:00Z',
                invocation_id: 'inv-123'
            };

            const command = createCommandFromEvent(event);
            command?.execute(mockGraphState);

            expect(mockGraphState.getOrCreateAgent).toHaveBeenCalledWith('parent-agent');
            expect(mockGraphState.getOrCreateAgent).toHaveBeenCalledWith('child-agent');
            expect(mockGraphState.getOrCreateA2aCall).toHaveBeenCalledWith('parent-agent', 'child-agent');
            expect(mockEdge.running).toBe(true);
        });

        it('should handle invoke_agent_end event', () => {
            const event: InvokeAgentEndEvent = {
                event_type: 'invoke_agent_end',
                acting_agent: 'parent-agent',
                invoked_agent: 'child-agent',
                conversation_id: 'conv-123',
                timestamp: '2024-01-01T00:00:00Z',
                invocation_id: 'inv-123'
            };

            mockEdge.running = true;
            const command = createCommandFromEvent(event);
            command?.execute(mockGraphState);

            expect(mockGraphState.getOrCreateA2aCall).toHaveBeenCalledWith('parent-agent', 'child-agent');
            expect(mockEdge.running).toBe(false);
        });
    });

    describe('command execution integration', () => {
        it('should handle a sequence of related events', () => {
            const events: CommunicationEvent[] = [
                {
                    event_type: 'agent_start',
                    acting_agent: 'main-agent',
                    conversation_id: 'conv-123',
                    timestamp: '2024-01-01T00:00:00Z',
                    invocation_id: 'inv-123'
                },
                {
                    event_type: 'llm_call_start',
                    acting_agent: 'main-agent',
                    conversation_id: 'conv-123',
                    timestamp: '2024-01-01T00:00:01Z',
                    invocation_id: 'inv-123',
                    content: {
                        role: 'user',
                        content: [
                            { text: 'Query', thought: false }
                        ]
                    }
                } as LLMCallStartEvent,
                {
                    event_type: 'llm_call_end',
                    acting_agent: 'main-agent',
                    conversation_id: 'conv-123',
                    timestamp: '2024-01-01T00:00:02Z',
                    invocation_id: 'inv-123',
                    content: {
                        role: 'user',
                        parts: [
                            { text: 'Response', thought: false }
                        ]
                    }
                } as LLMCallEndEvent,
                {
                    event_type: 'agent_end',
                    acting_agent: 'main-agent',
                    conversation_id: 'conv-123',
                    timestamp: '2024-01-01T00:00:03Z',
                    invocation_id: 'inv-123'
                }
            ];

            events.forEach(event => {
                const command = createCommandFromEvent(event);
                expect(command).not.toBeNull();
                command?.execute(mockGraphState);
            });

            expect(mockAgent.running).toBe(false);
            expect(mockAgent.llmCalls).toEqual([
                { text: 'Query', state: 'outgoing' },
                { text: 'Response', state: 'incoming' }
            ]);
        });

        it('should handle mixed tool responses in llm_call_end', () => {
            const event: LLMCallEndEvent = {
                event_type: 'llm_call_end',
                acting_agent: 'test-agent',
                conversation_id: 'conv-123',
                timestamp: '2024-01-01T00:00:00Z',
                invocation_id: 'inv-123',
                content: {
                    role: 'user',
                    parts: [
                        { tool_name: 'search_tool', arguments: {} }
                    ]
                }
            };

            const command = createCommandFromEvent(event);
            command?.execute(mockGraphState);

            expect(mockAgent.llmCalls).toEqual([
                { text: 'search_tool', state: 'incoming' }
            ]);
        });
    });
});