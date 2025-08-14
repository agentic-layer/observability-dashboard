# Agent Communication Dashboard - Backend

Implementation details for the Agent Communication Dashboard backend service.

## Core Components

### FastAPI Application (`main.py`)
Entry point that sets up the FastAPI app and includes routers. The actual endpoints are organized into separate route modules.

### API Routes (`api/routes/`)
- **`traces.py`**: OTLP trace ingestion endpoint that receives protobuf data and processes it into events
- **`websockets.py`**: WebSocket endpoints for global and conversation-specific event streaming

### Core Business Logic (`core/`)
- **`span_preprocessor.py`**: Converts OpenTelemetry spans into typed events by extracting semantic attributes, mapping span kinds to event types, and preserving tracing context
- **`connection_manager.py`**: Manages WebSocket connections with global broadcast and conversation-specific routing
- **`state.py`**: Global application state management for connection managers and shared resources

### Data Models (`models/`)
- **`events.py`**: Structured dataclasses for communication events (agent lifecycle, LLM calls, tool invocations)
- **`content.py`**: Content type definitions for LLM requests/responses and tool interactions

### Utilities (`utils/`)
- **`extractors.py`**: Attribute extraction logic for parsing OTLP span data
- **`factories.py`**: Factory functions for creating specific event types from span data

## Development

### Setup
```bash
uv sync
```

### Code Quality
```bash
uv run poe check      # Run all quality checks
uv run poe mypy       # Type checking
uv run poe ruff       # Linting and formatting
uv run poe bandit     # Security analysis
```

### Running Locally

You have several options to run the backend service locally:

#### Option 1: Direct with uv + FastAPI
```bash
# Development server with hot reload
uv run fastapi dev src/agent_monitor/main.py

# Production-like server
uv run fastapi run src/agent_monitor/main.py
```

#### Option 2: Kubernetes with Tilt
```bash
# From project root:
tilt up

# The backend will be available at http://localhost:10005
# Tilt UI available at http://localhost:10350
```