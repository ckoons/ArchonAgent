#!/usr/bin/env python3
"""
Tools for the Search Agent

This module provides the tools used by the search agent to perform web searches
and calculate Julian dates.
"""

import datetime
import json
import urllib.parse
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, List, Annotated

def calculate_julian_date() -> Dict[str, Any]:
    """
    Calculate the current Julian date.
    
    Returns:
        Dict: Contains the Julian date and additional information
    """
    today = datetime.datetime.now()
    
    # Calculate Julian date
    # Formula: JD = 367 * year - INT(7 * (year + INT((month + 9) / 12)) / 4) - 
    #               INT(3 * (INT((year + (month - 9) / 7) / 100) + 1) / 4) + 
    #               INT(275 * month / 9) + day + 1721028.5
    
    year = today.year
    month = today.month
    day = today.day
    
    # Simplified version for current date (approximation)
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    
    julian_day = day + ((153 * m + 2) // 5) + 365 * y + (y // 4) - (y // 100) + (y // 400) - 32045
    
    return {
        "julian_date": julian_day,
        "gregorian_date": today.strftime("%Y-%m-%d"),
        "day_of_year": today.timetuple().tm_yday,
        "calculation": "Used standard Julian Day Number formula"
    }

def perform_search(
    website: Annotated[str, "The website to search (e.g., Google, Bing, Wikipedia)"],
    query: Annotated[str, "The search query"]
) -> Dict[str, Any]:
    """
    Perform a search on the specified website.
    
    Args:
        website: The website to search (e.g., Google, Bing, Wikipedia)
        query: The search query
        
    Returns:
        Dict: Contains the search results and metadata
    """
    if not query:
        return {
            "error": "No search query provided",
            "results": []
        }
    
    # Use a simple approach for demonstration
    # In a real implementation, this would use proper API clients or web scraping
    
    search_url = ""
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    
    # Determine which search engine to use
    website_lower = website.lower()
    encoded_query = urllib.parse.quote(query)
    
    if "google" in website_lower:
        search_url = f"https://www.googleapis.com/customsearch/v1?q={encoded_query}&key=$SEARCH_API_KEY"
        # Note: In a real implementation, you would use the Google Custom Search API
        # This requires an API key and is rate-limited for free users
        
        # For demo purposes (no real API), return simulated results
        return {
            "search_engine": "Google",
            "query": query,
            "results": [
                {
                    "title": f"Search result 1 for {query}",
                    "link": f"https://example.com/result1?q={encoded_query}",
                    "snippet": f"This is a simulated search result for {query} with detailed information..."
                },
                {
                    "title": f"Search result 2 for {query}",
                    "link": f"https://example.com/result2?q={encoded_query}",
                    "snippet": f"Another simulated search result with information about {query}..."
                }
            ],
            "note": "Using simulated results for demonstration purposes"
        }
        
    elif "bing" in website_lower:
        search_url = f"https://api.bing.microsoft.com/v7.0/search?q={encoded_query}"
        # Note: The Bing Search API requires a subscription key
        
        # For demo purposes (no real API), return simulated results
        return {
            "search_engine": "Bing",
            "query": query,
            "results": [
                {
                    "title": f"Bing result 1 for {query}",
                    "link": f"https://example.com/bing1?q={encoded_query}",
                    "snippet": f"This is a simulated Bing search result for {query}..."
                },
                {
                    "title": f"Bing result 2 for {query}",
                    "link": f"https://example.com/bing2?q={encoded_query}",
                    "snippet": f"Another simulated Bing result with details about {query}..."
                }
            ],
            "note": "Using simulated results for demonstration purposes"
        }
        
    elif "wikipedia" in website_lower:
        search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={encoded_query}&format=json"
        
        try:
            # Wikipedia has a public API that doesn't require authentication
            request = urllib.request.Request(search_url, headers={"User-Agent": user_agent})
            with urllib.request.urlopen(request) as response:
                data = json.loads(response.read().decode())
                
                # Extract the search results
                search_results = []
                for item in data.get("query", {}).get("search", []):
                    search_results.append({
                        "title": item.get("title", "Unknown"),
                        "link": f"https://en.wikipedia.org/wiki/{urllib.parse.quote(item.get('title', ''))}",
                        "snippet": item.get("snippet", "No description available")
                    })
                
                return {
                    "search_engine": "Wikipedia",
                    "query": query,
                    "results": search_results[:3],  # Limit to top 3 results
                    "note": "Real results from Wikipedia API"
                }
        except Exception as e:
            # Fallback to simulated results if the API call fails
            return {
                "search_engine": "Wikipedia",
                "query": query,
                "results": [
                    {
                        "title": f"Wikipedia: {query}",
                        "link": f"https://en.wikipedia.org/wiki/{encoded_query}",
                        "snippet": f"Simulated Wikipedia entry about {query}..."
                    }
                ],
                "error": str(e),
                "note": "Using simulated results due to API error"
            }
    
    else:
        # For any other website, return a generic response
        return {
            "search_engine": website,
            "query": query,
            "results": [
                {
                    "title": f"Result for {query} on {website}",
                    "link": f"https://{website.lower().replace(' ', '')}.com/search?q={encoded_query}",
                    "snippet": f"This is a simulated search result for {query} from {website}..."
                }
            ],
            "note": f"Using simulated results for {website}"
        }