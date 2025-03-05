#!/usr/bin/env python3
"""
Test Search Agent - Created with Archon

This is a test version that demonstrates the search agent with hardcoded inputs.
"""

import datetime
import json
import urllib.parse
import urllib.request
import urllib.error
import os
from typing import Dict, Any

def calculate_julian_date() -> Dict[str, Any]:
    """Calculate the current Julian date."""
    today = datetime.datetime.now()
    
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

def perform_search(website: str, query: str) -> Dict[str, Any]:
    """Perform a search on the specified website."""
    if not query:
        return {
            "error": "No search query provided",
            "results": []
        }
    
    # Use a simple approach for demonstration
    website_lower = website.lower()
    encoded_query = urllib.parse.quote(query)
    
    if "wikipedia" in website_lower:
        search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={encoded_query}&format=json"
        
        try:
            # Wikipedia has a public API that doesn't require authentication
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
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
            print(f"Wikipedia API error: {str(e)}")
    
    # For any other website or if Wikipedia fails, return simulated results
    return {
        "search_engine": website,
        "query": query,
        "results": [
            {
                "title": f"Result for {query} on {website}",
                "link": f"https://{website_lower.replace(' ', '')}.com/search?q={encoded_query}",
                "snippet": f"This is a simulated search result for {query} from {website}..."
            }
        ],
        "note": f"Using simulated results for {website}"
    }

def main():
    """Test the search agent with hardcoded examples."""
    print("=== Search Agent Test ===")
    print("This test will run two examples:")
    print("1. Search for 'climate change' on Wikipedia")
    print("2. Get today's Julian date")
    
    # Example 1: Search Wikipedia
    print("\n=== Example 1: Search for 'climate change' on Wikipedia ===")
    website = "Wikipedia"
    query = "climate change"
    
    print(f"Searching for '{query}' on {website}...")
    results = perform_search(website, query)
    
    print(f"\nSearch results for '{query}' on {results['search_engine']}:")
    
    if 'note' in results:
        print(f"Note: {results['note']}")
        
    if len(results.get('results', [])) > 0:
        for i, result in enumerate(results['results']):
            print(f"\n{i+1}. {result['title']}")
            print(f"   {result['link']}")
            print(f"   {result['snippet']}")
    else:
        print("No results found")
    
    # Example 2: Julian date
    print("\n\n=== Example 2: Get today's Julian date ===")
    date_info = calculate_julian_date()
    
    print("\nToday's Julian Date Information:")
    print(f"Julian Day Number: {date_info['julian_date']}")
    print(f"Gregorian Date: {date_info['gregorian_date']}")
    print(f"Day of Year: {date_info['day_of_year']}")
    print(f"\nThe Julian Day Number is used in astronomy and represents")
    print(f"the number of days since January 1, 4713 BCE (proleptic Julian calendar).")
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {str(e)}")
    except KeyboardInterrupt:
        print("Test interrupted by user.")