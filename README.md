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
- [Configuration](#configuration)
- [End-to-End (E2E) Testing](#end-to-end-e2e-testing)
- [Testing Tools and Their Configuration](#testing-tools-and-their-configuration)
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

| Tool | Version | Notes |
| :--- | :--- | :--- |
| **Python** | `>= 3.13` | The core programming language. |
| **uv** | `latest` | A fast Python package installer and virtual environment manager. |
| **Docker** | `>= 20.10+` | For containerized deployment. |
| **pre-commit**| `latest` | Manages pre-commit hooks. Installed via `brew bundle`. |
| **go-task** | `latest` | A modern task runner/build tool. Installed via `brew bundle`. |
| **tilt** | `latest` | For local multi-service Kubernetes development. Installed via `brew bundle`.|
| **Kubernetes**| `any` | Required for local development with Tilt. |

-----

## Getting Started

Follow these steps to get the application running on your local machine.

### 1. Clone the Repository

First, clone the project from GitHub:

```bash
git clone <repository-url>
cd <repository-directory>
````

### 2\. Install Dependencies

Install system-level and Python dependencies.

```bash
# Install system dependencies (pre-commit, go-task, tilt) using Homebrew
brew bundle

# Install Python packages using uv
uv sync
```

### 3\. Run the Application

You can run the service directly with `uv` or in a Kubernetes cluster using `tilt`.

**Option A: Locally with `uv`**

This is the simplest way to get started.

```bash
# Start a development server with hot-reloading
uv run fastapi dev src/agent_monitor/main.py
```
```bash
# Or, start a production-like server
uv run fastapi run src/agent_monitor/main.py
```
Once running, you can access the following endpoints:

  - **API Server**: `http://localhost:8000`
  - **Health Check**: `http://localhost:8000/health`
  - **API Docs (Swagger)**: `http://localhost:8000/docs`

**Option B: With Kubernetes with Tilt**

This method is ideal for simulating a production environment.

```bash
# Ensure your local Kubernetes cluster is running, then start tilt
tilt up
```
The application will be available at `http://localhost:10005`, with the Tilt UI at `http://localhost:10350`.


-----

## Configuration

Current configurations are managed within the source files.

Key configuration points include:

  * **Server Host/Port**: Defined in the FastAPI application startup logic in `src/agent_monitor/main.py`.
  * **Logging**: Configured in `src/agent_monitor/main.py`, with health check endpoints excluded from access logs.
  * **OTLP Span Processing**: Business logic is located in `src/agent_monitor/core/span_preprocessor.py`.

-----

## End-to-End (E2E) Testing

The project includes a comprehensive test suite to ensure reliability and correctness.

### Prerequisites for Testing

  * All Python dependencies must be installed via `uv sync`.
  * The tests utilize mock span data located at `tests/mock_spans.json`. No running database or external services are required.

### Running the Test Suite

Use the following commands to execute the tests:

```bash
# Run the full test suite once
uv run poe test
```
```bash
# Run tests in watch mode for continuous testing during development
uv run poe test-watch
```
```bash
# Run a specific test file with verbose output
uv run pytest tests/test_integration.py -v
```
```bash
# Run tests with coverage analysis
uv run pytest --cov=src/agent_monitor
```

The integration tests validate the complete workflow, from OTLP trace ingestion to WebSocket event broadcasting.

-----

## Testing Tools and Their Configuration


  * **Testing Framework**: **pytest** is used as the primary testing framework.
  * **API Testing**: FastAPI's `TestClient` is used for synchronous testing of asynchronous API endpoints and WebSocket connections.
  * **Mocking**: Test scenarios are driven by mock OpenTelemetry span data to simulate realistic agent interactions.


Tool configurations are centralized in `pyproject.toml`. The test execution commands are defined as tasks using `poe-the-poet`.

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
### Event Types

The system processes OpenTelemetry traces into structured communication events. For complete event definitions and schemas, see [`src/agent_monitor/models/events.py`](src/agent_monitor/models/events.py).

### Conversation ID Validation
- Conversation IDs must be valid UUID4 strings (e.g., `123e4567-e89b-12d3-a456-426614174000`)
- Fixed length: 36 characters
- Format: `^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$` (case-insensitive)

-----

## Contributing

We welcome contributions\! Please follow these guidelines to ensure a smooth development process.

### One-Time Setup

**Important**: After cloning the repository, you **must** install the pre-commit hooks. This enforces code quality standards automatically on every commit.

```bash
pre-commit install
```

### Development Workflow

1.  **Fork** the repository and create your branch from `main`.
2.  **Create a feature branch**: `git checkout -b feature/your-awesome-feature`.
3.  Make your changes, adhering to the project's code style.
4.  **Run all quality checks** locally before committing: `uv run poe check`.
5.  Submit a **Pull Request** with a clear description of your changes.

### Code Quality

We use the following tools to maintain high code quality. All are orchestrated by `pre-commit` and can be run manually.

| Command | Description | Tool |
| :--- | :--- | :--- |
| `uv run poe ruff`| Runs the linter and formatter. | **Ruff** |
| `uv run poe mypy`| Performs static type checking. | **Mypy** |
| `uv run poe bandit`| Scans for common security vulnerabilities. | **Bandit**|
| `uv run poe check`| Runs all of the above checks sequentially. | - |
