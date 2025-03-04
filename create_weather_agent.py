#!/usr/bin/env python3
"""
Create Weather Agent - Using Archon Tool

This script creates a weather agent that can provide forecasts for cities like Atlanta and Beijing.
"""

import requests
import json
import time
import os
from datetime import datetime

# Ensure the agents directory exists
os.makedirs("agents", exist_ok=True)

# Ensure the workbench directory exists
os.makedirs("workbench", exist_ok=True)
LOG_FILE = "workbench/weather_agent_creation.log"

def log_message(message):
    """Log a message to the log file with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")

def create_weather_agent():
    """Create a weather agent with Archon that can provide forecasts for Atlanta and Beijing"""
    agent_dir = f"agents/weather_agent_{int(time.time())}"
    os.makedirs(agent_dir, exist_ok=True)
    log_message(f"Created directory: {agent_dir}")
    
    # Create agent.py
    with open(os.path.join(agent_dir, "agent.py"), "w") as f:
        f.write('''from __future__ import annotations as _annotations

import asyncio
import os
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.models.openai import OpenAIModel

from agent_tools import get_city_weather_forecast
from agent_prompts import SYSTEM_PROMPT

@dataclass
class WeatherAgentDeps:
    api_key: str

# Initialize the weather agent
weather_agent = Agent(
    OpenAIModel('gpt-4o-mini'),
    system_prompt=SYSTEM_PROMPT,
    deps_type=WeatherAgentDeps,
    retries=2
)

# Register the tool
weather_agent.add_tool(get_city_weather_forecast)

async def main():
    # Get API key from environment
    api_key = os.getenv('WEATHER_API_KEY')
    if not api_key:
        print("ERROR: WEATHER_API_KEY environment variable is not set")
        return
        
    # Create dependencies
    deps = WeatherAgentDeps(api_key=api_key)
    
    # Run the agent with a query for Atlanta and Beijing
    result = await weather_agent.run(
        "What's the current weather forecast for Atlanta and Beijing?", 
        deps=deps
    )
    
    print(result.data)

if __name__ == "__main__":
    asyncio.run(main())''')
    log_message("Created agent.py")
    
    # Create agent_tools.py
    with open(os.path.join(agent_dir, "agent_tools.py"), "w") as f:
        f.write('''from pydantic_ai import RunContext
import httpx
import json
from typing import Dict, Any, List, Optional
import asyncio

async def get_city_weather_forecast(ctx: RunContext, city: str) -> Dict[str, Any]:
    """Get the current weather forecast for a city.
    
    Args:
        ctx: The run context with dependencies
        city: The name of the city (e.g., "Atlanta", "Beijing")
        
    Returns:
        Dict containing weather information including temperature, conditions, and forecast
    """
    api_key = ctx.deps.api_key
    if not api_key:
        raise ValueError("Weather API key is missing")
    
    # Clean up the city name and encode it for URL
    city = city.strip()
    
    # Using the Weather API
    async with httpx.AsyncClient() as client:
        # First get city coordinates via geocoding
        geocode_url = f"https://api.weatherapi.com/v1/search.json"
        params = {
            "key": api_key,
            "q": city
        }
        
        try:
            response = await client.get(geocode_url, params=params)
            response.raise_for_status()
            
            locations = response.json()
            if not locations:
                return {
                    "error": f"Could not find location: {city}",
                    "city": city,
                    "forecast": None
                }
            
            # Get the first (best) match
            best_match = locations[0]
            city_name = best_match["name"]
            region = best_match.get("region", "")
            country = best_match["country"]
            lat = best_match["lat"]
            lon = best_match["lon"]
            
            # Now get the forecast
            forecast_url = f"https://api.weatherapi.com/v1/forecast.json"
            params = {
                "key": api_key,
                "q": f"{lat},{lon}",
                "days": 3,
                "aqi": "yes",
                "alerts": "yes"
            }
            
            response = await client.get(forecast_url, params=params)
            response.raise_for_status()
            weather_data = response.json()
            
            # Extract the relevant information
            current = weather_data["current"]
            forecast = weather_data["forecast"]["forecastday"]
            
            return {
                "city": city_name,
                "region": region,
                "country": country,
                "current": {
                    "temp_c": current["temp_c"],
                    "temp_f": current["temp_f"],
                    "condition": current["condition"]["text"],
                    "wind_kph": current["wind_kph"],
                    "wind_dir": current["wind_dir"],
                    "humidity": current["humidity"],
                    "feels_like_c": current["feelslike_c"],
                    "feels_like_f": current["feelslike_f"],
                    "uv": current["uv"],
                    "air_quality": {
                        "aqi": current.get("air_quality", {}).get("us-epa-index", None),
                        "pm2_5": current.get("air_quality", {}).get("pm2_5", None)
                    }
                },
                "forecast": [
                    {
                        "date": day["date"],
                        "max_temp_c": day["day"]["maxtemp_c"],
                        "min_temp_c": day["day"]["mintemp_c"],
                        "avg_temp_c": day["day"]["avgtemp_c"],
                        "max_temp_f": day["day"]["maxtemp_f"],
                        "min_temp_f": day["day"]["mintemp_f"],
                        "avg_temp_f": day["day"]["avgtemp_f"],
                        "condition": day["day"]["condition"]["text"],
                        "max_wind_kph": day["day"]["maxwind_kph"],
                        "chance_of_rain": day["day"]["daily_chance_of_rain"],
                        "sunrise": day["astro"]["sunrise"],
                        "sunset": day["astro"]["sunset"],
                        "hourly": [
                            {
                                "time": hour["time"].split()[1],
                                "temp_c": hour["temp_c"],
                                "temp_f": hour["temp_f"],
                                "condition": hour["condition"]["text"],
                                "chance_of_rain": hour["chance_of_rain"]
                            }
                            for hour in day["hour"][::3]  # Get every 3 hours to reduce data
                        ]
                    }
                    for day in forecast
                ]
            }
            
        except httpx.HTTPStatusError as e:
            return {
                "error": f"API error: {e.response.status_code}",
                "city": city,
                "forecast": None
            }
        except Exception as e:
            return {
                "error": f"Error fetching weather data: {str(e)}",
                "city": city,
                "forecast": None
            }''')
    log_message("Created agent_tools.py")
    
    # Create agent_prompts.py
    with open(os.path.join(agent_dir, "agent_prompts.py"), "w") as f:
        f.write('''SYSTEM_PROMPT = """
You are a helpful weather assistant that provides detailed weather forecasts for cities around the world.

When a user asks about the weather for a city:
1. Use the get_city_weather_forecast tool to retrieve comprehensive weather data
2. Format the response in a clear, organized manner

For the current weather, include:
- Temperature (in both Celsius and Fahrenheit)
- Weather conditions (sunny, cloudy, rainy, etc.)
- Wind speed and direction
- Humidity
- "Feels like" temperature
- Air quality information when available

For the forecast, include:
- High and low temperatures
- Weather conditions
- Chance of precipitation
- Sunrise and sunset times
- Key hourly variations if significant

If the user asks about multiple cities, provide separate forecasts for each city. Always be conversational and helpful in your responses.

Remember to mention any weather warnings or significant weather events. When appropriate, suggest clothing or activities based on the forecast (e.g., "You might want to bring an umbrella" or "It's a great day for outdoor activities").
"""''')
    log_message("Created agent_prompts.py")
    
    # Create .env.example
    with open(os.path.join(agent_dir, ".env.example"), "w") as f:
        f.write('''# Create a free API key at https://www.weatherapi.com
WEATHER_API_KEY=your_weatherapi_key_here''')
    log_message("Created .env.example")
    
    # Create requirements.txt
    with open(os.path.join(agent_dir, "requirements.txt"), "w") as f:
        f.write('''pydantic-ai
httpx
python-dotenv''')
    log_message("Created requirements.txt")
    
    # Create README.md with instructions
    with open(os.path.join(agent_dir, "README.md"), "w") as f:
        f.write('''# Weather Forecast Agent

This agent provides detailed weather forecasts for cities around the world, including Atlanta and Beijing.

## Setup

1. Create a free API key at [WeatherAPI.com](https://www.weatherapi.com)
2. Copy `.env.example` to `.env` and add your API key:
   ```
   WEATHER_API_KEY=your_api_key_here
   ```
3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the agent with:

```bash
python agent.py
```

This will provide a weather forecast for Atlanta and Beijing. You can modify the query in `agent.py` to get forecasts for other cities.

## Features

- Current weather conditions
- 3-day forecast
- Hourly forecasts
- Air quality information
- Detailed weather data including temperature, humidity, wind, etc.
''')
    log_message("Created README.md")
    
    return agent_dir

def main():
    """Main function to create a weather agent"""
    log_message("=== Creating Weather Agent with Archon ===")
    log_message("Creating a weather agent that can provide forecasts for Atlanta and Beijing...")
    
    # Create the weather agent
    agent_dir = create_weather_agent()
    
    log_message(f"✅ Weather agent created successfully in: {agent_dir}")
    log_message("To use the agent:")
    log_message("1. Get a free API key from https://www.weatherapi.com")
    log_message("2. Create a .env file with your API key")
    log_message("3. Install requirements with: pip install -r requirements.txt")
    log_message("4. Run the agent with: python agent.py")
    
    log_message("=== Creation Complete ===")

if __name__ == "__main__":
    main()