"""
Error Handling Module for CAI CLI

Centralizes error handling, cleanup, and recovery logic.
"""

import os
import asyncio
import time
from typing import Any, Optional
from rich.console import Console

from cai.util import fix_message_list


class ErrorHandler:
    """Handles errors and cleanup operations for the CLI."""

    def __init__(self, console: Console):
        """Initialize the error handler.

        Args:
            console: Rich console for output
        """
        self.console = console

    async def handle_keyboard_interrupt(self, agent: Any) -> None:
        """Handle keyboard interrupt (Ctrl+C).

        Args:
            agent: The current agent
        """
        # Clean up any active streaming panels
        try:
            from cai.util import cleanup_all_streaming_resources
            cleanup_all_streaming_resources()
        except Exception:
            pass

        # Handle pending tool calls
        await self._handle_pending_tool_calls(agent)

        # Add a small delay to allow the system to settle
        time.sleep(0.1)

        # Clear any asyncio event loop state
        await self._cleanup_event_loop()

    async def _handle_pending_tool_calls(self, agent: Any) -> None:
        """Handle any pending tool calls before shutdown.

        Args:
            agent: The current agent
        """
        try:
            # Look for orphaned tool calls in the message history
            orphaned_tool_calls = []
            for msg in agent.model.message_history:
                if msg.get("role") == "assistant" and msg.get("tool_calls"):
                    for tool_call in msg["tool_calls"]:
                        call_id = tool_call.get("id")
                        if call_id:
                            # Check if this tool call has a corresponding tool result
                            has_result = any(
                                m.get("role") == "tool" and m.get("tool_call_id") == call_id
                                for m in agent.model.message_history
                            )
                            if not has_result:
                                orphaned_tool_calls.append((call_id, tool_call))

            # Add synthetic tool results for orphaned tool calls
            if orphaned_tool_calls:
                for call_id, tool_call in orphaned_tool_calls:
                    tool_response_msg = {
                        "role": "tool",
                        "tool_call_id": call_id,
                        "content": "Tool execution interrupted"
                    }
                    agent.model.add_to_message_history(tool_response_msg)

                # Apply message list fixes to ensure consistency
                agent.model.message_history[:] = fix_message_list(agent.model.message_history)

        except Exception:
            pass

    async def _cleanup_event_loop(self) -> None:
        """Clean up asyncio event loop state."""
        try:
            # Get the current event loop if it exists
            loop = asyncio.get_event_loop()
            if loop and loop.is_running():
                # Can't close a running loop, but we can clear pending tasks
                pending = asyncio.all_tasks(loop) if hasattr(asyncio, 'all_tasks') else asyncio.Task.all_tasks(loop)
                for task in pending:
                    if not task.done():
                        task.cancel()
        except Exception:
            pass

        # Reset the event loop policy
        try:
            asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
        except Exception:
            pass

    def handle_agent_execution_error(self, error: Exception) -> None:
        """Handle agent execution errors.

        Args:
            error: The exception that occurred
        """
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"An error occurred during agent execution: {str(error)}", exc_info=True)

        if os.getenv("CAI_DEBUG", "1") == "2":
            import traceback
            self.console.print(f"[red]Traceback:\n{traceback.format_exc()}[/red]")

    def handle_main_loop_error(self, error: Exception) -> None:
        """Handle main loop errors.

        Args:
            error: The exception that occurred
        """
        import sys
        import traceback

        # Only show detailed errors in debug mode
        if os.getenv("CAI_DEBUG", "1") == "2":
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb_info = traceback.extract_tb(exc_traceback)
            filename, line, func, text = tb_info[-1]
            self.console.print(f"[bold red]Error: {str(error)}[/bold red]")
            self.console.print(f"[bold red]Traceback: {tb_info}[/bold red]")
        else:
            # In normal mode, just log the error
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in main loop: {str(error)}", exc_info=True)

    async def graceful_shutdown(self) -> None:
        """Perform graceful shutdown of async resources."""
        try:
            # Get the current event loop
            loop = asyncio.get_event_loop()
            if loop and not loop.is_closed():
                # Cancel all pending tasks
                pending = asyncio.all_tasks(loop) if hasattr(asyncio, 'all_tasks') else asyncio.Task.all_tasks(loop)
                for task in pending:
                    if not task.done():
                        task.cancel()

                # Wait a bit for tasks to cancel gracefully
                if pending:
                    try:
                        await asyncio.wait_for(
                            asyncio.gather(*pending, return_exceptions=True),
                            timeout=1.0
                        )
                    except (asyncio.TimeoutError, asyncio.CancelledError):
                        pass

                # Close any remaining transports and connections
                try:
                    # Give time for subprocess transports to clean up
                    await asyncio.sleep(0.1)
                except:
                    pass

        except Exception:
            # Ignore errors during shutdown
            pass

    def setup_graceful_shutdown(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        import signal
        import atexit

        def signal_handler(signum, frame):
            try:
                loop = asyncio.get_event_loop()
                if loop and not loop.is_closed():
                    loop.create_task(self.graceful_shutdown())
            except:
                pass
            # Let the normal KeyboardInterrupt handling take over
            raise KeyboardInterrupt()

        def exit_handler():
            try:
                loop = asyncio.get_event_loop()
                if loop and not loop.is_closed() and not loop.is_running():
                    loop.run_until_complete(self.graceful_shutdown())
            except:
                pass

        # Register handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        atexit.register(exit_handler)

    def handle_streaming_error(self, agent: Any, error: Exception) -> None:
        """Handle streaming-related errors.

        Args:
            agent: The agent that encountered the error
            error: The exception that occurred
        """
        self.console.print("\n[yellow]Interrupted by user. Cleaning up...[/yellow]")

        # The error handling is already done in the streaming context
        # Just ensure we don't propagate the error further
        pass

    def validate_agent_state(self, agent: Any) -> bool:
        """Validate agent state before operations.

        Args:
            agent: The agent to validate

        Returns:
            bool: True if agent is in valid state
        """
        if not agent:
            self.console.print("[red]Error: No active agent available[/red]")
            return False

        if not hasattr(agent, 'model'):
            self.console.print("[red]Error: Agent has no model configured[/red]")
            return False

        return True

    def handle_configuration_error(self, message: str) -> None:
        """Handle configuration-related errors.

        Args:
            message: Error message
        """
        from cai.util import color
        print(color(f"Configuration errors found. Please check your environment variables: {message}", fg="red"))

    def log_error_with_context(self, error: Exception, context: str = "") -> None:
        """Log error with additional context.

        Args:
            error: The exception that occurred
            context: Additional context information
        """
        import logging
        logger = logging.getLogger(__name__)

        error_message = str(error)
        if context:
            error_message = f"{context}: {error_message}"

        logger.error(error_message, exc_info=True)

        # Only show to user in debug mode
        if os.getenv("CAI_DEBUG", "1") == "2":
            self.console.print(f"[red]Error: {error_message}[/red]")