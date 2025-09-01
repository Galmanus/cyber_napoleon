#!/bin/bash
set -euo pipefail

# Napoleon Cybersecurity AI - Smart Entrypoint
# Auto-configures the environment for any machine

echo "🚀 Starting Napoleon Cybersecurity AI v0.5.3-ml..."

# Function to log with timestamp
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

log "Initializing Napoleon environment..."

# Create required directories if they don't exist
mkdir -p "${CAI_DATA:-/app/data}" "${CAI_LOGS:-/app/logs}" "${CAI_CONFIG:-/app/config}"
mkdir -p "${CAI_DATA}/ml_models" "${CAI_DATA}/knowledge_base" "${CAI_DATA}/cache"

# Generate default configuration if not exists
if [[ ! -f "${CAI_CONFIG}/config.yml" ]]; then
    log "Creating default configuration..."
    cat > "${CAI_CONFIG}/config.yml" << EOF
# Napoleon AI Configuration
version: "0.5.3-ml"
environment: "${CAI_ENV:-production}"

# Model settings
model:
  provider: "${CAI_MODEL_PROVIDER:-litellm}"
  name: "${CAI_MODEL:-gemini/gemini-2.5-flash}"
  temperature: ${CAI_MODEL_TEMPERATURE:-0.7}
  max_tokens: ${CAI_MODEL_MAX_TOKENS:-8192}

# Machine Learning
ml_engine:
  enabled: ${CAI_ML_ENGINE_ENABLED:-true}
  model_dir: "${CAI_ML_MODEL_DIR:-/app/data/ml_models}"
  training_interval: ${CAI_ML_TRAINING_INTERVAL:-3600}
  min_samples: ${CAI_ML_MIN_SAMPLES_PER_CLASS:-5}
  confidence_threshold: ${CAI_ML_CONFIDENCE_THRESHOLD:-0.8}

# Security
security:
  mode: "${CAI_SECURITY_MODE:-strict}"
  enable_dangerous_tools: ${CAI_ENABLE_DANGEROUS_TOOLS:-false}
  max_concurrent_agents: ${CAI_MAX_CONCURRENT_AGENTS:-5}

# Network
network:
  bind_address: "${CAI_BIND_ADDRESS:-0.0.0.0}"
  port: ${CAI_PORT:-8080}
  timeout: ${CAI_TIMEOUT:-300}

# Features
features:
  continuous_learning: ${CAI_CONTINUOUS_LEARNING:-true}
  advanced_reasoning: ${CAI_ADVANCED_REASONING:-true}
  parallel_execution: ${CAI_PARALLEL_EXECUTION:-true}
  session_management: ${CAI_SESSION_MANAGEMENT:-true}
EOF
fi

# Generate agents configuration if not exists
if [[ ! -f "${CAI_CONFIG}/agents.yml" ]]; then
    log "Creating default agents configuration..."
    cat > "${CAI_CONFIG}/agents.yml" << EOF
# Napoleon AI Agents Configuration
agents:
  red_team:
    name: "Red Team Agent"
    description: "Offensive security testing and vulnerability assessment"
    enabled: true
    tools: ["nmap", "sqlmap", "metasploit"]
    
  blue_team:
    name: "Blue Team Agent"
    description: "Defensive security monitoring and incident response"
    enabled: true
    tools: ["wireshark", "osquery", "yara"]
    
  bug_bounty:
    name: "Bug Bounty Hunter"
    description: "Automated vulnerability discovery and exploitation"
    enabled: true
    tools: ["burpsuite", "nuclei", "ffuf"]
    
  dfir:
    name: "Digital Forensics Agent"
    description: "Incident response and forensic analysis"
    enabled: true
    tools: ["volatility", "autopsy", "sleuthkit"]
    
  napoleon_evasion:
    name: "Napoleon Evasion Expert"
    description: "Advanced firewall evasion and bypass techniques"
    enabled: true
    tools: ["waf_bypasser", "payload_encoder", "traffic_obfuscator"]
EOF
fi

# Create ML models directory structure
log "Setting up ML environment..."
mkdir -p "${CAI_DATA}/ml_models/trained" "${CAI_DATA}/ml_models/cache"

# Initialize empty knowledge base if needed
if [[ ! -f "${CAI_DATA}/knowledge_base/initialized" ]]; then
    log "Initializing knowledge base..."
    mkdir -p "${CAI_DATA}/knowledge_base/cybersecurity"
    mkdir -p "${CAI_DATA}/knowledge_base/exploits"
    mkdir -p "${CAI_DATA}/knowledge_base/tactics"
    echo "$(date)" > "${CAI_DATA}/knowledge_base/initialized"
fi

# Set proper permissions
chmod -R 755 "${CAI_DATA}" "${CAI_LOGS}" "${CAI_CONFIG}" 2>/dev/null || true

# Validate Python environment
log "Validating Python environment..."
if ! python -c "import sys; print(f'Python {sys.version}')"; then
    echo "❌ Python validation failed!"
    exit 1
fi

# Test core imports
log "Testing core dependencies..."
python -c "
try:
    import sklearn, pandas, numpy
    import litellm, httpx
    import rich, click
    import yaml, requests
    print('✅ All core dependencies available')
except ImportError as e:
    print(f'❌ Missing dependency: {e}')
    exit(1)
"

# Check if CAI module is importable
log "Validating CAI framework..."
if python -c "import sys; sys.path.append('/app/src'); import cai" 2>/dev/null; then
    log "✅ CAI framework validated successfully"
else
    log "⚠️  CAI framework not fully available, running in minimal mode"
fi

# Environment summary
log "Environment ready:"
log "  - Python: $(python --version)"
log "  - Working Directory: $(pwd)"
log "  - Data Directory: ${CAI_DATA:-/app/data}"
log "  - Logs Directory: ${CAI_LOGS:-/app/logs}"
log "  - Config Directory: ${CAI_CONFIG:-/app/config}"

log "🎯 Napoleon Cybersecurity AI initialization complete!"

# Execute the main command
exec "$@"
