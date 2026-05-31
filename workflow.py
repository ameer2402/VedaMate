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
from agents.question_generator_agent import question_generator_agent
from agents.question_answering_agent import question_answering_agent
from agents.quiz_agent import quiz_agent
from typing import Optional, List, Dict

def route_from_router(state: AgentState) -> str:
    if state.get("mode") == "quiz":
        return "process_path"
    if state["query_type"] in ["greeting", "general"]:
        return "greeting_path"
    return "process_path"

def route_from_processor(state: AgentState) -> str:
    if state.get("mode") == "quiz":
        return "quiz_path"
    if state["query_type"] == "question_generation":
        return "question_generation_path"
    elif state["query_type"] == "reasoning":
        return "reasoning_path"
    elif state["query_type"] == "question_answering":
        return "question_answering_path"
    else:
        return "factual_path"

async def parallel_search(state: AgentState) -> AgentState:
    vector_db_task = asyncio.create_task(vector_db_agent(state))
    web_search_task = asyncio.create_task(web_search_agent(state))
    vector_db_result, web_search_result = await asyncio.gather(vector_db_task, web_search_task)
    state.update(vector_db_result)
    state.update(web_search_result)
    return state

async def get_pdf_context_only(state: AgentState) -> AgentState:
    return await vector_db_agent(state)

def create_workflow():
    workflow = StateGraph(AgentState)

    # --- Define the Nodes ---
    workflow.add_node("query_rewriter", query_rewriter_agent)
    workflow.add_node("multi_query_generator", multi_query_agent)
    workflow.add_node("query_processor", query_processing_agent)
    workflow.add_node("router", router_agent)
    workflow.add_node("greeting_responder", greeting_agent)
    workflow.add_node("question_generator", question_generator_agent)
    workflow.add_node("question_answering_responder", question_answering_agent)
    workflow.add_node("quiz_responder", quiz_agent)
    
    workflow.add_node("parallel_searcher", parallel_search)
    workflow.add_node("factual_rag_responder", factual_rag_agent)

    workflow.add_node("pdf_context_retriever", get_pdf_context_only)
    workflow.add_node("reasoning_responder", reasoning_agent) 
    
    # --- Define the Edges ---
    workflow.set_entry_point("router")

    workflow.add_conditional_edges(
        "router",
        route_from_router,
        {
            "greeting_path": "greeting_responder",
            "process_path": "query_rewriter",
        },
    )

    workflow.add_edge("query_rewriter", "multi_query_generator")
    workflow.add_edge("multi_query_generator", "query_processor")

    workflow.add_conditional_edges(
        "query_processor",
        route_from_processor,
        {
            "factual_path": "parallel_searcher",
            "reasoning_path": "pdf_context_retriever",
            "question_generation_path": "pdf_context_retriever",
            "question_answering_path": "parallel_searcher",
            "quiz_path": "pdf_context_retriever",
        },
    )
    
    workflow.add_conditional_edges(
        "pdf_context_retriever",
        lambda state: "quiz" if state.get("mode") == "quiz" else ("reasoning" if state["query_type"] == "reasoning" else "question_generation"),
        {
            "quiz": "quiz_responder",
            "reasoning": "reasoning_responder",
            "question_generation": "question_generator"
        }
    )

    workflow.add_conditional_edges(
        "parallel_searcher",
        lambda state: "question_answering" if state["query_type"] == "question_answering" else "factual",
        {
            "factual": "factual_rag_responder",
            "question_answering": "question_answering_responder"
        }
    )

    workflow.add_edge("factual_rag_responder", END)
    workflow.add_edge("question_answering_responder", END)
    workflow.add_edge("reasoning_responder", END)
    workflow.add_edge("question_generator", END)
    workflow.add_edge("greeting_responder", END)
    workflow.add_edge("quiz_responder", END)
    return workflow.compile()

app_workflow = create_workflow()

from utils.vector_db_utils import get_semantic_cache, set_semantic_cache

async def multi_agent_query(
    query_text: str, pdf_context_name: str, chat_history: List[Dict[str, str]],
    persona: Dict[str, str] = None, current_topic: str = "General Overview", mode: str = "chat"
) -> Dict[str, any]:
    if persona is None:
        persona = {}
        
    # Apply Semantic Caching if in chat mode
    if mode == "chat":
        cached = get_semantic_cache(query_text, pdf_context_name)
        if cached:
            print("--- SEMANTIC CACHE HIT ---")
            return cached

    initial_state = create_initial_state(query_text, pdf_context_name, chat_history, persona, current_topic, mode)
    final_state = await app_workflow.ainvoke(initial_state)
    
    # Parse citation snippets
    citation_snippets = {}
    vector_db_context = final_state.get("vector_db_context", "")
    if vector_db_context:
        for block in vector_db_context.split("\n\n---\n\n"):
            if "Source Page: " in block and "Content: " in block:
                try:
                    parts = block.split("Content: ", 1)
                    header = parts[0].strip()
                    content = parts[1].strip()
                    page_num = header.replace("Source Page: ", "").strip()
                    if page_num not in citation_snippets:
                        citation_snippets[page_num] = []
                    if content not in citation_snippets[page_num]:
                        citation_snippets[page_num].append(content)
                except Exception:
                    pass

    answer = final_state.get("final_answer", "Sorry, an error occurred and I could not generate a response.")
    suggestions = final_state.get("suggested_questions", [])
    
    # Cache the result
    if mode == "chat":
        set_semantic_cache(query_text, answer, suggestions, citation_snippets, pdf_context_name)
        
    return {
        "answer": answer,
        "suggestions": suggestions,
        "citation_snippets": citation_snippets
    }