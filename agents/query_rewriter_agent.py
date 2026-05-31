from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from models.agent_state import AgentState
from utils.config import GEMINI_MODEL_NAME # CORRECTED IMPORT

def query_rewriter_agent(state: AgentState) -> AgentState:
    """
    Conditionally rewrites the user's query using the Gemini model.
    """
    history = state.get("chat_history")
    if not history or len(state["query"]) > 50:
        print("--- SKIPPING REWRITE (No history or long query) ---")
        state["rewritten_query"] = state["query"]
        return state

    llm = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL_NAME, # CORRECTED VARIABLE
        temperature=0,
        convert_system_message_to_human=True
    )

    prompt = ChatPromptTemplate.from_template(
        """Analyze the chat history and the latest user query.
- If the latest query is a follow-up question that depends on the history (e.g., "why?", "tell me more"), rephrase it into a standalone question.
- If the latest query is a completely new topic, respond with the original query itself, without any changes.

Chat History:
{chat_history}

Latest User Query: "{question}"

Standalone question or original query:"""
    )
    
    history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
    chain = prompt | llm
    response = chain.invoke({"chat_history": history_str, "question": state["query"]})
    
    rewritten_query = response.content.strip()
    print(f"--- REWRITTEN QUERY: {rewritten_query} ---")
    state["rewritten_query"] = rewritten_query
    return state