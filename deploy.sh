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

# Check required configuration files
check_config_files() {
    log "Checking required configuration files..."
    
    local missing_files=()
    
    # Check agents.yml
    if [[ ! -f "agents.yml" ]]; then
        missing_files+=("agents.yml")
        if [[ -f "agents.yml.example" ]]; then
            warning "agents.yml missing, but agents.yml.example found. Copying..."
            cp agents.yml.example agents.yml
            success "Created agents.yml from template."
        fi
    fi
    
    # Check .env
    if [[ ! -f ".env" ]]; then
        if [[ -f ".env.example" ]]; then
            warning ".env missing, creating from .env.example template..."
            cp .env.example .env
            success "Created .env from template. You may need to add your API keys later."
        else
            warning ".env and .env.example not found. Creating minimal .env..."
            cat > .env << 'EOF'
# CAI Framework - Basic Configuration
# Generated automatically by deploy.sh

# Basic settings
OPENAI_API_KEY=""
ANTHROPIC_API_KEY=""
OLLAMA=""
PROMPT_TOOLKIT_NO_CPR=1
CAI_STREAM=false

# Production settings
CAI_ENV=production
CAI_VERSION=0.5.3-ml
CAI_LOG_LEVEL=INFO
CAI_ML_ENGINE_ENABLED=true
CAI_SECURITY_MODE=strict
CAI_ENABLE_DANGEROUS_TOOLS=false
CAI_MAX_CONCURRENT_AGENTS=5
CAI_DATA_DIR=/opt/cai/data
CAI_LOG_DIR=/opt/cai/logs
CAI_BIND_ADDRESS=0.0.0.0
CAI_PORT=8080
CAI_TIMEOUT=300
CAI_HEALTH_CHECK_ENABLED=true
CAI_METRICS_ENABLED=true
CAI_PERFORMANCE_MONITORING=true
CAI_CONTINUOUS_LEARNING=true
CAI_ADVANCED_REASONING=true
CAI_PARALLEL_EXECUTION=true
CAI_SESSION_MANAGEMENT=true
EOF
            success "Created minimal .env file. Add your API keys if needed."
        fi
    fi
    
    # Check critical source directories
    if [[ ! -d "src" ]]; then
        error "src/ directory not found. This is required for CAI framework."
        missing_files+=("src/")
    fi
    
    if [[ ! -f "pyproject.toml" ]]; then
        error "pyproject.toml not found. This is required for Python dependencies."
        missing_files+=("pyproject.toml")
    fi
    
    if [[ ${#missing_files[@]} -gt 0 ]]; then
        error "Missing required files for Docker build:"
        for file in "${missing_files[@]}"; do
            echo "  - $file"
        done
        error "Please ensure all required files exist before building."
        exit 1
    fi
    
    success "All required configuration files are present."
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
    
    # Check for Docker 28.x build bug workaround
    DOCKER_VERSION=$(docker version --format '{{.Client.Version}}' 2>/dev/null || echo "unknown")
    
    if [[ $DOCKER_VERSION =~ ^28\. ]]; then
        warning "Docker 28.x detected - applying build workaround for known bug..."
        
        # Try alternative build methods
        log "Attempting build with explicit context..."
        if docker build --file ./Dockerfile --tag "${IMAGE_NAME}" .; then
            success "Docker image built successfully with workaround."
            return 0
        fi
        
        log "Trying with absolute path..."
        if docker build --file "$(pwd)/Dockerfile" --tag "${IMAGE_NAME}" "$(pwd)"; then
            success "Docker image built successfully with absolute path."
            return 0
        fi
        
        log "Attempting with production Dockerfile..."
        if [[ -f "Dockerfile.production" ]]; then
            if docker build --file ./Dockerfile.production --tag "${IMAGE_NAME}" .; then
                success "Docker image built successfully with production Dockerfile."
                return 0
            fi
        fi
        
        error "Docker 28.x build bug detected. Unable to build image."
        error "Please downgrade Docker to version 27.x or try manual build."
        error "Manual build command: docker build -t ${IMAGE_NAME} ."
        exit 1
    else
        # Standard build for other Docker versions
        if docker build -t "${IMAGE_NAME}" .; then
            success "Docker image built successfully."
        else
            error "Failed to build Docker image."
            exit 1
        fi
    fi
}

# Deploy using Docker Compose
deploy() {
    log "Deploying CAI with Docker Compose..."
    
    # Clean up existing deployment
    log "Cleaning up existing deployment..."
    docker-compose down --remove-orphans 2>/dev/null || true
    
    # Remove any existing containers with the same name
    docker rm -f cai-ml-system 2>/dev/null || true
    docker rm -f cai-web-interface 2>/dev/null || true
    
    # Remove conflicting networks if they exist
    docker network rm cyber_napoleon_cai_network 2>/dev/null || true
    docker network prune -f 2>/dev/null || true
    
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
            check_config_files
            create_directories
            build_image
            ;;
        --deploy-only)
            check_dependencies
            check_config_files
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
            check_config_files
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
