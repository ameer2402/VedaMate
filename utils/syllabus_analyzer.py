import os
import json
import re
from pypdf import PdfReader
from langchain_google_genai import ChatGoogleGenerativeAI
from utils.config import SYLLABUS_GENERATION_PROMPT, GEMINI_MODEL_NAME

def extract_intro_text(pdf_path: str, max_pages: int = 15) -> str:
    text = ""
    try:
        reader = PdfReader(pdf_path)
        for i, page in enumerate(reader.pages):
            if i >= max_pages:
                break
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error reading PDF: {e}")
    return text

def analyze_syllabus(pdf_path: str, user_syllabus: str = "") -> list:
    text = extract_intro_text(pdf_path)
    if not text.strip():
        print("--- SYLLABUS ANALYZER WARNING: No selectable text extracted from PDF ---")
        return ["General Overview"]
    
    llm = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL_NAME,
        temperature=0.2,
    )
    
    # Cap string length to avoid extreme context length if it's dense
    prompt = SYLLABUS_GENERATION_PROMPT.format(
        book_text=text[:30000],
        user_syllabus=user_syllabus if user_syllabus else "None provided."
    ) 
    
    try:
        response = llm.invoke(prompt)
        content = response.content.strip()
        
        # Clean markdown if present
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```\s*', '', content)
        
        # Robust JSON Array extractor (finds the outermost brackets)
        match = re.search(r'\[\s*.*?\s*\]', content, re.DOTALL)
        if match:
            content = match.group(0)
        
        syllabus = json.loads(content)
        if isinstance(syllabus, list):
            return syllabus
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Failed to generate syllabus: {e}")
    
    return ["General Overview"]
