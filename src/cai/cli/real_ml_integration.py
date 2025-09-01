"""
REAL MACHINE LEARNING INTEGRATION FOR CAI

This module integrates the real ML engine with CAI's CLI system,
replacing the fake "continuous learning" with actual machine learning.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from .real_ml_engine import get_ml_engine, initialize_real_ml

logger = logging.getLogger(__name__)


class RealMLIntegration:
    """Integration manager for real machine learning with CAI."""
    
    def __init__(self):
        """Initialize the real ML integration."""
        self.ml_engine = get_ml_engine()
        self.learning_enabled = True
        self.current_session_id: Optional[str] = None
        self.session_interactions: List[Dict[str, Any]] = []
        
        # Performance tracking
        self.predictions_made = 0
        self.correct_predictions = 0
    
    def enable_learning(self) -> None:
        """Enable real machine learning."""
        self.learning_enabled = True
        print("🤖 Real Machine Learning ENABLED")
    
    def disable_learning(self) -> None:
        """Disable real machine learning."""
        self.learning_enabled = False
        print("🚫 Real Machine Learning DISABLED")
    
    def start_ml_session(self, session_id: str) -> None:
        """Start a new ML learning session."""
        if not self.learning_enabled:
            return
        
        self.current_session_id = session_id
        self.session_interactions = []
        print(f"🧠 ML Session started: {session_id}")
    
    async def record_interaction(
        self,
        agent_name: str,
        user_input: str,
        agent_response: Any,
        success: bool = None,
        execution_time: float = None,
        tools_used: List[str] = None,
        context: str = "general"
    ) -> None:
        """Record an interaction for ML training."""
        if not self.learning_enabled or not self.current_session_id:
            return
        
        # Extract response content
        response_content = ""
        if hasattr(agent_response, 'final_output') and agent_response.final_output:
            response_content = agent_response.final_output
        elif hasattr(agent_response, 'content'):
            response_content = agent_response.content
        else:
            response_content = str(agent_response)
        
        # Auto-assess success if not provided
        if success is None:
            success = self._assess_success(response_content, user_input)
        
        # Classify interaction type
        interaction_type = self._classify_interaction(user_input, response_content)
        
        interaction_data = {
            'agent_name': agent_name,
            'user_input': user_input,
            'response': response_content,
            'success': success,
            'execution_time': execution_time or 0.0,
            'tools_used': tools_used or [],
            'interaction_type': interaction_type,
            'context': context,
            'timestamp': datetime.now().isoformat(),
            'session_id': self.current_session_id
        }
        
        # Store for session and add to ML training data
        self.session_interactions.append(interaction_data)
        self.ml_engine.add_training_sample(interaction_data)
        
        print(f"📊 ML Sample recorded: {interaction_type} ({'success' if success else 'failure'})")
    
    def _assess_success(self, response: str, user_input: str) -> bool:
        """Auto-assess interaction success using heuristics."""
        response_lower = response.lower()
        input_lower = user_input.lower()
        
        # Success indicators
        success_keywords = [
            'successfully', 'completed', 'found', 'discovered', 'identified',
            'access granted', 'vulnerability', 'exploit', 'shell', 'root',
            'admin', 'password', 'credential', 'compromised'
        ]
        
        # Failure indicators  
        failure_keywords = [
            'failed', 'error', 'unable', 'cannot', 'denied', 'blocked',
            'not found', 'no results', 'timeout', 'connection refused'
        ]
        
        success_score = sum(1 for kw in success_keywords if kw in response_lower)
        failure_score = sum(1 for kw in failure_keywords if kw in response_lower)
        
        if success_score > failure_score:
            return True
        elif failure_score > success_score:
            return False
        
        # Default: success if response is substantial
        return len(response.strip()) > 20
    
    def _classify_interaction(self, user_input: str, response: str) -> str:
        """Classify interaction type for ML training."""
        input_lower = user_input.lower()
        response_lower = response.lower()
        
        # Classification based on keywords
        if any(kw in input_lower for kw in ['scan', 'nmap', 'discover', 'enumerate', 'recon']):
            return 'reconnaissance'
        elif any(kw in input_lower for kw in ['exploit', 'attack', 'payload', 'metasploit']):
            return 'exploitation'
        elif any(kw in input_lower for kw in ['sql', 'sqlmap', 'database', 'inject']):
            return 'database_attack'
        elif any(kw in input_lower for kw in ['privilege', 'escalate', 'root', 'admin']):
            return 'privilege_escalation'
        elif any(kw in input_lower for kw in ['password', 'crack', 'brute', 'hash']):
            return 'credential_attack'
        elif any(kw in response_lower for kw in ['tool', 'command', 'execute']):
            return 'tool_usage'
        else:
            return 'general_security'
    
    async def predict_outcome(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use ML to predict interaction outcome."""
        if not self.learning_enabled or not self.ml_engine.is_trained:
            return {
                'prediction': 'unknown',
                'confidence': 0.0,
                'advice': 'ML models not trained yet'
            }
        
        try:
            prediction = self.ml_engine.predict(interaction_data)
            self.predictions_made += 1
            
            # Generate advice based on prediction
            advice = self._generate_advice(prediction)
            
            result = {
                **prediction,
                'advice': advice,
                'ml_engine_version': self.ml_engine.model_version
            }
            
            print(f"🔮 ML Prediction: {prediction['prediction']} (confidence: {prediction['confidence']:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"Error making ML prediction: {e}")
            return {
                'prediction': 'error',
                'confidence': 0.0,
                'error': str(e),
                'advice': 'Unable to make prediction'
            }
    
    def _generate_advice(self, prediction: Dict[str, Any]) -> str:
        """Generate actionable advice based on ML prediction."""
        pred_class = prediction.get('prediction', '')
        confidence = prediction.get('confidence', 0.0)
        
        if confidence < 0.5:
            return "Low confidence prediction - proceed with caution"
        
        advice_map = {
            'successful_nmap_recon': "High success probability for nmap reconnaissance. Consider comprehensive port scanning.",
            'successful_discovery': "Discovery operation likely to succeed. Focus on thorough enumeration.",
            'successful_privilege_escalation': "Privilege escalation has good chance of success. Check for common vulnerabilities.",
            'successful_access': "System access likely achievable. Prepare post-exploitation strategies.",
            'successful_exploit': "Exploitation attempt has high success probability. Ensure you have proper authorization.",
            'successful_sql_tool': "SQL injection tools likely to be effective. Try different payloads systematically.",
            'successful_metasploit': "Metasploit modules should work well in this scenario. Check module options carefully.",
            'failure': "Operation likely to fail. Consider alternative approaches or gather more intelligence first."
        }
        
        base_advice = advice_map.get(pred_class, "Standard security assessment recommended.")
        
        if confidence > 0.8:
            return f"HIGH CONFIDENCE: {base_advice}"
        elif confidence > 0.6:
            return f"MEDIUM CONFIDENCE: {base_advice}"
        else:
            return f"LOW CONFIDENCE: {base_advice} Verify assumptions."
    
    async def get_ml_insights(self, context: str) -> Dict[str, Any]:
        """Get ML-based insights for given context."""
        if not self.learning_enabled:
            return {
                'insights': [],
                'message': 'ML learning disabled'
            }
        
        stats = self.ml_engine.get_model_stats()
        
        # Generate insights based on ML model performance and feature importance
        insights = []
        
        if self.ml_engine.is_trained:
            feature_importance = self.ml_engine.get_feature_importance()
            
            # Get top important features across all models
            all_importance = {}
            for model_name, features in feature_importance.items():
                for feature, importance in features.items():
                    if feature not in all_importance:
                        all_importance[feature] = []
                    all_importance[feature].append(importance)
            
            # Calculate average importance
            avg_importance = {
                feature: sum(scores) / len(scores)
                for feature, scores in all_importance.items()
            }
            
            # Sort by importance
            top_features = sorted(avg_importance.items(), key=lambda x: x[1], reverse=True)[:5]
            
            insights.append({
                'type': 'feature_importance',
                'title': 'Most Important Success Factors',
                'data': [f"{feature}: {importance:.3f}" for feature, importance in top_features],
                'confidence': 0.9
            })
            
            # Model performance insights
            if stats['performance']:
                best_model = max(stats['performance'].items(), 
                               key=lambda x: x[1].get('accuracy', 0) if isinstance(x[1], dict) else 0)
                
                insights.append({
                    'type': 'model_performance',
                    'title': f'Best Performing Model: {best_model[0]}',
                    'data': f"Accuracy: {best_model[1].get('accuracy', 0):.3f}",
                    'confidence': best_model[1].get('accuracy', 0)
                })
        
        return {
            'insights': insights,
            'model_stats': stats,
            'context': context,
            'timestamp': datetime.now().isoformat()
        }
    
    async def train_models(self) -> Dict[str, Any]:
        """Trigger ML model training."""
        if not self.learning_enabled:
            return {'error': 'ML learning disabled'}
        
        print("🏋️ Training ML models...")
        performance = self.ml_engine.train_models()
        
        if performance:
            print("✅ ML Training completed!")
            for model_name, perf in performance.items():
                if 'accuracy' in perf:
                    print(f"  • {model_name}: {perf['accuracy']:.3f} accuracy")
        
        return {
            'training_completed': True,
            'performance': performance,
            'model_version': self.ml_engine.model_version,
            'training_samples': len(self.ml_engine.training_data)
        }
    
    async def optimize_models(self) -> Dict[str, Any]:
        """Optimize ML model hyperparameters."""
        if not self.learning_enabled:
            return {'error': 'ML learning disabled'}
        
        print("🔧 Optimizing ML model hyperparameters...")
        optimization_results = self.ml_engine.optimize_hyperparameters()
        
        if optimization_results:
            print("✅ Hyperparameter optimization completed!")
            for model_name, results in optimization_results.items():
                print(f"  • {model_name}: {results['best_score']:.3f} best score")
        
        return optimization_results
    
    def validate_prediction(self, prediction_id: str, actual_outcome: bool) -> None:
        """Validate ML prediction against actual outcome."""
        if actual_outcome:
            self.correct_predictions += 1
        
        accuracy = self.correct_predictions / max(self.predictions_made, 1)
        print(f"📈 ML Prediction accuracy: {accuracy:.2f} ({self.correct_predictions}/{self.predictions_made})")
    
    def get_ml_status(self) -> Dict[str, Any]:
        """Get current ML system status."""
        stats = self.ml_engine.get_model_stats()
        
        prediction_accuracy = self.correct_predictions / max(self.predictions_made, 1) if self.predictions_made > 0 else 0.0
        
        return {
            'enabled': self.learning_enabled,
            'current_session': self.current_session_id,
            'models_trained': stats['is_trained'],
            'model_version': stats['model_version'],
            'training_samples': stats['training_samples'],
            'feature_count': stats['feature_count'],
            'model_performance': stats['performance'],
            'predictions_made': self.predictions_made,
            'prediction_accuracy': prediction_accuracy,
            'last_training': stats['last_training'],
            'session_interactions': len(self.session_interactions)
        }
    
    async def end_session_and_learn(self) -> Dict[str, Any]:
        """End current ML session and analyze results."""
        if not self.current_session_id:
            return {'message': 'No active session'}
        
        session_id = self.current_session_id
        interactions_count = len(self.session_interactions)
        
        # Trigger training if we have enough new data
        training_triggered = False
        if len(self.ml_engine.training_data) >= 20:
            await self.train_models()
            training_triggered = True
        
        # Reset session
        self.current_session_id = None
        self.session_interactions = []
        
        return {
            'session_id': session_id,
            'interactions_recorded': interactions_count,
            'training_triggered': training_triggered,
            'total_training_samples': len(self.ml_engine.training_data),
            'models_trained': self.ml_engine.is_trained,
            'model_version': self.ml_engine.model_version
        }


# Global ML integration instance
_ml_integration: Optional[RealMLIntegration] = None


def get_ml_integration() -> RealMLIntegration:
    """Get the global ML integration instance."""
    global _ml_integration
    if _ml_integration is None:
        _ml_integration = RealMLIntegration()
    return _ml_integration


async def initialize_real_ml_integration() -> None:
    """Initialize the real ML integration system."""
    initialize_real_ml()
    integration = get_ml_integration()
    
    print("🚀 Real ML Integration System Initialized")
    status = integration.get_ml_status()
    print(f"  • ML enabled: {status['enabled']}")
    print(f"  • Models trained: {status['models_trained']}")
    print(f"  • Training samples: {status['training_samples']}")
    print(f"  • Feature count: {status['feature_count']}")


# Integration hooks for CAI components
async def ml_hook_before_agent_run(agent: Any, user_input: str, context: str) -> Dict[str, Any]:
    """Hook to run before agent execution for ML prediction."""
    integration = get_ml_integration()
    if not integration.learning_enabled:
        return {}
    
    # Create interaction data for prediction
    interaction_data = {
        'user_input': user_input,
        'context': context,
        'agent_name': getattr(agent, 'name', 'Unknown'),
        'timestamp': datetime.now().isoformat()
    }
    
    # Get ML prediction
    prediction = await integration.predict_outcome(interaction_data)
    
    return prediction


async def ml_hook_after_agent_run(
    agent: Any,
    user_input: str,
    response: Any,
    execution_time: float,
    tools_used: List[str],
    context: str = "general"
) -> None:
    """Hook to run after agent execution for ML learning."""
    integration = get_ml_integration()
    if not integration.learning_enabled:
        return
    
    agent_name = getattr(agent, 'name', 'Unknown Agent')
    await integration.record_interaction(
        agent_name=agent_name,
        user_input=user_input,
        agent_response=response,
        execution_time=execution_time,
        tools_used=tools_used,
        context=context
    )


def ml_hook_session_start(session_id: str) -> None:
    """Hook when ML session starts."""
    integration = get_ml_integration()
    integration.start_ml_session(session_id)


async def ml_hook_session_end() -> Dict[str, Any]:
    """Hook when ML session ends."""
    integration = get_ml_integration()
    return await integration.end_session_and_learn()
