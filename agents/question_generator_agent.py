from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from models.agent_state import AgentState
from utils.config import GEMINI_MODEL_NAME, QUESTION_GENERATION_PROMPT_TEMPLATE

def question_generator_agent(state: AgentState) -> AgentState:
    """
    Invokes the Gemini model to generate questions based on the provided context.
    """
    print("--- EXECUTING QUESTION GENERATION PATH ---")
    # SIMPLIFIED: No extra options needed.
    llm = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL_NAME, # This will now resolve to "models/gemini-2.0-flash"
        temperature=0, # or other value
        convert_system_message_to_human=True,
        transport="rest",
    )
    
    prompt = ChatPromptTemplate.from_template(QUESTION_GENERATION_PROMPT_TEMPLATE)
    chain = prompt | llm
    
    persona_dict = state.get("persona", {})
    persona_str = f"Education Level: {persona_dict.get('education_level', 'Not specified')}\\nInterests: {persona_dict.get('interests', 'Not specified')}"

    response_content = chain.invoke({
        "question": state.get("rewritten_query") or state["query"],
        "professor_context": state.get("vector_db_context", ""),
        "persona_context": persona_str,
        "topic_context": state.get("current_topic", "General Topic")
    }).content

    state["final_answer"] = response_content
    state["suggested_questions"] = []
    
    return state