import React from 'react';
import { Handle, Position } from '@xyflow/react';
import { Loader2, Activity, CircleX } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface AgentNodeData {
  name: string;
  status: 'running' | 'active' | 'inactive';
  connections: string[];
  messages: Array<{
    type: 'incoming' | 'outgoing';
    content: string;
    timestamp: string;
  }>;
}

interface AgentNodeProps {
  data: AgentNodeData;
  selected?: boolean;
}

export function AgentNode({ data, selected }: AgentNodeProps) {
  const getStatusIcon = () => {
    switch (data.status) {
      case 'running':
        return <Loader2 className="w-4 h-4 animate-spin-slow text-agent-running" />;
      case 'active':
        return <Activity className="w-4 h-4 text-agent-active" />;
      case 'inactive':
        return <CircleX className="w-4 h-4 text-red-500" />;
      default:
        return <CircleX className="w-4 h-4 text-red-500" />;
    }
  };

  const getStatusTextColor = () => {
    switch (data.status) {
      case 'running':
        return 'text-orange-500';
      case 'active':
        return 'text-green-500';
      case 'inactive':
        return 'text-red-500';
      default:
        return 'text-red-500';
    }
  };

  const getStatusColor = () => {
    switch (data.status) {
      case 'running':
        return 'border-transparent shadow-agent';
      case 'active':
        return 'border-white';
      case 'inactive':
        return 'border-agent-inactive';
      default:
        return 'border-agent-inactive';
    }
  };

  const getHandleColor = () => {
    switch (data.status) {
      case 'running':
      case 'active':
        return 'bg-white border-2 border-background';
      case 'inactive':
        return 'bg-agent-inactive border-2 border-background';
      default:
        return 'bg-agent-inactive border-2 border-background';
    }
  };

  const getSelectionColor = () => {
    switch (data.status) {
      case 'running':
      case 'active':
        return 'ring-white';
      case 'inactive':
        return 'ring-gray-500';
      default:
        return 'ring-gray-500';
    }
  };

  return (
    <div
      className={cn(
        'relative bg-card border rounded-lg p-4 min-w-[200px] shadow-lg transition-all duration-300 cursor-pointer hover:scale-105',
        getStatusColor(),
        selected && `ring-1 ${getSelectionColor()} ring-offset-2 ring-offset-background`
      )}
    >
      {/* Animated SVG border for running agents */}
      {data.status === 'running' && (
        <svg
          className="absolute inset-0 w-full h-full pointer-events-none"
          style={{ borderRadius: '0.5rem' }}
        >
          <rect
            x="1"
            y="1"
            width="calc(100% - 2px)"
            height="calc(100% - 2px)"
            rx="7"
            ry="7"
            fill="none"
            stroke="white"
            strokeWidth="1"
            strokeDasharray="8 4"
            className="animate-flow-dash"
            style={{
              filter: 'drop-shadow(0 0 6px rgba(255, 255, 255, 0.6))'
            }}
          />
        </svg>
      )}
      {/* Input Handles */}
      <Handle
        type="target"
        position={Position.Top}
        className={cn("w-3 h-3", getHandleColor())}
      />
      <Handle
        type="target"
        position={Position.Left}
        className={cn("w-3 h-3", getHandleColor())}
      />

      {/* Agent Content */}
      <div className="flex items-start gap-3 mb-2">
        {getStatusIcon()}
        <div>
          <h3 className="font-semibold text-foreground text-sm">{data.name}</h3>
          <p className={cn("text-xs capitalize", getStatusTextColor())}>{data.status}</p>
        </div>
      </div>

      {/* Connection Count */}
      <div className="text-xs text-muted-foreground ml-7">
        {data.connections.length} connections
      </div>

      {/* Output Handles */}
      <Handle
        type="source"
        position={Position.Bottom}
        className={cn("w-3 h-3", getHandleColor())}
      />
      <Handle
        type="source"
        position={Position.Right}
        className={cn("w-3 h-3", getHandleColor())}
      />
    </div>
  );
}