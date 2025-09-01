"""
State Management Module for CAI CLI

Manages CLI state variables and transitions.
"""

import os
from typing import Any, Optional
from dataclasses import dataclass, field


@dataclass
class CLIState:
    """Represents the current state of the CLI."""

    # Agent state
    current_agent: Optional[Any] = None
    last_agent_type: str = "one_tool_agent"
    last_model: str = "alias0"

    # Turn and limit state
    turn_count: int = 0
    max_turns: float = float("inf")
    prev_max_turns: float = float("inf")
    turn_limit_reached: bool = False

    # Parallel execution state
    parallel_count: int = 1

    # CTF state
    ctf_global: Optional[Any] = None
    messages_ctf: str = ""
    ctf_init: int = 1
    previous_ctf_name: Optional[str] = None

    # Timing state
    idle_time: float = 0.0

    # Command state
    current_text: list = field(default_factory=lambda: [""])

    def __post_init__(self):
        """Initialize state with environment defaults."""
        self.last_model = os.getenv("CAI_MODEL", "alias0")
        self.last_agent_type = os.getenv("CAI_AGENT_TYPE", "one_tool_agent")
        self.parallel_count = int(os.getenv("CAI_PARALLEL", "1"))
        self.previous_ctf_name = os.getenv("CTF_NAME", None)

    def update_from_environment(self) -> None:
        """Update state from current environment variables."""
        # Update model if changed
        current_model = os.getenv("CAI_MODEL", "alias0")
        if current_model != self.last_model:
            self.last_model = current_model

        # Update agent type if changed
        current_agent_type = os.getenv("CAI_AGENT_TYPE", "one_tool_agent")
        if current_agent_type != self.last_agent_type:
            self.last_agent_type = current_agent_type

        # Update parallel count
        self.parallel_count = int(os.getenv("CAI_PARALLEL", "1"))

        # Update max turns
        current_max_turns = os.getenv("CAI_MAX_TURNS", "inf")
        if current_max_turns != str(self.prev_max_turns):
            self.max_turns = float(current_max_turns)
            self.prev_max_turns = self.max_turns

            if self.turn_limit_reached and self.turn_count < self.max_turns:
                self.turn_limit_reached = False

    def check_turn_limits(self) -> bool:
        """Check if turn limits are reached.

        Returns:
            bool: True if limits are reached
        """
        if self.turn_count >= self.max_turns and self.max_turns != float("inf"):
            if not self.turn_limit_reached:
                self.turn_limit_reached = True
            return True
        return False

    def increment_turn(self) -> None:
        """Increment the turn counter."""
        self.turn_count += 1

    def reset_turn_limit(self) -> None:
        """Reset turn limit flag when limit is increased."""
        if self.turn_limit_reached and self.turn_count < self.max_turns:
            self.turn_limit_reached = False

    def update_ctf_state(self, ctf: Any, messages: str) -> None:
        """Update CTF state.

        Args:
            ctf: CTF instance
            messages: CTF messages
        """
        self.ctf_global = ctf
        self.messages_ctf = messages
        self.ctf_init = 0
        self.previous_ctf_name = os.getenv("CTF_NAME", None)

    def should_use_ctf_input(self) -> bool:
        """Check if CTF input should be used.

        Returns:
            bool: True if CTF input should be used
        """
        return not self.ctf_init and self.messages_ctf

    def get_ctf_input(self) -> str:
        """Get CTF input and mark as used.

        Returns:
            str: CTF input message
        """
        self.ctf_init = 1
        return self.messages_ctf

    def update_agent_model(self, new_model: str) -> None:
        """Update the current agent's model.

        Args:
            new_model: New model string
        """
        if self.current_agent and hasattr(self.current_agent, "model"):
            # Update recursively for agent and handoffs
            self._update_agent_models_recursively(self.current_agent, new_model)
            self.last_model = new_model

    def _update_agent_models_recursively(self, agent: Any, new_model: str, visited: Optional[set] = None) -> None:
        """Recursively update the model for an agent and all agents in its handoffs.

        Args:
            agent: The agent to update
            new_model: The new model string to set
            visited: Set of agent names already visited to prevent infinite loops
        """
        if visited is None:
            visited = set()

        # Avoid infinite loops by tracking visited agents
        if hasattr(agent, 'name') and agent.name in visited:
            return
        if hasattr(agent, 'name'):
            visited.add(agent.name)

        # Update the main agent's model
        if hasattr(agent, "model") and hasattr(agent.model, "model"):
            agent.model.model = new_model
            # Also ensure the agent name is set correctly in the model
            if hasattr(agent.model, "agent_name"):
                agent.model.agent_name = agent.name

            # Clear any cached state in the model
            if hasattr(agent.model, "_client"):
                agent.model._client = None
            if hasattr(agent.model, "_converter"):
                if hasattr(agent.model._converter, "recent_tool_calls"):
                    agent.model._converter.recent_tool_calls.clear()
                if hasattr(agent.model._converter, "tool_outputs"):
                    agent.model._converter.tool_outputs.clear()

        # Update models for all handoff agents
        if hasattr(agent, "handoffs"):
            for handoff_item in agent.handoffs:
                if hasattr(handoff_item, "on_invoke_handoff"):
                    # This is a Handoff object
                    try:
                        if (hasattr(handoff_item.on_invoke_handoff, "__closure__") and
                            handoff_item.on_invoke_handoff.__closure__):
                            for cell in handoff_item.on_invoke_handoff.__closure__:
                                if hasattr(cell.cell_contents, "model") and hasattr(cell.cell_contents, "name"):
                                    handoff_agent = cell.cell_contents
                                    self._update_agent_models_recursively(handoff_agent, new_model, visited)
                                    break
                    except Exception:
                        pass
                elif hasattr(handoff_item, "model"):
                    # This is a direct Agent reference
                    self._update_agent_models_recursively(handoff_item, new_model, visited)

    def switch_agent(self, new_agent: Any, agent_type: str) -> None:
        """Switch to a new agent.

        Args:
            new_agent: The new agent instance
            agent_type: The agent type string
        """
        self.current_agent = new_agent
        self.last_agent_type = agent_type

        # Apply current model to the new agent
        if self.last_model:
            self.update_agent_model(self.last_model)

    def get_agent_short_name(self) -> str:
        """Get short name for the current agent.

        Returns:
            str: Agent short name
        """
        if hasattr(self.current_agent, "name"):
            return self.current_agent.name
        return "Agent"

    def is_parallel_mode(self) -> bool:
        """Check if parallel mode is enabled.

        Returns:
            bool: True if parallel mode
        """
        return self.parallel_count > 1

    def reset_for_new_session(self) -> None:
        """Reset state for a new session."""
        self.turn_count = 0
        self.idle_time = 0.0
        self.turn_limit_reached = False
        self.ctf_init = 1
        self.current_text = [""]


class StateManager:
    """Manages CLI state transitions and persistence."""

    def __init__(self):
        """Initialize the state manager."""
        self.state = CLIState()

    def get_state(self) -> CLIState:
        """Get the current CLI state.

        Returns:
            CLIState: Current state
        """
        return self.state

    def update_state_from_env(self) -> None:
        """Update state from environment variables."""
        self.state.update_from_environment()

    def check_and_handle_limits(self) -> bool:
        """Check turn limits and return if commands only are allowed.

        Returns:
            bool: True if only commands are allowed
        """
        return self.state.check_turn_limits()

    def increment_turn(self) -> None:
        """Increment turn counter."""
        self.state.increment_turn()

    def reset_session_state(self) -> None:
        """Reset state for new session."""
        self.state.reset_for_new_session()

    def update_ctf_context(self, ctf: Any, messages: str) -> None:
        """Update CTF context.

        Args:
            ctf: CTF instance
            messages: CTF messages
        """
        self.state.update_ctf_state(ctf, messages)

    def should_use_ctf_input(self) -> bool:
        """Check if CTF input should be used.

        Returns:
            bool: True if CTF input should be used
        """
        return self.state.should_use_ctf_input()

    def get_ctf_input(self) -> str:
        """Get CTF input.

        Returns:
            str: CTF input
        """
        return self.state.get_ctf_input()

    def switch_to_agent(self, agent: Any, agent_type: str) -> None:
        """Switch to a new agent.

        Args:
            agent: New agent instance
            agent_type: Agent type string
        """
        self.state.switch_agent(agent, agent_type)

    def update_model(self, new_model: str) -> None:
        """Update the model for current agent.

        Args:
            new_model: New model string
        """
        self.state.update_agent_model(new_model)