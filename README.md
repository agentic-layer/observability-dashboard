# Agent Communication Dashboard

A real-time dashboard backend service for monitoring and visualizing inter-agent communications through OpenTelemetry tracing data. Built with FastAPI and WebSocket support for live event streaming.

## Overview

The Agent Communication Dashboard processes OpenTelemetry traces from multi-agent systems and transforms them into structured communication events. These events are then broadcasted via WebSocket connections to enable real-time monitoring of agent interactions, LLM calls, tool invocations, and system events.

This service acts as the observability backbone for agentic systems, providing crucial insights into agent behavior and communication patterns.

## Architecture

### Components

- **FastAPI Service** (`backend/src/main.py`) - REST API endpoints and WebSocket management
- **Span Preprocessor** (`backend/src/span_preprocessor.py`) - Converts OpenTelemetry spans to communication events
- **Connection Manager** (`backend/src/connection_manager.py`) - Manages WebSocket connections and broadcasting
- **Event Models** (`backend/src/events.py`) - Structured dataclasses for different event types

### Event Flow

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Agent System  │───▶│  Dashboard API   │───▶│  WebSocket      │
│  (OTLP Traces)  │    │  (/v1/traces)    │    │  Clients        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ Span Preprocessor│
                       │ (Event Creation) │
                       └──────────────────┘
```

## Prerequisites

- **Python 3.13+**: Required for the backend service
- **Docker**: For containerized development
- **Kubernetes**: Local cluster (Docker Desktop, Rancher Desktop, Colima, or k3d)
- **Tilt**: For local development orchestration
- **uv**: Package manager for Python projects

## Setup

### 1. Install Dependencies

```bash
# Install system dependencies
brew bundle

# Install Python dependencies
cd backend
uv sync
```

### 2. Integration Setup

This service is designed to run as part of the [cross-selling-use-case](../cross-selling-use-case) system. Follow the setup instructions in that repository for the complete Kubernetes and Tilt configuration.

## Development

### Local Deployment

When integrated with the cross-selling use case, the dashboard backend is automatically deployed as part of the full system:

```bash
# From the cross-selling-use-case directory
tilt up

# The dashboard backend will be available at:
# http://localhost:10005
```

### Code Quality

The project includes comprehensive code quality tools:

```bash
# Run all checks
cd backend
uv run poe check

# Individual checks
uv run poe mypy          # Type checking
uv run poe ruff          # Linting and formatting
uv run poe bandit        # Security analysis
uv run poe lint-imports  # Import linting
```

## API Reference

### Trace Ingestion

- **POST** `/v1/traces` - Receives OpenTelemetry trace data (protobuf format)

### WebSocket Connections

- **WebSocket** `/ws/{conversation_id}` - Subscribe to events for a specific conversation
- **WebSocket** `/ws` - Subscribe to global event stream (all conversations)

## Event Types

The system processes traces into the following structured events:

### Agent Events
- `agent_start` - Agent initialization
- `agent_end` - Agent termination

### LLM Events
- `llm_call_start` - LLM request initiated
- `llm_call_end` - LLM response received
- `llm_call_error` - LLM request failed

### Tool Events
- `tool_call_start` - Tool invocation started
- `tool_call_end` - Tool execution completed
- `tool_call_error` - Tool execution failed
- `invoke_agent_start` - Agent-to-agent communication initiated
- `invoke_agent_end` - Agent-to-agent communication completed

## Configuration

### Environment Variables
- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 8000)

### Conversation ID Validation
- Conversation IDs must be valid UUID4 strings (e.g., `123e4567-e89b-12d3-a456-426614174000`)
- Fixed length: 36 characters
- Format: `^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$` (case-insensitive)

## Integration

### Agent Framework Setup

Configure your agents to send OpenTelemetry traces to:
```
http://dashboard-backend-host:8000/v1/traces
```

### WebSocket Client Connection

**Conversation-specific events**:
```javascript
const ws = new WebSocket('ws://dashboard-backend-host:8000/ws/your-conversation-id');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Agent event:', data);
};
```

**Global events**:
```javascript
const ws = new WebSocket('ws://dashboard-backend-host:8000/ws');
```

## Project Structure

```
├── backend/                      # Backend service implementation
│   ├── src/                      # Source code
│   │   ├── main.py               # FastAPI application
│   │   ├── span_preprocessor.py  # OpenTelemetry processing
│   │   ├── connection_manager.py # WebSocket management
│   │   └── events.py             # Event model definitions
│   ├── Dockerfile                # Container definition
│   └── pyproject.toml            # Python project configuration
├── CLAUDE.md                     # AI assistant instructions
└── README.md                     # Project documentation
```