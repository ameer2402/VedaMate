import os
import json
import re
from pypdf import PdfReader
from langchain_google_genai import ChatGoogleGenerativeAI
from utils.config import SYLLABUS_GENERATION_PROMPT, GEMINI_MODEL_NAME, safe_get_content

def extract_intro_text(pdf_path: str, max_pages: int = 15) -> str:
    text = ""
    try:
        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)
        print(f"Syllabus Analyzer: Extracting text from {pdf_path}. Total pages: {total_pages}")
        
        # 1. Try to extract from the first 15 pages
        pages_checked = 0
        for i in range(total_pages):
            if pages_checked >= max_pages:
                break
            page_text = reader.pages[i].extract_text()
            if page_text and page_text.strip():
                text += page_text + "\n"
                pages_checked += 1
                
        # 2. If no text extracted at all, check all pages sequentially to find any text
        if not text.strip():
            print("Syllabus Analyzer: No text found in first 15 pages. Scanning entire document for text...")
            for i in range(total_pages):
                page_text = reader.pages[i].extract_text()
                if page_text and page_text.strip():
                    text += page_text + "\n"
                    # Stop if we collected enough text for syllabus analysis
                    if len(text) > 15000:
                        break
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error reading PDF in extract_intro_text: {e}")
    return text

def analyze_syllabus(pdf_path: str, user_syllabus: str = "") -> list:
    text = extract_intro_text(pdf_path)
    filename = os.path.basename(pdf_path)
    
    llm = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL_NAME,
        temperature=0.2,
    )
    
    if not text.strip():
        print(f"--- SYLLABUS ANALYZER WARNING: No selectable text extracted from {filename}. Attempting fallback generation based on filename. ---")
        fallback_prompt = f"""
You are an expert Educational Curriculum Designer.
The user uploaded a PDF document named "{filename}". We were unable to extract selectable text from this file (it may be scanned or image-based).
Based on the filename "{filename}" and any custom syllabus topics provided by the user below, generate a structured syllabus/chapters breakdown of 5 to 15 major topics.

**USER PROVIDED SYLLABUS/TOPICS (Optional):**
{user_syllabus if user_syllabus else "None provided."}

**CRITICAL INSTRUCTIONS:**
1. You MUST output ONLY valid JSON format.
2. The JSON should be a list of strings, where each string represents a major topic or chapter heading.
3. Keep the topics concise but descriptive (e.g., "Chapter 1: Intro to Physics", "Topic 2: Newton's Laws").
4. DO NOT include any markdown formatting (like ```json), just output the raw JSON array.
5. If the filename is generic or ambiguous (e.g. 'document.pdf', 'file.pdf', 'scan.pdf'), generate a general study curriculum covering typical foundational subjects.
"""
        try:
            response = llm.invoke(fallback_prompt)
            content = safe_get_content(response.content).strip()
            content = re.sub(r'```json\s*', '', content)
            content = re.sub(r'```\s*', '', content)
            match = re.search(r'\[\s*.*?\s*\]', content, re.DOTALL)
            if match:
                content = match.group(0)
            syllabus = json.loads(content)
            if isinstance(syllabus, list) and len(syllabus) > 0:
                print(f"Successfully generated fallback syllabus for {filename}: {syllabus}")
                return syllabus
        except Exception as e:
            print(f"Failed fallback syllabus generation for {filename}: {e}")
            raise RuntimeError(f"Syllabus analysis failed and fallback generation failed: {str(e)}")
            
        return ["General Overview"]
    
    # Cap string length to avoid extreme context length if it's dense
    prompt = SYLLABUS_GENERATION_PROMPT.format(
        book_text=text[:30000],
        user_syllabus=user_syllabus if user_syllabus else "None provided."
    ) 
    
    try:
        response = llm.invoke(prompt)
        content = safe_get_content(response.content).strip()
        
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
        print(f"Failed to generate syllabus for {filename}: {e}")
        raise RuntimeError(f"AI Syllabus Analysis failed: {str(e)}")

