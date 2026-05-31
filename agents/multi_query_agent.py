from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from models.agent_state import AgentState
from utils.config import GEMINI_MODEL_NAME
import re

def multi_query_agent(state: AgentState) -> AgentState:
    """
    Acts as a retrieval strategist. To conserve API quota and avoid 429 rate limit errors,
    it maps the rewritten query directly to generated queries without making an extra LLM call.
    """
    print("--- MULTI-QUERY / QUESTION EXTRACTION ---")
    rewritten_query = state.get("rewritten_query", state["query"])
    
    if state.get("query_type") == "question_answering":
        questions = re.findall(r'([^?]+?\?)', rewritten_query)
        if questions:
            final_queries = [q.strip() for q in questions]
            print(f"--- EXTRACTED {len(final_queries)} QUESTIONS for retrieval: {final_queries} ---")
            state["generated_queries"] = final_queries
            return state

    state["generated_queries"] = [rewritten_query]
    return state