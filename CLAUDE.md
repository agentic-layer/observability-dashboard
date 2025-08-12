# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains an agentic communications dashboard. The main components are:

- **Backend**: Located in `backend/`, contains a FastAPI service for receiving OpenTelemetry traces, processing them into communication events, and broadcasting via WebSocket connections

## Architecture

- **FastAPI Service** (`backend/src/main.py`): REST API endpoints for trace ingestion and WebSocket connections
- **Span Preprocessor** (`backend/src/span_preprocessor.py`): Converts OpenTelemetry spans into structured communication events
- **Connection Manager** (`backend/src/connection_manager.py`): Manages WebSocket connections and message broadcasting
- **Event Models** (`backend/src/events.py`): Dataclass definitions for different event types (agent lifecycle, LLM calls, tool calls)

## Development Setup

```shell
# Install dependencies
brew bundle

# Install Python dependencies
uv sync
```

## Dependencies

- Python 3.13+
- uv for dependency management
- FastAPI for REST API and WebSocket support
- OpenTelemetry proto for trace processing
- Uvicorn as ASGI server