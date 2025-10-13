from models.agent_state import AgentState

def response_formatting_agent(state: AgentState) -> AgentState:
    raw_response = state.get("combined_response", "")
    
    # PDF Sources are now inline, so we remove the separate key.
    formatted_result = {
        "Overview from Textbook (PDF)": "",
        "Insights from Web Research": "",
        "Cross-Verification and Contradictions": "",
        "Web Sources": state.get("web_search_sources", []),
    }

    current_section = None
    for line in raw_response.split("\n"):
        line_stripped = line.strip()
        if "1. Overview from Textbook (PDF):" in line_stripped:
            current_section = "Overview from Textbook (PDF)"
        elif "2. Insights from Web Research:" in line_stripped:
            current_section = "Insights from Web Research"
        elif "3. Cross-Verification and Contradictions:" in line_stripped:
            current_section = "Cross-Verification and Contradictions"
        elif current_section and current_section in formatted_result:
             formatted_result[current_section] += line + "\n"

    for key in formatted_result:
        if isinstance(formatted_result[key], str):
            formatted_result[key] = formatted_result[key].strip()

    state["formatted_result"] = formatted_result
    return state