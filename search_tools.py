import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from langchain.tools import tool
from tavily import TavilyClient
from duckduckgo_search import DDGS

@tool
def fetch_web_search(query: str, tavily_api_key: Optional[str] = None, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Executes web research on a given topic.
    Uses Tavily if an API key is provided, otherwise falls back to DuckDuckGo.
    """
    search_results: List[Dict[str, Any]] = []

    # If tavily key is provided
    if tavily_api_key and tavily_api_key.strip():
        try:
            client = TavilyClient(api_key=tavily_api_key.strip())
            response = client.search(query=query, max_results=max_results, search_depth='advanced')

            for item in response.get("results", []):
                search_results.append({
                    "title": item.get("title", "Untitled Source"),
                    "url": item.get("url", ""),
                    "content": item.get("content", "")
                })
            if search_results:
                return search_results
        except Exception as e:
            print(f"[Warning] Tavily search failed ({e}). Falling back to DuckDuckGo...")

    # Fallback: DuckDuckGo
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(keywords=query, max_results=max_results))
            for item in results:
                search_results.append({
                    "title": item.get("title", "Untitled Source"),
                    "url": item.get("href", ""),
                    "content": item.get("body", "")
                })
    except Exception as err:
        print(f"[Error] DuckDuckGo search error: {err}")

    return search_results
