from pydantic_ai import RunContext
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
            }