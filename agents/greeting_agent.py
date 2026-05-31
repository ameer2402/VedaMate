# agents/greeting_agent.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from models.agent_state import AgentState
from utils.config import GEMINI_MODEL_NAME
from datetime import datetime

def greeting_agent(state: AgentState) -> AgentState:
    """
    Provides a personalized, topic-aware, and persona-tailored response to a greeting or general off-topic/chitchat question using Gemini.
    """
    print("--- EXECUTING GREETING/GENERAL CHITCHAT PATH ---")
    
    try:
        llm = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL_NAME,
            temperature=0.7,
            convert_system_message_to_human=True,
            transport="rest",
        )
        
        prompt = ChatPromptTemplate.from_template(
            """You are VedaMate, an enthusiastic and friendly AI Tutor helping a student.
Student Profile:
- Education Level: {education_level}
- Interests/Hobbies: {interests}

Current Topic of Study: {current_topic}
Current Date/Time: {current_date}

The student asked you: "{query}"

INSTRUCTIONS:
1. If the query is a simple greeting (like hello, hi, hey), respond with a very friendly, enthusiastic greeting. Tailor your tone and style to the student's education level and interests. Mention the current topic they are studying, and invite them to ask questions or dive into the material. Keep it short (1-2 sentences).
2. If the query is a general question or chit-chat unrelated to the textbook or current topic (like "What is today's date?", "Who are you?", "Tell me a joke", "What is the capital of France?", etc.), answer it directly, accurately, and in a friendly manner. Utilize the current date provided if the question asks for the date. Do NOT try to search the textbook or reference it if it's completely unrelated. Keep it concise (1-3 sentences).

Do not output any JSON or RAG formatting. Just output the friendly response text directly."""
        )
        
        chain = prompt | llm
        
        persona = state.get("persona", {})
        education_level = persona.get("education_level", "Middle School")
        interests = persona.get("interests", "Sports")
        current_topic = state.get("current_topic", "General Science")
        query = state.get("query", "Hello")
        current_date_str = datetime.now().strftime("%A, %B %d, %Y")
        
        response = chain.invoke({
            "education_level": education_level,
            "interests": interests,
            "current_topic": current_topic,
            "query": query,
            "current_date": current_date_str
        })
        
        state["final_answer"] = response.content.strip()
    except Exception as e:
        print(f"Greeting Agent LLM call failed ({e}), using fallback greeting.")
        fallback_greetings = [
            f"Hey there! Ready to dive into {state.get('current_topic', 'the topic')} today? What questions do you have?",
            f"Hello! Let's explore {state.get('current_topic', 'the topic')} together. How can I help you study?",
            f"Hi! Excited to learn about {state.get('current_topic', 'the topic')} with you. What would you like to ask first?"
        ]
        import random
        state["final_answer"] = random.choice(fallback_greetings)
        
    state["suggested_questions"] = []
    return state