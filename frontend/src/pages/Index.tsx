import React from 'react';
import {WorkflowSidebar} from '@/components/WorkflowSidebar';
import {WorkflowHeader} from '@/components/WorkflowHeader';
import {DashboardCanvas} from '@/components/DashboardCanvas';
import {getWebSocketUrl} from '@/config/websocket';

const Index = () => {

    return (
        <div className="min-h-screen bg-background text-foreground dark">
            <div className="flex h-screen w-full">
                {/* Sidebar */}
                <WorkflowSidebar/>

                {/* Main Content */}
                <div className="flex-1 flex flex-col">
                    {/* Header */}
                    <WorkflowHeader
                        flowName="Observability Dashboard"
                    />

                    {/* Dashboard Canvas */}
                    <DashboardCanvas websocketUrl={getWebSocketUrl()} />
                </div>
            </div>
        </div>
    );
};

export default Index;
