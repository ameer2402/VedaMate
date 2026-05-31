from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from models.agent_state import AgentState
from utils.config import GEMINI_MODEL_NAME, QUIZ_GENERATION_PROMPT

def quiz_agent(state: AgentState) -> AgentState:
    print("--- EXECUTING QUIZ GENERATION PATH ---")
    
    llm = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL_NAME,
        temperature=0.3,
        convert_system_message_to_human=True,
    )
    
    prompt = ChatPromptTemplate.from_template(QUIZ_GENERATION_PROMPT)
    chain = prompt | llm
    
    persona_dict = state.get("persona", {})
    persona_str = f"Education Level: {persona_dict.get('education_level', 'Not specified')}\nInterests: {persona_dict.get('interests', 'Not specified')}"
    
    response_content = chain.invoke({
        "professor_context": state.get("vector_db_context", ""),
        "question": state.get("query", ""),
        "persona_context": persona_str,
        "topic_context": state.get("current_topic", "General Topic")
    }).content

    state["final_answer"] = response_content
    state["suggested_questions"] = []
    return state
