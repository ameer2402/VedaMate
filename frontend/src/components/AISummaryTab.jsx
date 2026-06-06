import React, { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';
import { Award, Youtube, Globe, ExternalLink, BookOpen } from 'lucide-react';

// Override default error callback to prevent raw error banners in the DOM
mermaid.parseError = (err, hash) => {
  console.warn("Intercepted Mermaid parse error:", err);
  // Proactively clean up any error divs appended to document.body by Mermaid
  const errorElements = document.querySelectorAll('.mermaid-error-span, [id^="dmermaid-"], [id^="mermaid-"]');
  errorElements.forEach(el => {
    if (el && el.parentNode === document.body) {
      el.remove();
    }
  });
};

mermaid.initialize({
  startOnLoad: false,
  theme: 'base',
  securityLevel: 'loose',
  suppressErrorNotifications: true,
  themeVariables: {
    background: '#0a0e1a',
    primaryColor: '#151e36',
    primaryTextColor: '#f8fafc',
    primaryBorderColor: '#6366f1',
    lineColor: '#8b5cf6',
    secondaryColor: '#0f1526',
    tertiaryColor: '#1a2542'
  }
});

function MermaidRenderer({ chartCode, onNodeClick }) {
  const containerRef = useRef(null);

  useEffect(() => {
    if (containerRef.current && chartCode) {
      containerRef.current.removeAttribute('data-processed');
      containerRef.current.innerHTML = '';
      
      const cleanCode = chartCode
        .replace(/```mermaid/g, '')
        .replace(/```/g, '')
        .trim();

      // First, parse/validate the code to prevent document.body error injections
      mermaid.parse(cleanCode)
        .then(() => {
          const id = 'mermaid-render-' + Math.floor(Math.random() * 1000000);
          mermaid.render(id, cleanCode)
            .then(({ svg }) => {
              if (containerRef.current) {
                containerRef.current.innerHTML = svg;
              }
              // Clean up any temporary elements created by mermaid in body
              const bindErrorEl = document.getElementById('d' + id);
              if (bindErrorEl) bindErrorEl.remove();
            })
            .catch(err => {
              console.error("Mermaid render failed:", err);
              // Clean up errors injected into body
              const errEl = document.getElementById(id);
              if (errEl) errEl.remove();
              const bindErrorEl = document.getElementById('d' + id);
              if (bindErrorEl) bindErrorEl.remove();
              
              if (containerRef.current) {
                containerRef.current.innerHTML = `<p style="color:var(--text-secondary);font-size:0.8rem;text-align:center;">[Flowchart compilation error]</p>`;
              }
            });
        })
        .catch(err => {
          console.warn("Mermaid code validation failed:", err);
          if (containerRef.current) {
            containerRef.current.innerHTML = `<p style="color:var(--text-secondary);font-size:0.8rem;text-align:center;">[Flowchart syntax error: unable to render diagram]</p>`;
          }
          // Clean up any error visual remnants
          const errorElements = document.querySelectorAll('.mermaid-error-span, [id^="dmermaid-"], [id^="mermaid-"]');
          errorElements.forEach(el => {
            if (el && el.parentNode === document.body) {
              el.remove();
            }
          });
        });
    }
  }, [chartCode]);

  useEffect(() => {
    const handleSvgClick = (e) => {
      const nodeEl = e.target.closest('.node');
      if (nodeEl) {
        e.preventDefault();
        e.stopPropagation();

        const labelEl = nodeEl.querySelector('.label') || nodeEl.querySelector('text') || nodeEl;
        let nodeText = labelEl.textContent || labelEl.innerText || "";
        
        // Clean text content (remove inline carriage returns, extra spaces)
        nodeText = nodeText.replace(/\r?\n|\r/g, ' ').replace(/\s+/g, ' ').trim();
        
        if (nodeText && onNodeClick) {
          const rect = nodeEl.getBoundingClientRect();
          onNodeClick({
            text: nodeText,
            x: rect.left + rect.width / 2,
            y: rect.top - 10
          });
        }
      }
    };

    const container = containerRef.current;
    if (container) {
      container.addEventListener('click', handleSvgClick);
    }
    return () => {
      if (container) {
        container.removeEventListener('click', handleSvgClick);
      }
    };
  }, [chartCode, onNodeClick]);

  return (
    <div 
      ref={containerRef} 
      style={{ 
        background: 'rgba(15, 21, 38, 0.4)', 
        padding: '24px', 
        borderRadius: '12px', 
        border: '1px solid var(--border-color)', 
        display: 'flex', 
        justifyContent: 'center', 
        overflowX: 'auto',
        marginTop: '16px' 
      }} 
    />
  );
}

function parseInlineMarkdown(text) {
  if (!text) return "";
  
  let parts = [text];
  
  // 1. Inline code: `code`
  parts = parts.flatMap(part => {
    if (typeof part !== 'string') return part;
    const regex = /`([^`]+)`/g;
    const subParts = [];
    let lastIdx = 0;
    let match;
    while ((match = regex.exec(part)) !== null) {
      if (match.index > lastIdx) {
        subParts.push(part.substring(lastIdx, match.index));
      }
      subParts.push(
        <code key={match.index} style={{
          background: 'rgba(99, 102, 241, 0.1)',
          color: '#a78bfa',
          padding: '2px 6px',
          borderRadius: '4px',
          fontFamily: 'monospace',
          fontSize: '0.85em',
          border: '1px solid rgba(139, 92, 246, 0.2)'
        }}>
          {match[1]}
        </code>
      );
      lastIdx = regex.lastIndex;
    }
    if (lastIdx < part.length) {
      subParts.push(part.substring(lastIdx));
    }
    return subParts;
  });

  // 2. Bold: **bold**
  parts = parts.flatMap(part => {
    if (typeof part !== 'string') return part;
    const regex = /\*\*([^*]+)\*\*/g;
    const subParts = [];
    let lastIdx = 0;
    let match;
    while ((match = regex.exec(part)) !== null) {
      if (match.index > lastIdx) {
        subParts.push(part.substring(lastIdx, match.index));
      }
      subParts.push(
        <strong key={match.index} style={{ fontWeight: '700', color: '#ffffff' }}>
          {match[1]}
        </strong>
      );
      lastIdx = regex.lastIndex;
    }
    if (lastIdx < part.length) {
      subParts.push(part.substring(lastIdx));
    }
    return subParts;
  });

  // 3. Italic: *italic*
  parts = parts.flatMap(part => {
    if (typeof part !== 'string') return part;
    const regex = /\*([^*]+)\*/g;
    const subParts = [];
    let lastIdx = 0;
    let match;
    while ((match = regex.exec(part)) !== null) {
      if (match.index > lastIdx) {
        subParts.push(part.substring(lastIdx, match.index));
      }
      subParts.push(
        <em key={match.index} style={{ fontStyle: 'italic', color: '#cbd5e1' }}>
          {match[1]}
        </em>
      );
      lastIdx = regex.lastIndex;
    }
    if (lastIdx < part.length) {
      subParts.push(part.substring(lastIdx));
    }
    return subParts;
  });

  return parts;
}

function renderMarkdown(text) {
  if (!text) return null;

  const lines = text.split('\n');
  const blocks = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];
    const trimmed = line.trim();

    // 0. Handle Horizontal Rules
    if (/^([-*_])\1\1+$/.test(trimmed) || trimmed === '---' || trimmed === '--') {
      blocks.push(
        <hr key={`hr-${i}`} style={{ border: 'none', borderTop: '1px solid var(--border-color)', margin: '20px 0', opacity: 0.5 }} />
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
        <pre key={`code-${i}`} style={{
          background: 'rgba(0, 0, 0, 0.4)',
          border: '1px solid var(--border-color)',
          padding: '16px',
          borderRadius: '8px',
          overflowX: 'auto',
          fontFamily: 'monospace',
          fontSize: '0.85rem',
          color: '#e2e8f0',
          margin: '16px 0'
        }}>
          <code>{codeLines.join('\n')}</code>
        </pre>
      );
      continue;
    }

    // 2. Handle Tables
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
          <div key={`table-${i}`} style={{ overflowX: 'auto', margin: '20px 0', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem', textAlign: 'left', background: 'rgba(15, 23, 42, 0.2)' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid var(--border-color)', background: 'rgba(255, 255, 255, 0.04)' }}>
                  {headerCells.map((cell, cIdx) => (
                    <th key={cIdx} style={{ padding: '12px 16px', fontWeight: '700', color: '#ffffff' }}>
                      {parseInlineMarkdown(cell)}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {bodyRows.map((rowCells, rIdx) => (
                  <tr key={rIdx} style={{
                    borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
                    background: rIdx % 2 === 1 ? 'rgba(255, 255, 255, 0.01)' : 'transparent'
                  }}>
                    {rowCells.map((cell, cIdx) => (
                      <td key={cIdx} style={{ padding: '10px 16px', color: 'var(--text-primary)' }}>
                        {parseInlineMarkdown(cell)}
                      </td>
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

    // 3. Handle Ordered Lists
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
            <li key={idx} style={{ marginBottom: '6px', color: 'var(--text-primary)', fontSize: '0.95rem', lineHeight: '1.5' }}>
              {parseInlineMarkdown(item)}
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
            <li key={idx} style={{ marginBottom: '6px', color: 'var(--text-primary)', fontSize: '0.95rem', lineHeight: '1.5' }}>
              {parseInlineMarkdown(item)}
            </li>
          ))}
        </ul>
      );
      continue;
    }

    // 5. Handle Headings
    if (trimmed.startsWith('####')) {
      blocks.push(
        <h5 key={`h5-${i}`} style={{ margin: '16px 0 8px 0', fontSize: '1.0rem', fontWeight: '700', color: '#ffffff' }}>
          {parseInlineMarkdown(trimmed.replace('####', '').trim())}
        </h5>
      );
      i++;
      continue;
    }
    if (trimmed.startsWith('###')) {
      blocks.push(
        <h4 key={`h4-${i}`} style={{ margin: '20px 0 10px 0', fontSize: '1.1rem', fontWeight: '700', color: '#ffffff' }}>
          {parseInlineMarkdown(trimmed.replace('###', '').trim())}
        </h4>
      );
      i++;
      continue;
    }
    if (trimmed.startsWith('##')) {
      blocks.push(
        <h3 key={`h3-${i}`} style={{ margin: '24px 0 12px 0', fontSize: '1.25rem', fontWeight: '800', color: '#ffffff' }}>
          {parseInlineMarkdown(trimmed.replace('##', '').trim())}
        </h3>
      );
      i++;
      continue;
    }
    if (trimmed.startsWith('#')) {
      blocks.push(
        <h2 key={`h2-${i}`} style={{ margin: '28px 0 16px 0', fontSize: '1.5rem', fontWeight: '800', color: '#ffffff' }}>
          {parseInlineMarkdown(trimmed.replace('#', '').trim())}
        </h2>
      );
      i++;
      continue;
    }

    // 6. Handle Blank Lines
    if (trimmed === '') {
      blocks.push(<div key={`blank-${i}`} style={{ height: '8px' }} />);
      i++;
      continue;
    }

    // 7. Default Paragraph
    blocks.push(
      <p key={`p-${i}`} style={{ marginBottom: '14px', lineHeight: '1.6', color: 'var(--text-primary)', fontSize: '0.95rem' }}>
        {parseInlineMarkdown(trimmed)}
      </p>
    );
    i++;
  }

  return blocks;
}

export default function AISummaryTab({ hookText, chartCode, resources = [], onExplainConcept }) {
  const [explainTooltip, setExplainTooltip] = useState(null);

  useEffect(() => {
    const closeTooltip = () => setExplainTooltip(null);
    window.addEventListener('click', closeTooltip);
    return () => window.removeEventListener('click', closeTooltip);
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '32px', position: 'relative' }}>
      
      {/* Click explanation interactive tooltip */}
      {explainTooltip && (
        <div
          style={{
            position: 'fixed',
            left: `${explainTooltip.x}px`,
            top: `${explainTooltip.y}px`,
            transform: 'translate(-50%, -100%)',
            background: 'rgba(15, 23, 42, 0.95)',
            border: '1px solid var(--border-color)',
            borderRadius: '12px',
            padding: '12px',
            boxShadow: '0 10px 30px rgba(0, 0, 0, 0.6), 0 0 15px rgba(99, 102, 241, 0.2)',
            zIndex: 10000,
            width: '260px',
            display: 'flex',
            flexDirection: 'column',
            gap: '8px',
            backdropFilter: 'blur(12px)',
            pointerEvents: 'auto'
          }}
          onClick={(e) => e.stopPropagation()} // Prevent closing tooltip
        >
          <div style={{ fontSize: '0.8rem', fontWeight: '700', color: 'var(--text-secondary)', marginBottom: '4px', textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }}>
            💡 Explain "{explainTooltip.text}"
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={() => {
                if (onExplainConcept) onExplainConcept('eli5', explainTooltip.text);
                setExplainTooltip(null);
              }}
              style={{
                flex: 1,
                background: 'linear-gradient(135deg, var(--accent-indigo) 0%, var(--accent-purple) 100%)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                color: '#ffffff',
                padding: '6px 8px',
                borderRadius: '8px',
                fontSize: '0.78rem',
                fontWeight: '600',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '4px'
              }}
            >
              👶 ELI5
            </button>
            <button
              onClick={() => {
                if (onExplainConcept) onExplainConcept('deep_dive', explainTooltip.text);
                setExplainTooltip(null);
              }}
              style={{
                flex: 1,
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid var(--border-color)',
                color: 'var(--text-primary)',
                padding: '6px 8px',
                borderRadius: '8px',
                fontSize: '0.78rem',
                fontWeight: '600',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '4px'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)';
              }}
            >
              🔍 Deep Dive
            </button>
          </div>
        </div>
      )}

      {/* Comprehensive Textbook Summary card */}
      {hookText && (
        <div className="glass-panel" style={{ borderLeft: '3px solid var(--accent-purple)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <BookOpen size={20} style={{ color: 'var(--accent-purple)' }} />
            <h3 style={{ fontSize: '1.1rem', fontWeight: '700', color: '#ffffff' }}>Comprehensive Textbook Summary</h3>
          </div>
          <div className="markdown-content" style={{ lineHeight: '1.7', fontSize: '0.95rem' }}>
            {renderMarkdown(hookText)}
          </div>
        </div>
      )}

      {/* Visual map card */}
      {chartCode && (
        <div className="glass-panel">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
            <Award size={20} />
            <h3 style={{ fontSize: '1.1rem', fontWeight: '700' }}>Visual Concept Flowchart</h3>
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '12px' }}>
            A structured mindmap highlighting sub-processes and relationships within this chapter.
          </p>
          <MermaidRenderer chartCode={chartCode} onNodeClick={setExplainTooltip} />
        </div>
      )}

      {/* Recommended Learning Resources */}
      {resources && resources.length > 0 && (
        <div className="glass-panel">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <BookOpen size={20} />
            <h3 style={{ fontSize: '1.15rem', fontWeight: '700' }}>Recommended Study Resources</h3>
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '16px' }}>
            Hand-curated video search links and educational materials to extend your learning on this topic.
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
            {resources.map((res, index) => {
              const isVideo = res.type === 'video';
              return (
                <a
                  key={index}
                  href={res.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    background: 'rgba(255, 255, 255, 0.02)',
                    border: '1px solid var(--border-color)',
                    borderRadius: '12px',
                    padding: '16px',
                    textDecoration: 'none',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '10px',
                    transition: 'all 0.3s ease',
                    color: 'inherit'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = 'var(--accent-purple)';
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.background = 'rgba(167, 139, 250, 0.05)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = 'var(--border-color)';
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.background = 'rgba(255, 255, 255, 0.02)';
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: isVideo ? '#ef4444' : 'var(--accent-purple)' }}>
                      {isVideo ? <Youtube size={16} /> : <Globe size={16} />}
                      <span style={{ fontSize: '0.7rem', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                        {res.type}
                      </span>
                    </div>
                    <ExternalLink size={12} style={{ color: 'var(--text-muted)' }} />
                  </div>
                  <h4 style={{ fontSize: '0.9rem', fontWeight: '700', color: '#ffffff', margin: 0 }}>
                    {res.title}
                  </h4>
                  <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: '1.4', margin: 0 }}>
                    {res.description}
                  </p>
                </a>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
