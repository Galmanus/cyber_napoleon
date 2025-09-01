"""
Parallel Execution Module for CAI CLI

Handles parallel agent execution and coordination.
"""

import os
import asyncio
from typing import List, Dict, Any, Tuple, Optional
from rich.console import Console

from cai.repl.commands.parallel import PARALLEL_CONFIGS, ParallelConfig, PARALLEL_AGENT_INSTANCES
from cai.sdk.agents import Runner


class ParallelExecutor:
    """Handles parallel execution of multiple agents."""

    def __init__(self, console: Console):
        """Initialize the parallel executor.

        Args:
            console: Rich console for output
        """
        self.console = console

    async def execute_parallel_if_configured(self, agent: Any, user_input: str) -> bool:
        """Execute parallel agents if configured.

        Args:
            agent: The main agent
            user_input: User input for the conversation

        Returns:
            bool: True if parallel execution was performed, False otherwise
        """
        if not PARALLEL_CONFIGS:
            return False

        # Show which agents have custom prompts
        agents_with_prompts = [(idx, config) for idx, config in enumerate(PARALLEL_CONFIGS, 1) if config.prompt]

        # Setup parallel isolation for these agents
        await self._setup_parallel_isolation(agent, len(PARALLEL_CONFIGS))

        # Create agent instances
        await self._create_parallel_instances()

        # Execute parallel agents
        await self._execute_parallel_agents(user_input)

        return True

    async def _setup_parallel_isolation(self, agent: Any, num_configs: int) -> None:
        """Setup parallel isolation for agents.

        Args:
            agent: The main agent
            num_configs: Number of parallel configurations
        """
        from cai.sdk.agents.parallel_isolation import PARALLEL_ISOLATION

        # Get agent IDs
        agent_ids = [config.id or f"P{idx}" for idx, config in enumerate(PARALLEL_CONFIGS, 1)]

        # Check if we already have isolated histories
        already_has_histories = await self._check_existing_histories(agent_ids)

        if not already_has_histories:
            # Get the current agent's history to transfer
            current_history = []
            if hasattr(agent, 'model') and hasattr(agent.model, 'message_history'):
                current_history = agent.model.message_history
            elif hasattr(agent, 'name'):
                from cai.sdk.agents.simple_agent_manager import AGENT_MANAGER
                current_history = AGENT_MANAGER.get_message_history(agent.name)

            # Check if we should transfer history to all agents
            transfer_to_all = self._should_transfer_to_all()

            if transfer_to_all:
                # Transfer to parallel mode - creates isolated copies for each agent
                PARALLEL_ISOLATION.transfer_to_parallel(current_history, num_configs, agent_ids)
            else:
                # Only transfer to the first agent (P1)
                PARALLEL_ISOLATION._parallel_mode = True
                if current_history and agent_ids:
                    # Clear any existing histories first
                    PARALLEL_ISOLATION.clear_all_histories()
                    # Set history only for the first agent
                    PARALLEL_ISOLATION.replace_isolated_history(agent_ids[0], current_history.copy())
                    # Initialize empty histories for other agents
                    for agent_id in agent_ids[1:]:
                        PARALLEL_ISOLATION.replace_isolated_history(agent_id, [])
        else:
            # Already have isolated histories, just ensure we're in parallel mode
            PARALLEL_ISOLATION._parallel_mode = True

    async def _check_existing_histories(self, agent_ids: List[str]) -> bool:
        """Check if isolated histories already exist.

        Args:
            agent_ids: List of agent IDs to check

        Returns:
            bool: True if histories exist
        """
        from cai.sdk.agents.parallel_isolation import PARALLEL_ISOLATION

        if PARALLEL_ISOLATION.is_parallel_mode():
            # Check if at least one agent has a non-empty isolated history
            for agent_id in agent_ids:
                isolated_history = PARALLEL_ISOLATION.get_isolated_history(agent_id)
                if isolated_history:
                    return True
        return False

    def _should_transfer_to_all(self) -> bool:
        """Determine if history should be transferred to all agents.

        Returns:
            bool: True if should transfer to all agents
        """
        # Check if this is a pattern that requires different contexts
        pattern_description = os.getenv("CAI_PATTERN_DESCRIPTION", "")
        if "different contexts" in pattern_description.lower():
            return False
        return True

    async def _create_parallel_instances(self) -> None:
        """Create parallel agent instances."""
        from cai.agents import get_available_agents

        for idx, config in enumerate(PARALLEL_CONFIGS, 1):
            instance_key = (config.agent_name, idx)
            if instance_key not in PARALLEL_AGENT_INSTANCES:
                # Create instance for this config
                base_agent = get_available_agents().get(config.agent_name.lower())
                if base_agent:
                    agent_display_name = getattr(base_agent, "name", config.agent_name)
                    custom_name = f"{agent_display_name} #{idx}"

                    # Determine model
                    model_to_use = config.model or os.getenv("CAI_MODEL", "alias0")

                    # Create and store the instance
                    from cai.agents import get_agent_by_name
                    instance_agent = get_agent_by_name(
                        config.agent_name, custom_name=custom_name, model_override=model_to_use,
                        agent_id=config.id
                    )
                    PARALLEL_AGENT_INSTANCES[instance_key] = instance_agent

    async def _execute_parallel_agents(self, user_input: str) -> None:
        """Execute all configured agents in parallel.

        Args:
            user_input: The user input for the conversation
        """
        async def run_agent_instance(config: ParallelConfig, input_text: str) -> Tuple[ParallelConfig, Any]:
            """Run a single agent instance with its own configuration."""
            instance_agent = None
            agent_id = None
            try:
                # Get instance number based on position in PARALLEL_CONFIGS
                instance_number = PARALLEL_CONFIGS.index(config) + 1
                agent_id = config.id or f"P{instance_number}"

                # Get the existing instance
                instance_key = (config.agent_name, instance_number)
                instance_agent = PARALLEL_AGENT_INSTANCES.get(instance_key)

                if not instance_agent:
                    # Fallback: create instance if not found
                    await self._create_fallback_instance(config, instance_number)
                    instance_agent = PARALLEL_AGENT_INSTANCES[instance_key]

                # Register the agent with AGENT_MANAGER for parallel mode
                from cai.sdk.agents.simple_agent_manager import AGENT_MANAGER
                agent_display_name = getattr(instance_agent, 'name', config.agent_name)
                AGENT_MANAGER.set_parallel_agent(agent_id, instance_agent, agent_display_name)

                # Ensure the model is properly set
                model_to_use = config.model or os.getenv("CAI_MODEL", "alias0")
                if model_to_use:
                    self._update_agent_models_recursively(instance_agent, model_to_use)

                # Use custom prompt if available
                instance_input = config.prompt if config.prompt else input_text

                # Run the agent
                result = await Runner.run(instance_agent, instance_input)

                # Clean up streaming resources
                await self._cleanup_streaming_resources(instance_agent, config)

                # Save the agent's history
                if instance_agent and agent_id:
                    await self._save_agent_history(instance_agent, agent_id)

                return (config, result)

            except asyncio.CancelledError:
                # Handle cancellation
                await self._handle_cancellation(instance_agent, agent_id)
                raise
            except Exception as e:
                # Handle other exceptions
                await self._handle_execution_error(config, instance_agent, agent_id, e)
                return (config, None)

        async def run_parallel_agents():
            """Run all configured agents in parallel."""
            # Create tasks for each agent
            tasks = []
            for config in PARALLEL_CONFIGS:
                input_for_config = config.prompt if config.prompt else user_input
                tasks.append(run_agent_instance(config, input_for_config))

            # Wait for all to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Filter out exceptions and failed results
            valid_results = []
            for item in results:
                if isinstance(item, tuple) and len(item) == 2 and item[1] is not None:
                    valid_results.append(item)

            return valid_results

        # Execute parallel agents
        try:
            with self.console.status("[bold green]Thinking...", spinner="dots") as status:
                results = await run_parallel_agents()
        except KeyboardInterrupt:
            # Handle interruption during parallel execution
            await self._handle_parallel_interruption()
            raise

    async def _create_fallback_instance(self, config: ParallelConfig, instance_number: int) -> None:
        """Create a fallback agent instance.

        Args:
            config: The parallel configuration
            instance_number: The instance number
        """
        from cai.agents import get_available_agents, get_pattern
        from cai.agents.patterns import get_pattern

        agent_display_name = None
        actual_agent_name = config.agent_name

        if config.agent_name.endswith("_pattern"):
            pattern = get_pattern(config.agent_name)
            if pattern and hasattr(pattern, 'entry_agent'):
                agent_display_name = getattr(pattern.entry_agent, "name", config.agent_name)
                actual_agent_name = config.agent_name
        else:
            base_agent = get_available_agents().get(config.agent_name.lower())
            agent_display_name = base_agent.name if base_agent else config.agent_name

        if not config.agent_name.endswith("_pattern"):
            custom_name = f"{agent_display_name} #{instance_number}"
        else:
            custom_name = agent_display_name

        model_to_use = config.model or os.getenv("CAI_MODEL", "alias0")

        from cai.agents import get_agent_by_name
        instance_agent = get_agent_by_name(
            actual_agent_name, custom_name=custom_name, model_override=model_to_use,
            agent_id=config.id
        )

        instance_key = (config.agent_name, instance_number)
        PARALLEL_AGENT_INSTANCES[instance_key] = instance_agent

    async def _cleanup_streaming_resources(self, instance_agent: Any, config: ParallelConfig) -> None:
        """Clean up streaming resources for an agent.

        Args:
            instance_agent: The agent instance
            config: The parallel configuration
        """
        try:
            from cai.util import finish_tool_streaming, cli_print_tool_output, _LIVE_STREAMING_PANELS

            if hasattr(cli_print_tool_output, "_streaming_sessions"):
                agent_display_name = getattr(instance_agent, 'name', config.agent_name)

                # Find sessions belonging to this agent
                for session_id, session_info in list(cli_print_tool_output._streaming_sessions.items()):
                    if (session_info.get("agent_name") == agent_display_name and
                        not session_info.get("is_complete", False)):
                        finish_tool_streaming(
                            tool_name=session_info.get("tool_name", "unknown"),
                            args=session_info.get("args", {}),
                            output=session_info.get("current_output", "Tool execution completed"),
                            call_id=session_id,
                            execution_info={"status": "completed", "is_final": True},
                            token_info={
                                "agent_name": agent_display_name,
                                "agent_id": getattr(instance_agent.model, "agent_id", None) if hasattr(instance_agent, 'model') else None
                            }
                        )
        except Exception:
            # Silently ignore cleanup errors
            pass

    async def _save_agent_history(self, instance_agent: Any, agent_id: str) -> None:
        """Save agent history after execution.

        Args:
            instance_agent: The agent instance
            agent_id: The agent ID
        """
        from cai.sdk.agents.parallel_isolation import PARALLEL_ISOLATION

        if hasattr(instance_agent, 'model') and hasattr(instance_agent.model, 'message_history'):
            PARALLEL_ISOLATION.replace_isolated_history(agent_id, instance_agent.model.message_history)

    async def _handle_cancellation(self, instance_agent: Any, agent_id: str) -> None:
        """Handle cancellation of agent execution.

        Args:
            instance_agent: The agent instance
            agent_id: The agent ID
        """
        try:
            from cai.util import cleanup_agent_streaming_resources

            if instance_agent:
                agent_display_name = getattr(instance_agent, 'name', instance_agent.__class__.__name__)
                cleanup_agent_streaming_resources(agent_display_name)
        except Exception:
            pass

        if instance_agent and agent_id:
            from cai.sdk.agents.parallel_isolation import PARALLEL_ISOLATION
            if hasattr(instance_agent, 'model') and hasattr(instance_agent.model, 'message_history'):
                PARALLEL_ISOLATION.replace_isolated_history(agent_id, instance_agent.model.message_history)

    async def _handle_execution_error(self, config: ParallelConfig, instance_agent: Any, agent_id: str, error: Exception) -> None:
        """Handle execution errors.

        Args:
            config: The parallel configuration
            instance_agent: The agent instance
            agent_id: The agent ID
            error: The exception that occurred
        """
        try:
            from cai.util import cleanup_agent_streaming_resources

            if instance_agent:
                agent_display_name = getattr(instance_agent, 'name', config.agent_name)
                cleanup_agent_streaming_resources(agent_display_name)
        except Exception:
            pass

        # Save history on error
        if instance_agent and agent_id:
            from cai.sdk.agents.parallel_isolation import PARALLEL_ISOLATION
            if hasattr(instance_agent, 'model') and hasattr(instance_agent.model, 'message_history'):
                PARALLEL_ISOLATION.replace_isolated_history(agent_id, instance_agent.model.message_history)

        # Log error details
        import logging
        logger = logging.getLogger(__name__)
        error_details = f"Error in {config.agent_name}"
        if config.model:
            error_details += f" (model: {config.model})"
        error_details += f": {str(error)}"
        logger.error(error_details, exc_info=True)

        # Only show error in debug mode
        if os.getenv("CAI_DEBUG", "1") == "2":
            self.console.print(f"[bold red]{error_details}[/bold red]")

    async def _handle_parallel_interruption(self) -> None:
        """Handle interruption during parallel execution."""
        # Force save all parallel agent histories
        for idx, config in enumerate(PARALLEL_CONFIGS, 1):
            instance_key = (config.agent_name, idx)
            if instance_key in PARALLEL_AGENT_INSTANCES:
                instance_agent = PARALLEL_AGENT_INSTANCES[instance_key]
                if hasattr(instance_agent, 'model') and hasattr(instance_agent.model, 'message_history'):
                    agent_id = config.id or f"P{idx}"
                    from cai.sdk.agents.parallel_isolation import PARALLEL_ISOLATION
                    PARALLEL_ISOLATION.replace_isolated_history(agent_id, instance_agent.model.message_history)

                    # Also sync with AGENT_MANAGER for display
                    from cai.agents import get_available_agents
                    available_agents = get_available_agents()
                    if config.agent_name in available_agents:
                        agent = available_agents[config.agent_name]
                        agent_display_name = getattr(agent, "name", config.agent_name)

                        # Add instance number if needed
                        total_count = sum(1 for c in PARALLEL_CONFIGS if c.agent_name == config.agent_name)
                        if total_count > 1:
                            instance_num = 0
                            for c in PARALLEL_CONFIGS:
                                if c.agent_name == config.agent_name:
                                    instance_num += 1
                                    if c.id == config.id:
                                        break
                            agent_display_name = f"{agent_display_name} #{instance_num}"

                        # Clear and replace the history in AGENT_MANAGER
                        from cai.sdk.agents.simple_agent_manager import AGENT_MANAGER
                        AGENT_MANAGER.clear_history(agent_display_name)
                        for msg in instance_agent.model.message_history:
                            AGENT_MANAGER.add_to_history(agent_display_name, msg)

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
        if agent.name in visited:
            return
        visited.add(agent.name)

        # Update the main agent's model
        if hasattr(agent, "model") and hasattr(agent.model, "model"):
            agent.model.model = new_model
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
                    self._update_agent_models_recursively(handoff_item, new_model, visited)