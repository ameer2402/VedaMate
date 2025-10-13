import asyncio
from langgraph.graph import StateGraph, END
from models.agent_state import AgentState, create_initial_state
from agents.query_rewriter_agent import query_rewriter_agent
from agents.multi_query_agent import multi_query_agent
from agents.query_processing_agent import query_processing_agent
from agents.router_agent import router_agent
from agents.vector_db_agent import vector_db_agent
from agents.web_search_agent import web_search_agent
from agents.reasoning_agent import reasoning_agent
from agents.result_processing_agent import factual_rag_agent
from agents.greeting_agent import greeting_agent
from agents.question_generator_agent import question_generator_agent # IMPORT new agent
from typing import Optional, List, Dict

# This function reads the router's decision from the state and directs the workflow
def should_continue(state: AgentState) -> str:
    if state["query_type"] == "greeting":
        return "greeting_path"
    elif state["query_type"] == "question_generation":
        return "question_generation_path"
    elif state["query_type"] == "reasoning":
        return "reasoning_path"
    else:
        return "factual_path"

# Helper function to run searches in parallel for the factual path
async def parallel_search(state: AgentState) -> AgentState:
    vector_db_task = asyncio.create_task(vector_db_agent(state))
    web_search_task = asyncio.create_task(web_search_agent(state))
    vector_db_result, web_search_result = await asyncio.gather(vector_db_task, web_search_task)
    state.update(vector_db_result)
    state.update(web_search_result)
    return state

# Helper function to only retrieve PDF context for reasoning/generation paths
async def get_pdf_context_only(state: AgentState) -> AgentState:
    return await vector_db_agent(state)

# --- WORKFLOW DEFINITION ---
def create_workflow():
    """
    Creates the main LangGraph agent workflow with four distinct paths.
    """
    workflow = StateGraph(AgentState)

    # --- Define the Nodes ---
    workflow.add_node("query_rewriter", query_rewriter_agent)
    workflow.add_node("multi_query_generator", multi_query_agent)
    workflow.add_node("query_processor", query_processing_agent)
    workflow.add_node("router", router_agent)
    workflow.add_node("greeting_responder", greeting_agent)
    workflow.add_node("question_generator", question_generator_agent) # NEW node
    
    # Factual Path Nodes
    workflow.add_node("parallel_searcher", parallel_search)
    workflow.add_node("factual_rag_responder", factual_rag_agent)

    # Reasoning/Generation Path Nodes
    workflow.add_node("pdf_context_retriever", get_pdf_context_only)
    workflow.add_node("reasoning_responder", reasoning_agent) 
    
    # --- Define the Edges ---
    workflow.set_entry_point("query_rewriter")
    workflow.add_edge("query_rewriter", "multi_query_generator")
    workflow.add_edge("multi_query_generator", "query_processor")
    workflow.add_edge("query_processor", "router")

    # This is the conditional branch that directs the flow based on the router's decision.
    workflow.add_conditional_edges(
        "router",
        should_continue,
        {
            "factual_path": "parallel_searcher",
            "reasoning_path": "pdf_context_retriever",
            "question_generation_path": "pdf_context_retriever", # Reuse the same retriever
            "greeting_path": "greeting_responder",
        },
    )
    
    # Conditional branch from the context retriever to the correct agent
    workflow.add_conditional_edges(
        "pdf_context_retriever",
        # A simple lambda function to check the query type again
        lambda state: "reasoning" if state["query_type"] == "reasoning" else "question_generation",
        {
            "reasoning": "reasoning_responder",
            "question_generation": "question_generator"
        }
    )

    # Connect the end of each path to the final END node.
    workflow.add_edge("parallel_searcher", "factual_rag_responder")
    workflow.add_edge("factual_rag_responder", END)
    workflow.add_edge("reasoning_responder", END)
    workflow.add_edge("question_generator", END)
    workflow.add_edge("greeting_responder", END)

    # Compile the graph into a runnable application.
    return workflow.compile()

# Create a single, compiled instance of the workflow to be used by the app.
app_workflow = create_workflow()

async def multi_agent_query(
    query_text: str, pdf_context_name: str, chat_history: List[Dict[str, str]]
) -> Dict[str, any]:
    """
    Invokes the agent workflow and returns the final answer and suggested questions.
    """
    initial_state = create_initial_state(query_text, pdf_context_name, chat_history)
    final_state = await app_workflow.ainvoke(initial_state)
    
    return {
        "answer": final_state.get("final_answer", "Sorry, an error occurred and I could not generate a response."),
        "suggestions": final_state.get("suggested_questions", [])
    }