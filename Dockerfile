# Stage 1: Build React frontend
FROM node:24 AS frontend-builder
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
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --link-mode=copy

# Copy source code after dependency installation
COPY app/ ./app/

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose port
EXPOSE 8000

# Run FastAPI application with uv and fastapi
ENTRYPOINT ["uv", "run", "fastapi", "run"]
