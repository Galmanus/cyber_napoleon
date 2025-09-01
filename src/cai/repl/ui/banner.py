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
    Display a stylized CAI banner with Alias Robotics corporate colors.

    Args:
        console: Rich console for output
    """
    version = get_version()

    # Epic Cyber Napoleon banner with French Imperial colors (gold and blue)
    # Perfectly centered and elegant ASCII art
    banner = f"""
[bold gold]                 ____      _                 _   _                   _                   
[bold gold]                / ___|   _| |__   ___ _ __  | \ | | __ _ _ __   ___ | | ___  ___  _ __   
[bold gold]               | |  | | | | '_ \ / _ \ '__| |  \| |/ _` | '_ \ / _ \| |/ _ \/ _ \| '_ \  
[bold gold]               | |__| |_| | |_) |  __/ |    | |\  | (_| | |_) | (_) | |  __/ (_) | | | | 
[bold gold]                \____\__, |_.__/ \___|_|    |_| \_|\__,_| .__/ \___/|_|\___|\___/|_| |_| 
[bold gold]                     |___/                              |_|                             

[bold blue]                           ⚔️  CYBER NAPOLEON v{version} ⚔️
[bold white]                      🏴‍☠️ Conquer the digital battlefield 🏴‍☠️
    """

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
        ("⚔️ CYBER NAPOLEON COMMAND ARSENAL ⚔️", "bold gold underline"), "\n\n",
        ("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", "dim"), "\n",
        ("🏛️ IMPERIAL AGENT COMMAND", "bold yellow"), " (/a)\n",
        ("  Napoleon>/agent list", "green"), " - Muster all available generals\n",
        ("  Napoleon>/agent select [NAME]", "green"), " - Appoint field commander\n",
        ("  Napoleon>/agent info [NAME]", "green"), " - Review general's dossier\n",
        ("  Napoleon>/parallel add [NAME]", "green"), " - Deploy multiple corps\n\n",
        
        ("📜 CAMPAIGN ARCHIVES", "bold yellow"), "\n",
        ("  Napoleon>/memory list", "green"), " - Review battle chronicles\n",
        ("  Napoleon>/history", "green"), " - Study campaign records\n",
        ("  Napoleon>/compact", "green"), " - Imperial intelligence summary\n",
        ("  Napoleon>/flush", "green"), " - Clear the war room\n\n",
        
        ("🏴‍☠️ BATTLEFIELD CONTROL", "bold yellow"), "\n",
        ("  Napoleon>/workspace set [NAME]", "green"), " - Establish command post\n",
        ("  Napoleon>/config", "green"), " - Adjust battle parameters\n",
        ("  Napoleon>/virt run [IMAGE]", "green"), " - Deploy siege engines\n\n",
        
        ("⚡ ARTILLERY & RECONNAISSANCE", "bold yellow"), "\n",
        ("  Napoleon>/mcp load [TYPE] [CONFIG]", "green"), " - Load siege weapons\n",
        ("  Napoleon>/shell [COMMAND]", "green"), " or $ - Execute field orders\n",
        ("  Napoleon>/model [NAME]", "green"), " - Choose war strategy\n\n",
        
        ("🗡️ TACTICAL MANEUVERS", "bold yellow"), "\n",
        ("  ESC + ENTER", "green"), " - Multi-line battle plans\n",
        ("  TAB", "green"), " - Command suggestions\n",
        ("  ↑/↓", "green"), " - Previous orders\n",
        ("  Ctrl+C", "green"), " - Strategic retreat\n",
        ("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", "dim"), "\n",
    )
    
    # Get current environment variable values
    current_model = os.getenv('CAI_MODEL', "alias0")
    current_agent_type = os.getenv('CAI_AGENT_TYPE', "one_tool_agent")
    
    config_text = Text.assemble(
        ("⚔️ IMPERIAL BATTLE STRATEGIES ⚔️", "bold gold underline"), "\n\n",
        ("🎯 Conquest Campaign", "bold yellow"), "\n",
        ("  1. Napoleon> /agent select redteam_agent", "green"), "\n",
        ("  2. Napoleon> /workspace set enemy_fortress", "green"), "\n",
        ("  3. Napoleon> Begin the digital siege...", "green"), "\n\n",
        
        ("🛡️ Bounty Warfare", "bold yellow"), "\n",
        ("  1. Napoleon> /agent select bug_bounter_agent", "green"), "\n",
        ("  2. Napoleon> /model claude-3-7-sonnet", "green"), "\n",
        ("  3. Napoleon> Attack https://enemy.com", "green"), "\n\n",
        
        ("The Emperor protects your data through imperial decree.\n"
         "Privacy secured by the Code Napoléon of cybersecurity.\n"
         "Advance to victory, or retreat with Ctrl-C.", "yellow"), "\n\n",
        
        ("🔍 Multi-Corps Reconnaissance", "bold yellow"), "\n",
        ("  1. Napoleon> /parallel add red_teamer", "green"), "\n",
        ("  2. Napoleon> /parallel add network_traffic_analyzer", "green"), "\n",
        ("  3. Napoleon> Scout enemy network 192.168.1.0/24", "green"), "\n\n",
        
        ("🏹 Artillery Integration", "bold yellow"), "\n",
        ("  1. Napoleon> /mcp load cannon http://localhost:3000", "green"), "\n",
        ("  2. Napoleon> /mcp add artillery_unit field_marshal", "green"), "\n",
        ("  3. Napoleon> Deploy the war machines...", "green"), "\n\n",
        
        ("Environment Variables:", "bold yellow"), "\n",
        ("  CAI_MODEL", "green"), f" = {current_model}\n",
        ("  CAI_AGENT_TYPE", "green"), f" = {current_agent_type}\n",
        ("  CAI_PARALLEL", "green"), f" = {os.getenv('CAI_PARALLEL', '1')}\n",
        ("  CAI_STREAM", "green"), f" = {os.getenv('CAI_STREAM', 'true')}\n",
        ("  CAI_WORKSPACE", "green"), f" = {os.getenv('CAI_WORKSPACE', 'default')}\n\n",
        
        ("💡 Pro Tips:", "bold yellow"), "\n",
        ("• Use /help for detailed command help\n", "dim"),
        ("• Use /help quick for this guide\n", "dim"),
        ("• Use /help commands for all commands\n", "dim"),
        ("• Use $ prefix for quick shell: $ ls\n", "dim"),
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
            ("🔒 Security-Focused AI Framework\n\n", "bold white"),
            "For optimal cybersecurity AI performance, use\n", 
            ("alias0", "bold green"), 
            " - specifically designed for cybersecurity\n"
            "tasks with superior domain knowledge.\n\n",
            ("alias0", "bold green"), 
            " outperforms general-purpose models in:\n",
            "• Vulnerability assessment\n",
            "• Penetration testing and bug bounty\n",
            "• Security analysis\n",
            "• Threat detection\n\n",
            "Learn more about ", 
            ("alias0", "bold green"), 
            " and its privacy-first approach:\n",
            ("https://news.aliasrobotics.com/alias0-a-privacy-first-cybersecurity-ai/", "blue underline")
        ),
        title="[bold yellow]🛡️ Alias0 - best model for cybersecurity [/bold yellow]",
        border_style="yellow",
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
        title="[bold]⚔️ CYBER NAPOLEON - AI-Powered Digital Warfare Framework - Type /help for battle commands ⚔️[/bold]",
        border_style="blue",
        padding=(1, 2),
        title_align="center"
    ), end="")
