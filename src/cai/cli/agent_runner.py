"""
Agent Runner Module for CAI CLI

Handles agent execution, conversation processing, and result management.
"""

import os
import time
import asyncio
from typing import List, Dict, Any, Optional, Union
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text

from cai.sdk.agents import Runner
from cai.sdk.agents.stream_events import RunItemStreamEvent
from cai.sdk.agents.items import ToolCallOutputItem
from cai.util import fix_message_list, start_active_timer, stop_active_timer, start_idle_timer, stop_idle_timer


class AgentRunner:
    """Handles agent execution and conversation processing."""

    def __init__(self, console: Console):
        """Initialize the agent runner.

        Args:
            console: Rich console for output
        """
        self.console = console

    async def run_agent_conversation(
        self,
        agent: Any,
        user_input: str,
        parallel_count: int = 1
    ) -> None:
        """Run agent conversation with support for parallel execution.

        Args:
            agent: The agent to run
            user_input: User input for the conversation
            parallel_count: Number of parallel instances to run
        """
        # Build conversation context
        conversation_input = self._build_conversation_context(agent, user_input)

        # Process the conversation with parallel execution if enabled
        if parallel_count > 1:
            await self._run_parallel_agents(agent, conversation_input, parallel_count)
        else:
            await self._run_single_agent(agent, conversation_input)

        # Final validation to ensure message history follows OpenAI's requirements
        if hasattr(agent, 'model') and hasattr(agent.model, 'message_history'):
            agent.model.message_history[:] = fix_message_list(agent.model.message_history)

    def _build_conversation_context(self, agent: Any, user_input: str) -> Union[List[Dict], str]:
        """Build conversation context from message history.

        Args:
            agent: The agent whose history to use
            user_input: The current user input

        Returns:
            Conversation context for the agent
        """
        # Build conversation context from previous turns
        history_context = []

        # Use the agent's model's message history directly
        if hasattr(agent, 'model') and hasattr(agent.model, 'message_history'):
            for msg in agent.model.message_history:
                role = msg.get("role")
                content = msg.get("content")
                tool_calls = msg.get("tool_calls")

                if role == "user":
                    history_context.append({"role": "user", "content": content or ""})
                elif role == "system":
                    history_context.append({"role": "system", "content": content or ""})
                elif role == "assistant":
                    if tool_calls:
                        history_context.append({
                            "role": "assistant",
                            "content": content,  # Can be None
                            "tool_calls": tool_calls,
                        })
                    elif content is not None:
                        history_context.append({"role": "assistant", "content": content})
                    elif content is None and not tool_calls:
                        # Explicitly handle empty assistant message
                        history_context.append({"role": "assistant", "content": None})
                elif role == "tool":
                    history_context.append({
                        "role": "tool",
                        "tool_call_id": msg.get("tool_call_id"),
                        "content": msg.get("content"),  # Tool output
                    })

        # Fix message list structure BEFORE sending to the model
        try:
            history_context = fix_message_list(history_context)
        except Exception:
            pass

        # Append the current user input as the last message
        conversation_input: Union[List[Dict], str]
        if history_context:
            history_context.append({"role": "user", "content": user_input})
            conversation_input = history_context
        else:
            # Fallback for CTF or other special cases
            conversation_input = user_input

        return conversation_input

    async def _run_single_agent(self, agent: Any, conversation_input: Union[List[Dict], str]) -> None:
        """Run a single agent instance.

        Args:
            agent: The agent to run
            conversation_input: The conversation context
        """
        # Determine if streaming is enabled
        cai_stream = os.getenv("CAI_STREAM", "false")
        if not cai_stream or cai_stream.strip() == "":
            cai_stream = "false"
        stream = cai_stream.lower() == "true"

        result = None
        with self.console.status("[bold green]Thinking...", spinner="dots"):
            try:
                if stream:
                    result = await self._process_streamed_response(agent, conversation_input)
                else:
                    result = await Runner.run(agent, conversation_input)

            except (KeyboardInterrupt, Exception) as e:
                if isinstance(e, KeyboardInterrupt):
                    self.console.print("\n[yellow]Interrupted by user. Cleaning up...[/yellow]")
                else:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"An error occurred during agent execution: {str(e)}", exc_info=True)
                    if os.getenv("CAI_DEBUG", "1") == "2":
                        import traceback
                        self.console.print(f"[red]Traceback:\n{traceback.format_exc()}[/red]")

    async def _process_streamed_response(self, agent: Any, conversation_input: Union[List[Dict], str]) -> Any:
        """Process a streamed response from the agent.

        Args:
            agent: The agent to run
            conversation_input: The conversation context

        Returns:
            The streaming result
        """
        tool_calls_seen = {}
        tool_results_seen = set()
        stream_result = None
        stream_iterator = None

        try:
            stream_result = Runner.run_streamed(agent, conversation_input)
            stream_iterator = stream_result.stream_events()

            async for event in stream_iterator:
                if isinstance(event, RunItemStreamEvent):
                    if event.name == "tool_called" and hasattr(event.item, 'raw_item'):
                        call_id = getattr(event.item.raw_item, 'call_id', None)
                        if call_id:
                            tool_calls_seen[call_id] = event.item
                    elif event.name == "tool_output" and isinstance(event.item, ToolCallOutputItem):
                        call_id = event.item.raw_item["call_id"]
                        tool_results_seen.add(call_id)
                        agent.model.add_to_message_history({
                            "role": "tool",
                            "tool_call_id": call_id,
                            "content": event.item.output,
                        })
        finally:
            if stream_iterator and hasattr(stream_iterator, 'aclose'):
                await stream_iterator.aclose()

        return stream_result

    async def _run_parallel_agents(self, agent: Any, conversation_input: Union[List[Dict], str], parallel_count: int) -> None:
        """Run multiple agent instances in parallel.

        Args:
            agent: The base agent to clone
            conversation_input: The conversation context
            parallel_count: Number of parallel instances
        """
        # Import here to avoid circular imports
        from cai.agents import get_available_agents, get_agent_by_name

        async def run_agent_instance(instance_number: int, conversation_context: Union[List[Dict], str]):
            """Run a single agent instance with its own complete context"""
            try:
                # Create a fresh agent instance with unique name
                base_agent = get_available_agents().get(agent.name.lower())
                agent_display_name = base_agent.name if base_agent else agent.name
                custom_name = f"{agent_display_name} #{instance_number + 1}"
                instance_agent = get_agent_by_name(agent.name, custom_name=custom_name, agent_id=f"P{instance_number + 1}")

                # Configure agent instance to match main agent settings
                if hasattr(instance_agent, "model") and hasattr(agent, "model"):
                    if hasattr(instance_agent.model, "model") and hasattr(agent.model, "model"):
                        # Check for instance-specific model override
                        instance_specific_model = os.getenv(f"CAI_{agent.name.upper()}_{instance_number + 1}_MODEL")

                        if instance_specific_model:
                            model_to_use = instance_specific_model
                        else:
                            # Check for agent-specific model override
                            agent_specific_model = os.getenv(f"CAI_{agent.name.upper()}_MODEL")
                            model_to_use = agent_specific_model if agent_specific_model else agent.model.model

                        # Update model recursively
                        self._update_agent_models_recursively(instance_agent, model_to_use)

                # Run the agent with its own isolated context
                result = await Runner.run(instance_agent, conversation_context)
                return (instance_number, result)

            except Exception as e:
                # Log error for debugging
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error in instance {instance_number}: {str(e)}", exc_info=True)

                # Only show error in debug mode
                if os.getenv("CAI_DEBUG", "1") == "2":
                    self.console.print(f"[bold red]Error in instance {instance_number}: {str(e)}[/bold red]")
                return (instance_number, None)

        async def process_parallel_responses():
            """Process multiple parallel agent executions"""
            # Create tasks for each instance
            tasks = [run_agent_instance(i, conversation_input) for i in range(parallel_count)]

            # Wait for all to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Filter out exceptions and failed results
            valid_results = []
            for result in results:
                if isinstance(result, tuple) and len(result) == 2:
                    idx, res = result
                    if res is not None and not isinstance(res, Exception):
                        valid_results.append((idx, res))

            return valid_results

        # Execute all parallel instances
        results = await process_parallel_responses()

        # Display the results
        for idx, result in results:
            if result and hasattr(result, "final_output") and result.final_output:
                # Add to main message history for context
                agent.model.add_to_message_history({
                    "role": "assistant",
                    "content": f"{result.final_output}"
                })

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