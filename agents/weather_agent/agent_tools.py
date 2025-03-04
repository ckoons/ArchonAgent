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