#!/bin/bash

# ⚔️ NAPOLEON Environment Setup Script ⚔️
# Interactive configuration of .env file

set -e

# Colors
GOLD='\033[1;33m'
BLUE='\033[1;34m' 
GREEN='\033[1;32m'
RED='\033[1;31m'
WHITE='\033[1;37m'
NC='\033[0m'

echo -e "${GOLD}"
echo "════════════════════════════════════════════════════════════════"
echo "                    NAPOLEON ENVIRONMENT SETUP"
echo "                 Configure Your API Keys & Settings"
echo "════════════════════════════════════════════════════════════════"
echo -e "${NC}"

# Check if .env already exists
if [[ -f .env ]]; then
    echo -e "${BLUE}📋 Existing .env file found.${NC}"
    echo ""
    read -p "Do you want to reconfigure it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}✅ Keeping existing configuration${NC}"
        exit 0
    fi
    
    # Backup existing .env
    cp .env .env.backup
    echo -e "${GREEN}📦 Backed up existing .env to .env.backup${NC}"
    echo ""
fi

echo -e "${WHITE}🔑 API Keys Configuration${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# OpenAI API Key
echo ""
echo -e "${GOLD}🤖 OpenAI API Key (REQUIRED)${NC}"
echo -e "${WHITE}Get your key at: ${GREEN}https://platform.openai.com/api-keys${NC}"
echo ""
read -p "Enter your OpenAI API Key: " openai_key

if [[ -z "$openai_key" ]]; then
    echo -e "${RED}❌ OpenAI API Key is required for Napoleon to work!${NC}"
    exit 1
fi

# Anthropic API Key (optional)
echo ""
echo -e "${GOLD}🧠 Anthropic API Key (Optional - for Claude models)${NC}"
echo -e "${WHITE}Get your key at: ${GREEN}https://console.anthropic.com/${NC}"
echo ""
read -p "Enter your Anthropic API Key (press Enter to skip): " anthropic_key

# Model selection
echo ""
echo -e "${WHITE}🎯 Model Configuration${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GOLD}Available models:${NC}"
echo -e "  ${WHITE}1)${NC} gpt-4 (Recommended - Most capable)"
echo -e "  ${WHITE}2)${NC} gpt-4-turbo"
echo -e "  ${WHITE}3)${NC} gpt-3.5-turbo (Faster, cheaper)"
echo -e "  ${WHITE}4)${NC} claude-3-sonnet (If you have Anthropic key)"
echo -e "  ${WHITE}5)${NC} claude-3-haiku (Fast Anthropic model)"
echo ""
read -p "Choose your default model (1-5, default: 1): " model_choice

case $model_choice in
    2) model="gpt-4-turbo" ;;
    3) model="gpt-3.5-turbo" ;;
    4) model="claude-3-sonnet" ;;
    5) model="claude-3-haiku" ;;
    *) model="gpt-4" ;;
esac

# Agent type
echo ""
echo -e "${GOLD}Available agent types:${NC}"
echo -e "  ${WHITE}1)${NC} one_tool_agent (Recommended - Good for beginners)"
echo -e "  ${WHITE}2)${NC} red_teamer (Offensive security)"
echo -e "  ${WHITE}3)${NC} blue_teamer (Defensive security)" 
echo -e "  ${WHITE}4)${NC} bug_bounter (Bug bounty hunting)"
echo -e "  ${WHITE}5)${NC} dfir (Digital forensics)"
echo ""
read -p "Choose your default agent (1-5, default: 1): " agent_choice

case $agent_choice in
    2) agent="red_teamer" ;;
    3) agent="blue_teamer" ;;
    4) agent="bug_bounter" ;;
    5) agent="dfir" ;;
    *) agent="one_tool_agent" ;;
esac

# Advanced settings
echo ""
echo -e "${WHITE}⚙️  Advanced Settings${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
read -p "Enable streaming responses? (Y/n): " stream_choice
if [[ $stream_choice =~ ^[Nn]$ ]]; then
    stream="false"
else
    stream="true"
fi

read -p "Parallel execution limit (default: 3): " parallel_limit
parallel_limit=${parallel_limit:-3}

read -p "Workspace name (default: napoleon_workspace): " workspace
workspace=${workspace:-napoleon_workspace}

# Generate .env file
echo ""
echo -e "${BLUE}📝 Generating .env configuration...${NC}"

cat > .env << EOF
# ⚔️ CYBER NAPOLEON - Configuration File ⚔️
# Generated on $(date)

# =============================================================================
# 🔑 AI MODEL API KEYS (REQUIRED)
# =============================================================================

# OpenAI API Key (REQUIRED for Napoleon to work)
OPENAI_API_KEY=$openai_key

# Anthropic API Key (Optional - for Claude models)
$(if [[ -n "$anthropic_key" ]]; then echo "ANTHROPIC_API_KEY=$anthropic_key"; else echo "# ANTHROPIC_API_KEY=your_anthropic_api_key_here"; fi)

# =============================================================================
# 🏛️ NAPOLEON FRAMEWORK SETTINGS
# =============================================================================

# Default AI model to use
CAI_MODEL=$model

# Default agent type
CAI_AGENT_TYPE=$agent

# Enable streaming responses (true/false)
CAI_STREAM=$stream

# Workspace name
CAI_WORKSPACE=$workspace

# Parallel execution limit
CAI_PARALLEL=$parallel_limit

# =============================================================================
# 🌐 OLLAMA CONFIGURATION (Optional - for local models)
# =============================================================================

# Ollama API endpoint (uncomment if using Ollama)
# OLLAMA_API_BASE=http://host.docker.internal:11434/v1

# =============================================================================
# 🚀 DEPLOYMENT SETTINGS
# =============================================================================

# Container name prefix
COMPOSE_PROJECT_NAME=napoleon

# Environment (development/production)
ENVIRONMENT=production

# Log level (DEBUG/INFO/WARNING/ERROR)
LOG_LEVEL=INFO

# =============================================================================
# 🛡️ SECURITY SETTINGS
# =============================================================================

# Enable security features (true/false)
ENABLE_SECURITY_HARDENING=true

# Container resource limits
MEMORY_LIMIT=4g
CPU_LIMIT=2.0

# =============================================================================
# 📊 MONITORING & TELEMETRY
# =============================================================================

# Enable monitoring (true/false)
ENABLE_MONITORING=true

# Health check interval (seconds)
HEALTH_CHECK_INTERVAL=30

# =============================================================================
# 🧠 MACHINE LEARNING SETTINGS
# =============================================================================

# ML model storage path
ML_MODELS_PATH=/opt/cai/data/ml_models

# Enable ML auto-training (true/false)
ENABLE_ML_TRAINING=true

# ML training interval (hours)
ML_TRAINING_INTERVAL=24

# =============================================================================
# 🔧 ADVANCED SETTINGS (Optional)
# =============================================================================

# Custom Python path
PYTHONPATH=/opt/cai/src

# Enable debug mode (true/false)
DEBUG_MODE=false

# Custom user agent for requests
USER_AGENT="Napoleon/1.0 (Cybersecurity AI Framework)"

# Request timeout (seconds)
REQUEST_TIMEOUT=30
EOF

echo -e "${GREEN}✅ Configuration saved to .env${NC}"
echo ""
echo -e "${GOLD}🎖️  Configuration Summary:${NC}"
echo -e "${WHITE}Model:${NC} $model"
echo -e "${WHITE}Agent:${NC} $agent" 
echo -e "${WHITE}Streaming:${NC} $stream"
echo -e "${WHITE}Parallel Limit:${NC} $parallel_limit"
echo -e "${WHITE}Workspace:${NC} $workspace"
echo ""
echo -e "${BLUE}🚀 You can now start Napoleon with:${NC}"
echo -e "${GREEN}  ./napoleon.sh${NC}"
echo -e "${GREEN}  ./start-napoleon.sh${NC}"
echo ""
echo -e "${GOLD}⚔️ Ready to conquer the digital battlefield! ⚔️${NC}"

#!/bin/bash

# ⚔️ NAPOLEON Environment Setup Script ⚔️
# Interactive configuration of .env file

set -e

# Colors
GOLD='\033[1;33m'
BLUE='\033[1;34m' 
GREEN='\033[1;32m'
RED='\033[1;31m'
WHITE='\033[1;37m'
NC='\033[0m'

echo -e "${GOLD}"
echo "════════════════════════════════════════════════════════════════"
echo "                    NAPOLEON ENVIRONMENT SETUP"
echo "                 Configure Your API Keys & Settings"
echo "════════════════════════════════════════════════════════════════"
echo -e "${NC}"

# Check if .env already exists
if [[ -f .env ]]; then
    echo -e "${BLUE}📋 Existing .env file found.${NC}"
    echo ""
    read -p "Do you want to reconfigure it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}✅ Keeping existing configuration${NC}"
        exit 0
    fi
    
    # Backup existing .env
    cp .env .env.backup
    echo -e "${GREEN}📦 Backed up existing .env to .env.backup${NC}"
    echo ""
fi

echo -e "${WHITE}🔑 API Keys Configuration${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# OpenAI API Key
echo ""
echo -e "${GOLD}🤖 OpenAI API Key (REQUIRED)${NC}"
echo -e "${WHITE}Get your key at: ${GREEN}https://platform.openai.com/api-keys${NC}"
echo ""
read -p "Enter your OpenAI API Key: " openai_key

if [[ -z "$openai_key" ]]; then
    echo -e "${RED}❌ OpenAI API Key is required for Napoleon to work!${NC}"
    exit 1
fi

# Anthropic API Key (optional)
echo ""
echo -e "${GOLD}🧠 Anthropic API Key (Optional - for Claude models)${NC}"
echo -e "${WHITE}Get your key at: ${GREEN}https://console.anthropic.com/${NC}"
echo ""
read -p "Enter your Anthropic API Key (press Enter to skip): " anthropic_key

# Model selection
echo ""
echo -e "${WHITE}🎯 Model Configuration${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GOLD}Available models:${NC}"
echo -e "  ${WHITE}1)${NC} gpt-4 (Recommended - Most capable)"
echo -e "  ${WHITE}2)${NC} gpt-4-turbo"
echo -e "  ${WHITE}3)${NC} gpt-3.5-turbo (Faster, cheaper)"
echo -e "  ${WHITE}4)${NC} claude-3-sonnet (If you have Anthropic key)"
echo -e "  ${WHITE}5)${NC} claude-3-haiku (Fast Anthropic model)"
echo ""
read -p "Choose your default model (1-5, default: 1): " model_choice

case $model_choice in
    2) model="gpt-4-turbo" ;;
    3) model="gpt-3.5-turbo" ;;
    4) model="claude-3-sonnet" ;;
    5) model="claude-3-haiku" ;;
    *) model="gpt-4" ;;
esac

# Agent type
echo ""
echo -e "${GOLD}Available agent types:${NC}"
echo -e "  ${WHITE}1)${NC} one_tool_agent (Recommended - Good for beginners)"
echo -e "  ${WHITE}2)${NC} red_teamer (Offensive security)"
echo -e "  ${WHITE}3)${NC} blue_teamer (Defensive security)" 
echo -e "  ${WHITE}4)${NC} bug_bounter (Bug bounty hunting)"
echo -e "  ${WHITE}5)${NC} dfir (Digital forensics)"
echo ""
read -p "Choose your default agent (1-5, default: 1): " agent_choice

case $agent_choice in
    2) agent="red_teamer" ;;
    3) agent="blue_teamer" ;;
    4) agent="bug_bounter" ;;
    5) agent="dfir" ;;
    *) agent="one_tool_agent" ;;
esac

# Advanced settings
echo ""
echo -e "${WHITE}⚙️  Advanced Settings${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
read -p "Enable streaming responses? (Y/n): " stream_choice
if [[ $stream_choice =~ ^[Nn]$ ]]; then
    stream="false"
else
    stream="true"
fi

read -p "Parallel execution limit (default: 3): " parallel_limit
parallel_limit=${parallel_limit:-3}

read -p "Workspace name (default: napoleon_workspace): " workspace
workspace=${workspace:-napoleon_workspace}

# Generate .env file
echo ""
echo -e "${BLUE}📝 Generating .env configuration...${NC}"

cat > .env << EOF
# ⚔️ CYBER NAPOLEON - Configuration File ⚔️
# Generated on $(date)

# =============================================================================
# 🔑 AI MODEL API KEYS (REQUIRED)
# =============================================================================

# OpenAI API Key (REQUIRED for Napoleon to work)
OPENAI_API_KEY=$openai_key

# Anthropic API Key (Optional - for Claude models)
$(if [[ -n "$anthropic_key" ]]; then echo "ANTHROPIC_API_KEY=$anthropic_key"; else echo "# ANTHROPIC_API_KEY=your_anthropic_api_key_here"; fi)

# =============================================================================
# 🏛️ NAPOLEON FRAMEWORK SETTINGS
# =============================================================================

# Default AI model to use
CAI_MODEL=$model

# Default agent type
CAI_AGENT_TYPE=$agent

# Enable streaming responses (true/false)
CAI_STREAM=$stream

# Workspace name
CAI_WORKSPACE=$workspace

# Parallel execution limit
CAI_PARALLEL=$parallel_limit

# =============================================================================
# 🌐 OLLAMA CONFIGURATION (Optional - for local models)
# =============================================================================

# Ollama API endpoint (uncomment if using Ollama)
# OLLAMA_API_BASE=http://host.docker.internal:11434/v1

# =============================================================================
# 🚀 DEPLOYMENT SETTINGS
# =============================================================================

# Container name prefix
COMPOSE_PROJECT_NAME=napoleon

# Environment (development/production)
ENVIRONMENT=production

# Log level (DEBUG/INFO/WARNING/ERROR)
LOG_LEVEL=INFO

# =============================================================================
# 🛡️ SECURITY SETTINGS
# =============================================================================

# Enable security features (true/false)
ENABLE_SECURITY_HARDENING=true

# Container resource limits
MEMORY_LIMIT=4g
CPU_LIMIT=2.0

# =============================================================================
# 📊 MONITORING & TELEMETRY
# =============================================================================

# Enable monitoring (true/false)
ENABLE_MONITORING=true

# Health check interval (seconds)
HEALTH_CHECK_INTERVAL=30

# =============================================================================
# 🧠 MACHINE LEARNING SETTINGS
# =============================================================================

# ML model storage path
ML_MODELS_PATH=/opt/cai/data/ml_models

# Enable ML auto-training (true/false)
ENABLE_ML_TRAINING=true

# ML training interval (hours)
ML_TRAINING_INTERVAL=24

# =============================================================================
# 🔧 ADVANCED SETTINGS (Optional)
# =============================================================================

# Custom Python path
PYTHONPATH=/opt/cai/src

# Enable debug mode (true/false)
DEBUG_MODE=false

# Custom user agent for requests
USER_AGENT="Napoleon/1.0 (Cybersecurity AI Framework)"

# Request timeout (seconds)
REQUEST_TIMEOUT=30
EOF

echo -e "${GREEN}✅ Configuration saved to .env${NC}"
echo ""
echo -e "${GOLD}🎖️  Configuration Summary:${NC}"
echo -e "${WHITE}Model:${NC} $model"
echo -e "${WHITE}Agent:${NC} $agent" 
echo -e "${WHITE}Streaming:${NC} $stream"
echo -e "${WHITE}Parallel Limit:${NC} $parallel_limit"
echo -e "${WHITE}Workspace:${NC} $workspace"
echo ""
echo -e "${BLUE}🚀 You can now start Napoleon with:${NC}"
echo -e "${GREEN}  ./napoleon.sh${NC}"
echo -e "${GREEN}  ./start-napoleon.sh${NC}"
echo ""
echo -e "${GOLD}⚔️ Ready to conquer the digital battlefield! ⚔️${NC}"

#!/bin/bash

# ⚔️ NAPOLEON Environment Setup Script ⚔️
# Interactive configuration of .env file

set -e

# Colors
GOLD='\033[1;33m'
BLUE='\033[1;34m' 
GREEN='\033[1;32m'
RED='\033[1;31m'
WHITE='\033[1;37m'
NC='\033[0m'

echo -e "${GOLD}"
echo "════════════════════════════════════════════════════════════════"
echo "                    NAPOLEON ENVIRONMENT SETUP"
echo "                 Configure Your API Keys & Settings"
echo "════════════════════════════════════════════════════════════════"
echo -e "${NC}"

# Check if .env already exists
if [[ -f .env ]]; then
    echo -e "${BLUE}📋 Existing .env file found.${NC}"
    echo ""
    read -p "Do you want to reconfigure it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}✅ Keeping existing configuration${NC}"
        exit 0
    fi
    
    # Backup existing .env
    cp .env .env.backup
    echo -e "${GREEN}📦 Backed up existing .env to .env.backup${NC}"
    echo ""
fi

echo -e "${WHITE}🔑 API Keys Configuration${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# OpenAI API Key
echo ""
echo -e "${GOLD}🤖 OpenAI API Key (REQUIRED)${NC}"
echo -e "${WHITE}Get your key at: ${GREEN}https://platform.openai.com/api-keys${NC}"
echo ""
read -p "Enter your OpenAI API Key: " openai_key

if [[ -z "$openai_key" ]]; then
    echo -e "${RED}❌ OpenAI API Key is required for Napoleon to work!${NC}"
    exit 1
fi

# Anthropic API Key (optional)
echo ""
echo -e "${GOLD}🧠 Anthropic API Key (Optional - for Claude models)${NC}"
echo -e "${WHITE}Get your key at: ${GREEN}https://console.anthropic.com/${NC}"
echo ""
read -p "Enter your Anthropic API Key (press Enter to skip): " anthropic_key

# Model selection
echo ""
echo -e "${WHITE}🎯 Model Configuration${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GOLD}Available models:${NC}"
echo -e "  ${WHITE}1)${NC} gpt-4 (Recommended - Most capable)"
echo -e "  ${WHITE}2)${NC} gpt-4-turbo"
echo -e "  ${WHITE}3)${NC} gpt-3.5-turbo (Faster, cheaper)"
echo -e "  ${WHITE}4)${NC} claude-3-sonnet (If you have Anthropic key)"
echo -e "  ${WHITE}5)${NC} claude-3-haiku (Fast Anthropic model)"
echo ""
read -p "Choose your default model (1-5, default: 1): " model_choice

case $model_choice in
    2) model="gpt-4-turbo" ;;
    3) model="gpt-3.5-turbo" ;;
    4) model="claude-3-sonnet" ;;
    5) model="claude-3-haiku" ;;
    *) model="gpt-4" ;;
esac

# Agent type
echo ""
echo -e "${GOLD}Available agent types:${NC}"
echo -e "  ${WHITE}1)${NC} one_tool_agent (Recommended - Good for beginners)"
echo -e "  ${WHITE}2)${NC} red_teamer (Offensive security)"
echo -e "  ${WHITE}3)${NC} blue_teamer (Defensive security)" 
echo -e "  ${WHITE}4)${NC} bug_bounter (Bug bounty hunting)"
echo -e "  ${WHITE}5)${NC} dfir (Digital forensics)"
echo ""
read -p "Choose your default agent (1-5, default: 1): " agent_choice

case $agent_choice in
    2) agent="red_teamer" ;;
    3) agent="blue_teamer" ;;
    4) agent="bug_bounter" ;;
    5) agent="dfir" ;;
    *) agent="one_tool_agent" ;;
esac

# Advanced settings
echo ""
echo -e "${WHITE}⚙️  Advanced Settings${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
read -p "Enable streaming responses? (Y/n): " stream_choice
if [[ $stream_choice =~ ^[Nn]$ ]]; then
    stream="false"
else
    stream="true"
fi

read -p "Parallel execution limit (default: 3): " parallel_limit
parallel_limit=${parallel_limit:-3}

read -p "Workspace name (default: napoleon_workspace): " workspace
workspace=${workspace:-napoleon_workspace}

# Generate .env file
echo ""
echo -e "${BLUE}📝 Generating .env configuration...${NC}"

cat > .env << EOF
# ⚔️ CYBER NAPOLEON - Configuration File ⚔️
# Generated on $(date)

# =============================================================================
# 🔑 AI MODEL API KEYS (REQUIRED)
# =============================================================================

# OpenAI API Key (REQUIRED for Napoleon to work)
OPENAI_API_KEY=$openai_key

# Anthropic API Key (Optional - for Claude models)
$(if [[ -n "$anthropic_key" ]]; then echo "ANTHROPIC_API_KEY=$anthropic_key"; else echo "# ANTHROPIC_API_KEY=your_anthropic_api_key_here"; fi)

# =============================================================================
# 🏛️ NAPOLEON FRAMEWORK SETTINGS
# =============================================================================

# Default AI model to use
CAI_MODEL=$model

# Default agent type
CAI_AGENT_TYPE=$agent

# Enable streaming responses (true/false)
CAI_STREAM=$stream

# Workspace name
CAI_WORKSPACE=$workspace

# Parallel execution limit
CAI_PARALLEL=$parallel_limit

# =============================================================================
# 🌐 OLLAMA CONFIGURATION (Optional - for local models)
# =============================================================================

# Ollama API endpoint (uncomment if using Ollama)
# OLLAMA_API_BASE=http://host.docker.internal:11434/v1

# =============================================================================
# 🚀 DEPLOYMENT SETTINGS
# =============================================================================

# Container name prefix
COMPOSE_PROJECT_NAME=napoleon

# Environment (development/production)
ENVIRONMENT=production

# Log level (DEBUG/INFO/WARNING/ERROR)
LOG_LEVEL=INFO

# =============================================================================
# 🛡️ SECURITY SETTINGS
# =============================================================================

# Enable security features (true/false)
ENABLE_SECURITY_HARDENING=true

# Container resource limits
MEMORY_LIMIT=4g
CPU_LIMIT=2.0

# =============================================================================
# 📊 MONITORING & TELEMETRY
# =============================================================================

# Enable monitoring (true/false)
ENABLE_MONITORING=true

# Health check interval (seconds)
HEALTH_CHECK_INTERVAL=30

# =============================================================================
# 🧠 MACHINE LEARNING SETTINGS
# =============================================================================

# ML model storage path
ML_MODELS_PATH=/opt/cai/data/ml_models

# Enable ML auto-training (true/false)
ENABLE_ML_TRAINING=true

# ML training interval (hours)
ML_TRAINING_INTERVAL=24

# =============================================================================
# 🔧 ADVANCED SETTINGS (Optional)
# =============================================================================

# Custom Python path
PYTHONPATH=/opt/cai/src

# Enable debug mode (true/false)
DEBUG_MODE=false

# Custom user agent for requests
USER_AGENT="Napoleon/1.0 (Cybersecurity AI Framework)"

# Request timeout (seconds)
REQUEST_TIMEOUT=30
EOF

echo -e "${GREEN}✅ Configuration saved to .env${NC}"
echo ""
echo -e "${GOLD}🎖️  Configuration Summary:${NC}"
echo -e "${WHITE}Model:${NC} $model"
echo -e "${WHITE}Agent:${NC} $agent" 
echo -e "${WHITE}Streaming:${NC} $stream"
echo -e "${WHITE}Parallel Limit:${NC} $parallel_limit"
echo -e "${WHITE}Workspace:${NC} $workspace"
echo ""
echo -e "${BLUE}🚀 You can now start Napoleon with:${NC}"
echo -e "${GREEN}  ./napoleon.sh${NC}"
echo -e "${GREEN}  ./start-napoleon.sh${NC}"
echo ""
echo -e "${GOLD}⚔️ Ready to conquer the digital battlefield! ⚔️${NC}"
