#!/usr/bin/env python3
"""
Search Agent - Created with Archon

This agent performs web searches using a specified website (defaults to Google).
It can answer questions or calculate the current Julian date if no query is provided.
"""

from __future__ import annotations as _annotations

import asyncio
import os
import datetime
from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Callable
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from pydantic_ai import Agent
from pydantic_ai.tools import Tools
from pydantic_ai.models.openai import OpenAIModel

from claude_agent_tools import perform_search, calculate_julian_date
from claude_agent_prompts import SYSTEM_PROMPT

@dataclass
class SearchAgentDeps:
    """Dependencies for the search agent."""
    search_api_key: Optional[str] = None

# Define the agent's tools
tools = Tools()
tools.register(perform_search)
tools.register(calculate_julian_date)
    
# Initialize the search agent
search_agent = Agent(
    model=OpenAIModel(
        model_name='gpt-3.5-turbo',  # You can change this to your preferred model
        base_url=os.getenv('OPENAI_BASE_URL', None)  # Will use official OpenAI API if not set
    ),
    system_prompt=SYSTEM_PROMPT,
    tools=tools,
    deps_type=SearchAgentDeps
)

async def main():
    """Run the search agent interactively."""
    # Get API key from environment (optional for some search engines)
    api_key = os.getenv('SEARCH_API_KEY', '')
        
    # Create dependencies
    deps = SearchAgentDeps(search_api_key=api_key)
    
    print("=== Search Agent ===")
    print("This agent can search websites and retrieve information.")
    
    while True:
        # Get website from user
        website = input("\nEnter website to search (or press Enter for Google): ").strip()
        if not website:
            website = "Google"
        
        # Get search query from user
        query = input("Enter your search query (or press Enter for today's Julian date): ").strip()
        
        # Prepare the message for the agent
        if query:
            message = f"Search for '{query}' on {website}"
        else:
            message = f"What is today's Julian date?"
        
        print("\nProcessing your request...")
        
        # Run the agent
        try:
            result = await search_agent.run(message, deps=deps)
            print("\nResult:")
            print(result.content.strip())
        except Exception as e:
            print(f"\nError: {str(e)}")
        
        # Ask if the user wants to continue
        continue_prompt = input("\nWould you like to perform another search? (y/n): ")
        if continue_prompt.lower() != 'y':
            break
    
    print("Thank you for using the Search Agent!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSearch Agent terminated by user.")