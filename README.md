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

The backend service processes incoming traces and broadcasts structured events to connected WebSocket clients. See [`backend/README.md`](backend/README.md) for implementation details.

## Prerequisites

- **Python 3.13+**: Required for the backend service
- **uv**: Package manager for Python projects
- **Kubernetes cluster**: Required for Tilt development (see Local Kubernetes Setup below)

## Setup

### 1. Install Dependencies

```bash
# Install system dependencies
brew bundle

# Install Python dependencies
cd backend
uv sync
```

### 2. Running Locally (Backend)

See [backend/README.md](backend/README.md) for detailed instructions on running the service locally.

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

The system processes OpenTelemetry traces into structured communication events. For complete event definitions and schemas, see [`backend/src/agent_monitor/models/events.py`](backend/src/agent_monitor/models/events.py).

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