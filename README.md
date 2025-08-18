# Observability Dashboard

A real-time observability service for monitoring agentic systems. Ingests OpenTelemetry traces from multi-agent applications and transforms them into structured communication events, broadcasting them via WebSocket for live monitoring.

## What This Project Does

This dashboard service solves the observability challenge in multi-agent systems by:

1. **Trace Ingestion**: Receives OpenTelemetry traces from agent frameworks via OTLP HTTP
2. **Event Processing**: Converts raw telemetry spans into structured communication events (agent lifecycle, LLM calls, tool invocations)
3. **Real-time Streaming**: Broadcasts processed events to WebSocket clients for live dashboard updates
4. **Conversation Filtering**: Supports both global event streams and conversation-specific filtering

The service acts as a centralized hub for understanding agent behavior, communication patterns, and system performance in production agentic applications.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Agent System  │───▶│  OTLP API        │───▶│  WebSocket      │
│  (OTLP Traces)  │    │  (/v1/traces)    │    │  Clients        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ Span Preprocessor│
                       │ (Event Creation) │
                       └──────────────────┘
```

The service processes incoming traces and broadcasts structured events to connected WebSocket clients.

## Implementation Details

### Core Components

#### FastAPI Application (`main.py`)
Entry point that sets up the FastAPI app and includes routers. The actual endpoints are organized into separate route modules.

#### API Routes (`api/routes/`)
- **`traces.py`**: OTLP trace ingestion endpoint that receives protobuf data and processes it into events
- **`websockets.py`**: WebSocket endpoints for global and conversation-specific event streaming

#### Core Business Logic (`core/`)
- **`span_preprocessor.py`**: Converts OpenTelemetry spans into typed events by extracting semantic attributes, mapping span kinds to event types, and preserving tracing context
- **`connection_manager.py`**: Manages WebSocket connections with global broadcast and conversation-specific routing
- **`state.py`**: Global application state management for connection managers and shared resources

#### Data Models (`models/`)
- **`events.py`**: Structured dataclasses for communication events (agent lifecycle, LLM calls, tool invocations)
- **`content.py`**: Content type definitions for LLM requests/responses and tool interactions

#### Utilities (`utils/`)
- **`extractors.py`**: Attribute extraction logic for parsing OTLP span data
- **`factories.py`**: Factory functions for creating specific event types from span data

## Prerequisites

- **Python 3.13+**: Required for the app
- **uv**: Package manager for Python projects
- **Kubernetes cluster**: Required for Tilt development (see Local Kubernetes Setup below)

## Setup

### 1. Install Dependencies

```bash
# Install system dependencies
brew bundle

# Install Python dependencies
uv sync

# Install frontend dependencies
cd frontend && npm install && cd ..
```

### 2. Running Locally

#### Option 1: Development Mode 

Run backend and frontend separately for hot reload:

```bash
# Terminal 1: Start the FastAPI backend
uv run fastapi dev src/agent_monitor/main.py

# Terminal 2: Start the React frontend with proxy
cd frontend && npm run dev
```

The application will be available at:
- **Frontend UI**: http://localhost:3000/ (with hot reload)
- **Backend API**: http://localhost:8000/ (API calls proxied from frontend)
- **API Documentation**: http://localhost:8000/docs

#### Option 2: Production Mode (Single container)

Build frontend and serve everything from FastAPI:

```bash
# Build the frontend
cd frontend && npm run build && cd ..

# Start the integrated server
uv run fastapi dev src/agent_monitor/main.py
```

The application will be available at:
- **Frontend UI**: http://localhost:8000/
- **API Documentation**: http://localhost:8000/docs

#### Option 3: Kubernetes with Tilt
```bash
# From project root:
tilt up

# The app will be available at http://localhost:10005
# Tilt UI available at http://localhost:10350
```

### 3. Code Quality

```bash
uv run poe check      # Run all quality checks
uv run poe mypy       # Type checking
uv run poe ruff       # Linting and formatting
uv run poe bandit     # Security analysis
```

## Local Kubernetes Setup

For local development, you need a Kubernetes cluster.
Use your preferred method to set up a local Kubernetes cluster. Docker Desktop, Ranger Desktop and Colima all provide standard Kubernetes clusters. Those are recommended.

Alternatively, use `k3d` for a lightweight solution.

Using `k3d`, create a local registry and cluster:
```bash
brew install k3d
k3d registry create local-paal-registry --port 6169
# Currently required for Colima users. See https://github.com/k3d-io/k3d/pull/1584
export K3D_FIX_DNS=0
k3d cluster create local-paal --registry-use k3d-local-paal-registry
```

## API Reference

### Trace Ingestion

- **POST** `/v1/traces` - Receives OpenTelemetry trace data (protobuf format) following the [OTLP specification](https://opentelemetry.io/docs/specs/otlp/#otlphttp-request)

### WebSocket Connections

- **WebSocket** `/ws/{conversation_id}` - Subscribe to events for a specific conversation
- **WebSocket** `/ws` - Subscribe to global event stream (all conversations)

## Event Types

The system processes OpenTelemetry traces into structured communication events. For complete event definitions and schemas, see [`src/agent_monitor/models/events.py`](backend/src/agent_monitor/models/events.py).

### Conversation ID Validation
- Conversation IDs must be valid UUID4 strings (e.g., `123e4567-e89b-12d3-a456-426614174000`)
- Fixed length: 36 characters
- Format: `^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$` (case-insensitive)

## Integration

### Agent Framework Setup

Configure your agents to send OpenTelemetry traces to:
```
http://observability-dashboard:8000/v1/traces
```

### WebSocket Client Connection

**Conversation-specific events**:
```javascript
const ws = new WebSocket('ws://observability-dashboard:8000/ws/your-conversation-id');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Agent event:', data);
};
```
