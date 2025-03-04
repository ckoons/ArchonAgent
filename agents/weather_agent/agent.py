from __future__ import annotations as _annotations

import asyncio
import os
from dataclasses import dataclass
from typing import Dict, Any

from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.models.openai import OpenAIModel

from agent_tools import get_weather_forecast, get_city_coordinates
from agent_prompts import SYSTEM_PROMPT

@dataclass
class WeatherDeps:
    weather_api_key: str

# Initialize the weather agent
weather_agent = Agent(
    OpenAIModel('gpt-4o-mini'),
    system_prompt=SYSTEM_PROMPT,
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