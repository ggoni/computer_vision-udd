# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS base

# Install system dependencies for ML and production
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install uv package manager
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# ============================================================================
# DEPENDENCIES STAGE
# ============================================================================
FROM base AS dependencies

# Copy project configuration
COPY backend/pyproject.toml backend/uv.lock ./

# Configure uv for container environment
ENV UV_SYSTEM_PYTHON=1 \
    UV_CACHE_DIR=/tmp/uv-cache \
    UV_NO_PROGRESS=1 \
    UV_COMPILE_BYTECODE=1

# Install dependencies with cache mount
RUN --mount=type=cache,target=/tmp/uv-cache \
    uv sync --frozen --no-dev --no-editable

# ============================================================================
# PRODUCTION STAGE
# ============================================================================
FROM base AS production

# Create non-root user for security
RUN groupadd -g 1001 appuser && \
    useradd -r -u 1001 -g appuser appuser

# Copy dependencies from previous stage
COPY --from=dependencies /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Set environment variables for production
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/backend/src \
    TRANSFORMERS_CACHE=/app/.cache/transformers \
    TORCH_HOME=/app/.cache/torch \
    UV_SYSTEM_PYTHON=1

# Create cache and storage directories
RUN mkdir -p /app/.cache /app/storage /app/logs && \
    chown -R appuser:appuser /app

# Copy application code
COPY --chown=appuser:appuser backend/src /app/backend/src
COPY --chown=appuser:appuser backend/alembic /app/backend/alembic
COPY --chown=appuser:appuser backend/alembic.ini /app/backend/
COPY --chown=appuser:appuser docker/api/entrypoint.sh /app/

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Switch to non-root user
USER appuser

# Expose API and metrics ports
EXPOSE 8000 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command
CMD ["uvicorn", "backend.src.main:app", "--host", "0.0.0.0", "--port", "8000"]