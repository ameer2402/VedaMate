from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from models.agent_state import AgentState
from utils.config import GEMINI_MODEL_NAME
import json

def router_agent(state: AgentState) -> AgentState:
    """
    Classifies the user's query using the globally configured Gemini model.
    """
    # Quick greeting check in Python to save LLM quota and speed up greetings
    query_clean = state["query"].strip().lower().rstrip("!?.").strip()
    greetings = {
        "hello", "hi", "hii", "hey", "greetings", "good morning", "good afternoon", 
        "good evening", "howdy", "yo", "hello there", "hello vedamate", "hello veda mate",
        "hii and hello", "hi and hello", "hii hello", "hello tutor", "hello ai"
    }
    if query_clean in greetings:
        print("--- ROUTER DECISION (PYTHON FAST PATH): GREETING ---")
        state["query_type"] = "greeting"
        return state

    # SIMPLIFIED: No extra options needed. The global config in app.py is used.
    llm = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL_NAME, # This will now resolve to "models/gemini-2.0-flash"
        temperature=0, # or other value
        convert_system_message_to_human=True,
        transport="rest",
    )

    prompt = ChatPromptTemplate.from_template(
        """Given the user's query, classify it as "factual", "reasoning", "greeting", "general", "question_generation", or "question_answering".
- "greeting": The user is saying hello.
- "general": The user asks a general query, off-topic question, or chit-chat that is unrelated to the textbook topics (e.g., "What is today's date?", "Who are you?", "Tell me a joke", "What is the capital of Spain?", etc.).
- "question_answering": The user has provided a list of one or more explicit questions to be answered.
- "question_generation": The user wants you to create questions, a quiz, or a test based on the document.
- "reasoning": The user asks for a plan, summary, or subjective opinion.
- "factual": The user asks a single, specific academic question to be looked up from the textbook.

Respond with a JSON object with a single key "query_type".

Query: {query}"""
    )

    chain = prompt | llm
    try:
        query_for_routing = state.get("rewritten_query") or state["query"]
        response_str = chain.invoke({"query": query_for_routing})
        response_content = response_str.content.strip().replace("```json", "").replace("```", "")
        response_json = json.loads(response_content)
        query_type = response_json.get("query_type", "factual")
        print(f"--- ROUTER DECISION: {query_type.upper()} ---")
        state["query_type"] = query_type
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"--- ROUTER FAILED ({e}): Defaulting to Factual ---")
        state["query_type"] = "factual"
        
    return state