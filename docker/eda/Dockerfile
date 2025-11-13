# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS base

# Install system dependencies for data science
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    git \
    libgl1-mesa-glx \
    libglib2.0-0 \
    pandoc \
    texlive-xetex \
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
COPY docker/eda/pyproject.toml docker/eda/uv.lock ./

# Configure uv for container environment
ENV UV_SYSTEM_PYTHON=1 \
    UV_CACHE_DIR=/tmp/uv-cache \
    UV_NO_PROGRESS=1 \
    UV_COMPILE_BYTECODE=1

# Install EDA dependencies
RUN --mount=type=cache,target=/tmp/uv-cache \
    uv sync --frozen --no-editable

# ============================================================================
# EDA STAGE
# ============================================================================
FROM base AS eda

# Create non-root user
RUN groupadd -g 1001 analyst && \
    useradd -r -u 1001 -g analyst analyst

# Copy dependencies from previous stage
COPY --from=dependencies /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    JUPYTER_ENABLE_LAB=yes \
    JUPYTER_CONFIG_DIR=/app/.jupyter \
    UV_SYSTEM_PYTHON=1

# Create directories
RUN mkdir -p /app/notebooks /app/data /app/reports /app/.jupyter /app/logs && \
    chown -R analyst:analyst /app

# Copy notebooks and configuration
COPY --chown=analyst:analyst docker/eda/notebooks /app/notebooks
COPY --chown=analyst:analyst docker/eda/config /app/config
COPY --chown=analyst:analyst docker/eda/entrypoint.sh /app/

# Configure Jupyter
COPY --chown=analyst:analyst docker/eda/jupyter_config.py /app/.jupyter/

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Switch to non-root user
USER analyst

# Expose Jupyter port
EXPOSE 8888

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command - start Jupyter Lab
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]