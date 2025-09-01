#!/bin/bash

# Manual Docker Build Script - Workaround for Docker 28.x Bug
# Use this if deploy.sh fails due to Dockerfile read issues

set -euo pipefail

echo "🔧 Manual Docker Build - Workaround for Docker 28.x"
echo "=================================================="

# Check if we're in the right directory
if [[ ! -f "Dockerfile" ]]; then
    echo "❌ ERROR: Dockerfile not found. Make sure you're in the cyber_napoleon directory."
    exit 1
fi

# Check Docker version
DOCKER_VERSION=$(docker version --format '{{.Client.Version}}' 2>/dev/null || echo "unknown")
echo "📋 Docker Version: $DOCKER_VERSION"

# Create required files if missing
echo "🔍 Checking configuration files..."
if [[ ! -f ".env" && -f ".env.example" ]]; then
    echo "📄 Creating .env from template..."
    cp .env.example .env
fi

if [[ ! -f "agents.yml" && -f "agents.yml.example" ]]; then
    echo "📄 Creating agents.yml from template..."
    cp agents.yml.example agents.yml
fi

# Create directories
echo "📁 Creating directories..."
mkdir -p data/ml_models data/knowledge_base logs config

# Try different build methods
echo ""
echo "🚀 Attempting different build methods..."

BUILD_SUCCESS=false

# Method 1: Standard build
echo "1️⃣  Trying standard build..."
if docker build -t cai-framework:0.5.3-ml . 2>/dev/null; then
    echo "✅ Standard build succeeded!"
    BUILD_SUCCESS=true
else
    echo "❌ Standard build failed"
fi

# Method 2: Explicit Dockerfile
if [[ "$BUILD_SUCCESS" == false ]]; then
    echo "2️⃣  Trying with explicit Dockerfile..."
    if docker build --file ./Dockerfile -t cai-framework:0.5.3-ml . 2>/dev/null; then
        echo "✅ Explicit Dockerfile build succeeded!"
        BUILD_SUCCESS=true
    else
        echo "❌ Explicit Dockerfile build failed"
    fi
fi

# Method 3: Absolute paths
if [[ "$BUILD_SUCCESS" == false ]]; then
    echo "3️⃣  Trying with absolute paths..."
    CURRENT_DIR=$(pwd)
    if docker build --file "$CURRENT_DIR/Dockerfile" -t cai-framework:0.5.3-ml "$CURRENT_DIR" 2>/dev/null; then
        echo "✅ Absolute path build succeeded!"
        BUILD_SUCCESS=true
    else
        echo "❌ Absolute path build failed"
    fi
fi

# Method 4: Production Dockerfile
if [[ "$BUILD_SUCCESS" == false && -f "Dockerfile.production" ]]; then
    echo "4️⃣  Trying production Dockerfile..."
    
    # Create requirements.txt if missing
    if [[ ! -f "requirements.txt" ]]; then
        echo "📄 Creating requirements.txt from pyproject.toml..."
        cat > requirements.txt << 'EOF'
scikit-learn>=1.3.0
pandas>=1.3.0
numpy>=1.21.0
matplotlib>=3.0.0
seaborn>=0.11.0
litellm>=1.63.7
httpx>=0.24.0
rich>=13.9.4
click>=8.0.0
pyyaml>=6.0
requests>=2.0.0
beautifulsoup4>=4.11.0
aiohttp>=3.8.0
fastapi>=0.100.0
uvicorn>=0.18.0
mcp>=1.0.0
lxml>=4.9.0
jinja2>=3.1.0
python-dotenv>=1.0.0
anthropic>=0.25.0
openai>=1.75.0
python-multipart>=0.0.6
pydantic>=2.10.0
typing-extensions>=4.12.2
EOF
    fi
    
    if docker build --file ./Dockerfile.production -t cai-framework:0.5.3-ml . 2>/dev/null; then
        echo "✅ Production Dockerfile build succeeded!"
        BUILD_SUCCESS=true
    else
        echo "❌ Production Dockerfile build failed"
    fi
fi

# Results
echo ""
echo "📊 Build Results:"
echo "=================="
if [[ "$BUILD_SUCCESS" == true ]]; then
    echo "✅ SUCCESS: Docker image built successfully!"
    echo ""
    echo "🎯 Next steps:"
    echo "   docker-compose up -d        # Start the containers"
    echo "   docker-compose exec cai bash  # Access the container"
    echo ""
    echo "🔍 Verify the image:"
    docker images | grep cai-framework
else
    echo "❌ FAILED: All build methods failed!"
    echo ""
    echo "🛠️ Troubleshooting:"
    echo "1. Check Docker version: docker version"
    echo "2. Try downgrading Docker to version 27.x"
    echo "3. Check if Dockerfile exists and is readable"
    echo "4. Try building on a different machine"
    echo ""
    echo "📋 System Information:"
    echo "   Docker Version: $DOCKER_VERSION"
    echo "   Current Directory: $(pwd)"
    echo "   Dockerfile Size: $(stat -c%s Dockerfile 2>/dev/null || echo 'N/A') bytes"
    echo ""
    echo "🐛 This appears to be a Docker 28.x bug. Consider:"
    echo "   - Downgrading Docker to 27.x"
    echo "   - Using Podman instead of Docker"
    echo "   - Building on a different machine"
    
    exit 1
fi
