# agents/web_search_agent.py (Corrected)

from models.agent_state import AgentState
from utils.web_search_utils import perform_web_search
import asyncio

async def web_search_agent(state: AgentState) -> AgentState:
    """
    Performs multiple web searches in parallel by running the synchronous
    search function in a thread pool to avoid blocking the main async loop.
    """
    print("--- SEARCHING WEB WITH MULTIPLE QUERIES ---")
    queries = state.get("generated_queries", [])
    if not queries:
        print("--- No queries for web search. Skipping. ---")
        return state

    # --- THE FIX ---
    # The function `perform_web_search` is synchronous (def), not async (async def).
    # We cannot directly await it. Instead, we must run this "blocking" function
    # in a separate thread for each query so it doesn't freeze the application.
    # `asyncio.to_thread` is the modern and clean way to do this.

    try:
        # Create a list of awaitable tasks, where each task runs the
        # synchronous function in a separate thread.
        tasks = [asyncio.to_thread(perform_web_search, query) for query in queries]

        # Now we can correctly gather the results from these concurrent threads.
        results = await asyncio.gather(*tasks)

    except Exception as e:
        print(f"--- ERROR during threaded web search: {e} ---")
        state["web_search_results"] = "Web search failed."
        state["web_search_sources"] = []
        return state
    
    # --- De-duplicate and combine results (Your original logic is good) ---
    unique_contexts = {} # Use URL as key for de-duplication
    
    for res in results:
        # Gracefully handle cases where a search might fail and return None or an empty dict
        if not res or not res.get("sources"):
            continue
            
        for i, source_url in enumerate(res["sources"]):
            if source_url not in unique_contexts:
                # Ensure context_parts exists and index is valid
                if "context_parts" in res and i < len(res["context_parts"]):
                    unique_contexts[source_url] = res["context_parts"][i]
                else:
                    unique_contexts[source_url] = "" # Assign empty string if context is missing
                
    final_context = "\n\n".join(unique_contexts.values())
    final_sources = list(unique_contexts.keys())

    print(f"--- WEB SEARCH COMPLETED. Found {len(final_sources)} unique sources. ---")
    
    state["web_search_results"] = final_context
    state["web_search_sources"] = final_sources
    return state