# Observability Dashboard for Agentic Systems

A real-time observability service for multi-agent systems. It ingests **OpenTelemetry** traces over OTLP/HTTP, converts spans into structured agent events (lifecycle, LLM calls, tool invocations), and broadcasts them via **WebSocket** for live dashboards.

📖 **Documentation:** https://docs.agentic-layer.ai/observability-dashboard/

## Development

### Prerequisites

- **Python** 3.13+
- **uv** (Python package and venv manager)
- **Docker**
- **pre-commit**, **tilt**, **kubectl** (all installable via `brew bundle`)
- A local Kubernetes cluster (only needed for the Tilt path)

### Build and run locally

```shell
# Install system dependencies
brew bundle
# Install Python dependencies
uv sync
# Install pre-commit hooks (one-time)
pre-commit install

# Hot-reloading dev server
make dev
# Or, production-like server
make run
# Or, run inside a local Kubernetes cluster
tilt up
```

The service listens on `http://localhost:10005` (Tilt UI: `http://localhost:10350`).

### Test

```shell
make check-fix  # linters and formatters with auto-fix
make check      # all checks and tests
make test       # tests only
```

### Verify the local deploy

Confirm the service is up and accepting traces:

```shell
# Health probe
curl http://localhost:10005/health
# Subscribe to the global event stream
websocat ws://localhost:10005/ws
```

To generate traffic, point an agent's `OTEL_EXPORTER_OTLP_ENDPOINT` at `http://localhost:10005/v1/traces`.

## Contributing

See the [Contribution Guide](https://github.com/agentic-layer/.github?tab=contributing-ov-file). Documentation lives in [`docs/`](docs/) (AsciiDoc, [Diátaxis](https://diataxis.fr/) layout, built with Antora).
