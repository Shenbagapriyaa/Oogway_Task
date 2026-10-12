import React from 'react';
import { Sparkles, Cpu, Sidebar as SidebarIcon, Plus, Sun, Moon } from 'lucide-react';

export function Navbar({
  selectedModel,
  onModelChange,
  modelStatus,
  theme,
  onToggleTheme,
  onToggleSidebar,
  onNewChat
}) {
  const isOllamaReady = modelStatus?.ollama_status?.available;
  const isClaudeReady = modelStatus?.anthropic_status?.has_key;
  const isOpenAIReady = modelStatus?.openai_status?.has_key;

  let currentStatusClass = "ready";
  let statusTooltip = "Local Ollama ready";

  if (selectedModel === "ollama") {
    currentStatusClass = isOllamaReady ? "ready" : "offline";
    statusTooltip = isOllamaReady ? "Ollama daemon connected (localhost:11434)" : "Ollama offline (using Grounded Fallback)";
  } else if (selectedModel === "anthropic") {
    currentStatusClass = isClaudeReady ? "ready" : "offline";
    statusTooltip = isClaudeReady ? "Anthropic Claude API Key configured" : "No API key (using Grounded Fallback)";
  } else if (selectedModel === "openai") {
    currentStatusClass = isOpenAIReady ? "ready" : "offline";
    statusTooltip = isOpenAIReady ? "OpenAI API Key configured" : "No API key (using Grounded Fallback)";
  }

  return (
    <header className="navbar">
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <button 
          className="btn-icon" 
          type="button"
          aria-label="Toggle sessions sidebar"
          onClick={onToggleSidebar}
          title="Toggle Sessions Sidebar"
        >
          <SidebarIcon size={18} />
        </button>
        <div className="nav-brand">
          <div className="brand-icon">
            <Sparkles size={20} color="#fff" />
          </div>
          <div>
            <span className="brand-title">The Lenny Growth Assistant</span>
          </div>
          <span className="brand-badge">50 Transcripts</span>
        </div>
      </div>

      <div className="nav-controls">
        <div className="model-toggle-container" title={statusTooltip}>
          <Cpu size={14} color="#818cf8" />
          <span style={{ color: '#9ca3af', fontSize: '12px' }}>Engine:</span>
          <select 
            className="model-select"
            aria-label="Select language model provider"
            value={selectedModel}
            onChange={(e) => onModelChange(e.target.value)}
          >
            <option value="ollama">Ollama (Local Mandatory)</option>
            <option value="anthropic">Anthropic Claude (Cloud)</option>
            <option value="openai">OpenAI GPT-4o (Cloud)</option>
            <option value="grounded-fallback">Deterministic Fallback</option>
          </select>
          <span className={`status-indicator ${currentStatusClass}`} />
        </div>

        <button
          className="btn-icon theme-toggle"
          type="button"
          aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`}
          title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`}
          onClick={onToggleTheme}
        >
          {theme === 'dark' ? <Sun size={17} /> : <Moon size={17} />}
        </button>

        <button className="btn-new-chat" type="button" onClick={onNewChat} style={{ width: 'auto', padding: '7px 14px' }}>
          <Plus size={16} />
          <span>New Chat</span>
        </button>
      </div>
    </header>
  );
}
