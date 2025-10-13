from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from models.agent_state import AgentState
from utils.config import GEMINI_MODEL_NAME
import re

def multi_query_agent(state: AgentState) -> AgentState:
    """
    Acts as a retrieval strategist using the globally configured Gemini model.
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
        else:
            state["generated_queries"] = [rewritten_query]
            return state

    # SIMPLIFIED: No extra options needed.
    llm = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL_NAME, # This will now resolve to "models/gemini-2.0-flash"
        temperature=0, # or other value
        convert_system_message_to_human=True,
        transport="rest",
    )

    prompt = ChatPromptTemplate.from_template(
        """You are an AI assistant who is an expert at converting a user's question into 3-5 diverse, high-quality search queries.
Provide these alternative queries separated by newlines.
Original question: {question}"""
    )
    
    chain = prompt | llm | StrOutputParser()
    
    generated_queries = chain.invoke({"question": rewritten_query}).split("\n")
    generated_queries.insert(0, rewritten_query)
    final_queries = list(dict.fromkeys([q.strip() for q in generated_queries if q.strip()]))
    
    print(f"--- GENERATED {len(final_queries)} QUERIES: {final_queries} ---")
    state["generated_queries"] = final_queries
    
    return state