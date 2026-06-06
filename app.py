import streamlit as st
import os
import asyncio
import re
from dotenv import load_dotenv

load_dotenv()

# Global monkey-patch for LangChain AIMessage to guarantee content is always a string.
# Prevents 'list' object has no attribute 'strip' errors across the entire app.
try:
    from langchain_core.messages import AIMessage
    from utils.config import safe_get_content
    original_init = AIMessage.__init__
    def patched_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self.content = safe_get_content(self.content)
    AIMessage.__init__ = patched_init
except Exception:
    pass

from utils.config import PDF_STORAGE_PATH
from utils.vector_db_utils import process_and_store_pdf
from utils.metadata_manager import load_metadata, save_metadata
from utils.syllabus_analyzer import analyze_syllabus
from workflow import multi_agent_query
from utils.concept_mastery import generate_hook, generate_mermaid_chart, generate_scenario, generate_flashcards
from utils.vector_db_utils import query_vector_db
from utils.profile_manager import load_profile, save_profile
import streamlit.components.v1 as components

st.set_page_config(page_title="VedaMate AI Tutor", page_icon="🎓", layout="wide")

# Inject premium white-and-black monochrome styling
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background-color: #0a0a0a !important;
        color: #ffffff !important;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"], [data-testid="stSidebarNav"] {
        background-color: #121212 !important;
        border-right: 1px solid #262626 !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
        color: #ffffff !important;
    }
    
    /* Headers styling */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 700 !important;
        letter-spacing: -0.03em !important;
    }
    
    /* Metric Cards Styling */
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #888888 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    
    /* Buttons custom style */
    .stButton>button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #ffffff !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.2rem !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    .stButton>button:hover {
        background-color: #000000 !important;
        color: #ffffff !important;
        border-color: #ffffff !important;
        box-shadow: 0 0 15px rgba(255, 255, 255, 0.2) !important;
    }
    .stButton>button:active {
        transform: scale(0.97) !important;
    }
    
    /* Form & Keyed buttons override */
    button[key*="back_to_"] {
        background-color: transparent !important;
        color: #aaaaaa !important;
        border: 1px solid #333333 !important;
    }
    button[key*="back_to_"]:hover {
        color: #ffffff !important;
        border-color: #ffffff !important;
        background-color: rgba(255, 255, 255, 0.05) !important;
    }
    
    /* Input Elements */
    div[data-baseweb="input"], div[data-baseweb="textarea"] {
        background-color: #121212 !important;
        border: 1px solid #262626 !important;
        border-radius: 6px !important;
        color: #ffffff !important;
    }
    div[data-baseweb="input"]:focus-within, div[data-baseweb="textarea"]:focus-within {
        border-color: #ffffff !important;
        box-shadow: 0 0 8px rgba(255, 255, 255, 0.15) !important;
    }
    
    /* Selectboxes & Multiselect */
    div[data-baseweb="select"], div[data-baseweb="select"] > div {
        background-color: #121212 !important;
        border-color: #262626 !important;
        color: #ffffff !important;
    }
    span[data-baseweb="tag"] {
        background-color: #262626 !important;
        color: #ffffff !important;
        border: 1px solid #333333 !important;
    }
    
    /* Tabs Styling */
    button[data-baseweb="tab"] {
        color: #888888 !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        border-bottom: 2px solid transparent !important;
        background-color: transparent !important;
        transition: all 0.2s ease !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #ffffff !important;
        border-bottom-color: #ffffff !important;
        font-weight: 700 !important;
    }
    button[data-baseweb="tab"]:hover {
        color: #ffffff !important;
    }
    
    /* Progress bars */
    div[data-testid="stProgress"] > div > div > div {
        background-color: #ffffff !important;
    }
    div[data-testid="stProgress"] > div {
        background-color: #222222 !important;
    }
    
    /* Chat Input Styling */
    div[data-testid="stChatInput"] {
        background-color: transparent !important;
    }
    div[data-testid="stChatInput"] textarea {
        background-color: #121212 !important;
        border: 1px solid #262626 !important;
        color: #ffffff !important;
    }
    div[data-testid="stChatInput"] button {
        color: #000000 !important;
        background-color: #ffffff !important;
        border-radius: 50% !important;
    }
    
    /* Streamlit Alerts / Success / Info / Warning / Error Overrides */
    div[data-testid="stAlert"] {
        background-color: #121212 !important;
        color: #ffffff !important;
        border: 1px solid #262626 !important;
        border-radius: 8px !important;
    }
    div[data-testid="stAlert"] > div {
        border-left: 4px solid #ffffff !important;
    }
    div[data-testid="stAlert"] [data-testid="stMarkdownContainer"] p {
        color: #ffffff !important;
    }
    
    /* Beautiful Containers / Cards styling */
    div[data-testid="stVerticalBlock"] > div[style*="border"] {
        background-color: #121212 !important;
        border: 1px solid #262626 !important;
        border-radius: 8px !important;
        padding: 20px !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="stVerticalBlock"] > div[style*="border"]:hover {
        border-color: #ffffff !important;
        box-shadow: 0 4px 25px rgba(255, 255, 255, 0.05) !important;
    }
    
    /* Sidebar specific button overrides */
    [data-testid="stSidebar"] div.stButton > button {
        background-color: transparent !important;
        color: #aaaaaa !important;
        border: 1px solid #262626 !important;
        text-align: left !important;
        justify-content: flex-start !important;
        width: 100% !important;
    }
    [data-testid="stSidebar"] div.stButton > button:hover {
        color: #ffffff !important;
        border-color: #ffffff !important;
        background-color: rgba(255, 255, 255, 0.05) !important;
        box-shadow: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def sanitize_filename(filename):
    return re.sub(r'[^a-zA-Z0-9_-]', '_', filename)

@st.cache_resource
def setup_storage():
    if not os.path.exists(PDF_STORAGE_PATH):
        os.makedirs(PDF_STORAGE_PATH)
    return True

setup_storage()

# --- Hobbies & Interests Preset Options ---
INTERESTS_OPTIONS = [
    "Cricket", "Football / Soccer", "Basketball", "Tennis & Badminton", 
    "Video Games (RPG/FPS/Strategy)", "Board Games & Chess", 
    "Anime & Manga", "Sci-Fi Movies & Shows", "Marvel / DC Universe", 
    "Fantasy Literature (Harry Potter, LOTR)", "Music (Pop, Rock, Hip-Hop, Classical, Lo-Fi)", 
    "Coding & Artificial Intelligence", "Photography & Video Making", 
    "Painting, Sketching & Crafts", "Cooking & Baking", 
    "Travelling & Geography", "Reading & Literature", 
    "Gardening & Nature", "Astronomy & Space Science", 
    "History & Mythology", "Gym, Fitness & Running", 
    "Pets & Animals", "Cryptocurrencies & Finance", 
    "Fashion & Design", "Dances & Performing Arts"
]

# --- Initial Session State ---
if "thinking" not in st.session_state:
    st.session_state.thinking = False
if "selected_pdf" not in st.session_state:
    st.session_state.selected_pdf = None
if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = None
if "processing_pdf" not in st.session_state:
    st.session_state.processing_pdf = None
if "show_upload_form" not in st.session_state:
    st.session_state.show_upload_form = False

def get_library_stats(pdf_files):
    total_books = len(pdf_files)
    total_topics = 0
    total_completed_score = 0
    
    book_masteries = {}
    for pdf in pdf_files:
        meta = load_metadata(pdf)
        syllabus = meta.get("syllabus", [])
        total_topics += len(syllabus)
        
        # Calculate book mastery
        mastery_dict = meta.get("mastery", {})
        book_score = 0
        if syllabus:
            book_score = sum(mastery_dict.get(t, {}).get("score", 0) for t in syllabus) / len(syllabus)
        book_masteries[pdf] = book_score
        total_completed_score += book_score
        
    global_avg = total_completed_score / total_books if total_books > 0 else 0
    return total_books, total_topics, global_avg, book_masteries

# --- Global Persona Check ---
profile = load_profile()
if not profile:
    st.title("🎓 Welcome to VedaMate!")
    st.write("Set up your global learning profile to tailor all study content to your background.")
    
    with st.form("global_profile_setup"):
        edu_level = st.selectbox(
            "What is your education level?", 
            ["Middle School", "High School", "College Undergraduate", "Graduate", "Professional"]
        )
        selected_interests = st.multiselect(
            "Select your hobbies or interests (Select one or more):",
            options=INTERESTS_OPTIONS,
            default=["Video Games (RPG/FPS/Strategy)"]
        )
        submit = st.form_submit_button("Save Profile & Start Learning 🚀")
        if submit:
            interests_str = ", ".join(selected_interests) if selected_interests else "General Topics"
            save_profile({"education_level": edu_level, "interests": interests_str})
            st.success("Learning profile saved globally!")
            st.rerun()
    st.stop()

# Get available textbooks
pdf_files = [f for f in os.listdir(PDF_STORAGE_PATH) if f.endswith('.pdf')]

# --- Sidebar Navigation ---
with st.sidebar:
    st.title("🎓 VedaMate")
    st.write("Your Intelligent Learning Partner")
    st.divider()

    # VIEW A: No Textbook Selected
    if not st.session_state.selected_pdf:
        st.subheader("📚 Textbook Library")
        
        # Upload PDF button toggles the upload form in main panel
        if st.button("➕ Upload PDF", key="btn_toggle_upload", use_container_width=True):
            st.session_state.show_upload_form = True
            st.rerun()

        # History list
        st.divider()
        st.write("### 📖 History of Textbooks")
        if pdf_files:
            for pdf in pdf_files:
                meta = load_metadata(pdf)
                syllabus = meta.get("syllabus", [])
                mastery_dict = meta.get("mastery", {})
                mastery_pct = 0
                if syllabus:
                    mastery_pct = sum(mastery_dict.get(t, {}).get("score", 0) for t in syllabus) / len(syllabus)
                
                # Active styling or standard
                if st.button(f"📘 {pdf} ({mastery_pct:.0f}%)", key=f"select_pdf_{pdf}", use_container_width=True):
                    # Check if already processed
                    if "syllabus" in meta and meta["syllabus"]:
                        st.session_state.selected_pdf = pdf
                        st.session_state.selected_topic = None
                        st.session_state.show_upload_form = False
                    else:
                        st.session_state.processing_pdf = pdf
                    st.rerun()
        else:
            st.info("No textbooks uploaded yet.")

    # VIEW B: Textbook Selected - Show chapters in sidebar navigation
    else:
        st.subheader("📘 Active Textbook")
        st.write(f"**{st.session_state.selected_pdf}**")
        
        if st.button("⬅️ Switch Textbook", key="btn_switch_pdf", use_container_width=True):
            st.session_state.selected_pdf = None
            st.session_state.selected_topic = None
            st.session_state.show_upload_form = False
            st.rerun()
            
        st.divider()
        st.subheader("🎯 Syllabus Chapters")
        
        pdf_meta = load_metadata(st.session_state.selected_pdf)
        syllabus = pdf_meta.get("syllabus", [])
        mastery_dict = pdf_meta.get("mastery", {})
        
        if syllabus:
            for idx, topic in enumerate(syllabus):
                topic_mastery = mastery_dict.get(topic, {})
                topic_score = topic_mastery.get("score", 0)
                
                # Highlight if selected
                is_selected = (st.session_state.selected_topic == topic)
                prefix = "➡️ " if is_selected else "📖 "
                btn_label = f"{prefix}{topic} ({topic_score}%)"
                
                if st.button(btn_label, key=f"sidebar_topic_{idx}", use_container_width=True):
                    st.session_state.selected_topic = topic
                    st.rerun()
        else:
            st.info("No chapters found. Try re-processing.")

# --- Main App Content Logic ---

# 1. Loader screen if processing_pdf is active
if st.session_state.processing_pdf:
    st.title("⚙️ Ingesting Textbook...")
    st.write(f"Analyzing and generating syllabus chapters for **{st.session_state.processing_pdf}**...")
    
    with st.spinner("Analyzing document structure, chunking, indexing in vector store and extracting syllabus..."):
        try:
            processing_name = st.session_state.processing_pdf
            file_path = os.path.join(PDF_STORAGE_PATH, processing_name)
            collection_name = sanitize_filename(processing_name)
            
            # Process in ChromaDB
            process_and_store_pdf(file_path, collection_name)
            
            # Syllabus Extraction
            custom_syllabus = st.session_state.get("custom_syllabus_text", "")
            topics = analyze_syllabus(file_path, custom_syllabus)
            
            # Initialize metadata
            meta = load_metadata(processing_name)
            meta["syllabus"] = topics
            meta["persona"] = load_profile()
            meta["mastery"] = {}
            meta["mastery_assets"] = {}
            save_metadata(processing_name, meta)
            
            st.session_state.selected_pdf = processing_name
            st.session_state.selected_topic = None
            st.session_state.custom_syllabus_text = None
            st.session_state.show_upload_form = False
        except Exception as e:
            st.error(f"Failed to process PDF: {e}")
        finally:
            st.session_state.processing_pdf = None
            st.rerun()

# 2. Upload Form Screen (toggled from sidebar)
elif st.session_state.show_upload_form:
    st.title("📤 Ingest New Textbook")
    st.write("Upload a PDF textbook and optionally align it to a custom course syllabus.")
    
    with st.container(border=True):
        new_uploaded = st.file_uploader("Select PDF file:", type="pdf", key="main_file_uploader")
        custom_syllabus_input = st.text_area(
            "Paste Custom Syllabus Topics (Optional):", 
            placeholder="Paste syllabus topics here, one per line. If left empty, VedaMate will auto-divide textbook sections into logical chapters.",
            height=120,
            key="main_syllabus_input"
        )
        
        col_submit, col_cancel = st.columns([1, 1])
        with col_submit:
            if st.button("Process & Start Learning 🚀", use_container_width=True):
                if new_uploaded:
                    st.session_state.processing_pdf = new_uploaded.name
                    # Save PDF to disk
                    file_path = os.path.join(PDF_STORAGE_PATH, new_uploaded.name)
                    with open(file_path, "wb") as f:
                        f.write(new_uploaded.getbuffer())
                    st.session_state.custom_syllabus_text = custom_syllabus_input
                    st.rerun()
                else:
                    st.error("Please upload a PDF file first.")
        with col_cancel:
            if st.button("Cancel & Return", use_container_width=True):
                st.session_state.show_upload_form = False
                st.rerun()

# 3. Main Dashboard (if no textbook is selected and not showing upload form)
elif not st.session_state.selected_pdf:
    col_title, col_profile = st.columns([3, 1])
    with col_title:
        st.title("🎓 VedaMate Learning Hub")
        st.write("Analyze and master any textbook using personalized, multi-agent AI.")
    with col_profile:
        with st.expander(f"👤 {profile.get('education_level', 'Student')}", expanded=False):
            st.write(f"**Interests:** {profile.get('interests', 'None')}")
            edit_profile = st.checkbox("Edit Persona Settings")
            if edit_profile:
                saved_interests = [i.strip() for i in profile.get('interests', '').split(',') if i.strip()]
                default_selected = [i for i in saved_interests if i in INTERESTS_OPTIONS]
                
                with st.form("edit_profile_form"):
                    new_level = st.selectbox(
                        "Education Level:",
                        ["Middle School", "High School", "College Undergraduate", "Graduate", "Professional"],
                        index=["Middle School", "High School", "College Undergraduate", "Graduate", "Professional"].index(profile.get('education_level', 'College Undergraduate'))
                    )
                    new_selected_interests = st.multiselect(
                        "Hobbies / Interests:",
                        options=INTERESTS_OPTIONS,
                        default=default_selected
                    )
                    save_new = st.form_submit_button("Save Settings")
                    if save_new:
                        new_interests_str = ", ".join(new_selected_interests) if new_selected_interests else "General Topics"
                        save_profile({"education_level": new_level, "interests": new_interests_str})
                        st.success("Profile updated!")
                        st.rerun()

    total_books, total_topics, global_avg, book_masteries = get_library_stats(pdf_files)
    
    # Premium Analytics Dashboard Cards
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.metric("Books Uploaded", total_books)
    with col2:
        with st.container(border=True):
            st.metric("Total Study Topics", total_topics)
    with col3:
        with st.container(border=True):
            st.metric("Global Course Mastery", f"{global_avg:.1f}%")
            
    st.write("---")
    st.info("👈 **Upload a new textbook PDF or select one from the History library in the sidebar to start studying!**")

# 4. Active Textbook Overview (if a textbook is selected but no chapter is selected)
elif st.session_state.selected_pdf and not st.session_state.selected_topic:
    st.title(f"📘 {st.session_state.selected_pdf}")
    st.write("---")
    
    st.info("👈 **Please select a topic from the left side navigation menu to show study options, AI summary, chat room, and interactive quizzes for that topic.**")

# 5. Active Topic Study Panel (Textbook and Chapter selected)
else:
    pdf_meta = load_metadata(st.session_state.selected_pdf)
    current_topic = st.session_state.selected_topic
    
    # Ensure mastery structures exist in metadata
    if "mastery" not in pdf_meta:
        pdf_meta["mastery"] = {}
    if current_topic not in pdf_meta["mastery"]:
        pdf_meta["mastery"][current_topic] = {"completed_parts": [], "score": 0, "selected_option": None}

    if "mastery_assets" not in pdf_meta:
        pdf_meta["mastery_assets"] = {}
    if current_topic not in pdf_meta["mastery_assets"]:
        pdf_meta["mastery_assets"][current_topic] = {
            "hook": None,
            "mermaid_chart": None,
            "scenario": None,
            "flashcards": None
        }

    # Define Mermaid rendering helper
    def render_mermaid(code: str):
        html_code = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
            <script>
                mermaid.initialize({{
                    startOnLoad: true,
                    theme: 'base',
                    themeVariables: {{
                        background: '#121212',
                        primaryColor: '#121212',
                        primaryTextColor: '#ffffff',
                        primaryBorderColor: '#333333',
                        lineColor: '#ffffff',
                        secondaryColor: '#151515',
                        tertiaryColor: '#1a1a1a'
                    }},
                    securityLevel: 'loose'
                }});
            </script>
            <style>
                body {{
                    background-color: #0a0a0a;
                    color: #ffffff;
                    font-family: sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    margin: 0;
                    padding: 10px;
                    overflow: auto;
                }}
                .mermaid {{
                    background-color: #121212;
                    padding: 20px;
                    border-radius: 10px;
                    border: 1px solid #262626;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.5);
                }}
            </style>
        </head>
        <body>
            <div class="mermaid">
                {code}
            </div>
        </body>
        </html>
        """
        components.html(html_code, height=450, scrolling=True)

    # --- Topic Header & Concept Mastery Dashboard ---
    col_back, col_title = st.columns([1, 4])
    with col_back:
        if st.button("⬅️ Book Overview", key="back_to_book_overview", use_container_width=True):
            st.session_state.selected_topic = None
            st.rerun()
    with col_title:
        st.markdown(f"### Selected Topic: **{current_topic}**")

    topic_mastery = pdf_meta["mastery"][current_topic]
    completed = topic_mastery.setdefault("completed_parts", [])
    score = topic_mastery.get("score", 0)

    # Display a beautiful progress dashboard card
    with st.container(border=True):
        st.subheader("🎯 Concept Mastery Dashboard")
        st.write(f"Current Mastery Level: **{score}%**")
        
        # Show nice badges
        badges = []
        badges.append("✅ AI Summary" if "Part 1" in completed else "❌ AI Summary")
        badges.append("✅ Chat" if "Part 2" in completed else "❌ Chat")
        badges.append("✅ Quiz" if "Part 5" in completed else "❌ Quiz")
        st.write(" | ".join(badges))

    # Create tabs for the 3 requested views: AI Summary, Chat, Quiz
    tab_summary, tab_chat, tab_quiz = st.tabs([
        "📖 1. AI Summary & Analogy",
        "💬 2. Chat with Topic",
        "📝 3. Topic Quiz & Exercises"
    ])

    # --- TAB 1: AI Summary & Analogy ---
    with tab_summary:
        st.header("📖 AI Summary & Analogy")
        st.write("Understand the core concept through an engaging, personalized analogy and visual flowchart.")
        
        assets = pdf_meta["mastery_assets"][current_topic]
        if not assets.get("hook"):
            with st.spinner("Writing a creative analogy for you..."):
                collection_name = sanitize_filename(st.session_state.selected_pdf)
                db_result = asyncio.run(query_vector_db(current_topic, collection_name))
                context = db_result.get("context_text", "No context found.")
                assets["hook"] = generate_hook(current_topic, profile, context)
                pdf_meta["mastery_assets"][current_topic] = assets
                save_metadata(st.session_state.selected_pdf, pdf_meta)
        
        st.markdown(assets["hook"])
        st.write("---")
        
        st.subheader("📊 Visual Concept Map")
        if not assets.get("mermaid_chart"):
            with st.spinner("Generating visual concept map..."):
                collection_name = sanitize_filename(st.session_state.selected_pdf)
                db_result = asyncio.run(query_vector_db(current_topic, collection_name))
                context = db_result.get("context_text", "No context found.")
                assets["mermaid_chart"] = generate_mermaid_chart(current_topic, context)
                pdf_meta["mastery_assets"][current_topic] = assets
                save_metadata(st.session_state.selected_pdf, pdf_meta)
        
        render_mermaid(assets["mermaid_chart"])
        st.write("---")
        
        if "Part 1" not in completed:
            if st.button("Mark AI Summary as Mastered", key="mark_part_1"):
                completed.append("Part 1")
                topic_mastery["completed_parts"] = completed
                topic_mastery["score"] = len(completed) * 33 if len(completed) < 3 else 100
                pdf_meta["mastery"][current_topic] = topic_mastery
                save_metadata(st.session_state.selected_pdf, pdf_meta)
                st.success("AI Summary completed! Your mastery level has increased!")
                st.balloons()
                st.rerun()
        else:
            st.success("🎉 You have mastered this section!")

    # --- TAB 2: Chat & Deep-Dive ---
    with tab_chat:
        st.header("💬 Chat & Deep-Dive")
        st.write("Ask questions, clarify doubts, and converse with your AI Tutor grounded in the textbook contents.")
        
        if "chat_history" not in pdf_meta:
            pdf_meta["chat_history"] = {}
        if current_topic not in pdf_meta["chat_history"]:
            pdf_meta["chat_history"][current_topic] = []
        
        topic_messages = pdf_meta["chat_history"][current_topic]
        
        # Display isolated chat history
        for message in topic_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Standard chat input
        if prompt := st.chat_input("Ask a question about this topic...", key="chat_tab_input", disabled=st.session_state.thinking):
            topic_messages.append({"role": "user", "content": prompt})
            pdf_meta["chat_history"][current_topic] = topic_messages
            save_metadata(st.session_state.selected_pdf, pdf_meta)
            st.session_state.thinking = True
            st.rerun()

        if st.session_state.thinking:
            with st.chat_message("assistant"):
                with st.spinner("🤖 VedaMate is thinking..."):
                    collection_name = sanitize_filename(st.session_state.selected_pdf)
                    
                    # Call Workflow with the global active persona
                    result_dict = asyncio.run(multi_agent_query(
                        query_text=topic_messages[-1]["content"],
                        pdf_context_name=collection_name,
                        chat_history=topic_messages[:-1],
                        persona=profile,
                        current_topic=current_topic,
                        mode="chat"
                    ))

                    response = result_dict.get("answer", "Error generating response.")
                    st.markdown(response, unsafe_allow_html=True)

                    topic_messages.append({"role": "assistant", "content": response})
                    pdf_meta["chat_history"][current_topic] = topic_messages
                    save_metadata(st.session_state.selected_pdf, pdf_meta)
                    
                    st.session_state.thinking = False
                    st.rerun()
                    
        st.write("---")
        if "Part 2" not in completed:
            if st.button("Mark Chat as Mastered", key="mark_part_2"):
                completed.append("Part 2")
                topic_mastery["completed_parts"] = completed
                topic_mastery["score"] = len(completed) * 33 if len(completed) < 3 else 100
                pdf_meta["mastery"][current_topic] = topic_mastery
                save_metadata(st.session_state.selected_pdf, pdf_meta)
                st.success("Chat Deep-Dive completed! Your mastery level has increased!")
                st.balloons()
                st.rerun()
        else:
            st.success("🎉 You have mastered this section!")

    # --- TAB 3: Quiz & Active Recall ---
    with tab_quiz:
        st.header("📝 Topic Quiz & Exercises")
        st.write("Test your knowledge and practice active recall.")
        
        quiz_mode = st.radio("Select Quiz Activity:", ["🧪 Scenario Sandbox", "🧠 Active Recall Flashcards"], horizontal=True)
        
        assets = pdf_meta["mastery_assets"][current_topic]
        
        if quiz_mode == "🧪 Scenario Sandbox":
            st.subheader("Scenario Sandbox")
            if not assets.get("scenario"):
                with st.spinner("Creating interactive scenario..."):
                    collection_name = sanitize_filename(st.session_state.selected_pdf)
                    db_result = asyncio.run(query_vector_db(current_topic, collection_name))
                    context = db_result.get("context_text", "No context found.")
                    assets["scenario"] = generate_scenario(current_topic, profile, context)
                    pdf_meta["mastery_assets"][current_topic] = assets
                    save_metadata(st.session_state.selected_pdf, pdf_meta)
            
            scenario_data = assets["scenario"]
            st.markdown(f"### 🚩 Scenario:\n{scenario_data['situation']}")
            
            selected_opt = topic_mastery.get("selected_option")
            
            col1, col2, col3 = st.columns(3)
            if col1.button(f"Option A: {scenario_data['options']['A']['text']}", key="btn_opt_A"):
                selected_opt = "A"
            if col2.button(f"Option B: {scenario_data['options']['B']['text']}", key="btn_opt_B"):
                selected_opt = "B"
            if col3.button(f"Option C: {scenario_data['options']['C']['text']}", key="btn_opt_C"):
                selected_opt = "C"
                
            if selected_opt:
                topic_mastery["selected_option"] = selected_opt
                pdf_meta["mastery"][current_topic] = topic_mastery
                save_metadata(st.session_state.selected_pdf, pdf_meta)
                
                option_info = scenario_data["options"][selected_opt]
                is_correct = option_info.get("is_correct", False)
                
                st.write("---")
                if is_correct:
                    st.success(f"**Option {selected_opt} is Correct!**\n\n{option_info['feedback']}")
                else:
                    st.error(f"**Option {selected_opt} is Sub-optimal.**\n\n{option_info['feedback']}")
                    st.info("Try selecting a different option to discover the optimal path!")
                    
        else:
            st.subheader("Active Recall Deck")
            if not assets.get("flashcards"):
                with st.spinner("Generating flashcard study deck..."):
                    collection_name = sanitize_filename(st.session_state.selected_pdf)
                    db_result = asyncio.run(query_vector_db(current_topic, collection_name))
                    context = db_result.get("context_text", "No context found.")
                    assets["flashcards"] = generate_flashcards(current_topic, profile, context)
                    pdf_meta["mastery_assets"][current_topic] = assets
                    save_metadata(st.session_state.selected_pdf, pdf_meta)
            
            flashcards = assets["flashcards"]
            state_key = f"flashcard_idx_{current_topic}"
            if state_key not in st.session_state:
                st.session_state[state_key] = 0
                
            idx = st.session_state[state_key]
            
            if idx < len(flashcards):
                card = flashcards[idx]
                st.subheader(f"🎴 Card {idx + 1} of {len(flashcards)}")
                
                st.markdown(
                    f"""
                    <div style="background-color: #121212; padding: 25px; border-radius: 12px; border: 1px solid #262626; text-align: center; margin-bottom: 20px;">
                        <h4 style="color: #888888; margin-bottom: 10px; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 0.05em;">Question</h4>
                        <p style="font-size: 1.1rem; color: #ffffff; font-weight: 500;">{card['front']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                reveal_key = f"reveal_{current_topic}_{idx}"
                revealed = st.session_state.get(reveal_key, False)
                
                if not revealed:
                    if st.button("👀 Reveal Answer", key=f"btn_reveal_{idx}"):
                        st.session_state[reveal_key] = True
                        st.rerun()
                else:
                    st.markdown(
                        f"""
                        <div style="background-color: #ffffff; padding: 25px; border-radius: 12px; border: 1px solid #ffffff; margin-bottom: 20px;">
                            <h4 style="color: #000000; margin-bottom: 10px; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 0.05em; font-weight: 700;">Answer</h4>
                            <p style="font-size: 1.1rem; color: #000000; font-weight: 600;">{card['back']}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    st.write("**Self-Assess Your Recall:**")
                    col1, col2, col3 = st.columns(3)
                    if col1.button("🔴 Hard", key=f"btn_hard_{idx}"):
                        st.session_state[reveal_key] = False
                        st.session_state[state_key] = idx + 1
                        st.rerun()
                    if col2.button("🟡 Good", key=f"btn_good_{idx}"):
                        st.session_state[reveal_key] = False
                        st.session_state[state_key] = idx + 1
                        st.rerun()
                    if col3.button("🟢 Easy", key=f"btn_easy_{idx}"):
                        st.session_state[reveal_key] = False
                        st.session_state[state_key] = idx + 1
                        st.rerun()
            else:
                st.success("🎉 You have reviewed all 5 flashcards for this topic!")
                if st.button("Reset Recall Deck", key="btn_reset_deck"):
                    st.session_state[state_key] = 0
                    for i in range(len(flashcards)):
                        st.session_state[f"reveal_{current_topic}_{i}"] = False
                    st.rerun()
                    
        st.write("---")
        if "Part 5" not in completed:
            if st.button("Mark Quiz as Mastered", key="mark_part_5"):
                completed.append("Part 5")
                topic_mastery["completed_parts"] = completed
                topic_mastery["score"] = len(completed) * 33 if len(completed) < 3 else 100
                pdf_meta["mastery"][current_topic] = topic_mastery
                save_metadata(st.session_state.selected_pdf, pdf_meta)
                st.success("Quiz completed! Your mastery level has increased!")
                st.balloons()
                st.rerun()
        else:
            st.success("🎉 You have mastered this section!")