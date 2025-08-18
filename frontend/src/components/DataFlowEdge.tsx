import React from 'react';
import {
  EdgeProps,
  getSmoothStepPath,
} from '@xyflow/react';

export function DataFlowEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data,
}: EdgeProps) {
  const [edgePath] = getSmoothStepPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
    borderRadius: 8,
  });

  const isActive = (data as any)?.isActive || false;

  return (
    <>
      {/* Background edge */}
      <path
        id={`${id}-bg`}
        style={{
          stroke: isActive ? 'hsl(var(--border))' : 'hsl(var(--agent-inactive))',
          strokeWidth: 1,
          fill: 'none',
        }}
        className="react-flow__edge-path"
        d={edgePath}
      />
      
      {/* Active data flow overlay */}
      {isActive && (
        <path
          style={{
            stroke: 'white',
            strokeWidth: 1,
            fill: 'none',
            strokeDasharray: '8 4',
            filter: 'drop-shadow(0 0 6px rgba(255, 255, 255, 0.6))',
          }}
          className="react-flow__edge-path animate-flow-dash"
          d={edgePath}
        />
      )}
    </>
  );
}