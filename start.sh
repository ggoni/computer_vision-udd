#!/bin/bash
# Simple startup script for Computer Vision Detection API

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 Starting Computer Vision Detection API...${NC}"

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Docker Compose is not installed. Please install it and try again.${NC}"
    exit 1
fi

# Start the services
echo -e "${BLUE}📦 Starting all services...${NC}"
docker-compose up -d

# Wait for services to be ready
echo -e "${BLUE}⏳ Waiting for services to start (this may take 30-60 seconds)...${NC}"
sleep 30

# Check if API is responding
if curl -f http://localhost:8000/health >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Services are ready!${NC}"
    echo ""
    echo -e "${GREEN}🌐 Access your application:${NC}"
    echo -e "   Frontend:     http://localhost:3000"
    echo -e "   API Docs:     http://localhost:8000/docs"
    echo -e "   Monitoring:   http://localhost:3001 (admin/grafana123)"
    echo -e "   Storage:      http://localhost:9001 (minioadmin/minio123456)"
    echo ""
    echo -e "${BLUE}📊 Check service status:${NC} docker-compose ps"
    echo -e "${BLUE}📝 View logs:${NC} docker-compose logs backend"
    echo -e "${BLUE}🛑 Stop services:${NC} docker-compose down"
else
    echo -e "${YELLOW}⚠️  API not ready yet. Check logs: docker-compose logs backend${NC}"
    echo -e "${BLUE}ℹ️  First startup may take longer due to model download.${NC}"
fi