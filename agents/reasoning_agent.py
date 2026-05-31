from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from models.agent_state import AgentState
from utils.config import GEMINI_MODEL_NAME, REASONING_PROMPT_TEMPLATE

def reasoning_agent(state: AgentState) -> AgentState:
    """
    Handles analytical or subjective tasks and parses suggestions from the output using Gemini.
    """
    print("--- EXECUTING REASONING PATH ---")
    # SIMPLIFIED: No extra options needed.
    llm = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL_NAME, # This will now resolve to "models/gemini-2.0-flash"
        temperature=0, # or other value
        convert_system_message_to_human=True,
        transport="rest",
    )
    
    prompt = ChatPromptTemplate.from_template(REASONING_PROMPT_TEMPLATE)
    chain = prompt | llm
    
    history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in state.get("chat_history", [])])

    persona_dict = state.get("persona", {})
    persona_str = f"Education Level: {persona_dict.get('education_level', 'Not specified')}\\nInterests: {persona_dict.get('interests', 'Not specified')}"

    response_content = chain.invoke({
        "question": state.get("rewritten_query") or state["query"],
        "professor_context": state.get("vector_db_context", ""),
        "chat_history": history_str,
        "persona_context": persona_str,
        "topic_context": state.get("current_topic", "General Topic")
    }).content

    import re
    main_answer = response_content
    suggestions = []
    
    # Robust suggested questions matching
    pattern = r"(?:---|###|\*\*|\*)*\s*Suggested Questions\s*(?::|---|###|\*\*|\*)*"
    parts = re.split(pattern, response_content, flags=re.IGNORECASE)
    if len(parts) > 1:
        main_answer = parts[0].strip()
        suggestions_text = parts[1].strip()
        raw_lines = suggestions_text.split('\n')
        for line in raw_lines:
            line_str = line.strip()
            if "source" in line_str.lower() or "---" in line_str:
                break
            if re.match(r'^(\d+[\.\)]|[-*•])', line_str):
                clean_q = re.sub(r'^(\d+[\.\)]|[-*•])\s*', '', line_str).strip()
                if clean_q:
                    suggestions.append(clean_q)

    state["final_answer"] = main_answer
    state["suggested_questions"] = suggestions
    return state