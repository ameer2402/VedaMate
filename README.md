<div align="center">

<img src="https://capsule-render.vercel.app/api?type=venom&color=0:667eea,50:764ba2,100:f093fb&height=240&section=header&text=VedaMate&fontSize=80&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=Multi-Agent%20RAG%20AI%20Teaching%20Assistant&descSize=22&descAlignY=62&descAlign=50"/>

<h3>🎓 Transform Any PDF into an Intelligent Conversational Learning Partner 🤖</h3>

<p><em>Powered by LangGraph • Google Gemini • ChromaDB • Hybrid RAG Architecture</em></p>

<p>
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white&labelColor=000000"/>
  <img src="https://img.shields.io/badge/LangGraph-Multi--Agent-FF6F00?style=for-the-badge&labelColor=000000"/>
  <img src="https://img.shields.io/badge/Gemini-2.0_Flash-8E75B2?style=for-the-badge&logo=google&logoColor=white&labelColor=000000"/>
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white&labelColor=000000"/>
  <img src="https://img.shields.io/badge/ChromaDB-Vector_Store-FF6B9D?style=for-the-badge&labelColor=000000"/>
  <img src="https://img.shields.io/badge/RAG-Architecture-00D9FF?style=for-the-badge&labelColor=000000"/>
</p>

<p>
  <img src="https://img.shields.io/badge/Status-Production_Ready-00C853?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Hackathon-Google_AI_2025-4285F4?style=for-the-badge&logo=google&logoColor=white"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/PRs-Welcome-brightgreen?style=for-the-badge"/>
</p>

</div>

<div align="center">
  <img src="https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif" width="100%"/>
</div>

## 📋 Table of Contents

- [🌟 Overview](#-overview)
- [🎯 The Problem We're Solving](#-the-problem-were-solving)
- [✨ Our Solution](#-our-solution)
- [🚀 Key Features](#-key-features)
- [🏗️ Architecture & Tech Stack](#️-architecture--tech-stack)
- [🤖 Meet the Agents](#-meet-the-agents)
- [🆚 Why VedaMate Stands Out](#-why-vedamate-stands-out)
- [📦 Setup & Installation](#-setup--installation)
- [🎮 How to Use](#-how-to-use)
- [📊 Performance & Impact Metrics](#-performance--impact-metrics)
- [🌍 Real-World Impact](#-real-world-impact)
- [🗺️ Roadmap](#️-roadmap)
- [🤝 Contributing](#-contributing)
- [📜 License](#-license)
- [👨‍💻 Author](#-author)
- [🏆 Acknowledgments](#-acknowledgments)

<div align="center">
  <img src="https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif" width="100%"/>
</div>

## 🌟 Overview

**VedaMate** is a sophisticated, production-grade **Conversational AI Teaching Assistant** built with **Python**, **Streamlit**, and **Google's Generative AI** ecosystem. Leveraging a state-of-the-art **Retrieval-Augmented Generation (RAG)** architecture orchestrated by a **multi-agent system on LangGraph**, this application transforms static PDF documents into interactive, intelligent learning partners.

> 💡 **Upload any PDF → Ask anything → Get context-aware answers grounded in your document AND real-time web data.**

Whether you're a **student** decoding a 500-page textbook, a **researcher** parsing dense academic papers, or a **professional** analyzing legal/technical documents — VedaMate delivers semantic, citation-backed answers in seconds.

## 🎯 The Problem We're Solving

Learning from digital documents today is **broken**:

| 🚨 Pain Point | 📉 Impact |
|:---|:---|
| **Information Overload** | Hard to find specific answers in 100s of pages; `Ctrl+F` misses context |
| **Zero Interactivity** | PDFs are read-only — you can't ask, clarify, or explore |
| **Disconnected Learning** | Constant tab-switching between textbook & browser kills focus |
| **Generic AI Limitations** | ChatGPT has no clue about your specific course material → hallucinations |

## ✨ Our Solution

An **intelligent agentic application** that fuses your **personal documents** with the **live web**, delivering grounded, hallucination-free, citation-rich answers through an elegant conversational interface.

<div align="center">
  <img src="https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif" width="100%"/>
</div>

## 🚀 Key Features

<table>
  <tr>
    <td width="50%">
      <h3>📄 PDF Document Chat</h3>
      <p>Upload <b>any PDF</b> and engage in <b>semantic, context-aware conversations</b>. Powered by vector embeddings, not keyword matching.</p>
    </td>
    <td width="50%">
      <h3>🤖 Multi-Agent Workflow</h3>
      <p><b>6+ specialized AI agents</b> orchestrated via <b>LangGraph state machine</b> — each handling a discrete task with surgical precision.</p>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3>🌐 Hybrid Parallel Search</h3>
      <p><b>Async parallel retrieval</b> from <b>ChromaDB vector store</b> AND <b>Google Custom Search API</b> — slashing latency by <b>~40%</b>.</p>
    </td>
    <td width="50%">
      <h3>🧠 Intent-Aware Routing</h3>
      <p>Smart <b>Router Agent</b> classifies queries (factual, reasoning, greeting) and dynamically chooses the optimal execution path.</p>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3>📚 Citation-Grounded Answers</h3>
      <p>Every response is <b>backed by source citations</b> from the PDF, eliminating hallucinations and boosting trust.</p>
    </td>
    <td width="50%">
      <h3>💬 Streaming Conversational UI</h3>
      <p>Clean, responsive <b>Streamlit interface</b> with <b>real-time token streaming</b>, follow-up suggestions & keyboard navigation.</p>
    </td>
  </tr>
</table>

<div align="center">
  <img src="https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif" width="100%"/>
</div>

## 🏗️ Architecture & Tech Stack

### 🔥 Modern RAG Pipeline Orchestrated by LangGraph
