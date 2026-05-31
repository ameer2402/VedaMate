# from tavily import TavilyClient
# import os
# import logging
# from typing import Dict, List

# tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

# async def perform_web_search(query: str) -> Dict[str, any]:
#     """
#     Performs a web search and returns context parts and source URLs.
#     """
#     try:
#         results = tavily_client.search(query=query, search_depth="advanced", max_results=3)
#         context_parts = [res["content"] for res in results["results"]]
#         sources = [res["url"] for res in results["results"]]
#         return {"context_parts": context_parts, "sources": sources}
#     except Exception as e:
#         logging.error(f"Failed to perform web search: {str(e)}")
#         return {"context_parts": ["Web search failed."], "sources": []}

# utils/web_search_utils.py
import os
import logging
import requests
from typing import Dict
from dotenv import load_dotenv

# Ensure environment variables are loaded/reloaded from .env using absolute path
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'), override=True)
from googleapiclient.discovery import build

def perform_web_search(query: str) -> Dict[str, any]:
    """
    Performs a web search using Tavily API (if configured) or Google Programmable Search Engine.
    """
    tavily_key = os.environ.get("TAVILY_API_KEY")
    
    # 1. Try Tavily Search first (Recommended & much easier for LLM usage)
    if tavily_key:
        try:
            logging.info(f"Performing web search using Tavily for query: '{query}'")
            response = requests.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": tavily_key,
                    "query": query,
                    "search_depth": "basic",
                    "max_results": 3
                },
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                context_parts = [res.get("content", "") for res in results]
                sources = [res.get("url", "") for res in results]
                return {"context_parts": context_parts, "sources": sources}
            else:
                logging.error(f"Tavily API responded with status {response.status_code}: {response.text}")
        except Exception as e:
            logging.error(f"Failed to perform Tavily web search: {str(e)}")

    # 2. Fall back to Google Custom Search API
    api_key = os.environ.get("GOOGLE_API_KEY")
    cse_id = os.environ.get("GOOGLE_CSE_ID")
    
    if api_key and cse_id:
        # Prevent calling Google Custom Search with account-bound keys starting with AQ
        if api_key.startswith("AQ."):
            logging.warning("Skipping Google Custom Search because the configured GOOGLE_API_KEY is account-bound (AQ...) and not supported by Custom Search.")
            return {"context_parts": ["Web search skipped: Account-bound keys (AQ...) cannot be used for Google Custom Search."], "sources": []}
            
        try:
            logging.info(f"Performing web search using Google Custom Search for query: '{query}'")
            service = build("customsearch", "v1", developerKey=api_key)
            res = service.cse().list(q=query, cx=cse_id, num=3).execute()
            
            items = res.get("items", [])
            context_parts = [item.get("snippet", "") for item in items]
            sources = [item.get("link", "") for item in items]
            
            return {"context_parts": context_parts, "sources": sources}
        except Exception as e:
            logging.error(f"Failed to perform Google web search: {str(e)}")
            if "Required parameter: cx" in str(e):
                return {"context_parts": ["Web search failed: Programmable Search Engine ID (cx) is missing."], "sources": []}
                
    # 3. Graceful Fallback (if no search keys are configured or search failed)
    return {
        "context_parts": ["Web search is currently unconfigured or unavailable. Please check your TAVILY_API_KEY or GOOGLE_API_KEY settings."],
        "sources": []
    }