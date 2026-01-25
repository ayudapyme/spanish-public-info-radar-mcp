# syntax=docker/dockerfile:1
# Public Radar MCP Server Dockerfile

FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for package management
RUN pip install uv

# Copy dependency files and README (required by hatchling)
COPY pyproject.toml uv.lock README.md ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY src/ ./src/

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Default environment variables
ENV LOG_LEVEL="INFO"

# Health check - MCP SSE server doesn't have a /health endpoint by default
# Use process check instead
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD pgrep -f "public_radar" || exit 1

# Expose MCP server port
EXPOSE 8080

# Default command - run MCP SSE server (HTTP transport)
CMD ["uv", "run", "python", "-m", "public_radar", "--port", "8080"]
