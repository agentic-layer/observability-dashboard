# Stage 1: Build React frontend
FROM node:22-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python backend with static files
FROM python:3.13-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy workspace configuration files for dependency resolution
COPY uv.lock pyproject.toml ./

# Install dependencies
RUN uv sync --frozen

# Copy source code after dependency installation
COPY src/ ./src/

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose port
EXPOSE 8000

# Run FastAPI application with uv and fastapi
CMD ["uv", "run", "fastapi", "run", "src/agent_monitor/main.py"]
