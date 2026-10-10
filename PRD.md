# Product Requirements Document (PRD)
## The Lenny Growth Assistant
**Forward Deployed Engineering Engagement**
**Version:** 1.0.0  
**Author:** Forward Deployed Engineer  
**Status:** Approved & Implemented  

---

## 1. Forward Deployment Brief

### 1.1 User and Problem Definition
* **Primary Persona:** Product Managers, Growth Leads, Founders, and Product Operations Specialists.
* **Core Job-to-be-Done (JTBD):** 
  > *"When I am formulating product strategy, growth loops, monetization models, or onboarding flows, I want to quickly extract proven, practitioner-tested advice from top tech operators (Lenny’s Podcast guests) and convert that knowledge into usable deliverables (Ship 30 for 30 essays, PRD templates, growth model calculators, and launch artifacts) without having to spend hours listening to transcripts or crafting complex prompts."*
* **Pain Points Removed:**
  1. **Knowledge Retrieval Friction:** Lenny’s library contains over 150+ hours of transcripts across hundreds of episodes. Finding specific advice (e.g., Elena Verna’s B2B PLG loops or Keith Rabois’s hiring formula) requires manual searching through text or audio.
  2. **Unverified Hallucinations:** Generic public LLMs hallucinate growth advice or mix up operator quotes. Users need verifiable, grounded citations with timestamps and guest attribution.
  3. **The "Blank Canvas" Format Gap:** PMs need structured artifacts (atomic essays, calculators, playbooks), not just chat replies. Translating chat answers into finished documents currently requires manual copy-pasting and reformatting.
  4. **Infrastructure Opacity:** Non-technical growth teams struggle with configuring local models, API keys, or Docker containers.

### 1.2 Measurable Success Metrics
1. **Product Adoption & Task Completion Rate:** $\ge 85\%$ of user queries result in either a cited answer or a generated native artifact without follow-up re-prompts.
2. **Grounding & Citation Accuracy:** $100\%$ of substantive strategic claims are backed by an episode citation (Guest Name, Episode Title, Timestamp range, and direct transcript excerpt).
3. **Artifact Generation Speed & Quality:** Time-to-artifact $< 4$ seconds on Cloud LLMs and $< 12$ seconds on local Ollama, with $0\%$ unsandboxed script execution vulnerabilities.
4. **Evaluator Deployment Success (Operational Metric):** A new engineer or evaluator can launch the complete full-stack system from a clean clone in $< 2$ minutes using a single command.

### 1.3 Key Assumptions (Addressing Brief Ambiguities)
1. **Model Availability:** Evaluators may run the tool on machines ranging from lightweight laptops (no local GPU/Ollama) to heavy developer workstations. *Decision:* Provide a triple-tier model layer: Local Ollama (mandatory for local demo), Cloud LLMs (Anthropic Claude & OpenAI), and an Intelligent Grounded Mock/Fallback engine that guarantees 100% functionality out of the box.
2. **Database Environment:** Many evaluators do not have a dedicated PostgreSQL server running locally. *Decision:* Default to PostgreSQL connection string (compatible with Supabase, Railway, or Docker), but automatically and seamlessly fall back to local persistent SQLite (`data/lenny_assistant.db`) if PostgreSQL is unavailable.
3. **Knowledge Base Scope:** Ingested 50 full, real transcripts from Lenny's official archive covering top tier operators (Elena Verna, Brian Halligan, Marc Andreessen, Keith Rabois, Tony Fadell, Eric Ries, etc.) with pre-indexed chunk metadata and speaker dialogue parsing.
4. **Artifact Scope:** Artifacts encompass both rich structured Markdown documents (Ship 30 for 30 essays, PM specs, framework summaries) and complete interactive HTML/CSS components (growth calculators, conversion funnels, interactive decision trees).

### 1.4 Scope Choices
* **In Scope (Included):**
  * Full-stack conversational assistant with session management and persistence.
  * Real-time semantic and lexical (BM25) hybrid retrieval across 50 complete Lenny podcast transcripts.
  * Rigorous source grounding with guest name, episode title, timestamp, and source quotes.
  * Dedicated **Ship 30 for 30 Content Skill** producing ~1,250-word atomic essays adhering to Cole & Bush’s framework (1-3-1 rhythm, bold emphasis, hook, tactical pillars).
  * In-app Claude-style **Artifact Viewer** rendering Markdown and sandboxed HTML/CSS in a side-by-side responsive split view.
  * Interactive security sandbox (`iframe` isolation without `allow-same-origin`) to prevent cross-site scripting or token theft.
  * Multi-provider toggle: Ollama (local), Anthropic Claude, OpenAI, and Local Fallback.
  * Comprehensive automated test suite and structured logging.
  * One-command startup script (`run.py` and `docker-compose.yml`).
* **Out of Scope (Intentionally Excluded & Why):**
  * *Audio playback of original podcast files:* Increases repository size by gigabytes without adding strategic value over accurate timestamps and text excerpts.
  * *User authentication (Auth0/OAuth):* Adds setup friction for evaluators; local session UUIDs provide full session isolation without credential barriers.
  * *Fine-tuning custom model weights:* RAG with accurate transcript chunking provides verifiable citations and zero hallucination risk, whereas fine-tuning is brittle and opaque.

### 1.5 Risks and Trade-offs
| Risk Area | Severity | Mitigation Strategy |
| :--- | :--- | :--- |
| **Hallucination** | High | Strict RAG prompt boundaries: Model is instructed to cite only retrieved excerpts and explicitly declare when the corpus does not contain the answer. |
| **Local Model Latency & Memory** | Medium | Configurable model choices in Ollama (`llama3.2`, `mistral`, `qwen2.5:1.5b`). If Ollama is slow or down, fallback displays a clear notification banner with diagnostic guidance. |
| **Unsafe Artifact Rendering** | High | Sandboxed HTML preview inside an isolated `<iframe>` (`sandbox="allow-scripts"` without `allow-same-origin`), stripping external script injections and dangerous protocol handlers. |
| **PostgreSQL Connection Failures** | Medium | Dual-engine database adapter: tests connection on boot; auto-switches to SQLite with persistent storage if PostgreSQL credentials are unset or invalid. |
| **Cloud API Costs & Rate Limits** | Low | Local caching of retrieval embeddings and chunk metadata; token-efficient context window management. |

---

## 2. User Flows & Requirements

### 2.1 Core User Journey
1. **Session Initialization:** User opens app; a new chat session is automatically initialized or selected from the sidebar history.
2. **Model Selection:** Top navigation displays current active LLM (e.g. Local Ollama `llama3.2` or Cloud Claude `claude-3-5-sonnet`). User can toggle provider anytime.
3. **Grounded Query:** User asks a product question (e.g. *"What did Elena Verna say about AI companies having to recapture product-market fit every 3 months?"*).
4. **Citation Inspection:** Response answers the query and displays clickable Citation Cards showing the exact episode, guest, timestamp, and transcript quote.
5. **Ship 30 for 30 Skill Trigger:** User clicks *"Generate Ship 30 Essay"* or types *"Write a Ship 30 for 30 essay on this"*. The assistant generates a ~1,250-word structured atomic essay.
6. **Artifact Native Viewing:** Artifact opens in the side-by-side Artifact Viewer. User can toggle between rendered visual preview, raw code inspector, copy to clipboard, or download.
7. **HTML/CSS Interactive Artifacts:** User can ask for an interactive growth calculator (e.g. *"Build an interactive viral coefficient calculator in HTML/CSS"*), which renders instantly and interactively in the sandbox.

---

## 3. Acceptance Criteria
- [x] Full-stack architecture running FastAPI backend and React frontend.
- [x] Multi-session persistence in PostgreSQL with SQLite fallback.
- [x] Model switching between Ollama, Claude, OpenAI, and Local Fallback without restarting the application.
- [x] Grounded citations on Lenny's Podcast transcripts with guest, episode, timestamp, and excerpt.
- [x] Dedicated Ship 30 for 30 skill implementing 1,250-word atomic essay architecture.
- [x] Claude-style Artifact Viewer rendering Markdown and sandboxed HTML/CSS side-by-side.
- [x] Untrusted HTML isolation via sandboxed iframe preventing origin leakage.
- [x] One-command startup script and full Docker Compose configuration.
- [x] Complete automated test suite covering API, persistence, retrieval, skill, and security.
