import React, { useState, useEffect } from 'react';
import { WorkflowCanvas } from './WorkflowCanvas';
import { AgentOverlay } from './AgentOverlay';
import { GraphState, Agent } from '@/model/graphstate';
import { Command } from '@/model/command';
import { useWebSocketCommands } from '@/hooks/useWebSocketCommands';

interface DashboardCanvasProps {
    websocketUrl: string;
}

export function DashboardCanvas({ websocketUrl }: DashboardCanvasProps) {
    const [overlayOpen, setOverlayOpen] = useState(false);
    const [overlayExpanded, setOverlayExpanded] = useState(false);
    const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
    const [commandHistory, setCommandHistory] = useState<Command[]>([]);
    const [graphState, setGraphState] = useState<GraphState>(new GraphState());

    const command = useWebSocketCommands(websocketUrl);

    // Effect to handle incoming commands
    useEffect(() => {
        if (!command) return;

        setCommandHistory(prev => [...prev, command]);
    }, [command]);

    useEffect(() => {
        if (commandHistory.length === 0) return;

        const newGraphState = new GraphState();

        for (const command of commandHistory) {
            command.execute(newGraphState);
        }
        setGraphState(newGraphState);
    }, [commandHistory]);

    const handleNodeClick = (nodeId: string) => {
        setSelectedAgent(graphState.agents.find(node => node.id === nodeId) || null);
        setOverlayOpen(true);
        setOverlayExpanded(false);
    };

    const handleCloseOverlay = () => {
        setOverlayOpen(false);
        setSelectedAgent(null);
    };

    return (
        <div className="flex-1 relative">
            <WorkflowCanvas
                onNodeClick={handleNodeClick}
                onPaneClick={handleCloseOverlay}
                graphState={graphState}
            />

            <AgentOverlay
                isOpen={overlayOpen}
                onClose={handleCloseOverlay}
                agentData={selectedAgent}
                isExpanded={overlayExpanded}
                onToggleExpand={() => setOverlayExpanded(!overlayExpanded)}
            />
        </div>
    );
}