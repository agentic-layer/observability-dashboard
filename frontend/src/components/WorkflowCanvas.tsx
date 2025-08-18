import React, { useCallback, useState } from 'react';
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
import { AgentNode } from './AgentNode';
import { DataFlowEdge } from './DataFlowEdge';

const nodeTypes: NodeTypes = {
  agent: AgentNode,
};

const edgeTypes: EdgeTypes = {
  dataFlow: DataFlowEdge,
};

const initialNodes: Node[] = [
  {
    id: '1',
    type: 'agent',
    position: { x: 100, y: 100 },
    data: {
      name: 'Claims Agent',
      status: 'running',
      connections: ['2', '3'],
      messages: [
        { type: 'incoming', content: 'Processing claim #CLM-2024-001', timestamp: '10:45 AM' },
        { type: 'outgoing', content: 'Validation complete', timestamp: '10:46 AM' },
      ]
    },
  },
  {
    id: '2',
    type: 'agent',
    position: { x: 400, y: 50 },
    data: {
      name: 'Validation Agent',
      status: 'active',
      connections: ['1', '3'],
      messages: [
        { type: 'incoming', content: 'Received validation request', timestamp: '10:46 AM' },
        { type: 'outgoing', content: 'Documents verified', timestamp: '10:47 AM' },
      ]
    },
  },
  {
    id: '3',
    type: 'agent',
    position: { x: 250, y: 250 },
    data: {
      name: 'Processing Agent',
      status: 'inactive',
      connections: ['1', '2'],
      messages: [
        { type: 'incoming', content: 'Awaiting input', timestamp: '10:40 AM' },
      ]
    },
  },
];

const initialEdges: Edge[] = [
  {
    id: '1-2',
    source: '1',
    target: '2',
    type: 'dataFlow',
    data: { isActive: true },
    style: { strokeWidth: 1 },
  },
  {
    id: '2-3',
    source: '2',
    target: '3',
    type: 'dataFlow',
    data: { isActive: false },
    style: { strokeWidth: 1 },
  },
  {
    id: '1-3',
    source: '1',
    target: '3',
    type: 'dataFlow',
    data: { isActive: true },
    style: { strokeWidth: 1 },
  },
];

interface WorkflowCanvasProps {
  onNodeClick: (nodeId: string, nodeData: any) => void;
  onPaneClick?: () => void;
}

export function WorkflowCanvas({ onNodeClick, onPaneClick }: WorkflowCanvasProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback(
    (params: Edge | Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const handleNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    onNodeClick(node.id, node.data);
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
        defaultViewport={{ x: 0, y: 0, zoom: 0.8 }}
        style={{ background: 'hsl(var(--background))' }}
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
