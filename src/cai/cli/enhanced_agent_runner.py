"""
Enhanced Agent Runner with Continuous Learning Integration

Extends the base agent runner with learning capabilities.
"""

import asyncio
import time
from typing import List, Dict, Any, Union, Optional

from .agent_runner import AgentRunner
from .learning_integration import (
    get_learning_integration,
    learning_hook_before_agent_run,
    learning_hook_after_agent_run
)


class EnhancedAgentRunner(AgentRunner):
    """Enhanced agent runner with continuous learning capabilities."""

    def __init__(self, console: Any):
        """Initialize the enhanced agent runner.

        Args:
            console: Rich console for output
        """
        super().__init__(console)
        self.learning_manager = get_learning_integration()
        self.learning_enabled = True

    async def run_agent_conversation(
        self,
        agent: Any,
        user_input: str,
        parallel_count: int = 1,
        context: str = ""
    ) -> None:
        """Run agent conversation with learning integration.

        Args:
            agent: The agent to run
            user_input: User input for the conversation
            parallel_count: Number of parallel instances to run
            context: Context description for learning
        """
        if not context:
            context = self._extract_context_from_input(user_input)

        # Learning hook: before agent run
        if self.learning_enabled:
            await learning_hook_before_agent_run(agent, user_input, context)

        # Track execution time and tools used
        start_time = time.time()
        tools_used = []
        result = None  # Initialize result variable

        try:
            # Build conversation context
            conversation_input = self._build_conversation_context(agent, user_input)

            # Process the conversation
            if parallel_count > 1:
                await self._run_parallel_agents(agent, conversation_input, parallel_count)
                result = "Parallel agents execution completed"  # Simple result for parallel case
            else:
                result = await self._run_single_agent_with_tracking(
                    agent, conversation_input, tools_used
                )

            # Calculate execution time
            execution_time = time.time() - start_time

            # Learning hook: after agent run
            if self.learning_enabled and result:
                await learning_hook_after_agent_run(
                    agent=agent,
                    user_input=user_input,
                    response=result,
                    execution_time=execution_time,
                    tools_used=tools_used
                )

        except Exception as e:
            # Still record failed interactions for learning
            execution_time = time.time() - start_time
            if self.learning_enabled:
                await learning_hook_after_agent_run(
                    agent=agent,
                    user_input=user_input,
                    response=f"Error: {str(e)}",
                    execution_time=execution_time,
                    tools_used=tools_used
                )
            raise

    async def _run_single_agent_with_tracking(
        self,
        agent: Any,
        conversation_input: Union[List[Dict], str],
        tools_used: List[str]
    ) -> Any:
        """Run single agent with tool usage tracking.

        Args:
            agent: The agent to run
            conversation_input: Conversation context
            tools_used: List to track tools used

        Returns:
            Agent result
        """
        # Determine if streaming is enabled
        import os
        cai_stream = os.getenv("CAI_STREAM", "false")
        if not cai_stream or cai_stream.strip() == "":
            cai_stream = "false"
        stream = cai_stream.lower() == "true"

        result = None

        with self.console.status("[bold green]Thinking...", spinner="dots"):
            try:
                if stream:
                    result = await self._process_streamed_response_with_tracking(
                        agent, conversation_input, tools_used
                    )
                else:
                    result = await self._run_non_streaming_with_tracking(
                        agent, conversation_input, tools_used
                    )

            except Exception as e:
                if isinstance(e, KeyboardInterrupt):
                    self.console.print("\n[yellow]Interrupted by user. Cleaning up...[/yellow]")
                else:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"An error occurred during agent execution: {str(e)}", exc_info=True)
                    if os.getenv("CAI_DEBUG", "1") == "2":
                        import traceback
                        self.console.print(f"[red]Traceback:\n{traceback.format_exc()}[/red]")

        return result

    async def _run_non_streaming_with_tracking(
        self,
        agent: Any,
        conversation_input: Union[List[Dict], str],
        tools_used: List[str]
    ) -> Any:
        """Run non-streaming agent with tool tracking.

        Args:
            agent: The agent to run
            conversation_input: Conversation context
            tools_used: List to track tools used

        Returns:
            Agent result
        """
        # For non-streaming, we need to monitor tool calls differently
        # This is a simplified implementation - in practice, you'd need
        # to hook into the agent's tool execution system

        result = await self._run_non_streaming(agent, conversation_input)

        # Extract tool usage from result (simplified)
        if hasattr(result, 'tool_calls') and result.tool_calls:
            for tool_call in result.tool_calls:
                if hasattr(tool_call, 'function') and hasattr(tool_call.function, 'name'):
                    tools_used.append(tool_call.function.name)

        return result
        
    async def _run_non_streaming(self, agent: Any, conversation_input: Union[List[Dict], str]) -> Any:
        """Run non-streaming agent execution.

        Args:
            agent: The agent to run
            conversation_input: Conversation context

        Returns:
            Agent result
        """
        from cai.sdk.agents import Runner
        return await Runner.run(agent, conversation_input)

    async def _process_streamed_response_with_tracking(
        self,
        agent: Any,
        conversation_input: Union[List[Dict], str],
        tools_used: List[str]
    ) -> Any:
        """Process streamed response with tool usage tracking.

        Args:
            agent: The agent to run
            conversation_input: Conversation context
            tools_used: List to track tools used

        Returns:
            Streaming result
        """
        from cai.sdk.agents.stream_events import RunItemStreamEvent
        from cai.sdk.agents.items import ToolCallOutputItem

        tool_calls_seen = {}
        stream_result = None
        stream_iterator = None

        try:
            stream_result = self._run_streaming(agent, conversation_input)
            stream_iterator = stream_result.stream_events()

            async for event in stream_iterator:
                if isinstance(event, RunItemStreamEvent):
                    if event.name == "tool_called" and hasattr(event.item, 'raw_item'):
                        call_id = getattr(event.item.raw_item, 'call_id', None)
                        if call_id:
                            tool_calls_seen[call_id] = event.item
                            # Track tool usage
                            if hasattr(event.item.raw_item, 'function'):
                                func_name = event.item.raw_item.function.get('name', 'unknown')
                                if func_name not in tools_used:
                                    tools_used.append(func_name)

                    elif event.name == "tool_output" and isinstance(event.item, ToolCallOutputItem):
                        call_id = event.item.raw_item["call_id"]
                        agent.model.add_to_message_history({
                            "role": "tool",
                            "tool_call_id": call_id,
                            "content": event.item.output,
                        })

        finally:
            if stream_iterator and hasattr(stream_iterator, 'aclose'):
                await stream_iterator.aclose()

        return stream_result

    def _extract_context_from_input(self, user_input: str) -> str:
        """Extract context description from user input.

        Args:
            user_input: User input

        Returns:
            str: Context description
        """
        # Simple context extraction - in practice, this could be more sophisticated
        input_lower = user_input.lower()

        if any(word in input_lower for word in ['scan', 'recon', 'enumerate']):
            return "reconnaissance and network scanning"
        elif any(word in input_lower for word in ['exploit', 'attack', 'vulnerability']):
            return "vulnerability exploitation and attack techniques"
        elif any(word in input_lower for word in ['analyze', 'assess', 'evaluate']):
            return "security analysis and assessment"
        elif any(word in input_lower for word in ['web', 'http', 'url']):
            return "web application security testing"
        elif any(word in input_lower for word in ['network', 'port', 'service']):
            return "network security and service enumeration"
        else:
            return "general cybersecurity operations"

    def enable_learning(self) -> None:
        """Enable learning for this runner."""
        self.learning_enabled = True
        print("✓ Learning enabled for agent runner")

    def disable_learning(self) -> None:
        """Disable learning for this runner."""
        self.learning_enabled = False
        print("✓ Learning disabled for agent runner")

    async def get_learning_insights(self, context: str) -> Dict[str, Any]:
        """Get learning insights for current context.

        Args:
            context: Context description

        Returns:
            Dict with learning insights
        """
        return await self.learning_manager.get_learning_insights(context)

    def add_user_feedback(self, feedback: str, rating: Optional[int] = None) -> None:
        """Add user feedback to learning system.

        Args:
            feedback: User feedback
            rating: Optional rating (1-5)
        """
        self.learning_manager.add_user_feedback(feedback, rating)


# Example usage and integration
async def demonstrate_learning_integration():
    """Demonstrate how the enhanced runner works with learning."""
    from rich.console import Console

    console = Console()
    runner = EnhancedAgentRunner(console)

    # Enable learning
    runner.enable_learning()

    # Example agent (simplified)
    class MockAgent:
        def __init__(self):
            self.name = "Test Agent"
            self.model = None

    agent = MockAgent()

    # Simulate a conversation with learning
    user_input = "Scan the network for vulnerabilities"

    print("Running agent with learning integration...")
    try:
        await runner.run_agent_conversation(agent, user_input)
    except Exception as e:
        print(f"Demo completed with expected error: {e}")

    # Get learning insights
    insights = await runner.get_learning_insights("network scanning")
    print(f"Learning insights: {len(insights.get('insights', []))} patterns found")

    # Add user feedback
    runner.add_user_feedback("The scanning was very thorough", rating=5)


if __name__ == "__main__":
    asyncio.run(demonstrate_learning_integration())