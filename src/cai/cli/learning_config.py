"""
Configuration and Setup for Continuous Learning System

Provides configuration management and setup utilities for the learning system.
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path


class LearningConfig:
    """Configuration manager for the continuous learning system."""

    DEFAULT_CONFIG = {
        "enabled": True,
        "knowledge_base_path": "data/knowledge_base",
        "learning_config": {
            "min_confidence_threshold": 0.7,
            "max_patterns_per_session": 10,
            "learning_interval_minutes": 30,
            "feedback_collection_enabled": True,
            "pattern_similarity_threshold": 0.85,
            "auto_update_models": False
        },
        "model_config": {
            "learning_model": "openai/gpt-4o",
            "embedding_model": "text-embedding-3-small",
            "max_tokens_per_analysis": 2000,
            "temperature": 0.3
        },
        "storage_config": {
            "max_patterns": 10000,
            "cleanup_old_patterns": True,
            "pattern_retention_days": 365,
            "compress_old_sessions": True
        },
        "privacy_config": {
            "anonymize_sensitive_data": True,
            "exclude_commands": ["password", "key", "token", "secret"],
            "data_retention_policy": "1_year"
        },
        "performance_config": {
            "max_concurrent_analyses": 3,
            "analysis_timeout_seconds": 60,
            "background_processing": True
        }
    }

    def __init__(self, config_file: str = "config/learning_config.json"):
        """Initialize learning configuration.

        Args:
            config_file: Path to configuration file
        """
        self.config_file = Path(config_file)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default.

        Returns:
            Dict with configuration
        """
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to handle missing keys
                    return self._merge_configs(self.DEFAULT_CONFIG, loaded_config)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
                return self.DEFAULT_CONFIG.copy()
        else:
            # Create default config file
            self._save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()

    def _merge_configs(self, default: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
        """Merge loaded config with defaults.

        Args:
            default: Default configuration
            loaded: Loaded configuration

        Returns:
            Merged configuration
        """
        merged = default.copy()

        for key, value in loaded.items():
            if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value

        return merged

    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file.

        Args:
            config: Configuration to save
        """
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.

        Args:
            key: Configuration key (dot notation supported)
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """Set configuration value.

        Args:
            key: Configuration key (dot notation supported)
            value: Value to set
        """
        keys = key.split('.')
        config = self.config

        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Set the value
        config[keys[-1]] = value
        self._save_config(self.config)

    def is_enabled(self) -> bool:
        """Check if learning is enabled.

        Returns:
            bool: True if learning is enabled
        """
        return self.get('enabled', True)

    def enable_learning(self) -> None:
        """Enable continuous learning."""
        self.set('enabled', True)
        print("✓ Continuous learning enabled")

    def disable_learning(self) -> None:
        """Disable continuous learning."""
        self.set('enabled', False)
        print("✓ Continuous learning disabled")

    def get_knowledge_base_path(self) -> str:
        """Get knowledge base path.

        Returns:
            str: Path to knowledge base
        """
        return self.get('knowledge_base_path', 'data/knowledge_base')

    def get_learning_model(self) -> str:
        """Get the model used for learning analysis.

        Returns:
            str: Model name
        """
        # First check for specific learning model override
        env_learning_model = os.getenv('CAI_LEARNING_MODEL')
        if env_learning_model:
            return env_learning_model
            
        # Then check for general model setting
        env_model = os.getenv('CAI_MODEL')
        if env_model:
            return env_model
            
        # Finally fall back to configuration file or default
        return self.get('model_config.learning_model', 'openai/gpt-4o')

    def get_min_confidence_threshold(self) -> float:
        """Get minimum confidence threshold for patterns.

        Returns:
            float: Confidence threshold
        """
        return self.get('learning_config.min_confidence_threshold', 0.7)

    def update_model_config(self, model_name: str, **kwargs) -> None:
        """Update model configuration.

        Args:
            model_name: Name of the model to update
            **kwargs: Additional configuration parameters
        """
        current_config = self.get('model_config', {})
        current_config['learning_model'] = model_name

        for key, value in kwargs.items():
            current_config[key] = value

        self.set('model_config', current_config)
        print(f"✓ Updated learning model to: {model_name}")

    def get_privacy_settings(self) -> Dict[str, Any]:
        """Get privacy-related settings.

        Returns:
            Dict with privacy settings
        """
        return self.get('privacy_config', {})

    def should_anonymize_data(self) -> bool:
        """Check if sensitive data should be anonymized.

        Returns:
            bool: True if data should be anonymized
        """
        return self.get('privacy_config.anonymize_sensitive_data', True)

    def get_excluded_commands(self) -> list:
        """Get list of commands to exclude from learning.

        Returns:
            List of excluded command patterns
        """
        return self.get('privacy_config.exclude_commands', [])

    def validate_config(self) -> Dict[str, Any]:
        """Validate current configuration.

        Returns:
            Dict with validation results
        """
        issues = []

        # Check required paths
        kb_path = self.get_knowledge_base_path()
        if not os.path.exists(kb_path):
            issues.append(f"Knowledge base path does not exist: {kb_path}")

        # Check model configuration
        model = self.get_learning_model()
        if not model:
            issues.append("Learning model not configured")

        # Check thresholds
        confidence = self.get_min_confidence_threshold()
        if not (0.0 <= confidence <= 1.0):
            issues.append(f"Invalid confidence threshold: {confidence}")

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'config_summary': {
                'enabled': self.is_enabled(),
                'model': model,
                'confidence_threshold': confidence,
                'knowledge_base': kb_path
            }
        }

    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults."""
        self.config = self.DEFAULT_CONFIG.copy()
        self._save_config(self.config)
        print("✓ Configuration reset to defaults")

    def export_config(self, export_path: str) -> None:
        """Export configuration to file.

        Args:
            export_path: Path to export configuration
        """
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"✓ Configuration exported to: {export_path}")
        except Exception as e:
            print(f"Error exporting config: {e}")

    def import_config(self, import_path: str) -> None:
        """Import configuration from file.

        Args:
            import_path: Path to import configuration from
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)

            self.config = self._merge_configs(self.DEFAULT_CONFIG, imported_config)
            self._save_config(self.config)
            print(f"✓ Configuration imported from: {import_path}")
        except Exception as e:
            print(f"Error importing config: {e}")

    def get_performance_settings(self) -> Dict[str, Any]:
        """Get performance-related settings.

        Returns:
            Dict with performance settings
        """
        return self.get('performance_config', {})

    def __str__(self) -> str:
        """String representation of configuration."""
        return f"LearningConfig(enabled={self.is_enabled()}, model={self.get_learning_model()})"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"LearningConfig(config_file='{self.config_file}', enabled={self.is_enabled()})"


# Global configuration instance
_config_instance: Optional[LearningConfig] = None


def get_learning_config() -> LearningConfig:
    """Get the global learning configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = LearningConfig()
    return _config_instance


def setup_learning_environment():
    """Setup the learning environment with default configuration."""
    config = get_learning_config()

    # Create necessary directories first
    kb_path = Path(config.get_knowledge_base_path())
    kb_path.mkdir(parents=True, exist_ok=True)
    (kb_path / "patterns").mkdir(exist_ok=True)
    (kb_path / "sessions").mkdir(exist_ok=True)

    # Validate configuration after directories are created
    validation = config.validate_config()
    if not validation['valid']:
        print("Configuration issues found:")
        for issue in validation['issues']:
            print(f"  - {issue}")
        return False

    print("✓ Learning environment setup complete")
    print(f"  - Knowledge base: {kb_path}")
    print(f"  - Model: {config.get_learning_model()}")
    print(f"  - Confidence threshold: {config.get_min_confidence_threshold()}")

    return True


if __name__ == "__main__":
    # Example usage
    config = get_learning_config()

    print("Current Learning Configuration:")
    print(f"Enabled: {config.is_enabled()}")
    print(f"Model: {config.get_learning_model()}")
    print(f"Confidence Threshold: {config.get_min_confidence_threshold()}")
    print(f"Knowledge Base: {config.get_knowledge_base_path()}")

    # Validate configuration
    validation = config.validate_config()
    print(f"\nConfiguration Valid: {validation['valid']}")
    if validation['issues']:
        print("Issues:")
        for issue in validation['issues']:
            print(f"  - {issue}")