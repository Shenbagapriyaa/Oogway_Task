# UI/UX Design Specification: The Lenny Growth Assistant
**Forward Deployed Engineering Design Document**
**Version:** 1.0.0

---

## 1. UI/UX Principles & Aesthetic Philosophy

The Lenny Growth Assistant is designed to feel like a high-end, native enterprise productivity tool—combining the clean focus of modern AI workbenches (like Claude 3.5 Artifacts and Linear) with the tactical editorial quality of Lenny’s Newsletter.

### Core Principles
1. **Rich Aesthetics & First-Impression Polish:** 
   * Sleek dark mode by default with curated slate-charcoal tones (`#0B0F19`, `#111827`, `#1F2937`) and subtle gradient borders (`#6366F1` indigo to `#EC4899` pink accents).
   * Refined glassmorphism on floating toolbars and citation badges (`backdrop-filter: blur(12px)` with subtle rgba white border strokes).
   * Clean, modern typography using Google Font **Inter** and **Outfit** for headlines, ensuring maximum legibility.
2. **Context Continuity via Split-Screen Architecture:**
   * Chat conversation on the left, rendered artifacts on the right.
   * Users never lose their place in the dialogue when reading or testing a generated PRD, Ship 30 essay, or interactive calculator.
3. **Transparent Grounding:**
   * Citations are prominent, interactive interactive pill cards displaying speaker name, episode, and timestamp.
   * Clicking a citation opens an inspection modal with the exact transcript quote snippet.
4. **Instant Actionability:**
   * One-click action prompts for frequent PM/Growth workflows: *"Write Ship 30 Essay"*, *"Build Interactive Growth Calculator"*, *"Synthesize PLG Playbook"*, *"Compare Operator Tactics"*.

---

## 2. Information Architecture & Layout Structure

```
+---------------------------------------------------------------------------------------------------+
|  [Logo] Lenny Growth Assistant   | Provider: [Ollama (Local) v] (● Ready)  |  [+ New Session]     |
+--------------------------+---------------------------------------+--------------------------------+
|  SESSIONS SIDEBAR        |  CENTRAL CHAT STREAM                  |  CLAUDE ARTIFACT VIEWER        |
|  - Growth Loops Q3       |                                       |  [Preview] [Code] [Copy] [X]   |
|  - Elena Verna AI PMF    |  [User Message]                       |  ----------------------------  |
|  - Keith Rabois Hiring   |  "What is Elena Verna's thesis on     |                                |
|  - Viral Loops Model     |   recapturing PMF every 3 months?"    |  # The 90-Day PMF Treadmill:   |
|                          |                                       |  Why AI Startups Must Die and  |
|  [Filter / Search]       |  [Lenny Assistant]                    |  Be Reborn Every Quarter       |
|  ----------------------  |  Detailed answer citing Elena...      |                                |
|  [Transcripts Indexed]   |                                       |  By Elena Verna & Lenny        |
|  50 Episodes Loaded      |  [Citations]                          |                                |
|                          |  [Elena Verna 4.0 (00:03:15)]         |  ... rendered Markdown or      |
|                          |                                       |  live interactive HTML/CSS     |
|                          |  [Actions: ✨ Generate Ship 30 Essay]  |  calculator ...                |
+--------------------------+---------------------------------------+--------------------------------+
|                          |  [Input: Ask a product or growth question...     ] [Model Toggle] [Send]|
+--------------------------+------------------------------------------------------------------------+
```

---

## 3. Key Interaction States

### 3.1 Initial / Empty State
* Welcome greeting introducing Lenny’s knowledge base with 50 loaded founder/operator transcripts.
* Prominent quick-start prompt chips:
  * *"Elena Verna: Why AI companies must recapture PMF every 3 months"*
  * *"Keith Rabois: Why you should hire Barrels instead of Ammo"*
  * *"Brian Halligan: How HubSpot pivoted to inbound product loops"*
  * *"Create an interactive HTML Viral Coefficient Calculator"*
* Status indicator showing the current model engine (Local Ollama, Cloud, or Fallback).

### 3.2 Streaming & Processing State
* Progressive streaming indicator with pulse animation.
* Retrieval status step-pills indicating:
  1. `Searching 50 transcripts...`
  2. `Matching operator quotes...`
  3. `Synthesizing grounded answer...`

### 3.3 Artifact Generation & Inspection State
* When an artifact is detected or requested:
  * Central chat automatically transitions from full-width to 50/50 split-screen.
  * Right-hand pane loads the **Claude-Style Artifact Viewer**.
  * Header controls:
    * **Preview Mode:** Live sandboxed rendering (Markdown or HTML/CSS).
    * **Code Mode:** Syntax-highlighted raw markdown/HTML with line numbers.
    * **Copy Button:** Instant clipboard copy with animated success checkmark.
    * **Full-Screen / Popout Toggle:** Allows expanding the artifact to 100% width for detailed reading or testing interactive tools.
    * **Close Button:** Returns chat to full-width view.

### 3.4 Error & Offline Resilience State
* If local Ollama is offline or uninstalled:
  * Non-blocking amber banner notifies the user: *"Local Ollama is offline at localhost:11434. The assistant has seamlessly switched to the Grounded Fallback Engine. Run `ollama run llama3.2` to enable local LLM."*
  * User can switch providers with one click in the navbar.
* If query does not match any transcripts:
  * Honest, grounded response acknowledging the corpus boundary: *"The available Lenny Podcast transcripts do not contain specific insights on this topic. Try asking about B2B growth loops, PMF, hiring, or product roadmaps."*

---

## 4. Color Palette & Design Tokens

```css
:root {
  /* Surface colors (Dark Theme) */
  --bg-primary: #0b0f19;
  --bg-secondary: #111827;
  --bg-tertiary: #1f2937;
  --bg-card: rgba(31, 41, 55, 0.7);
  --border-color: rgba(255, 255, 255, 0.08);
  --border-focus: #6366f1;

  /* Typography */
  --text-primary: #f9fafb;
  --text-secondary: #9ca3af;
  --text-muted: #6b7280;

  /* Brand Accents */
  --accent-primary: #6366f1;       /* Indigo */
  --accent-primary-hover: #4f46e5;
  --accent-secondary: #ec4899;     /* Fuchsia / Pink */
  --accent-gradient: linear-gradient(135deg, #6366f1 0%, #ec4899 100%);
  --success: #10b981;              /* Emerald */
  --warning: #f59e0b;              /* Amber */
  --danger: #ef4444;               /* Rose */

  /* Shadows & Glass */
  --shadow-card: 0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.5);
  --glass-backdrop: blur(16px);
}
```

---

## 5. Responsive Behavior

* **Desktop ($\ge 1200\text{px}$):** 
  * Full 3-column layout: Sessions Sidebar (260px) + Chat Stream (Flexible) + Artifact Viewer (550px - 750px).
* **Laptop / Tablet ($768\text{px} - 1199\text{px}$):**
  * Collapsible sidebar. Chat and Artifact viewer share screen with an interactive split slider or tabbed toggle.
* **Mobile ($< 768\text{px}$):**
  * Single view with bottom navigation bar. Floating drawer for sessions. When artifact opens, an animated modal sheet covers the screen with easy toggle back to chat.

---

## 6. Accessibility (a11y) Considerations

* **Keyboard Navigation:** Full support for `Tab` focusing on all inputs, citation pills, action buttons, and session links.
* **Screen Reader Accessibility:** Semantic HTML5 elements (`<header>`, `<nav>`, `<main>`, `<aside>`, `<article>`), ARIA labels on icon-only buttons (`aria-label="Copy artifact to clipboard"`).
* **Contrast Compliance:** WCAG AA compliance ($\ge 4.5:1$ contrast ratio) for all body text against dark backgrounds.
* **Sandboxed Security Notice:** Clear visual badge on the Artifact Viewer indicating whether the rendered code is sanitized Markdown or sandboxed HTML.
