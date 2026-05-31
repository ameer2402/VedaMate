import json
import re
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from utils.config import GEMINI_MODEL_NAME

logger = logging.getLogger(__name__)

def _get_llm(temperature: float = 0.2):
    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL_NAME,
        temperature=temperature,
        convert_system_message_to_human=True,
    )

def _clean_json_response(content: str) -> str:
    # Remove markdown code blocks if the LLM outputted them
    content = re.sub(r'```json\s*', '', content)
    content = re.sub(r'```\s*', '', content)
    return content.strip()

def generate_hook(topic: str, persona: dict, context: str) -> str:
    """
    Generates a comprehensive, highly detailed textbook summary for the topic.
    """
    llm = _get_llm(temperature=0.3)
    
    edu_level = persona.get("education_level", "General Student")
    
    prompt = f"""You are an elite academic tutor. Your task is to write a comprehensive, highly detailed, and structured textbook summary for the topic: "{topic}".
The summary must be exhaustive, ensuring the student does NOT miss any critical details, definitions, principles, formulas, or concepts present in the textbook reference context.

**Student Education Level:** {edu_level}

**Textbook Reference Context:**
{context[:25000]}

**INSTRUCTIONS:**
1. Provide a thorough, structured, and comprehensive explanation of "{topic}" based strictly on the provided Textbook Reference Context. Do not summarize briefly; make it exhaustive.
2. Structure the summary with clear headings, subheadings, bullet points, and bold terms for high readability.
3. Include all formulas, key terminology definitions, and step-by-step procedures/mechanisms mentioned in the context.
4. Adapt the explanation depth and vocabulary to fit the student's Education Level ({edu_level}), explaining complex terms clearly while maintaining academic precision.
5. Do not include introductory dialogue or conversational fillers. Start directly with the structured summary. Use Markdown styling.
"""
    try:
        response = llm.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return f"Welcome to studying **{topic}**! Take a look at the textbook sections to explore this concept in depth."

def generate_mermaid_chart(topic: str, context: str) -> str:
    """
    Generates a valid Mermaid.js flowchart or diagram representing the topic's structure or processes.
    """
    llm = _get_llm(temperature=0.1)
    
    prompt = f"""You are a skilled Technical Illustrator. Your task is to generate a visual flowchart or concept map in Mermaid.js syntax that represents the core processes, relationships, or anatomy of a topic.

**Selected Topic:** {topic}

**Textbook Reference Context:**
{context[:20000]}

**INSTRUCTIONS:**
1. Generate a valid Mermaid.js flowchart. Prefer 'graph TD' (top-down) or 'flowchart LR' (left-right).
2. Connect the core sub-concepts, steps, or components logically as described in the context.
3. Use descriptive labels for nodes. Avoid special characters inside labels that might break Mermaid syntax; you MUST use double quotes for labels, like: A["Label Text"] --> B["Another Label"].
4. Keep the flowchart clean, readable, and focused on this specific topic.
5. Output ONLY the raw Mermaid code block. Do NOT include markdown blocks (like ```mermaid or ```), just start directly with 'graph TD' or 'flowchart LR'.
"""
    try:
        response = llm.invoke(prompt)
        text = response.content.strip()
        
        # Robust extraction:
        # 1. Look for ```mermaid ... ``` or ``` ... ``` blocks
        code_blocks = re.findall(r'```(?:mermaid)?\s*(.*?)\s*```', text, re.DOTALL)
        if code_blocks:
            for block in code_blocks:
                cleaned = block.strip()
                if any(cleaned.startswith(p) for p in ["graph", "flowchart", "sequenceDiagram", "classDiagram", "stateDiagram", "erDiagram", "gantt", "pie", "gitGraph"]):
                    return cleaned
        
        # 2. Find the first occurrence of standard diagram start keyword
        lines = text.split('\n')
        start_idx = -1
        keywords = ["graph ", "flowchart ", "sequenceDiagram", "classDiagram", "stateDiagram", "erDiagram", "gantt", "pie", "gitGraph"]
        for idx, line in enumerate(lines):
            if any(line.strip().startswith(kw) for kw in keywords):
                start_idx = idx
                break
                
        if start_idx != -1:
            chart_lines = lines[start_idx:]
            chart_text = "\n".join(chart_lines).strip()
            chart_text = re.sub(r'```\s*$', '', chart_text).strip()
            return chart_text

        # 3. Cleanup fallback if nothing matches
        chart_code = re.sub(r'```mermaid\s*', '', text)
        chart_code = re.sub(r'```\s*', '', chart_code)
        return chart_code.strip()
    except Exception as e:
        logger.error(f"Error generating Mermaid chart: {e}")
        # Default simple flowchart if generator fails
        return f'graph TD\n    A["{topic}"] --> B["Read Textbook Details"]\n    A --> C["Engage in Chat Deep-Dive"]'

def generate_scenario(topic: str, persona: dict, context: str) -> dict:
    """
    Generates 5 real-world scenarios/simulations with 3 interactive choices each.
    """
    llm = _get_llm(temperature=0.7)
    
    edu_level = persona.get("education_level", "General Student")
    interests = persona.get("interests", "General Topics")
    
    prompt = f"""You are an Educational Game Designer. Your task is to create a list of exactly 5 small interactive decision-making scenarios (simulations) based on the topic.
The student will read each scenario and choose one of the three options to see what happens.

**Student Profile:**
- Education Level: {edu_level}
- Personal Interests: {interests}

**Selected Topic:** {topic}

**Textbook Reference Context:**
{context[:20000]}

**INSTRUCTIONS:**
1. Design exactly 5 hypothetical, real-world situations or problems related to the Topic. If possible, weave in the student's Personal Interests to make them highly engaging and diverse.
2. For each situation, provide three distinct options (A, B, and C) that the student can choose to solve/handle the situation.
3. One option should be the scientifically/conceptually **optimal (correct)** action based on the textbook context. The other two should be common misconceptions or sub-optimal choices.
4. Provide detailed feedback for all three choices: what the consequence is, whether it's correct/incorrect, and the underlying conceptual reason.
5. You MUST respond with ONLY a raw JSON object matching the schema below. No markdown wrapping, no commentary.

**JSON Schema:**
{{
  "scenarios": [
    {{
      "situation": "A detailed description of the first scenario setup and the dilemma.",
      "options": {{
        "A": {{
          "text": "Description of Option A.",
          "is_correct": true,
          "feedback": "Detailed feedback showing the immediate consequences and explaining why it is correct based on the textbook."
        }},
        "B": {{
          "text": "Description of Option B.",
          "is_correct": false,
          "feedback": "Detailed feedback explaining the consequence and why this choice is incorrect or sub-optimal."
        }},
        "C": {{
          "text": "Description of Option C.",
          "is_correct": false,
          "feedback": "Detailed feedback explaining the consequence and why this choice is incorrect or sub-optimal."
        }}
      }}
    }},
    ... // exactly 5 scenarios total
  ]
}}
"""
    fallback = {
        "scenarios": [
            {
                "situation": f"Imagine you are applying the concepts of {topic} in a lab experiment. You need to decide the first step to take.",
                "options": {
                  "A": {"text": "Review the core safety guidelines and textbook procedure.", "is_correct": True, "feedback": "Correct! Starting with a clear plan ensures safety and accuracy."},
                  "B": {"text": "Start mixing components immediately to see what happens.", "is_correct": False, "feedback": "Sub-optimal. Proceeding without a plan can lead to incorrect results or safety hazards."},
                  "C": {"text": "Wait for someone else to perform the experiment first.", "is_correct": False, "feedback": "Sub-optimal. Active participation is key to mastering the topic."}
                }
            },
            {
                "situation": f"You are explaining the core principles of {topic} to a peer who is struggling. What is the most effective approach?",
                "options": {
                  "A": {"text": "Use a simple real-world analogy and walk through a textbook example.", "is_correct": True, "feedback": "Correct! Analogies help anchor abstract concepts to familiar experiences."},
                  "B": {"text": "Tell them to memorize all the formulas and definitions directly.", "is_correct": False, "feedback": "Sub-optimal. Rote memorization without understanding leads to poor retention."},
                  "C": {"text": "Give them your notes and tell them to read them on their own.", "is_correct": False, "feedback": "Sub-optimal. Passive reading is far less effective than interactive explanation."}
                }
            }
        ]
    }
    
    try:
        response = llm.invoke(prompt)
        cleaned = _clean_json_response(response.content)
        parsed = json.loads(cleaned)
        if "scenarios" in parsed and isinstance(parsed["scenarios"], list):
            return parsed
        if "situation" in parsed and "options" in parsed:
            return {"scenarios": [parsed]}
        return fallback
    except Exception as e:
        logger.error(f"Error generating scenarios: {e}")
        return fallback

def generate_flashcards(topic: str, persona: dict, context: str) -> list:
    """
    Generates 5 active recall flashcards (questions and answers) grounded in textbook facts.
    """
    llm = _get_llm(temperature=0.3)
    
    edu_level = persona.get("education_level", "General Student")
    interests = persona.get("interests", "General Topics")
    
    prompt = f"""You are a Spaced Repetition Study Expert. Your task is to generate 5 active recall study flashcards for the topic.

**Student Profile:**
- Education Level: {edu_level}
- Personal Interests: {interests}

**Selected Topic:** {topic}

**Textbook Reference Context:**
{context[:20000]}

**INSTRUCTIONS:**
1. Generate exactly 5 flashcards.
2. The front (question) should pose an insightful, specific question testing key concepts of the topic. Incorporate analogies or themes based on the student's interests if appropriate.
3. The back (answer) should contain a detailed, easy-to-understand explanation of the correct answer, citing facts directly from the textbook context.
4. Keep the cards focused on active recall (learning to retrieve information rather than passive reading).
5. You MUST respond with ONLY a raw JSON list of objects matching the schema below. No markdown wrapping.

**JSON Schema:**
[
  {{
    "front": "Clear, challenging study question.",
    "back": "Detailed answer grounding the concept in textbook facts."
  }},
  ...
]
"""
    fallback = [
        {"front": f"What is the main definition of {topic}?", "back": "Refer to the textbook's main summary of this chapter for exact definitions."},
        {"front": f"Explain one key application of {topic}.", "back": "See Chapter details for the primary applications of this concept."},
        {"front": f"Why is active recall important when studying {topic}?", "back": "Active recall forces the brain to retrieve information, strengthening neural pathways for long-term retention."},
        {"front": f"What is a common misconception about {topic}?", "back": "Check the textbook contradictions section to see what errors students frequently make."},
        {"front": f"How does {topic} relate to real-world scenarios?", "back": "Review the scenario simulation tab to see how this is applied in practical contexts."}
    ]
    
    try:
        response = llm.invoke(prompt)
        cleaned = _clean_json_response(response.content)
        parsed = json.loads(cleaned)
        if isinstance(parsed, list) and len(parsed) > 0:
            return parsed
        return fallback
    except Exception as e:
        logger.error(f"Error generating flashcards: {e}")
        return fallback

def generate_resources(topic: str, context: str) -> list:
    """
    Generates 3 curated external study resources (video search links, articles, etc.) tailored to the topic.
    """
    llm = _get_llm(temperature=0.4)
    
    prompt = f"""You are a helpful Educational Resource Curator. Your task is to recommend exactly 3 high-quality external learning resource searches or references related to the topic.
    
**Selected Topic:** {topic}

**Textbook Reference Context:**
{context[:10000]}

**INSTRUCTIONS:**
1. Generate exactly 3 resource recommendations.
2. For each recommendation, provide:
   - "title": A descriptive title (e.g., "YouTube: Visualizing Wave Interference", "Physics Classroom: Reflection and Refraction Guide").
   - "type": The type of resource ("video", "article", "website", or "simulation").
   - "url": A helpful direct or search URL. For YouTube videos, you can use a search URL like "https://www.youtube.com/results?search_query=wave+propagation+physics". For other sites, provide a reliable search or direct URL.
   - "description": A short explanation (1 sentence) of why this resource is helpful.
3. You MUST respond with ONLY a raw JSON list of objects matching the schema below. No markdown wrapping (like ```json), just output the raw JSON array.

**JSON Schema:**
[
  {{
    "title": "YouTube: Topic Name Explanation",
    "type": "video",
    "url": "https://www.youtube.com/results?search_query=...",
    "description": "Short explanation of the resource."
  }},
  ...
]
"""
    fallback = [
        {
            "title": f"YouTube: Learn {topic} visually",
            "type": "video",
            "url": f"https://www.youtube.com/results?search_query={topic.replace(' ', '+')}+physics",
            "description": "Search YouTube for visual video explanations and tutorials explaining the concepts."
        },
        {
            "title": f"Google Scholar: Research on {topic}",
            "type": "article",
            "url": f"https://scholar.google.com/scholar?q={topic.replace(' ', '+')}",
            "description": "Find academic articles and studies reviewing modern research on this topic."
        },
        {
            "title": f"Wikipedia: {topic} Overview",
            "type": "website",
            "url": f"https://en.wikipedia.org/wiki/Special:Search?search={topic.replace(' ', '+')}",
            "description": "Read a comprehensive structured summary covering history and core formulas."
        }
    ]
    
    try:
        response = llm.invoke(prompt)
        cleaned = _clean_json_response(response.content)
        parsed = json.loads(cleaned)
        if isinstance(parsed, list) and len(parsed) > 0:
            return parsed
        return fallback
    except Exception as e:
        logger.error(f"Error generating study resources: {e}")
        return fallback

def explain_concept(text: str, mode: str) -> str:
    """
    Explains selected text using either 'eli5' (Explain Like I'm 5) or 'deep_dive' mode.
    """
    llm = _get_llm(temperature=0.5)
    
    if mode == "eli5":
        instruction = "Explain the following text like I am a 5-year-old (ELI5). Use extremely simple, clear words, fun analogies, and short sentences. Avoid complex terminology."
    else:
        instruction = "Provide a deep-dive, advanced technical explanation of the following text. Detail the underlying mechanics, context, key definitions, and implications."
        
    prompt = f"""{instruction}

Text to explain:
"{text}"

Explanation:"""
    try:
        res = llm.invoke(prompt)
        return res.content.strip()
    except Exception as e:
        logger.error(f"Error explaining concept: {e}")
        return f"Could not generate explanation: {str(e)}"
