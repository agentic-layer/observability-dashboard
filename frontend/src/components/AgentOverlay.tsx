
import React, { useState, useEffect } from 'react';
import { X, Maximize2, Minimize2, MessageCircle, ArrowRight, ArrowLeft, ChevronDown, ChevronUp } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { AgentNodeData } from './AgentNode';

interface AgentOverlayProps {
  isOpen: boolean;
  onClose: () => void;
  agentData: AgentNodeData | null;
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
  const [expandedMessageIndex, setExpandedMessageIndex] = useState<number | null>(null);
  
  // Reset expanded message when overlay collapses
  useEffect(() => {
    if (!isExpanded) {
      setExpandedMessageIndex(null);
    }
  }, [isExpanded]);
  
  if (!isOpen || !agentData) return null;

  const handleMessageClick = (index: number) => {
    if (expandedMessageIndex === index) {
      setExpandedMessageIndex(null);
    } else {
      setExpandedMessageIndex(index);
      if (!isExpanded) {
        onToggleExpand();
      }
    }
  };

  const handleMessageHeaderClick = (index: number, e: React.MouseEvent) => {
    e.stopPropagation();
    setExpandedMessageIndex(null);
  };

  return (
    <div 
      className={cn(
        'fixed top-0 right-0 h-full bg-background border-l border-border shadow-overlay z-50 transition-all duration-300 ease-out',
        isExpanded ? 'w-2/3' : 'w-80',
        isOpen ? 'animate-slide-in-right' : 'animate-slide-out-right'
      )}
      style={{ minWidth: '200px' }}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border">
        <h2 className="text-lg font-semibold text-foreground">{agentData.name}</h2>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={onToggleExpand}
            className="h-8 w-8 p-0"
          >
            {isExpanded ? (
              <Minimize2 className="w-4 h-4" />
            ) : (
              <Maximize2 className="w-4 h-4" />
            )}
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="h-8 w-8 p-0"
          >
            <X className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Content */}
      <div className="p-4 space-y-6 h-full overflow-y-auto">
        {/* Connected Agents */}
        <div>
          <h3 className="text-sm font-medium text-foreground mb-3">Connected Agents</h3>
          <div className="space-y-2">
            {agentData.connections.map((connectionId) => {
              // Map connection IDs to agent names and statuses
              const getAgentInfo = (id: string) => {
                const agentInfo: Record<string, { name: string; status: 'running' | 'active' | 'inactive' }> = {
                  '1': { name: 'Claims Agent', status: 'running' },
                  '2': { name: 'Validation Agent', status: 'active' }, 
                  '3': { name: 'Processing Agent', status: 'inactive' }
                };
                return agentInfo[id] || { name: `Agent ${id}`, status: 'inactive' };
              };
              
              const agentInfo = getAgentInfo(connectionId);
              
              const getDotColor = (status: string) => {
                switch (status) {
                  case 'running':
                    return 'bg-orange-500';
                  case 'active':
                    return 'bg-green-500';
                  case 'inactive':
                    return 'bg-red-500';
                  default:
                    return 'bg-red-500';
                }
              };
              
              return (
                <div 
                  key={connectionId}
                  className="flex items-center gap-2 p-2 rounded-lg bg-muted/50 text-sm"
                >
                  <div className={cn("w-2 h-2 rounded-full", getDotColor(agentInfo.status))} />
                  <span className="text-foreground">{agentInfo.name}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Message History */}
        <div>
          <h3 className="text-sm font-medium text-foreground mb-3">Recent Messages</h3>
          <div className="space-y-3 flex-1 overflow-y-auto">
            {agentData.messages.map((message, index) => {
              const claimNames = ['Claims Agent', 'Claims Agent'];
              const arrows = [ArrowRight, ArrowLeft];
              const ArrowIcon = arrows[index] || ArrowRight;
              const claimName = claimNames[index] || `Agent ${index + 1}`;
              
              const messageTexts = [
                "Im Rahmen der Bearbeitung der Schadensmeldung CLM-45892 (eingereicht am 25. Juli 2025 durch Herrn Markus Weber, Versicherungsnehmer-Nr. 112589) benötige ich Ihre Unterstützung bei der Verifizierung einiger Angaben.\n\nBitte prüfen Sie insbesondere:\n\nEchtheit der eingereichten Rechnungen (Anhang: \"Rechnungen_Weber.pdf\") – insbesondere die Rechnung der Firma \"TechNova GmbH\" vom 20.07.2025.\n\nVor-Ort-Inspektion des Schadensorts in 10115 Berlin – falls möglich bis spätestens 05. August 2025.\n\nFotodokumentation zur Bestätigung der gemeldeten Schäden an den elektronischen Geräten.\n\nSollten Sie zusätzliche Informationen benötigen, lassen Sie es mich bitte wissen. Ich habe die relevanten Dokumente beigefügt.",
                "Ich habe mit der Prüfung der Schadensmeldung CLM-45892 begonnen. Hier ein kurzer Zwischenstand:\n\nRechnungsprüfung:\nDie Rechnung der TechNova GmbH vom 20.07.2025 weist Unstimmigkeiten auf – insbesondere fehlt die USt-ID, und die Formatierung unterscheidet sich von früheren Rechnungen dieser Firma. Ich habe bereits eine Anfrage zur Echtheitsbestätigung an TechNova geschickt.\n\nVor-Ort-Inspektion:\nEin Termin für die Begehung des Schadensorts in Berlin ist für Freitag, den 02. August 2025 um 10:00 Uhr angesetzt. Der Versicherungsnehmer wurde informiert und hat bereits zugesagt.\n\nFotodokumentation:\nIch werde direkt im Anschluss an die Besichtigung eine Fotodokumentation anfertigen und Ihnen bis spätestens 05. August 2025 zukommen lassen.\n\nSobald mir eine Rückmeldung von TechNova vorliegt oder sich sonstige relevante Informationen ergeben, melde ich mich umgehend."
              ];
              const messageContent = messageTexts[index] || message.content;
              const isExpanded = expandedMessageIndex === index;
              
              return (
                <div 
                  key={index}
                  className={cn(
                    "rounded-lg bg-muted/50 cursor-pointer transition-all duration-200",
                    isExpanded ? "bg-muted" : "hover:bg-muted/70"
                  )}
                  onClick={() => handleMessageClick(index)}
                >
                  <div className="flex items-start gap-3 p-3">
                    <div className="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 bg-muted-foreground">
                      <ArrowIcon className="w-3 h-3 text-white" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div 
                        className="flex items-center justify-between cursor-pointer"
                        onClick={(e) => isExpanded ? handleMessageHeaderClick(index, e) : undefined}
                      >
                        <p className="text-sm font-medium text-foreground">{claimName}</p>
                        <div className="flex items-center gap-2">
                          <p className="text-xs text-muted-foreground">{message.timestamp}</p>
                          {isExpanded ? (
                            <ChevronUp className="w-4 h-4 text-muted-foreground" />
                          ) : (
                            <ChevronDown className="w-4 h-4 text-muted-foreground" />
                          )}
                        </div>
                      </div>
                      
                      {isExpanded ? (
                        <div className="mt-3 text-left">
                          <div className="text-sm text-white whitespace-pre-wrap break-words font-sans" style={{ maxWidth: '80ch' }}>
                            {messageContent}
                          </div>
                        </div>
                      ) : (
                        <p className={cn("text-sm text-muted-foreground mt-1", !isExpanded && "truncate")}>{messageContent}</p>
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
