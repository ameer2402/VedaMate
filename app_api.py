import os
import asyncio
import re
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file using absolute path
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'), override=True)

from utils.config import PDF_STORAGE_PATH
from utils.vector_db_utils import process_and_store_pdf, query_vector_db
from utils.metadata_manager import load_metadata, save_metadata
from utils.syllabus_analyzer import analyze_syllabus
from utils.profile_manager import load_profile, save_profile
from utils.concept_mastery import generate_hook, generate_mermaid_chart, generate_scenario, generate_flashcards, generate_resources, explain_concept
from workflow import multi_agent_query
from utils.database import init_db

# Initialize SQL Database tables (SQLite or PostgreSQL)
init_db()

app = FastAPI(title="VedaMate AI Tutor API")


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def sanitize_filename(filename: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_-]', '_', filename)

class ProfileUpdate(BaseModel):
    education_level: str
    interests: str

class ChatPayload(BaseModel):
    message: str

class MasteryUpdate(BaseModel):
    part: str

class ChatHistoryReplacePayload(BaseModel):
    chat_history: List[dict]

class ExplainPayload(BaseModel):
    text: str
    mode: str


@app.get("/api/profile")
async def get_user_profile():
    profile = load_profile()
    if not profile:
        return {"education_level": "", "interests": ""}
    return profile

@app.post("/api/profile")
async def update_user_profile(payload: ProfileUpdate):
    save_profile({"education_level": payload.education_level, "interests": payload.interests})
    
    # Clear cached assets for all books to force regeneration with the new persona
    if os.path.exists(PDF_STORAGE_PATH):
        pdf_files = [f for f in os.listdir(PDF_STORAGE_PATH) if f.endswith('.pdf')]
        for pdf in pdf_files:
            meta = load_metadata(pdf)
            if meta:
                meta["mastery_assets"] = {}
                save_metadata(pdf, meta)
                
    return {"status": "success", "profile": load_profile()}


@app.get("/api/textbooks")
async def list_textbooks():
    if not os.path.exists(PDF_STORAGE_PATH):
        os.makedirs(PDF_STORAGE_PATH)
        
    pdf_files = [f for f in os.listdir(PDF_STORAGE_PATH) if f.endswith('.pdf')]
    total_books = len(pdf_files)
    total_topics = 0
    total_completed_score = 0
    
    books_list = []
    for pdf in pdf_files:
        meta = load_metadata(pdf)
        syllabus = meta.get("syllabus", [])
        total_topics += len(syllabus)
        
        # Calculate book mastery
        mastery_dict = meta.get("mastery", {})
        book_score = 0
        if syllabus:
            book_score = sum(mastery_dict.get(t, {}).get("score", 0) for t in syllabus) / len(syllabus)
        total_completed_score += book_score
        
        books_list.append({
            "name": pdf,
            "mastery": book_score,
            "chapters_count": len(syllabus)
        })
        
    global_avg = total_completed_score / total_books if total_books > 0 else 0
    
    return {
        "textbooks": books_list,
        "stats": {
            "total_books": total_books,
            "total_topics": total_topics,
            "global_avg_mastery": round(global_avg, 1)
        }
    }

@app.post("/api/textbooks/upload")
async def upload_textbook(
    file: UploadFile = File(...),
    custom_syllabus: Optional[str] = Form(None)
):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    file_path = os.path.join(PDF_STORAGE_PATH, file.filename)
    
    # Save the file
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
        
    try:
        collection_name = sanitize_filename(file.filename)
        
        # Ingest and Index PDF in ChromaDB (running async inside block or thread pool if needed, but keeping it simple)
        process_and_store_pdf(file_path, collection_name)
        
        # Syllabus/Topic Extraction
        topics = analyze_syllabus(file_path, custom_syllabus or "")
        
        # Initialize Metadata
        meta = load_metadata(file.filename)
        meta["syllabus"] = topics
        meta["persona"] = load_profile()
        meta["mastery"] = {}
        meta["mastery_assets"] = {}
        save_metadata(file.filename, meta)
        
        return {
            "status": "success",
            "filename": file.filename,
            "chapters": topics
        }
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")

@app.get("/api/textbooks/{pdf_name}/chapters")
async def get_textbook_chapters(pdf_name: str):
    meta = load_metadata(pdf_name)
    if not meta or "syllabus" not in meta:
        raise HTTPException(status_code=404, detail="Textbook syllabus metadata not found.")
    
    return {
        "chapters": meta.get("syllabus", []),
        "mastery": meta.get("mastery", {})
    }

@app.get("/api/textbooks/{pdf_name}/chapters/{topic_name}/assets")
async def get_chapter_assets(pdf_name: str, topic_name: str, regenerate: Optional[str] = None):
    meta = load_metadata(pdf_name)
    if not meta:
        raise HTTPException(status_code=404, detail="Textbook metadata not found.")
        
    profile = load_profile()
    if not profile:
        profile = {"education_level": "Undergraduate", "interests": "General"}

    # Initialize assets structures if needed
    if "mastery_assets" not in meta:
        meta["mastery_assets"] = {}
    if topic_name not in meta["mastery_assets"]:
        meta["mastery_assets"][topic_name] = {
            "hook": None,
            "mermaid_chart": None,
            "scenario": None,
            "flashcards": None,
            "resources": None
        }

    assets = meta["mastery_assets"][topic_name]
    
    # Handle regeneration query parameter
    if regenerate:
        if regenerate == "scenario":
            assets["scenario"] = None
            if "mastery" in meta and topic_name in meta["mastery"]:
                meta["mastery"][topic_name]["selected_option"] = None
        elif regenerate == "flashcards":
            assets["flashcards"] = None
        elif regenerate == "resources":
            assets["resources"] = None
        elif regenerate == "hook":
            assets["hook"] = None
        elif regenerate == "mermaid_chart":
            assets["mermaid_chart"] = None
        elif regenerate == "all":
            assets["scenario"] = None
            assets["flashcards"] = None
            assets["resources"] = None
            assets["hook"] = None
            assets["mermaid_chart"] = None
            if "mastery" in meta and topic_name in meta["mastery"]:
                meta["mastery"][topic_name]["selected_option"] = None

    collection_name = sanitize_filename(pdf_name)
    
    # We query vector DB context if any asset is missing
    context = None
    if not assets.get("hook") or not assets.get("mermaid_chart") or not assets.get("scenario") or not assets.get("flashcards") or not assets.get("resources"):
        db_result = await query_vector_db(topic_name, collection_name)
        context = db_result.get("context_text", "")

    updated = False
    
    # 1. Analogy/Hook
    if not assets.get("hook"):
        assets["hook"] = generate_hook(topic_name, profile, context)
        updated = True
        
    # 2. Mermaid Chart Flowchart
    if not assets.get("mermaid_chart"):
        assets["mermaid_chart"] = generate_mermaid_chart(topic_name, context)
        updated = True

    # 3. Scenario Sandbox
    if not assets.get("scenario"):
        assets["scenario"] = generate_scenario(topic_name, profile, context)
        updated = True

    # 4. Active Recall Flashcards
    if not assets.get("flashcards"):
        assets["flashcards"] = generate_flashcards(topic_name, profile, context)
        updated = True

    # 5. Curator Recommended Study Resources
    if not assets.get("resources"):
        assets["resources"] = generate_resources(topic_name, context)
        updated = True

    if updated:
        meta["mastery_assets"][topic_name] = assets
        save_metadata(pdf_name, meta)

    # Return assets
    return assets

@app.get("/api/textbooks/{pdf_name}/chapters/{topic_name}/chat")
async def get_chat_history(pdf_name: str, topic_name: str):
    meta = load_metadata(pdf_name)
    if not meta:
        raise HTTPException(status_code=404, detail="Textbook metadata not found.")
        
    if "chat_history" not in meta:
        meta["chat_history"] = {}
    if topic_name not in meta["chat_history"]:
        meta["chat_history"][topic_name] = []
        
    return {"chat_history": meta["chat_history"][topic_name]}

@app.put("/api/textbooks/{pdf_name}/chapters/{topic_name}/chat")
async def replace_chat_history(pdf_name: str, topic_name: str, payload: ChatHistoryReplacePayload):
    meta = load_metadata(pdf_name)
    if not meta:
        raise HTTPException(status_code=404, detail="Textbook metadata not found.")
        
    if "chat_history" not in meta:
        meta["chat_history"] = {}
        
    meta["chat_history"][topic_name] = payload.chat_history
    save_metadata(pdf_name, meta)
    
    return {"status": "success", "chat_history": payload.chat_history}

@app.post("/api/textbooks/{pdf_name}/chapters/{topic_name}/chat")
async def chat_with_topic(pdf_name: str, topic_name: str, payload: ChatPayload):
    meta = load_metadata(pdf_name)
    if not meta:
        raise HTTPException(status_code=404, detail="Textbook metadata not found.")
        
    profile = load_profile() or {"education_level": "Undergraduate", "interests": "General"}
    
    if "chat_history" not in meta:
        meta["chat_history"] = {}
    if topic_name not in meta["chat_history"]:
        meta["chat_history"][topic_name] = []
        
    topic_messages = meta["chat_history"][topic_name]
    
    # Append User Message
    topic_messages.append({"role": "user", "content": payload.message})
    
    collection_name = sanitize_filename(pdf_name)
    
    try:
        # Run agentic query workflow
        result = await multi_agent_query(
            query_text=payload.message,
            pdf_context_name=collection_name,
            chat_history=topic_messages[:-1],
            persona=profile,
            current_topic=topic_name,
            mode="chat"
        )
        
        response_text = result.get("answer", "I couldn't process that question. Please try again.")
        suggestions = result.get("suggestions", [])
        citation_snippets = result.get("citation_snippets", {})
        
        # Append Assistant Message with suggestions and citation snippets
        topic_messages.append({
            "role": "assistant",
            "content": response_text,
            "suggestions": suggestions,
            "citation_snippets": citation_snippets
        })
        meta["chat_history"][topic_name] = topic_messages
        save_metadata(pdf_name, meta)
        
        return {
            "role": "assistant",
            "content": response_text,
            "suggestions": suggestions,
            "chat_history": topic_messages,
            "citation_snippets": citation_snippets
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        error_detail = str(e)
        if "429" in error_detail or "quota" in error_detail.lower():
            friendly_msg = (
                "⚠️ **Google Gemini API Quota Limit Exceeded**\n\n"
                "It looks like your Gemini API Key has hit its daily rate limits or quota limits.\n\n"
                "**How to fix this:**\n"
                "1. Wait for the quota to reset (usually daily).\n"
                "2. Provide an alternate or paid API key in your `.env` file.\n"
                "3. Try changing model versions in `utils/config.py`."
            )
        else:
            friendly_msg = (
                f"⚠️ **AI Tutor Error**\n\n"
                f"Something went wrong while processing your question: *{error_detail}*"
            )
        
        # Save the error response in chat history so the chat does not break or get lost
        topic_messages.append({
            "role": "assistant",
            "content": friendly_msg,
            "suggestions": []
        })
        meta["chat_history"][topic_name] = topic_messages
        save_metadata(pdf_name, meta)
        
        return {
            "role": "assistant",
            "content": friendly_msg,
            "suggestions": [],
            "chat_history": topic_messages
        }

@app.post("/api/textbooks/{pdf_name}/chapters/{topic_name}/mastery")
async def update_topic_mastery(pdf_name: str, topic_name: str, payload: MasteryUpdate):
    meta = load_metadata(pdf_name)
    if not meta:
        raise HTTPException(status_code=404, detail="Textbook metadata not found.")
        
    if "mastery" not in meta:
        meta["mastery"] = {}
    if topic_name not in meta["mastery"]:
        meta["mastery"][topic_name] = {"completed_parts": [], "score": 0, "selected_option": None}
        
    topic_mastery = meta["mastery"][topic_name]
    completed = topic_mastery.setdefault("completed_parts", [])
    
    if payload.part not in completed:
        completed.append(payload.part)
        
    topic_mastery["completed_parts"] = completed
    topic_mastery["score"] = len(completed) * 33 if len(completed) < 3 else 100
    
    meta["mastery"][topic_name] = topic_mastery
    save_metadata(pdf_name, meta)
    
    return {
        "status": "success",
        "score": topic_mastery["score"],
        "completed_parts": completed
    }

@app.post("/api/textbooks/{pdf_name}/chapters/{topic_name}/option")
async def select_scenario_option(pdf_name: str, topic_name: str, payload: ChatPayload):
    # We use ChatPayload to get the selected option (A, B, or C)
    meta = load_metadata(pdf_name)
    if not meta:
        raise HTTPException(status_code=404, detail="Textbook metadata not found.")
        
    if "mastery" not in meta:
        meta["mastery"] = {}
    if topic_name not in meta["mastery"]:
        meta["mastery"][topic_name] = {"completed_parts": [], "score": 0, "selected_option": None}
        
    meta["mastery"][topic_name]["selected_option"] = payload.message
    save_metadata(pdf_name, meta)
    
    return {"status": "success", "selected_option": payload.message}

@app.post("/api/explain")
async def explain_text(payload: ExplainPayload):
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    explanation = explain_concept(payload.text, payload.mode)
    return {"explanation": explanation}
