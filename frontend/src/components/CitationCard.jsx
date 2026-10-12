import React, { useState } from 'react';
import { Quote, X, ExternalLink, Clock } from 'lucide-react';

export function CitationCard({ citations }) {
  const [selectedCitation, setSelectedCitation] = useState(null);

  if (!citations || citations.length === 0) return null;

  return (
    <div className="citations-container">
      <div className="citations-label">
        <Quote size={12} />
        <span>Grounded Sources ({citations.length}):</span>
      </div>

      <div className="citation-chips">
        {citations.map((c, i) => (
          <button
            key={i}
            className="citation-chip"
            onClick={() => setSelectedCitation(c)}
            title="Inspect transcript quote"
          >
            <span>{c.guest}</span>
            <span className="citation-time">
              <Clock size={10} style={{ marginRight: 3, verticalAlign: -1 }} />
              {c.timestamp}
            </span>
          </button>
        ))}
      </div>

      {/* Quote Inspection Modal */}
      {selectedCitation && (
        <div className="modal-overlay" onClick={() => setSelectedCitation(null)}>
          <div className="modal-content" role="dialog" aria-modal="true" aria-labelledby="citation-dialog-title" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <div className="modal-guest" id="citation-dialog-title">{selectedCitation.guest}</div>
                <div className="modal-episode">
                  {selectedCitation.episode_title} • {selectedCitation.timestamp}
                </div>
              </div>
              <button className="btn-icon" type="button" aria-label="Close citation details" onClick={() => setSelectedCitation(null)}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-quote-box">
              "{selectedCitation.quote}"
            </div>

            <div style={{ marginTop: 16, display: 'flex', justifyContent: 'flex-end' }}>
              <button
                type="button"
                className="btn-skill-tag"
                onClick={() => setSelectedCitation(null)}
                style={{ padding: '6px 14px' }}
              >
                Close Excerpt
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
