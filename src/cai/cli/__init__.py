"""
CAI CLI Module

Provides a modular CLI interface for CAI agents with proper separation of concerns,
including continuous learning capabilities.
"""

# Core CLI modules
from .session_manager import SessionManager, CLISession, TimingStats
from .command_processor import CommandProcessor
from .agent_runner import AgentRunner
from .parallel_executor import ParallelExecutor
from .ui_manager import UIManager
from .error_handler import ErrorHandler
from .state_manager import StateManager, CLIState
from .warning_suppressor import WarningSuppressor, setup_warning_suppression

# Continuous learning modules
from .continuous_learning import (
    ContinuousLearningEngine,
    LearningPattern,
    LearningSession,
    get_learning_engine,
    start_background_learning
)
from .learning_integration import (
    LearningIntegrationManager,
    get_learning_integration,
    initialize_learning_integration,
    learning_hook_before_agent_run,
    learning_hook_after_agent_run,
    learning_hook_session_start,
    learning_hook_session_end
)
from .enhanced_agent_runner import EnhancedAgentRunner
from .learning_config import LearningConfig, get_learning_config, setup_learning_environment
# Import main functions
from .main import main_refactored
from .integrated_main import main_with_learning
from .real_ml_main import main_with_real_ml

# Default to REAL ML main
main = main_with_real_ml

__all__ = [
    # Core CLI
    "SessionManager",
    "CLISession",
    "TimingStats",
    "CommandProcessor",
    "AgentRunner",
    "ParallelExecutor",
    "UIManager",
    "ErrorHandler",
    "StateManager",
    "CLIState",
    "WarningSuppressor",
    "setup_warning_suppression",

    # Continuous Learning
    "ContinuousLearningEngine",
    "LearningPattern",
    "LearningSession",
    "get_learning_engine",
    "start_background_learning",
    "LearningIntegrationManager",
    "get_learning_integration",
    "initialize_learning_integration",
    "learning_hook_before_agent_run",
    "learning_hook_after_agent_run",
    "learning_hook_session_start",
    "learning_hook_session_end",
    "EnhancedAgentRunner",
    "LearningConfig",
    "get_learning_config",
    "setup_learning_environment",
    "main",
]
