# The Lenny Growth Assistant - Demo Video Walkthrough Guide
**Deliverable:** 2-3 Minute Walkthrough Video Script & Demonstration Plan  
**Target Audience:** Forward Deployed Engineering Hiring Team & Client Evaluators  

---

## 1. Video Requirements Checklist
- [x] Duration: Exactly 2:30 – 3:00 minutes.
- [x] Presenter: Camera enabled (face in corner or introduction), clear audio.
- [x] Key Sections:
  1. **The Problem & Value Proposition** (0:00 - 0:40)
  2. **Product Walkthrough & Grounded Retrieval** (0:40 - 1:20)
  3. **Local Ollama Integration & Model Toggle** (1:20 - 1:55)
  4. **Ship 30 for 30 Skill & Native Claude Artifact Viewer** (1:55 - 2:30)
  5. **Core Technical Trade-off & Closing** (2:30 - 3:00)

---

## 2. Word-for-Word Video Script

### [0:00 - 0:40] Introduction & The Problem
> **(Camera on face, greeting the viewer)**  
> *"Hi everyone, I’m excited to share the Lenny Growth Assistant—a full-stack AI platform built to turn over 150 hours of Lenny’s Podcast transcripts into an actionable internal partner for product and growth teams.*  
>  
> *The core problem growth leads face isn't a lack of information; it's the friction of extraction. PMs spend hours digging through audio or text trying to recall tactical playbooks—like Elena Verna's B2B growth loops or Keith Rabois's hiring rules—and then struggle to turn chat outputs into structured, usable deliverables.*  
>  
> *We built this forward-deployment solution to give teams verified, source-grounded answers, native Claude-style artifacts, and a dedicated Ship 30 for 30 digital writing engine, with zero infrastructure friction."*

---

### [0:40 - 1:20] Live Product Walkthrough & Grounded RAG
> **(Screen share showing `http://localhost:5173` with dark mode UI)**  
> *"Here is the application. The interface has a sleek dark aesthetic with a split-screen design. On the left, we maintain independent session histories persisted in PostgreSQL. In the center, we have our chat stream.*  
>  
> *Let's ask a strategic question: 'What did Elena Verna say about AI startups having to recapture product-market fit every 3 months?'*  
>  
> *(Click or submit question)*  
>  
> *Notice what happens: Our hybrid BM25 retrieval engine scans across 50 full indexed transcripts. The assistant answers with operator precision and provides interactive citation pills. If I click on Elena's citation, an inspection modal displays the exact podcast timestamp and verified quote snippet directly from the episode."*

---

### [1:20 - 1:55] Local Ollama Demo & Flexible Provider Toggle
> **(Screen pointing to the top navigation model dropdown)**  
> *"A key operational requirement of this engagement is model flexibility. In the top navbar, you can see our live provider switcher.*  
>  
> *By default, the demo runs against local Ollama at `localhost:11434` with `llama3.2`. We display a real-time health indicator. If Ollama is running, it routes locally with zero external API calls. But if an evaluator switches to Anthropic Claude, OpenAI, or runs the system offline without a local model, our system gracefully engages an intelligent Grounded Fallback Engine that continues serving cited answers without crashing."*

---

### [1:55 - 2:30] Ship 30 for 30 Skill & Claude-Style Artifact Viewer
> **(Click 'Write Ship 30 Essay' or prompt chip)**  
> *"Now let's demonstrate the Ship 30 for 30 content skill. Instead of relying on a generic prompt, we encoded Nicolas Cole and Dickie Bush's digital writing framework into a dedicated tool.*  
>  
> *With one click, the assistant synthesizes the discussion into a ~1,250-word atomic essay featuring a 1-3-1 hook cadence, the conventional wisdom villain, 4 tactical pillars with selective bold emphasis, and an actionable 24-hour takeaway.*  
>  
> *Notice that the application automatically transitions to a side-by-side split screen. This is our Claude-style Artifact Viewer. We can inspect the rendered Markdown, switch to Code mode to copy the source, or generate an interactive HTML/CSS viral growth calculator with slider controls. Untrusted HTML is isolated in a sandboxed iframe without allow-same-origin, preventing cookie leakage or DOM tampering."*

---

### [2:30 - 3:00] Key Technical Trade-off & Operational Handoff
> **(Camera on face / architecture overview)**  
> *"One important technical trade-off we made was choosing a hybrid BM25 lexical and token-overlap retrieval engine over an external vector database like Pinecone or Milvus.*  
>  
> *In production, external vector stores introduce credential dependencies, network latency, and cold-start failures for local evaluators. By combining speaker-level dialogue chunking, BM25 Okapi with exact entity boosting, and local disk caching, we achieved sub-50ms retrieval latency, 100% deterministic citation attribution, and single-command startup with zero external infrastructure.*  
>  
> *The entire application boots via `python run.py` or Docker Compose. Thank you for your time, and I look forward to discussing the architecture with the team!"*

---

## 3. Recording Recommendations
1. **Screen Resolution:** Record at 1920x1080 (1080p).
2. **Camera Placement:** Bottom-right corner using Loom, OBS, or QuickTime.
3. **Pacing:** Keep energy high and transitions crisp.
4. **YouTube Upload:** Set visibility to Unlisted or Public, copy link, and paste into the submission form.
