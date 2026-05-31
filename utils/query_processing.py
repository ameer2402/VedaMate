from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from .config import LOCAL_LLM_MODEL, COMBINED_PROMPT_TEMPLATE

def process_query_with_llm(state):
    """
    Invokes the local LLM with the combined context and detail instruction.
    """
    llm = ChatOllama(model=LOCAL_LLM_MODEL, temperature=0.1) # Slightly increased temp for more fluid language

    prompt_template = ChatPromptTemplate.from_template(COMBINED_PROMPT_TEMPLATE)
    
    prompt_params = {
        "professor_context": state.get("vector_db_context", ""),
        "professor_sources": "\n".join(state.get("vector_db_sources", [])),
        "web_context": state.get("web_search_results", ""),
        "question": state.get("query", ""),
        "detail_instruction": state.get("detail_instruction", "Provide a detailed explanation.") # Pass the new instruction
    }

    chain = prompt_template | llm
    response = chain.invoke(prompt_params)
    
    return response.content