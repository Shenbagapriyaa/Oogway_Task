# The Lenny Growth Assistant
> **Forward Deployed Engineer Engagement Submission**  
> AI-powered product and growth intelligence platform grounded in Lenny’s Podcast transcripts, featuring Claude-style native artifact rendering and a dedicated Ship 30 for 30 digital writing skill.

---

## 1. Executive Summary & Engagement Context

A product and growth organization required a grounded internal assistant to turn over 150+ hours of Lenny’s Podcast transcripts into reliable strategic counsel, reusable Ship 30 for 30 content, and native interactive artifacts—without requiring non-technical PMs to understand prompts or infrastructure.

**Key Technical & Product Highlights:**
* **Hybrid Grounded RAG:** Ingests 50 complete transcripts from Lenny's library with dialogue chunking, speaker parsing, and sub-50ms BM25 Okapi hybrid retrieval with exact citations and timestamps.
* **Ship 30 for 30 Content Skill:** Algorithmic prompt skill encoding Nicolas Cole & Dickie Bush’s digital writing architecture into ~1,250-word atomic essays with 1-3-1 cadence, 4 actionable pillars, selective bolding, and immediate takeaways.
* **Claude-Style Artifact Viewer:** Interactive side-by-side split screen rendering rich Markdown and complete HTML/CSS prototypes (e.g. viral growth calculators) directly beside the chat stream.
* **Strict Security Isolation:** Untrusted HTML artifacts are isolated inside a sandboxed `<iframe>` (`sandbox="allow-scripts"` strictly omitting `allow-same-origin`) with injected Content Security Policy headers to block cookie/token theft and host DOM manipulation.
* **Flexible LLM Layer:** Multi-provider architecture supporting **Local Ollama** (mandatory for local demo), **Anthropic Claude**, **OpenAI**, and an intelligent **Grounded Fallback Engine** for zero-friction evaluation.
* **Persistent Sessions:** PostgreSQL persistence (Supabase / Railway / Docker) with automatic, seamless fallback to persistent local SQLite.

---

## 2. Architecture Overview

```
+------------------------------------------------------------------------------------------------+
|                                    REACT + VITE FRONTEND                                       |
|  - Split-Screen Layout       - Claude-Style Artifact Viewer      - Provider Toggle & Badge     |
|  - Interactive Citations     - Session History Sidebar           - Dark Mode & Glassmorphism   |
+-----------------------------------------------+------------------------------------------------+
                                                | HTTP / REST (Vite Proxy :5173 -> :8000)
                                                v
+------------------------------------------------------------------------------------------------+
|                                    FASTAPI BACKEND GATEWAY                                     |
|  - Lifespan Ingestion Engine - Pydantic v2 Contracts             - Security Sanitization       |
|  - Session Persistence       - Structured Error Handling         - Health & Diagnostics API    |
+-----------------------------------------------+------------------------------------------------+
                                                |
               +--------------------------------+--------------------------------+
               |                                                                 |
               v                                                                 v
+-----------------------------+                                   +------------------------------+
|   HYBRID RETRIEVAL CORE     |                                   |     AGENT & LLM PROVIDER     |
|  - 50 Ingested Transcripts  |                                   |  - Local Ollama (llama3.2)   |
|  - Speaker Dialogue Parser  |                                   |  - Anthropic Claude 3.5      |
|  - BM25 Okapi + Entity Boost|                                   |  - OpenAI GPT-4o             |
|  - Verified Quote Citations |                                   |  - Grounded Fallback Engine  |
+-----------------------------+                                   +------------------------------+
               |                                                                 |
               +--------------------------------+--------------------------------+
                                                v
+------------------------------------------------------------------------------------------------+
|                                    PERSISTENCE & STORAGE                                       |
|  - PostgreSQL (Supabase / Railway / Docker Compose)                                            |
|  - Auto-Fallback to Persistent Local SQLite (data/lenny_assistant.db)                           |
+------------------------------------------------------------------------------------------------+
```

For complete database schema diagrams, component boundaries, and security models, see [`architecture.md`](file:///architecture.md).

---

## 3. Prerequisites

* **Python:** 3.10+ (Tested on Python 3.11 and Python 3.13)
* **Node.js:** v18+ (Tested on Node v20 and v24)
* **Local LLM (Mandatory for Demo):** [Ollama](https://ollama.ai/) installed with model `llama3.2` or `mistral`.
  *(Note: If Ollama is not installed or offline, the app automatically engages the Grounded Fallback Engine so all features remain testable without setup blockers).*
* **Optional:** Docker & Docker Compose (for containerized startup).

---

## 4. Quick Start (One-Command Startup)

### Option A: Direct Python Runner (Recommended for Local Dev)

Clone the repository and run the unified startup script:

```bash
# 1. Install Backend Dependencies
pip install -r backend/requirements.txt

# 2. Install Frontend Dependencies
cd frontend && npm install && cd ..

# 3. Launch both servers with one command
python run.py
```
*(On Windows, you can also double-click `run.bat`)*

**What this does:**
1. Verifies the 50 ingested transcripts in `backend/data/transcripts/`.
2. Starts the **FastAPI Backend** on `http://localhost:8000`.
3. Starts the **React Vite Frontend** on `http://localhost:5173`.
4. Automatically opens your default web browser to `http://localhost:5173`.

---

### Option B: Docker Compose (One Command)

```bash
docker compose up --build
```
* **Frontend:** `http://localhost:5173`
* **Backend API:** `http://localhost:8000`
* **API Docs:** `http://localhost:8000/docs`
* **PostgreSQL:** `localhost:5432`

---

## 5. Local & Cloud Model Configuration

Copy the example environment file:
```bash
cp .env.example .env
```

### 1. Local Ollama (Mandatory for Demo)
1. Download and run Ollama from [ollama.ai](https://ollama.ai).
2. Pull the lightweight model:
   ```bash
   ollama run llama3.2
   ```
3. Set in `.env`:
   ```ini
   DEFAULT_PROVIDER=ollama
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama3.2
   ```

### 2. Cloud Providers (Anthropic / OpenAI)
To enable Cloud LLMs, add your API keys to `.env`:
```ini
ANTHROPIC_API_KEY=sk-ant-api...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

OPENAI_API_KEY=sk-proj...
OPENAI_MODEL=gpt-4o
```
You can toggle between providers in real-time using the **Engine Selector** in the top navigation bar.

### 3. Graceful Fallback Behavior
If Ollama is unreachable at `localhost:11434` and no cloud keys are provided:
* The system logs a diagnostic notice and engages the **Deterministic Grounded Fallback Engine**.
* Queries, grounded citations, Ship 30 for 30 essays, and interactive HTML artifacts continue functioning seamlessly.

---

## 6. Running Automated Tests

A comprehensive 12-test automated suite validates the API, database persistence, BM25 retrieval, Ship 30 for 30 skill, and security sandboxing.

Run the test suite with:
```bash
python -m pytest backend/tests -v
```

### Test Coverage Summary:
- [x] `test_health_endpoint`: Validates application status and indexed transcript count.
- [x] `test_models_status_endpoint`: Verifies live provider discovery.
- [x] `test_transcripts_endpoint`: Validates transcript metadata catalog.
- [x] `test_session_lifecycle`: Full CRUD test on sessions in persistent database.
- [x] `test_chat_grounded_response`: End-to-end conversation turn verifying citations.
- [x] `test_retrieval_elena_verna`: Grounded retrieval on Elena Verna (Lovable, PMF loops).
- [x] `test_retrieval_keith_rabois`: Grounded retrieval on Keith Rabois (Barrels vs. Ammo).
- [x] `test_out_of_domain_query`: Rejection and disclaimer handling for ungrounded queries.
- [x] `test_security_blocks_parent_escape`: Blocks iframe window breakout exploits.
- [x] `test_security_blocks_cookie_stealing`: Blocks untrusted script cookie/token access.
- [x] `test_security_injects_csp`: Verifies Content Security Policy header injection.
- [x] `test_ship30_essay_structure`: Verifies ~1,250 words, hook, 4 pillars, and selective bolding.

For manual UI verification steps, see [`manual_test_plan.md`](file:///manual_test_plan.md).

---

## 7. Deliverables & Documentation Index

| Deliverable | File | Description |
|---|---|---|
| **Product Brief & PRD** | [`PRD.md`](file:///PRD.md) | Discovery brief, JTBD, success metrics, scope decisions, and risk matrix. |
| **System Architecture** | [`architecture.md`](file:///architecture.md) | Database schema, API contracts, BM25 retrieval pipeline, and security model. |
| **UI/UX Design Spec** | [`design.md`](file:///design.md) | UI principles, dark mode tokens, split-screen architecture, and a11y. |
| **Agent Transcripts** | [`agent_transcripts/`](file:///agent_transcripts/) | Full agent execution trajectory, failed attempts, and technical corrections. |
| **Demo Video Guide** | [`demo_guide.md`](file:///demo_guide.md) | Word-for-word 2-3 minute demo video script with YouTube submission notes. |
| **Manual Test Plan** | [`manual_test_plan.md`](file:///manual_test_plan.md) | 12-step interactive verification checklist for evaluators. |

---

## 8. Troubleshooting & Operational FAQ

### Q: What if Ollama is not running on my machine?
**A:** The assistant detects when `localhost:11434` is offline, shows an amber indicator, and seamlessly activates the Grounded Fallback Engine. You can still test Q&A, citations, Ship 30 essays, and interactive artifacts without running Ollama. To start Ollama, install it from [ollama.ai](https://ollama.ai) and run `ollama run llama3.2`.

### Q: What database is used?
**A:** The backend defaults to persistent SQLite at `backend/data/lenny_assistant.db` for zero-friction setup. If you specify a PostgreSQL connection string in `DATABASE_URL` (e.g. Supabase, Railway, or local Docker), it automatically connects to PostgreSQL.

### Q: How is untrusted HTML isolated?
**A:** HTML artifacts are rendered inside an `<iframe>` with `sandbox="allow-scripts"` (strictly omitting `allow-same-origin`). This assigns the iframe an opaque null-origin, mathematically preventing it from accessing the host's cookies, localStorage, or parent DOM. In addition, an inline CSP (`default-src 'none'`) restricts external network requests.

---

## 9. License & Attribution

Transcripts and interview content are property of [Lenny's Podcast / Newsletter](https://www.lennysnewsletter.com/). Built for the Forward Deployed Engineer technical engagement.
