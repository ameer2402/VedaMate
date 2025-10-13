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
from googleapiclient.discovery import build
import os
import logging
from typing import Dict, List

def perform_web_search(query: str) -> Dict[str, any]:
    """
    Performs a web search using the Google Programmable Search Engine API.
    """
    try:
        api_key = os.environ.get("GOOGLE_API_KEY")
        cse_id = os.environ.get("GOOGLE_CSE_ID")
        
        service = build("customsearch", "v1", developerKey=api_key)
        res = service.cse().list(q=query, cx=cse_id, num=3).execute()
        
        items = res.get("items", [])
        
        context_parts = [item.get("snippet", "") for item in items]
        sources = [item.get("link", "") for item in items]
        
        return {"context_parts": context_parts, "sources": sources}
    except Exception as e:
        logging.error(f"Failed to perform Google web search: {str(e)}")
        # Check if the error is due to a missing CSE ID
        if "Required parameter: cx" in str(e):
            logging.error("The GOOGLE_CSE_ID might be missing from your .env file.")
            return {"context_parts": ["Web search failed: Programmable Search Engine ID (cx) is missing."], "sources": []}
        return {"context_parts": ["Web search failed."], "sources": []}