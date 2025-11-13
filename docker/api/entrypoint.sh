#!/bin/bash
set -e

echo "Starting API server setup..."

# Give some time for dependencies to be ready
echo "Waiting for dependencies to be ready..."
sleep 10

# Skip database migrations for now due to configuration issues
echo "Skipping database migrations..."

# Start the application
echo "Starting API server..."
exec "$@"