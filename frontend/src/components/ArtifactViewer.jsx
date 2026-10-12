import React, { useState } from 'react';
import { Eye, Code, Copy, Check, Maximize2, Minimize2, X, ShieldCheck } from 'lucide-react';
import { renderMarkdown } from '../utils/renderMarkdown';
import confetti from 'canvas-confetti';

export function ArtifactViewer({
  artifact,
  onClose,
  isExpanded,
  onToggleExpand
}) {
  const [viewMode, setViewMode] = useState('preview'); // 'preview' | 'code'
  const [copied, setCopied] = useState(false);

  if (!artifact) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(artifact.content);
    setCopied(true);
    confetti({ particleCount: 30, spread: 60, origin: { y: 0.8 } });
    setTimeout(() => setCopied(false), 2000);
  };

  const isHtml = artifact.type === 'html';
  const renderedMarkdown = !isHtml ? renderMarkdown(artifact.content) : '';

  return (
    <div className={`artifact-pane ${isExpanded ? 'expanded' : ''}`}>
      {/* Artifact Viewer Header */}
      <div className="artifact-header">
        <div className="artifact-header-left">
          <span className="artifact-tag">
            {isHtml ? 'HTML / CSS' : 'Ship 30 Essay'}
          </span>
          <h3 className="artifact-title-heading" title={artifact.title}>
            {artifact.title}
          </h3>
        </div>

        <div className="artifact-controls">
          <div className="tab-toggle">
            <button
              className={`tab-btn ${viewMode === 'preview' ? 'active' : ''}`}
              onClick={() => setViewMode('preview')}
            >
              <Eye size={13} style={{ marginRight: 4, verticalAlign: -2 }} />
              Preview
            </button>
            <button
              className={`tab-btn ${viewMode === 'code' ? 'active' : ''}`}
              onClick={() => setViewMode('code')}
            >
              <Code size={13} style={{ marginRight: 4, verticalAlign: -2 }} />
              Code
            </button>
          </div>

          <button
            className="btn-icon"
              type="button"
              aria-label="Copy artifact content"
            onClick={handleCopy}
            title="Copy artifact content to clipboard"
          >
            {copied ? <Check size={16} color="#10b981" /> : <Copy size={16} />}
          </button>

          <button
            className="btn-icon"
            type="button"
            aria-label={isExpanded ? 'Collapse artifact viewer' : 'Expand artifact viewer'}
            onClick={onToggleExpand}
            title={isExpanded ? 'Collapse width' : 'Expand full width'}
          >
            {isExpanded ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
          </button>

          <button
            className="btn-icon"
            type="button"
            aria-label="Close artifact viewer"
            onClick={onClose}
            title="Close artifact viewer"
          >
            <X size={16} />
          </button>
        </div>
      </div>

      {/* Security Isolation Notice */}
      <div style={{
        padding: '6px 16px',
        backgroundColor: 'rgba(16, 185, 129, 0.08)',
        borderBottom: '1px solid rgba(16, 185, 129, 0.2)',
        fontSize: '11px',
        color: '#6ee7b7',
        display: 'flex',
        alignItems: 'center',
        gap: '6px'
      }}>
        <ShieldCheck size={13} color="#10b981" />
        <span>
          {isHtml 
            ? "Sandboxed Iframe Isolation: Script execution allowed; host origin & cookie access strictly blocked." 
            : "Markdown sanitized before rendering"}
        </span>
      </div>

      {/* Artifact Content Body */}
      <div className="artifact-body">
        {viewMode === 'preview' ? (
          isHtml ? (
            <div className="artifact-iframe-container">
              {/* 
                SECURITY ISOLATION:
                sandbox="allow-scripts" WITHOUT allow-same-origin
                Ensures untrusted HTML runs in an isolated null-origin
                Preventing cookie access, localStorage theft, or parent DOM tampering.
              */}
              <iframe
                title="Sandboxed Artifact Preview"
                className="artifact-iframe"
                sandbox="allow-scripts"
                srcDoc={artifact.content}
              />
            </div>
          ) : (
            <div 
              className="artifact-markdown-view"
              dangerouslySetInnerHTML={{ __html: renderedMarkdown }}
            />
          )
        ) : (
          <pre className="artifact-code-view">
            <code>{artifact.content}</code>
          </pre>
        )}
      </div>
    </div>
  );
}
