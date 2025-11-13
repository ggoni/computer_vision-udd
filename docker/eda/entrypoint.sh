#!/bin/bash
set -e

echo "Setting up EDA environment..."

# Wait for services
until curl -f http://postgres:5432 >/dev/null 2>&1; do
  echo "Database is unavailable - sleeping"
  sleep 2
done

until curl -f http://minio:9000/minio/health/live >/dev/null 2>&1; do
  echo "MinIO is unavailable - sleeping"
  sleep 2
done

# Configure Jupyter
jupyter lab --generate-config

echo "EDA environment ready!"
exec "$@"