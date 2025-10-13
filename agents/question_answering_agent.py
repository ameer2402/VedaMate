from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from models.agent_state import AgentState
from utils.config import GEMINI_MODEL_NAME, QUESTION_ANSWERING_PROMPT_TEMPLATE

def question_answering_agent(state: AgentState) -> AgentState:
    """
    Takes a list of questions and answers them sequentially using the Gemini model.
    """
    print("--- EXECUTING QUESTION ANSWERING PATH ---")
    # SIMPLIFIED: No extra options needed.
    llm = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL_NAME, # This will now resolve to "models/gemini-2.0-flash"
        temperature=0, # or other value
        convert_system_message_to_human=True,
        transport="rest",
    )
    
    prompt = ChatPromptTemplate.from_template(QUESTION_ANSWERING_PROMPT_TEMPLATE)
    chain = prompt | llm
    
    response_content = chain.invoke({
        "question": state.get("rewritten_query", state["query"]),
        "professor_context": state.get("vector_db_context", ""),
        "web_context": state.get("web_search_results", "")
    }).content

    state["final_answer"] = response_content
    state["suggested_questions"] = []
    
    return state