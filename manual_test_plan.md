# Manual Test Plan: The Lenny Growth Assistant UI & Interactions
**Version:** 1.0.0  
**Evaluator Verification Checklist**

Use this checklist to verify the browser experience after starting the app. The browser scenarios have not been run as part of the current automated test pass; mark each row only after checking it interactively.

---

## Test Suite Matrix

Before submission, also verify the Compose PostgreSQL path at `/api/health` and exercise prompts, sessions, citations, and artifact controls using only the keyboard at a narrow mobile viewport. These checks have not yet been run.

| # | Test Scenario | Steps to Execute | Expected Result | Status |
|---|---|---|---|---|
| **1** | **One-Command Boot** | Run `python run.py` from repository root. | Backend starts on `:8000`, frontend starts on `:5173`, and the browser opens. | [ ] Not run |
| **2** | **Transcripts & Knowledge Base** | Check the transcript count in the sidebar. | UI reports 50 podcast transcript files. | [ ] Not run |
| **3** | **Grounded Question & Citations** | Ask about Elena Verna and product-market fit. | Response includes matching source cards and a timestamp; inspect the excerpt before treating claims as grounded. | [ ] Not run |
| **4** | **Citation Excerpt Inspection** | Open a citation card. | The episode and retrieved excerpt are visible. | [ ] Not run |
| **5** | **Ship 30 for 30 Content Skill** | Select the Ship 30 prompt and run with an available model. | Model-backed answer follows the writing prompt and appears as a Markdown artifact. Without a model, the app labels its output as a short source brief. | [ ] Not run |
| **6** | **Artifact Viewer** | Generate a Markdown artifact; inspect Preview, Code, Copy, expand, and close controls. | Rendered Markdown is sanitized; controls operate without losing the chat. | [ ] Not run |
| **7** | **Interactive HTML/CSS Artifact** | Ask for an interactive HTML calculator while a model is available. | HTML renders in the sandboxed iframe and its controls respond. Offline mode shows only the generic built-in example. | [ ] Not run |
| **8** | **Security Sandbox Verification** | Inspect the preview iframe in browser DevTools. | `sandbox="allow-scripts"` is present without `allow-same-origin`; verify CSP restrictions in the preview. | [ ] Not run |
| **9** | **Model Engine Switcher** | Switch between Ollama, configured cloud provider, and fallback. | The selected provider is reflected in chat results; unavailable providers fall back. | [ ] Not run |
| **10** | **Session Persistence** | Send a message, refresh, and reopen the session. | Messages and generated artifacts reload from SQLite or PostgreSQL; follow-up questions use recent history. | [ ] Not run |
| **11** | **New Session Lifecycle** | Start a new chat and then return to the prior session. | The new chat is separate; the previous session remains available in the sidebar. | [ ] Not run |
| **12** | **Out-of-Domain Disclaimer** | Ask a question unrelated to the transcript corpus. | Fallback acknowledges that no relevant excerpt was found rather than inventing transcript claims. | [ ] Not run |
