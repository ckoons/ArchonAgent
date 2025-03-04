#!/usr/bin/env python3
"""
ClaudeCode Archon Tool - Simplified Version

This script demonstrates how Claude Code can use Archon as a tool
to generate a new AI agent based on user requirements, without
requiring Selenium for browser automation.
"""

import requests
import json
import time
import os
import uuid
from datetime import datetime

# Configuration
STREAMLIT_URL = "http://localhost:8501"
GRAPH_SERVICE_URL = "http://localhost:8100"
LOG_FILE = "workbench/claudecode_archon_simple.log"

# Ensure log directory exists
os.makedirs("workbench", exist_ok=True)

def log_message(message):
    """Log a message to the log file with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")

class ArchonTool:
    """Tool class for Claude Code to interact with Archon"""
    
    def __init__(self):
        """Initialize the Archon tool"""
        self.check_availability()
    
    def check_availability(self):
        """Check if Archon is available"""
        try:
            response = requests.get(STREAMLIT_URL, timeout=5)
            if response.status_code == 200:
                log_message("✅ Archon Streamlit UI is running")
            else:
                log_message(f"❌ Archon Streamlit UI returned status code {response.status_code}")
                return False
        except requests.RequestException as e:
            log_message(f"❌ Failed to connect to Archon Streamlit UI: {str(e)}")
            return False
        
        try:
            response = requests.get(f"{GRAPH_SERVICE_URL}/health", timeout=5)
            if response.status_code == 200:
                log_message(f"✅ Archon Graph Service is running")
            else:
                log_message(f"❌ Archon Graph Service returned status code {response.status_code}")
                return False
        except requests.RequestException as e:
            log_message(f"❌ Failed to connect to Archon Graph Service: {str(e)}")
            log_message("⚠️ Using simulated mode since Graph Service is not accessible")
        
        return True
    
    def create_agent(self, prompt):
        """Create an agent using Archon based on a prompt"""
        log_message(f"Creating agent from prompt: {prompt}")
        
        # Try to use the actual Archon Graph Service API
        try:
            thread_id = str(uuid.uuid4())
            payload = {
                "message": prompt,
                "thread_id": thread_id,
                "is_first_message": True
            }
            
            log_message(f"Sending request to Archon Graph Service with thread_id: {thread_id}")
            response = requests.post(f"{GRAPH_SERVICE_URL}/invoke", json=payload, timeout=60)
            
            if response.status_code == 200:
                response_data = response.json()
                log_message("Received response from Archon Graph Service")
                return True, "Response received from Archon", response_data
            else:
                log_message(f"❌ Archon Graph Service returned status code {response.status_code}")
        except requests.RequestException as e:
            log_message(f"❌ Failed to connect to Archon Graph Service: {str(e)}")
        
        # If the actual API failed, simulate a response
        log_message("⚠️ Using simulated mode to demonstrate Claude Code using Archon as a tool")
        return self.simulate_archon_response(prompt)
    
    def simulate_archon_response(self, prompt):
        """Simulate a response from Archon (for demonstration purposes)"""
        log_message("Simulating Archon agent creation process...")
        
        # Simulate processing time
        time.sleep(5)
        
        # Generate a simulated response with code blocks
        files = self.generate_agent_files(prompt)
        
        # Implement the agent code
        agent_dir = self.implement_agent_code(files)
        
        return True, f"Agent created successfully in {agent_dir}", files
    
    def generate_agent_files(self, prompt):
        """Generate agent files based on the user prompt"""
        log_message("Generating agent files based on prompt")
        
        # Extract keywords from the prompt to customize the agent
        keywords = prompt.lower()
        
        if "news" in keywords and "summarization" in keywords:
            agent_type = "news_summarization"
            agent_name = "NewsSummarizer"
            agent_description = "News summarization agent"
        elif "weather" in keywords:
            agent_type = "weather_forecast"
            agent_name = "WeatherAgent" 
            agent_description = "Weather forecast agent"
        elif "translation" in keywords:
            agent_type = "language_translator"
            agent_name = "TranslatorAgent"
            agent_description = "Language translation agent"
        else:
            agent_type = "general_assistant"
            agent_name = "AssistantAgent"
            agent_description = "General assistant agent"
        
        # Generate the agent files
        files = {
            "agent.py": self.generate_agent_py(agent_name, agent_description),
            "agent_tools.py": self.generate_agent_tools_py(agent_type),
            "agent_prompts.py": self.generate_agent_prompts_py(agent_type, agent_description),
            ".env.example": self.generate_env_example(agent_type),
            "requirements.txt": self.generate_requirements_txt(agent_type)
        }
        
        return files
    
    def generate_agent_py(self, agent_name, agent_description):
        """Generate the main agent.py file"""
        return f'''from __future__ import annotations as _annotations

import asyncio
import os
from dataclasses import dataclass
from typing import Dict, Any

from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.models.openai import OpenAIModel

from agent_tools import *
from agent_prompts import SYSTEM_PROMPT

@dataclass
class {agent_name}Deps:
    api_key: str

# Initialize the agent
{agent_name.lower()} = Agent(
    OpenAIModel('gpt-4o-mini'),
    system_prompt=SYSTEM_PROMPT,
    deps_type={agent_name}Deps,
    retries=2
)

async def main():
    # Get API key from environment
    api_key = os.getenv('API_KEY')
    if not api_key:
        print("ERROR: API_KEY environment variable is not set")
        return
        
    # Create dependencies
    deps = {agent_name}Deps(api_key=api_key)
    
    # Run the agent
    result = await {agent_name.lower()}.run(
        "Help me with {agent_description.lower()}", 
        deps=deps
    )
    
    print(result.data)

if __name__ == "__main__":
    asyncio.run(main())'''
    
    def generate_agent_tools_py(self, agent_type):
        """Generate the agent_tools.py file based on agent type"""
        if agent_type == "news_summarization":
            return '''from pydantic_ai import RunContext
import httpx
from typing import Dict, Any, List
import asyncio

async def fetch_news_headlines(ctx: RunContext, category: str = "general") -> List[Dict[str, str]]:
    """Fetch news headlines from a news API.
    
    Args:
        ctx: The run context with dependencies
        category: News category (general, business, technology, etc.)
        
    Returns:
        List of news articles with title, description, and source
    """
    api_key = ctx.deps.api_key
    if not api_key:
        raise ValueError("API key is missing")
    
    async with httpx.AsyncClient() as client:
        params = {
            "apiKey": api_key,
            "category": category,
            "language": "en"
        }
        response = await client.get("https://newsapi.org/v2/top-headlines", params=params)
        response.raise_for_status()
        
        data = response.json()
        return [
            {
                "title": article["title"],
                "description": article["description"],
                "source": article["source"]["name"],
                "url": article["url"]
            }
            for article in data["articles"]
            if article["description"]
        ]

async def fetch_article_content(ctx: RunContext, url: str) -> str:
    """Fetch and extract main content from a news article.
    
    Args:
        ctx: The run context with dependencies
        url: URL of the news article
        
    Returns:
        Extracted main content of the article
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        
        # In a real implementation, this would use a proper HTML parser
        # and extraction logic to get the article content
        html = response.text
        
        # Simple extraction for demonstration
        # This is a placeholder - real implementation would be more robust
        start_idx = html.find("<body")
        end_idx = html.find("</body>")
        body_content = html[start_idx:end_idx] if start_idx > 0 and end_idx > 0 else html
        
        # Very naive approach to extract text
        body_content = body_content.replace("<p>", " ").replace("</p>", " ")
        body_content = " ".join(body_content.split())
        
        return body_content[:5000]  # Limit to 5000 chars for demonstration

async def summarize_text(ctx: RunContext, text: str, max_length: int = 200) -> str:
    """Summarize a text using built-in AI capabilities.
    
    This tool demonstrates how to use the LLM itself for a subtask.
    In a real implementation, this could be a call to a separate LLM.
    
    Args:
        ctx: The run context with dependencies
        text: The text to summarize
        max_length: Maximum length of the summary in words
        
    Returns:
        Summarized text
    """
    # In a real implementation, this would call another LLM or use a separate tool
    # For demonstration, we'll return a placeholder
    if len(text) <= max_length:
        return text
    
    return f"Summary of text with {len(text.split())} words (limited to {max_length} words)"
'''
        elif agent_type == "weather_forecast":
            return '''from pydantic_ai import RunContext
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
    api_key = ctx.deps.api_key
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
'''
        else:
            return '''from pydantic_ai import RunContext
import httpx
from typing import Dict, Any, List
import asyncio

async def search_web(ctx: RunContext, query: str) -> Dict[str, Any]:
    """Search the web for information.
    
    Args:
        ctx: The run context with dependencies
        query: The search query
        
    Returns:
        Search results
    """
    api_key = ctx.deps.api_key
    if not api_key:
        raise ValueError("API key is missing")
    
    async with httpx.AsyncClient() as client:
        params = {
            "key": api_key,
            "q": query,
            "num": 5
        }
        # This URL is for demonstration only, would use a real search API
        response = await client.get("https://example.com/api/search", params=params)
        response.raise_for_status()
        
        # Simplified response for demonstration
        return {
            "query": query,
            "results": [
                {"title": f"Result {i} for {query}", "url": f"https://example.com/{i}"}
                for i in range(1, 6)
            ]
        }

async def fetch_content(ctx: RunContext, url: str) -> str:
    """Fetch content from a URL.
    
    Args:
        ctx: The run context with dependencies
        url: The URL to fetch content from
        
    Returns:
        Content of the URL
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        
        # Return the content (simplified for demonstration)
        return f"Content from {url} (simplified for demonstration)"
'''
    
    def generate_agent_prompts_py(self, agent_type, agent_description):
        """Generate the agent_prompts.py file based on agent type"""
        if agent_type == "news_summarization":
            return '''SYSTEM_PROMPT = """
You are a news summarization assistant that can fetch and summarize news articles from various sources.

When a user asks for news or news summaries:
1. Use the fetch_news_headlines tool to get recent news articles based on categories
2. For detailed summaries, use the fetch_article_content tool to get the full article text
3. Use the summarize_text tool to create concise summaries of the articles
4. Present the information in a clear, organized format with sources cited

Always provide a balanced view of the news and cite your sources. If multiple perspectives exist on a topic, try to present different viewpoints.
"""'''
        elif agent_type == "weather_forecast":
            return '''SYSTEM_PROMPT = """
You are a helpful weather assistant that provides forecasts for cities around the world.

When a user asks about the weather in a city:
1. Use the get_city_coordinates tool to find the city's location
2. Use the get_weather_forecast tool to retrieve the forecast
3. Summarize the weather in a friendly, conversational manner

Include the high and low temperatures, general conditions, and chance of rain in your summary.
If you're asked about multiple cities, provide separate forecasts for each.
"""'''
        else:
            return f'''SYSTEM_PROMPT = """
You are a helpful {agent_description.lower()} that can assist users with various tasks.

When responding to user requests:
1. Think step-by-step about how to best help the user
2. Use the available tools when needed to gather information
3. Present information in a clear, concise manner
4. Be friendly and conversational in your responses

Always prioritize being helpful, accurate, and efficient in your assistance.
"""'''
    
    def generate_env_example(self, agent_type):
        """Generate the .env.example file based on agent type"""
        if agent_type == "news_summarization":
            return '''# Create a free API key at https://newsapi.org
API_KEY=your_newsapi_key_here'''
        elif agent_type == "weather_forecast":
            return '''# Create a free API key at https://www.weatherapi.com
API_KEY=your_weatherapi_key_here'''
        else:
            return '''# API key for external services
API_KEY=your_api_key_here'''
    
    def generate_requirements_txt(self, agent_type):
        """Generate the requirements.txt file based on agent type"""
        return '''pydantic-ai
httpx
python-dotenv'''
    
    def implement_agent_code(self, files):
        """Implement the agent code by writing files to disk"""
        # Create a unique directory for the agent
        agent_dir = f"agents/archon_agent_{int(time.time())}"
        os.makedirs(agent_dir, exist_ok=True)
        log_message(f"Created directory for agent: {agent_dir}")
        
        # Write each file
        for filename, content in files.items():
            file_path = os.path.join(agent_dir, filename)
            with open(file_path, 'w') as f:
                f.write(content)
            log_message(f"Created file: {file_path}")
        
        return agent_dir

def main():
    """Main function to demonstrate Claude Code using Archon as a tool"""
    log_message("=== Claude Code Using Archon as a Tool ===")
    
    # Example user prompt
    user_prompt = "Create a news summarization agent that can fetch and summarize news articles from various sources."
    
    # Initialize the Archon tool
    archon_tool = ArchonTool()
    
    # Create an agent using Archon
    success, message, files = archon_tool.create_agent(user_prompt)
    
    # Report results
    if success:
        log_message(f"✅ {message}")
        if isinstance(files, dict):
            log_message(f"Agent files: {list(files.keys())}")
    else:
        log_message(f"❌ {message}")
    
    log_message("=== End of Demonstration ===")

if __name__ == "__main__":
    main()