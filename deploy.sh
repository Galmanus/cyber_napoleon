#!/bin/bash

# CAI Framework - Production Deployment Script
# Version: 0.5.3-ml
# Author: CAI Development Team

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CAI_VERSION="0.5.3-ml"
CONTAINER_NAME="cai-ml-system"
IMAGE_NAME="cai-framework:${CAI_VERSION}"

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check dependencies
check_dependencies() {
    log "Checking dependencies..."
    
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    success "All dependencies are installed."
}

# Create required directories
create_directories() {
    log "Creating required directories..."
    
    mkdir -p data/ml_models
    mkdir -p data/knowledge_base
    mkdir -p logs
    mkdir -p config
    
    # Set appropriate permissions
    chmod 755 data/ml_models data/knowledge_base logs config
    
    success "Directories created successfully."
}

# Build Docker image
build_image() {
    log "Building CAI Docker image..."
    
    if docker build -t "${IMAGE_NAME}" .; then
        success "Docker image built successfully."
    else
        error "Failed to build Docker image."
        exit 1
    fi
}

# Deploy using Docker Compose
deploy() {
    log "Deploying CAI with Docker Compose..."
    
    # Stop existing containers if running
    if docker-compose ps | grep -q "${CONTAINER_NAME}"; then
        warning "Stopping existing CAI container..."
        docker-compose down
    fi
    
    # Start new deployment
    if docker-compose up -d; then
        success "CAI deployed successfully!"
        
        # Wait for container to be ready
        log "Waiting for container to be ready..."
        sleep 5
        
        # Check container status
        if docker-compose ps | grep -q "Up"; then
            success "CAI container is running successfully."
            
            # Show container info
            echo ""
            log "Container Information:"
            docker-compose ps
            
            echo ""
            log "To interact with CAI, run:"
            echo "  docker-compose exec cai python -m cai.cli"
            
            echo ""
            log "To view logs, run:"
            echo "  docker-compose logs -f cai"
            
        else
            error "Container failed to start. Check logs with: docker-compose logs cai"
            exit 1
        fi
    else
        error "Failed to deploy CAI."
        exit 1
    fi
}

# Health check
health_check() {
    log "Performing health check..."
    
    if docker-compose exec -T cai python -c "import cai; print('CAI import successful')" &>/dev/null; then
        success "CAI health check passed."
    else
        error "CAI health check failed."
        return 1
    fi
}

# Show usage
usage() {
    echo "CAI Framework Deployment Script v${CAI_VERSION}"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --build-only     Only build the Docker image"
    echo "  --deploy-only    Only deploy (skip build)"
    echo "  --health-check   Run health check only"
    echo "  --stop          Stop the deployment"
    echo "  --logs          Show container logs"
    echo "  --shell         Open shell in container"
    echo "  --help          Show this help message"
    echo ""
}

# Stop deployment
stop_deployment() {
    log "Stopping CAI deployment..."
    
    if docker-compose down; then
        success "CAI deployment stopped."
    else
        error "Failed to stop deployment."
        exit 1
    fi
}

# Show logs
show_logs() {
    log "Showing CAI container logs..."
    docker-compose logs -f cai
}

# Open shell
open_shell() {
    log "Opening shell in CAI container..."
    docker-compose exec cai /bin/bash
}

# Main execution
main() {
    case "${1:-}" in
        --build-only)
            check_dependencies
            create_directories
            build_image
            ;;
        --deploy-only)
            check_dependencies
            create_directories
            deploy
            health_check
            ;;
        --health-check)
            health_check
            ;;
        --stop)
            stop_deployment
            ;;
        --logs)
            show_logs
            ;;
        --shell)
            open_shell
            ;;
        --help)
            usage
            exit 0
            ;;
        "")
            log "Starting full CAI deployment process..."
            check_dependencies
            create_directories
            build_image
            deploy
            health_check
            success "CAI deployment completed successfully!"
            ;;
        *)
            error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
}

# Execute main function with all arguments
main "$@"
