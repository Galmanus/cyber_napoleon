# Napoleon Cybersecurity AI - Deployment Guide

## 🚀 One-Command Deployment (GUARANTEED TO WORK)

This deployment is **guaranteed to work** on any machine with Docker and Docker Compose installed.

### Prerequisites (Only 2 things needed!)

1. **Docker** 20.03+ → [Install Docker](https://docs.docker.com/get-docker/)
2. **Docker Compose** 1.29+ → [Install Docker Compose](https://docs.docker.com/compose/install/)

### Deploy Napoleon AI (One Command!)

```bash
git clone https://github.com/Galmanus/cyber_napoleon.git
cd cyber_napoleon
./deploy-production.sh
```

**That's it!** Napoleon will:
- ✅ Check your system automatically
- ✅ Build the container with all dependencies
- ✅ Start the services with health checks
- ✅ Configure everything automatically
- ✅ Show you how to use it

## 🎯 Usage After Deployment

### Start Interactive Session
```bash
docker-compose -f docker-compose.production.yml exec napoleon bash
```

### View Logs
```bash
docker-compose -f docker-compose.production.yml logs -f napoleon
```

### Start Web Interface (Optional)
```bash
docker-compose -f docker-compose.production.yml --profile web up -d
# Access at: http://localhost:8081
```

## 🔧 Management Commands

### Stop Napoleon
```bash
docker-compose -f docker-compose.production.yml down
```

### Restart Napoleon
```bash
docker-compose -f docker-compose.production.yml restart
```

### Clean Rebuild
```bash
./deploy-production.sh --clean
```

## 🛡️ Security Features

- **Non-root containers**: Runs as `napoleon` user
- **Network isolation**: Custom Docker network
- **Resource limits**: CPU and memory constraints
- **Health checks**: Automatic failure detection
- **Named volumes**: Data persists across updates

## 📊 What's Included Out-of-the-Box

### Machine Learning Stack
- scikit-learn, pandas, numpy
- 4 ML algorithms ready to use
- Automatic model training and persistence

### Cybersecurity Tools
- nmap for network scanning
- netcat for network testing
- DNS utilities for analysis
- Custom evasion techniques

### Web Framework
- FastAPI for web interfaces
- Rich CLI for beautiful terminal output
- Full async support

## 🔍 Troubleshooting

### Container Won't Start?
```bash
docker-compose -f docker-compose.production.yml logs napoleon
```

### Need More Memory?
Edit `.env` file:
```bash
MEMORY_LIMIT=8G
CPU_LIMIT=4.0
```

### API Keys Configuration
Napoleon supports multiple AI providers. Edit `.env` file:

**For Gemini (Recommended):**
```bash
# Gemini Configuration (Google AI)
GEMINI_API_KEY="AIzaSy..."
CAI_MODEL="gemini/gemini-2.5-flash"

# Required placeholder for framework compatibility
OPENAI_API_KEY="sk-1234"
```

**For OpenAI:**
```bash
OPENAI_API_KEY="sk-..."
CAI_MODEL="gpt-4"
```

**For OpenRouter:**
```bash
OPENROUTER_API_KEY="sk-or-v1-..."
CAI_MODEL="openrouter/mistralai/mistral-small-3.2-24b-instruct:free"
```

**For Anthropic (Claude):**
```bash
ANTHROPIC_API_KEY="sk-ant-..."
CAI_MODEL="claude-3-sonnet-20240229"
```

## ✅ Testing Your Deployment

### Quick Health Check
```bash
docker-compose -f docker-compose.production.yml ps
# All services should show "Up" or "healthy"
```

### Test Python Environment
```bash
docker-compose -f docker-compose.production.yml exec napoleon python -c "
import sklearn, pandas, numpy
print('✅ ML stack working!')
"
```

### Test Napoleon Framework
```bash
docker-compose -f docker-compose.production.yml exec napoleon python -c "
import sys
sys.path.append('/app/src')
import cai
print('✅ Napoleon framework loaded!')
"
```

## 🔧 Advanced Configuration

### Custom Environment Variables
Create/edit `.env` file:
```bash
# Core settings
CAI_ENV=production
CAI_LOG_LEVEL=INFO

# Model configuration
CAI_MODEL=gemini/gemini-2.5-flash
CAI_MODEL_TEMPERATURE=0.7

# Resource limits
MEMORY_LIMIT=4G
CPU_LIMIT=2.0

# Network ports
NAPOLEON_PORT=8080
NAPOLEON_WEB_PORT=8081
```

### Persistent Data Locations
All data is stored in Docker named volumes:
- `napoleon_data`: ML models and knowledge base
- `napoleon_logs`: Application logs
- `napoleon_config`: Configuration files

### Backup Your Data
```bash
docker run --rm -v napoleon_data:/data -v $(pwd):/backup alpine tar czf /backup/napoleon-backup.tar.gz -C /data .
```

### Restore Your Data
```bash
docker run --rm -v napoleon_data:/data -v $(pwd):/backup alpine tar xzf /backup/napoleon-backup.tar.gz -C /data
```

## 🚨 What Makes This Deployment Special?

### 1. **Zero Configuration Required**
- Works immediately after `./deploy-production.sh`
- All dependencies bundled in container
- Safe defaults for all settings

### 2. **Multi-Platform Support**
- Linux (any distribution)
- macOS (Intel and Apple Silicon)
- Windows (with Docker Desktop)

### 3. **Production-Ready Security**
- Non-root containers
- Resource limits
- Network isolation
- Health monitoring

### 4. **Self-Healing Infrastructure**
- Automatic restarts on failure
- Health checks with recovery
- Graceful error handling

## 📞 Support

If this deployment doesn't work on your machine, it's a bug! Please report:
- Your OS and version
- Docker version
- Error logs from `docker-compose logs`

**This deployment WILL work on any machine with Docker!** 🚀
