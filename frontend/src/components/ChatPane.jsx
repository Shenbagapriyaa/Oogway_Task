import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, FileText, Layout, ArrowRight } from 'lucide-react';
import { CitationCard } from './CitationCard';
import { renderMarkdown } from '../utils/renderMarkdown';

export function ChatPane({
  messages,
  isLoading,
  onSendMessage,
  onOpenArtifact,
  onPromptClick
}) {
  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSubmit = (e) => {
    e?.preventDefault();
    if (!inputText.trim() || isLoading) return;
    onSendMessage(inputText);
    setInputText('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="main-chat-area">
      <div className="messages-scroll">
        {messages.length === 0 ? (
          <div className="welcome-hero">
            <h1 className="hero-title">The Lenny Growth Assistant</h1>
            <p className="hero-sub">
              Your forward-deployed AI partner trained directly on 50+ transcripts of Lenny’s Podcast.
              Ask complex growth questions, generate Ship 30 for 30 essays, and preview interactive artifacts natively.
            </p>

            <div className="quick-prompts-grid">
              <button
                type="button"
                className="prompt-card"
                onClick={() => onPromptClick("What did Elena Verna say about AI companies having to recapture product-market fit every 3 months?")}
              >
                <div className="prompt-card-header">
                  <Sparkles size={14} /> Elena Verna • AI Growth
                </div>
                <div className="prompt-card-text">
                  "Why must AI companies recapture product-market fit every 3 months?"
                </div>
              </button>

              <button
                type="button"
                className="prompt-card"
                onClick={() => onPromptClick("Write a Ship 30 for 30 essay on Elena Verna's product-led growth loops and Lovable's scaling playbook", "ship30")}
              >
                <div className="prompt-card-header">
                  <FileText size={14} /> Ship 30 for 30 Skill
                </div>
                <div className="prompt-card-text">
                  "Generate a ~1,250-word atomic essay on Lovable's PLG loops and reinvention."
                </div>
              </button>

              <button
                type="button"
                className="prompt-card"
                onClick={() => onPromptClick("Build an interactive HTML/CSS Viral Coefficient and K-Factor calculator", "artifact_html")}
              >
                <div className="prompt-card-header">
                  <Layout size={14} /> Native HTML Artifact
                </div>
                <div className="prompt-card-text">
                  "Build an interactive viral growth calculator with slider controls."
                </div>
              </button>

              <button
                type="button"
                className="prompt-card"
                onClick={() => onPromptClick("What is Keith Rabois's concept of hiring Barrels vs. Ammo?")}
              >
                <div className="prompt-card-header">
                  <Sparkles size={14} /> Keith Rabois • Leadership
                </div>
                <div className="prompt-card-text">
                  "Explain the Barrels vs. Ammo hiring framework and how to spot barrels."
                </div>
              </button>
            </div>
          </div>
        ) : (
          messages.map((m) => {
            const isAssistant = m.role === 'assistant';
            return (
              <div key={m.id} className={`message-row ${m.role}`}>
                {isAssistant && (
                  <div className="message-avatar assistant">
                    ⚡
                  </div>
                )}

                <div className="message-bubble">
                  {isAssistant ? (
                    <div dangerouslySetInnerHTML={{ __html: renderMarkdown(m.content) }} />
                  ) : (
                    <div>{m.content}</div>
                  )}

                  {/* Grounded Citations */}
                  {isAssistant && m.citations && m.citations.length > 0 && (
                    <CitationCard citations={m.citations} />
                  )}

                  {/* Produced Artifact Attachment */}
                  {isAssistant && m.artifacts && m.artifacts.length > 0 && (
                    m.artifacts.map((art) => (
                      <button
                        type="button"
                        key={art.id || art.title}
                        className="artifact-attachment-card"
                        onClick={() => onOpenArtifact(art)}
                      >
                        <div className="artifact-info">
                          <div className="artifact-icon">
                            {art.type === 'html' ? <Layout size={18} /> : <FileText size={18} />}
                          </div>
                          <div>
                            <div className="artifact-text-title">{art.title}</div>
                            <div className="artifact-text-sub">
                              Click to inspect in Claude Artifact Viewer
                            </div>
                          </div>
                        </div>
                        <ArrowRight size={16} color="#818cf8" />
                      </button>
                    ))
                  )}
                </div>
              </div>
            );
          })
        )}

        {isLoading && (
          <div className="message-row assistant">
            <div className="message-avatar assistant">⚡</div>
            <div className="message-bubble" style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#9ca3af' }}>
              <span className="status-indicator ready" />
              <span>Retrieving Lenny's transcripts and synthesizing response...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Bar */}
      <div className="input-area-wrapper">
        <div className="input-container">
          <textarea
            className="input-field"
            aria-label="Message the Lenny Growth Assistant"
            placeholder="Ask a product or growth question from Lenny's library..."
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={1}
          />
          <div className="input-toolbar">
            <div className="input-quick-actions">
              <button
                type="button"
                className="btn-skill-tag"
                onClick={() => setInputText("Write a Ship 30 for 30 essay on ")}
              >
                <FileText size={12} />
                <span>Write Ship 30 Essay</span>
              </button>
              <button
                type="button"
                className="btn-skill-tag"
                onClick={() => setInputText("Build an interactive HTML calculator for ")}
              >
                <Layout size={12} />
                <span>HTML Calculator</span>
              </button>
            </div>

            <button
              className="btn-send"
              type="button"
              aria-label="Send message"
              onClick={handleSubmit}
              disabled={!inputText.trim() || isLoading}
            >
              <Send size={16} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
