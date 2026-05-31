import React, { useState, useEffect } from 'react';
import { HelpCircle, Layers, Eye, RefreshCw, AlertCircle, CheckCircle2, ChevronLeft, ChevronRight } from 'lucide-react';

export default function QuizTab({
  scenario = null,
  flashcards = [],
  selectedOption = null,
  selectedOptions = {},
  onSelectOption,
  isMastered,
  onMarkMastered,
  onRegenerateAsset,
  initialActivity = 'scenario'
}) {
  const [activity, setActivity] = useState(initialActivity); // 'scenario' | 'flashcards'
  const [cardIdx, setCardIdx] = useState(0);
  const [revealed, setRevealed] = useState(false);
  const [scenarioIdx, setScenarioIdx] = useState(0);

  useEffect(() => {
    setActivity(initialActivity);
  }, [initialActivity]);

  useEffect(() => {
    setCardIdx(0);
    setRevealed(false);
  }, [flashcards]);

  useEffect(() => {
    setScenarioIdx(0);
  }, [scenario]);

  // Scenario Choice Logic
  const handleChooseOption = (optionKey) => {
    onSelectOption(`${scenarioIdx}:${optionKey}`);
  };

  // Flashcards Logic
  const handleReveal = () => {
    setRevealed(!revealed);
  };

  const handleNextCard = () => {
    setRevealed(false);
    setCardIdx((prev) => prev + 1);
  };

  const handleResetDeck = () => {
    setCardIdx(0);
    setRevealed(false);
  };

  // Resolve scenario list safely
  const scenarioList = scenario?.scenarios || (Array.isArray(scenario) ? scenario : (scenario ? [scenario] : []));
  const currentScenario = scenarioList[scenarioIdx];

  // Resolve selected option for current scenario index
  const currentSelectedOption = selectedOptions && selectedOptions[scenarioIdx] !== undefined 
    ? selectedOptions[scenarioIdx] 
    : (scenarioIdx === 0 ? selectedOption : null);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>

      {/* ACTIVITY A: Scenario Sandbox */}
      {activity === 'scenario' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {scenarioList.length > 0 && currentScenario ? (
            <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              
              {/* Header with Navigation Arrows */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-color)', paddingBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <HelpCircle size={18} style={{ color: 'var(--accent-purple)' }} />
                  <span style={{ fontSize: '0.85rem', fontWeight: '700', color: 'var(--text-secondary)' }}>
                    Scenario {scenarioIdx + 1} of {scenarioList.length}
                  </span>
                </div>
                
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <button
                    onClick={() => setScenarioIdx(prev => Math.max(0, prev - 1))}
                    disabled={scenarioIdx === 0}
                    className="btn-secondary"
                    style={{ padding: '6px 12px', display: 'flex', alignItems: 'center', gap: '4px', opacity: scenarioIdx === 0 ? 0.4 : 1, cursor: scenarioIdx === 0 ? 'not-allowed' : 'pointer', fontSize: '0.8rem' }}
                  >
                    <ChevronLeft size={14} /> Prev
                  </button>
                  <button
                    onClick={() => setScenarioIdx(prev => Math.min(scenarioList.length - 1, prev + 1))}
                    disabled={scenarioIdx === scenarioList.length - 1}
                    className="btn-secondary"
                    style={{ padding: '6px 12px', display: 'flex', alignItems: 'center', gap: '4px', opacity: scenarioIdx === scenarioList.length - 1 ? 0.4 : 1, cursor: scenarioIdx === scenarioList.length - 1 ? 'not-allowed' : 'pointer', fontSize: '0.8rem' }}
                  >
                    Next <ChevronRight size={14} />
                  </button>
                  
                  {onRegenerateAsset && (
                    <button 
                      className="btn-secondary" 
                      onClick={() => onRegenerateAsset('scenario')}
                      style={{ padding: '6px 12px', display: 'flex', alignItems: 'center', gap: '4px', borderLeft: '1px solid var(--border-color)', marginLeft: '8px', color: 'var(--accent-purple)', fontSize: '0.8rem' }}
                    >
                      <RefreshCw size={12} />
                      New List
                    </button>
                  )}
                </div>
              </div>

              {/* Scenario Situation */}
              <div>
                <p style={{ fontSize: '0.95rem', lineHeight: '1.6', color: 'var(--text-primary)' }}>
                  {currentScenario.situation}
                </p>
              </div>

              {/* Options */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '12px', marginTop: '12px' }}>
                {['A', 'B', 'C'].map((optKey) => {
                  const option = currentScenario.options[optKey];
                  const isSelected = currentSelectedOption === optKey;
                  
                  return (
                    <button
                      key={optKey}
                      onClick={() => handleChooseOption(optKey)}
                      style={{
                        padding: '16px 20px',
                        borderRadius: '8px',
                        border: '1px solid',
                        borderColor: isSelected ? '#ffffff' : 'var(--border-color)',
                        backgroundColor: isSelected ? 'rgba(255,255,255,0.05)' : 'var(--bg-secondary)',
                        color: 'var(--text-primary)',
                        textAlign: 'left',
                        cursor: 'pointer',
                        transition: 'all 0.15s ease',
                        fontSize: '0.9rem',
                        fontWeight: isSelected ? '600' : '500'
                      }}
                    >
                      <strong style={{ marginRight: '8px' }}>Option {optKey}:</strong> {option.text}
                    </button>
                  );
                })}
              </div>

              {/* Display choice feedback */}
              {currentSelectedOption && currentScenario.options[currentSelectedOption] && (
                <div 
                  style={{ 
                    marginTop: '20px',
                    padding: '20px',
                    borderRadius: '8px',
                    border: '1px solid',
                    backgroundColor: 'var(--bg-secondary)',
                    borderColor: currentScenario.options[currentSelectedOption].is_correct ? '#ffffff' : '#441111',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '8px'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: '700', fontSize: '0.95rem' }}>
                    {currentScenario.options[currentSelectedOption].is_correct ? (
                      <span style={{ color: '#ffffff' }}>✓ Option {currentSelectedOption} is Correct!</span>
                    ) : (
                      <span style={{ color: '#ff8888' }}>✗ Option {currentSelectedOption} is Sub-optimal.</span>
                    )}
                  </div>
                  <p style={{ fontSize: '0.88rem', lineHeight: '1.5', color: 'var(--text-secondary)' }}>
                    {currentScenario.options[currentSelectedOption].feedback}
                  </p>
                </div>
              )}
            </div>
          ) : (
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Loading scenario...</p>
          )}
        </div>
      )}

      {/* ACTIVITY B: Flashcards active recall */}
      {activity === 'flashcards' && (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '20px' }}>
          {flashcards.length > 0 ? (
            cardIdx < flashcards.length ? (
              <div style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                
                {/* Header with Counter and Refresh */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', maxWidth: '500px', marginBottom: '12px' }}>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', margin: 0 }}>
                    Card {cardIdx + 1} of {flashcards.length}
                  </p>
                  {onRegenerateAsset && (
                    <button 
                      className="btn-secondary" 
                      onClick={() => onRegenerateAsset('flashcards')}
                      style={{ padding: '6px 10px', fontSize: '0.75rem', display: 'inline-flex', alignItems: 'center', gap: '4px', borderRadius: '6px' }}
                    >
                      <RefreshCw size={10} />
                      New Flashcards
                    </button>
                  )}
                </div>

                {/* 3D Flippable Card */}
                <div 
                  className={`flashcard-wrapper ${revealed ? 'flipped' : ''}`}
                  onClick={handleReveal}
                >
                  <div className="flashcard-inner">
                    
                    {/* Front */}
                    <div className="flashcard-front">
                      <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '16px' }}>
                        Question
                      </p>
                      <h4 style={{ fontSize: '1.15rem', fontWeight: '600', lineHeight: '1.5' }}>
                        {flashcards[cardIdx].front}
                      </h4>
                      <div style={{ marginTop: '24px', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        <Eye size={12} /> Click card to reveal answer
                      </div>
                    </div>

                    {/* Back */}
                    <div className="flashcard-back">
                      <p style={{ fontSize: '0.75rem', opacity: 0.6, textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '16px' }}>
                        Correct Explanation
                      </p>
                      <h4 style={{ fontSize: '1.15rem', fontWeight: '700', lineHeight: '1.5', marginBottom: '16px' }}>
                        {flashcards[cardIdx].back}
                      </h4>
                      <p style={{ fontSize: '0.75rem', opacity: 0.5 }}>
                        Click card to view question
                      </p>
                    </div>

                  </div>
                </div>

                {/* Navigation and Assessment Buttons */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', width: '100%', maxWidth: '500px', marginTop: '24px' }}>
                  
                  {/* Styled Arrows Navigation */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
                    <button
                      onClick={() => {
                        setCardIdx(prev => Math.max(0, prev - 1));
                        setRevealed(false);
                      }}
                      disabled={cardIdx === 0}
                      className="btn-secondary"
                      style={{ padding: '8px 16px', display: 'flex', alignItems: 'center', gap: '6px', opacity: cardIdx === 0 ? 0.4 : 1, cursor: cardIdx === 0 ? 'not-allowed' : 'pointer', fontSize: '0.85rem' }}
                    >
                      <ChevronLeft size={16} /> Previous Card
                    </button>
                    <button
                      onClick={() => {
                        setCardIdx(prev => Math.min(flashcards.length, prev + 1));
                        setRevealed(false);
                      }}
                      className="btn-secondary"
                      style={{ padding: '8px 16px', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem' }}
                    >
                      Next Card <ChevronRight size={16} />
                    </button>
                  </div>

                  {revealed && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', width: '100%', textAlign: 'center', borderTop: '1px solid var(--border-color)', paddingTop: '16px', marginTop: '8px' }}>
                      <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', margin: 0 }}>Self-Assess Your Recall:</p>
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <button 
                          className="btn-secondary" 
                          onClick={handleNextCard}
                          style={{ flex: 1, borderColor: '#441111', color: '#ff8888' }}
                        >
                          🔴 Hard
                        </button>
                        <button 
                          className="btn-secondary" 
                          onClick={handleNextCard}
                          style={{ flex: 1, borderColor: 'var(--border-color)', color: 'var(--text-primary)' }}
                        >
                          🟡 Good
                        </button>
                        <button 
                          className="btn-primary" 
                          onClick={handleNextCard}
                          style={{ flex: 1 }}
                        >
                          🟢 Easy
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="glass-panel" style={{ textAlign: 'center', width: '100%', maxWidth: '500px', padding: '32px' }}>
                <CheckCircle2 size={36} style={{ margin: '0 auto 16px auto', color: '#ffffff' }} />
                <h4 style={{ fontWeight: '700', marginBottom: '8px' }}>Deck Review Completed!</h4>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '20px' }}>
                  You have reviewed all {flashcards.length} active recall cards.
                </p>
                <div style={{ display: 'flex', justifyContent: 'center', gap: '12px', flexWrap: 'wrap' }}>
                  <button
                    className="btn-secondary"
                    onClick={() => {
                      setCardIdx(flashcards.length - 1);
                      setRevealed(false);
                    }}
                    style={{ display: 'inline-flex', gap: '6px', alignItems: 'center' }}
                  >
                    <ChevronLeft size={14} /> Back to Last Card
                  </button>
                  <button className="btn-secondary" onClick={handleResetDeck} style={{ display: 'inline-flex', gap: '8px', alignItems: 'center' }}>
                    <RefreshCw size={14} /> Reset Recall Deck
                  </button>
                  {onRegenerateAsset && (
                    <button className="btn-primary" onClick={() => onRegenerateAsset('flashcards')} style={{ display: 'inline-flex', gap: '8px', alignItems: 'center' }}>
                      <Layers size={14} /> New Flashcards
                    </button>
                  )}
                </div>
              </div>
            )
          ) : (
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Loading flashcards...</p>
          )}
        </div>
      )}

    </div>
  );
}
