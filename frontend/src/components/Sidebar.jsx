import React from 'react';
import { BookOpen, Upload, LogOut, Award, RefreshCw, ChevronRight, CheckCircle2, X } from 'lucide-react';

export default function Sidebar({
  textbooks = [],
  selectedPdf = null,
  onSelectPdf,
  onToggleUpload,
  activeTopic = null,
  onSelectTopic,
  chapters = [],
  masteryMap = {},
  onSwitchTextbook,
  stats = {},
  isOpen = false,
  onClose
}) {
  return (
    <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
      {/* Sidebar Header */}
      <div style={{ padding: '24px 20px', borderBottom: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ background: '#ffffff', color: '#000000', borderRadius: '8px', padding: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Award size={20} />
          </div>
          <div>
            <h1 style={{ fontSize: '1.2rem', fontWeight: '800', letterSpacing: '-0.02em' }}>VedaMate</h1>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Intelligent Study Workspace</p>
          </div>
        </div>
        
        {/* Mobile Close Button */}
        <button
          className="sidebar-close-btn"
          onClick={onClose}
          style={{
            background: 'transparent',
            border: 'none',
            color: 'var(--text-secondary)',
            cursor: 'pointer',
            padding: '4px',
            display: 'none',
            alignItems: 'center',
            justifyContent: 'center',
            borderRadius: '50%'
          }}
        >
          <X size={18} />
        </button>
      </div>


      {/* Main Sidebar Section */}
      <div style={{ flex: 1, padding: '20px 16px', overflowY: 'auto', display: 'flex', flexcol: 'column', flexDirection: 'column', gap: '20px' }}>
        
        {/* VIEW A: No active textbook selected */}
        {!selectedPdf ? (
          <>
            <div>
              <button 
                className="btn-primary" 
                onClick={onToggleUpload}
                style={{ width: '100%', padding: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
              >
                <Upload size={16} />
                Upload PDF
              </button>
            </div>

            <div>
              <h3 style={{ fontSize: '0.75rem', fontWeight: '700', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>
                Textbooks Library
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {textbooks.length > 0 ? (
                  textbooks.map((book) => (
                    <button
                      key={book.name}
                      onClick={() => onSelectPdf(book.name)}
                      className="btn-sidebar-topic"
                      style={{ padding: '12px' }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', overflow: 'hidden' }}>
                        <BookOpen size={16} style={{ flexShrink: 0 }} />
                        <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                          {book.name}
                        </span>
                      </div>

                    </button>
                  ))
                ) : (
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textAlign: 'center', padding: '20px 0' }}>
                    No books uploaded yet.
                  </p>
                )}
              </div>
            </div>
          </>
        ) : (
          /* VIEW B: Active textbook selected */
          <>
            <div>
              <div style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '12px', marginBottom: '12px' }}>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '4px' }}>Active Book</p>
                <h4 style={{ fontSize: '0.85rem', fontWeight: '700', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {selectedPdf}
                </h4>
              </div>
              <button 
                className="btn-secondary" 
                onClick={onSwitchTextbook}
                style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', padding: '8px' }}
              >
                <LogOut size={14} />
                Switch Textbook
              </button>
            </div>

            <div>
              <h3 style={{ fontSize: '0.75rem', fontWeight: '700', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>
                Syllabus Chapters
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {chapters.length > 0 ? (
                  chapters.map((topic, idx) => {
                    const mastery = masteryMap[topic] || {};
                    const score = mastery.score || 0;
                    const isActive = activeTopic === topic;

                    return (
                      <button
                        key={idx}
                        onClick={() => onSelectTopic(topic)}
                        className={`btn-sidebar-topic ${isActive ? 'active' : ''}`}
                      >
                        <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', paddingRight: '8px' }}>
                          {topic}
                        </span>

                      </button>
                    );
                  })
                ) : (
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>No chapters found.</p>
                )}
              </div>
            </div>
          </>
        )}
      </div>


    </aside>
  );
}
