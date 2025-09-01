"""
Module for displaying the CAI banner and welcome message.
"""
# Standard library imports
import os
import glob
import logging
import sys
from configparser import ConfigParser

# Third-party imports
import requests  # pylint: disable=import-error
from rich.console import Console  # pylint: disable=import-error
from rich.panel import Panel  # pylint: disable=import-error
from rich.table import Table  # pylint: disable=import-error

# For reading TOML files
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        # If tomli is not available, we'll handle it in the get_version function
        pass


def get_version():
    """Get the CAI version from pyproject.toml."""
    version = "unknown"
    try:
        # Determine which TOML parser to use
        if sys.version_info >= (3, 11):
            toml_parser = tomllib
        else:
            try:
                import tomli as toml_parser
            except ImportError:
                logging.warning("Could not import tomli. Falling back to manual parsing.")
                # Simple manual parsing for version only
                with open('pyproject.toml', 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip().startswith('version = '):
                            # Extract version from line like 'version = "0.4.0"'
                            version = line.split('=')[1].strip().strip('"\'')
                            return version
                return version
                
        # Use proper TOML parser if available
        with open('pyproject.toml', 'rb') as f:
            config = toml_parser.load(f)
        version = config.get('project', {}).get('version', 'unknown')
    except Exception as e:  # pylint: disable=broad-except
        logging.warning("Could not read version from pyproject.toml: %s", e)
    return version


def get_supported_models_count():
    """Get the count of supported models (with function calling)."""
    try:
        # Fetch model data from LiteLLM repository
        response = requests.get(
            "https://raw.githubusercontent.com/BerriAI/litellm/main/"
            "model_prices_and_context_window.json",
            timeout=2
        )

        if response.status_code == 200:
            model_data = response.json()

            # Count models with function calling support
            function_calling_models = sum(
                1 for model_info in model_data.values()
                if model_info.get("supports_function_calling", False)
            )

            # Try to get Ollama models count
            try:
                ollama_api_base = os.getenv(
                    "OLLAMA_API_BASE",
                    "http://host.docker.internal:8000/v1"
                )
                ollama_response = requests.get(
                    f"{ollama_api_base.replace('/v1', '')}/api/tags",
                    timeout=1
                )

                if ollama_response.status_code == 200:
                    ollama_data = ollama_response.json()
                    ollama_models = len(
                        ollama_data.get(
                            'models', ollama_data.get('items', [])
                        )
                    )
                    return function_calling_models + ollama_models
            except Exception:  # pylint: disable=broad-except
                logging.debug("Could not fetch Ollama models")
                # Continue without Ollama models

            return function_calling_models
    except Exception:  # pylint: disable=broad-except
        logging.warning("Could not fetch model data from LiteLLM")

    # Default count if we can't fetch the data
    return "many"


def count_tools():
    """Count the number of tools in the CAI framework."""
    try:
        # Count Python files in the tools directory
        tool_files = glob.glob("cai/tools/**/*.py", recursive=True)
        # Exclude __init__.py and other non-tool files
        tool_files = [
            f for f in tool_files
            if not f.endswith("__init__.py") and not f.endswith("__pycache__")
        ]
        return len(tool_files)
    except Exception:  # pylint: disable=broad-except
        logging.warning("Could not count tools")
        return "50+"


def count_agents():
    """Count the number of agents in the CAI framework."""
    try:
        # Count Python files in the agents directory
        agent_files = glob.glob("cai/agents/**/*.py", recursive=True)
        # Exclude __init__.py and other non-agent files
        agent_files = [
            f for f in agent_files
            if not f.endswith("__init__.py") and not f.endswith("__pycache__")
        ]
        return len(agent_files)
    except Exception:  # pylint: disable=broad-except
        logging.warning("Could not count agents")
        return "20+"


def count_ctf_memories():
    """Count the number of CTF memories in the CAI framework."""
    # This is a placeholder - adjust the actual counting logic based on your
    # framework structure
    return "100+"


def display_banner(console: Console):
    """
    Display a stylized NAPOLEON banner with French imperial colors.

    Args:
        console: Rich console for output
    """
    version = get_version()

    # Napoleon banner with French imperial colors (gold and blue)
    # Use noqa to ignore line length for the ASCII art
    banner = f"""
[bold yellow]═══════════════════════════════════════════════════════════════════════════════════[/bold yellow]
[bold yellow]                                    NAPOLEON[/bold yellow]
[bold white]                          Advanced Cybersecurity AI Framework[/bold white]
[bold yellow]═══════════════════════════════════════════════════════════════════════════════════[/bold yellow]

[bold gold1]       ███╗   ██╗ █████╗ ██████╗  ██████╗ ██╗     ███████╗ ██████╗ ███╗   ██╗[/bold gold1]
[bold gold1]       ████╗  ██║██╔══██╗██╔══██╗██╔═══██╗██║     ██╔════╝██╔═══██╗████╗  ██║[/bold gold1]
[bold gold1]       ██╔██╗ ██║███████║██████╔╝██║   ██║██║     █████╗  ██║   ██║██╔██╗ ██║[/bold gold1]
[bold gold1]       ██║╚██╗██║██╔══██║██╔═══╝ ██║   ██║██║     ██╔══╝  ██║   ██║██║╚██╗██║[/bold gold1]
[bold gold1]       ██║ ╚████║██║  ██║██║     ╚██████╔╝███████╗███████╗╚██████╔╝██║ ╚████║[/bold gold1]
[bold gold1]       ╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝      ╚═════╝ ╚══════╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝[/bold gold1]

[bold blue]                            EMPEROR OF CYBERSECURITY AI[/bold blue]
[bold white]                              Version {version} - ML Enhanced[/bold white]
[bold yellow]              Production-Ready • Machine Learning • Enterprise Grade[/bold yellow]

[bold gold1]┌─────────────────────────────────────────────────────────────────────────────┐[/bold gold1]
[bold gold1]│    Based on CAI Framework + Advanced ML Engine + Production Infrastructure  │[/bold gold1]
[bold gold1]│    4 ML Algorithms • 43 Features • Real-time Predictions • Auto-learning   │[/bold gold1]
[bold gold1]│    Docker Ready • Kubernetes Support • Enterprise Monitoring • HA Deploy   │[/bold gold1]
[bold gold1]│    Parallel Execution • Session Management • Performance Optimized        │[/bold gold1]
[bold gold1]└─────────────────────────────────────────────────────────────────────────────┘[/bold gold1]    """

    console.print(banner, end="")

    # # Create a table showcasing CAI framework capabilities
    # #
    # # reconsider in the future if necessary
    # display_framework_capabilities(console)


def display_framework_capabilities(console: Console):
    """
    Display a table showcasing CAI framework capabilities in Metasploit style.

    Args:
        console: Rich console for output
    """
    # Create the main table
    table = Table(
        title="",
        box=None,
        show_header=False,
        show_edge=False,
        padding=(0, 2)
    )

    table.add_column("Category", style="bold cyan")
    table.add_column("Count", style="bold yellow")
    table.add_column("Description", style="white")

    # Add rows for different capabilities
    table.add_row(
        "AI Models",
        str(get_supported_models_count()),
        "Supported AI models including GPT-4, Claude, Llama"
    )

    # table.add_row(
    #     "Tools",
    #     str(count_tools()),
    #     "Cybersecurity tools for reconnaissance and scanning"
    # )

    table.add_row(
        "Agents",
        str(count_agents()),
        "Specialized AI agents for different cybersecurity tasks"
    )

    # Add the table to a panel for better visual separation
    capabilities_panel = Panel(
        table,
        title="[bold blue]CAI Features[/bold blue]",
        border_style="blue",
        padding=(1, 2)
    )

    console.print(capabilities_panel)


def display_welcome_tips(console: Console):
    """
    Display welcome message with tips for using the REPL.

    Args:
        console: Rich console for output
    """
    console.print(Panel(
        "[white]• Use arrow keys ↑↓ to navigate command history[/white]\n"
        "[white]• Press Tab for command completion[/white]\n"
        "[white]• Type /help for available commands[/white]\n"
        "[white]• Type /help aliases for command shortcuts[/white]\n"
        "[white]• Press Ctrl+L to clear the screen[/white]\n"
        "[white]• Press Esc+Enter to add a new line (multiline input)[/white]\n"
        "[white]• Press Ctrl+C to exit[/white]",
        title="Quick Tips",
        border_style="blue"
    ))


def display_agent_overview(console: Console):
    """
    Display a quick overview of available agents.
    
    Args:
        console: Rich console for output
    """
    from rich.table import Table
    
    # Create agents table
    agents_table = Table(
        title="",
        box=None,
        show_header=True,
        header_style="bold yellow",
        show_edge=False,
        padding=(0, 1)
    )
    
    agents_table.add_column("Agent", style="cyan", width=25)
    agents_table.add_column("Specialization", style="white")
    agents_table.add_column("Best For", style="green")
    
    # Add agent rows
    agents = [
        ("one_tool_agent", "Basic CTF solver", "CTF challenges, Linux operations"),
        ("red_teamer", "Offensive security", "Penetration testing, exploitation"),
        ("blue_teamer", "Defensive security", "System defense, monitoring"),
        ("bug_bounter", "Bug bounty hunter", "Web security, API testing"),
        ("dfir", "Digital forensics", "Incident response, analysis"),
        ("network_traffic_analyzer", "Network security", "Traffic analysis, monitoring"),
        ("flag_discriminator", "CTF flag extraction", "Finding and validating flags"),
        ("codeagent", "Code specialist", "Exploit development, analysis"),
        ("thought", "Strategic planning", "High-level analysis, planning"),
    ]
    
    for agent, spec, best_for in agents:
        agents_table.add_row(agent, spec, best_for)
    
    # Create the panel
    agent_panel = Panel(
        agents_table,
        title="[bold yellow]🤖 Available Security Agents[/bold yellow]",
        border_style="yellow",
        padding=(1, 2),
        title_align="center"
    )
    
    console.print(agent_panel)


def display_quick_guide(console: Console):
    """Display the quick guide with comprehensive command reference."""
    # Display help panel instead
    from rich.panel import Panel
    from rich.text import Text
    from rich.columns import Columns
    from rich.console import Group  # <-- Fix: import Group

    help_text = Text.assemble(
        ("⚔️ NAPOLEON COMMAND ARSENAL ⚔️", "bold gold1 underline"), "\n\n",
        ("═══════════════════════════════════════════════════════════════", "gold1"), "\n",
        ("🏛️ IMPERIAL AGENT COMMAND", "bold yellow"), " (/agent)\n",
        ("  NAPOLEON>/agent list", "green"), " - Display your cyber legions\n",
        ("  NAPOLEON>/agent deploy [NAME]", "green"), " - Deploy specialist agent\n",
        ("  NAPOLEON>/agent status [NAME]", "green"), " - Agent battle readiness\n",
        ("  NAPOLEON>/parallel deploy [NAME]", "green"), " - Multi-front operations\n\n",
        
        ("🧠 IMPERIAL INTELLIGENCE", "bold yellow"), "\n",
        ("  NAPOLEON>/memory scan", "green"), " - Review intelligence archives\n",
        ("  NAPOLEON>/history", "green"), " - Campaign battle logs\n",
        ("  NAPOLEON>/analyze", "green"), " - Strategic AI analysis\n",
        ("  NAPOLEON>/purge", "green"), " - Clear operational history\n\n",
        
        ("🏰 BATTLEFIELD CONTROL", "bold yellow"), "\n",
        ("  NAPOLEON>/fortress set [NAME]", "green"), " - Establish command center\n",
        ("  NAPOLEON>/arsenal", "green"), " - Configure weapons cache\n",
        ("  NAPOLEON>/deploy container [IMAGE]", "green"), " - Launch siege engines\n\n",
        
        ("⚡ STRATEGIC OPERATIONS", "bold yellow"), "\n",
        ("  NAPOLEON>/artillery load [TYPE]", "green"), " - Deploy heavy weapons\n",
        ("  NAPOLEON>/execute [COMMAND]", "green"), " or $ - Direct assault\n",
        ("  NAPOLEON>/model [NAME]", "green"), " - Select battle strategy\n\n",
        
        ("🎯 EMPEROR'S SHORTCUTS", "bold yellow"), "\n",
        ("  ESC + ENTER", "green"), " - Multi-line battle orders\n",
        ("  TAB", "green"), " - Strategic completion\n",
        ("  ↑/↓", "green"), " - Command history recall\n",
        ("  Ctrl+C", "green"), " - Strategic retreat\n",
        ("═══════════════════════════════════════════════════════════════", "gold1"), "\n",
    )
    
    # Get current environment variable values
    current_model = os.getenv('CAI_MODEL', "alias0")
    current_agent_type = os.getenv('CAI_AGENT_TYPE', "one_tool_agent")
    
    config_text = Text.assemble(
        ("🏆 IMPERIAL CAMPAIGNS 🏆", "bold gold1 underline"), "\n\n",
        ("⚔️ SIEGE OF FORTRESSES (CTF)", "bold yellow"), "\n",
        ("  1. NAPOLEON> /agent deploy redteam_agent", "green"), "\n",
        ("  2. NAPOLEON> /fortress set challenge_name", "green"), "\n",
        ("  3. NAPOLEON> Commence the siege...", "green"), "\n\n",
        
        ("💰 BOUNTY CAMPAIGN", "bold yellow"), "\n",
        ("  1. NAPOLEON> /agent deploy bug_bounter_agent", "green"), "\n",
        ("  2. NAPOLEON> /model alias0", "green"), "\n",
        ("  3. NAPOLEON> Assault target.com", "green"), "\n\n",
        
        ("Napoleon advances cybersecurity through strategic AI.\n"
         "Your digital sovereignty is protected with enterprise security.\n"
         "Glory awaits - press Enter to conquer, Ctrl-C to retreat.", "gold1"), "\n\n",
        
        ("🔭 BLITZKRIEG RECONNAISSANCE", "bold yellow"), "\n",
        ("  1. NAPOLEON> /parallel deploy red_teamer", "green"), "\n",
        ("  2. NAPOLEON> /parallel deploy network_analyzer", "green"), "\n",
        ("  3. NAPOLEON> Scan enemy territory 192.168.1.0/24", "green"), "\n\n",
        
        ("🛡️ ADVANCED WEAPONRY", "bold yellow"), "\n",
        ("  1. NAPOLEON> /artillery load mcp http://localhost:3000", "green"), "\n",
        ("  2. NAPOLEON> /artillery deploy server_name", "green"), "\n",
        ("  3. NAPOLEON> Unleash the weapons...", "green"), "\n\n",
        
        ("Imperial Configuration:", "bold yellow"), "\n",
        ("  NAPOLEON_MODEL", "green"), f" = {current_model}\n",
        ("  NAPOLEON_AGENT", "green"), f" = {current_agent_type}\n",
        ("  NAPOLEON_LEGIONS", "green"), f" = {os.getenv('CAI_PARALLEL', '1')}\n",
        ("  NAPOLEON_STREAM", "green"), f" = {os.getenv('CAI_STREAM', 'true')}\n",
        ("  NAPOLEON_COMMAND_CENTER", "green"), f" = {os.getenv('CAI_WORKSPACE', 'default')}\n\n",
        
        ("🎖️ EMPEROR'S WISDOM:", "bold yellow"), "\n",
        ("• Use /help for strategic intel\n", "dim"),
        ("• Use /help campaigns for battle plans\n", "dim"),
        ("• Use /help arsenal for weapon specs\n", "dim"),
        ("• Use $ prefix for direct commands: $ ls\n", "dim"),
    )
    
    # Create additional tips panels
    ollama_tip = Panel(
        "To use Ollama models, configure OLLAMA_API_BASE\n"
        "before startup.\n\n"
        "Default: host.docker.internal:8000/v1",
        title="[bold yellow]Ollama Configuration[/bold yellow]",
        border_style="yellow",
        padding=(1, 2),
        title_align="center"
    )
    
    # Simplified privacy notice
    privacy_notice = Text.assemble(
        ("CAI collects pseudonymized data to improve our research.\n"
         "Your privacy is protected in compliance with GDPR.\n"
         "Continue to start, or press Ctrl-C to exit.", "yellow"), "\n\n",
    )
    
    context_tip = Panel(
        Text.assemble(
            ("NAPOLEON - Advanced Cybersecurity AI Framework\n\n", "bold gold1"),
            "Production-ready cybersecurity AI with:\n\n", 
            "• Advanced Machine Learning Engine\n",
            "• Real-time threat analysis\n",
            "• Enterprise-grade security\n",
            "• Multi-agent orchestration\n",
            "• Docker & Kubernetes ready\n\n",
            "Developed by Manuel Guilherme (@Galmanus)\n",
            "Based on CAI Framework by Alias Robotics"
        ),
        title="[bold gold1]🏛️ NAPOLEON Framework [/bold gold1]",
        border_style="gold1",
        padding=(1, 2),
        title_align="center"
    )
    # Combine tips into a group
    # tips_group = Group(ollama_tip, context_tip, privacy_notice)
    tips_group = Group(context_tip)
    
    # Create a three-column panel layout
    console.print(Panel(
        Columns(
            [help_text, config_text, tips_group],
            column_first=True,
            expand=True,
            align="center"
        ),
        title="[bold]🔱 NAPOLEON - Advanced Cybersecurity AI Framework - Type /help for detailed documentation 🔱[/bold]",
        border_style="gold1",
        padding=(1, 2),
        title_align="center"
    ), end="")
