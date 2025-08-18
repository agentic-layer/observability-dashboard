import React from 'react';
import { Button } from '@/components/ui/button';
import { RefreshCw, Settings } from 'lucide-react';

interface WorkflowHeaderProps {
  flowName: string;
  onRefresh: () => void;
}

export function WorkflowHeader({ 
  flowName, 
  onRefresh 
}: WorkflowHeaderProps) {
  return (
    <div className="h-16 bg-background border-b border-border flex items-center justify-between px-6">
      {/* Flow Name */}
      <div className="flex items-end gap-3">
        <h1 className="text-xl font-semibold text-foreground">{flowName}</h1>
        <p className="text-sm text-muted-foreground">
          Last updated: just now
        </p>
      </div>

    </div>
  );
}