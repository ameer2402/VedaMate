import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, Pencil, Check, X, Copy } from 'lucide-react';

function parseInlineMarkdown(text, citationSnippets = {}) {
  if (!text) return "";
  
  const parts = [];
  let lastIdx = 0;
  // tokenRegex matches:
  // 1. Bold: **text**
  // 2. Bracket page reference: [p. X] or [Page X]
  // 3. Standard markdown link: [text](url)
  const tokenRegex = /(\*\*(.*?)\*\*|\[(p\.\s*\d+|page\s*\d+)\]|\[(.*?)\]\((.*?)\))/gi;
  let match;
  
  while ((match = tokenRegex.exec(text)) !== null) {
    if (match.index > lastIdx) {
      parts.push(text.substring(lastIdx, match.index));
    }
    
    const fullMatch = match[1];
    if (fullMatch.startsWith('**')) {
      // Bold
      parts.push(
        <strong key={match.index} style={{ fontWeight: '700', color: '#ffffff' }}>
          {match[2]}
        </strong>
      );
    } else if (fullMatch.startsWith('[') && !fullMatch.includes('](')) {
      // Bare citation [p. X]
      const citationText = match[3];
      const pageDigitsMatch = citationText.match(/\d+/);
      const pageNum = pageDigitsMatch ? pageDigitsMatch[0] : "";
      
      const snippets = citationSnippets[pageNum] || citationSnippets[citationText.trim()] || [];
      
      parts.push(
        <span 
          key={match.index} 
          className="citation-badge citation-interactive" 
          style={{ position: 'relative', cursor: 'pointer' }}
        >
          {citationText}
          {snippets.length > 0 && (
            <span className="citation-tooltip-bubble">
              <strong style={{ display: 'block', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '4px', marginBottom: '6px', fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--accent-purple)' }}>
                📖 Textbook Snippet (p. {pageNum})
              </strong>
              {snippets.map((snip, sIdx) => (
                <p key={sIdx} style={{ margin: '0 0 6px 0', fontSize: '0.8rem', lineHeight: '1.4', fontStyle: 'italic', color: 'var(--text-secondary)' }}>
                  "{snip}"
                </p>
              ))}
            </span>
          )}
        </span>
      );
    } else {
      // Standard markdown link [text](url)
      const linkText = match[4];
      const linkUrl = match[5];
      const isCitation = linkUrl.startsWith('file://') || /^(p\.\s*\d+|page\s*\d+)$/i.test(linkText);
      
      if (isCitation) {
        const pageDigitsMatch = linkText.match(/\d+/);
        const pageNum = pageDigitsMatch ? pageDigitsMatch[0] : "";
        const snippets = citationSnippets[pageNum] || citationSnippets[linkText.trim()] || [];
        
        parts.push(
          <a 
            key={match.index} 
            href={linkUrl} 
            target="_blank" 
            rel="noopener noreferrer" 
            className="citation-badge citation-interactive"
            style={{ position: 'relative', textDecoration: 'none' }}
          >
            {linkText}
            {snippets.length > 0 && (
              <span className="citation-tooltip-bubble">
                <strong style={{ display: 'block', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '4px', marginBottom: '6px', fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--accent-purple)' }}>
                  📖 Textbook Snippet (p. {pageNum})
                </strong>
                {snippets.map((snip, sIdx) => (
                  <p key={sIdx} style={{ margin: '0 0 6px 0', fontSize: '0.8rem', lineHeight: '1.4', fontStyle: 'italic', color: 'var(--text-secondary)' }}>
                    "{snip}"
                  </p>
                ))}
              </span>
            )}
          </a>
        );
      } else {
        parts.push(
          <a 
            key={match.index} 
            href={linkUrl} 
            target="_blank" 
            rel="noopener noreferrer" 
            className="chat-link"
          >
            {linkText}
          </a>
        );
      }
    }
    lastIdx = tokenRegex.lastIndex;
  }
  
  if (lastIdx < text.length) {
    parts.push(text.substring(lastIdx));
  }
  
  return parts.length > 0 ? parts : text;
}


export function renderMarkdown(text, citationSnippets = {}) {
  if (!text) return null;

  const lines = text.split('\n');
  const blocks = [];
  
  let i = 0;
  while (i < lines.length) {
    let line = lines[i];
    let trimmed = line.trim();

    // 0. Handle Horizontal Rules (Dividers)
    if (/^([-*_])\1\1+$/.test(trimmed) || trimmed === '---' || trimmed === '--') {
      blocks.push(
        <hr 
          key={`hr-${i}`} 
          style={{ 
            border: 'none', 
            borderTop: '1px solid var(--border-color)', 
            margin: '16px 0',
            opacity: 0.5
          }} 
        />
      );
      i++;
      continue;
    }

    // 1. Handle Code Blocks
    if (trimmed.startsWith('```')) {
      const codeLines = [];
      i++;
      while (i < lines.length && !lines[i].trim().startsWith('```')) {
        codeLines.push(lines[i]);
        i++;
      }
      i++; // Skip closing ```
      blocks.push(
        <pre key={`code-${i}`} style={{ background: 'rgba(0,0,0,0.3)', padding: '12px', borderRadius: '8px', overflowX: 'auto', border: '1px solid var(--border-color)', margin: '12px 0', fontSize: '0.85rem' }}>
          <code>{codeLines.join('\n')}</code>
        </pre>
      );
      continue;
    }

    // 2. Handle Markdown Tables
    if (trimmed.startsWith('|')) {
      const tableLines = [];
      while (i < lines.length && lines[i].trim().startsWith('|')) {
        tableLines.push(lines[i].trim());
        i++;
      }
      
      if (tableLines.length >= 1) {
        const parseRow = (rowText) => {
          const cells = rowText.split('|').map(c => c.trim());
          if (cells[0] === '') cells.shift();
          if (cells[cells.length - 1] === '') cells.pop();
          return cells;
        };

        const headerCells = parseRow(tableLines[0]);
        let separatorRowIdx = -1;
        
        if (tableLines[1] && tableLines[1].includes('-')) {
          separatorRowIdx = 1;
        }

        const bodyRows = [];
        const startIdx = separatorRowIdx !== -1 ? 2 : 1;
        for (let r = startIdx; r < tableLines.length; r++) {
          bodyRows.push(parseRow(tableLines[r]));
        }

        blocks.push(
          <div key={`table-${i}`} style={{ overflowX: 'auto' }}>
            <table>
              <thead>
                <tr>
                  {headerCells.map((cell, cIdx) => (
                    <th key={cIdx}>{parseInlineMarkdown(cell, citationSnippets)}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {bodyRows.map((rowCells, rIdx) => (
                  <tr key={rIdx}>
                    {rowCells.map((cell, cIdx) => (
                      <td key={cIdx}>{parseInlineMarkdown(cell, citationSnippets)}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );
      }
      continue;
    }

    // 3. Handle Ordered Lists (lines starting with \d+. or * \d+. or - \d+.)
    const isOrderedListLine = (lineStr) => {
      const t = lineStr.trim();
      return /^\d+\.\s+/.test(t) || /^[-*]\s+\d+\.\s+/.test(t);
    };

    if (isOrderedListLine(line)) {
      const listItems = [];
      while (i < lines.length && isOrderedListLine(lines[i])) {
        const itemTrimmed = lines[i].trim();
        const cleanItem = itemTrimmed.replace(/^[-*]\s+/, '');
        const match = cleanItem.match(/^\d+\.\s*(.*)/);
        const content = match ? match[1] : cleanItem;
        listItems.push(content);
        i++;
      }

      blocks.push(
        <ol key={`ol-${i}`} style={{ marginLeft: '24px', marginBottom: '14px', listStyleType: 'decimal' }}>
          {listItems.map((item, idx) => (
            <li key={idx} style={{ marginBottom: '6px', color: 'var(--text-primary)', fontSize: '0.92rem' }}>
              {parseInlineMarkdown(item, citationSnippets)}
            </li>
          ))}
        </ol>
      );
      continue;
    }

    // 4. Handle Bullet Lists
    const isBulletListLine = (lineStr) => {
      const t = lineStr.trim();
      return (t.startsWith('- ') || t.startsWith('* ')) && !t.startsWith('**');
    };

    if (isBulletListLine(line)) {
      const listItems = [];
      while (i < lines.length && isBulletListLine(lines[i])) {
        const itemTrimmed = lines[i].trim();
        const content = itemTrimmed.substring(2).trim();
        listItems.push(content);
        i++;
      }

      blocks.push(
        <ul key={`list-${i}`} style={{ marginLeft: '24px', marginBottom: '14px', listStyleType: 'disc' }}>
          {listItems.map((item, idx) => (
            <li key={idx} style={{ marginBottom: '6px', color: 'var(--text-primary)', fontSize: '0.92rem' }}>
              {parseInlineMarkdown(item, citationSnippets)}
            </li>
          ))}
        </ul>
      );
      continue;
    }

    // 4. Handle Headings
    if (trimmed.startsWith('###')) {
      blocks.push(
        <h4 key={`h4-${i}`} style={{ margin: '18px 0 8px 0', fontSize: '1.05rem', fontWeight: '700', color: '#ffffff' }}>
          {parseInlineMarkdown(trimmed.replace('###', '').trim(), citationSnippets)}
        </h4>
      );
      i++;
      continue;
    }
    if (trimmed.startsWith('##')) {
      blocks.push(
        <h3 key={`h3-${i}`} style={{ margin: '22px 0 10px 0', fontSize: '1.15rem', fontWeight: '800', color: '#ffffff' }}>
          {parseInlineMarkdown(trimmed.replace('##', '').trim(), citationSnippets)}
        </h3>
      );
      i++;
      continue;
    }
    if (trimmed.startsWith('#')) {
      blocks.push(
        <h2 key={`h2-${i}`} style={{ margin: '26px 0 12px 0', fontSize: '1.3rem', fontWeight: '800', color: '#ffffff' }}>
          {parseInlineMarkdown(trimmed.replace('#', '').trim(), citationSnippets)}
        </h2>
      );
      i++;
      continue;
    }

    // 5. Handle Blank Lines
    if (trimmed === '') {
      blocks.push(<div key={`blank-${i}`} style={{ height: '8px' }} />);
      i++;
      continue;
    }

    // 6. Default Paragraph
    blocks.push(
      <p key={`p-${i}`} style={{ marginBottom: '12px', lineHeight: '1.6', color: 'var(--text-primary)', fontSize: '0.92rem' }}>
        {parseInlineMarkdown(trimmed, citationSnippets)}
      </p>
    );
    i++;
  }

  return blocks;
}


export default function ChatTab({ messages = [], onSendMessage, isThinking, onEditMessage }) {
  const [input, setInput] = useState('');
  const [editingIndex, setEditingIndex] = useState(null);
  const [editInput, setEditInput] = useState('');
  const [copiedIndex, setCopiedIndex] = useState(null);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isThinking]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isThinking) return;
    onSendMessage(input);
    setInput('');
  };

  const handleCopy = (text, index) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', height: '100%', flex: 1 }}>
      
      {/* Scrollable Chat Area */}
      <div 
        className="chat-container" 
        style={{ 
          flex: 1, 
          display: 'flex', 
          flexDirection: 'column', 
          gap: '16px', 
          overflowY: 'auto', 
          padding: '20px',
          border: '1px solid var(--border-color)',
          borderRadius: '12px',
          backgroundColor: 'var(--bg-secondary)'
        }}
      >
        {messages.length === 0 ? (
          <div style={{ margin: 'auto', textAlign: 'center', maxWidth: '400px' }}>
            <div style={{ width: '48px', height: '48px', borderRadius: '50%', background: 'rgba(255, 255, 255, 0.05)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px auto', border: '1px solid var(--border-color)' }}>
              <Bot size={24} />
            </div>
            <h4 style={{ fontWeight: '700', marginBottom: '8px' }}>Chat with Chapter Context</h4>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              Ask anything about this chapter. Your AI tutor will answer with factual references from the textbook and real-time web searches.
            </p>
          </div>
        ) : (
          messages.map((msg, i) => {
            const isUser = msg.role === 'user';
            return (
              <div 
                key={i} 
                style={{ 
                  display: 'flex', 
                  flexDirection: 'column', 
                  alignSelf: isUser ? 'flex-end' : 'flex-start',
                  width: 'fit-content',
                  maxWidth: '80%',
                  gap: '4px',
                  alignItems: isUser ? 'flex-end' : 'flex-start'
                }}
              >
                {/* Header (Role Label) rendered above the bubble */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.75rem', fontWeight: '700', color: 'var(--text-secondary)', opacity: 0.6, margin: '0 4px' }}>
                  {isUser ? <User size={10} /> : <Bot size={10} />}
                  <span>{isUser ? 'You' : 'VedaMate AI Tutor'}</span>
                </div>

                {/* Message Bubble */}
                <div 
                  className={`chat-bubble ${isUser ? 'user' : 'assistant'}`}
                  style={{
                    backgroundColor: isUser ? 'var(--bg-tertiary)' : 'rgba(255,255,255,0.03)',
                    border: '1px solid var(--border-color)',
                    color: 'var(--text-primary)',
                    padding: '12px 38px 12px 16px', // Extra right padding for absolute edit/copy button
                    borderRadius: '12px',
                    width: '100%', 
                    maxWidth: '100%', // Override CSS max-width 80% to fill the parent wrapper
                    fontSize: '0.92rem',
                    lineHeight: '1.5',
                    position: 'relative' // Essential for absolute positioning of icons
                  }}
                >
                  {/* Action Icon placed in the top-right corner of the bubble */}
                  {isUser ? (
                    editingIndex !== i && (
                      <button
                        onClick={() => { setEditingIndex(i); setEditInput(msg.content); }}
                        style={{
                          position: 'absolute',
                          top: '10px',
                          right: '12px',
                          background: 'none',
                          border: 'none',
                          color: 'var(--text-secondary)',
                          cursor: 'pointer',
                          padding: '2px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          opacity: 0.5,
                          transition: 'opacity 0.2s',
                        }}
                        onMouseEnter={(e) => e.currentTarget.style.opacity = 1}
                        onMouseLeave={(e) => e.currentTarget.style.opacity = 0.5}
                        title="Edit query"
                      >
                        <Pencil size={13} style={{ strokeWidth: 2 }} />
                      </button>
                    )
                  ) : (
                    <button
                      onClick={() => handleCopy(msg.content, i)}
                      style={{
                        position: 'absolute',
                        top: '10px',
                        right: '12px',
                        background: 'none',
                        border: 'none',
                        color: copiedIndex === i ? '#10b981' : 'var(--text-secondary)',
                        cursor: 'pointer',
                        padding: '2px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        opacity: copiedIndex === i ? 1 : 0.5,
                        transition: 'opacity 0.2s, color 0.2s',
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.opacity = 1}
                      onMouseLeave={(e) => e.currentTarget.style.opacity = copiedIndex === i ? 1 : 0.5}
                      title="Copy response"
                    >
                      {copiedIndex === i ? <Check size={13} style={{ strokeWidth: 3 }} /> : <Copy size={13} style={{ strokeWidth: 2 }} />}
                    </button>
                  )}

                  {isUser && editingIndex === i ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', width: '100%', minWidth: '220px', marginTop: '4px' }}>
                      <textarea
                        value={editInput}
                        onChange={(e) => setEditInput(e.target.value)}
                        className="textarea-field"
                        style={{
                          width: '100%',
                          minHeight: '60px',
                          fontSize: '0.9rem',
                          backgroundColor: 'rgba(0,0,0,0.2)',
                          border: '1px solid var(--border-color)',
                          color: 'var(--text-primary)',
                          padding: '8px 12px',
                          borderRadius: '8px',
                          resize: 'vertical'
                        }}
                      />
                      <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                        <button
                          onClick={() => {
                            if (editInput.trim()) {
                              onEditMessage(i, editInput.trim());
                              setEditingIndex(null);
                              setEditInput('');
                            }
                          }}
                          className="btn-primary"
                          style={{ padding: '4px 10px', fontSize: '0.75rem', borderRadius: '6px', display: 'flex', alignItems: 'center', gap: '4px' }}
                        >
                          <Check size={12} /> Save
                        </button>
                        <button
                          onClick={() => { setEditingIndex(null); setEditInput(''); }}
                          className="btn-secondary"
                          style={{ padding: '4px 10px', fontSize: '0.75rem', borderRadius: '6px', display: 'flex', alignItems: 'center', gap: '4px' }}
                        >
                          <X size={12} /> Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div style={{ wordBreak: 'break-word' }}>
                      {isUser ? msg.content : renderMarkdown(msg.content, msg.citation_snippets)}
                    </div>
                  )}
                </div>

                {/* Suggested Questions Pills */}
                {!isUser && msg.suggestions && msg.suggestions.length > 0 && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', padding: '0 8px', marginTop: '4px' }}>
                    <span style={{ fontSize: '0.7rem', fontWeight: '700', color: 'var(--text-secondary)', opacity: 0.6, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                      💡 Suggested Questions:
                    </span>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                      {msg.suggestions.map((suggestion, sIdx) => (
                        <button
                          key={sIdx}
                          onClick={() => onSendMessage(suggestion)}
                          style={{
                            background: 'rgba(255, 255, 255, 0.02)',
                            border: '1px solid var(--border-color)',
                            color: 'var(--text-secondary)',
                            padding: '6px 12px',
                            borderRadius: '16px',
                            fontSize: '0.8rem',
                            cursor: 'pointer',
                            textAlign: 'left',
                            transition: 'all 0.2s',
                          }}
                          onMouseEnter={(e) => {
                            e.currentTarget.style.background = 'rgba(255, 255, 255, 0.08)';
                            e.currentTarget.style.color = '#ffffff';
                            e.currentTarget.style.borderColor = '#ffffff';
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.background = 'rgba(255, 255, 255, 0.02)';
                            e.currentTarget.style.color = 'var(--text-secondary)';
                            e.currentTarget.style.borderColor = 'var(--border-color)';
                          }}
                        >
                          {suggestion}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            );
          })
        )}

        {/* Thinking Loader */}
        {isThinking && (
          <div 
            style={{ 
              display: 'flex', 
              flexDirection: 'column', 
              alignSelf: 'flex-start',
              maxWidth: '75%',
              gap: '4px',
              alignItems: 'flex-start'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.75rem', fontWeight: '700', color: 'var(--text-secondary)', opacity: 0.6, margin: '0 4px' }}>
              <Bot size={10} />
              <span>VedaMate AI Tutor</span>
            </div>
            <div 
              className="chat-bubble assistant"
              style={{
                backgroundColor: 'rgba(255,255,255,0.03)',
                border: '1px solid var(--border-color)',
                padding: '12px 16px',
                borderRadius: '12px',
                width: '120px',
                display: 'flex',
                flexDirection: 'column',
                gap: '8px'
              }}
            >
              <div style={{ display: 'flex', gap: '4px' }}>
                <span className="skeleton" style={{ width: '30px', height: '10px' }}></span>
                <span className="skeleton" style={{ width: '50px', height: '10px' }}></span>
                <span className="skeleton" style={{ width: '20px', height: '10px' }}></span>
              </div>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Chat Form Footer */}
      <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about this chapter..."
          className="input-field"
          style={{ flex: 1, padding: '14px 18px' }}
          disabled={isThinking}
        />
        <button 
          type="submit" 
          className="btn-primary" 
          disabled={!input.trim() || isThinking}
          style={{ width: '50px', height: '50px', borderRadius: '50%', padding: 0, flexShrink: 0 }}
        >
          <Send size={16} />
        </button>
      </form>
    </div>
  );
}
