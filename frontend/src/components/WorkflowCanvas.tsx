import React, {useCallback, useEffect} from 'react';
import {
    ReactFlow,
    MiniMap,
    Controls,
    Background,
    BackgroundVariant,
    useNodesState,
    useEdgesState,
    addEdge,
    Connection,
    Edge,
    Node,
    NodeTypes,
    EdgeTypes,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import {AgentNode} from './AgentNode';
import {DataFlowEdge} from './DataFlowEdge';
import {GraphState} from "@/model/graphstate.ts";

const nodeTypes: NodeTypes = {
    agent: AgentNode,
};

const edgeTypes: EdgeTypes = {
    dataFlow: DataFlowEdge,
};

interface WorkflowCanvasProps {
    onNodeClick: (nodeId: string) => void;
    onPaneClick?: () => void;
    graphState: GraphState;
}

export function WorkflowCanvas({onNodeClick, onPaneClick, graphState}: WorkflowCanvasProps) {
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);

    useEffect(() => {
        setNodes(
            graphState.agents.map((agent, index) => ({
                id: agent.id,
                type: 'agent',
                position: {x: 100, y: index * 200},
                data: agent,
            }))
        )

        setEdges(
            graphState.a2aCalls.map((a2aCall) => ({
                id: a2aCall.id,
                source: a2aCall.source_id,
                target: a2aCall.target_id,
                type: 'dataFlow',
                data: a2aCall,
                style: {strokeWidth: 1},
            }))
        )
    }, [graphState, setNodes, setEdges]);

    const onConnect = useCallback(
        (params: Edge | Connection) => setEdges((eds) => addEdge(params, eds)),
        [setEdges]
    );

    const handleNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
        onNodeClick(node.id);
    }, [onNodeClick]);

    return (
        <div className="w-full h-full bg-background">
            <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onConnect={onConnect}
                onNodeClick={handleNodeClick}
                onPaneClick={onPaneClick}
                nodeTypes={nodeTypes}
                edgeTypes={edgeTypes}
                fitView
                minZoom={0.2}
                maxZoom={2}
                defaultViewport={{x: 0, y: 0, zoom: 0.8}}
                style={{background: 'hsl(var(--background))'}}
            >
                <Background
                    variant={BackgroundVariant.Dots}
                    color="hsl(var(--muted-foreground))"
                    gap={20}
                    size={1}
                />
                <Controls
                    className="bg-card border border-border rounded-lg shadow-lg"
                />
                <MiniMap
                    className="bg-card border border-border rounded-lg shadow-lg"
                    nodeColor="hsl(var(--muted))"
                    maskColor="hsl(var(--background) / 0.8)"
                />
            </ReactFlow>
        </div>
    );
}
