import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { SessionSidebar } from './components/SessionSidebar';
import { ChatPane } from './components/ChatPane';
import { ArtifactViewer } from './components/ArtifactViewer';

export function App() {
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [activeArtifact, setActiveArtifact] = useState(null);
  const [isArtifactExpanded, setIsArtifactExpanded] = useState(false);
  const [selectedModel, setSelectedModel] = useState('ollama');
  const [modelStatus, setModelStatus] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [isLoading, setIsLoading] = useState(false);

  // 1. Fetch Models Status
  const loadModelStatus = async () => {
    try {
      const res = await fetch('/api/models/status');
      if (res.ok) {
        const data = await res.json();
        setModelStatus(data);
      }
    } catch (err) {
      console.warn("Could not reach model status API:", err);
    }
  };

  // 2. Fetch Sessions List
  const loadSessions = async () => {
    try {
      const res = await fetch('/api/sessions');
      if (res.ok) {
        const data = await res.json();
        setSessions(data);
        if (data.length > 0 && !activeSessionId) {
          // Select first session or keep current
        }
      }
    } catch (err) {
      console.warn("Could not reach sessions API:", err);
    }
  };

  // 3. Fetch Messages for Active Session
  const loadSessionMessages = async (sessionId) => {
    if (!sessionId) return;
    try {
      const res = await fetch(`/api/sessions/${sessionId}`);
      if (res.ok) {
        const data = await res.json();
        setMessages(data.messages || []);
        // If the last message produced an artifact, preview it
        const lastMsgWithArtifact = [...(data.messages || [])]
          .reverse()
          .find((m) => m.artifacts && m.artifacts.length > 0);
        if (lastMsgWithArtifact) {
          setActiveArtifact(lastMsgWithArtifact.artifacts[0]);
        }
      }
    } catch (err) {
      console.error("Failed to load session messages:", err);
    }
  };

  useEffect(() => {
    loadModelStatus();
    loadSessions();
  }, []);

  useEffect(() => {
    if (activeSessionId) {
      loadSessionMessages(activeSessionId);
    } else {
      setMessages([]);
      setActiveArtifact(null);
    }
  }, [activeSessionId]);

  // Handle New Session
  const handleNewChat = () => {
    setActiveSessionId(null);
    setMessages([]);
    setActiveArtifact(null);
  };

  // Handle Delete Session
  const handleDeleteSession = async (sessionId) => {
    try {
      await fetch(`/api/sessions/${sessionId}`, { method: 'DELETE' });
      setSessions((prev) => prev.filter((s) => s.id !== sessionId));
      if (activeSessionId === sessionId) {
        handleNewChat();
      }
    } catch (err) {
      console.error("Failed to delete session:", err);
    }
  };

  // Handle Sending Message
  const handleSendMessage = async (text, forceSkill = null) => {
    setIsLoading(true);

    // Optimistically add user message to list
    const tempUserMsg = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: text,
      created_at: new Date().toISOString()
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          session_id: activeSessionId,
          model_provider: selectedModel,
          force_skill: forceSkill
        })
      });

      if (res.ok) {
        const data = await res.json();
        setActiveSessionId(data.session_id);

        const newAssistantMsg = {
          id: `asst-${Date.now()}`,
          role: 'assistant',
          content: data.message,
          citations: data.citations || [],
          artifacts: data.artifact ? [data.artifact] : [],
          created_at: data.created_at || new Date().toISOString()
        };

        setMessages((prev) => [...prev, newAssistantMsg]);

        if (data.artifact) {
          setActiveArtifact(data.artifact);
        }

        // Refresh sessions list in background
        loadSessions();
      } else {
        const errData = await res.json();
        alert(`Request error: ${errData.detail || 'Could not complete query'}`);
      }
    } catch (err) {
      console.error("Chat error:", err);
      alert("Failed to communicate with Lenny Assistant backend.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar
        selectedModel={selectedModel}
        onModelChange={setSelectedModel}
        modelStatus={modelStatus}
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
        onNewChat={handleNewChat}
      />

      <div className="app-container">
        <SessionSidebar
          sessions={sessions}
          activeSessionId={activeSessionId}
          onSelectSession={setActiveSessionId}
          onNewChat={handleNewChat}
          onDeleteSession={handleDeleteSession}
          isOpen={sidebarOpen}
        />

        <ChatPane
          messages={messages}
          isLoading={isLoading}
          onSendMessage={handleSendMessage}
          onOpenArtifact={setActiveArtifact}
          onPromptClick={(text, skill) => handleSendMessage(text, skill)}
        />

        {activeArtifact && (
          <ArtifactViewer
            artifact={activeArtifact}
            onClose={() => setActiveArtifact(null)}
            isExpanded={isArtifactExpanded}
            onToggleExpand={() => setIsArtifactExpanded(!isArtifactExpanded)}
          />
        )}
      </div>
    </div>
  );
}

export default App;
