"""
Learning Integration Module for CAI

Integrates continuous learning capabilities with the existing CAI architecture.
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from .continuous_learning import get_learning_engine, start_background_learning
from .agent_runner import AgentRunner
from .state_manager import CLIState


class LearningIntegrationManager:
    """Manages integration of continuous learning with CAI components."""

    def __init__(self):
        """Initialize the learning integration manager."""
        self.learning_engine = get_learning_engine()
        self.learning_enabled = True
        self.current_session_id: Optional[str] = None

    def enable_learning(self) -> None:
        """Enable continuous learning."""
        self.learning_enabled = True
        print("✓ Continuous learning enabled")

    def disable_learning(self) -> None:
        """Disable continuous learning."""
        self.learning_enabled = False
        print("✓ Continuous learning disabled")

    def start_session(self, session_id: str) -> None:
        """Start a learning session.

        Args:
            session_id: Unique session identifier
        """
        if not self.learning_enabled:
            return

        self.current_session_id = session_id
        self.learning_engine.start_learning_session(session_id)
        print(f"✓ Learning session started: {session_id}")

    async def record_agent_interaction(
        self,
        agent_name: str,
        user_input: str,
        agent_response: Any,
        success: bool = None,
        execution_time: float = None,
        tools_used: List[str] = None
    ) -> None:
        """Record an agent interaction for learning.

        Args:
            agent_name: Name of the agent
            user_input: User's input
            agent_response: Agent's response
            success: Whether the interaction was successful
            execution_time: Time taken for execution
            tools_used: List of tools used
        """
        if not self.learning_enabled or not self.current_session_id:
            return

        # Extract response content
        response_content = ""
        if hasattr(agent_response, 'final_output') and agent_response.final_output:
            response_content = agent_response.final_output
        elif hasattr(agent_response, 'content'):
            response_content = agent_response.content
        else:
            response_content = str(agent_response)

        # Determine success if not provided
        if success is None:
            success = self._assess_interaction_success(response_content, user_input)

        interaction_data = {
            'agent_name': agent_name,
            'user_input': user_input,
            'response_content': response_content,
            'success': success,
            'execution_time': execution_time,
            'tools_used': tools_used or [],
            'interaction_type': self._classify_interaction_type(user_input, response_content),
            'metadata': {
                'response_length': len(response_content),
                'has_tools': bool(tools_used),
                'tool_count': len(tools_used) if tools_used else 0
            }
        }

        self.learning_engine.record_interaction(self.current_session_id, interaction_data)

    def _assess_interaction_success(self, response: str, user_input: str) -> bool:
        """Assess whether an interaction was successful.

        Args:
            response: Agent response
            user_input: User input

        Returns:
            bool: Success assessment
        """
        # Simple heuristics for success assessment
        success_indicators = [
            'success', 'successful', 'completed', 'found', 'identified',
            'vulnerability', 'exploit', 'access', 'gained', 'successful'
        ]

        failure_indicators = [
            'failed', 'error', 'unable', 'cannot', 'failed to',
            'no results', 'not found', 'denied', 'blocked'
        ]

        response_lower = response.lower()
        input_lower = user_input.lower()

        # Check for success indicators
        success_score = sum(1 for indicator in success_indicators
                          if indicator in response_lower)

        # Check for failure indicators
        failure_score = sum(1 for indicator in failure_indicators
                           if indicator in response_lower)

        # If we have clear success/failure signals, use them
        if success_score > failure_score:
            return True
        elif failure_score > success_score:
            return False

        # Default to success for non-empty responses
        return len(response.strip()) > 10

    def _classify_interaction_type(self, user_input: str, response: str) -> str:
        """Classify the type of interaction.

        Args:
            user_input: User input
            response: Agent response

        Returns:
            str: Interaction type
        """
        input_lower = user_input.lower()
        response_lower = response.lower()

        # Classification rules
        if any(word in input_lower for word in ['scan', 'recon', 'enumerate', 'discover']):
            return 'reconnaissance'
        elif any(word in input_lower for word in ['exploit', 'attack', 'vulnerability']):
            return 'exploitation'
        elif any(word in input_lower for word in ['analyze', 'assess', 'evaluate']):
            return 'analysis'
        elif any(word in response_lower for word in ['tool', 'command', 'execute']):
            return 'tool_usage'
        elif any(word in input_lower for word in ['report', 'summary', 'findings']):
            return 'reporting'
        else:
            return 'general'

    async def get_learning_insights(self, context: str) -> Dict[str, Any]:
        """Get learning insights relevant to current context.

        Args:
            context: Current context description

        Returns:
            Dict with learning insights
        """
        if not self.learning_enabled:
            return {'insights': [], 'message': 'Learning disabled'}

        # Get relevant patterns
        patterns = self.learning_engine.get_relevant_patterns(context, limit=3)

        insights = []
        for pattern in patterns:
            insights.append({
                'pattern_id': pattern.pattern_id,
                'type': pattern.pattern_type,
                'description': pattern.description,
                'confidence': pattern.confidence_score,
                'success_rate': pattern.success_rate,
                'recommendations': pattern.metadata.get('recommendations', [])
            })

        return {
            'insights': insights,
            'total_patterns': len(self.learning_engine.learning_patterns),
            'context': context
        }

    async def apply_learning_to_agent(self, agent: Any, context: str) -> None:
        """Apply learned patterns to enhance agent behavior.

        Args:
            agent: The agent to enhance
            context: Current context
        """
        if not self.learning_enabled:
            return

        insights = await self.get_learning_insights(context)

        if not insights['insights']:
            return

        # Create enhanced instructions based on learned patterns
        enhancement_prompt = self._create_enhancement_prompt(insights['insights'])

        # Apply enhancement to agent
        if hasattr(agent, 'instructions'):
            original_instructions = agent.instructions
            enhanced_instructions = f"{original_instructions}\n\n--- LEARNED INSIGHTS ---\n{enhancement_prompt}"
            agent.instructions = enhanced_instructions

        print(f"✓ Applied {len(insights['insights'])} learned patterns to agent")

    def _create_enhancement_prompt(self, insights: List[Dict[str, Any]]) -> str:
        """Create an enhancement prompt from learned insights.

        Args:
            insights: List of learning insights

        Returns:
            str: Enhancement prompt
        """
        if not insights:
            return ""

        prompt_parts = ["Based on previous successful interactions, consider these proven approaches:"]

        for insight in insights:
            if insight['confidence'] > 0.7:  # Only high-confidence patterns
                prompt_parts.append(f"- {insight['description']}")
                if insight['recommendations']:
                    prompt_parts.append(f"  Recommendations: {', '.join(insight['recommendations'][:2])}")

        return "\n".join(prompt_parts)

    async def end_session_and_learn(self) -> Dict[str, Any]:
        """End current session and trigger learning analysis.

        Returns:
            Dict with learning results
        """
        if not self.current_session_id:
            return {'message': 'No active session'}

        # Analyze patterns from session
        patterns = await self.learning_engine.analyze_session_patterns(self.current_session_id)

        # Get learning statistics
        stats = self.learning_engine.get_learning_stats()

        result = {
            'session_id': self.current_session_id,
            'patterns_discovered': len(patterns),
            'total_patterns': stats['total_patterns'],
            'average_confidence': stats['average_confidence'],
            'new_patterns': [
                {
                    'id': p.pattern_id,
                    'type': p.pattern_type,
                    'description': p.description,
                    'confidence': p.confidence_score
                }
                for p in patterns
            ]
        }

        # Clear current session
        self.current_session_id = None

        return result

    def add_user_feedback(self, feedback: str, rating: int = None) -> None:
        """Add user feedback to the learning system.

        Args:
            feedback: User feedback text
            rating: Optional rating (1-5)
        """
        if not self.current_session_id:
            return

        feedback_data = {
            'feedback': feedback,
            'rating': rating,
            'timestamp': datetime.now().isoformat(),
            'type': 'user_feedback'
        }

        self.learning_engine.add_feedback(self.current_session_id, feedback_data)

    def get_learning_status(self) -> Dict[str, Any]:
        """Get current learning system status.

        Returns:
            Dict with learning status
        """
        stats = self.learning_engine.get_learning_stats()

        return {
            'enabled': self.learning_enabled,
            'current_session': self.current_session_id,
            'total_patterns': stats['total_patterns'],
            'active_sessions': stats['active_sessions'],
            'pattern_types': stats['pattern_types'],
            'average_confidence': stats['average_confidence'],
            'last_updated': stats['last_updated']
        }


# Global integration manager
_integration_manager: Optional[LearningIntegrationManager] = None


def get_learning_integration() -> LearningIntegrationManager:
    """Get the global learning integration manager."""
    global _integration_manager
    if _integration_manager is None:
        _integration_manager = LearningIntegrationManager()
    return _integration_manager


async def initialize_learning_integration() -> None:
    """Initialize the learning integration system."""
    manager = get_learning_integration()

    # Start background learning
    start_background_learning()

    print("✓ Learning integration system initialized")
    print(f"  - Learning enabled: {manager.learning_enabled}")
    print(f"  - Existing patterns: {len(manager.learning_engine.learning_patterns)}")


# Integration hooks for existing CAI components
async def learning_hook_before_agent_run(agent: Any, user_input: str, context: str) -> None:
    """Hook to run before agent execution for learning integration.

    Args:
        agent: The agent being executed
        user_input: User input
        context: Current context
    """
    manager = get_learning_integration()
    if not manager.learning_enabled:
        return

    # Apply learned patterns to agent
    await manager.apply_learning_to_agent(agent, context)


async def learning_hook_after_agent_run(
    agent: Any,
    user_input: str,
    response: Any,
    execution_time: float,
    tools_used: List[str]
) -> None:
    """Hook to run after agent execution for learning.

    Args:
        agent: The agent that was executed
        user_input: User input
        response: Agent response
        execution_time: Time taken
        tools_used: Tools used
    """
    manager = get_learning_integration()
    if not manager.learning_enabled:
        return

    # Record interaction for learning
    agent_name = getattr(agent, 'name', 'Unknown Agent')
    await manager.record_agent_interaction(
        agent_name=agent_name,
        user_input=user_input,
        agent_response=response,
        execution_time=execution_time,
        tools_used=tools_used
    )


def learning_hook_session_start(session_id: str) -> None:
    """Hook to run when a session starts.

    Args:
        session_id: Session identifier
    """
    manager = get_learning_integration()
    manager.start_session(session_id)


async def learning_hook_session_end() -> Dict[str, Any]:
    """Hook to run when a session ends.

    Returns:
        Dict with learning results
    """
    manager = get_learning_integration()
    return await manager.end_session_and_learn()