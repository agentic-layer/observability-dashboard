import React from 'react';
import { Button } from '@/components/ui/button';
import { RefreshCw, Settings } from 'lucide-react';

interface WorkflowHeaderProps {
  flowName: string;
}

export function WorkflowHeader({ 
  flowName, 
}: WorkflowHeaderProps) {
  return (
    <div className="h-16 bg-background border-b border-border flex items-center justify-between px-6">
      {/* Flow Name */}
      <div className="flex items-end gap-3">
        <h1 className="text-xl font-semibold text-foreground">{flowName}</h1>
      </div>

    </div>
  );
}