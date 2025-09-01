#!/bin/bash

# ⚔️ CYBER NAPOLEON - Imperial Cybersecurity AI Framework ⚔️
# Quick Launch Script - Deploy and Run Napoleon CLI
# 
# Usage: ./napoleon.sh [options]
# Options:
#   start    - Deploy and start Napoleon (default)
#   cli      - Access Napoleon CLI directly
#   logs     - Show Napoleon logs
#   status   - Show container status
#   stop     - Stop Napoleon containers
#   rebuild  - Force rebuild and restart
#   clean    - Clean everything and rebuild from scratch

set -e  # Exit on error

# Colors for imperial output
GOLD='\033[1;33m'
BLUE='\033[1;34m'
GREEN='\033[1;32m'
RED='\033[1;31m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Napoleon Banner
show_banner() {
    echo -e "${GOLD}"
    echo "════════════════════════════════════════════════════════════════════════════════════"
    echo "                                    NAPOLEON"
    echo "                          Advanced Cybersecurity AI Framework"
    echo "════════════════════════════════════════════════════════════════════════════════════"
    echo -e "${NC}"
    echo -e "${BLUE}                            EMPEROR OF CYBERSECURITY AI${NC}"
    echo -e "${WHITE}                              Production-Ready • ML Enhanced${NC}"
    echo -e "${GOLD}              Docker Ready • Kubernetes Support • Enterprise Grade${NC}"
    echo ""
}

# Check prerequisites
check_prerequisites() {
    echo -e "${BLUE}🔍 Checking system requirements...${NC}"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
        echo "Visit: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        echo -e "${RED}❌ Docker daemon is not running. Please start Docker first.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ All prerequisites satisfied${NC}"
    echo ""
}

# Deploy Napoleon
deploy_napoleon() {
    echo -e "${BLUE}🚀 Deploying CYBER NAPOLEON...${NC}"
    
    # Run deployment script
    if [ -f "./deploy.sh" ]; then
        echo -e "${GREEN}📦 Running deployment script...${NC}"
        chmod +x ./deploy.sh
        ./deploy.sh
    else
        echo -e "${RED}❌ deploy.sh not found. Creating basic deployment...${NC}"
        
        # Basic docker-compose up
        echo -e "${GREEN}📦 Starting containers with docker-compose...${NC}"
        docker-compose up -d --build
        
        # Wait for container to be ready
        echo -e "${BLUE}⏳ Waiting for Napoleon to initialize...${NC}"
        sleep 10
        
        # Install dependencies inside container
        echo -e "${GREEN}📦 Installing dependencies...${NC}"
        docker-compose exec -T cai bash -c "
            python -m pip install --user --upgrade pip
            python -m pip install --user griffe wasabi mako colorama
        " || echo -e "${RED}⚠️  Some dependencies may need manual installation${NC}"
    fi
    
    echo -e "${GREEN}✅ Napoleon deployment complete!${NC}"
    echo ""
}

# Show container status
show_status() {
    echo -e "${BLUE}📊 Napoleon Container Status:${NC}"
    docker-compose ps
    echo ""
    
    echo -e "${BLUE}💾 System Resources:${NC}"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" 2>/dev/null || echo "Container stats not available"
    echo ""
}

# Show logs
show_logs() {
    echo -e "${BLUE}📋 Napoleon Logs (last 50 lines):${NC}"
    docker-compose logs --tail=50 cai
}

# Access Napoleon CLI
access_cli() {
    echo -e "${GOLD}⚔️ Accessing Napoleon Imperial CLI...${NC}"
    echo -e "${WHITE}Type 'exit' to return to host shell${NC}"
    echo ""
    
    # Check if container is running
    if ! docker-compose ps | grep -q "cai.*Up"; then
        echo -e "${RED}❌ Napoleon container is not running. Starting deployment...${NC}"
        deploy_napoleon
    fi
    
    # Install missing dependencies if needed
    echo -e "${BLUE}🔧 Ensuring dependencies are installed...${NC}"
    docker-compose exec -T cai bash -c "
        python -m pip install --user griffe wasabi mako colorama 2>/dev/null || true
    "
    
    # Access the CLI
    echo -e "${GOLD}🏛️ Welcome to Napoleon Imperial Command Center${NC}"
    echo -e "${GREEN}Commands:${NC}"
    echo -e "  ${WHITE}python /opt/cai/src/cai/cli.py${NC} - Start Napoleon CLI"
    echo -e "  ${WHITE}python /opt/cai/src/cai/cli.py --help${NC} - Show help"
    echo ""
    
    docker-compose exec cai bash
}

# Stop Napoleon
stop_napoleon() {
    echo -e "${BLUE}🛑 Stopping Napoleon containers...${NC}"
    docker-compose down
    echo -e "${GREEN}✅ Napoleon stopped${NC}"
}

# Rebuild Napoleon
rebuild_napoleon() {
    echo -e "${BLUE}🔄 Rebuilding Napoleon...${NC}"
    docker-compose down
    docker-compose build --no-cache
    deploy_napoleon
}

# Clean everything
clean_napoleon() {
    echo -e "${RED}🧹 Cleaning all Napoleon resources...${NC}"
    read -p "This will remove all containers, images, and volumes. Continue? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down --volumes --remove-orphans
        docker system prune -f
        echo -e "${GREEN}✅ Cleanup complete${NC}"
        
        echo -e "${BLUE}🚀 Rebuilding from scratch...${NC}"
        deploy_napoleon
    else
        echo -e "${BLUE}❌ Cleanup cancelled${NC}"
    fi
}

# Quick start function
quick_start() {
    show_banner
    check_prerequisites
    
    # Check if already running
    if docker-compose ps | grep -q "cai.*Up"; then
        echo -e "${GREEN}✅ Napoleon is already running!${NC}"
        show_status
        echo -e "${GOLD}🎯 Ready to access CLI? Run: ${WHITE}./napoleon.sh cli${NC}"
        return
    fi
    
    deploy_napoleon
    show_status
    
    echo -e "${GOLD}🎖️ Napoleon is ready for battle!${NC}"
    echo ""
    echo -e "${WHITE}Next steps:${NC}"
    echo -e "  ${GREEN}./napoleon.sh cli${NC}    - Access Napoleon CLI"
    echo -e "  ${GREEN}./napoleon.sh status${NC}  - Check system status"
    echo -e "  ${GREEN}./napoleon.sh logs${NC}    - View system logs"
    echo ""
}

# Main script logic
case "${1:-start}" in
    "start")
        quick_start
        ;;
    "cli")
        show_banner
        access_cli
        ;;
    "status")
        show_banner
        show_status
        ;;
    "logs")
        show_banner
        show_logs
        ;;
    "stop")
        show_banner
        stop_napoleon
        ;;
    "rebuild")
        show_banner
        check_prerequisites
        rebuild_napoleon
        ;;
    "clean")
        show_banner
        check_prerequisites
        clean_napoleon
        ;;
    "help"|"-h"|"--help")
        show_banner
        echo -e "${WHITE}Napoleon Launcher - Usage:${NC}"
        echo ""
        echo -e "${GREEN}./napoleon.sh [command]${NC}"
        echo ""
        echo -e "${WHITE}Commands:${NC}"
        echo -e "  ${GREEN}start${NC}     - Deploy and start Napoleon (default)"
        echo -e "  ${GREEN}cli${NC}       - Access Napoleon CLI directly"
        echo -e "  ${GREEN}status${NC}    - Show container status and resources"
        echo -e "  ${GREEN}logs${NC}      - Show Napoleon system logs"
        echo -e "  ${GREEN}stop${NC}      - Stop Napoleon containers"
        echo -e "  ${GREEN}rebuild${NC}   - Force rebuild and restart"
        echo -e "  ${GREEN}clean${NC}     - Clean everything and rebuild from scratch"
        echo -e "  ${GREEN}help${NC}      - Show this help message"
        echo ""
        echo -e "${GOLD}Examples:${NC}"
        echo -e "  ${WHITE}./napoleon.sh${NC}           # Quick start"
        echo -e "  ${WHITE}./napoleon.sh cli${NC}       # Access CLI directly"
        echo -e "  ${WHITE}./napoleon.sh rebuild${NC}   # Force rebuild"
        echo ""
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo -e "${WHITE}Run '${GREEN}./napoleon.sh help${NC}${WHITE}' for usage information${NC}"
        exit 1
        ;;
esac
