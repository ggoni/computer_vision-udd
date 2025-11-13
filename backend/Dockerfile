# Backend Dockerfile - Multi-stage build optimized for CI/CD
FROM python:3.12-slim AS base

# Install system dependencies (minimal)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install uv package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

# Stage 1: Dependencies
FROM base AS dependencies

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Set environment variables to reduce disk usage during build
ENV UV_CACHE_DIR=/tmp/uv-cache
ENV TORCH_HOME=/tmp/torch-cache

# Sync dependencies (production only, no dev group)
RUN uv sync --frozen --no-dev \
    && rm -rf /tmp/uv-cache \
    && rm -rf /tmp/torch-cache \
    && find /app/.venv -type f -name "*.pyc" -delete \
    && find /app/.venv -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true


# Stage 2: Production
FROM base AS production

# Copy installed dependencies from previous stage
COPY --from=dependencies /app/.venv /app/.venv

# Copy application code
COPY src ./src
COPY scripts ./scripts

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    APP_ENV=production

# Expose port (avoid 5000 as requested)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
