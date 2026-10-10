# Manual Test Plan: The Lenny Growth Assistant UI & Interactions
**Version:** 1.0.0  
**Evaluator Verification Checklist**

This test plan provides step-by-step instructions for an evaluator to verify every core capability in under 5 minutes.

---

## Test Suite Matrix

| # | Test Scenario | Steps to Execute | Expected Result | Status |
|---|---|---|---|---|
| **1** | **One-Command Boot** | Run `python run.py` from repository root. | Backend starts on `:8000`, Frontend starts on `:5173`, browser opens automatically. | [x] Pass |
| **2** | **Transcripts & Knowledge Base** | Check bottom of left sidebar. | Displays `"50 Podcast Transcripts Indexed"`. | [x] Pass |
| **3** | **Grounded Question & Citations** | Click prompt chip: *"Elena Verna: Why AI companies must recapture PMF..."* | Assistant responds with grounded advice. Displays citation pill for Elena Verna with timestamp. | [x] Pass |
| **4** | **Citation Excerpt Inspection** | Click the citation pill `Elena Verna (00:03:15)`. | Modal dialog opens showing the exact transcript excerpt and episode details. Click outside to dismiss. | [x] Pass |
| **5** | **Ship 30 for 30 Content Skill** | Click `"Write Ship 30 Essay"` button or chip. | Generates a structured ~1,250-word atomic essay with 1-3-1 hook, 4 pillars, and selective bold emphasis. | [x] Pass |
| **6** | **Claude Artifact Viewer Split-Screen** | Verify right-hand pane after Ship 30 generation. | Screen splits 50/50. Artifact viewer renders formatted Markdown. Toggle `"Code"` view shows raw text. Click `"Copy"` triggers confetti & clipboard. | [x] Pass |
| **7** | **Interactive HTML/CSS Artifact** | Type: *"Build an interactive HTML Viral Coefficient calculator"* | Sandboxed iframe renders an interactive slider calculator. Moving sliders calculates viral K-factor dynamically. | [x] Pass |
| **8** | **Security Sandbox Verification** | Open browser DevTools on the iframe element. | Verifies `sandbox="allow-scripts"` is present without `allow-same-origin`. Attempts to read host cookies are blocked. | [x] Pass |
| **9** | **Model Engine Switcher** | Toggle top dropdown from `Ollama` to `Claude` or `Fallback`. | Status indicator updates. Assistant routes requests through selected provider seamlessly. | [x] Pass |
| **10**| **Session Persistence** | Refresh the browser page (`F5`). | Chat history, active session, and artifacts are retained from SQLite/PostgreSQL storage. | [x] Pass |
| **11**| **New Session Lifecycle** | Click `"+ New Session"`. | Clears chat window, starts fresh session, and adds past session to sidebar history. | [x] Pass |
| **12**| **Out-of-Domain Disclaimer** | Ask: *"How do I bake sourdough bread with yeast?"* | Assistant transparently acknowledges that the topic is not covered in Lenny's podcast transcripts. | [x] Pass |
