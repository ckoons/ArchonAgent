# Weather Forecast Agent

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
