"""
Continuous Learning Module for CAI

Implements real-time learning capabilities using LLM-based knowledge extraction,
pattern recognition, and model adaptation.
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import hashlib
import os

from cai.sdk.agents import Agent, OpenAIChatCompletionsModel
from cai.util import fix_message_list


@dataclass
class LearningPattern:
    """Represents a learned pattern from interactions."""
    pattern_id: str
    pattern_type: str  # 'technique', 'vulnerability', 'exploit', 'defense'
    description: str
    confidence_score: float
    success_rate: float
    usage_count: int
    last_updated: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    examples: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class LearningSession:
    """Tracks learning data from a single session."""
    session_id: str
    start_time: datetime
    interactions: List[Dict[str, Any]] = field(default_factory=list)
    patterns_discovered: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    feedback_received: List[Dict[str, Any]] = field(default_factory=list)


class ContinuousLearningEngine:
    """Main engine for continuous learning capabilities."""

    def __init__(self, knowledge_base_path: str = "data/knowledge_base"):
        """Initialize the continuous learning engine.

        Args:
            knowledge_base_path: Path to store learned knowledge
        """
        self.knowledge_base_path = knowledge_base_path
        self.learning_patterns: Dict[str, LearningPattern] = {}
        self.active_sessions: Dict[str, LearningSession] = {}
        self.learning_agent: Optional[Agent] = None

        # Learning configuration
        self.learning_config = {
            "min_confidence_threshold": 0.7,
            "max_patterns_per_session": 10,
            "learning_interval_minutes": 30,
            "feedback_collection_enabled": True,
            "pattern_similarity_threshold": 0.85,
            "auto_update_models": False
        }

        # Create knowledge base directory
        os.makedirs(knowledge_base_path, exist_ok=True)
        os.makedirs(f"{knowledge_base_path}/patterns", exist_ok=True)
        os.makedirs(f"{knowledge_base_path}/sessions", exist_ok=True)

        # Load existing knowledge
        self._load_knowledge_base()

    def _load_knowledge_base(self) -> None:
        """Load existing patterns and knowledge from disk."""
        try:
            # Load patterns
            patterns_file = f"{self.knowledge_base_path}/patterns.json"
            if os.path.exists(patterns_file):
                with open(patterns_file, 'r', encoding='utf-8') as f:
                    patterns_data = json.load(f)
                    for pattern_data in patterns_data:
                        pattern = LearningPattern(**pattern_data)
                        self.learning_patterns[pattern.pattern_id] = pattern

            print(f"✓ Loaded {len(self.learning_patterns)} learning patterns")

        except Exception as e:
            print(f"Warning: Could not load knowledge base: {e}")

    def _save_knowledge_base(self) -> None:
        """Save current knowledge base to disk."""
        try:
            patterns_file = f"{self.knowledge_base_path}/patterns.json"
            patterns_data = [
                {
                    **pattern.__dict__,
                    'last_updated': pattern.last_updated.isoformat()
                }
                for pattern in self.learning_patterns.values()
            ]

            with open(patterns_file, 'w', encoding='utf-8') as f:
                json.dump(patterns_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"Error saving knowledge base: {e}")

    def start_learning_session(self, session_id: str) -> LearningSession:
        """Start a new learning session.

        Args:
            session_id: Unique identifier for the session

        Returns:
            LearningSession: The created session
        """
        session = LearningSession(
            session_id=session_id,
            start_time=datetime.now()
        )
        self.active_sessions[session_id] = session
        return session

    def record_interaction(self, session_id: str, interaction_data: Dict[str, Any]) -> None:
        """Record an interaction for learning.

        Args:
            session_id: The session ID
            interaction_data: Data about the interaction
        """
        if session_id not in self.active_sessions:
            return

        session = self.active_sessions[session_id]
        session.interactions.append({
            **interaction_data,
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id
        })

    async def analyze_session_patterns(self, session_id: str) -> List[LearningPattern]:
        """Analyze a session to extract learning patterns.

        Args:
            session_id: The session ID to analyze

        Returns:
            List of discovered patterns
        """
        if session_id not in self.active_sessions:
            return []

        session = self.active_sessions[session_id]

        # Initialize learning agent if not done
        if not self.learning_agent:
            await self._initialize_learning_agent()

        # Extract patterns from interactions
        patterns = await self._extract_patterns_from_interactions(session.interactions)

        # Filter and validate patterns
        valid_patterns = []
        for pattern in patterns:
            if self._validate_pattern(pattern):
                valid_patterns.append(pattern)
                self.learning_patterns[pattern.pattern_id] = pattern
                session.patterns_discovered.append(pattern.pattern_id)

        # Save updated knowledge base
        self._save_knowledge_base()

        return valid_patterns

    async def _initialize_learning_agent(self) -> None:
        """Initialize the specialized learning agent."""
        from cai.sdk.agents import Agent, OpenAIChatCompletionsModel
        from openai import AsyncOpenAI

        learning_instructions = """
        You are a cybersecurity pattern recognition and learning specialist.
        Your role is to analyze security interactions and extract actionable patterns
        that can improve future security assessments.

        Focus on:
        1. Vulnerability patterns and exploitation techniques
        2. Defense mechanisms and their effectiveness
        3. Tool usage patterns and success rates
        4. Environmental factors affecting security outcomes
        5. Adaptive strategies for different threat scenarios

        Always provide structured, actionable insights with confidence scores.
        """

        self.learning_agent = Agent(
            name="Learning Agent",
            instructions=learning_instructions,
            model=OpenAIChatCompletionsModel(
                model=os.getenv("CAI_MODEL", "openai/gpt-4o"),
                openai_client=AsyncOpenAI()
            )
        )

    async def _extract_patterns_from_interactions(self, interactions: List[Dict[str, Any]]) -> List[LearningPattern]:
        """Extract learning patterns from interaction data.

        Args:
            interactions: List of interaction data

        Returns:
            List of extracted patterns
        """
        patterns = []

        # Group interactions by type
        interaction_groups = self._group_interactions_by_type(interactions)

        for interaction_type, group_interactions in interaction_groups.items():
            if len(group_interactions) < 3:  # Need minimum data for pattern recognition
                continue

            # Analyze patterns for this group
            group_patterns = await self._analyze_interaction_group(
                interaction_type, group_interactions
            )
            patterns.extend(group_patterns)

        return patterns

    def _group_interactions_by_type(self, interactions: List[Dict[str, Any]]) -> Dict[str, List]:
        """Group interactions by their type/category.

        Args:
            interactions: List of interactions

        Returns:
            Dict of grouped interactions
        """
        groups = {}

        for interaction in interactions:
            # Determine interaction type
            interaction_type = self._classify_interaction(interaction)
            if interaction_type not in groups:
                groups[interaction_type] = []
            groups[interaction_type].append(interaction)

        return groups

    def _classify_interaction(self, interaction: Dict[str, Any]) -> str:
        """Classify an interaction into a category.

        Args:
            interaction: Interaction data

        Returns:
            Classification string
        """
        # Simple classification logic
        if 'tool' in interaction.get('type', '').lower():
            return 'tool_usage'
        elif 'exploit' in interaction.get('content', '').lower():
            return 'exploitation'
        elif 'scan' in interaction.get('content', '').lower():
            return 'reconnaissance'
        elif 'vulnerability' in interaction.get('content', '').lower():
            return 'vulnerability_analysis'
        else:
            return 'general_security'

    async def _analyze_interaction_group(self, group_type: str, interactions: List[Dict[str, Any]]) -> List[LearningPattern]:
        """Analyze a group of interactions to extract patterns.

        Args:
            group_type: Type of interaction group
            interactions: List of interactions in the group

        Returns:
            List of extracted patterns
        """
        patterns = []

        # Create analysis prompt
        analysis_prompt = self._create_analysis_prompt(group_type, interactions)

        try:
            # Use learning agent to analyze patterns
            result = await self.learning_agent.run(analysis_prompt)

            # Parse the result to extract patterns
            extracted_patterns = self._parse_analysis_result(result, group_type)
            patterns.extend(extracted_patterns)

        except Exception as e:
            print(f"Error analyzing interaction group {group_type}: {e}")

        return patterns

    def _create_analysis_prompt(self, group_type: str, interactions: List[Dict[str, Any]]) -> str:
        """Create a prompt for pattern analysis.

        Args:
            group_type: Type of interaction group
            interactions: List of interactions

        Returns:
            Analysis prompt string
        """
        # Summarize interactions for analysis
        interaction_summary = "\n".join([
            f"- {i.get('content', '')[:200]}... (Success: {i.get('success', 'unknown')})"
            for i in interactions[:10]  # Limit to first 10 for analysis
        ])

        prompt = f"""
        Analyze the following {group_type} interactions and extract learning patterns:

        INTERACTIONS:
        {interaction_summary}

        Please identify:
        1. Common techniques or approaches that worked well
        2. Patterns in successful vs unsuccessful attempts
        3. Environmental factors that affected outcomes
        4. Recommendations for future similar scenarios

        Provide your analysis in the following JSON format:
        {{
            "patterns": [
                {{
                    "type": "technique|vulnerability|exploit|defense",
                    "description": "Clear description of the pattern",
                    "confidence_score": 0.0-1.0,
                    "success_indicators": ["list", "of", "indicators"],
                    "failure_indicators": ["list", "of", "indicators"],
                    "recommendations": ["list", "of", "recommendations"]
                }}
            ]
        }}
        """

        return prompt

    def _parse_analysis_result(self, result: Any, group_type: str) -> List[LearningPattern]:
        """Parse analysis result to extract patterns.

        Args:
            result: Analysis result from learning agent
            group_type: Type of interaction group

        Returns:
            List of parsed patterns
        """
        patterns = []

        try:
            # Extract content from result
            content = ""
            if hasattr(result, 'final_output'):
                content = result.final_output
            elif hasattr(result, 'content'):
                content = result.content
            else:
                content = str(result)

            # Try to parse JSON from content
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                analysis_data = json.loads(json_match.group())

                for pattern_data in analysis_data.get('patterns', []):
                    # Create pattern ID
                    pattern_content = f"{group_type}_{pattern_data['description']}"
                    pattern_id = hashlib.md5(pattern_content.encode()).hexdigest()[:16]

                    # Check if pattern already exists
                    if pattern_id in self.learning_patterns:
                        existing_pattern = self.learning_patterns[pattern_id]
                        # Update existing pattern
                        existing_pattern.usage_count += 1
                        existing_pattern.last_updated = datetime.now()
                        # Update success rate based on new data
                        existing_pattern.success_rate = (
                            (existing_pattern.success_rate * (existing_pattern.usage_count - 1)) +
                            pattern_data.get('confidence_score', 0.5)
                        ) / existing_pattern.usage_count
                    else:
                        # Create new pattern
                        pattern = LearningPattern(
                            pattern_id=pattern_id,
                            pattern_type=pattern_data.get('type', group_type),
                            description=pattern_data['description'],
                            confidence_score=pattern_data.get('confidence_score', 0.5),
                            success_rate=pattern_data.get('confidence_score', 0.5),
                            usage_count=1,
                            last_updated=datetime.now(),
                            metadata={
                                'source_group': group_type,
                                'success_indicators': pattern_data.get('success_indicators', []),
                                'failure_indicators': pattern_data.get('failure_indicators', []),
                                'recommendations': pattern_data.get('recommendations', [])
                            }
                        )
                        patterns.append(pattern)

        except Exception as e:
            print(f"Error parsing analysis result: {e}")

        return patterns

    def _validate_pattern(self, pattern: LearningPattern) -> bool:
        """Validate a learning pattern.

        Args:
            pattern: Pattern to validate

        Returns:
            bool: True if pattern is valid
        """
        # Check confidence threshold
        if pattern.confidence_score < self.learning_config['min_confidence_threshold']:
            return False

        # Check for duplicate patterns
        for existing_pattern in self.learning_patterns.values():
            if self._calculate_pattern_similarity(pattern, existing_pattern) > self.learning_config['pattern_similarity_threshold']:
                return False  # Too similar to existing pattern

        return True

    def _calculate_pattern_similarity(self, pattern1: LearningPattern, pattern2: LearningPattern) -> float:
        """Calculate similarity between two patterns.

        Args:
            pattern1: First pattern
            pattern2: Second pattern

        Returns:
            Similarity score (0.0-1.0)
        """
        # Simple similarity based on description overlap
        desc1_words = set(pattern1.description.lower().split())
        desc2_words = set(pattern2.description.lower().split())

        if not desc1_words or not desc2_words:
            return 0.0

        intersection = desc1_words.intersection(desc2_words)
        union = desc1_words.union(desc2_words)

        return len(intersection) / len(union)

    def get_relevant_patterns(self, context: str, limit: int = 5) -> List[LearningPattern]:
        """Get patterns relevant to a given context.

        Args:
            context: Context description
            limit: Maximum number of patterns to return

        Returns:
            List of relevant patterns
        """
        # Simple relevance scoring based on keyword matching
        context_words = set(context.lower().split())
        pattern_scores = []

        for pattern in self.learning_patterns.values():
            pattern_words = set(pattern.description.lower().split())
            relevance_score = len(context_words.intersection(pattern_words))

            if relevance_score > 0:
                pattern_scores.append((pattern, relevance_score))

        # Sort by relevance and confidence
        pattern_scores.sort(key=lambda x: (x[1], x[0].confidence_score), reverse=True)

        return [pattern for pattern, score in pattern_scores[:limit]]

    def add_feedback(self, session_id: str, feedback_data: Dict[str, Any]) -> None:
        """Add feedback to a learning session.

        Args:
            session_id: The session ID
            feedback_data: Feedback data
        """
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.feedback_received.append({
                **feedback_data,
                'timestamp': datetime.now().isoformat()
            })

    async def update_models_with_learned_patterns(self) -> None:
        """Update AI models with newly learned patterns."""
        if not self.learning_config['auto_update_models']:
            return

        # This would integrate with model fine-tuning systems
        # For now, just log the intent
        print(f"Model update triggered with {len(self.learning_patterns)} patterns")

        # TODO: Implement actual model fine-tuning integration
        # This could involve:
        # 1. Creating fine-tuning datasets from patterns
        # 2. Triggering model updates via external services
        # 3. Updating model configurations

    def get_learning_stats(self) -> Dict[str, Any]:
        """Get statistics about the learning system.

        Returns:
            Dict with learning statistics
        """
        total_patterns = len(self.learning_patterns)
        avg_confidence = sum(p.confidence_score for p in self.learning_patterns.values()) / max(total_patterns, 1)
        avg_success_rate = sum(p.success_rate for p in self.learning_patterns.values()) / max(total_patterns, 1)

        pattern_types = {}
        for pattern in self.learning_patterns.values():
            pattern_type = pattern.pattern_type
            pattern_types[pattern_type] = pattern_types.get(pattern_type, 0) + 1

        return {
            'total_patterns': total_patterns,
            'average_confidence': round(avg_confidence, 3),
            'average_success_rate': round(avg_success_rate, 3),
            'pattern_types': pattern_types,
            'active_sessions': len(self.active_sessions),
            'last_updated': datetime.now().isoformat()
        }


# Global learning engine instance
_learning_engine: Optional[ContinuousLearningEngine] = None


def get_learning_engine() -> ContinuousLearningEngine:
    """Get the global learning engine instance."""
    global _learning_engine
    if _learning_engine is None:
        _learning_engine = ContinuousLearningEngine()
    return _learning_engine


async def initialize_continuous_learning() -> None:
    """Initialize the continuous learning system."""
    engine = get_learning_engine()
    print("✓ Continuous learning system initialized")
    print(f"  - Loaded {len(engine.learning_patterns)} existing patterns")
    print(f"  - Learning interval: {engine.learning_config['learning_interval_minutes']} minutes")


def start_background_learning() -> None:
    """Start background learning tasks."""
    async def background_learning_loop():
        """Background loop for continuous learning tasks."""
        engine = get_learning_engine()

        while True:
            try:
                # Analyze completed sessions
                sessions_to_analyze = [
                    session_id for session_id, session in engine.active_sessions.items()
                    if (datetime.now() - session.start_time) > timedelta(minutes=5)
                ]

                for session_id in sessions_to_analyze:
                    await engine.analyze_session_patterns(session_id)
                    # Remove old sessions to prevent memory buildup
                    if (datetime.now() - engine.active_sessions[session_id].start_time) > timedelta(hours=1):
                        del engine.active_sessions[session_id]

                # Periodic model updates
                await engine.update_models_with_learned_patterns()

                # Wait for next learning cycle
                await asyncio.sleep(engine.learning_config['learning_interval_minutes'] * 60)

            except Exception as e:
                print(f"Error in background learning: {e}")
                await asyncio.sleep(60)  # Wait before retrying

    # Start background task
    asyncio.create_task(background_learning_loop())