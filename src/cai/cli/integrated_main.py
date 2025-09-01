"""
Integrated CAI CLI with Continuous Learning

This version integrates the continuous learning system with the existing CAI CLI.
"""

import os
import asyncio
import time
from typing import Optional

# Import CAI components
from cai.agents import get_agent_by_name
from cai.repl.commands import FuzzyCommandCompleter
from cai.repl.ui.logging import setup_session_logging
from cai.util import (
    start_active_timer,
    stop_active_timer,
    start_idle_timer,
    stop_idle_timer,
    validate_and_warn
)
from cai import is_pentestperf_available
from cai.util import setup_ctf

# Import learning system
from .learning_config import setup_learning_environment, get_learning_config
from .learning_integration import (
    initialize_learning_integration,
    get_learning_integration,
    learning_hook_session_start,
    learning_hook_session_end
)
from .enhanced_agent_runner import EnhancedAgentRunner
from .warning_suppressor import setup_warning_suppression


async def run_cai_with_learning(
    starting_agent,
    context_variables=None,
    max_turns=float("inf"),
    force_until_flag=False,
    initial_prompt: Optional[str] = None,
    prompt_file: Optional[str] = None,
):
    """
    Run CAI with integrated continuous learning.

    Args:
        starting_agent: The initial agent to use for the conversation
        context_variables: Optional dictionary of context variables to initialize the session
        max_turns: Maximum number of interaction turns before terminating (default: infinity)
        initial_prompt: A single prompt to run non-interactively.
        prompt_file: A file with prompts to run non-interactively, one per line.

    Returns:
        None
    """
    # Initialize learning system
    print("🧠 Initializing continuous learning system...")

    # Setup learning environment
    learning_success = setup_learning_environment()
    if learning_success:
        print("✅ Learning environment configured")

        # Initialize learning integration
        await initialize_learning_integration()
        print("✅ Learning integration initialized")

        # Get learning manager
        learning_manager = get_learning_integration()
        print("✅ Learning manager ready")
    else:
        print("❌ Failed to setup learning environment")
        return

    # Start learning session
    session_id = f"cai_session_{int(time.time())}"
    learning_hook_session_start(session_id)
    print(f"📝 Started learning session: {session_id}")

    # Create enhanced agent runner with learning
    from rich.console import Console
    console = Console()
    enhanced_runner = EnhancedAgentRunner(console)
    enhanced_runner.enable_learning()

    # Apply learning to the agent
    agent_name = getattr(starting_agent, "name", "CAI Agent")
    await enhanced_runner.learning_manager.apply_learning_to_agent(starting_agent, "general cybersecurity assistance")

    print("🚀 Starting CAI with continuous learning enabled...")

    try:
        # Run with enhanced learning capabilities
        await enhanced_runner.run_agent_conversation(
            starting_agent,
            initial_prompt or "Hello, I'm ready to help with cybersecurity tasks.",
            context="general cybersecurity assistance"
        )

    except KeyboardInterrupt:
        print("\n👋 Session interrupted by user")

    except Exception as e:
        print(f"\n❌ Error during session: {e}")

    finally:
        # End learning session and analyze patterns
        print("\n🔍 Analyzing session patterns...")
        try:
            results = await learning_hook_session_end()

            if results and results.get('patterns_discovered', 0) > 0:
                print("🎯 Learning Results:")
                print(f"   • Patterns discovered: {results['patterns_discovered']}")
                print(f"   • Total patterns: {results['total_patterns']}")
                print(f"   • Average confidence: {results['average_confidence']:.2f}")

                if results.get('new_patterns'):
                    print("   • New patterns learned:")
                    for pattern in results['new_patterns'][:3]:
                        print(f"     - {pattern['type']}: {pattern['description'][:50]}...")

                print("\n💡 The system has learned from this session and will apply these insights to future interactions!")

            else:
                print("ℹ️  No new patterns discovered in this session")

        except Exception as e:
            print(f"⚠️  Error analyzing session: {e}")

        # Show learning statistics
        try:
            from .continuous_learning import get_learning_engine
            engine = get_learning_engine()
            stats = engine.get_learning_stats()

            print("\n📊 Learning System Statistics:")
            print(f"   • Total patterns: {stats['total_patterns']}")
            print(f"   • Active sessions: {stats['active_sessions']}")
            print(f"   • Pattern types: {len(stats['pattern_types'])}")

        except Exception as e:
            print(f"⚠️  Error getting statistics: {e}")


async def main_integrated():
    """Main integrated function with learning."""
    # Setup warning suppression
    setup_warning_suppression()

    # Validate configuration first
    config_valid, validated_config = validate_and_warn()
    if not config_valid:
        from cai.util import color
        print(color("Configuration errors found. Please check your environment variables.", fg="red"))
        return

    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Cybersecurity AI (CAI) with Continuous Learning")
    parser.add_argument("--prompt", type=str, help="Run with a single prompt and exit (non-interactive mode).")
    parser.add_argument("--file", type=str, help="Run with a series of prompts from a file and exit (non-interactive mode).")
    parser.add_argument("--no-learning", action="store_true", help="Disable continuous learning for this session.")

    cli_args = parser.parse_args()

    # Check if learning should be disabled
    if cli_args.no_learning:
        print("🔇 Continuous learning disabled for this session")
        # Fall back to original CAI
        from cai.cli.main import main_async_refactored
        await main_async_refactored()
        return

    # Get agent type from validated config
    agent_type = validated_config.get('agent_type', 'one_tool_agent')

    # Get the agent instance
    agent = get_agent_by_name(agent_type, agent_id="P1")

    # Configure agent model settings
    if hasattr(agent, "model"):
        if hasattr(agent.model, "disable_rich_streaming"):
            agent.model.disable_rich_streaming = True
        if hasattr(agent.model, "suppress_final_output"):
            agent.model.suppress_final_output = False

    # Update agent model recursively
    current_model = os.getenv("CAI_MODEL", "alias0")
    if hasattr(agent, "model"):
        # Import the update function
        from cai.cli.agent_runner import AgentRunner
        runner = AgentRunner(console=None)
        runner._update_agent_models_recursively(agent, current_model)

    # Run CAI with integrated learning
    await run_cai_with_learning(
        agent,
        initial_prompt=cli_args.prompt,
        prompt_file=cli_args.file
    )


def main_with_learning():
    """Main entry point with integrated learning."""
    try:
        asyncio.run(main_integrated())
    except KeyboardInterrupt:
        print("\n👋 CAI with continuous learning terminated")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()


# Convenience functions for easy access
def enable_learning():
    """Enable continuous learning globally."""
    config = get_learning_config()
    config.enable_learning()
    print("✅ Continuous learning enabled globally")


def disable_learning():
    """Disable continuous learning globally."""
    config = get_learning_config()
    config.disable_learning()
    print("🔇 Continuous learning disabled globally")


def get_learning_status():
    """Get current learning system status."""
    try:
        config = get_learning_config()
        learning_manager = get_learning_integration()
        engine = get_learning_engine()

        status = {
            "enabled": config.is_enabled(),
            "current_session": learning_manager.current_session_id,
            "total_patterns": len(engine.learning_patterns),
            "active_sessions": len(engine.active_sessions),
            "model": config.get_learning_model(),
            "confidence_threshold": config.get_min_confidence_threshold()
        }

        print("📊 Learning System Status:")
        print(f"   • Enabled: {status['enabled']}")
        print(f"   • Current session: {status['current_session'] or 'None'}")
        print(f"   • Total patterns: {status['total_patterns']}")
        print(f"   • Active sessions: {status['active_sessions']}")
        print(f"   • Model: {status['model']}")
        print(f"   • Confidence threshold: {status['confidence_threshold']}")

        return status

    except Exception as e:
        print(f"❌ Error getting learning status: {e}")
        return None


if __name__ == "__main__":
    main_with_learning()