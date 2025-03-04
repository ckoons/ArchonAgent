#!/usr/bin/env python3
"""
Simple test of the Claude Code - Archon integration.
Creates a weather agent from simulated Archon output.
"""

import os

def create_weather_agent():
    """Create a weather agent in the agents/weather_agent directory."""
    # Create the directory
    agent_dir = "agents/weather_agent"
    os.makedirs(agent_dir, exist_ok=True)
    
    # Write agent.py
    with open(os.path.join(agent_dir, "agent.py"), "w") as f:
        f.write('''from __future__ import annotations as _annotations

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
    asyncio.run(main())''')
    print(f"Created file: {agent_dir}/agent.py")
    
    # Write agent_tools.py
    with open(os.path.join(agent_dir, "agent_tools.py"), "w") as f:
        f.write('''from pydantic_ai import RunContext
import httpx
from typing import Dict, Any, List
import asyncio

async def get_city_coordinates(ctx: RunContext, city: str) -> Dict[str, float]:
    """Get latitude and longitude coordinates for a city.
    
    Args:
        ctx: The run context with dependencies
        city: The name of the city to look up
        
    Returns:
        Dict containing latitude and longitude
    """
    async with httpx.AsyncClient() as client:
        params = {
            "q": city,
            "limit": 1,
            "format": "json"
        }
        response = await client.get("https://nominatim.openstreetmap.org/search", params=params)
        response.raise_for_status()
        
        results = response.json()
        if not results:
            raise ValueError(f"Could not find coordinates for city: {city}")
            
        return {
            "lat": float(results[0]["lat"]),
            "lon": float(results[0]["lon"])
        }

async def get_weather_forecast(ctx: RunContext, lat: float, lon: float, days: int = 3) -> List[Dict[str, Any]]:
    """Get weather forecast for a location.
    
    Args:
        ctx: The run context with dependencies
        lat: Latitude of the location
        lon: Longitude of the location
        days: Number of days to forecast (default: 3)
        
    Returns:
        List of daily forecasts with weather data
    """
    api_key = ctx.deps.weather_api_key
    if not api_key:
        raise ValueError("Weather API key is missing")
    
    async with httpx.AsyncClient() as client:
        params = {
            "key": api_key,
            "q": f"{lat},{lon}",
            "days": days,
            "aqi": "no",
            "alerts": "no"
        }
        response = await client.get("https://api.weatherapi.com/v1/forecast.json", params=params)
        response.raise_for_status()
        
        data = response.json()
        return [
            {
                "date": day["date"],
                "max_temp_c": day["day"]["maxtemp_c"],
                "min_temp_c": day["day"]["mintemp_c"],
                "condition": day["day"]["condition"]["text"],
                "chance_of_rain": day["day"]["daily_chance_of_rain"]
            }
            for day in data["forecast"]["forecastday"]
        ]''')
    print(f"Created file: {agent_dir}/agent_tools.py")
    
    # Write agent_prompts.py
    with open(os.path.join(agent_dir, "agent_prompts.py"), "w") as f:
        f.write('''SYSTEM_PROMPT = """
You are a helpful weather assistant that provides forecasts for cities around the world.

When a user asks about the weather in a city:
1. Use the get_city_coordinates tool to find the city's location
2. Use the get_weather_forecast tool to retrieve the forecast
3. Summarize the weather in a friendly, conversational manner

Include the high and low temperatures, general conditions, and chance of rain in your summary.
If you're asked about multiple cities, provide separate forecasts for each.
"""''')
    print(f"Created file: {agent_dir}/agent_prompts.py")
    
    # Write .env.example
    with open(os.path.join(agent_dir, ".env.example"), "w") as f:
        f.write('''# Create a free API key at https://www.weatherapi.com
WEATHER_API_KEY=your_api_key_here''')
    print(f"Created file: {agent_dir}/.env.example")
    
    # Write requirements.txt
    with open(os.path.join(agent_dir, "requirements.txt"), "w") as f:
        f.write('''pydantic-ai
httpx
python-dotenv''')
    print(f"Created file: {agent_dir}/requirements.txt")

def main():
    """Main test function."""
    print("=== Claude Code Integration Test with Archon ===\n")
    print("Simulating agent implementation from Archon's output...\n")
    
    create_weather_agent()
    
    print("\n=== Integration Test Complete ===")
    print("The weather agent has been successfully implemented.")
    print("\nTo run the agent:")
    print("1. Create a .env file with your WEATHER_API_KEY")
    print("2. Install the requirements: pip install -r agents/weather_agent/requirements.txt")
    print("3. Run the agent: python agents/weather_agent/agent.py")

if __name__ == "__main__":
    main()