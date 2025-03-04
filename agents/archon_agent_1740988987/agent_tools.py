from pydantic_ai import RunContext
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
