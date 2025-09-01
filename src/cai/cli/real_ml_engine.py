"""
REAL MACHINE LEARNING ENGINE FOR CYBERSECURITY

This module implements actual machine learning algorithms to learn from cybersecurity
interactions, not just LLM-based text analysis.

Features:
- Real ML models (Random Forest, SVM, Neural Networks)
- Feature extraction from cybersecurity data
- Model training and validation
- Performance metrics
- Automated model retraining
- Ensemble methods
"""

import os
import json
import pickle
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from pathlib import Path

# Machine Learning imports
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.base import BaseEstimator, TransformerMixin
import joblib

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MLPattern:
    """Real ML Pattern with numerical features and predictions."""
    pattern_id: str
    pattern_type: str
    features: Dict[str, float]
    target: str  # What we're predicting
    confidence: float
    created_at: datetime
    model_version: str
    validation_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass 
class TrainingData:
    """Container for ML training data."""
    features: np.ndarray
    targets: np.ndarray
    feature_names: List[str]
    target_names: List[str]
    timestamp: datetime


class CybersecurityFeatureExtractor(BaseEstimator, TransformerMixin):
    """Extract numerical features from cybersecurity interactions."""
    
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000, 
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.fitted = False
    
    def fit(self, X, y=None):
        """Fit the feature extractor."""
        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X)
            
        # Fit text vectorizer if text columns exist
        text_data = []
        for _, row in X.iterrows():
            text = f"{row.get('user_input', '')} {row.get('response', '')}"
            text_data.append(text)
        
        if text_data:
            self.tfidf_vectorizer.fit(text_data)
        
        self.fitted = True
        return self
    
    def transform(self, X):
        """Transform interactions into numerical features."""
        if not self.fitted:
            raise ValueError("FeatureExtractor not fitted!")
            
        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X)
        
        features = []
        
        for _, row in X.iterrows():
            feature_dict = {}
            
            # 1. TEMPORAL FEATURES
            feature_dict['execution_time'] = float(row.get('execution_time', 0))
            feature_dict['hour_of_day'] = datetime.now().hour if 'timestamp' not in row else pd.to_datetime(row['timestamp']).hour
            feature_dict['day_of_week'] = datetime.now().weekday() if 'timestamp' not in row else pd.to_datetime(row['timestamp']).weekday()
            
            # 2. SUCCESS/FAILURE FEATURES
            feature_dict['success'] = 1.0 if row.get('success', False) else 0.0
            feature_dict['error_occurred'] = 1.0 if 'error' in str(row.get('response', '')).lower() else 0.0
            
            # 3. TOOL USAGE FEATURES
            tools_used = row.get('tools_used', [])
            feature_dict['num_tools'] = float(len(tools_used))
            feature_dict['used_nmap'] = 1.0 if any('nmap' in str(tool).lower() for tool in tools_used) else 0.0
            feature_dict['used_metasploit'] = 1.0 if any('metasploit' in str(tool).lower() for tool in tools_used) else 0.0
            feature_dict['used_sqlmap'] = 1.0 if any('sqlmap' in str(tool).lower() for tool in tools_used) else 0.0
            feature_dict['used_exploit'] = 1.0 if any('exploit' in str(tool).lower() for tool in tools_used) else 0.0
            
            # 4. INPUT/OUTPUT COMPLEXITY FEATURES
            user_input = str(row.get('user_input', ''))
            response = str(row.get('response', ''))
            
            feature_dict['input_length'] = float(len(user_input))
            feature_dict['output_length'] = float(len(response))
            feature_dict['input_words'] = float(len(user_input.split()))
            feature_dict['output_words'] = float(len(response.split()))
            
            # 5. CYBERSECURITY KEYWORD FEATURES
            cyber_keywords = {
                'vulnerability': ['vuln', 'vulnerability', 'cve', 'exploit'],
                'reconnaissance': ['scan', 'recon', 'enumerate', 'discover'],
                'network': ['port', 'tcp', 'udp', 'ip', 'domain'],
                'database': ['sql', 'mysql', 'postgres', 'database', 'db'],
                'web': ['http', 'https', 'web', 'url', 'website'],
                'privilege': ['root', 'admin', 'privilege', 'escalation'],
                'password': ['password', 'passwd', 'login', 'auth']
            }
            
            combined_text = f"{user_input} {response}".lower()
            for category, keywords in cyber_keywords.items():
                feature_dict[f'has_{category}'] = 1.0 if any(kw in combined_text for kw in keywords) else 0.0
            
            # 6. NETWORK/IP FEATURES
            import re
            ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
            port_pattern = r'\b(?:port|tcp|udp)[\s:]*(\d+)\b'
            
            feature_dict['has_ip_addresses'] = 1.0 if re.search(ip_pattern, combined_text) else 0.0
            feature_dict['has_port_numbers'] = 1.0 if re.search(port_pattern, combined_text) else 0.0
            
            # 7. TEXT SIMILARITY FEATURES (using TF-IDF)
            try:
                text_features = self.tfidf_vectorizer.transform([combined_text]).toarray()[0]
                # Use top 20 TF-IDF features
                for i, val in enumerate(text_features[:20]):
                    feature_dict[f'tfidf_{i}'] = float(val)
            except:
                # If TF-IDF fails, add zeros
                for i in range(20):
                    feature_dict[f'tfidf_{i}'] = 0.0
            
            features.append(feature_dict)
        
        # Convert to DataFrame and then numpy array
        feature_df = pd.DataFrame(features)
        return feature_df.values
    
    def get_feature_names(self):
        """Get names of extracted features."""
        base_features = [
            'execution_time', 'hour_of_day', 'day_of_week', 'success', 'error_occurred',
            'num_tools', 'used_nmap', 'used_metasploit', 'used_sqlmap', 'used_exploit',
            'input_length', 'output_length', 'input_words', 'output_words',
            'has_vulnerability', 'has_reconnaissance', 'has_network', 'has_database',
            'has_web', 'has_privilege', 'has_password', 'has_ip_addresses', 'has_port_numbers'
        ]
        
        tfidf_features = [f'tfidf_{i}' for i in range(20)]
        return base_features + tfidf_features


class RealMLEngine:
    """Real Machine Learning Engine for Cybersecurity."""
    
    def __init__(self, models_dir: str = "data/ml_models"):
        """Initialize the real ML engine."""
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Feature extractor
        self.feature_extractor = CybersecurityFeatureExtractor()
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        
        # ML Models ensemble
        self.models = {
            'random_forest': RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            ),
            'gradient_boosting': GradientBoostingClassifier(
                n_estimators=100,
                max_depth=6,
                random_state=42
            ),
            'svm': SVC(
                probability=True,
                random_state=42
            ),
            'neural_network': MLPClassifier(
                hidden_layer_sizes=(100, 50),
                max_iter=500,
                random_state=42
            )
        }
        
        # Training data storage
        self.training_data: List[Dict[str, Any]] = []
        self.is_trained = False
        self.model_version = "1.0.0"
        self.last_training = None
        
        # Performance metrics
        self.model_performance = {}
        
        # Load existing models if available
        self._load_models()
    
    def add_training_sample(self, interaction_data: Dict[str, Any]) -> None:
        """Add a training sample from cybersecurity interaction."""
        
        # Create target labels based on interaction success and type
        target = self._create_target_label(interaction_data)
        
        training_sample = {
            **interaction_data,
            'target': target,
            'timestamp': datetime.now().isoformat()
        }
        
        self.training_data.append(training_sample)
        
        # Auto-retrain if we have enough new data
        if len(self.training_data) % 50 == 0 and len(self.training_data) >= 100:
            logger.info(f"Auto-retraining triggered with {len(self.training_data)} samples")
            self.train_models()
    
    def _create_target_label(self, interaction_data: Dict[str, Any]) -> str:
        """Create target labels for ML training."""
        success = interaction_data.get('success', False)
        interaction_type = interaction_data.get('interaction_type', 'general')
        tools_used = interaction_data.get('tools_used', [])
        response = str(interaction_data.get('response', '')).lower()
        
        # Complex target labeling based on multiple factors
        if not success:
            return 'failure'
        
        # Successful operations get more specific labels
        if interaction_type == 'reconnaissance':
            if any('nmap' in str(tool).lower() for tool in tools_used):
                return 'successful_nmap_recon'
            elif 'discover' in response or 'found' in response:
                return 'successful_discovery'
            else:
                return 'successful_recon'
        
        elif interaction_type == 'exploitation':
            if 'root' in response or 'admin' in response:
                return 'successful_privilege_escalation'
            elif 'access' in response or 'shell' in response:
                return 'successful_access'
            else:
                return 'successful_exploit'
        
        elif interaction_type == 'tool_usage':
            if any('sql' in str(tool).lower() for tool in tools_used):
                return 'successful_sql_tool'
            elif any('metasploit' in str(tool).lower() for tool in tools_used):
                return 'successful_metasploit'
            else:
                return 'successful_tool'
        
        else:
            return 'successful_general'
    
    def train_models(self) -> Dict[str, float]:
        """Train all ML models with current data."""
        if len(self.training_data) < 10:
            logger.warning(f"Not enough training data: {len(self.training_data)} samples")
            return {}
        
        logger.info(f"Training ML models with {len(self.training_data)} samples")
        
        # Prepare training data
        df = pd.DataFrame(self.training_data)
        
        # Extract features
        X = self.feature_extractor.fit_transform(df)
        
        # Extract targets
        targets = df['target'].values
        y = self.label_encoder.fit_transform(targets)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data - check if stratification is possible
        from collections import Counter
        y_counts = Counter(y)
        min_class_count = min(y_counts.values())
        
        if min_class_count >= 2:
            # Safe to use stratify
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42, stratify=y
            )
        else:
            # Skip stratification for small datasets
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42
            )
        
        performance = {}
        
        # Train each model
        for model_name, model in self.models.items():
            logger.info(f"Training {model_name}...")
            
            try:
                # Train model
                model.fit(X_train, y_train)
                
                # Evaluate
                y_pred = model.predict(X_test)
                accuracy = accuracy_score(y_test, y_pred)
                
                # Cross-validation
                cv_scores = cross_val_score(model, X_scaled, y, cv=5)
                
                performance[model_name] = {
                    'accuracy': accuracy,
                    'cv_mean': cv_scores.mean(),
                    'cv_std': cv_scores.std(),
                    'samples_trained': len(X_train)
                }
                
                logger.info(f"{model_name}: Accuracy={accuracy:.3f}, CV={cv_scores.mean():.3f}±{cv_scores.std():.3f}")
                
            except Exception as e:
                logger.error(f"Error training {model_name}: {e}")
                performance[model_name] = {'error': str(e)}
        
        self.model_performance = performance
        self.is_trained = True
        self.last_training = datetime.now()
        self.model_version = f"{self.model_version.split('.')[0]}.{int(self.model_version.split('.')[1]) + 1}.0"
        
        # Save models
        self._save_models()
        
        logger.info(f"Model training completed. New version: {self.model_version}")
        return performance
    
    def predict(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make ML predictions on new interaction data."""
        if not self.is_trained:
            return {
                'prediction': 'unknown',
                'confidence': 0.0,
                'error': 'Models not trained'
            }
        
        try:
            # Extract features
            df = pd.DataFrame([interaction_data])
            X = self.feature_extractor.transform(df)
            X_scaled = self.scaler.transform(X)
            
            # Get predictions from all models
            predictions = {}
            confidences = {}
            
            for model_name, model in self.models.items():
                if hasattr(model, 'predict_proba'):
                    pred_proba = model.predict_proba(X_scaled)[0]
                    pred_class = model.classes_[np.argmax(pred_proba)]
                    confidence = np.max(pred_proba)
                else:
                    pred_class = model.predict(X_scaled)[0]
                    confidence = 0.5  # Default confidence for models without probability
                
                # Convert back to original label
                original_label = self.label_encoder.inverse_transform([pred_class])[0]
                
                predictions[model_name] = original_label
                confidences[model_name] = float(confidence)
            
            # Ensemble prediction (majority voting)
            pred_counts = {}
            for pred in predictions.values():
                pred_counts[pred] = pred_counts.get(pred, 0) + 1
            
            ensemble_pred = max(pred_counts, key=pred_counts.get)
            ensemble_confidence = np.mean(list(confidences.values()))
            
            return {
                'prediction': ensemble_pred,
                'confidence': float(ensemble_confidence),
                'individual_predictions': predictions,
                'individual_confidences': confidences,
                'model_version': self.model_version,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            return {
                'prediction': 'error',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def get_feature_importance(self) -> Dict[str, Dict[str, float]]:
        """Get feature importance from tree-based models."""
        importance = {}
        feature_names = self.feature_extractor.get_feature_names()
        
        for model_name, model in self.models.items():
            if hasattr(model, 'feature_importances_'):
                importance[model_name] = dict(zip(feature_names, model.feature_importances_))
        
        return importance
    
    def optimize_hyperparameters(self) -> Dict[str, Any]:
        """Perform hyperparameter optimization using GridSearch."""
        if len(self.training_data) < 50:
            logger.warning("Not enough data for hyperparameter optimization")
            return {}
        
        logger.info("Starting hyperparameter optimization...")
        
        # Prepare data
        df = pd.DataFrame(self.training_data)
        X = self.feature_extractor.transform(df)
        X_scaled = self.scaler.transform(X)
        y = self.label_encoder.transform(df['target'].values)
        
        # Parameter grids
        param_grids = {
            'random_forest': {
                'n_estimators': [50, 100, 200],
                'max_depth': [5, 10, 15],
                'min_samples_split': [2, 5, 10]
            },
            'gradient_boosting': {
                'n_estimators': [50, 100, 150],
                'max_depth': [3, 5, 7],
                'learning_rate': [0.01, 0.1, 0.2]
            }
        }
        
        best_params = {}
        
        for model_name in ['random_forest', 'gradient_boosting']:
            logger.info(f"Optimizing {model_name}...")
            
            model = self.models[model_name]
            param_grid = param_grids[model_name]
            
            grid_search = GridSearchCV(
                model, param_grid, cv=3, scoring='accuracy', n_jobs=-1
            )
            
            grid_search.fit(X_scaled, y)
            
            best_params[model_name] = {
                'best_params': grid_search.best_params_,
                'best_score': grid_search.best_score_
            }
            
            # Update model with best parameters
            self.models[model_name] = grid_search.best_estimator_
            
            logger.info(f"{model_name} best score: {grid_search.best_score_:.3f}")
        
        return best_params
    
    def get_model_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the ML models."""
        stats = {
            'training_samples': len(self.training_data),
            'is_trained': self.is_trained,
            'model_version': self.model_version,
            'last_training': self.last_training.isoformat() if self.last_training else None,
            'performance': self.model_performance,
            'feature_count': len(self.feature_extractor.get_feature_names()) if hasattr(self.feature_extractor, 'fitted') and self.feature_extractor.fitted else 0
        }
        
        if self.is_trained and self.training_data:
            # Add target distribution
            df = pd.DataFrame(self.training_data)
            if 'target' in df.columns:
                target_dist = df['target'].value_counts().to_dict()
                stats['target_distribution'] = target_dist
            
            # Add feature importance
            stats['feature_importance'] = self.get_feature_importance()
        
        return stats
    
    def _save_models(self) -> None:
        """Save trained models to disk."""
        try:
            # Save models
            for model_name, model in self.models.items():
                model_path = self.models_dir / f"{model_name}_v{self.model_version}.pkl"
                joblib.dump(model, model_path)
            
            # Save supporting components
            joblib.dump(self.feature_extractor, self.models_dir / f"feature_extractor_v{self.model_version}.pkl")
            joblib.dump(self.scaler, self.models_dir / f"scaler_v{self.model_version}.pkl")
            joblib.dump(self.label_encoder, self.models_dir / f"label_encoder_v{self.model_version}.pkl")
            
            # Save metadata
            metadata = {
                'model_version': self.model_version,
                'training_samples': len(self.training_data),
                'last_training': self.last_training.isoformat() if self.last_training else None,
                'performance': self.model_performance
            }
            
            with open(self.models_dir / f"metadata_v{self.model_version}.json", 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Models saved to {self.models_dir}")
            
        except Exception as e:
            logger.error(f"Error saving models: {e}")
    
    def _load_models(self) -> bool:
        """Load the latest trained models from disk."""
        try:
            # Find latest version
            model_files = list(self.models_dir.glob("metadata_v*.json"))
            if not model_files:
                logger.info("No saved models found")
                return False
            
            latest_metadata_file = max(model_files, key=lambda x: x.stat().st_mtime)
            
            with open(latest_metadata_file, 'r') as f:
                metadata = json.load(f)
            
            version = metadata['model_version']
            logger.info(f"Loading models version {version}")
            
            # Load models
            for model_name in self.models.keys():
                model_path = self.models_dir / f"{model_name}_v{version}.pkl"
                if model_path.exists():
                    self.models[model_name] = joblib.load(model_path)
            
            # Load supporting components
            self.feature_extractor = joblib.load(self.models_dir / f"feature_extractor_v{version}.pkl")
            self.scaler = joblib.load(self.models_dir / f"scaler_v{version}.pkl")
            self.label_encoder = joblib.load(self.models_dir / f"label_encoder_v{version}.pkl")
            
            # Load metadata
            self.model_version = version
            self.model_performance = metadata.get('performance', {})
            self.is_trained = True
            
            if metadata.get('last_training'):
                self.last_training = datetime.fromisoformat(metadata['last_training'])
            
            logger.info(f"Successfully loaded models version {version}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            return False


# Global ML engine instance
_ml_engine: Optional[RealMLEngine] = None


def get_ml_engine() -> RealMLEngine:
    """Get the global ML engine instance."""
    global _ml_engine
    if _ml_engine is None:
        _ml_engine = RealMLEngine()
    return _ml_engine


def initialize_real_ml() -> None:
    """Initialize the real machine learning system."""
    engine = get_ml_engine()
    stats = engine.get_model_stats()
    
    print("🤖 Real Machine Learning Engine Initialized")
    print(f"  • Training samples: {stats['training_samples']}")
    print(f"  • Models trained: {stats['is_trained']}")
    print(f"  • Model version: {stats['model_version']}")
    print(f"  • Feature count: {stats['feature_count']}")
    
    if stats['performance']:
        print("  • Model Performance:")
        for model_name, perf in stats['performance'].items():
            if 'accuracy' in perf:
                print(f"    - {model_name}: {perf['accuracy']:.3f} accuracy")
