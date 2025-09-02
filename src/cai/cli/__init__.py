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
# Try to import the original CLI with Napoleon> prompt first
try:
    # Import the original CAI CLI that uses Napoleon> prompt
    from cai.cli import main as original_main
    main = original_main
    print("🏛️ Loaded original NAPOLEON CLI interface")
except ImportError:
    # Try ML-dependent components as fallback
    try:
        from .main import main_refactored
        from .integrated_main import main_with_learning
        from .real_ml_main import main_with_real_ml
        # Use the refactored main as fallback
        main = main_refactored
        print("⚠️  Using fallback CLI (Napoleon interface may not be available)")
    except ImportError as e:
        # Final fallback to basic CLI if all ML dependencies are unavailable
        print(f"Warning: ML features unavailable due to import error: {e}")
        # Create a simple main function that works without ML dependencies
        def main():
            import sys
            print("CAI Framework - Basic Mode")
            print("ML features are unavailable due to dependency conflicts")
            print("Please fix NumPy/pandas/scikit-learn version conflicts to enable full functionality")
            print("")
            print("Available commands:")
            print("  --help      Show this help message")
            print("  --version   Show version information")
            
            if len(sys.argv) > 1:
                if "--version" in sys.argv:
                    print("CAI Framework v0.5.3")
                elif "--help" in sys.argv:
                    print("CAI Framework - Cybersecurity AI")
                else:
                    print(f"Unknown command: {' '.join(sys.argv[1:])}")
            else:
                print("Use --help for more information")

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
