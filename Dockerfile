# CAI Framework with Real Machine Learning - Production Docker Image
FROM python:3.12-slim

# Set metadata
LABEL maintainer="CAI Framework Team"
LABEL version="0.5.3-ml"
LABEL description="Cybersecurity AI Framework with Real Machine Learning"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV CAI_HOME=/opt/cai
ENV CAI_DATA=/opt/cai/data
ENV CAI_MODELS=/opt/cai/data/ml_models

# Install system dependencies for cybersecurity tools
RUN apt-get update && apt-get install -y \
    # Network tools
    nmap \
    netcat-openbsd \
    dnsutils \
    curl \
    wget \
    # Build essentials for Python packages
    build-essential \
    gcc \
    g++ \
    # System utilities
    git \
    vim \
    htop \
    procps \
    # Clean up
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create CAI user for security (non-root)
RUN groupadd -r cai && useradd -r -g cai -d $CAI_HOME -s /bin/bash cai

# Create directories
RUN mkdir -p $CAI_HOME $CAI_DATA $CAI_MODELS \
    && chown -R cai:cai $CAI_HOME

# Switch to CAI user
USER cai
WORKDIR $CAI_HOME

# Copy the CAI framework source code first
COPY --chown=cai:cai src/ ./src/
COPY --chown=cai:cai tools/ ./tools/
COPY --chown=cai:cai agents.yml ./
COPY --chown=cai:cai *.md ./
COPY --chown=cai:cai pyproject.toml ./

# Install Python dependencies from pyproject.toml
RUN python -m pip install --user --upgrade pip

# Install core CAI dependencies (matching pyproject.toml)
RUN python -m pip install --user \
    folium \
    matplotlib \
    numpy \
    pandas \
    openai==1.75.0 \
    pydantic \
    griffe \
    typing-extensions \
    requests \
    types-requests \
    openinference-instrumentation-openai \
    wasabi \
    rich \
    prompt_toolkit \
    python-dotenv \
    litellm \
    mako \
    mcp \
    mkdocs \
    mkdocs-material \
    paramiko \
    dnspython \
    flask \
    networkx \
    PyPDF2

# Install additional cybersecurity and ML packages
RUN python -m pip install --user \
    scikit-learn \
    seaborn \
    httpx \
    click \
    pyyaml \
    beautifulsoup4 \
    aiohttp \
    fastapi \
    uvicorn \
    lxml \
    jinja2 \
    anthropic \
    python-multipart

# Copy ML models if they exist
COPY --chown=cai:cai data/ml_models/ ./data/ml_models/

# Note: .env file is created by deploy.sh before build if needed

# Set Python path
ENV PYTHONPATH="/opt/cai/src"
ENV PATH="/home/cai/.local/bin:${PATH}"

# Expose ports (if needed for future web interface)
EXPOSE 8080

# Set volumes for persistent data
VOLUME ["/opt/cai/data", "/opt/cai/logs"]

# Default command - Interactive CAI
CMD ["bash", "-c", "echo '🤖 CAI Framework v0.5.3-ml Ready!' && python -c 'import sys; print(f\"Python: {sys.version}\"); print(f\"Working Dir: /opt/cai\")' && exec bash"]
