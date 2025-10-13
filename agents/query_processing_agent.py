from models.agent_state import AgentState

def query_processing_agent(state: AgentState) -> AgentState:
    """
    Analyzes the user's query to determine the desired level of detail for the answer.
    """
    query = state["query"].lower()
    
    # Define keywords that suggest a brief answer
    simple_keywords = ["simple", "brief", "short", "summarize", "in a nutshell"]

    if any(keyword in query for keyword in simple_keywords):
        state["detail_instruction"] = "Provide a brief, simple, and concise explanation suitable for a quick overview. Use 1-2 paragraphs."
    else:
        state["detail_instruction"] = "Provide a comprehensive, detailed explanation like a teacher explaining a core concept to a student. Use multiple paragraphs and be thorough."

    state["processed_query"] = state["query"]
    return state