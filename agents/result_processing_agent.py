# agents/result_processing_agent.py (Corrected)

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from models.agent_state import AgentState
from utils.config import GEMINI_MODEL_NAME, COMBINED_PROMPT_TEMPLATE

def factual_rag_agent(state: AgentState) -> AgentState:
    """
    Handles the factual RAG path. It now correctly passes the detail_instruction
    to the final prompt to generate a cited and well-formatted response.
    """
    print("--- EXECUTING FACTUAL RAG PATH ---")
    
    llm = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL_NAME,
        temperature=0.1,
        convert_system_message_to_human=True,
        transport="rest", # Keep this for stability
    )
    
    prompt = ChatPromptTemplate.from_template(COMBINED_PROMPT_TEMPLATE)
    chain = prompt | llm
    
    history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in state.get("chat_history", [])])

    # --- THE FIX ---
    # We must pass the `detail_instruction` from the state into the prompt.
    # It was being ignored before.
    response_content = chain.invoke({
        "professor_context": state.get("vector_db_context", ""),
        "web_context": state.get("web_search_results", ""),
        "question": state.get("rewritten_query", state["query"]),
        "chat_history": history_str,
        "detail_instruction": state.get("detail_instruction", "Provide a detailed explanation.") # This is the crucial addition
    }).content

    # This logic correctly parses the final response and suggested questions
    main_answer = response_content
    suggestions = []
    if "---Suggested Questions---" in response_content:
        parts = response_content.split("---Suggested Questions---")
        main_answer = parts[0].strip()
        if len(parts) > 1:
            suggestions_text = parts[1].strip()
            suggestions = [q.strip().lstrip('0123456789. ') for q in suggestions_text.split('\n') if q.strip()]

    web_sources_md = "\n".join([f"- [{src}]({src})" for src in state.get("web_search_sources", [])])
    
    # We construct the final answer to be displayed in the UI
    final_formatted_answer = f"""
{main_answer}

---
### Sources Used
**From the Web (Clickable Links):**
{web_sources_md if web_sources_md else "No specific web sources were used."}
"""

    state["final_answer"] = final_formatted_answer
    state["suggested_questions"] = suggestions
    return state