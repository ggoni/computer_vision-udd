# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS base

# Install system dependencies for ML training
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    git \
    libgl1-mesa-glx \
    libglib2.0-0 \
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

# Copy project configuration with training dependencies
COPY docker/training/pyproject.toml docker/training/uv.lock ./

# Configure uv for container environment
ENV UV_SYSTEM_PYTHON=1 \
    UV_CACHE_DIR=/tmp/uv-cache \
    UV_NO_PROGRESS=1 \
    UV_COMPILE_BYTECODE=1

# Install training dependencies
RUN --mount=type=cache,target=/tmp/uv-cache \
    uv sync --frozen --no-editable

# ============================================================================
# TRAINING STAGE
# ============================================================================
FROM base AS training

# Create non-root user
RUN groupadd -g 1001 trainer && \
    useradd -r -u 1001 -g trainer trainer

# Copy dependencies from previous stage
COPY --from=dependencies /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    TRANSFORMERS_CACHE=/app/.cache/transformers \
    TORCH_HOME=/app/.cache/torch \
    MLFLOW_TRACKING_URI=http://mlflow:5000 \
    UV_SYSTEM_PYTHON=1

# Create directories
RUN mkdir -p /app/.cache /app/experiments /app/data /app/models /app/logs && \
    chown -R trainer:trainer /app

# Copy training scripts and configuration
COPY --chown=trainer:trainer docker/training/src /app/src
COPY --chown=trainer:trainer docker/training/scripts /app/scripts
COPY --chown=trainer:trainer docker/training/entrypoint.sh /app/

# Make scripts executable
RUN chmod +x /app/entrypoint.sh /app/scripts/*.py

# Switch to non-root user
USER trainer

# Expose MLflow port (if running tracking server)
EXPOSE 5000

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command - training job
CMD ["python", "/app/scripts/train_model.py"]