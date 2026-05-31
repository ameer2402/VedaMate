from typing import TypedDict, Optional, List, Dict

class AgentState(TypedDict):
    # --- Inputs ---
    query: str
    pdf_context_name: str
    chat_history: Optional[List[Dict[str, str]]]
    persona: Dict[str, str]
    current_topic: str
    mode: str

    # --- State variables ---
    query_type: str
    detail_instruction: str
    rewritten_query: Optional[str]
    generated_queries: Optional[List[str]] # NEW: To hold multiple search queries
    vector_db_context: Optional[str]
    web_search_results: Optional[str]
    web_search_sources: Optional[List[str]]
    
    # --- Final Outputs ---
    final_answer: Optional[str]
    suggested_questions: Optional[List[str]]

def create_initial_state(
    query: str, pdf_context_name: str, chat_history: List[Dict[str, str]],
    persona: Dict[str, str], current_topic: str, mode: str
) -> AgentState:
    return AgentState(
        query=query,
        pdf_context_name=pdf_context_name,
        chat_history=chat_history,
        persona=persona,
        current_topic=current_topic,
        mode=mode,
        query_type="",
        detail_instruction="",
        rewritten_query=None,
        generated_queries=[], # Initialize as empty list
        vector_db_context=None,
        web_search_results=None,
        web_search_sources=[],
        final_answer=None,
        suggested_questions=[],
    )