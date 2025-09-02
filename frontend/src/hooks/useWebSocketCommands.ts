import {useMemo} from 'react';
import useWebSocket from 'react-use-websocket';
import {CommunicationEvent} from '@/model/events';
import {createCommandFromEvent} from '@/lib/commandFactory.ts';

export function useWebSocketCommands(url: string) {
    const { lastJsonMessage } = useWebSocket<CommunicationEvent>(url);
    return useMemo(() => {
        if (!lastJsonMessage) return null;

        return createCommandFromEvent(lastJsonMessage);
    }, [lastJsonMessage]);
}