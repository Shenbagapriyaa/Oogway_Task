import React from 'react';
import { MessageSquare, Plus, Trash2, Database } from 'lucide-react';

export function SessionSidebar({
  sessions,
  activeSessionId,
  onSelectSession,
  onNewChat,
  onDeleteSession,
  isOpen
}) {
  return (
    <aside className={`sidebar ${isOpen ? '' : 'collapsed'}`}>
      <div className="sidebar-header">
        <button className="btn-new-chat" onClick={onNewChat}>
          <Plus size={16} />
          <span>New Session</span>
        </button>
      </div>

      <div className="session-list">
        {sessions.length === 0 ? (
          <div style={{ padding: '24px 12px', textAlign: 'center', color: '#6b7280', fontSize: '13px' }}>
            No past sessions yet. Ask a question to get started.
          </div>
        ) : (
          sessions.map((s) => (
            <div
              key={s.id}
              className={`session-item ${s.id === activeSessionId ? 'active' : ''}`}
              onClick={() => onSelectSession(s.id)}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', overflow: 'hidden' }}>
                <MessageSquare size={14} style={{ flexShrink: 0, opacity: 0.7 }} />
                <div className="session-info">
                  <span className="session-title">{s.title || 'Growth Session'}</span>
                  <span className="session-date">
                    {new Date(s.updated_at || s.created_at).toLocaleDateString([], {
                      month: 'short',
                      day: 'numeric'
                    })}
                  </span>
                </div>
              </div>
              <button
                className="btn-icon"
                onClick={(e) => {
                  e.stopPropagation();
                  onDeleteSession(s.id);
                }}
                title="Delete session"
                style={{ opacity: 0.6 }}
              >
                <Trash2 size={13} />
              </button>
            </div>
          ))
        )}
      </div>

      <div className="sidebar-footer">
        <Database size={14} color="#10b981" />
        <span>50 Podcast Transcripts Indexed</span>
      </div>
    </aside>
  );
}
