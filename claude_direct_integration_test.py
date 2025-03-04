#!/usr/bin/env python3
"""
Direct integration test for Claude Code - Archon integration.

This script demonstrates how Claude Code can directly implement code generated from Archon.
It bypasses the MCP adapter to focus on the core functionality of implementing AI agent code.
"""

import os
import asyncio
from typing import Dict, Any

# Simulated response from Archon
ARCHON_RESPONSE = """
I'll create a weather agent with Pydantic AI that can fetch forecasts for multiple cities!

First, let's implement the main agent file:

```python
# agent.py
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
```

Now let's implement the tools:

```python
# agent_tools.py
from pydantic_ai import RunContext
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
        ]
```

And finally, let's create the system prompt:

```python
# agent_prompts.py
SYSTEM_PROMPT = '''
You are a helpful weather assistant that provides forecasts for cities around the world.

When a user asks about the weather in a city:
1. Use the get_city_coordinates tool to find the city\'s location
2. Use the get_weather_forecast tool to retrieve the forecast
3. Summarize the weather in a friendly, conversational manner

Include the high and low temperatures, general conditions, and chance of rain in your summary.
If you\'re asked about multiple cities, provide separate forecasts for each.
'''
```

Don't forget the environment file:

```
# .env.example
# Create a free API key at https://www.weatherapi.com
WEATHER_API_KEY=your_api_key_here
```

And the requirements.txt file:

```
# requirements.txt
pydantic-ai
httpx
python-dotenv
```

That's everything you need for a complete weather agent that can fetch forecasts for multiple cities! To run it:

1. Copy your API key to a .env file
2. Install the requirements: pip install -r requirements.txt
3. Run the agent: python agent.py
"""

def extract_code_blocks(text: str) -> Dict[str, str]:
    """Extract code blocks from markdown text based on filename comments."""
    code_blocks = {}
    lines = text.split('\n')
    current_file = None
    current_content = []
    
    in_code_block = False
    
    for line in lines:
        if line.startswith('```'):
            if in_code_block:
                # End of code block
                if current_file:
                    code_blocks[current_file] = '\n'.join(current_content)
                current_file = None
                current_content = []
                in_code_block = False
            else:
                # Start of code block
                in_code_block = True
        elif in_code_block:
            if not current_content and line.startswith('#'):
                # Check if this is a filename comment like "# agent.py"
                parts = line.strip('# ').split()
                if len(parts) == 1 and '.' in parts[0]:
                    current_file = parts[0]
                    continue
            
            # Add line to current content
            current_content.append(line)
    
    return code_blocks

def implement_code(files: Dict[str, str], base_dir: str = "agents/weather_agent") -> None:
    """Implement extracted code files into the filesystem."""
    # Create base directory if it doesn't exist
    os.makedirs(base_dir, exist_ok=True)
    
    # Write each file
    for filename, content in files.items():
        file_path = os.path.join(base_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created file: {file_path}")

def main():
    """Run the integration test."""
    print("=== Direct Integration Test: Claude Code + Archon ===\n")
    
    print("1. Simulating Archon's agent generation response...")
    print("   Archon has generated a complete weather agent with multiple files")
    
    print("\n2. Extracting code blocks from Archon's response...")
    code_blocks = extract_code_blocks(ARCHON_RESPONSE)
    print(f"   Extracted {len(code_blocks)} code files:")
    for filename in code_blocks:
        print(f"   - {filename}")
    
    print("\n3. Implementing agent code into workspace...")
    implement_code(code_blocks)
    
    print("\n=== Integration Test Complete ===")
    print("The weather agent has been successfully implemented.")
    print("To run it:")
    print("1. Create a .env file with your WEATHER_API_KEY")
    print("2. Install the requirements: pip install -r agents/weather_agent/requirements.txt")
    print("3. Run the agent: python agents/weather_agent/agent.py")

if __name__ == "__main__":
    main()