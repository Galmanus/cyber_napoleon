"""
Test script for refactored CLI modules

Verifies that all modules can be imported and instantiated correctly.
"""

import sys
import os
from rich.console import Console

# Add the parent directory to the path to import CAI modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def test_module_imports():
    """Test that all refactored modules can be imported."""
    print("Testing module imports...")

    try:
        from cai.cli.session_manager import SessionManager, CLISession, TimingStats
        print("✓ Session manager imported successfully")

        from cai.cli.command_processor import CommandProcessor
        print("✓ Command processor imported successfully")

        from cai.cli.agent_runner import AgentRunner
        print("✓ Agent runner imported successfully")

        from cai.cli.parallel_executor import ParallelExecutor
        print("✓ Parallel executor imported successfully")

        from cai.cli.ui_manager import UIManager
        print("✓ UI manager imported successfully")

        from cai.cli.error_handler import ErrorHandler
        print("✓ Error handler imported successfully")

        from cai.cli.state_manager import StateManager, CLIState
        print("✓ State manager imported successfully")

        from cai.cli.warning_suppressor import WarningSuppressor, setup_warning_suppression
        print("✓ Warning suppressor imported successfully")

        from cai.cli.main import main_async_refactored, main_refactored
        print("✓ Main CLI module imported successfully")

        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_module_instantiation():
    """Test that modules can be instantiated."""
    print("\nTesting module instantiation...")

    try:
        console = Console()

        # Test session manager
        session_manager = SessionManager()
        session = session_manager.create_session()
        print("✓ Session manager instantiated")

        # Test state manager
        state_manager = StateManager()
        state = state_manager.get_state()
        print("✓ State manager instantiated")

        # Test UI manager
        ui_manager = UIManager(console)
        print("✓ UI manager instantiated")

        # Test command processor
        command_processor = CommandProcessor(console)
        print("✓ Command processor instantiated")

        # Test agent runner
        agent_runner = AgentRunner(console)
        print("✓ Agent runner instantiated")

        # Test parallel executor
        parallel_executor = ParallelExecutor(console)
        print("✓ Parallel executor instantiated")

        # Test error handler
        error_handler = ErrorHandler(console)
        print("✓ Error handler instantiated")

        return True
    except Exception as e:
        print(f"✗ Instantiation error: {e}")
        return False

def test_warning_suppression():
    """Test warning suppression setup."""
    print("\nTesting warning suppression...")

    try:
        setup_warning_suppression()
        print("✓ Warning suppression setup completed")
        return True
    except Exception as e:
        print(f"✗ Warning suppression error: {e}")
        return False

def test_state_transitions():
    """Test state management transitions."""
    print("\nTesting state transitions...")

    try:
        state_manager = StateManager()
        state = state_manager.get_state()

        # Test initial state
        assert state.turn_count == 0
        assert state.max_turns == float("inf")
        print("✓ Initial state correct")

        # Test turn increment
        state_manager.increment_turn()
        assert state.turn_count == 1
        print("✓ Turn increment works")

        # Test state reset
        state_manager.reset_session_state()
        assert state.turn_count == 0
        print("✓ State reset works")

        return True
    except Exception as e:
        print(f"✗ State transition error: {e}")
        return False

def run_tests():
    """Run all tests."""
    print("Running CAI CLI Refactoring Tests")
    print("=" * 40)

    tests = [
        test_module_imports,
        test_module_instantiation,
        test_warning_suppression,
        test_state_transitions,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")

    print("\n" + "=" * 40)
    print(f"Tests completed: {passed}/{total} passed")

    if passed == total:
        print("🎉 All tests passed! Refactoring appears successful.")
        return True
    else:
        print("❌ Some tests failed. Please review the refactoring.")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)