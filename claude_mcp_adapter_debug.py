#!/usr/bin/env python3
"""
Debug version of the Claude Code MCP Adapter for Archon
This version bypasses the health check to work even if the Archon API is unstable
"""

from datetime import datetime
import asyncio
import os
import uuid
import json
import sys
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("claude-archon-debug")

# Store active threads
active_threads: Dict[str, List[str]] = {}

# Graph service URL
GRAPH_SERVICE_URL = os.getenv("GRAPH_SERVICE_URL", "http://localhost:8100")

# Configure logging
os.makedirs("workbench", exist_ok=True)
LOG_FILE = os.path.join("workbench", "claude_debug_logs.txt")

def write_to_log(message: str):
    """Write a message to the logs file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)

@mcp.tool()
async def create_archon_thread() -> str:
    """Create a new conversation thread for Archon."""
    thread_id = str(uuid.uuid4())
    active_threads[thread_id] = []
    write_to_log(f"Created new thread: {thread_id}")
    return thread_id

@mcp.tool()
async def get_archon_status() -> Dict[str, Any]:
    """Check the status of the Archon service."""
    return {
        "archon_service": "unknown - bypassing health check",
        "active_threads": len(active_threads),
        "service_url": GRAPH_SERVICE_URL
    }

@mcp.tool()
async def simulate_archon_request(request: str) -> str:
    """Simulate a request to Archon without actually calling the API.
    
    For testing when the actual Archon API is not responding correctly.
    
    Args:
        request: The user's request for an agent
        
    Returns:
        str: Simulated response from Archon
    """
    write_to_log(f"Simulating Archon request: {request}")
    
    # Wait to simulate processing time
    await asyncio.sleep(2)
    
    # Simple response template
    return f"""
I'll create a Pydantic AI agent based on your request: "{request}"

Here's the implementation for your agent:

```python
# agent.py
from __future__ import annotations as _annotations

import asyncio
import os
from dataclasses import dataclass
from typing import Any

from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.models.openai import OpenAIModel

@dataclass
class AgentDeps:
    api_key: str

# Initialize the agent
my_agent = Agent(
    OpenAIModel('gpt-4o-mini'),
    system_prompt="You are a helpful assistant specialized in {request}",
    deps_type=AgentDeps,
    retries=2
)

async def main():
    # Get API key from environment
    api_key = os.getenv('API_KEY')
    if not api_key:
        print("ERROR: API_KEY environment variable is not set")
        return
        
    # Create dependencies
    deps = AgentDeps(api_key=api_key)
    
    # Run the agent
    result = await my_agent.run(
        "Help me with {request}", 
        deps=deps
    )
    
    print(result.data)

if __name__ == "__main__":
    asyncio.run(main())
```

This is a basic implementation. Let me know if you need additional features or tools for this agent!
"""

@mcp.tool()
async def implement_agent_code(file_path: str, code: str) -> str:
    """Implement the generated agent code into the user's workspace."""
    # Ensure the file path is valid
    file_path = os.path.normpath(file_path)
    if file_path.startswith('..') or file_path.startswith('/'):
        raise ValueError("Invalid file path. Must be relative to current directory.")
    
    # Create directories if needed
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    
    # Write the code to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(code)
    
    abs_path = os.path.abspath(file_path)
    write_to_log(f"Implemented agent code at: {abs_path}")
    
    return f"Agent code implemented successfully at {abs_path}"

if __name__ == "__main__":
    write_to_log("Starting Claude Code MCP Debug Adapter")
    print(f"Claude Code MCP Debug Adapter starting...")
    print(f"This is a debug version that will work even if Archon API is unstable")
    print(f"Log file: {LOG_FILE}")
    
    # Run MCP server
    mcp.run(transport='stdio')