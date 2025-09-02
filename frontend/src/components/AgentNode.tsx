import React from 'react';
import {Handle, Position} from '@xyflow/react';
import {Loader2, Activity} from 'lucide-react';
import {cn} from '@/lib/utils';
import {Agent} from "@/model/graphstate.ts";

interface AgentNodeProps {
    data: Agent;
    selected?: boolean;
}

export function AgentNode({data, selected}: AgentNodeProps) {
    const getStatusIcon = () => {
        if (data.running) {
            return <Loader2 className="w-4 h-4 animate-spin-slow text-agent-running"/>;
        } else {
            return <Activity className="w-4 h-4 text-agent-active"/>;
        }
    };

    const getStatusTextColor = () => {
        if(data.running) {
            return 'text-orange-500';
        } else {
            return 'text-green-500';
        }
    };

    const getStatusColor = () => {
        if(data.running) {
            return 'border-transparent shadow-agent';
        } else {
            return 'border-white';
        }
    };

    const getHandleColor = () => {
        return 'bg-white border-2 border-background';
    };

    const getSelectionColor = () => {
        return 'ring-white';
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
            {data.running && (
                <svg
                    className="absolute inset-0 w-full h-full pointer-events-none"
                    style={{borderRadius: '0.5rem'}}
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
                    <h3 className="font-semibold text-foreground text-sm">{data.id}</h3>
                    <p className={cn("text-xs capitalize", getStatusTextColor())}>{data.running ? "Running" : "Active"}</p>
                </div>
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