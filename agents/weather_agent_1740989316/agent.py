from __future__ import annotations as _annotations

import asyncio
import os
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.models.openai import OpenAIModel

# Load environment variables from .env file
load_dotenv()

# No longer needed since we've implemented the tool directly in this file
# from agent_tools import get_city_weather_forecast
from agent_prompts import SYSTEM_PROMPT

@dataclass
class WeatherAgentDeps:
    api_key: str

# In Pydantic AI, tools are registered with a decorator
# so let's define the tool directly in this file
@Agent.tool
async def get_city_weather_forecast(ctx: RunContext[WeatherAgentDeps], city: str) -> Dict[str, Any]:
    """Get the current weather forecast for a city.
    
    Args:
        ctx: The run context with dependencies
        city: The name of the city (e.g., "Atlanta", "Beijing")
        
    Returns:
        Dict containing weather information including temperature, conditions, and forecast
    """
    import httpx
    
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
                        "sunset": day["astro"]["sunset"]
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
            }

# Initialize the weather agent
weather_agent = Agent(
    OpenAIModel('gpt-4o-mini'),
    system_prompt=SYSTEM_PROMPT,
    deps_type=WeatherAgentDeps,
    retries=2
)

async def main():
    # Get API key from environment
    api_key = os.getenv('WEATHER_API_KEY')
    if not api_key:
        print("ERROR: WEATHER_API_KEY environment variable is not set")
        print("Current working directory:", os.getcwd())
        print("Contents of .env file:")
        try:
            with open(".env", "r") as f:
                content = f.read()
                # Mask most of the API key for security if it exists
                if "WEATHER_API_KEY" in content:
                    lines = content.split('\n')
                    for line in lines:
                        if line.startswith("WEATHER_API_KEY"):
                            key = line.split('=')[1].strip()
                            if len(key) > 8:
                                masked_key = key[:4] + "*" * (len(key) - 8) + key[-4:]
                                print(f"WEATHER_API_KEY={masked_key}")
                            else:
                                print("WEATHER_API_KEY=[too short to display safely]")
                        else:
                            print(line)
                else:
                    print("No WEATHER_API_KEY found in .env file")
        except Exception as e:
            print(f"Error reading .env file: {e}")
        return
        
    # Create dependencies
    deps = WeatherAgentDeps(api_key=api_key)
    
    # Display a message about starting the query
    print(f"Fetching weather forecast for Atlanta and Beijing...")
    
    try:
        # Run the agent with a query for Atlanta and Beijing
        result = await weather_agent.run(
            "What's the current weather forecast for Atlanta and Beijing?", 
            deps=deps
        )
        
        print(result.data)
    except Exception as e:
        print(f"Error running weather agent: {e}")

if __name__ == "__main__":
    asyncio.run(main())