import { renderHook } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import useWebSocket from 'react-use-websocket';
import { useWebSocketCommands } from './useWebSocketCommands';
import { createCommandFromEvent } from '@/lib/commandFactory';
import { CommunicationEvent } from '@/model/events';

// Mock dependencies
vi.mock('react-use-websocket');
vi.mock('@/lib/commandFactory');

describe('useWebSocketCommands', () => {
    const mockUrl = 'ws://localhost:10005/ws';
    const mockCreateCommandFromEvent = vi.mocked(createCommandFromEvent);
    const mockUseWebSocket = vi.mocked(useWebSocket);

    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('should return null when no message is received', () => {
        mockUseWebSocket.mockReturnValue({
            lastJsonMessage: null,
            sendMessage: vi.fn(),
            sendJsonMessage: vi.fn(),
            readyState: 1,
            getWebSocket: vi.fn(),
        } as any);

        const { result } = renderHook(() => useWebSocketCommands(mockUrl));

        expect(result.current).toBeNull();
        expect(mockCreateCommandFromEvent).not.toHaveBeenCalled();
    });

    it('should create command from valid WebSocket message', () => {
        const mockMessage: CommunicationEvent = {
            event_type: 'agent_start',
            acting_agent: 'test-agent',
            conversation_id: 'conv-123',
            timestamp: '2024-01-01T00:00:00Z',
            invocation_id: 'inv-123',
        };

        const mockCommand = {
            type: 'agent_start',
            execute: vi.fn(),
        };

        mockUseWebSocket.mockReturnValue({
            lastJsonMessage: mockMessage,
            sendMessage: vi.fn(),
            sendJsonMessage: vi.fn(),
            readyState: 1,
            getWebSocket: vi.fn(),
        } as any);

        mockCreateCommandFromEvent.mockReturnValue(mockCommand as any);

        const { result } = renderHook(() => useWebSocketCommands(mockUrl));

        expect(mockCreateCommandFromEvent).toHaveBeenCalledWith(mockMessage);
        expect(result.current).toBe(mockCommand);
    });

    it('should handle null command from createCommandFromEvent', () => {
        const mockMessage: CommunicationEvent = {
            event_type: 'unknown_event' as any,
            acting_agent: 'test-agent',
            conversation_id: 'conv-123',
            timestamp: '2024-01-01T00:00:00Z',
            invocation_id: 'inv-123',
        };

        mockUseWebSocket.mockReturnValue({
            lastJsonMessage: mockMessage,
            sendMessage: vi.fn(),
            sendJsonMessage: vi.fn(),
            readyState: 1,
            getWebSocket: vi.fn(),
        } as any);

        mockCreateCommandFromEvent.mockReturnValue(null);

        const { result } = renderHook(() => useWebSocketCommands(mockUrl));

        expect(mockCreateCommandFromEvent).toHaveBeenCalledWith(mockMessage);
        expect(result.current).toBeNull();
    });

    it('should update command when new message is received', () => {
        const firstMessage: CommunicationEvent = {
            event_type: 'agent_start',
            acting_agent: 'agent-1',
            conversation_id: 'conv-123',
            timestamp: '2024-01-01T00:00:00Z',
            invocation_id: 'inv-123',
        };

        const secondMessage: CommunicationEvent = {
            event_type: 'agent_end',
            acting_agent: 'agent-1',
            conversation_id: 'conv-123',
            timestamp: '2024-01-01T00:00:01Z',
            invocation_id: 'inv-123',
        };

        const firstCommand = { type: 'agent_start', execute: vi.fn() };
        const secondCommand = { type: 'agent_end', execute: vi.fn() };

        // First render with first message
        mockUseWebSocket.mockReturnValue({
            lastJsonMessage: firstMessage,
            sendMessage: vi.fn(),
            sendJsonMessage: vi.fn(),
            readyState: 1,
            getWebSocket: vi.fn(),
        } as any);

        mockCreateCommandFromEvent.mockReturnValue(firstCommand as any);

        const { result, rerender } = renderHook(() => useWebSocketCommands(mockUrl));

        expect(result.current).toBe(firstCommand);

        // Update with second message
        mockUseWebSocket.mockReturnValue({
            lastJsonMessage: secondMessage,
            sendMessage: vi.fn(),
            sendJsonMessage: vi.fn(),
            readyState: 1,
            getWebSocket: vi.fn(),
        } as any);

        mockCreateCommandFromEvent.mockReturnValue(secondCommand as any);

        rerender();

        expect(result.current).toBe(secondCommand);
        expect(mockCreateCommandFromEvent).toHaveBeenCalledWith(secondMessage);
    });

    it('should memoize command creation', () => {
        const mockMessage: CommunicationEvent = {
            event_type: 'agent_start',
            acting_agent: 'test-agent',
            conversation_id: 'conv-123',
            timestamp: '2024-01-01T00:00:00Z',
            invocation_id: 'inv-123',
        };

        const mockCommand = {
            type: 'agent_start',
            execute: vi.fn(),
        };

        mockUseWebSocket.mockReturnValue({
            lastJsonMessage: mockMessage,
            sendMessage: vi.fn(),
            sendJsonMessage: vi.fn(),
            readyState: 1,
            getWebSocket: vi.fn(),
        } as any);

        mockCreateCommandFromEvent.mockReturnValue(mockCommand as any);

        const { result, rerender } = renderHook(() => useWebSocketCommands(mockUrl));

        const firstResult = result.current;

        // Rerender without changing the message
        rerender();

        const secondResult = result.current;

        // Should return the same memoized value
        expect(firstResult).toBe(secondResult);
        // Should only have been called once
        expect(mockCreateCommandFromEvent).toHaveBeenCalledTimes(1);
    });

    it('should connect to the correct WebSocket URL', () => {
        const customUrl = 'wss://custom.example.com/ws';

        mockUseWebSocket.mockReturnValue({
            lastJsonMessage: null,
            sendMessage: vi.fn(),
            sendJsonMessage: vi.fn(),
            readyState: 1,
            getWebSocket: vi.fn(),
        } as any);

        renderHook(() => useWebSocketCommands(customUrl));

        expect(mockUseWebSocket).toHaveBeenCalledWith(customUrl);
    });
});