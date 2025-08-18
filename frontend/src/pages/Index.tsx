import React, { useState } from 'react';
import { WorkflowSidebar } from '@/components/WorkflowSidebar';
import { WorkflowHeader } from '@/components/WorkflowHeader';
import { WorkflowCanvas } from '@/components/WorkflowCanvas';
import { AgentOverlay } from '@/components/AgentOverlay';
import { AgentNodeData } from '@/components/AgentNode';

const Index = () => {
  const [overlayOpen, setOverlayOpen] = useState(false);
  const [overlayExpanded, setOverlayExpanded] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState<AgentNodeData | null>(null);

  const handleNodeClick = (nodeId: string, nodeData: AgentNodeData) => {
    setSelectedAgent(nodeData);
    setOverlayOpen(true);
    setOverlayExpanded(false);
  };

  const handleCloseOverlay = () => {
    setOverlayOpen(false);
    setSelectedAgent(null);
  };

  return (
    <div className="min-h-screen bg-background text-foreground dark">
      <div className="flex h-screen w-full">
        {/* Sidebar */}
        <WorkflowSidebar />

        {/* Main Content */}
        <div className="flex-1 flex flex-col">
          {/* Header */}
          <WorkflowHeader
            flowName="Claims Processing Flow"
            onRefresh={() => console.log('Refreshing...')}
          />

          {/* Canvas */}
          <div className="flex-1 relative">
            <WorkflowCanvas onNodeClick={handleNodeClick} onPaneClick={handleCloseOverlay} />
            
            {/* Overlay */}
            <AgentOverlay
              isOpen={overlayOpen}
              onClose={handleCloseOverlay}
              agentData={selectedAgent}
              isExpanded={overlayExpanded}
              onToggleExpand={() => setOverlayExpanded(!overlayExpanded)}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;
