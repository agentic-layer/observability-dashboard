import React, {useState, useEffect} from 'react';
import {X, Maximize2, Minimize2, MessageCircle, ArrowRight, ArrowLeft} from 'lucide-react';
import {Button} from '@/components/ui/button';
import {cn} from '@/lib/utils';
import {Agent} from "@/model/graphstate.ts";

interface AgentOverlayProps {
    isOpen: boolean;
    onClose: () => void;
    agentData: Agent | null;
    isExpanded: boolean;
    onToggleExpand: () => void;
}

export function AgentOverlay({
                                 isOpen,
                                 onClose,
                                 agentData,
                                 isExpanded,
                                 onToggleExpand
                             }: AgentOverlayProps) {
    const [expandedLlmCallIndex, setExpandedLlmCallIndex] = useState<number | null>(null);
    const [expandedToolCallIndex, setExpandedToolCallIndex] = useState<number | null>(null);

    // Reset expanded message when overlay collapses
    useEffect(() => {
        if (!isExpanded) {
            setExpandedLlmCallIndex(null);
        }
    }, [isExpanded]);

    if (!isOpen || !agentData) return null;

    const handleLlmCallClick = (index: number) => {
        if (expandedLlmCallIndex === index) {
            setExpandedLlmCallIndex(null);
        } else {
            setExpandedLlmCallIndex(index);
            if (!isExpanded) {
                onToggleExpand();
            }
        }
    };

    const handleToolCallClick = (index: number) => {
        if (expandedToolCallIndex === index) {
            setExpandedToolCallIndex(null);
        } else {
            setExpandedToolCallIndex(index);
            if (!isExpanded) {
                onToggleExpand();
            }
        }
    };

    return (
        <div
            className={cn(
                'fixed top-0 right-0 h-full bg-background border-l border-border shadow-overlay z-50 transition-all duration-300 ease-out',
                isExpanded ? 'w-2/3' : 'w-80',
                isOpen ? 'animate-slide-in-right' : 'animate-slide-out-right'
            )}
            style={{minWidth: '200px'}}
        >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-border">
                <h2 className="text-lg font-semibold text-foreground">{agentData.id}</h2>
                <div className="flex items-center gap-2">
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={onToggleExpand}
                        className="h-8 w-8 p-0"
                    >
                        {isExpanded ? (
                            <Minimize2 className="w-4 h-4"/>
                        ) : (
                            <Maximize2 className="w-4 h-4"/>
                        )}
                    </Button>
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={onClose}
                        className="h-8 w-8 p-0"
                    >
                        <X className="w-4 h-4"/>
                    </Button>
                </div>
            </div>

            {/* Content */}
            <div className="p-4 space-y-6 h-full overflow-y-auto">
                {/* LLM Calls */}
                <div>
                    <h3 className="text-sm font-medium text-foreground mb-3">LLM Calls</h3>
                    <div className="space-y-3 flex-1 overflow-y-auto">
                        {agentData.llmCalls.map((llmCall, index) => {
                            const ArrowIcon = {
                                "incoming": ArrowLeft,
                                "outgoing": ArrowRight,
                                "error": MessageCircle
                            }[llmCall.state]
                            const isExpanded = expandedLlmCallIndex === index;

                            return (
                                <div
                                    key={index}
                                    className={cn(
                                        "rounded-lg bg-muted/50 cursor-pointer transition-all duration-200",
                                        isExpanded ? "bg-muted" : "hover:bg-muted/70"
                                    )}
                                    onClick={() => handleLlmCallClick(index)}
                                >
                                    <div className="flex items-start gap-3 p-3">
                                        <div
                                            className="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 bg-muted-foreground">
                                            <ArrowIcon className="w-3 h-3 text-white"/>
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            {isExpanded ? (
                                                <div className="mt-3 text-left">
                                                    <div
                                                        className="text-sm text-white whitespace-pre-wrap break-words font-sans"
                                                        style={{maxWidth: '80ch'}}>
                                                        {llmCall.text}
                                                    </div>
                                                </div>
                                            ) : (
                                                <p className={cn("text-sm text-muted-foreground mt-1", !isExpanded && "truncate")}>{llmCall.text}</p>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* Tool Calls */}
                <div>
                    <h3 className="text-sm font-medium text-foreground mb-3">Tool Calls</h3>
                    <div className="space-y-3 flex-1 overflow-y-auto">
                        {agentData.toolCalls.map((toolCall, index) => {
                            const ArrowIcon = {
                                "incoming": ArrowLeft,
                                "outgoing": ArrowRight,
                                "error": MessageCircle
                            }[toolCall.state];
                            const isExpanded = expandedToolCallIndex === index;

                            return (
                                <div
                                    key={index}
                                    className={cn(
                                        "rounded-lg bg-muted/50 cursor-pointer transition-all duration-200",
                                        isExpanded ? "bg-muted" : "hover:bg-muted/70"
                                    )}
                                    onClick={() => handleToolCallClick(index)}
                                >
                                    <div className="flex items-start gap-3 p-3">
                                        <div
                                            className="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 bg-muted-foreground">
                                            <ArrowIcon className="w-3 h-3 text-white"/>
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            {isExpanded ? (
                                                <div className="mt-3 text-left">
                                                    <div
                                                        className="text-sm text-white whitespace-pre-wrap break-words font-sans"
                                                        style={{maxWidth: '80ch'}}>
                                                        {toolCall.name}
                                                    </div>
                                                </div>
                                            ) : (
                                                <p className={cn("text-sm text-muted-foreground mt-1", !isExpanded && "truncate")}>{toolCall.name}</p>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>
        </div>
    );
}
