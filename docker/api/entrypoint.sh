#!/bin/bash
set -e

echo "Starting API server setup..."

# Ensure storage directories exist and have correct permissions
echo "Setting up storage directories..."
mkdir -p /app/backend/storage/uploads
chown -R appuser:appuser /app/backend/storage /app/.cache /app/logs
chmod -R 755 /app/backend/storage

# Give some time for dependencies to be ready
echo "Waiting for dependencies to be ready..."
sleep 10

# Run database migrations
echo "Running database migrations..."
cd /app && gosu appuser alembic -c backend/alembic.ini upgrade head

# Start the application as appuser
echo "Starting API server as appuser..."
exec gosu appuser "$@"