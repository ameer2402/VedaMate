# app.py (Modified and Corrected)

import streamlit as st
import os
import asyncio
import re
from dotenv import load_dotenv

# Load environment variables at the very beginning.
load_dotenv()

# We no longer need the global genai.configure block.
# The API endpoint is now handled directly in each agent's LLM constructor.

from utils.config import PDF_STORAGE_PATH
from utils.vector_db_utils import process_and_store_pdf
from workflow import multi_agent_query

st.set_page_config(page_title="Conversational AI Assistant", page_icon="🤖", layout="wide")

def sanitize_filename(filename):
    """Removes special characters from a filename to make it safe for use."""
    return re.sub(r'[^a-zA-Z0-9_-]', '_', filename)

@st.cache_resource
def setup_storage():
    """Ensures that the PDF storage directory exists."""
    if not os.path.exists(PDF_STORAGE_PATH):
        os.makedirs(PDF_STORAGE_PATH)
    return True

# Ensure the PDF storage directory is created on startup.
setup_storage()

# --- Initialize Session State ---
# This ensures that these variables persist across reruns.
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_pdf" not in st.session_state:
    st.session_state.selected_pdf = None
if "suggestions" not in st.session_state:
    st.session_state.suggestions = []
if "thinking" not in st.session_state:
    st.session_state.thinking = False

# --- Sidebar for PDF Management ---
with st.sidebar:
    st.header("1. Upload Your PDF")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_file:
        file_path = os.path.join(PDF_STORAGE_PATH, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        with st.spinner(f"Processing '{uploaded_file.name}'..."):
            collection_name = sanitize_filename(uploaded_file.name)
            process_and_store_pdf(file_path, collection_name)
            st.success(f"'{uploaded_file.name}' is ready!")

    st.divider()
    st.header("2. Select Document")
    pdf_files = [f for f in os.listdir(PDF_STORAGE_PATH) if f.endswith('.pdf')]
    if pdf_files:
        selected_pdf_from_box = st.selectbox(
            "Choose a PDF to chat with:", pdf_files, key="pdf_selector"
        )
        # If the user selects a new PDF, reset the chat state.
        if selected_pdf_from_box != st.session_state.selected_pdf:
            st.session_state.selected_pdf = selected_pdf_from_box
            st.session_state.messages = []
            st.session_state.suggestions = []
            st.session_state.thinking = False
            st.rerun()
    else:
        st.info("Upload a PDF to begin.")

# --- Main Chat Interface ---
st.title(
    f"Chat with: {st.session_state.selected_pdf}"
    if st.session_state.selected_pdf
    else "Conversational AI Assistant"
)

# Display the chat history.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def process_and_display_query(query):
    """Handles the logic for when a user enters a new query or clicks a suggestion."""
    st.session_state.messages.append({"role": "user", "content": query})
    st.session_state.suggestions = []  # Clear old suggestions
    st.session_state.thinking = True
    st.rerun()

# Display suggested questions as clickable buttons.
if st.session_state.suggestions:
    st.markdown("---")
    # Dynamically create columns for the suggestions.
    cols = st.columns(len(st.session_state.suggestions))
    for i, suggestion in enumerate(st.session_state.suggestions):
        with cols[i]:
            if st.button(f"💡 {suggestion}", key=f"suggestion_{i}", type="secondary"):
                process_and_display_query(suggestion)

# The main chat input box.
if prompt := st.chat_input("Ask a question...", disabled=st.session_state.thinking):
    process_and_display_query(prompt)

# This block runs when a new message is submitted and the app reruns.
if st.session_state.thinking:
    with st.chat_message("assistant"):
        with st.spinner("🤖 Assistant is thinking..."):
            if st.session_state.selected_pdf:
                collection_name = sanitize_filename(st.session_state.selected_pdf)
                # Call the asynchronous multi-agent workflow.
                result_dict = asyncio.run(multi_agent_query(
                    st.session_state.messages[-1]["content"],
                    collection_name,
                    st.session_state.messages[:-1]
                ))

                response = result_dict.get("answer", "I encountered an error and couldn't find a response.")
                suggestions = result_dict.get("suggestions", [])

                st.markdown(response, unsafe_allow_html=True)

                # Update session state with the new response and suggestions.
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.session_state.suggestions = suggestions
                st.session_state.thinking = False
                st.rerun()
            else:
                st.warning("Please select a PDF to chat with first.")
                st.session_state.thinking = False
                st.rerun()