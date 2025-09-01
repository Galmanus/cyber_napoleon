"""
Session Management Module for CAI CLI

Handles session lifecycle, timing, metrics, and cleanup operations.
"""

import os
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.console import Group

from cai.internal.components.metrics import process_metrics
from cai.sdk.agents.run_to_jsonl import get_session_recorder
from cai.sdk.agents.global_usage_tracker import GLOBAL_USAGE_TRACKER
from cai.util import COST_TRACKER, get_active_time_seconds, get_idle_time_seconds


@dataclass
class TimingStats:
    """Tracks timing statistics for a session."""
    active_time: float = 0.0
    idle_time: float = 0.0
    session_start: float = field(default_factory=time.time)

    def format_time(self, seconds: float) -> str:
        """Format seconds into HH:MM:SS format."""
        mins, secs = divmod(int(seconds), 60)
        hours, mins = divmod(mins, 60)
        return f"{hours:02d}:{mins:02d}:{secs:02d}"

    def get_session_time(self) -> str:
        """Get formatted session time."""
        return self.format_time(time.time() - self.session_start)

    def get_active_time_formatted(self) -> str:
        """Get formatted active time."""
        return self.format_time(self.active_time)

    def get_idle_time_formatted(self) -> str:
        """Get formatted idle time."""
        return self.format_time(self.idle_time)

    def get_llm_percentage(self) -> float:
        """Calculate percentage of time spent on LLM operations."""
        total_time = time.time() - self.session_start
        if total_time > 0:
            return round((self.active_time / total_time) * 100, 1)
        return 0.0


@dataclass
class CLISession:
    """Represents a CLI session with all its state."""
    message_histories: Dict[str, List] = field(default_factory=dict)
    ctf_context: Optional[Any] = None
    timing_stats: TimingStats = field(default_factory=TimingStats)
    agent_manager: Optional[Any] = None
    session_logger: Optional[Any] = None
    console: Console = field(default_factory=Console)

    def __post_init__(self):
        """Initialize session components."""
        if self.session_logger is None:
            self.session_logger = get_session_recorder()


class SessionManager:
    """Manages CLI session lifecycle and operations."""

    @staticmethod
    def create_session() -> CLISession:
        """Create a new CLI session."""
        return CLISession()

    @staticmethod
    def handle_session_end(session: CLISession) -> None:
        """
        Handle session end logic including metrics and cleanup.

        Args:
            session: The CLI session to end
        """
        session.timing_stats.active_time = get_active_time_seconds()
        session.timing_stats.idle_time = get_idle_time_seconds()

        metrics = {
            "session_time": session.timing_stats.get_session_time(),
            "active_time": session.timing_stats.get_active_time_formatted(),
            "idle_time": session.timing_stats.get_idle_time_formatted(),
            "llm_percentage": session.timing_stats.get_llm_percentage(),
            "session_cost": f"${COST_TRACKER.session_total_cost:.6f}",
        }

        content = [
            f"Session Time: {metrics['session_time']}",
            f"Active Time: {metrics['active_time']} ({metrics['llm_percentage']}%) ",
            f"Idle Time: {metrics['idle_time']}",
            f"Total Session Cost: {metrics['session_cost']}",
        ]

        if hasattr(session.session_logger, "filename") and session.session_logger.filename:
            content.append(f"Log available at: {session.session_logger.filename}")

        panel = Panel(
            Group(*[Text(line) for line in content]),
            title="[bold]Session Summary[/bold]",
            border_style="blue"
        )
        session.console.print(panel)

        # Process telemetry if enabled
        telemetry_enabled = os.getenv("CAI_TELEMETRY", "true").lower() != "false"
        if (telemetry_enabled and
            hasattr(session.session_logger, "session_id") and
            hasattr(session.session_logger, "filename")):
            process_metrics(session.session_logger.filename, sid=session.session_logger.session_id)

        # Log session end
        if session.session_logger:
            session.session_logger.log_session_end()

        # End global usage tracking session
        GLOBAL_USAGE_TRACKER.end_session(final_cost=COST_TRACKER.session_total_cost)

        # Create symlink to the last log file
        if hasattr(session.session_logger, "filename"):
            SessionManager._create_last_log_symlink(session.session_logger.filename)

        os.environ["CAI_COST_DISPLAYED"] = "true"

    @staticmethod
    def _create_last_log_symlink(log_filename: str) -> None:
        """
        Create a symbolic link 'logs/last' pointing to the current log file.

        Args:
            log_filename: Path to the current log file
        """
        try:
            from pathlib import Path

            if not log_filename:
                return

            log_path = Path(log_filename)
            if not log_path.exists():
                return

            # Create the symlink path
            symlink_path = Path("logs/last")

            # Remove existing symlink if it exists
            if symlink_path.exists() or symlink_path.is_symlink():
                symlink_path.unlink()

            # Create new symlink pointing to just the filename (relative path within logs dir)
            symlink_path.symlink_to(log_path.name)

        except Exception:
            # Silently ignore errors to avoid disrupting the main flow
            pass

    @staticmethod
    def reset_cost_tracking() -> None:
        """Reset cost tracking for a new session."""
        from cai.util import COST_TRACKER
        COST_TRACKER.reset_agent_costs()

    @staticmethod
    def reset_agent_manager() -> None:
        """Reset the agent manager for clean start."""
        from cai.sdk.agents.simple_agent_manager import AGENT_MANAGER
        AGENT_MANAGER.reset_registry()

    @staticmethod
    def register_starting_agent(agent: Any, agent_name: str) -> None:
        """Register the starting agent with the session."""
        from cai.sdk.agents.simple_agent_manager import AGENT_MANAGER
        AGENT_MANAGER.switch_to_single_agent(agent, agent_name)