<div align="center">

<img src="https://capsule-render.vercel.app/api?type=venom&color=0:090D16,50:6366F1,100:090D16&height=240&section=header&text=VEDAMATE&fontSize=70&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=Stateful%20Multi-Agent%20AI%20Tutor%20and%20Courseware%20Platform&descSize=20&descAlignY=62&descAlign=50"/>

<h3>🎓 Transform Static Textbooks into Intelligent Conversational Learning Partners 🤖</h3>

<p><em>Powered by React • FastAPI • LangGraph • Google Gemini • ChromaDB • SQL</em></p>

<p>
  <img src="https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black&labelColor=000000"/>
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white&labelColor=000000"/>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white&labelColor=000000"/>
  <img src="https://img.shields.io/badge/LangGraph-0A0E1A?style=for-the-badge&logo=langchain&logoColor=white&labelColor=000000"/>
  <img src="https://img.shields.io/badge/ChromaDB-FC6D26?style=for-the-badge&logo=git&logoColor=white&labelColor=000000"/>
</p>

<p>
  <img src="https://img.shields.io/badge/Architecture-Stateful_Multi--Agent-6366F1?style=for-the-badge&labelColor=000000"/>
  <img src="https://img.shields.io/badge/Retrieval-Parallel_Hybrid_RAG-00C853?style=for-the-badge&labelColor=000000"/>
  <img src="https://img.shields.io/badge/Deployment-Vercel_%26_Render-4285F4?style=for-the-badge&labelColor=000000"/>
</p>

</div>

---

## 🌟 Overview

**VedaMate** is an enterprise-grade, full-stack Intelligent Study Workspace designed to transform static PDF textbooks and course documents into interactive, context-aware learning companions. It replaces passive reading with active, personalized study paths by integrating a state-of-the-art **stateful multi-agent LangGraph system** with a sleek **React frontend** and a high-performance **FastAPI backend**.

### 💼 Technical Highlights:
- **Stateful Multi-Agent Orchestration**: Orchestrated via **LangGraph**, the backend hosts a multi-agent system of 6+ specialized agents that coordinate stateful transitions to handle query rewriting, intent classification, and search.
- **Parallel Hybrid RAG**: Implements concurrent asynchronous data extraction from a **ChromaDB vector store** and live web sources using **Google Custom Search API**, slashing retrieval latency by **~40%**.
- **Syllabus & Courseware Alignment**: Automatically parses uploaded PDFs to extract structural syllabus chapters and dynamically compiles custom interactive study assets (Summaries, Scenarios, and Flashcards) tailored to the student's persona.
- **Robust SQL Persistence**: Persists user profiles, study progress, chapter mastery scores, and chat history using a database layer, ensuring progress is tracked continuously.
- **Premium UX/UI**: Featuring a responsive dark-themed workspace with real-time token streaming, Mermaid.js flowcharts, interactive Quiz Sandboxes, and spaced-repetition active recall decks.

---

## ✨ Key Features

<table>
  <tr>
    <td width="50%">
      <h3>📘 Automatic Syllabus Alignment</h3>
      <p>Upload any textbook PDF and let the AI parse the structural chapters. Alternatively, paste your course syllabus to align vector search chunks directly to your lecture topics.</p>
    </td>
    <td width="50%">
      <h3>📖 AI Summaries & Custom Analogies</h3>
      <p>Generates comprehensive academic textbook summaries. Automatically adapts vocabulary, depth, and real-world analogies to match the student's selected Education Level and Interests.</p>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3>🧪 Scenario Sandbox</h3>
      <p>Engage in real-world decision-making quizzes. Read complex scenarios, make choices, and receive detailed immediate feedback outlining correct principles and common misconceptions.</p>
    </td>
    <td width="50%">
      <h3>🧠 Active Recall Decks</h3>
      <p>Commit textbook facts to memory using flashcards. Features self-assessed difficulty scoring to support spaced-repetition learning.</p>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3>📊 Visual Concept Maps</h3>
      <p>Generates interactive Mermaid.js flowcharts mapped directly to the chapter's conceptual architecture. Students can click any node to request instant ELI5 or Deep-Dive explanations.</p>
    </td>
    <td width="50%">
      <h3>💬 Citation-Backed Chat</h3>
      <p>Engage in semantic dialogues with your documents. Every response includes inline page citations `[p. X]` and hovered textbook snippets, eliminating AI hallucinations.</p>
    </td>
  </tr>
</table>

---

## 👥 System Workflow & Architecture

VedaMate processes document ingestion, vector indexing, syllabus alignment, and conversational RAG using a highly structured, parallel pipeline.

```mermaid
graph TD
    User[Student / User] -->|1. Ingests PDF| WebApp[React Frontend]
    WebApp -->|2. Processes & Vectorizes| FastApi[FastAPI Backend]
    FastApi -->|3. Extracts Syllabus| Analyzer[Syllabus Analyzer]
    FastApi -->|4. Generates Embeddings| GeminiEmbed[Gemini Embeddings]
    GeminiEmbed -->|5. Indexes Chunks| Chroma[ChromaDB Vector Store]
    
    User -->|6. Selects Chapter & Studies| StudyHub[Active Study Hub]
    StudyHub -->|AI Summary & Analogy| ConceptMastery[Concept Mastery Engine]
    StudyHub -->|Scenario Sandbox Quiz| QuizAgent[Quiz/Scenario Agent]
    StudyHub -->|Active Recall Spaced Repetition| FlashcardAgent[Flashcard Agent]
    
    User -->|7. Chats with Document| MultiAgent[Multi-Agent QA Workflow]
    MultiAgent -->|Router Agent| IntentClassifier[Intent Classifier]
    IntentClassifier -->|Factual Lookup| ParallelSearch[Parallel Search: ChromaDB + Google Search]
    IntentClassifier -->|Reasoning Task| DocContext[Document Context Retrieval]
    ParallelSearch -->|Synthesizes Response| Gemini[Gemini 1.5/2.0 Flash]
    DocContext -->|Synthesizes Response| Gemini
    Gemini -->|8. Returns Citation-Backed Answer| User
```

---

## 🏗️ Technical Architecture

```text
                ┌─────────────────────────────┐
                │     👤 USER / STUDENT       │
                └──────────────┬──────────────┘
                               │ HTTP/HTTPS
                               ▼
        ╔══════════════════════════════════════════════╗
        ║            ⚛️ REACT FRONTEND SPA             ║
        ║  (Mermaid.js Flowcharts, State Management)   ║
        ╚══════════════════════════════════════════════╝
                               │
                               │ REST API (JSON) [Vercel Rewrites Proxy]
                               ▼
        ╔══════════════════════════════════════════════╗
        ║         ⚙️ FASTAPI BACKEND SERVICE           ║
        ║  (SQLAlchemy, Multi-threading, asyncio RAG)  ║
        ╚══════════════════════════════════════════════╝
                               │
            ┌──────────────────┼──────────────────┐
            ▼                  ▼                  ▼
   ┌─────────────────┐ ┌───────────────┐ ┌──────────────────┐
   │ 🗄️ PERSISTENT DB │ │ 🔢 CHROMADB   │ │ 🧠 GOOGLE GEMINI │
   │ (SQLite/Postgres│ │ (Vector Index │ │ (LLM Generation  │
   │  Metadata/Chat) │ │  PDF Chunks)  │ │  & Embeddings)   │
   └─────────────────┘ └───────────────┘ └──────────────────┘
```

---

## 🤖 Meet the Agents (LangGraph Stateful Flow)

VedaMate's multi-agent graph coordinates specialized workers to execute queries with maximum relevance and speed:

| Agent | 🎯 Responsibility | 🛠️ Implementation |
|:---|:---|:---|
| 🔀 **Router Agent** | Classifies incoming query intent (e.g. greeting, general, factual, reasoning, quiz, syllabus) | Gemini-powered semantic routing |
| 🔄 **Query Rewriter** | Analyzes chat history and reforms follow-up queries into standalone, search-optimized questions | Standalone rephrasing chain |
| 📚 **Vector DB Agent** | Queries ChromaDB for local context, retrieving the most relevant pages and text chunks | Semantic search with Query Expansion |
| 🌐 **Web Search Agent** | Fetches real-time academic or technical data from the web to complement local textbook facts | Google CSE integration |
| 🧠 **Reasoning Agent** | Resolves subjective, planning, or deep analysis questions requiring cross-referencing | Context-aware synthesis chain |
| 🧪 **Quiz/Study Generator**| Dynamically generates persona-aligned multiple-choice scenarios and spaced-repetition flashcards | JSON-structured generation |

---

## 🛠️ Tech Stack & Tools

| Layer | Technology | Purpose |
|:---|:---|:---|
| ⚛️ **Frontend** | `React`, `Vite`, `JavaScript` | Modern, responsive component-based client |
| 📊 **Visualizations** | `Mermaid.js` | Renders dynamic flowcharts from text-based diagrams |
| ⚙️ **Backend** | `Python`, `FastAPI` | Asynchronous, concurrent REST API backend |
| 🔗 **Orchestration** | `LangGraph`, `LangChain` | Stateful, cyclical agent workflows and chain abstractions |
| 🧠 **Generative AI** | `Google Gemini 1.5/2.0 Flash` | High-speed, high-quality response synthesis |
| 🔢 **Embeddings** | `models/gemini-embedding-001` | Semantic text vectorization |
| 💾 **Vector Database** | `ChromaDB` | Persistent local storage for indexed PDF document embeddings |
| 🗄️ **Relational DB** | `SQLite` (Local) / `PostgreSQL` | Stores profile personas, textbook syllabi, and chat histories |
| 🐋 **DevOps** | `Docker` | Containerized build, testing, and deployment |

---

## 📦 Setup & Installation

### 🔑 Prerequisites
- **Python 3.10+**
- **Node.js 18+** & **npm**
- **Google Gemini API Key** (from Google AI Studio)
- **Google Custom Search Engine ID** and API Key (Optional, for web search functionality)

---

### 1️⃣ Configure the Backend

1. **Navigate to the root directory and create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install the backend dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Create a `.env` file in the root directory:
   ```env
   # Google AI Services API Key
   GOOGLE_API_KEY="your-gemini-api-key-here"

   # Google Custom Search API (Optional for Web Search)
   GOOGLE_CSE_ID="your-google-custom-search-engine-id"
   
   # Database Configuration (Optional, defaults to SQLite)
   DATABASE_URL="postgresql://user:pass@host:port/dbname"
   ```

4. **Launch the FastAPI Server:**
   ```bash
   uvicorn app_api:app --reload --port 8000
   ```
   *The API documentation will be available at `http://127.0.0.1:8000/docs`.*

---

### 2️⃣ Configure the Frontend

1. **Navigate to the frontend folder:**
   ```bash
   cd frontend
   ```

2. **Install the node modules:**
   ```bash
   npm install
   ```

3. **Run the React Dev Server:**
   ```bash
   npm run dev
   ```
   *Open `http://localhost:5173` in your browser to start using VedaMate.*

---

## 👨💻 Author

<div align="center">

### **Mohammed Ameer Khan**
*Full Stack Software Engineer • Ex-Google Apprentice • AI Builder*

<p>
  <a href="https://www.linkedin.com/in/mohammed-ameerkhan-22368626a/">
    <img src="https://img.shields.io/badge/LinkedIn-CONNECT-0077B5?style=for-the-badge&logo=linkedin&logoColor=white&labelColor=000000"/>
  </a>
  <a href="mailto:ameerkhan20241a0497@gmail.com">
    <img src="https://img.shields.io/badge/Email-REACH%20OUT-D14836?style=for-the-badge&logo=gmail&logoColor=white&labelColor=000000"/>
  </a>
  <a href="https://github.com/ameer2402">
    <img src="https://img.shields.io/badge/GitHub-FOLLOW-181717?style=for-the-badge&logo=github&logoColor=white&labelColor=000000"/>
  </a>
  <a href="https://portfolio-frontend-rho-blond.vercel.app/">
    <img src="https://img.shields.io/badge/Portfolio-EXPLORE-FF5722?style=for-the-badge&logo=googlechrome&logoColor=white&labelColor=000000"/>
  </a>
</p>

</div>

<div align="center">

### ⭐ If this project demonstrates the engineering quality you're looking for, feel free to **reach out!** 🚀

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:6366F1,50:090D16,100:6366F1&height=140&section=footer&text=Built%20with%20%E2%9A%A1%20by%20Ameer%20Khan&fontSize=22&fontColor=ffffff&animation=twinkling&fontAlignY=70"/>

</div>
