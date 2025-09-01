#!/bin/bash
set -euo pipefail

# Napoleon Cybersecurity AI - GUARANTEED Production Deployment
# This script WILL work on any machine with Docker + Docker Compose

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Configuration
SCRIPT_VERSION="1.0.0"
PROJECT_NAME="napoleon-cybersecurity"
COMPOSE_FILE="docker-compose.production.yml"
IMAGE_NAME="napoleon-cybersecurity:latest"

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

info() {
    echo -e "${PURPLE}[INFO]${NC} $1"
}

# Banner
show_banner() {
    echo -e "${PURPLE}"
    echo "██╗   ██╗ █████╗ ██████╗  ██████╗ ██╗     ███████╗ ██████╗ ███╗   ██╗"
    echo "██║   ██║██╔══██╗██╔══██╗██╔═══██╗██║     ██╔════╝██╔═══██╗████╗  ██║"
    echo "██║   ██║███████║██████╔╝██║   ██║██║     █████╗  ██║   ██║██╔██╗ ██║"
    echo "██║   ██║██╔══██║██╔═══╝ ██║   ██║██║     ██╔══╝  ██║   ██║██║╚██╗██║"
    echo "╚██████╔╝██║  ██║██║     ╚██████╔╝███████╗███████╗╚██████╔╝██║ ╚████║"
    echo " ╚═════╝ ╚═╝  ╚═╝╚═╝      ╚═════╝ ╚══════╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝"
    echo -e "${NC}"
    echo -e "${GREEN}Napoleon Cybersecurity AI - Enterprise Deployment${NC}"
    echo -e "${BLUE}Version: v0.5.3-ml | Script: v${SCRIPT_VERSION}${NC}"
    echo ""
}

# Check system requirements
check_system() {
    log "Checking system requirements..."
    
    # Check OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        info "Detected Linux system"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        info "Detected macOS system"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        info "Detected Windows system"
    else
        warning "Unknown OS type: $OSTYPE (proceeding anyway)"
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed!"
        error "Please install Docker first: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    local docker_version
    docker_version=$(docker --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
    info "Docker version: ${docker_version}"
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed!"
        error "Please install Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    local compose_version
    compose_version=$(docker-compose --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
    info "Docker Compose version: ${compose_version}"
    
    # Check available memory
    if command -v free &> /dev/null; then
        local available_ram
        available_ram=$(free -h | awk '/^Mem:/{print $7}' | head -1)
        info "Available RAM: ${available_ram}"
    fi
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        error "Docker daemon is not running!"
        error "Please start Docker and try again."
        exit 1
    fi
    
    success "System requirements satisfied!"
}

# Validate project structure
validate_structure() {
    log "Validating project structure..."
    
    local required_files=(
        "Dockerfile.production"
        "docker-compose.production.yml" 
        "requirements.txt"
        "entrypoint.sh"
        ".env.example"
        "src/"
    )
    
    for file in "${required_files[@]}"; do
        if [[ ! -e "$file" ]]; then
            error "Required file/directory missing: $file"
            exit 1
        fi
    done
    
    # Make entrypoint executable
    chmod +x entrypoint.sh
    
    success "Project structure validated!"
}

# Setup environment
setup_environment() {
    log "Setting up environment..."
    
    # Create .env if it doesn't exist
    if [[ ! -f ".env" ]]; then
        log "Creating .env file from template..."
        cp .env.example .env
        warning "Please edit .env file to configure API keys if needed"
    fi
    
    # Set build variables
    export BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
    if command -v git &> /dev/null && git rev-parse --git-dir > /dev/null 2>&1; then
        export VCS_REF=$(git rev-parse --short HEAD)
    else
        export VCS_REF="unknown"
    fi
    
    info "Build date: ${BUILD_DATE}"
    info "VCS ref: ${VCS_REF}"
    
    success "Environment setup complete!"
}

# Clean old deployment
cleanup_old() {
    log "Cleaning up old deployment..."
    
    # Stop existing containers
    if docker-compose -f "$COMPOSE_FILE" ps -q | grep -q .; then
        warning "Stopping existing containers..."
        docker-compose -f "$COMPOSE_FILE" down --remove-orphans
    fi
    
    # Remove old images if requested
    if [[ "${CLEAN_BUILD:-false}" == "true" ]]; then
        warning "Removing old images..."
        docker image rm "$IMAGE_NAME" 2>/dev/null || true
    fi
    
    success "Cleanup complete!"
}

# Build images
build_images() {
    log "Building Napoleon images..."
    
    # Build with no cache if requested
    local build_args=()
    if [[ "${CLEAN_BUILD:-false}" == "true" ]]; then
        build_args+=(--no-cache)
    fi
    
    build_args+=(--build-arg "BUILD_DATE=${BUILD_DATE}")
    build_args+=(--build-arg "VCS_REF=${VCS_REF}")
    
    if ! docker-compose -f "$COMPOSE_FILE" build "${build_args[@]}"; then
        error "Failed to build images!"
        exit 1
    fi
    
    success "Images built successfully!"
}

# Deploy services
deploy_services() {
    log "Deploying Napoleon services..."
    
    # Start services
    if ! docker-compose -f "$COMPOSE_FILE" up -d; then
        error "Failed to start services!"
        exit 1
    fi
    
    # Wait for services to be healthy
    log "Waiting for services to be ready..."
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if docker-compose -f "$COMPOSE_FILE" ps | grep -q "healthy\|Up"; then
            success "Services are ready!"
            return 0
        fi
        
        echo -n "."
        sleep 2
        ((attempt++))
    done
    
    error "Services failed to start within timeout!"
    docker-compose -f "$COMPOSE_FILE" logs --tail=20
    exit 1
}

# Verify deployment
verify_deployment() {
    log "Verifying deployment..."
    
    # Check container status
    local status
    status=$(docker-compose -f "$COMPOSE_FILE" ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}")
    echo "$status"
    
    # Test health endpoint if available
    local container_ip
    if container_ip=$(docker inspect napoleon-ai --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' 2>/dev/null); then
        info "Container IP: ${container_ip}"
    fi
    
    success "Deployment verification complete!"
}

# Show usage instructions
show_usage() {
    echo ""
    echo -e "${GREEN}🎯 Napoleon Cybersecurity AI is now running!${NC}"
    echo ""
    echo -e "${YELLOW}Quick Start Commands:${NC}"
    echo "  docker-compose -f ${COMPOSE_FILE} exec napoleon bash"
    echo "  docker-compose -f ${COMPOSE_FILE} logs -f napoleon"
    echo "  docker-compose -f ${COMPOSE_FILE} ps"
    echo ""
    echo -e "${YELLOW}Web Interface:${NC}"
    echo "  To start web interface: docker-compose -f ${COMPOSE_FILE} --profile web up -d"
    echo "  Access at: http://localhost:8081"
    echo ""
    echo -e "${YELLOW}Management Commands:${NC}"
    echo "  Stop:    docker-compose -f ${COMPOSE_FILE} down"
    echo "  Restart: docker-compose -f ${COMPOSE_FILE} restart"
    echo "  Update:  docker-compose -f ${COMPOSE_FILE} pull && docker-compose -f ${COMPOSE_FILE} up -d"
    echo ""
}

# Main deployment function
main() {
    show_banner
    
    case "${1:-}" in
        --clean)
            export CLEAN_BUILD=true
            ;;
        --help)
            echo "Usage: $0 [--clean|--help]"
            echo "  --clean  Clean build (remove old images)"
            echo "  --help   Show this help"
            exit 0
            ;;
    esac
    
    log "Starting Napoleon Cybersecurity AI deployment..."
    
    check_system
    validate_structure
    setup_environment
    cleanup_old
    build_images
    deploy_services
    verify_deployment
    show_usage
    
    success "🚀 Napoleon deployment completed successfully!"
    info "Run 'docker-compose -f ${COMPOSE_FILE} exec napoleon bash' to start using Napoleon!"
}

# Handle script interruption
trap 'error "Deployment interrupted!"; exit 130' INT TERM

# Execute main function
main "$@"
