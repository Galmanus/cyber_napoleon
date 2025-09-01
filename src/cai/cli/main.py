"""
Refactored CAI CLI Main Entry Point

Uses modular architecture for better maintainability and separation of concerns.
"""

import os
import asyncio
import time
from typing import Optional

# Import the modular components
from .session_manager import SessionManager
from .command_processor import CommandProcessor
from .agent_runner import AgentRunner
from .parallel_executor import ParallelExecutor
from .ui_manager import UIManager
from .error_handler import ErrorHandler
from .state_manager import StateManager
from .warning_suppressor import setup_warning_suppression

# Import CAI components
from cai.agents import get_agent_by_name
from cai.repl.commands import FuzzyCommandCompleter
from cai.repl.ui.logging import setup_session_logging
from cai.sdk.agents.run_to_jsonl import get_session_recorder
from cai.util import (
    start_active_timer,
    stop_active_timer,
    start_idle_timer,
    stop_idle_timer,
    validate_and_warn
)
from cai import is_pentestperf_available
from cai.util import setup_ctf


async def run_cai_cli_refactored(
    starting_agent,
    context_variables=None,
    max_turns=float("inf"),
    force_until_flag=False,
    initial_prompt: Optional[str] = None,
    prompt_file: Optional[str] = None,
):
    """
    Run the refactored CAI CLI with modular architecture.

    Args:
        starting_agent: The initial agent to use for the conversation
        context_variables: Optional dictionary of context variables to initialize the session
        max_turns: Maximum number of interaction turns before terminating (default: infinity)
        initial_prompt: A single prompt to run non-interactively.
        prompt_file: A file with prompts to run non-interactively, one per line.

    Returns:
        None
    """
    # Initialize all managers
    session_manager = SessionManager()
    state_manager = StateManager()
    ui_manager = UIManager(console=None)  # Will be set after console creation
    command_processor = CommandProcessor(console=None)  # Will be set after console creation
    agent_runner = AgentRunner(console=None)  # Will be set after console creation
    parallel_executor = ParallelExecutor(console=None)  # Will be set after console creation
    error_handler = ErrorHandler(console=None)  # Will be set after console creation

    # Create console and update managers
    from rich.console import Console
    console = Console()
    ui_manager.console = console
    command_processor.console = console
    agent_runner.console = console
    parallel_executor.console = console
    error_handler.console = console

    # Setup graceful shutdown
    error_handler.setup_graceful_shutdown()

    # Initialize session
    session = session_manager.create_session()
    state_manager.reset_session_state()

    # Setup session logging
    history_file = setup_session_logging()
    if session.session_logger is None:
        session.session_logger = get_session_recorder()

    # Display initial interface
    ui_manager.display_initial_interface()

    # Handle non-interactive mode
    if initial_prompt or prompt_file:
        await _handle_non_interactive_mode(
            initial_prompt, prompt_file, starting_agent,
            session_manager, ui_manager, error_handler
        )
        return

    # Initialize command completer and key bindings
    command_completer = FuzzyCommandCompleter()
    state_manager.get_state().current_text = [""]

    # Main interactive loop
    try:
        while True:
            # Update state from environment
            state_manager.update_state_from_env()

            # Check turn limits
            if state_manager.check_and_handle_limits():
                ui_manager.display_turn_limit_warning()
                continue

            # Handle CTF input if needed
            if state_manager.should_use_ctf_input():
                user_input = state_manager.get_ctf_input()
            else:
                # Get user input
                user_input = await ui_manager.get_user_input_with_interface(
                    command_completer, state_manager.get_state().current_text, history_file
                )

            # Handle empty input
            if not user_input.strip():
                user_input = "User input is empty, maybe wants to continue"

            # Start timing
            stop_idle_timer()
            start_active_timer()

            try:
                # Process commands
                if command_processor.process_command(user_input):
                    continue

                # Check if parallel execution is configured
                if await parallel_executor.execute_parallel_if_configured(
                    state_manager.get_state().current_agent, user_input
                ):
                    continue

                # Run agent conversation
                await agent_runner.run_agent_conversation(
                    state_manager.get_state().current_agent,
                    user_input,
                    state_manager.get_state().parallel_count
                )

                # Increment turn counter
                state_manager.increment_turn()

            except KeyboardInterrupt:
                await error_handler.handle_keyboard_interrupt(state_manager.get_state().current_agent)
                break
            except Exception as e:
                error_handler.handle_agent_execution_error(e)
            finally:
                # Stop timing
                stop_active_timer()
                start_idle_timer()

    except KeyboardInterrupt:
        pass
    except Exception as e:
        error_handler.handle_main_loop_error(e)
    finally:
        # Handle session end
        session_manager.handle_session_end(session)


async def _handle_non_interactive_mode(
    initial_prompt, prompt_file, agent,
    session_manager, ui_manager, error_handler
):
    """Handle non-interactive mode execution."""
    prompts = []
    if initial_prompt:
        prompts.append(initial_prompt)
    if prompt_file:
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompts.extend([line.strip() for line in f if line.strip()])
        except FileNotFoundError:
            ui_manager.display_error_message(f"Error: Prompt file not found: {prompt_file}")
            return

    # Run non-interactive session
    stop_idle_timer()
    start_active_timer()

    for i, prompt in enumerate(prompts):
        ui_manager.display_non_interactive_prompt(prompt, i + 1, len(prompts))

        # Log user message - skip for now due to session_manager structure

        # Build conversation context
        history_context = []
        if hasattr(agent, 'model') and hasattr(agent.model, 'message_history'):
            history_context.extend(agent.model.message_history)
        history_context.append({"role": "user", "content": prompt})

        # Run agent
        from cai.sdk.agents import Runner
        await Runner.run(agent, history_context)

        ui_manager.display_completion_separator()

    stop_active_timer()

    # Handle session end - create a temporary session object
    temp_session = session_manager.create_session()
    session_manager.handle_session_end(temp_session)


async def main_async_refactored():
    """Main async function for the refactored CAI CLI."""
    # Validate configuration first
    config_valid, validated_config = validate_and_warn()
    if not config_valid:
        from cai.util import color
        print(color("Configuration errors found. Please check your environment variables.", fg="red"))
        return

    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Cybersecurity AI (CAI) Framework CLI.")
    parser.add_argument("--prompt", type=str, help="Run with a single prompt and exit (non-interactive mode).")
    parser.add_argument("--file", type=str, help="Run with a series of prompts from a file and exit (non-interactive mode).")

    cli_args = parser.parse_args()

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

    # Run the CLI
    await run_cai_cli_refactored(
        agent,
        initial_prompt=cli_args.prompt,
        prompt_file=cli_args.file
    )


def main_refactored():
    """Main entry point for the refactored CAI CLI."""
    # Create a new event loop and set it as the current one
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Run the main async function
        loop.run_until_complete(main_async_refactored())
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\n[yellow]CLI interrupted by user[/yellow]")
    except Exception as e:
        print(f"Error during CLI execution: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up: cancel all pending tasks more aggressively
        try:
            # Get all tasks and cancel them immediately without waiting
            pending = asyncio.all_tasks(loop)
            if pending:
                for task in pending:
                    try:
                        task.cancel()
                    except Exception:
                        pass  # Ignore cancellation errors
                
                # Try to gather cancelled tasks but with timeout
                try:
                    loop.run_until_complete(
                        asyncio.wait_for(
                            asyncio.gather(*pending, return_exceptions=True),
                            timeout=1.0
                        )
                    )
                except (asyncio.TimeoutError, Exception):
                    # If timeout or any other error, just proceed to close
                    pass
                
        except Exception as cleanup_error:
            # Ignore cleanup errors, just proceed
            pass
        finally:
            # Force close the loop
            try:
                loop.close()
            except Exception:
                pass


if __name__ == "__main__":
    main_refactored()