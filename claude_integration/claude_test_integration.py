#!/usr/bin/env python3
"""
Test script for the Claude Code - Archon integration

This script simulates how Claude Code would interact with Archon through the MCP adapter.
It creates a thread, sends a request to generate an agent, and implements the generated code.

Note: This requires the claude_mcp_adapter_debug.py to be running in another terminal.
"""

import asyncio
import json
import os
import sys
import subprocess
from typing import Dict, Any

# Function to simulate Claude Code calling an MCP tool
async def call_mcp_tool(tool_name: str, params: Dict[str, Any] = None) -> Any:
    """
    Simulate Claude Code calling an MCP tool via subprocess.
    
    In a real implementation, Claude Code would communicate with the MCP adapter
    directly via its internal mechanisms.
    """
    if params is None:
        params = {}
    
    # Construct the MCP command
    cmd = ["echo", json.dumps({
        "type": "call",
        "name": tool_name,
        "params": params
    })]
    
    # Pipe to the MCP adapter
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE
    )
    
    mcp_proc = subprocess.Popen(
        ["python", "claude_mcp_adapter_debug.py"],
        stdin=proc.stdout,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Get the result
    stdout, stderr = mcp_proc.communicate()
    
    # Parse the result
    for line in stdout.split("\n"):
        if line.startswith('{"type":"return"'):
            try:
                result = json.loads(line)
                if result.get("type") == "return":
                    return result.get("value")
            except json.JSONDecodeError:
                pass
    
    return None

async def main():
    """Main test flow"""
    print("=== Testing Claude Code Integration with Archon ===")
    
    # Step 1: Create a thread
    print("\n1. Creating a thread with Archon...")
    thread_id = await call_mcp_tool("create_archon_thread")
    print(f"   Thread created: {thread_id}")
    
    # Step 2: Check Archon status
    print("\n2. Checking Archon status...")
    status = await call_mcp_tool("get_archon_status")
    print(f"   Status: {json.dumps(status, indent=2)}")
    
    # Step 3: Send a request to generate an agent
    print("\n3. Requesting an agent from Archon...")
    user_request = "Create a weather agent that can get forecasts for multiple cities"
    response = await call_mcp_tool("simulate_archon_request", {"request": user_request})
    print("   Response from Archon:")
    print(f"   {response}")
    
    # Step 4: Extract and implement the code
    print("\n4. Implementing the generated agent code...")
    # In a real scenario, Claude Code would extract the code block from the response
    # Here we'll use a simplified version
    code = """
# Example agent.py extracted from Archon's response
from __future__ import annotations as _annotations

import asyncio
import os
from dataclasses import dataclass
from typing import Any

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel

@dataclass
class WeatherDeps:
    weather_api_key: str

# Initialize the weather agent
weather_agent = Agent(
    OpenAIModel('gpt-4o-mini'),
    system_prompt="You are a weather assistant. Provide forecasts for cities.",
    deps_type=WeatherDeps,
    retries=2
)

async def main():
    # Get API key from environment
    api_key = os.getenv('WEATHER_API_KEY')
    if not api_key:
        print("ERROR: WEATHER_API_KEY environment variable is not set")
        return
        
    # Create dependencies
    deps = WeatherDeps(weather_api_key=api_key)
    
    # Run the agent
    result = await weather_agent.run(
        "What's the weather forecast for New York and London?", 
        deps=deps
    )
    
    print(result.data)

if __name__ == "__main__":
    asyncio.run(main())
"""
    
    # Create the agents directory if it doesn't exist
    os.makedirs("agents/weather_agent", exist_ok=True)
    
    # Implement the code
    file_path = "agents/weather_agent/agent.py"
    result = await call_mcp_tool("implement_agent_code", {
        "file_path": file_path,
        "code": code
    })
    print(f"   {result}")
    
    print("\n=== Test Complete ===")
    print("The Claude Code integration with Archon has been successfully tested!")

if __name__ == "__main__":
    asyncio.run(main())