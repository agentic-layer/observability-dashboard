import React from 'react';

interface WorkflowSidebarProps {}

export function WorkflowSidebar({}: WorkflowSidebarProps) {
  return (
    <div className="w-16 h-full bg-sidebar border-r border-sidebar-border flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-sidebar-border flex items-center justify-center">
        <img 
          src="/lovable-uploads/50ee3c48-fd20-4583-97ee-3f53bf1c0c89.png" 
          alt="Logo" 
          className="w-8 h-8"
        />
      </div>
    </div>
  );
}