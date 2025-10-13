from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
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

    response_content = chain.invoke({
        "question": state.get("rewritten_query", state["query"]),
        "professor_context": state.get("vector_db_context", ""),
        "chat_history": history_str
    }).content

    main_answer = response_content
    suggestions = []
    if "---Suggested Questions---" in response_content:
        parts = response_content.split("---Suggested Questions---")
        main_answer = parts[0].strip()
        if len(parts) > 1:
            suggestions_text = parts[1].strip()
            suggestions = [q.strip().lstrip('0123456789. ') for q in suggestions_text.split('\n') if q.strip()]

    state["final_answer"] = main_answer
    state["suggested_questions"] = suggestions
    return state