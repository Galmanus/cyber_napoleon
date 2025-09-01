# CAI Framework - Production Deployment Guide

[![Version](https://img.shields.io/badge/version-0.5.3--ml-blue.svg)](https://github.com/cai-framework/cai)
[![Docker](https://img.shields.io/badge/docker-ready-green.svg)](https://docker.com)
[![Kubernetes](https://img.shields.io/badge/kubernetes-supported-blue.svg)](https://kubernetes.io)
[![ML Engine](https://img.shields.io/badge/ml--engine-scikit--learn-orange.svg)](https://scikit-learn.org)

## Overview

CAI (Cyber AI) Framework is an enterprise-grade cybersecurity automation platform with integrated machine learning capabilities. This guide covers production deployment, monitoring, and maintenance procedures.

## 🏢 Enterprise Features

- **250+ Python modules** with 79,000+ lines of production-ready code
- **63 specialized security tools** covering all penetration testing phases
- **Real Machine Learning Engine** with 4 high-performance algorithms
- **43 automated feature extraction** capabilities
- **Continuous learning** with statistical confidence metrics
- **Advanced session management** and parallel agent execution
- **Comprehensive logging** and monitoring systems
- **Production-grade containerization** ready

## 🚀 Quick Production Deployment

### Using Docker Compose (Recommended)

```bash
# 1. Clone and prepare environment
git clone <repository-url>
cd cai
cp .env.production .env

# 2. Deploy with our automated script
./deploy.sh

# 3. Access CAI
docker-compose exec cai python -m cai.cli
```

### Using Kubernetes

```bash
# 1. Apply Kubernetes manifests
kubectl apply -f k8s-deployment.yaml

# 2. Check deployment status
kubectl -n security get pods

# 3. Access CAI
kubectl -n security exec -it deployment/cai-framework -- python -m cai.cli
```

## 📋 Prerequisites

### System Requirements

- **CPU**: 2+ cores (4+ recommended)
- **Memory**: 4GB RAM minimum (8GB+ recommended)
- **Storage**: 20GB available space
- **OS**: Linux (Ubuntu 20.04+ preferred)

### Software Dependencies

- Docker 20.03+
- Docker Compose 1.29+
- Kubernetes 1.21+ (optional)
- Python 3.9+ (for development)

## 🔧 Deployment Options

### 1. Docker Compose Deployment

#### Features
- ✅ Persistent volume management
- ✅ Automatic restart policies
- ✅ Resource limits and reservations
- ✅ Security hardening
- ✅ Health checks
- ✅ Optional web interface

#### Commands

```bash
# Full deployment
./deploy.sh

# Build only
./deploy.sh --build-only

# Deploy without rebuilding
./deploy.sh --deploy-only

# Health check
./deploy.sh --health-check

# View logs
./deploy.sh --logs

# Stop deployment
./deploy.sh --stop

# Interactive shell
./deploy.sh --shell
```

### 2. Kubernetes Deployment

#### Features
- ✅ High availability with 2 replicas
- ✅ Rolling updates
- ✅ Persistent volumes for ML models
- ✅ ConfigMap-based configuration
- ✅ Resource quotas and limits
- ✅ Health and readiness probes

#### Deployment

```bash
# Create namespace and deploy
kubectl apply -f k8s-deployment.yaml

# Scale deployment
kubectl -n security scale deployment/cai-framework --replicas=3

# Update configuration
kubectl -n security edit configmap/cai-config

# Rolling restart
kubectl -n security rollout restart deployment/cai-framework
```

## 📊 Production Monitoring

### Automated Monitoring System

CAI includes a comprehensive monitoring system that tracks:

- **System health** and component status
- **Resource utilization** (CPU, Memory, Disk)
- **ML model performance** and training metrics
- **Security events** and alerts
- **Performance benchmarks**

### Running Monitoring

```bash
# Continuous monitoring (recommended)
python monitor.py --mode continuous

# One-time health check
python monitor.py --mode health

# Collect metrics
python monitor.py --mode metrics --output metrics.json

# Custom configuration
python monitor.py --config /path/to/monitor.json
```

### Monitoring Features

- **Real-time health checks** every 30 seconds
- **Metrics collection** every minute
- **Automated alerting** with cooldown periods
- **Historical data retention** (7 days default)
- **JSON export** for external systems

### Alert Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| CPU Usage | 80% | 90% |
| Memory Usage | 85% | 95% |
| Disk Usage | 90% | 95% |
| ML Accuracy | < 80% | < 70% |

## 🔒 Security Configuration

### Production Security Settings

```yaml
# .env.production
CAI_SECURITY_MODE=strict
CAI_ENABLE_DANGEROUS_TOOLS=false
CAI_MAX_CONCURRENT_AGENTS=5
```

### Container Security

- Non-root user execution (UID 1000)
- Read-only root filesystem where possible
- No privilege escalation
- Capability dropping
- Security contexts enforced

### Network Security

- Internal bridge networking
- No direct host network access
- Configurable port exposure
- Service mesh ready

## 🔄 Machine Learning Operations (MLOps)

### ML Engine Features

- **4 algorithms**: Random Forest, Gradient Boosting, SVM, Neural Network
- **Automated feature extraction**: 43 numerical features
- **Continuous training**: Hourly retraining cycles
- **Model versioning**: Automatic model persistence
- **Confidence scoring**: Statistical confidence metrics
- **Performance monitoring**: Accuracy tracking

### ML Model Management

```bash
# View model status
docker-compose exec cai python -c "
from cai.ml_engine import MLEngine
ml = MLEngine()
print(f'Models: {ml.get_model_count()}')
print(f'Training samples: {ml.get_training_sample_count()}')
"

# Trigger manual training
docker-compose exec cai python -c "
from cai.ml_engine import MLEngine
ml = MLEngine()
ml.train_models()
"

# View model performance
docker-compose exec cai python -c "
from cai.ml_engine import MLEngine
ml = MLEngine()
metrics = ml.get_model_metrics()
print(metrics)
"
```

## 📈 Performance Tuning

### Resource Optimization

```yaml
# docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '2.0'        # Adjust based on workload
      memory: 4G         # Increase for large datasets
    reservations:
      cpus: '0.5'
      memory: 1G
```

### ML Performance Tuning

```python
# Environment variables
CAI_ML_TRAINING_INTERVAL=3600      # Training frequency (seconds)
CAI_ML_MIN_SAMPLES_PER_CLASS=5     # Minimum samples for training
CAI_ML_CONFIDENCE_THRESHOLD=0.8    # Prediction confidence threshold
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Container Won't Start
```bash
# Check logs
docker-compose logs cai

# Common causes:
# - Port conflicts
# - Volume permission issues
# - Insufficient resources
```

#### 2. ML Engine Errors
```bash
# Check ML-specific logs
docker-compose exec cai grep -r "ml_engine" /opt/cai/logs/

# Common causes:
# - Insufficient training data
# - Disk space issues
# - Memory constraints
```

#### 3. High Resource Usage
```bash
# Monitor resource usage
python monitor.py --mode metrics

# Actions:
# - Reduce concurrent agents
# - Adjust training frequency
# - Increase resource limits
```

### Log Analysis

```bash
# Application logs
docker-compose logs -f cai

# System logs
tail -f /var/log/syslog

# CAI-specific logs
docker-compose exec cai tail -f /opt/cai/logs/cai.log

# ML engine logs
docker-compose exec cai tail -f /opt/cai/logs/ml_engine.log
```

## 🔄 Updates and Maintenance

### Rolling Updates

```bash
# Docker Compose
git pull
docker-compose pull
docker-compose up -d

# Kubernetes
kubectl -n security set image deployment/cai-framework cai=cai-framework:latest
kubectl -n security rollout status deployment/cai-framework
```

### Backup Procedures

```bash
# Backup ML models and data
docker-compose exec cai tar -czf /tmp/cai-backup.tar.gz \
    /opt/cai/data/ml_models \
    /opt/cai/data/knowledge_base

docker cp $(docker-compose ps -q cai):/tmp/cai-backup.tar.gz ./

# Backup configuration
cp docker-compose.yml docker-compose.yml.backup
cp .env .env.backup
```

### Restore Procedures

```bash
# Restore from backup
docker cp ./cai-backup.tar.gz $(docker-compose ps -q cai):/tmp/
docker-compose exec cai tar -xzf /tmp/cai-backup.tar.gz -C /
```

## 📊 Metrics and Dashboards

### Available Metrics

- **System Metrics**: CPU, Memory, Disk, Network
- **Application Metrics**: Request rates, Response times, Error rates
- **ML Metrics**: Training accuracy, Prediction confidence, Model performance
- **Security Metrics**: Tool execution counts, Success rates, Alert counts

### Integration with External Systems

```bash
# Export metrics to external monitoring
python monitor.py --mode metrics --output /shared/metrics/cai-metrics.json

# Integration examples:
# - Prometheus/Grafana
# - ELK Stack
# - Datadog
# - New Relic
```

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   Monitoring    │    │   Log Aggregator│
│   (Optional)    │    │   System        │    │   (Optional)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                        CAI Framework                             │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   Agent System  │   ML Engine     │   Security Tools (63)       │
│   - Parallel    │   - 4 Algorithms│   - Reconnaissance          │
│   - Session Mgmt│   - 43 Features │   - Exploitation           │
│   - Reasoning   │   - Continuous  │   - Post-Exploitation       │
│                 │     Learning    │   - Evasion                 │
└─────────────────┴─────────────────┴─────────────────────────────┘
                                │
                                ▼
                   ┌─────────────────────────┐
                   │   Persistent Storage    │
                   │   - ML Models           │
                   │   - Knowledge Base      │
                   │   - Session Data        │
                   │   - Logs               │
                   └─────────────────────────┘
```

## 🤝 Support and Maintenance

### Production Support Checklist

- [ ] Monitor system health daily
- [ ] Review security logs weekly
- [ ] Update dependencies monthly
- [ ] Backup ML models weekly
- [ ] Performance review monthly
- [ ] Security audit quarterly

### Contact and Resources

- **Documentation**: `/opt/cai/docs/`
- **Logs**: `/opt/cai/logs/`
- **Configuration**: `/opt/cai/config/`
- **Models**: `/opt/cai/data/ml_models/`

---

## 📝 Version History

### v0.5.3-ml (Current)
- ✅ Real ML engine with scikit-learn
- ✅ Production containerization
- ✅ Kubernetes deployment
- ✅ Comprehensive monitoring
- ✅ Enhanced security features

### Previous Versions
- v0.5.2: Enhanced CLI and tool integration
- v0.5.1: Advanced reasoning capabilities
- v0.5.0: Initial production release

---

**CAI Framework** - Enterprise Cybersecurity Automation with AI
*Production-ready since 2024*
