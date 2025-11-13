#!/bin/bash
# MLOps Platform Management Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE_PROD="docker-compose.production.yml"
COMPOSE_FILE_MLOPS="docker-compose.mlops.yml"
PROJECT_NAME="computer-vision-udd"

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Check if Docker Compose is available
check_compose() {
    if ! command -v docker-compose >/dev/null 2>&1; then
        log_error "Docker Compose is not installed. Please install it and try again."
        exit 1
    fi
}

# Start production stack
start_production() {
    log_info "Starting production MLOps stack..."
    check_docker
    check_compose
    
    docker-compose -f $COMPOSE_FILE_PROD -p $PROJECT_NAME up -d
    
    log_info "Waiting for services to be healthy..."
    sleep 30
    
    # Check service health
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        log_success "Production stack is running!"
        log_info "Services:"
        log_info "  - API: http://localhost:8000"
        log_info "  - Frontend: http://localhost:3000"
        log_info "  - Grafana: http://localhost:3001 (admin/grafana123)"
        log_info "  - Prometheus: http://localhost:9090"
    else
        log_error "Health check failed. Please check the logs."
        docker-compose -f $COMPOSE_FILE_PROD -p $PROJECT_NAME logs api
    fi
}

# Start full MLOps stack
start_mlops() {
    log_info "Starting full MLOps stack..."
    check_docker
    check_compose
    
    docker-compose -f $COMPOSE_FILE_MLOPS -p $PROJECT_NAME up -d
    
    log_info "Waiting for services to be healthy..."
    sleep 60
    
    log_success "MLOps stack is running!"
    log_info "Services:"
    log_info "  - API: http://localhost:8000"
    log_info "  - Frontend: http://localhost:3000"
    log_info "  - Grafana: http://localhost:3001 (admin/grafana123)"
    log_info "  - Jupyter Lab: http://localhost:8888 (token: eda_token_123)"
    log_info "  - MinIO Console: http://localhost:9001 (minioadmin/minio123456)"
    log_info "  - Prometheus: http://localhost:9090"
}

# Stop services
stop_services() {
    log_info "Stopping MLOps services..."
    
    if [ -f $COMPOSE_FILE_MLOPS ]; then
        docker-compose -f $COMPOSE_FILE_MLOPS -p $PROJECT_NAME down
    fi
    
    if [ -f $COMPOSE_FILE_PROD ]; then
        docker-compose -f $COMPOSE_FILE_PROD -p $PROJECT_NAME down
    fi
    
    log_success "Services stopped."
}

# Show service status
status() {
    log_info "Service status:"
    
    if docker-compose -f $COMPOSE_FILE_PROD -p $PROJECT_NAME ps >/dev/null 2>&1; then
        docker-compose -f $COMPOSE_FILE_PROD -p $PROJECT_NAME ps
    elif docker-compose -f $COMPOSE_FILE_MLOPS -p $PROJECT_NAME ps >/dev/null 2>&1; then
        docker-compose -f $COMPOSE_FILE_MLOPS -p $PROJECT_NAME ps
    else
        log_info "No services are currently running."
    fi
}

# View logs
logs() {
    local service=${1:-""}
    
    if [ -z "$service" ]; then
        log_info "Available services:"
        log_info "  api, frontend, postgres, redis, minio, prometheus, grafana"
        log_info "Usage: $0 logs <service_name>"
        return 1
    fi
    
    log_info "Showing logs for service: $service"
    
    if docker-compose -f $COMPOSE_FILE_PROD -p $PROJECT_NAME ps | grep -q $service; then
        docker-compose -f $COMPOSE_FILE_PROD -p $PROJECT_NAME logs -f $service
    elif docker-compose -f $COMPOSE_FILE_MLOPS -p $PROJECT_NAME ps | grep -q $service; then
        docker-compose -f $COMPOSE_FILE_MLOPS -p $PROJECT_NAME logs -f $service
    else
        log_error "Service '$service' not found or not running."
    fi
}

# Health check
health() {
    log_info "Performing health checks..."
    
    # API health
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        log_success "✓ API service is healthy"
    else
        log_error "✗ API service is unhealthy"
    fi
    
    # Frontend health
    if curl -f http://localhost:3000 >/dev/null 2>&1; then
        log_success "✓ Frontend service is healthy"
    else
        log_error "✗ Frontend service is unhealthy"
    fi
    
    # Database health
    if docker exec cv_postgres pg_isready -U cvuser -d computer_vision_db >/dev/null 2>&1; then
        log_success "✓ Database is healthy"
    else
        log_error "✗ Database is unhealthy"
    fi
    
    # Monitoring health
    if curl -f http://localhost:9090/-/healthy >/dev/null 2>&1; then
        log_success "✓ Prometheus is healthy"
    else
        log_warning "✗ Prometheus is not accessible"
    fi
}

# Cleanup unused resources
cleanup() {
    log_info "Cleaning up unused Docker resources..."
    
    docker system prune -f
    docker volume prune -f
    
    log_success "Cleanup completed."
}

# Update services
update() {
    log_info "Updating MLOps services..."
    
    # Pull latest images
    if [ -f $COMPOSE_FILE_PROD ]; then
        docker-compose -f $COMPOSE_FILE_PROD pull
    fi
    
    if [ -f $COMPOSE_FILE_MLOPS ]; then
        docker-compose -f $COMPOSE_FILE_MLOPS pull
    fi
    
    log_success "Images updated. Restart services to apply changes."
}

# Backup data
backup() {
    local backup_dir="./backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p $backup_dir
    
    log_info "Creating backup in $backup_dir..."
    
    # Backup database
    if docker ps | grep -q cv_postgres; then
        docker exec cv_postgres pg_dump -U cvuser computer_vision_db > $backup_dir/database.sql
        log_success "✓ Database backup created"
    fi
    
    # Backup monitoring data
    if docker volume ls | grep -q prometheus_data; then
        docker run --rm -v prometheus_data:/data -v $(pwd)/$backup_dir:/backup alpine tar czf /backup/prometheus.tar.gz -C /data .
        log_success "✓ Prometheus data backup created"
    fi
    
    log_success "Backup completed in $backup_dir"
}

# Show usage
usage() {
    echo "MLOps Platform Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start-prod    Start production stack"
    echo "  start-mlops   Start full MLOps stack"
    echo "  stop          Stop all services"
    echo "  status        Show service status"
    echo "  logs <svc>    Show logs for service"
    echo "  health        Check service health"
    echo "  cleanup       Clean unused resources"
    echo "  update        Update service images"
    echo "  backup        Backup data"
    echo "  help          Show this help"
    echo ""
}

# Main command handler
case "${1:-}" in
    "start-prod")
        start_production
        ;;
    "start-mlops")
        start_mlops
        ;;
    "stop")
        stop_services
        ;;
    "status")
        status
        ;;
    "logs")
        logs "$2"
        ;;
    "health")
        health
        ;;
    "cleanup")
        cleanup
        ;;
    "update")
        update
        ;;
    "backup")
        backup
        ;;
    "help"|"")
        usage
        ;;
    *)
        log_error "Unknown command: $1"
        usage
        exit 1
        ;;
esac