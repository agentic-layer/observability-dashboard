# Observability Dashboard for Agentic Systems

This repository provides a real-time observability service designed specifically for monitoring complex, multi-agent systems. It ingests **OpenTelemetry** traces, transforms them into structured communication events, and broadcasts them via **WebSocket** for live monitoring and analysis.

The primary goal is to solve the observability challenge in agentic systems by providing a centralized hub for understanding agent behavior, communication patterns, and overall system performance.

-----

## Key Features

  - **Trace Ingestion**: Receives OpenTelemetry traces from agent frameworks via OTLP/HTTP.
  - **Event Processing**: Converts raw telemetry spans into structured events (agent lifecycle, LLM calls, tool invocations).
  - **Real-time Streaming**: Broadcasts processed events to WebSocket clients for live dashboard updates.
  - **Conversation Filtering**: Supports both global event streams and filtering by a specific conversation ID.

-----

## Table of Contents

- [How It Works](#how-it-works)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [End-to-End (E2E) Testing](#end-to-end-e2e-testing)
- [API Reference and Integration](#api-reference-and-integration)
- [Contributing](#contributing)


-----

## How It Works

The service acts as a pipeline, processing telemetry data and making it available for real-time consumption.

1.  **Agent Instruments**: Your agentic application is instrumented with OpenTelemetry to emit traces.
2.  **Ingestion Endpoint**: The service receives these traces at its OTLP/HTTP endpoint (`/v1/traces`).
3.  **Span Processing**: A core preprocessor (`span_preprocessor.py`) parses the trace spans, extracting key attributes and mapping them to structured event models (e.g., `AgentStart`, `LLMCall`, `ToolOutput`).
4.  **WebSocket Broadcast**: The processed events are immediately broadcasted through a connection manager to all subscribed WebSocket clients.

-----

## Prerequisites

To build, run, and contribute to this project, you'll need the following tools installed.

| Tool | Notes                                                                       |
| :--- |:----------------------------------------------------------------------------|
| **Python** | The core programming language.                                              |
| **uv** | A fast Python package installer and virtual environment manager.            |
| **Docker** | For containerized deployment.                                               |
| **pre-commit**| Manages pre-commit hooks. Installed via `brew bundle`.                      |
| **tilt** | For local multi-service Kubernetes development. Installed via `brew bundle`.|
| **Kubernetes**| Required for local development with Tilt.                                   |

-----

## Getting Started

Follow these steps to get the application running on your local machine.

### 1\. Install Dependencies

Install system-level and Python dependencies.

```bash
# Install system dependencies using Homebrew
brew bundle

# Install Python packages using uv
uv sync
```

### 2\. Run the Application

You can run the service directly with `uv` or in a Kubernetes cluster using `tilt`.

**Option A: Locally with `uv`**

This is the simplest way to get started.

```bash
# Start a development server with hot-reloading
make dev
```
```bash
# Or, start a production-like server
make run
```
Once running, you can access the following endpoints:

  - **API Server**: http://localhost:10005
  - **Health Check**: http://localhost:10005/health
  - **API Docs (Swagger)**: http://localhost:10005/docs

**Option B: With Kubernetes with Tilt**

This method is ideal for simulating a production environment.

```bash
# Ensure your local Kubernetes cluster is running, then start tilt
tilt up
```
The application will be available at http://localhost:10005, with the Tilt UI at http://localhost:10350.


## End-to-End (E2E) Testing

The project includes a comprehensive test suite to ensure reliability and correctness.

### Prerequisites for Testing

  * All Python dependencies must be installed via `uv sync`.
  * The tests utilize mock span data located at `tests/mock_spans.json`. No running database or external services are required.

### Running the Test Suite

Use the following commands to execute the tests:

```bash
# Run the full test suite once
make test
```

The integration tests validate the complete workflow, from OTLP trace ingestion to WebSocket event broadcasting.

-----

## API Reference and Integration

You can integrate your agentic applications by sending telemetry data to the ingestion endpoint and connecting a client to the WebSocket stream.


| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/v1/traces` | Receives OpenTelemetry traces in protobuf format. |
| `WS` | `/ws` | Subscribes a client to the **global** event stream. |
| `WS` | `/ws/{conversation_id}` | Subscribes a client to a **conversation-specific** stream. |

### Agent Framework Setup

Configure your agents to send OpenTelemetry traces to:
```
http://localhost:10005/v1/traces
```

### WebSocket Client Connection

Events can be consumed by connecting to the WebSocket endpoint. For example with websocat:

```shell
websocat ws://localhost:10005/ws
```

Or in the browser console (replace url with your server address):

```javascript
new WebSocket('ws://observability-dashboard:10005/ws').onmessage = (event) => {
  console.log('Agent event:', JSON.parse(event.data));
}
```

### Event Types

The system processes OpenTelemetry traces into structured communication events. For complete event definitions and schemas, see [`app/models/events.py`](app/models/events.py).

### Conversation ID Validation
- Conversation IDs must be valid UUID4 strings (e.g., `123e4567-e89b-12d3-a456-426614174000`)
- Fixed length: 36 characters
- Format: `^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$` (case-insensitive)

-----

## Contributing

We welcome contributions\! Please follow these guidelines to ensure a smooth development process. Please read the [Contributing Guide](https://github.com/agentic-layer/.github?tab=contributing-ov-file) for more details.

### One-Time Setup

**Important**: After cloning the repository, you **must** install the pre-commit hooks. This enforces code quality standards automatically on every commit.

```bash
pre-commit install
```
### Documentation
Documentation is located in the [`/docs`](/docs) directory.

We use the **[Diátaxis framework](https://diataxis.fr/)** for structure and **Antora** to build the site. Please adhere to these conventions when making updates.

### Code Quality

We use the following tools to maintain high code quality. All are orchestrated by `pre-commit` and can be run manually.

| Command             | Description                                                              |
|:--------------------|:-------------------------------------------------------------------------|
| `make check-fix`    | Runs the linters and formatters and attempt to fix issues automatically. |
| `make check`        | Run all checks and tests                                                 |
