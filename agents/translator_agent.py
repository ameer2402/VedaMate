from models.agent_state import AgentState
from utils.translation_utils import translate_dict
import logging

async def translator_agent(state: AgentState) -> AgentState:
    target_language = state.get("target_language")
    if target_language and target_language.lower() not in ["en", "english", ""]:
        try:
            state["translated_result"] = await translate_dict(
                state["formatted_result"], target_language
            )
        except Exception as e:
            logging.error(f"Translation failed: {str(e)}")
            state["translated_result"] = state["formatted_result"]
    else:
        state["translated_result"] = state["formatted_result"]
    return state