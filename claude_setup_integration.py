#!/usr/bin/env python3
"""
Setup script for Claude Code integration with Archon.

This script helps verify that all prerequisites are met and
guides the user through the setup process for integrating
Claude Code with Archon.
"""

import os
import sys
import subprocess
import time
import json
import requests
from typing import Dict, Any, List, Optional, Tuple

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Configuration
ARCHON_SERVICE_URL = "http://localhost:8100"
STREAMLIT_URL = "http://localhost:8501"
ENV_FILE = ".env"
REQUIRED_PACKAGES = ["mcp", "requests", "dotenv"]

def print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== {text} ==={Colors.ENDC}\n")

def print_success(text: str) -> None:
    """Print a success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")

def print_error(text: str) -> None:
    """Print an error message."""
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")

def print_warning(text: str) -> None:
    """Print a warning message."""
    print(f"{Colors.YELLOW}! {text}{Colors.ENDC}")

def print_info(text: str) -> None:
    """Print an information message."""
    print(f"{Colors.BLUE}ℹ {text}{Colors.ENDC}")

def check_archon_running() -> bool:
    """Check if Archon graph service is running."""
    try:
        response = requests.get(f"{ARCHON_SERVICE_URL}/health", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def check_dependencies() -> List[str]:
    """Check if required Python packages are installed."""
    missing = []
    for package in REQUIRED_PACKAGES:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    return missing

def check_env_file() -> Tuple[bool, Dict[str, Any]]:
    """Check if .env file exists and has necessary variables."""
    env_vars = {}
    
    if not os.path.exists(ENV_FILE):
        return False, env_vars
    
    # Read .env file
    with open(ENV_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                try:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip().strip("'").strip('"')
                except ValueError:
                    continue
    
    return True, env_vars

def create_env_file(existing_vars: Dict[str, Any]) -> None:
    """Create or update .env file with necessary variables."""
    print_header("Environment Setup")
    
    # Required variables
    required_vars = {
        "LLM_API_KEY": "Your API key for the LLM (OpenAI, Anthropic, etc.)",
        "BASE_URL": "API base URL (default: https://api.openai.com/v1)",
        "PRIMARY_MODEL": "Main model to use (default: gpt-4o-mini)",
        "REASONER_MODEL": "Model for reasoning (default: o3-mini)",
        "GRAPH_SERVICE_URL": "URL for the Archon Graph Service (default: http://localhost:8100)",
        "SUPABASE_URL": "Your Supabase URL",
        "SUPABASE_SERVICE_KEY": "Your Supabase service key"
    }
    
    new_vars = {}
    
    # Ask user for missing or update existing variables
    for var, description in required_vars.items():
        default = existing_vars.get(var, "")
        if default:
            prompt = f"{var} [{default}]: "
        else:
            prompt = f"{var} ({description}): "
        
        value = input(prompt)
        new_vars[var] = value if value else default
    
    # Write to .env file
    with open(ENV_FILE, 'w') as f:
        for var, value in new_vars.items():
            f.write(f"{var}={value}\n")
    
    print_success(".env file created/updated successfully")

def main() -> None:
    """Main function to check and set up Claude Code integration with Archon."""
    print_header("Claude Code Integration with Archon - Setup")
    print_info("This script will help you set up the integration between Claude Code and Archon")
    
    # Check dependencies
    missing_packages = check_dependencies()
    if missing_packages:
        print_error(f"Missing required packages: {', '.join(missing_packages)}")
        install = input("Do you want to install them now? (y/n): ")
        if install.lower() == 'y':
            subprocess.run([sys.executable, "-m", "pip", "install"] + missing_packages)
            print_success("Packages installed successfully")
        else:
            print_warning("Please install the required packages and run this script again")
            sys.exit(1)
    else:
        print_success("All required packages are installed")
    
    # Check .env file
    env_exists, existing_vars = check_env_file()
    if not env_exists:
        print_warning("No .env file found")
        create_env_file({})
    else:
        update = input("Environment file found. Do you want to update it? (y/n): ")
        if update.lower() == 'y':
            create_env_file(existing_vars)
        else:
            print_info("Using existing environment configuration")
    
    # Check if Archon is running
    if check_archon_running():
        print_success("Archon graph service is running")
    else:
        print_warning("Archon graph service is not running")
        start = input("Do you want to start Archon now? (y/n): ")
        if start.lower() == 'y':
            print_info("Starting Archon...")
            print_info("Please open another terminal and run one of:")
            print_info("  python run_docker.py")
            print_info("  OR")
            print_info("  streamlit run streamlit_ui.py")
            
            input("Press Enter once Archon is running...")
            
            if check_archon_running():
                print_success("Archon graph service is now running")
            else:
                print_error("Could not detect Archon graph service")
                print_info("Please start Archon manually and try again")
    
    # Final instructions
    print_header("Setup Complete")
    print_info("To start the Claude Code MCP adapter, run:")
    print_info("  python claude_mcp_adapter.py")
    print_info("To access the Archon UI, open:")
    print_info(f"  {STREAMLIT_URL}")
    print_info("For more information, see CLAUDE.md")

if __name__ == "__main__":
    main()