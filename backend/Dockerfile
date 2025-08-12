FROM python:3.13-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy workspace configuration files for dependency resolution
COPY uv.lock pyproject.toml ./

# Install dependencies
RUN uv sync --frozen

# Copy source code after dependency installation
COPY . ./backend

# Expose port
EXPOSE 8000

# Run FastAPI application with uv and uvicorn
CMD uv run uvicorn backend.src.main:app --host 0.0.0.0 --port 8000