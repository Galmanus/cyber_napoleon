"""
Warning Suppression Module for CAI CLI

Centralizes warning filtering and suppression logic.
"""

import os
import logging
import warnings
import sys


class WarningSuppressor:
    """Handles warning suppression and filtering for the CLI."""

    # Patterns to suppress completely
    SUPPRESS_PATTERNS = [
        "asynchronous generator",
        "asyncgen",
        "closedresourceerror",
        "didn't stop after athrow",
        "didnt stop after athrow",
        "didn't stop after athrow",
        "generator didn't stop",
        "generator didn't stop",
        "cancel scope",
        "unhandled errors in a taskgroup",
        "error in post_writer",
        "was never awaited",
        "connection error while setting up",
        "error closing",
        "anyio._backends",
        "httpx_sse",
        "connection reset by peer",
        "broken pipe",
        "connection aborted",
        "runtime warning",
        "runtimewarning",
        "coroutine",
        "task was destroyed",
        "event loop is closed",
        "session is closed",
        # Add specific aiohttp session warnings
        "unclosed client session",
        "unclosed connector",
        "client_session:",
        "connector:",
        "connections:",
        # Suppress LiteLLM worker cancellation noise during shutdown
        "loggingworker cancelled",
        "loggingworker canceled",
    ]

    # Loggers to configure
    LOGGERS_TO_CONFIGURE = [
        "openai.agents",
        "mcp.client.sse",
        "httpx",
        "httpx_sse",
        "mcp",
        "asyncio",
        "anyio",
        "anyio._backends._asyncio",
        "cai.sdk.agents",
        "aiohttp",  # Add aiohttp logger to suppress session warnings
        "litellm",  # Suppress LiteLLM logs (common logger name)
        "LiteLLM",  # Some environments use capitalized logger name
    ]

    @staticmethod
    def setup_warning_suppression() -> None:
        """Setup comprehensive warning suppression."""
        # Configure Python warnings
        WarningSuppressor._configure_python_warnings()

        # Configure logging filters
        WarningSuppressor._configure_logging_filters()

        # Setup aiohttp warning suppression
        WarningSuppressor._suppress_aiohttp_warnings()

    @staticmethod
    def _configure_python_warnings() -> None:
        """Configure Python warning system."""
        # Custom warning handler to suppress specific warnings
        def custom_warning_handler(message, category, filename, lineno, file=None, line=None):
            # Only show warnings in debug mode
            if os.getenv("CAI_DEBUG", "1") == "2":
                # Format and print the warning
                warnings.showwarning(message, category, filename, lineno, file, line)
            # Otherwise, silently ignore

        # Set custom warning handler
        warnings.showwarning = custom_warning_handler

        # Suppress ALL warnings in production mode (unless CAI_DEBUG=2)
        if os.getenv("CAI_DEBUG", "1") != "2":
            warnings.filterwarnings("ignore")
            # Also set environment variable to prevent warnings from subprocesses
            os.environ["PYTHONWARNINGS"] = "ignore"

        # Suppress various warnings globally with more comprehensive patterns
        warnings.filterwarnings("ignore", category=RuntimeWarning)  # Ignore ALL RuntimeWarnings
        warnings.filterwarnings("ignore", category=ResourceWarning)  # Ignore ResourceWarnings (aiohttp sessions)

        # Suppress specific message patterns
        for pattern in WarningSuppressor.SUPPRESS_PATTERNS:
            warnings.filterwarnings("ignore", message=f".*{pattern}.*")

        # Also configure Python's warning system to be less verbose
        if not sys.warnoptions:
            warnings.simplefilter("ignore", RuntimeWarning)
            warnings.simplefilter("ignore", ResourceWarning)  # Also ignore ResourceWarnings

    @staticmethod
    def _configure_logging_filters() -> None:
        """Configure logging filters for various loggers."""
        # Create comprehensive error filter
        comprehensive_filter = ComprehensiveErrorFilter()

        # Apply comprehensive filter to all relevant loggers
        for logger_name in WarningSuppressor.LOGGERS_TO_CONFIGURE:
            logger = logging.getLogger(logger_name)
            logger.addFilter(comprehensive_filter)
            # Set appropriate level - ERROR for most, WARNING for critical ones
            if logger_name in ["asyncio", "anyio", "anyio._backends._asyncio"]:
                logger.setLevel(logging.ERROR)  # Only show critical errors
            else:
                logger.setLevel(logging.WARNING)

    @staticmethod
    def _suppress_aiohttp_warnings() -> None:
        """Suppress aiohttp specific warnings about unclosed sessions."""
        try:
            import aiohttp
            # Suppress aiohttp warnings about unclosed sessions
            aiohttp_logger = logging.getLogger("aiohttp")
            aiohttp_logger.setLevel(logging.ERROR)  # Only show errors, not warnings

            # Also suppress aiohttp.client warnings
            aiohttp_client_logger = logging.getLogger("aiohttp.client")
            aiohttp_client_logger.setLevel(logging.ERROR)

            # Suppress aiohttp.connector warnings
            aiohttp_connector_logger = logging.getLogger("aiohttp.connector")
            aiohttp_connector_logger.setLevel(logging.ERROR)

        except ImportError:
            # aiohttp not installed, skip
            pass


class ComprehensiveErrorFilter(logging.Filter):
    """Filter to suppress various expected errors and warnings."""

    def filter(self, record):
        msg = record.getMessage().lower()

        # Check if any suppress pattern matches
        for pattern in WarningSuppressor.SUPPRESS_PATTERNS:
            if pattern in msg:
                return False

        # SSE connection errors during cleanup
        if "sse" in msg and any(word in msg for word in ["cleanup", "closing", "shutdown", "closed"]):
            return False

        # MCP connection errors that we handle
        if "error invoking mcp tool" in msg and "closedresourceerror" in msg:
            return False

        # MCP reconnection messages - change to DEBUG level
        if "mcp server session not found" in msg or "successfully reconnected to mcp server" in msg:
            record.levelno = logging.DEBUG
            record.levelname = "DEBUG"
            return True

        return True


def setup_warning_suppression():
    """Convenience function to setup warning suppression."""
    WarningSuppressor.setup_warning_suppression()


def suppress_aiohttp_warnings():
    """Convenience function to suppress aiohttp warnings."""
    WarningSuppressor._suppress_aiohttp_warnings()