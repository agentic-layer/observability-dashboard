import React from 'react';
import logoBoxPng from '../assets/Logo-Box-2.png';


interface WorkflowSidebarProps {}

export function WorkflowSidebar({}: WorkflowSidebarProps) {
  return (
    <div className="w-16 h-full bg-sidebar border-r border-sidebar-border flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-sidebar-border flex items-center justify-center">
        <img 
          src={logoBoxPng}
          alt="Logo" 
          className="w-8 h-8"
        />
      </div>
    </div>
  );
}