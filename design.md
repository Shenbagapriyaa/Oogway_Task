# UI/UX Design Notes: The Lenny Growth Assistant
**Forward Deployed Engineering Design Document**
**Version:** 1.0.0

This document describes the current prototype, including known interaction and accessibility limits. It is not a list of unimplemented design targets.

---

## 1. UI/UX Principles & Aesthetic Philosophy

The Lenny Growth Assistant is designed to feel like a high-end, native enterprise productivity tool—combining the clean focus of modern AI workbenches (like Claude 3.5 Artifacts and Linear) with the tactical editorial quality of Lenny’s Newsletter.

### Core Principles
0. **Theme Choice:** Dark mode remains the default; the navbar Sun/Moon control switches between dark and light palettes, and the choice is saved in browser local storage.
1. **Rich Aesthetics & First-Impression Polish:** 
   * Sleek dark mode by default with curated slate-charcoal tones (`#0B0F19`, `#111827`, `#1F2937`) and subtle gradient borders (`#6366F1` indigo to `#EC4899` pink accents).
   * Refined glassmorphism on floating toolbars and citation badges (`backdrop-filter: blur(12px)` with subtle rgba white border strokes).
   * Clean, modern typography using Google Font **Inter** and **Outfit** for headlines, ensuring maximum legibility.
2. **Context Continuity via Split-Screen Architecture:**
   * Chat conversation on the left, rendered artifacts on the right.
   * Users never lose their place in the dialogue when reading or testing a generated PRD, Ship 30 essay, or interactive calculator.
3. **Transparent Grounding:**
  * Citations are interactive buttons displaying speaker name and timestamp; selecting one opens a dialog with the episode and excerpt.
   * Clicking a citation opens an inspection modal with the exact transcript quote snippet.
4. **Instant Actionability:**
  * One-click prompts currently cover an Elena Verna question, a Ship 30 essay, a generic HTML calculator, and a Keith Rabois question.

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

### 3.2 Processing State
* Requests are returned after generation completes; response-token streaming and retrieval progress steps are not implemented.
* While a request is running, the chat displays a single retrieval/generation status message.

### 3.3 Artifact Generation & Inspection State
* When an artifact is detected or requested:
  * Central chat automatically transitions from full-width to 50/50 split-screen.
  * Right-hand pane loads the **Claude-Style Artifact Viewer**.
  * Header controls:
    * **Preview Mode:** Live sandboxed rendering (Markdown or HTML/CSS).
    * **Code Mode:** Displays raw Markdown or HTML in a text block; syntax highlighting and line numbers are not implemented.
    * **Copy Button:** Copies artifact text and briefly shows a success icon.
    * **Expand Toggle:** Widens the artifact pane; it does not open a separate popout or full-screen route.
    * **Close Button:** Returns chat to full-width view.

### 3.4 Error & Offline Resilience State
* If a provider is offline or unconfigured, the navbar status dot indicates its availability and requests fall back to excerpt-only responses. There is no offline banner.
* Users can change the selected provider from the navbar.
* If no query excerpts qualify, fallback says it could not find relevant source material and does not generate strategic advice.

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
* **Tablet and Mobile (up to 760px):** The sessions sidebar overlays the chat when opened; an artifact fills the app area and can be closed to return. Quick prompts switch to a single column; there is no bottom navigation bar.
* **Wider screens:** Sessions, chat, and artifact panes share the available horizontal layout. The artifact pane can be widened.

---

## 6. Accessibility (a11y) Considerations

* **Keyboard Navigation:** Prompt cards, citation controls, session selection, provider selector, and artifact actions use native buttons/controls. A visible focus outline is provided. The citation dialog does not yet trap focus or restore focus on close.
* **Screen Reader Support:** Icon-only controls have accessible names and the citation excerpt uses dialog semantics. Contrast has not been measured against WCAG targets.
* **Artifact Notice:** The viewer labels Markdown as sanitized and HTML as sandboxed; HTML isolation still needs a production security review.
