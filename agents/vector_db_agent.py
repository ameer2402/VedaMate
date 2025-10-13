from models.agent_state import AgentState
from utils.vector_db_utils import query_vector_db
import asyncio

async def vector_db_agent(state: AgentState) -> AgentState:
    """
    Queries the vector database using multiple queries in parallel.
    """
    print("--- SEARCHING VECTOR DB WITH MULTIPLE QUERIES ---")
    queries = state["generated_queries"]
    
    # Run all queries in parallel
    tasks = [query_vector_db(query, state["pdf_context_name"]) for query in queries]
    results = await asyncio.gather(*tasks)
    
    # --- De-duplicate and combine results ---
    unique_contexts = {} # Use dict for de-duplication based on content
    all_sources = []
    
    for res in results:
        context_parts = res["context_text"].split("\n\n---\n\n")
        sources_parts = res["sources"]
        
        for i, part in enumerate(context_parts):
            if part and part not in unique_contexts:
                unique_contexts[part] = sources_parts[i] if i < len(sources_parts) else ""

    final_context = "\n\n---\n\n".join(unique_contexts.keys())
    final_sources = list(unique_contexts.values())

    state["vector_db_context"] = final_context
    state["vector_db_sources"] = final_sources
    return state