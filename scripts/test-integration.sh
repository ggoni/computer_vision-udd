#!/bin/bash
# Integration test script for MLOps platform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

# Test configuration
API_BASE_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:3000"
PROMETHEUS_URL="http://localhost:9090"
GRAFANA_URL="http://localhost:3001"

# Test API health endpoint
test_api_health() {
    log_info "Testing API health endpoint..."
    
    if curl -f -s "$API_BASE_URL/health" | grep -q "healthy"; then
        log_success "API health endpoint works"
        return 0
    else
        log_error "API health endpoint failed"
        return 1
    fi
}

# Test API documentation
test_api_docs() {
    log_info "Testing API documentation..."
    
    if curl -f -s "$API_BASE_URL/docs" >/dev/null; then
        log_success "API documentation accessible"
        return 0
    else
        log_error "API documentation not accessible"
        return 1
    fi
}

# Test image upload functionality
test_image_upload() {
    log_info "Testing image upload..."
    
    # Create a test image file
    convert -size 100x100 xc:red /tmp/test_image.jpg 2>/dev/null || {
        echo "R0lGODlhAQABAPAAAN3d3QAAACwAAAAAAQABAAACAkQBADs=" | base64 -d > /tmp/test_image.jpg
    }
    
    # Upload image
    response=$(curl -s -X POST \
        -F "file=@/tmp/test_image.jpg" \
        "$API_BASE_URL/api/v1/images/upload")
    
    if echo "$response" | grep -q "image_id"; then
        log_success "Image upload works"
        
        # Extract image ID for further tests
        image_id=$(echo "$response" | grep -o '"image_id":"[^"]*"' | cut -d'"' -f4)
        echo "$image_id" > /tmp/test_image_id.txt
        
        return 0
    else
        log_error "Image upload failed"
        return 1
    fi
}

# Test object detection
test_object_detection() {
    log_info "Testing object detection..."
    
    if [ ! -f /tmp/test_image_id.txt ]; then
        log_error "No image ID available for detection test"
        return 1
    fi
    
    image_id=$(cat /tmp/test_image_id.txt)
    
    response=$(curl -s -X POST "$API_BASE_URL/api/v1/images/$image_id/analyze")
    
    if echo "$response" | grep -q "detections\|bbox\|confidence"; then
        log_success "Object detection works"
        return 0
    else
        log_error "Object detection failed"
        return 1
    fi
}

# Test frontend accessibility
test_frontend() {
    log_info "Testing frontend accessibility..."
    
    if curl -f -s "$FRONTEND_URL" >/dev/null; then
        log_success "Frontend is accessible"
        return 0
    else
        log_error "Frontend is not accessible"
        return 1
    fi
}

# Test Prometheus metrics
test_prometheus() {
    log_info "Testing Prometheus metrics..."
    
    if curl -f -s "$PROMETHEUS_URL/metrics" >/dev/null; then
        log_success "Prometheus metrics accessible"
        return 0
    else
        log_error "Prometheus metrics not accessible"
        return 1
    fi
}

# Test Grafana dashboard
test_grafana() {
    log_info "Testing Grafana accessibility..."
    
    if curl -f -s "$GRAFANA_URL/api/health" >/dev/null; then
        log_success "Grafana is accessible"
        return 0
    else
        log_error "Grafana is not accessible"
        return 1
    fi
}

# Test database connectivity
test_database() {
    log_info "Testing database connectivity..."
    
    if docker exec cv_postgres pg_isready -U cvuser -d computer_vision_db >/dev/null 2>&1; then
        log_success "Database is accessible"
        return 0
    else
        log_error "Database is not accessible"
        return 1
    fi
}

# Test Redis connectivity
test_redis() {
    log_info "Testing Redis connectivity..."
    
    if docker exec cv_redis redis-cli ping | grep -q "PONG"; then
        log_success "Redis is accessible"
        return 0
    else
        log_error "Redis is not accessible"
        return 1
    fi
}

# Test MinIO accessibility
test_minio() {
    log_info "Testing MinIO accessibility..."
    
    if curl -f -s "http://localhost:9000/minio/health/live" >/dev/null; then
        log_success "MinIO is accessible"
        return 0
    else
        log_error "MinIO is not accessible"
        return 1
    fi
}

# Test custom metrics endpoint
test_custom_metrics() {
    log_info "Testing custom metrics endpoint..."
    
    if curl -f -s "http://localhost:8001/metrics" | grep -q "http_requests_total\|model_inference"; then
        log_success "Custom metrics are working"
        return 0
    else
        log_error "Custom metrics not working"
        return 1
    fi
}

# Performance test
test_performance() {
    log_info "Running basic performance test..."
    
    # Test API response time
    start_time=$(date +%s.%N)
    curl -f -s "$API_BASE_URL/health" >/dev/null
    end_time=$(date +%s.%N)
    
    response_time=$(echo "$end_time - $start_time" | bc)
    response_time_ms=$(echo "$response_time * 1000" | bc)
    
    if (( $(echo "$response_time < 1.0" | bc -l) )); then
        log_success "API response time: ${response_time_ms}ms (good)"
        return 0
    else
        log_error "API response time: ${response_time_ms}ms (slow)"
        return 1
    fi
}

# Cleanup test artifacts
cleanup_tests() {
    log_info "Cleaning up test artifacts..."
    rm -f /tmp/test_image.jpg /tmp/test_image_id.txt
}

# Main test execution
main() {
    log_info "Starting MLOps platform integration tests..."
    
    local tests_passed=0
    local total_tests=11
    
    # Core functionality tests
    test_api_health && ((tests_passed++))
    test_api_docs && ((tests_passed++))
    test_image_upload && ((tests_passed++))
    test_object_detection && ((tests_passed++))
    
    # UI and monitoring tests
    test_frontend && ((tests_passed++))
    test_prometheus && ((tests_passed++))
    test_grafana && ((tests_passed++))
    
    # Infrastructure tests
    test_database && ((tests_passed++))
    test_redis && ((tests_passed++))
    test_minio && ((tests_passed++))
    
    # Performance and metrics tests
    test_custom_metrics && ((tests_passed++))
    
    # Cleanup
    cleanup_tests
    
    # Results
    log_info "Test Results: $tests_passed/$total_tests passed"
    
    if [ $tests_passed -eq $total_tests ]; then
        log_success "All tests passed! MLOps platform is working correctly."
        exit 0
    else
        log_error "Some tests failed. Please check the logs above."
        exit 1
    fi
}

# Allow running specific tests
case "${1:-all}" in
    "api")
        test_api_health && test_api_docs && test_image_upload && test_object_detection
        ;;
    "frontend")
        test_frontend
        ;;
    "monitoring")
        test_prometheus && test_grafana && test_custom_metrics
        ;;
    "infrastructure")
        test_database && test_redis && test_minio
        ;;
    "performance")
        test_performance
        ;;
    "all"|"")
        main
        ;;
    *)
        echo "Usage: $0 [api|frontend|monitoring|infrastructure|performance|all]"
        exit 1
        ;;
esac