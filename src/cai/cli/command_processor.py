"""
Command Processing Module for CAI CLI

Handles command parsing, validation, and execution for CLI commands.
"""

import os
from typing import List, Optional, Any
from rich.console import Console

from cai.repl.commands import handle_command as commands_handle_command


class CommandProcessor:
    """Processes CLI commands and manages command execution."""

    def __init__(self, console: Console):
        """Initialize the command processor.

        Args:
            console: Rich console for output
        """
        self.console = console

    def process_command(self, user_input: str) -> bool:
        """Process a command from user input.

        Args:
            user_input: The raw user input that may contain a command

        Returns:
            bool: True if command was processed, False if it should be treated as regular input
        """
        if not (user_input.startswith("/") or user_input.startswith("$")):
            return False

        parts = user_input.strip().split()
        command = parts[0]
        args = parts[1:] if len(parts) > 1 else None

        # Process the command with the handler
        if commands_handle_command(command, args):
            return True  # Command was handled

        # If command wasn't recognized, show error (skip for /shell or /s)
        if command not in ("/shell", "/s"):
            self.console.print(f"[red]Command failed or unknown: {command}[/red]")

        return True  # Command was attempted, even if failed

    def is_command(self, user_input: str) -> bool:
        """Check if the input is a command.

        Args:
            user_input: The user input to check

        Returns:
            bool: True if input is a command
        """
        return user_input.startswith("/") or user_input.startswith("$")

    def validate_command_input(self, user_input: str, turn_limit_reached: bool) -> tuple[bool, Optional[str]]:
        """Validate command input based on current state.

        Args:
            user_input: The user input to validate
            turn_limit_reached: Whether the turn limit has been reached

        Returns:
            tuple: (is_valid, error_message)
        """
        # Check if turn limit is reached and allow only CLI commands
        if (turn_limit_reached and
            not user_input.startswith("/") and
            not user_input.startswith("$")):

            error_msg = ("[bold red]Error: Turn limit reached. Only CLI commands are allowed.[/bold red]\n"
                        "[yellow]Please use /config to increase CAI_MAX_TURNS limit.[/yellow]")
            return False, error_msg

        return True, None

    def handle_turn_limit_error(self) -> None:
        """Handle the case when turn limit is reached."""
        self.console.print(
            "[bold red]Error: Turn limit reached. Only CLI commands are allowed.[/bold red]"
        )
        self.console.print(
            "[yellow]Please use /config to increase CAI_MAX_TURNS limit.[/yellow]"
        )