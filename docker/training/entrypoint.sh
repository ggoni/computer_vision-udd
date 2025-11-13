#!/bin/bash
set -e

echo "Setting up training environment..."

# Wait for database and MinIO to be ready
echo "Waiting for services to be ready..."
until curl -f http://minio:9000/minio/health/live >/dev/null 2>&1; do
  echo "MinIO is unavailable - sleeping"
  sleep 2
done
echo "MinIO is ready!"

# Initialize MLflow tracking
echo "Initializing MLflow tracking..."
export MLFLOW_S3_ENDPOINT_URL=http://minio:9000
export AWS_ACCESS_KEY_ID=minioadmin
export AWS_SECRET_ACCESS_KEY=minio123456

# Create necessary directories
mkdir -p /app/experiments/runs
mkdir -p /app/data/processed
mkdir -p /app/models/checkpoints

echo "Training environment ready!"
exec "$@"