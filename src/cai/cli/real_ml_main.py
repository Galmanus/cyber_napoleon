"""
CAI CLI with REAL MACHINE LEARNING

This version integrates actual ML algorithms with the CAI CLI,
replacing the fake LLM-based "continuous learning" with real machine learning.
"""

import os
import asyncio
import time
from typing import Optional
from datetime import datetime

# Import CAI components
from cai.agents import get_agent_by_name
from cai.repl.commands import FuzzyCommandCompleter
from cai.repl.ui.logging import setup_session_logging
from cai.util import (
    start_active_timer,
    stop_active_timer,
    start_idle_timer,
    stop_idle_timer,
    validate_and_warn
)

# Import REAL ML system
from .real_ml_integration import (
    initialize_real_ml_integration,
    get_ml_integration,
    ml_hook_session_start,
    ml_hook_session_end,
    ml_hook_before_agent_run,
    ml_hook_after_agent_run
)
from .enhanced_agent_runner import EnhancedAgentRunner
from .warning_suppressor import setup_warning_suppression


class RealMLAgentRunner:
    """Agent runner with REAL machine learning integration."""
    
    def __init__(self, console):
        """Initialize ML-enhanced agent runner."""
        self.console = console
        self.ml_integration = get_ml_integration()
    
    async def run_agent_with_ml(self, agent, user_input: str, context: str = "general"):
        """Run agent with ML prediction and learning."""
        
        # STEP 1: Get ML prediction before execution
        prediction = await ml_hook_before_agent_run(agent, user_input, context)
        
        if prediction and prediction.get('prediction') != 'unknown':
            self.console.print(f"🤖 [bold cyan]ML Prediction:[/bold cyan] {prediction['prediction']}")
            self.console.print(f"🎯 [bold yellow]Confidence:[/bold yellow] {prediction['confidence']:.2f}")
            if prediction.get('advice'):
                self.console.print(f"💡 [bold green]AI Advice:[/bold green] {prediction['advice']}")
            self.console.print()
        
        # STEP 2: Execute agent
        start_time = time.time()
        
        try:
            # Build conversation context
            history_context = []
            if hasattr(agent, 'model') and hasattr(agent.model, 'message_history'):
                history_context.extend(agent.model.message_history)
            
            history_context.append({"role": "user", "content": user_input})
            
            # Run agent
            from cai.sdk.agents import Runner
            result = await Runner.run(agent, history_context)
            
            execution_time = time.time() - start_time
            
            # Extract tools used (if any)
            tools_used = []
            if hasattr(result, 'messages'):
                for msg in result.messages:
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        for tool_call in msg.tool_calls:
                            tools_used.append(tool_call.function.name)
            
            # STEP 3: Record interaction for ML learning
            await ml_hook_after_agent_run(
                agent=agent,
                user_input=user_input,
                response=result,
                execution_time=execution_time,
                tools_used=tools_used,
                context=context
            )
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Record failed interaction
            await ml_hook_after_agent_run(
                agent=agent,
                user_input=user_input,
                response=f"Error: {str(e)}",
                execution_time=execution_time,
                tools_used=[],
                context=context
            )
            
            raise e


async def run_cai_with_real_ml(
    starting_agent,
    context_variables=None,
    max_turns=float("inf"),
    force_until_flag=False,
    initial_prompt: Optional[str] = None,
    prompt_file: Optional[str] = None,
):
    """
    Run CAI with REAL machine learning integration.
    """
    # Initialize REAL ML system
    print("🤖 Initializing REAL Machine Learning system...")
    
    await initialize_real_ml_integration()
    ml_integration = get_ml_integration()
    
    print("✅ Real ML system ready!")
    
    # Start ML session
    session_id = f"real_ml_session_{int(time.time())}"
    ml_hook_session_start(session_id)
    print(f"🧠 Started Real ML session: {session_id}")
    
    # Create ML-enhanced agent runner
    from rich.console import Console
    console = Console()
    ml_runner = RealMLAgentRunner(console)
    
    # Display ML status
    ml_status = ml_integration.get_ml_status()
    print(f"📊 ML Status:")
    print(f"  • Models trained: {ml_status['models_trained']}")
    print(f"  • Training samples: {ml_status['training_samples']}")
    print(f"  • Model version: {ml_status['model_version']}")
    
    print("\n🚀 Starting CAI with REAL Machine Learning...\n")
    
    try:
        # Handle non-interactive mode
        if initial_prompt or prompt_file:
            await _handle_ml_non_interactive_mode(
                initial_prompt, prompt_file, starting_agent, ml_runner
            )
            return
        
        # Interactive mode with ML
        print("💬 [bold blue]Interactive Mode with Real ML[/bold blue]")
        print("💡 Type your cybersecurity queries and get ML-powered insights!")
        print("🔧 Use '/ml status' to see ML statistics")
        print("🏋️ Use '/ml train' to trigger model training")
        print("🔮 Use '/ml predict <query>' to get ML predictions")
        print()
        
        turn_count = 0
        
        while turn_count < max_turns:
            try:
                # Get user input
                user_input = input("🔥 CAI+ML> ")
                
                if not user_input.strip():
                    continue
                
                # Handle ML commands
                if user_input.startswith('/ml '):
                    await _handle_ml_commands(user_input, ml_integration, console)
                    continue
                
                # Handle exit
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    break
                
                # Start timing
                stop_idle_timer()
                start_active_timer()
                
                try:
                    # Run agent with ML integration
                    await ml_runner.run_agent_with_ml(
                        starting_agent,
                        user_input,
                        context="interactive_cybersecurity"
                    )
                    
                    turn_count += 1
                    
                except KeyboardInterrupt:
                    print("\n👋 Session interrupted")
                    break
                    
                except Exception as e:
                    print(f"❌ Error: {e}")
                    
                finally:
                    stop_active_timer()
                    start_idle_timer()
                    
            except KeyboardInterrupt:
                print("\n👋 Exiting CAI with Real ML")
                break
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # End ML session and get results
        print("\n🔍 Analyzing ML session results...")
        
        try:
            ml_results = await ml_hook_session_end()
            
            if ml_results:
                print("🎯 Real ML Results:")
                print(f"  • Session ID: {ml_results.get('session_id', 'N/A')}")
                print(f"  • Interactions recorded: {ml_results.get('interactions_recorded', 0)}")
                print(f"  • Training triggered: {'Yes' if ml_results.get('training_triggered') else 'No'}")
                print(f"  • Total training samples: {ml_results.get('total_training_samples', 0)}")
                print(f"  • Models trained: {'Yes' if ml_results.get('models_trained') else 'No'}")
                
                if ml_results.get('training_triggered'):
                    print("\n🏆 Models were retrained with new data!")
                
        except Exception as e:
            print(f"⚠️ Error analyzing ML results: {e}")
        
        # Final ML statistics
        try:
            final_status = ml_integration.get_ml_status()
            print(f"\n📈 Final ML Statistics:")
            print(f"  • Total training samples: {final_status['training_samples']}")
            print(f"  • Models trained: {final_status['models_trained']}")
            print(f"  • Predictions made: {final_status['predictions_made']}")
            if final_status['predictions_made'] > 0:
                print(f"  • Prediction accuracy: {final_status['prediction_accuracy']:.2f}")
            
        except Exception as e:
            print(f"⚠️ Error getting final statistics: {e}")


async def _handle_ml_non_interactive_mode(
    initial_prompt: Optional[str],
    prompt_file: Optional[str], 
    agent,
    ml_runner
):
    """Handle non-interactive mode with ML integration."""
    prompts = []
    
    if initial_prompt:
        prompts.append(initial_prompt)
    
    if prompt_file:
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompts.extend([line.strip() for line in f if line.strip()])
        except FileNotFoundError:
            print(f"❌ Error: Prompt file not found: {prompt_file}")
            return
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\n🔥 Running prompt {i}/{len(prompts)}: {prompt}")
        
        try:
            await ml_runner.run_agent_with_ml(
                agent,
                prompt,
                context="non_interactive_cybersecurity"
            )
        except Exception as e:
            print(f"❌ Error processing prompt {i}: {e}")


async def _handle_ml_commands(user_input: str, ml_integration, console):
    """Handle ML-specific commands."""
    command = user_input[4:].strip()  # Remove '/ml '
    
    if command == 'status':
        status = ml_integration.get_ml_status()
        console.print("\n📊 [bold cyan]Real ML System Status[/bold cyan]")
        console.print(f"  • Enabled: {'✅' if status['enabled'] else '❌'}")
        console.print(f"  • Models trained: {'✅' if status['models_trained'] else '❌'}")
        console.print(f"  • Training samples: {status['training_samples']}")
        console.print(f"  • Model version: {status['model_version']}")
        console.print(f"  • Feature count: {status['feature_count']}")
        console.print(f"  • Predictions made: {status['predictions_made']}")
        if status['predictions_made'] > 0:
            console.print(f"  • Prediction accuracy: {status['prediction_accuracy']:.2f}")
        
        if status['model_performance']:
            console.print("  • Model Performance:")
            for model_name, perf in status['model_performance'].items():
                if 'accuracy' in perf:
                    console.print(f"    - {model_name}: {perf['accuracy']:.3f}")
    
    elif command == 'train':
        console.print("🏋️ Training ML models...")
        results = await ml_integration.train_models()
        if results.get('training_completed'):
            console.print("✅ Training completed!")
            for model_name, perf in results.get('performance', {}).items():
                if 'accuracy' in perf:
                    console.print(f"  • {model_name}: {perf['accuracy']:.3f} accuracy")
        else:
            console.print("❌ Training failed or no data available")
    
    elif command == 'optimize':
        console.print("🔧 Optimizing model hyperparameters...")
        results = await ml_integration.optimize_models()
        if results:
            console.print("✅ Optimization completed!")
            for model_name, result in results.items():
                console.print(f"  • {model_name}: {result['best_score']:.3f} best score")
    
    elif command.startswith('predict '):
        query = command[8:]  # Remove 'predict '
        if query:
            prediction_data = {
                'user_input': query,
                'context': 'command_prediction',
                'timestamp': datetime.now().isoformat()
            }
            
            prediction = await ml_integration.predict_outcome(prediction_data)
            console.print(f"\n🔮 [bold cyan]ML Prediction for: '{query}'[/bold cyan]")
            console.print(f"  • Prediction: {prediction['prediction']}")
            console.print(f"  • Confidence: {prediction['confidence']:.2f}")
            if prediction.get('advice'):
                console.print(f"  • Advice: {prediction['advice']}")
        else:
            console.print("❌ Please provide a query to predict")
    
    elif command == 'insights':
        insights = await ml_integration.get_ml_insights("general_cybersecurity")
        console.print("\n💡 [bold cyan]ML Insights[/bold cyan]")
        for insight in insights.get('insights', []):
            console.print(f"  • {insight['title']}: {insight.get('data', '')}")
    
    else:
        console.print("❌ Unknown ML command. Available: status, train, optimize, predict <query>, insights")


async def main_real_ml():
    """Main function with real machine learning."""
    # Setup warning suppression
    setup_warning_suppression()
    
    # Validate configuration
    config_valid, validated_config = validate_and_warn()
    if not config_valid:
        from cai.util import color
        print(color("Configuration errors found. Please check your environment variables.", fg="red"))
        return
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="CAI with REAL Machine Learning")
    parser.add_argument("--prompt", type=str, help="Run with a single prompt (non-interactive)")
    parser.add_argument("--file", type=str, help="Run with prompts from file (non-interactive)")
    parser.add_argument("--no-ml", action="store_true", help="Disable machine learning")
    
    cli_args = parser.parse_args()
    
    # Check if ML should be disabled
    if cli_args.no_ml:
        print("🚫 Machine Learning disabled for this session")
        from cai.cli.main import main_async_refactored
        await main_async_refactored()
        return
    
    # Get agent
    agent_type = validated_config.get('agent_type', 'one_tool_agent')
    agent = get_agent_by_name(agent_type, agent_id="P1")
    
    # Configure agent
    if hasattr(agent, "model"):
        if hasattr(agent.model, "disable_rich_streaming"):
            agent.model.disable_rich_streaming = True
        if hasattr(agent.model, "suppress_final_output"):
            agent.model.suppress_final_output = False
    
    # Update agent model
    current_model = os.getenv("CAI_MODEL", "alias0")
    if hasattr(agent, "model"):
        from cai.cli.agent_runner import AgentRunner
        runner = AgentRunner(console=None)
        runner._update_agent_models_recursively(agent, current_model)
    
    # Run CAI with REAL ML
    await run_cai_with_real_ml(
        agent,
        initial_prompt=cli_args.prompt,
        prompt_file=cli_args.file
    )


def main_with_real_ml():
    """Main entry point with REAL machine learning."""
    # Create event loop with proper cleanup
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Run main async function
        loop.run_until_complete(main_real_ml())
    except KeyboardInterrupt:
        print("\n👋 CAI with Real ML terminated")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean shutdown
        try:
            # Cancel all tasks
            pending = asyncio.all_tasks(loop)
            if pending:
                for task in pending:
                    try:
                        task.cancel()
                    except Exception:
                        pass
                
                # Wait for cancellation with timeout
                try:
                    loop.run_until_complete(
                        asyncio.wait_for(
                            asyncio.gather(*pending, return_exceptions=True),
                            timeout=2.0
                        )
                    )
                except (asyncio.TimeoutError, Exception):
                    pass
                    
        except Exception:
            pass
        finally:
            # Close loop
            try:
                loop.close()
            except Exception:
                pass


if __name__ == "__main__":
    main_with_real_ml()
