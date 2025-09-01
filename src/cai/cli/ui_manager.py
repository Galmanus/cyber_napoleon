"""
UI Management Module for CAI CLI

Handles user interface elements including banners, prompts, and display management.
"""

import os
from typing import Optional, Any
from rich.console import Console
from rich.text import Text

from cai.repl.ui.banner import display_banner, display_quick_guide
from cai.repl.ui.keybindings import create_key_bindings
from cai.repl.ui.prompt import get_user_input
from cai.repl.ui.toolbar import get_toolbar_with_refresh


class UIManager:
    """Manages user interface elements and display."""

    def __init__(self, console: Console):
        """Initialize the UI manager.

        Args:
            console: Rich console for output
        """
        self.console = console

    def display_initial_interface(self) -> None:
        """Display the initial CLI interface with banner and guide."""
        display_banner(self.console)
        print("\n")
        display_quick_guide(self.console)

    def display_log_info(self, session_logger: Any) -> None:
        """Display log file information.

        Args:
            session_logger: The session logger instance
        """
        log_text = Text(
            f"Log file: {session_logger.filename}",
            style="yellow on black",
        )
        self.console.print(log_text)

    async def get_user_input_with_interface(
        self,
        command_completer: Any,
        current_text: list,
        history_file: Optional[str] = None
    ) -> str:
        """Get user input with full interface support.

        Args:
            command_completer: The command completer instance
            current_text: Current text buffer
            history_file: Path to history file

        Returns:
            str: The user input
        """
        kb = create_key_bindings(current_text)
        toolbar = get_toolbar_with_refresh(current_text)

        user_input = await get_user_input(
            command_completer, kb, history_file, toolbar, current_text
        )

        return user_input

    def display_turn_limit_warning(self) -> None:
        """Display warning when turn limit is reached."""
        self.console.print(
            "[bold red]Error: Turn limit reached. Only CLI commands are allowed.[/bold red]"
        )
        self.console.print(
            "[yellow]Please use /config to increase CAI_MAX_TURNS limit.[/yellow]"
        )

    def display_turn_limit_increased(self) -> None:
        """Display message when turn limit is increased."""
        self.console.print(
            "[green]Turn limit increased. You can now continue using CAI.[/green]"
        )

    def display_interruption_message(self) -> None:
        """Display interruption message."""
        self.console.print("\n[yellow]Interrupted by user. Cleaning up...[/yellow]")

    def display_error_message(self, message: str, show_traceback: bool = False) -> None:
        """Display error message.

        Args:
            message: Error message to display
            show_traceback: Whether to show traceback
        """
        self.console.print(f"[red]{message}[/red]")

        if show_traceback and os.getenv("CAI_DEBUG", "1") == "2":
            import traceback
            self.console.print(f"[red]Traceback:\n{traceback.format_exc()}[/red]")

    def display_debug_error(self, error: Exception) -> None:
        """Display error with debug information.

        Args:
            error: The exception to display
        """
        if os.getenv("CAI_DEBUG", "1") == "2":
            import sys
            import traceback

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

    def display_non_interactive_prompt(self, prompt: str, index: int, total: int) -> None:
        """Display non-interactive prompt information.

        Args:
            prompt: The prompt being executed
            index: Current prompt index (1-based)
            total: Total number of prompts
        """
        from rich.panel import Panel
        panel = Panel(
            f"Running prompt {index}/{total}: [yellow]{prompt}[/yellow]",
            border_style="blue"
        )
        self.console.print(panel)

    def display_completion_separator(self) -> None:
        """Display completion separator."""
        from rich.rule import Rule
        self.console.print(Rule(style="green"))

    def create_status_spinner(self, message: str = "[bold green]Thinking..."):
        """Create a status spinner for long-running operations.

        Args:
            message: The status message

        Returns:
            Status context manager
        """
        return self.console.status(message, spinner="dots")

    def print_colored_message(self, message: str, color: str = "white") -> None:
        """Print a colored message.

        Args:
            message: Message to print
            color: Color name
        """
        colored_message = f"[{color}]{message}[/{color}]"
        self.console.print(colored_message)