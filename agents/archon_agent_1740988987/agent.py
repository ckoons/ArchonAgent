from __future__ import annotations as _annotations

import asyncio
import os
from dataclasses import dataclass
from typing import Dict, Any

from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.models.openai import OpenAIModel

from agent_tools import *
from agent_prompts import SYSTEM_PROMPT

@dataclass
class NewsSummarizerDeps:
    api_key: str

# Initialize the agent
newssummarizer = Agent(
    OpenAIModel('gpt-4o-mini'),
    system_prompt=SYSTEM_PROMPT,
    deps_type=NewsSummarizerDeps,
    retries=2
)

async def main():
    # Get API key from environment
    api_key = os.getenv('API_KEY')
    if not api_key:
        print("ERROR: API_KEY environment variable is not set")
        return
        
    # Create dependencies
    deps = NewsSummarizerDeps(api_key=api_key)
    
    # Run the agent
    result = await newssummarizer.run(
        "Help me with news summarization agent", 
        deps=deps
    )
    
    print(result.data)

if __name__ == "__main__":
    asyncio.run(main())