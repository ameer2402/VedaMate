import React, { useState, useEffect } from 'react';
import { User, Check } from 'lucide-react';

const INTERESTS_OPTIONS = [
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
];

export default function GlobalProfile({ initialProfile, onSave, onCancel }) {
  const [level, setLevel] = useState(initialProfile?.education_level || "College Undergraduate");
  const [selectedInterests, setSelectedInterests] = useState([]);

  useEffect(() => {
    if (initialProfile?.interests) {
      const interestsArray = initialProfile.interests
        .split(',')
        .map(i => i.trim())
        .filter(i => INTERESTS_OPTIONS.includes(i));
      setSelectedInterests(interestsArray);
    }
  }, [initialProfile]);

  const handleToggleInterest = (interest) => {
    if (selectedInterests.includes(interest)) {
      setSelectedInterests(selectedInterests.filter(i => i !== interest));
    } else {
      setSelectedInterests([...selectedInterests, interest]);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const interestsStr = selectedInterests.join(', ') || 'General';
    onSave({ education_level: level, interests: interestsStr });
  };

  return (
    <div style={{ maxWidth: '600px', margin: '40px auto', padding: '12px' }}>
      <div className="glass-panel" style={{ border: '1px solid var(--border-color)', background: 'var(--bg-tertiary)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
          <div style={{ background: '#ffffff', color: '#000000', borderRadius: '50%', padding: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <User size={24} />
          </div>
          <div>
            <h2 style={{ fontSize: '1.4rem', fontWeight: '800', letterSpacing: '-0.02em' }}>Configure Persona Settings</h2>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Personalize explanations, analogies, and scenarios to match your background.</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: '700', textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: '8px' }}>
              Education Level
            </label>
            <select
              value={level}
              onChange={(e) => setLevel(e.target.value)}
              style={{
                width: '100%',
                padding: '12px',
                backgroundColor: 'var(--bg-secondary)',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                color: 'var(--text-primary)',
                outline: 'none'
              }}
            >
              {["Middle School", "High School", "College Undergraduate", "Graduate", "Professional"].map((l) => (
                <option key={l} value={l}>{l}</option>
              ))}
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: '700', textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: '8px' }}>
              Hobbies & Interests (Select multiple)
            </label>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: '8px', maxHeight: '200px', overflowY: 'auto', paddingRight: '8px', border: '1px solid var(--border-color)', padding: '12px', borderRadius: '8px', backgroundColor: 'var(--bg-secondary)' }}>
              {INTERESTS_OPTIONS.map((interest) => {
                const isSelected = selectedInterests.includes(interest);
                return (
                  <button
                    type="button"
                    key={interest}
                    onClick={() => handleToggleInterest(interest)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      padding: '8px 12px',
                      borderRadius: '6px',
                      border: '1px solid',
                      borderColor: isSelected ? 'var(--text-primary)' : 'var(--border-color)',
                      backgroundColor: isSelected ? 'rgba(255, 255, 255, 0.05)' : 'transparent',
                      color: isSelected ? 'var(--text-primary)' : 'var(--text-secondary)',
                      fontSize: '0.75rem',
                      cursor: 'pointer',
                      textAlign: 'left',
                      transition: 'all 0.1s ease'
                    }}
                  >
                    <div style={{ width: '12px', height: '12px', border: '1px solid var(--text-muted)', borderRadius: '3px', display: 'flex', alignItems: 'center', justifyContent: 'center', background: isSelected ? '#ffffff' : 'transparent' }}>
                      {isSelected && <Check size={10} style={{ color: '#000000', strokeWidth: 3 }} />}
                    </div>
                    <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{interest}</span>
                  </button>
                );
              })}
            </div>
          </div>

          <div style={{ display: 'flex', gap: '12px', marginTop: '12px' }}>
            <button type="submit" className="btn-primary" style={{ flex: 1 }}>
              Save Profile & Start Study
            </button>
            {onCancel && (
              <button type="button" className="btn-secondary" onClick={onCancel} style={{ flex: 1 }}>
                Cancel
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}
