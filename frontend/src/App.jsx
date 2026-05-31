import React, { useState, useEffect } from 'react';
import { Bot, Upload, Book, Award, BookOpen, AlertCircle, RefreshCw, User, Settings, ArrowLeft, X, Sparkles, Menu } from 'lucide-react';

import Sidebar from './components/Sidebar';
import GlobalProfile from './components/GlobalProfile';
import AISummaryTab from './components/AISummaryTab';
import ChatTab, { renderMarkdown } from './components/ChatTab';
import QuizTab from './components/QuizTab';

// Dynamic API Base URL configuration for local vs production
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? ''
  : 'https://vedamate-backend.onrender.com';

const originalFetch = window.fetch;
window.fetch = function (url, options) {
  if (typeof url === 'string' && url.startsWith('/api')) {
    url = API_BASE_URL + url;
  }
  return originalFetch(url, options);
};

export default function App() {
  // Session / Navigation States
  const [profile, setProfile] = useState(null);
  const [profileLoading, setProfileLoading] = useState(true);
  const [editingProfile, setEditingProfile] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const [textbooks, setTextbooks] = useState([]);
  const [stats, setStats] = useState({ total_books: 0, total_topics: 0, global_avg_mastery: 0 });
  const [libraryLoading, setLibraryLoading] = useState(true);

  const [selectedPdf, setSelectedPdf] = useState(null);
  const [showUploadForm, setShowUploadForm] = useState(false);
  const [processingPdf, setProcessingPdf] = useState(null);

  // Syllabus / Chapter States
  const [chapters, setChapters] = useState([]);
  const [masteryMap, setMasteryMap] = useState({});
  const [selectedTopic, setSelectedTopic] = useState(null);
  
  // Topic Asset States
  const [assets, setAssets] = useState(null);
  const [assetsLoading, setAssetsLoading] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatThinking, setChatThinking] = useState(false);
  
  // Global chat states
  const [globalChatMessages, setGlobalChatMessages] = useState([]);
  const [globalChatThinking, setGlobalChatThinking] = useState(false);
  const [showGlobalChat, setShowGlobalChat] = useState(false);
  
  // Active Main Panel View Tab
  const [activeTab, setActiveTab] = useState('dashboard'); // 'dashboard' | 'summary' | 'chat' | 'scenario' | 'flashcards'

  // File Uploader Local States
  const [file, setFile] = useState(null);
  const [customSyllabus, setCustomSyllabus] = useState('');
  const [uploadError, setUploadError] = useState('');

  // Highlight to explain states
  const [selectedText, setSelectedText] = useState('');
  const [tooltipPos, setTooltipPos] = useState(null);
  const [explanationText, setExplanationText] = useState(null);
  const [explanationMode, setExplanationMode] = useState(null);
  const [explanationContent, setExplanationContent] = useState('');
  const [explanationLoading, setExplanationLoading] = useState(false);

  // 1. Fetch Profile on load
  useEffect(() => {
    fetchProfile();
  }, []);

  // 2. Fetch Textbooks when profile changes or library updates
  useEffect(() => {
    if (profile && profile.education_level) {
      fetchLibrary();
    }
  }, [profile]);

  // 3. Fetch Syllabus Chapters when selected PDF changes
  useEffect(() => {
    if (selectedPdf) {
      fetchChapters(selectedPdf);
      resetGlobalChatHistory(selectedPdf);
    } else {
      setChapters([]);
      setMasteryMap({});
      setSelectedTopic(null);
      setAssets(null);
      setGlobalChatMessages([]);
    }
  }, [selectedPdf]);

  // 4. Fetch Assets when selected Topic changes or profile changes
  useEffect(() => {
    if (selectedPdf && selectedTopic) {
      fetchTopicAssets(selectedPdf, selectedTopic);
      resetChatHistory(selectedPdf, selectedTopic);
      setActiveTab('dashboard');
    } else {
      setAssets(null);
    }
  }, [selectedTopic, profile]);


  // selection listener for Highlight-to-Explain
  useEffect(() => {
    const handleMouseUp = (e) => {
      if (e.target.closest('#selection-tooltip') || e.target.closest('#explanation-popup')) {
        return;
      }
      
      const selection = window.getSelection();
      const text = selection.toString().trim();
      
      if (text.length >= 3 && text.length <= 3000) {
        try {
          const range = selection.getRangeAt(0);
          const rect = range.getBoundingClientRect();
          setTooltipPos({
            x: rect.left + rect.width / 2 + window.scrollX,
            y: rect.top - 44 + window.scrollY
          });
          setSelectedText(text);
        } catch (err) {
          setSelectedText('');
          setTooltipPos(null);
        }
      } else {
        setSelectedText('');
        setTooltipPos(null);
      }
    };

    const handleMouseDown = (e) => {
      if (e.target.closest('#selection-tooltip') || e.target.closest('#explanation-popup')) {
        return;
      }
      setSelectedText('');
      setTooltipPos(null);
    };

    document.addEventListener('mouseup', handleMouseUp);
    document.addEventListener('mousedown', handleMouseDown);
    return () => {
      document.removeEventListener('mouseup', handleMouseUp);
      document.removeEventListener('mousedown', handleMouseDown);
    };
  }, []);

  const handleExplain = async (mode, conceptText = null) => {
    const textToExplain = conceptText || selectedText;
    if (!textToExplain) return;
    setExplanationText(textToExplain);
    setExplanationMode(mode);
    setExplanationLoading(true);
    setExplanationContent('');
    if (!conceptText) {
      setSelectedText('');
      setTooltipPos(null);
    }

    try {
      const res = await fetch('/api/explain', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: textToExplain, mode })
      });
      const data = await res.json();
      setExplanationContent(data.explanation || 'Error generating explanation.');
    } catch (e) {
      console.error("Explain error:", e);
      setExplanationContent('Failed to fetch explanation from server.');
    } finally {
      setExplanationLoading(false);
    }
  };

  const fetchProfile = async () => {
    try {
      setProfileLoading(true);
      const res = await fetch('/api/profile');
      const data = await res.json();
      if (data.education_level) {
        setProfile(data);
      } else {
        setProfile(null);
      }
    } catch (e) {
      console.error("Profile load failed:", e);
    } finally {
      setProfileLoading(false);
    }
  };

  const handleSaveProfile = async (newProfile) => {
    try {
      const res = await fetch('/api/profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newProfile)
      });
      const data = await res.json();
      if (data.status === 'success') {
        setProfile(data.profile);
        setEditingProfile(false);
      }
    } catch (e) {
      console.error("Save profile failed:", e);
    }
  };

  const fetchLibrary = async () => {
    try {
      setLibraryLoading(true);
      const res = await fetch('/api/textbooks');
      const data = await res.json();
      setTextbooks(data.textbooks || []);
      setStats(data.stats || { total_books: 0, total_topics: 0, global_avg_mastery: 0 });
    } catch (e) {
      console.error("Library load failed:", e);
    } finally {
      setLibraryLoading(false);
    }
  };

  const fetchChapters = async (pdfName) => {
    try {
      const res = await fetch(`/api/textbooks/${encodeURIComponent(pdfName)}/chapters`);
      const data = await res.json();
      setChapters(data.chapters || []);
      
      const parsedMastery = {};
      if (data.mastery) {
        Object.keys(data.mastery).forEach(topic => {
          const topicMastery = data.mastery[topic];
          const selectedOptions = {};
          if (topicMastery.selected_option) {
            if (topicMastery.selected_option.includes(':')) {
              const [idx, opt] = topicMastery.selected_option.split(':');
              selectedOptions[idx] = opt;
            } else {
              selectedOptions['0'] = topicMastery.selected_option;
            }
          }
          parsedMastery[topic] = {
            ...topicMastery,
            selected_options: selectedOptions
          };
        });
      }
      setMasteryMap(parsedMastery);
    } catch (e) {
      console.error("Chapters load failed:", e);
    }
  };

  const fetchTopicAssets = async (pdfName, topicName) => {
    try {
      setAssetsLoading(true);
      const res = await fetch(`/api/textbooks/${encodeURIComponent(pdfName)}/chapters/${encodeURIComponent(topicName)}/assets`);
      const data = await res.json();
      setAssets(data);
    } catch (e) {
      console.error("Assets load failed:", e);
    } finally {
      setAssetsLoading(false);
    }
  };

  const resetChatHistory = async (pdfName, topicName) => {
    try {
      setChatMessages([]);
      await fetch(`/api/textbooks/${encodeURIComponent(pdfName)}/chapters/${encodeURIComponent(topicName)}/chat`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chat_history: [] })
      });
    } catch (e) {
      console.error("Chat reset failed:", e);
    }
  };

  const resetGlobalChatHistory = async (pdfName) => {
    try {
      setGlobalChatMessages([]);
      await fetch(`/api/textbooks/${encodeURIComponent(pdfName)}/chapters/${encodeURIComponent('__global__')}/chat`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chat_history: [] })
      });
    } catch (e) {
      console.error("Global chat reset failed:", e);
    }
  };

  const handleSendGlobalMessage = async (text) => {
    if (globalChatThinking) return;
    const updatedMessages = [...globalChatMessages, { role: 'user', content: text }];
    setGlobalChatMessages(updatedMessages);
    setGlobalChatThinking(true);

    try {
      const res = await fetch(`/api/textbooks/${encodeURIComponent(selectedPdf)}/chapters/${encodeURIComponent('__global__')}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });
      const data = await res.json();
      setGlobalChatMessages(data.chat_history || updatedMessages);
    } catch (e) {
      console.error("Send global message error:", e);
    } finally {
      setGlobalChatThinking(false);
    }
  };

  const handleEditGlobalMessage = async (index, newText) => {
    if (globalChatThinking) return;
    const truncatedHistory = globalChatMessages.slice(0, index);
    const updatedMessages = [...truncatedHistory, { role: 'user', content: newText }];
    setGlobalChatMessages(updatedMessages);
    setGlobalChatThinking(true);

    try {
      await fetch(`/api/textbooks/${encodeURIComponent(selectedPdf)}/chapters/${encodeURIComponent('__global__')}/chat`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chat_history: truncatedHistory })
      });

      const res = await fetch(`/api/textbooks/${encodeURIComponent(selectedPdf)}/chapters/${encodeURIComponent('__global__')}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: newText })
      });
      const data = await res.json();
      setGlobalChatMessages(data.chat_history || updatedMessages);
    } catch (e) {
      console.error("Edit global message error:", e);
    } finally {
      setGlobalChatThinking(false);
    }
  };

  const handleSendMessage = async (text) => {
    if (chatThinking) return;
    
    // Add optimistic user message
    const updatedMessages = [...chatMessages, { role: 'user', content: text }];
    setChatMessages(updatedMessages);
    setChatThinking(true);

    try {
      const res = await fetch(`/api/textbooks/${encodeURIComponent(selectedPdf)}/chapters/${encodeURIComponent(selectedTopic)}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });
      const data = await res.json();
      setChatMessages(data.chat_history || updatedMessages);
    } catch (e) {
      console.error("Send message error:", e);
    } finally {
      setChatThinking(false);
    }
  };

  const handleEditMessage = async (index, newText) => {
    if (chatThinking) return;
    
    // Truncate local chat messages state up to index - 1
    const truncatedHistory = chatMessages.slice(0, index);
    
    // Add optimistic edited user message
    const updatedMessages = [...truncatedHistory, { role: 'user', content: newText }];
    setChatMessages(updatedMessages);
    setChatThinking(true);

    try {
      // PUT the truncated history to the backend to sync
      await fetch(`/api/textbooks/${encodeURIComponent(selectedPdf)}/chapters/${encodeURIComponent(selectedTopic)}/chat`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chat_history: truncatedHistory })
      });

      // POST the new query to generate the new response
      const res = await fetch(`/api/textbooks/${encodeURIComponent(selectedPdf)}/chapters/${encodeURIComponent(selectedTopic)}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: newText })
      });
      const data = await res.json();
      setChatMessages(data.chat_history || updatedMessages);
    } catch (e) {
      console.error("Edit message error:", e);
    } finally {
      setChatThinking(false);
    }
  };

  const handleSelectOption = async (optionKey) => {
    try {
      const res = await fetch(`/api/textbooks/${encodeURIComponent(selectedPdf)}/chapters/${encodeURIComponent(selectedTopic)}/option`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: optionKey })
      });
      const data = await res.json();
      if (data.status === 'success') {
        setMasteryMap(prev => {
          const currentTopicMastery = prev[selectedTopic] || {};
          let newSelectedOptions = { ...(currentTopicMastery.selected_options || {}) };
          if (optionKey.includes(':')) {
            const [idxStr, optVal] = optionKey.split(':');
            newSelectedOptions[idxStr] = optVal;
          } else {
            newSelectedOptions['0'] = optionKey;
          }
          return {
            ...prev,
            [selectedTopic]: {
              ...currentTopicMastery,
              selected_option: optionKey,
              selected_options: newSelectedOptions
            }
          };
        });
      }
    } catch (e) {
      console.error("Select option failed:", e);
    }
  };

  const handleRegenerateAsset = async (assetType) => {
    if (!selectedPdf || !selectedTopic) return;
    try {
      setAssetsLoading(true);
      const res = await fetch(`/api/textbooks/${encodeURIComponent(selectedPdf)}/chapters/${encodeURIComponent(selectedTopic)}/assets?regenerate=${assetType}`);
      const data = await res.json();
      setAssets(data);
      if (assetType === 'scenario') {
        setMasteryMap(prev => ({
          ...prev,
          [selectedTopic]: {
            ...prev[selectedTopic],
            selected_option: null,
            selected_options: {}
          }
        }));
      }
    } catch (e) {
      console.error(`Regenerate ${assetType} failed:`, e);
    } finally {
      setAssetsLoading(false);
    }
  };

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setUploadError("Please select a PDF file first.");
      return;
    }
    
    setUploadError('');
    setProcessingPdf(file.name);
    setShowUploadForm(false);

    const formData = new FormData();
    formData.append('file', file);
    if (customSyllabus) {
      formData.append('custom_syllabus', customSyllabus);
    }

    try {
      const res = await fetch('/api/textbooks/upload', {
        method: 'POST',
        body: formData
      });
      if (!res.ok) {
        throw new Error(await res.text());
      }
      const data = await res.json();
      if (data.status === 'success') {
        fetchLibrary();
        setSelectedPdf(data.filename);
        setFile(null);
        setCustomSyllabus('');
      }
    } catch (e) {
      setUploadError(e.message || "Failed to process PDF file.");
      console.error("PDF upload failed:", e);
    } finally {
      setProcessingPdf(null);
    }
  };

  // Render Loader Screen if profile loading
  if (profileLoading) {
    return (
      <div style={{ display: 'flex', height: '100vh', justifyContent: 'center', alignItems: 'center', backgroundColor: 'var(--bg-primary)' }}>
        <div style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <RefreshCw className="skeleton" size={32} style={{ animation: 'spin 2s linear infinite', margin: '0 auto' }} />
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Booting VedaMate...</p>
        </div>
      </div>
    );
  }

  // Render Setup Profile if no profile exists
  if (!profile && !editingProfile) {
    return (
      <div style={{ backgroundColor: 'var(--bg-primary)', minHeight: '100vh', padding: '40px 20px' }}>
        <GlobalProfile initialProfile={null} onSave={handleSaveProfile} />
      </div>
    );
  }

  const gridLayout = selectedPdf
    ? (showGlobalChat ? '320px 0px 1fr' : '320px 1fr 0px')
    : '320px 1fr';

  return (
    <div 
      className="app-container"
      style={{
        display: 'grid',
        gridTemplateColumns: gridLayout,
        transition: 'grid-template-columns 0.4s cubic-bezier(0.16, 1, 0.3, 1)'
      }}
    >
      {/* Sidebar Backdrop Overlay */}
      {sidebarOpen && (
        <div 
          className="sidebar-backdrop" 
          onClick={() => setSidebarOpen(false)} 
        />
      )}

      {/* 1. Sidebar Nav */}
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        textbooks={textbooks}
        selectedPdf={selectedPdf}
        onSelectPdf={(pdf) => {
          setSelectedPdf(pdf);
          setShowUploadForm(false);
          setSidebarOpen(false);
        }}
        onToggleUpload={() => {
          setShowUploadForm(true);
          setSelectedPdf(null);
          setSidebarOpen(false);
        }}
        activeTopic={selectedTopic}
        onSelectTopic={(topic) => {
          setSelectedTopic(topic);
          setSidebarOpen(false);
        }}
        chapters={chapters}
        masteryMap={masteryMap}
        onSwitchTextbook={() => {
          setSelectedPdf(null);
          setSelectedTopic(null);
          setShowUploadForm(false);
          setSidebarOpen(false);
        }}
        stats={stats}
      />

      {/* 2. Workspace (Middle Column) */}
      <main 
        className="main-content" 
        style={{ 
          overflow: 'hidden',
          visibility: showGlobalChat ? 'hidden' : 'visible',
          opacity: showGlobalChat ? 0 : 1,
          transition: 'opacity 0.3s ease, visibility 0.3s ease'
        }}
      >
        {/* Header toolbar */}
        <header 
          className="workspace-header"
          style={{ 
            height: '68px', 
            borderBottom: '1px solid var(--border-color)', 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center', 
            background: 'rgba(10, 10, 10, 0.8)', 
            backdropFilter: 'blur(8px)', 
            boxSizing: 'border-box' 
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <button
              className="sidebar-toggle-btn"
              onClick={() => setSidebarOpen(true)}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--text-primary)',
                cursor: 'pointer',
                padding: '4px',
                display: 'none',
                alignItems: 'center',
                justifyContent: 'center',
                marginRight: '8px'
              }}
            >
              <Menu size={20} />
            </button>
          </div>

          
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            {profile && (
              <div 
                style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', border: '1px solid var(--border-color)', borderRadius: '6px', padding: '6px 12px', display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}
                onClick={() => setEditingProfile(true)}
              >
                <User size={12} />
                <span>{profile.education_level} Persona</span>
              </div>
            )}
          </div>
        </header>


        {/* Scrollable Workspace Body */}
        <div className="workspace-body" style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column' }}>
          {editingProfile ? (
            /* STATE B: Editing persona profile settings */
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '24px' }}>
                <button className="btn-secondary" onClick={() => setEditingProfile(false)} style={{ padding: '8px 12px' }}>
                  <ArrowLeft size={14} /> Back
                </button>
              </div>
              <GlobalProfile 
                initialProfile={profile} 
                onSave={(p) => {
                  handleSaveProfile(p);
                  setEditingProfile(false);
                }} 
                onCancel={() => setEditingProfile(false)} 
              />
            </div>
          ) : processingPdf ? (
            /* STATE A: Processing Loader */
            <div style={{ display: 'flex', height: '60vh', justifyContent: 'center', alignItems: 'center' }}>
              <div style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', gap: '16px', maxWidth: '400px' }}>
                <RefreshCw size={36} className="skeleton" style={{ animation: 'spin 2s linear infinite', margin: '0 auto' }} />
                <h3 style={{ fontSize: '1.2rem', fontWeight: '800' }}>Ingesting Textbook...</h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', lineHeight: 1.5 }}>
                  Analyzing and structuring chapters for <strong>{processingPdf}</strong>. This compiles vector database indexes and syllabus alignments.
                </p>
              </div>
            </div>
          ) : showUploadForm ? (
            /* STATE C: Show file upload Form */
            <div style={{ maxWidth: '700px', margin: '0 auto', width: '100%' }}>
              <h2 style={{ fontSize: '1.6rem', fontWeight: '800', letterSpacing: '-0.02em', marginBottom: '8px' }}>Ingest New Textbook</h2>
              <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '24px' }}>
                Ingest a textbook PDF file and optionally paste course topics. VedaMate aligns and vectorizes components.
              </p>
              
              {uploadError && (
                <div style={{ display: 'flex', gap: '8px', padding: '16px', borderRadius: '8px', border: '1px solid #441111', background: '#220000', color: '#ff8888', marginBottom: '20px', fontSize: '0.85rem', alignItems: 'center' }}>
                  <AlertCircle size={16} />
                  <span>{uploadError}</span>
                </div>
              )}

              <form onSubmit={handleUploadSubmit} className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: '700', textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                    Select PDF Document File
                  </label>
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={(e) => setFile(e.target.files[0])}
                    className="input-field"
                    style={{ padding: '10px' }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: '700', textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                    Custom Syllabus Topics (Optional)
                  </label>
                  <textarea
                    value={customSyllabus}
                    onChange={(e) => setCustomSyllabus(e.target.value)}
                    placeholder="Paste topics one per line (e.g. Wave Propagation, Tuning Forks...)"
                    className="textarea-field"
                    style={{ height: '140px' }}
                  />
                </div>

                <div style={{ display: 'flex', gap: '12px', marginTop: '12px' }}>
                  <button type="submit" className="btn-primary" style={{ flex: 1 }}>
                    Ingest & Process PDF 🚀
                  </button>
                  <button type="button" className="btn-secondary" onClick={() => setShowUploadForm(false)} style={{ flex: 1 }}>
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          ) : selectedPdf ? (
            !selectedTopic ? (
              /* STATE E: Textbook selected, but no chapter selected yet */
              <div style={{ display: 'flex', flexDirection: 'column', gap: '28px', animation: 'fadeIn 0.4s ease-out' }}>
                <div>
                  <h1 style={{ fontSize: '1.8rem', fontWeight: '800', letterSpacing: '-0.02em', marginBottom: '6px', color: '#ffffff' }}>
                    📘 {selectedPdf}
                  </h1>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                    Select a syllabus topic below to begin studying, or use the Global AI Assistant on the right to chat about the entire textbook.
                  </p>
                </div>

                <div className="glass-panel" style={{ padding: '32px' }}>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: '700', color: '#ffffff', marginBottom: '20px' }}>Syllabus Chapters</h3>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '16px' }}>
                    {chapters.map((chapter, idx) => (
                      <button
                        key={idx}
                        className="btn-sidebar-topic"
                        onClick={() => setSelectedTopic(chapter)}
                        style={{
                          border: '1px solid var(--border-color)',
                          background: 'rgba(255, 255, 255, 0.01)',
                          padding: '16px 20px',
                          borderRadius: '12px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'flex-start',
                          gap: '12px'
                        }}
                      >
                        <span style={{ background: 'rgba(99, 102, 241, 0.1)', color: 'var(--accent-purple)', width: '28px', height: '28px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.8rem', fontWeight: '700', flexShrink: 0 }}>
                          {idx + 1}
                        </span>
                        <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', fontWeight: '600' }}>
                          {chapter}
                        </span>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              /* STATE F: Topic selected! Render assets and study activities */
              <div className="animate-fade-in">
                {activeTab === 'dashboard' ? (
                  /* 3-Card dashboard view */
                  <div className="animate-fade-in-up">
                    <div style={{ marginBottom: '28px' }}>
                      <span style={{ fontSize: '0.75rem', fontWeight: '700', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                        Active Topic Hub
                      </span>
                      <h1 style={{ fontSize: '1.8rem', fontWeight: '800', letterSpacing: '-0.02em', marginTop: '4px' }}>
                        {selectedTopic}
                      </h1>
                      <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', marginTop: '6px' }}>
                        Select one of the study modules below to explore this topic:
                      </p>
                    </div>
                    
                    <div className="feature-grid">
                      <div className="feature-card" onClick={() => setActiveTab('summary')}>
                        <div className="feature-card-icon">
                          <BookOpen size={22} />
                        </div>
                        <h3 style={{ fontSize: '1.15rem', fontWeight: '800', color: '#ffffff' }}>📖 1. AI Summary & Analogy</h3>
                        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
                          Read an intuitive explanation, customized analogies, and interact with a visual concept flowchart.
                        </p>
                      </div>

                      <div className="feature-card" onClick={() => setActiveTab('scenario')}>
                        <div className="feature-card-icon">
                          <AlertCircle size={22} />
                        </div>
                        <h3 style={{ fontSize: '1.15rem', fontWeight: '800', color: '#ffffff' }}>🧪 2. Scenario Sandbox</h3>
                        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
                          Apply your conceptual knowledge to a real-world scenario with multiple choice choices and detailed feedback.
                        </p>
                      </div>

                      <div className="feature-card" onClick={() => setActiveTab('flashcards')}>
                        <div className="feature-card-icon">
                          <Award size={22} />
                        </div>
                        <h3 style={{ fontSize: '1.15rem', fontWeight: '800', color: '#ffffff' }}>🧠 3. Active Recall Deck</h3>
                        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
                          Commit details to memory using spaced repetition active recall cards and self-assessed difficulty ratings.
                        </p>
                      </div>
                    </div>
                  </div>
                ) : (
                  /* Sub-activity view */
                  <div className="animate-fade-in">
                    {/* Activity header with back button */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginBottom: '24px' }}>
                      <div>
                        <button 
                          className="btn-secondary" 
                          onClick={() => setActiveTab('dashboard')} 
                          style={{ padding: '8px 16px', display: 'inline-flex', alignItems: 'center', gap: '8px', fontSize: '0.8rem', borderRadius: '8px' }}
                        >
                          <ArrowLeft size={14} /> Back to Topic Dashboard
                        </button>
                      </div>
                      
                      <div>
                        <span style={{ fontSize: '0.75rem', fontWeight: '700', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                          {selectedTopic}
                        </span>
                        <h2 style={{ fontSize: '1.6rem', fontWeight: '800', letterSpacing: '-0.02em', marginTop: '2px', color: '#ffffff' }}>
                          {activeTab === 'summary' && '📖 AI Summary & Analogy'}
                          {activeTab === 'scenario' && '🧪 Scenario Sandbox'}
                          {activeTab === 'flashcards' && '🧠 Active Recall Deck'}
                        </h2>
                      </div>
                    </div>

                    {/* Viewport content */}
                    <div style={{ minHeight: '400px' }}>
                      {assetsLoading ? (
                        <div style={{ display: 'flex', height: '300px', justifyContent: 'center', alignItems: 'center' }}>
                          <div style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                            <RefreshCw size={24} className="skeleton" style={{ animation: 'spin 2s linear infinite', margin: '0 auto' }} />
                            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Generating study assets...</p>
                          </div>
                        </div>
                      ) : (
                        assets && (
                          <>
                            {activeTab === 'summary' && (
                              <AISummaryTab
                                hookText={assets.hook}
                                chartCode={assets.mermaid_chart}
                                resources={assets.resources}
                                onExplainConcept={handleExplain}
                              />
                            )}

                            {activeTab === 'scenario' && (
                              <QuizTab
                                scenario={assets.scenario}
                                flashcards={assets.flashcards}
                                selectedOption={masteryMap[selectedTopic]?.selected_option}
                                selectedOptions={masteryMap[selectedTopic]?.selected_options || {}}
                                onSelectOption={handleSelectOption}
                                onRegenerateAsset={handleRegenerateAsset}
                                initialActivity="scenario"
                              />
                            )}

                            {activeTab === 'flashcards' && (
                              <QuizTab
                                scenario={assets.scenario}
                                flashcards={assets.flashcards}
                                selectedOption={masteryMap[selectedTopic]?.selected_option}
                                selectedOptions={masteryMap[selectedTopic]?.selected_options || {}}
                                onSelectOption={handleSelectOption}
                                onRegenerateAsset={handleRegenerateAsset}
                                initialActivity="flashcards"
                              />
                            )}
                          </>
                        )
                      )}
                    </div>
                  </div>
                )}
              </div>
            )
          ) : (
          /* Fallback when no book selected (Library Hub) */
          <div style={{ display: 'flex', flexDirection: 'column', gap: '32px', maxWidth: '800px', margin: '0 auto', width: '100%', padding: '20px 0' }}>
            {/* Hero Section */}
            <div style={{ textAlign: 'center', marginBottom: '12px' }}>
              <div style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.15) 100%)', border: '1px solid var(--border-color)', borderRadius: '24px', padding: '8px 16px', marginBottom: '20px', gap: '8px' }}>
                <Sparkles size={14} style={{ color: 'var(--accent-purple)' }} />
                <span style={{ fontSize: '0.78rem', fontWeight: '700', color: 'var(--accent-purple)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  Intelligent Study Workspace
                </span>
              </div>
              <h1 style={{ fontSize: '2.5rem', fontWeight: '800', letterSpacing: '-0.04em', marginBottom: '16px', background: 'linear-gradient(to right, #ffffff, #cbd5e1)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                Welcome to VedaMate
              </h1>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', lineHeight: '1.6', maxWidth: '600px', margin: '0 auto' }}>
                Ingest textbook PDFs to generate customized AI summaries, interactive scenarios, spaced-repetition flashcards, and a context-aware chat assistant.
              </p>
            </div>

            {/* Quick Action Hero Card */}
            <div className="glass-panel" style={{ padding: '40px', textAlign: 'center', background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.4) 0%, rgba(9, 13, 22, 0.7) 100%)', border: '1px solid var(--border-color)' }}>
              <BookOpen size={48} style={{ margin: '0 auto 20px auto', color: 'var(--accent-purple)', filter: 'drop-shadow(0 0 10px rgba(167, 139, 250, 0.3))' }} />
              <h3 style={{ fontSize: '1.3rem', fontWeight: '800', color: '#ffffff', marginBottom: '12px' }}>Start Your Learning Session</h3>
              <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', maxWidth: '460px', margin: '0 auto 24px auto', lineHeight: '1.6' }}>
                Select an existing textbook from the left sidebar library to resume studying, or ingest a new PDF book to align and index its syllabus.
              </p>
              <div style={{ display: 'flex', justifyContent: 'center', gap: '16px', flexWrap: 'wrap' }}>
                <button className="btn-primary" onClick={() => setShowUploadForm(true)} style={{ padding: '14px 28px' }}>
                  <Upload size={16} /> Ingest New PDF Book
                </button>
              </div>
            </div>

            {/* How it works features */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '20px', marginTop: '12px' }}>
              <div style={{ padding: '20px', borderRadius: '12px', border: '1px solid var(--border-color)', background: 'rgba(255, 255, 255, 0.01)' }}>
                <span style={{ fontSize: '1.5rem', display: 'block', marginBottom: '12px' }}>📘</span>
                <h4 style={{ fontWeight: '700', color: '#ffffff', marginBottom: '8px', fontSize: '0.95rem' }}>1. Custom Syllabus Alignment</h4>
                <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
                  Upload a syllabus or let the AI parse chapters to create structured learning pathways.
                </p>
              </div>
              <div style={{ padding: '20px', borderRadius: '12px', border: '1px solid var(--border-color)', background: 'rgba(255, 255, 255, 0.01)' }}>
                <span style={{ fontSize: '1.5rem', display: 'block', marginBottom: '12px' }}>🧪</span>
                <h4 style={{ fontWeight: '700', color: '#ffffff', marginBottom: '8px', fontSize: '0.95rem' }}>2. Scenario Sandbox</h4>
                <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
                  Apply concepts to real-world scenarios to bridge the gap between theory and practice.
                </p>
              </div>
              <div style={{ padding: '20px', borderRadius: '12px', border: '1px solid var(--border-color)', background: 'rgba(255, 255, 255, 0.01)' }}>
                <span style={{ fontSize: '1.5rem', display: 'block', marginBottom: '12px' }}>🧠</span>
                <h4 style={{ fontWeight: '700', color: '#ffffff', marginBottom: '8px', fontSize: '0.95rem' }}>3. Active Recall Decks</h4>
                <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
                  Leverage spaced repetition flashcards with self-assessed recall difficulty scoring.
                </p>
              </div>
            </div>
          </div>
        )}

      </div>
    </main>

    {/* 3. Global Textbook Assistant (Right Column) */}
    {selectedPdf && (
      <div 
        className="global-agent-panel"
        style={{
          display: 'flex',
          flexDirection: 'column',
          background: 'rgba(9, 13, 22, 0.4)',
          borderLeft: showGlobalChat ? '1px solid var(--border-color)' : 'none',
          height: '100vh',
          overflow: 'hidden',
          visibility: showGlobalChat ? 'visible' : 'hidden',
          opacity: showGlobalChat ? 1 : 0,
          transition: 'opacity 0.3s ease, visibility 0.3s ease'
        }}
      >
        {/* Panel Header */}
        <header style={{
          height: '68px',
          padding: '0 24px 0 32px',
          borderBottom: '1px solid var(--border-color)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: 'rgba(10, 10, 10, 0.8)',
          backdropFilter: 'blur(8px)',
          boxSizing: 'border-box'
        }}>
          <div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: '800', color: '#ffffff', display: 'flex', alignItems: 'center', gap: '8px', margin: 0 }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#a78bfa', boxShadow: '0 0 10px #a78bfa' }}></span>
              Global Textbook Assistant
            </h3>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '2px', margin: 0 }}>
              Ask questions across the entire textbook scope
            </p>
          </div>
          
          <button
            onClick={() => setShowGlobalChat(false)}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-secondary)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.08)';
              e.currentTarget.style.color = '#ffffff';
              e.currentTarget.style.transform = 'rotate(90deg)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'transparent';
              e.currentTarget.style.color = 'var(--text-secondary)';
              e.currentTarget.style.transform = 'rotate(0deg)';
            }}
          >
            <X size={18} />
          </button>
        </header>

        {/* Panel Body */}
        <div style={{ flex: 1, padding: '24px', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <ChatTab
            messages={globalChatMessages}
            onSendMessage={handleSendGlobalMessage}
            isThinking={globalChatThinking}
            onEditMessage={handleEditGlobalMessage}
          />
        </div>
      </div>
    )}

    {/* Floating Global AI Button (visible when closed) */}
    {selectedPdf && !showGlobalChat && (
      <button
        onClick={() => setShowGlobalChat(true)}
        className="btn-primary animate-pulse-glow"
        style={{
          position: 'fixed',
          bottom: '32px',
          right: '32px',
          width: '60px',
          height: '60px',
          borderRadius: '50%',
          padding: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 0 20px rgba(139, 92, 246, 0.6)',
          zIndex: 99,
          cursor: 'pointer',
          transition: 'transform 0.2s ease-out'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'scale(1.1)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'scale(1)';
        }}
      >
        <Sparkles size={24} />
      </button>
    )}
    {/* Selection Tooltip */}
    {selectedText && tooltipPos && (
      <div
        id="selection-tooltip"
        style={{
          position: 'absolute',
          left: `${tooltipPos.x}px`,
          top: `${tooltipPos.y}px`,
          transform: 'translateX(-50%)',
          background: 'rgba(15, 23, 42, 0.95)',
          border: '1px solid var(--border-color)',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.4)',
          borderRadius: '20px',
          padding: '4px 8px',
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          zIndex: 9999,
          animation: 'fadeIn 0.15s ease-out',
          backdropFilter: 'blur(8px)'
        }}
      >
        <button
          onClick={() => handleExplain('eli5')}
          style={{
            background: 'transparent',
            border: 'none',
            color: '#ffffff',
            fontSize: '0.78rem',
            fontWeight: '600',
            cursor: 'pointer',
            padding: '6px 10px',
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            transition: 'background 0.2s'
          }}
          onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.08)'}
          onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
        >
          👶 ELI5
        </button>
        <span style={{ color: 'var(--border-color)', fontSize: '0.8rem' }}>|</span>
        <button
          onClick={() => handleExplain('deep_dive')}
          style={{
            background: 'transparent',
            border: 'none',
            color: '#ffffff',
            fontSize: '0.78rem',
            fontWeight: '600',
            cursor: 'pointer',
            padding: '6px 10px',
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            transition: 'background 0.2s'
          }}
          onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.08)'}
          onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
        >
          🔍 Deep Dive
        </button>
      </div>
    )}

    {/* Floating Explanation Drawer */}
    {(explanationText || explanationLoading) && (
      <div
        id="explanation-popup"
        className="glass-panel"
        style={{
          position: 'fixed',
          top: '80px',
          right: '24px',
          width: '380px',
          maxHeight: 'calc(100vh - 120px)',
          background: 'rgba(10, 12, 18, 0.95)',
          border: '1px solid var(--border-color)',
          borderRadius: '16px',
          boxShadow: '0 10px 30px rgba(0, 0, 0, 0.5)',
          display: 'flex',
          flexDirection: 'column',
          zIndex: 10000,
          overflow: 'hidden',
          backdropFilter: 'blur(12px)',
          animation: 'fadeIn 0.25s ease-out'
        }}
      >
        {/* Header */}
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(255, 255, 255, 0.02)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '1.2rem' }}>
              {explanationMode === 'eli5' ? '👶' : '🔍'}
            </span>
            <div>
              <h4 style={{ fontSize: '0.9rem', fontWeight: '800', margin: 0 }}>
                {explanationMode === 'eli5' ? 'Explain Like I\'m 5' : 'Technical Deep Dive'}
              </h4>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', margin: 0 }}>VedaMate Smart Assistant</p>
            </div>
          </div>
          <button
            onClick={() => {
              setExplanationText(null);
              setExplanationContent('');
            }}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-secondary)',
              cursor: 'pointer',
              padding: '4px',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            <X size={16} />
          </button>
        </div>

        {/* Content */}
        <div style={{ padding: '20px', overflowY: 'auto', flex: 1, display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Highlighted text quote */}
          <div style={{ borderLeft: '3px solid var(--accent-purple)', paddingLeft: '12px', background: 'rgba(255,255,255,0.02)', borderRadius: '0 8px 8px 0', padding: '10px 12px' }}>
            <p style={{ fontSize: '0.78rem', fontStyle: 'italic', color: 'var(--text-secondary)', margin: 0, lineHeight: '1.4' }}>
              "{explanationText}"
            </p>
          </div>

          {explanationLoading ? (
            <div style={{ display: 'flex', height: '150px', justifyContent: 'center', alignItems: 'center', flexDirection: 'column', gap: '10px' }}>
              <RefreshCw size={24} className="skeleton" style={{ animation: 'spin 2s linear infinite' }} />
              <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Analyzing context...</span>
            </div>
          ) : (
            <div style={{ fontSize: '0.88rem', lineHeight: '1.6', color: 'var(--text-primary)' }}>
              {renderMarkdown(explanationContent)}
            </div>
          )}
        </div>
      </div>
    )}
  </div>
);
}
