#!/usr/bin/env python3
"""
Claude Code MCP Adapter for Archon

This adapter enables seamless integration between Claude Code and the Archon agent builder.
It exposes Archon's functionality as a Model Context Protocol (MCP) server that can be used
by Claude Code to generate AI agents based on user requests.
"""

from datetime import datetime
import asyncio
import os
import uuid
import json
import sys
import requests
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load environment variables from .env file
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("claude-archon")

# Store active threads
active_threads: Dict[str, List[str]] = {}

# Graph service URL - this is where Archon's main API runs
GRAPH_SERVICE_URL = os.getenv("GRAPH_SERVICE_URL", "http://localhost:8100")

# Configure logging directory
os.makedirs("workbench", exist_ok=True)
LOG_FILE = os.path.join("workbench", "claude_logs.txt")

def write_to_log(message: str):
    """Write a message to the logs file in the workbench directory.
    
    Args:
        message: The message to log
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)

def check_archon_service():
    """Check if the Archon graph service is running."""
    try:
        response = requests.get(f"{GRAPH_SERVICE_URL}/health", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

@mcp.tool()
async def create_archon_thread() -> str:
    """Create a new conversation thread for Archon.
    Always call this tool before invoking Archon for the first time in a conversation.
    
    Returns:
        str: A unique thread ID for the conversation
    """
    if not check_archon_service():
        raise ConnectionError(
            "Cannot connect to Archon service. Please ensure Archon is running at " + 
            f"{GRAPH_SERVICE_URL}"
        )
    
    thread_id = str(uuid.uuid4())
    active_threads[thread_id] = []
    write_to_log(f"Created new thread: {thread_id}")
    return thread_id

def _make_archon_request(thread_id: str, user_input: str, config: dict) -> str:
    """Make synchronous request to Archon graph service"""
    response = requests.post(
        f"{GRAPH_SERVICE_URL}/invoke",
        json={
            "message": user_input,
            "thread_id": thread_id,
            "is_first_message": not active_threads[thread_id],
            "config": config
        }
    )
    response.raise_for_status()
    return response.json()

@mcp.tool()
async def run_archon_agent(thread_id: str, user_input: str) -> str:
    """Run the Archon agent to create or modify a Pydantic AI agent based on user requirements.
    
    This tool allows Claude Code to leverage Archon's agent-building capabilities.
    Before using this tool, you must first create a thread with create_archon_thread.
    
    The agent will generate complete, working code for a Pydantic AI agent that meets
    the user's requirements. After receiving the code, implement it into the user's
    workspace unless explicitly asked not to.
    
    Args:
        thread_id: The conversation thread ID from create_archon_thread
        user_input: The user's description of the agent they want to create
    
    Returns:
        str: The agent's response containing the generated code and explanations
    """
    if not check_archon_service():
        raise ConnectionError(
            "Cannot connect to Archon service. Please ensure Archon is running at " + 
            f"{GRAPH_SERVICE_URL}"
        )
    
    if thread_id not in active_threads:
        write_to_log(f"Error: Thread not found - {thread_id}")
        raise ValueError("Thread not found. You must first create a thread with create_archon_thread.")

    write_to_log(f"Processing message for thread {thread_id}: {user_input}")

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }
    
    try:
        result = await asyncio.to_thread(_make_archon_request, thread_id, user_input, config)
        active_threads[thread_id].append(user_input)
        return result['response']
        
    except Exception as e:
        error_msg = f"Error running Archon agent: {str(e)}"
        write_to_log(error_msg)
        raise RuntimeError(error_msg)

@mcp.tool()
async def get_archon_status() -> Dict[str, Any]:
    """Check the status of the Archon service and related components.
    
    Use this tool to verify that Archon is running properly and gather
    diagnostic information about the service's current state.
    
    Returns:
        dict: Status information about the Archon service
    """
    status = {
        "archon_service": "unknown",
        "active_threads": len(active_threads),
        "service_url": GRAPH_SERVICE_URL
    }
    
    try:
        response = requests.get(f"{GRAPH_SERVICE_URL}/health", timeout=5)
        status["archon_service"] = "running" if response.status_code == 200 else "error"
        status["service_response"] = response.json() if response.status_code == 200 else None
    except requests.RequestException as e:
        status["archon_service"] = "unavailable"
        status["error"] = str(e)
    
    write_to_log(f"Status check result: {json.dumps(status)}")
    return status

@mcp.tool()
async def implement_agent_code(file_path: str, code: str) -> str:
    """Implement the generated agent code into the user's workspace.
    
    After Archon generates a new agent, use this tool to automatically add
    the code to the user's workspace at the specified path.
    
    Args:
        file_path: Where to save the code (relative to current directory)
        code: The agent code to save
    
    Returns:
        str: Confirmation message with the absolute path to the created file
    """
    # Ensure the file path is valid and not trying to escape the workspace
    file_path = os.path.normpath(file_path)
    if file_path.startswith('..') or file_path.startswith('/'):
        raise ValueError("Invalid file path. Must be relative to current directory.")
    
    # Create directories if they don't exist
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    
    # Write the code to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(code)
    
    abs_path = os.path.abspath(file_path)
    write_to_log(f"Implemented agent code at: {abs_path}")
    
    return f"Agent code implemented successfully at {abs_path}"

if __name__ == "__main__":
    write_to_log("Starting Claude Code MCP Adapter for Archon")
    
    if not check_archon_service():
        print(f"WARNING: Cannot connect to Archon service at {GRAPH_SERVICE_URL}")
        print("Please ensure Archon is running before using this adapter.")
        print("You can start Archon with: python run_docker.py or streamlit run streamlit_ui.py")
    
    print(f"Claude Code MCP Adapter for Archon starting...")
    print(f"Connecting to Archon Graph Service at: {GRAPH_SERVICE_URL}")
    print(f"Log file: {LOG_FILE}")
    
    # Run MCP server
    mcp.run(transport='stdio')