#!/usr/bin/env python3
"""
CAI Framework - Production Monitoring Script
Version: 0.5.3-ml
Author: CAI Development Team

This script provides comprehensive monitoring capabilities for CAI in production:
- Health checks for all components
- Performance metrics collection
- ML model monitoring
- Resource usage tracking
- Alert generation
"""

import asyncio
import json
import logging
import os
import psutil
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./logs/monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class CAIMonitor:
    """Production monitoring system for CAI Framework."""
    
    def __init__(self, config_path: str = "/opt/cai/config/monitor.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.metrics_history = []
        self.alert_cooldowns = {}
        
    def _load_config(self) -> Dict[str, Any]:
        """Load monitoring configuration."""
        default_config = {
            "health_check_interval": 30,
            "metrics_collection_interval": 60,
            "ml_monitoring_interval": 300,
            "alerts": {
                "cpu_threshold": 80,
                "memory_threshold": 85,
                "disk_threshold": 90,
                "ml_accuracy_threshold": 0.8,
                "cooldown_minutes": 15
            },
            "retention_days": 7
        }
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    default_config.update(config)
            except Exception as e:
                logger.error(f"Error loading config: {e}, using defaults")
        
        return default_config
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": "healthy",
            "components": {}
        }
        
        try:
            # Check CAI import
            results["components"]["cai_import"] = await self._check_cai_import()
            
            # Check ML engine
            results["components"]["ml_engine"] = await self._check_ml_engine()
            
            # Check file system
            results["components"]["filesystem"] = await self._check_filesystem()
            
            # Check resources
            results["components"]["resources"] = await self._check_resources()
            
            # Determine overall status
            failed_components = [
                comp for comp, status in results["components"].items() 
                if status.get("status") != "healthy"
            ]
            
            if failed_components:
                results["overall_status"] = "degraded"
                if len(failed_components) > len(results["components"]) // 2:
                    results["overall_status"] = "unhealthy"
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            results["overall_status"] = "error"
            results["error"] = str(e)
        
        return results
    
    async def _check_cai_import(self) -> Dict[str, Any]:
        """Check if CAI can be imported successfully."""
        try:
            import cai
            return {
                "status": "healthy",
                "version": getattr(cai, "__version__", "unknown"),
                "message": "CAI import successful"
            }
        except ImportError as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "message": "CAI import failed"
            }
    
    async def _check_ml_engine(self) -> Dict[str, Any]:
        """Check ML engine status."""
        try:
            from cai.ml_engine import MLEngine
            
            ml_engine = MLEngine()
            model_files = list(Path(ml_engine.model_dir).glob("*.pkl"))
            
            return {
                "status": "healthy",
                "models_count": len(model_files),
                "model_dir": ml_engine.model_dir,
                "message": f"ML engine operational with {len(model_files)} models"
            }
        except Exception as e:
            return {
                "status": "degraded",
                "error": str(e),
                "message": "ML engine check failed"
            }
    
    async def _check_filesystem(self) -> Dict[str, Any]:
        """Check critical filesystem paths."""
        paths_to_check = [
            "/opt/cai/data/ml_models",
            "/opt/cai/data/knowledge_base",
            "/opt/cai/logs"
        ]
        
        results = {"status": "healthy", "paths": {}}
        
        for path in paths_to_check:
            try:
                path_obj = Path(path)
                if path_obj.exists():
                    # Check if writable
                    test_file = path_obj / f".health_check_{int(time.time())}"
                    try:
                        test_file.write_text("health check")
                        test_file.unlink()
                        results["paths"][path] = {"status": "healthy", "writable": True}
                    except PermissionError:
                        results["paths"][path] = {"status": "degraded", "writable": False}
                        results["status"] = "degraded"
                else:
                    results["paths"][path] = {"status": "unhealthy", "exists": False}
                    results["status"] = "degraded"
            except Exception as e:
                results["paths"][path] = {"status": "error", "error": str(e)}
                results["status"] = "degraded"
        
        return results
    
    async def _check_resources(self) -> Dict[str, Any]:
        """Check system resource usage."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            status = "healthy"
            alerts = []
            
            if cpu_percent > self.config["alerts"]["cpu_threshold"]:
                status = "degraded"
                alerts.append(f"High CPU usage: {cpu_percent:.1f}%")
            
            if memory.percent > self.config["alerts"]["memory_threshold"]:
                status = "degraded"
                alerts.append(f"High memory usage: {memory.percent:.1f}%")
            
            if disk.percent > self.config["alerts"]["disk_threshold"]:
                status = "degraded"
                alerts.append(f"High disk usage: {disk.percent:.1f}%")
            
            return {
                "status": status,
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / (1024**3),
                "alerts": alerts
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def collect_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive system metrics."""
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "system": await self._collect_system_metrics(),
            "ml": await self._collect_ml_metrics(),
            "performance": await self._collect_performance_metrics()
        }
        
        # Store in history
        self.metrics_history.append(metrics)
        
        # Clean old metrics
        cutoff_date = datetime.utcnow() - timedelta(days=self.config["retention_days"])
        self.metrics_history = [
            m for m in self.metrics_history 
            if datetime.fromisoformat(m["timestamp"]) > cutoff_date
        ]
        
        return metrics
    
    async def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system-level metrics."""
        try:
            return {
                "cpu": {
                    "percent": psutil.cpu_percent(interval=1),
                    "count": psutil.cpu_count(),
                    "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None
                },
                "memory": {
                    "total_gb": psutil.virtual_memory().total / (1024**3),
                    "used_gb": psutil.virtual_memory().used / (1024**3),
                    "percent": psutil.virtual_memory().percent
                },
                "disk": {
                    "total_gb": psutil.disk_usage('/').total / (1024**3),
                    "used_gb": psutil.disk_usage('/').used / (1024**3),
                    "percent": psutil.disk_usage('/').percent
                },
                "network": {
                    "bytes_sent": psutil.net_io_counters().bytes_sent,
                    "bytes_recv": psutil.net_io_counters().bytes_recv
                }
            }
        except Exception as e:
            logger.error(f"System metrics collection error: {e}")
            return {"error": str(e)}
    
    async def _collect_ml_metrics(self) -> Dict[str, Any]:
        """Collect ML-specific metrics."""
        try:
            from cai.ml_engine import MLEngine
            
            ml_engine = MLEngine()
            model_dir = Path(ml_engine.model_dir)
            
            # Count model files
            model_files = list(model_dir.glob("*.pkl"))
            
            # Get training data info if available
            training_data_file = model_dir / "training_data.json"
            training_samples = 0
            if training_data_file.exists():
                try:
                    with open(training_data_file, 'r') as f:
                        training_data = json.load(f)
                        training_samples = len(training_data)
                except Exception:
                    pass
            
            return {
                "models_count": len(model_files),
                "training_samples": training_samples,
                "model_dir_size_mb": sum(
                    f.stat().st_size for f in model_dir.rglob("*") if f.is_file()
                ) / (1024**2),
                "last_training": self._get_last_training_time(model_dir)
            }
        except Exception as e:
            logger.error(f"ML metrics collection error: {e}")
            return {"error": str(e)}
    
    def _get_last_training_time(self, model_dir: Path) -> Optional[str]:
        """Get the last training timestamp."""
        try:
            model_files = list(model_dir.glob("*.pkl"))
            if model_files:
                latest_file = max(model_files, key=lambda f: f.stat().st_mtime)
                return datetime.fromtimestamp(latest_file.stat().st_mtime).isoformat()
        except Exception:
            pass
        return None
    
    async def _collect_performance_metrics(self) -> Dict[str, Any]:
        """Collect performance metrics."""
        try:
            # Get process info for CAI
            current_process = psutil.Process()
            
            return {
                "process": {
                    "pid": current_process.pid,
                    "memory_mb": current_process.memory_info().rss / (1024**2),
                    "cpu_percent": current_process.cpu_percent(),
                    "threads": current_process.num_threads(),
                    "open_files": len(current_process.open_files()),
                    "uptime_seconds": time.time() - current_process.create_time()
                }
            }
        except Exception as e:
            logger.error(f"Performance metrics collection error: {e}")
            return {"error": str(e)}
    
    async def generate_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate alerts based on metrics."""
        alerts = []
        current_time = datetime.utcnow()
        
        # Check for alert conditions
        system_metrics = metrics.get("system", {})
        
        # CPU alert
        cpu_percent = system_metrics.get("cpu", {}).get("percent", 0)
        if cpu_percent > self.config["alerts"]["cpu_threshold"]:
            if self._should_send_alert("high_cpu"):
                alerts.append({
                    "type": "high_cpu",
                    "severity": "warning",
                    "message": f"High CPU usage: {cpu_percent:.1f}%",
                    "timestamp": current_time.isoformat(),
                    "value": cpu_percent,
                    "threshold": self.config["alerts"]["cpu_threshold"]
                })
        
        # Memory alert
        memory_percent = system_metrics.get("memory", {}).get("percent", 0)
        if memory_percent > self.config["alerts"]["memory_threshold"]:
            if self._should_send_alert("high_memory"):
                alerts.append({
                    "type": "high_memory",
                    "severity": "warning",
                    "message": f"High memory usage: {memory_percent:.1f}%",
                    "timestamp": current_time.isoformat(),
                    "value": memory_percent,
                    "threshold": self.config["alerts"]["memory_threshold"]
                })
        
        # Disk alert
        disk_percent = system_metrics.get("disk", {}).get("percent", 0)
        if disk_percent > self.config["alerts"]["disk_threshold"]:
            if self._should_send_alert("high_disk"):
                alerts.append({
                    "type": "high_disk",
                    "severity": "critical",
                    "message": f"High disk usage: {disk_percent:.1f}%",
                    "timestamp": current_time.isoformat(),
                    "value": disk_percent,
                    "threshold": self.config["alerts"]["disk_threshold"]
                })
        
        return alerts
    
    def _should_send_alert(self, alert_type: str) -> bool:
        """Check if alert should be sent based on cooldown."""
        cooldown_minutes = self.config["alerts"]["cooldown_minutes"]
        last_sent = self.alert_cooldowns.get(alert_type)
        
        if last_sent is None:
            self.alert_cooldowns[alert_type] = datetime.utcnow()
            return True
        
        if datetime.utcnow() - last_sent > timedelta(minutes=cooldown_minutes):
            self.alert_cooldowns[alert_type] = datetime.utcnow()
            return True
        
        return False
    
    async def save_metrics(self, metrics: Dict[str, Any], filepath: str = None):
        """Save metrics to file."""
        if filepath is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filepath = f"/opt/cai/logs/metrics_{timestamp}.json"
        
        try:
            with open(filepath, 'w') as f:
                json.dump(metrics, f, indent=2)
            logger.info(f"Metrics saved to {filepath}")
        except Exception as e:
            logger.error(f"Error saving metrics: {e}")
    
    async def run_monitoring_cycle(self):
        """Run one complete monitoring cycle."""
        logger.info("Starting monitoring cycle...")
        
        try:
            # Health check
            health_status = await self.health_check()
            logger.info(f"Health check completed: {health_status['overall_status']}")
            
            # Collect metrics
            metrics = await self.collect_metrics()
            logger.info("Metrics collection completed")
            
            # Generate alerts
            alerts = await self.generate_alerts(metrics)
            if alerts:
                logger.warning(f"Generated {len(alerts)} alerts")
                for alert in alerts:
                    logger.warning(f"ALERT: {alert['message']}")
            
            # Save results
            await self.save_metrics({
                "health": health_status,
                "metrics": metrics,
                "alerts": alerts
            })
            
        except Exception as e:
            logger.error(f"Monitoring cycle error: {e}")
    
    async def run_continuous_monitoring(self):
        """Run continuous monitoring loop."""
        logger.info("Starting continuous monitoring...")
        
        health_check_interval = self.config["health_check_interval"]
        metrics_interval = self.config["metrics_collection_interval"]
        
        last_metrics_time = 0
        
        while True:
            try:
                current_time = time.time()
                
                # Always run health check
                await self.health_check()
                
                # Run metrics collection at longer intervals
                if current_time - last_metrics_time >= metrics_interval:
                    await self.run_monitoring_cycle()
                    last_metrics_time = current_time
                
                # Wait for next cycle
                await asyncio.sleep(health_check_interval)
                
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Continuous monitoring error: {e}")
                await asyncio.sleep(30)  # Wait before retrying


async def main():
    """Main function to run monitoring."""
    import argparse
    
    parser = argparse.ArgumentParser(description="CAI Framework Production Monitor")
    parser.add_argument("--mode", choices=["health", "metrics", "continuous"], 
                       default="continuous", help="Monitoring mode")
    parser.add_argument("--config", default="/opt/cai/config/monitor.json",
                       help="Configuration file path")
    parser.add_argument("--output", help="Output file for results")
    
    args = parser.parse_args()
    
    monitor = CAIMonitor(args.config)
    
    if args.mode == "health":
        result = await monitor.health_check()
        print(json.dumps(result, indent=2))
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
    
    elif args.mode == "metrics":
        result = await monitor.collect_metrics()
        print(json.dumps(result, indent=2))
        if args.output:
            await monitor.save_metrics(result, args.output)
    
    elif args.mode == "continuous":
        await monitor.run_continuous_monitoring()


if __name__ == "__main__":
    asyncio.run(main())
