# agents/greeting_agent.py
from models.agent_state import AgentState
import random

def greeting_agent(state: AgentState) -> AgentState:
    """
    Provides a simple, friendly response to a greeting.
    """
    print("--- EXECUTING GREETING PATH ---")
    
    greetings = [
        "Hello! How can I help you with your document today?",
        "Hi there! What can I help you learn or plan?",
        "Greetings! I'm ready to assist. Feel free to ask me anything about your PDF."
    ]
    
    state["final_answer"] = random.choice(greetings)
    state["suggested_questions"] = [] # No suggestions for a simple greeting
    
    return state