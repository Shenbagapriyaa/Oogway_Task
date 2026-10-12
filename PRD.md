# Product Requirements Document (PRD)
## The Lenny Growth Assistant
**Forward Deployed Engineering Engagement**
**Version:** 1.0.0  
**Author:** Forward Deployed Engineer  
**Status:** Prototype implemented; see known gaps below

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
These are proposed acceptance targets, not measured outcomes. No user study or latency benchmark has been run for this prototype.
1. **Product Adoption & Task Completion Rate:** $\ge 85\%$ of user queries result in either a cited answer or a generated native artifact without follow-up re-prompts.
2. **Grounding & Citation Accuracy:** $100\%$ of substantive strategic claims are backed by an episode citation (Guest Name, Episode Title, Timestamp range, and direct transcript excerpt).
3. **Artifact Generation Speed & Quality:** Time-to-artifact $< 4$ seconds on Cloud LLMs and $< 12$ seconds on local Ollama, with $0\%$ unsandboxed script execution vulnerabilities.
4. **Evaluator Deployment Success (Operational Metric):** A new engineer or evaluator can launch the complete full-stack system from a clean clone in $< 2$ minutes using a single command.

### 1.3 Key Assumptions (Addressing Brief Ambiguities)
1. **Model Availability:** The local demo should run with Ollama; cloud options are available when credentials are configured. The deterministic fallback is intended for setup and source-inspection workflows, not as a substitute for generated analysis.
2. **Database Environment:** A lightweight local run should not require a database server, so it defaults to SQLite. Docker Compose provides PostgreSQL for exercising that deployment path. A failed PostgreSQL connection falls back to SQLite at backend startup.
3. **Knowledge Base Scope:** The submitted snapshot includes 50 local transcript Markdown files. It is a fixed corpus snapshot, not a live mirror of the full Lenny’s library.
4. **Artifact Scope:** The application can return Markdown and HTML artifacts. Markdown can be requested directly; when no model is available, the fallback creates only a source brief. The built-in offline HTML calculator is a generic example, not a transcript-derived recommendation.

### 1.4 Scope Choices
* **In Scope (Included):**
  * Full-stack conversational assistant with session management and persistence.
  * Local BM25 lexical retrieval across 50 transcript files, with recent session turns used to clarify follow-up searches.
  * Rigorous source grounding with guest name, episode title, timestamp, and source quotes.
  * Dedicated **Ship 30 for 30 writing prompt** for model-backed essays. Offline mode returns a cited source brief rather than inventing enough material to meet the requested length.
  * In-app Claude-style **Artifact Viewer** rendering Markdown and sandboxed HTML/CSS in a side-by-side responsive split view.
  * Sandboxed HTML preview and DOMPurify-sanitized Markdown rendering. These reduce risk but are not a substitute for a security review.
  * Multi-provider toggle: Ollama (local), Anthropic Claude, OpenAI, and Local Fallback.
  * Backend tests for API contracts, database persistence, retrieval, provider routing, essay fallback, and selected artifact-security behavior.
  * One-command startup script (`run.py` and `docker-compose.yml`).
* **Out of Scope (Intentionally Excluded & Why):**
  * *Audio playback of original podcast files:* Increases repository size by gigabytes without adding strategic value over accurate timestamps and text excerpts.
  * *User authentication (Auth0/OAuth):* Adds setup friction for evaluators; local session UUIDs provide full session isolation without credential barriers.
  * *Fine-tuning custom model weights:* Retrieval is simpler to inspect and update for this prototype. It does not eliminate hallucinations, so citations still need to be checked.

### 1.5 Risks and Trade-offs
| Risk Area | Severity | Mitigation Strategy |
| :--- | :--- | :--- |
| **Hallucination** | High | Strict RAG prompt boundaries: Model is instructed to cite only retrieved excerpts and explicitly declare when the corpus does not contain the answer. |
| **Local Model Latency & Memory** | Medium | Configurable model choices in Ollama (`llama3.2`, `mistral`, `qwen2.5:1.5b`). If Ollama is slow or down, fallback displays a clear notification banner with diagnostic guidance. |
| **Unsafe Artifact Rendering** | High | Sandboxed HTML preview inside an isolated `<iframe>` (`sandbox="allow-scripts"` without `allow-same-origin`), stripping external script injections and dangerous protocol handlers. |
| **PostgreSQL Connection Failures** | Medium | Dual-engine database adapter: tests connection on boot; auto-switches to SQLite with persistent storage if PostgreSQL credentials are unset or invalid. |
| **Cloud API Costs & Rate Limits** | Medium | Local Ollama is the default. Cloud requests are optional; the Anthropic SDK call is bounded by a timeout. No retrieval-embedding cache is used. |

### 1.6 Implementation Gaps
* Retrieval is BM25 keyword search; semantic/vector retrieval is not implemented.
* The data model supports optional session metadata and the UI identifies its client as `web`; there is no user authentication or identity verification.
* Prompt instructions and citations improve traceability but do not guarantee that model-generated claims are fully supported. Users should inspect source excerpts.
* The deterministic fallback returns source material and brief artifacts. Full-length essays and custom HTML require a configured language model.
* PostgreSQL is provided through Docker Compose. A dedicated production deployment has not been configured or tested.

---

## 2. User Flows & Requirements

### 2.1 Core User Journey
1. **Session Initialization:** User opens the empty chat, starts a new chat, or selects a saved session. A chat session is persisted on its first message.
2. **Model Selection:** Top navigation displays current active LLM (e.g. Local Ollama `llama3.2` or Cloud Claude `claude-3-5-sonnet`). User can toggle provider anytime.
3. **Grounded Query:** User asks a product question. The service retrieves chunks using BM25 and includes recent user questions in the query to help resolve follow-ups.
4. **Citation Inspection:** Response answers the query and displays clickable Citation Cards showing the exact episode, guest, timestamp, and transcript quote.
5. **Ship 30 for 30 Skill Trigger:** User clicks the Ship 30 prompt or requests an essay. With a configured model, the writing prompt requests an approximately 1,250-word structured essay; without one, the fallback returns a clearly labeled source brief.
6. **Artifact Native Viewing:** Artifact opens in the side-by-side Artifact Viewer. User can toggle between rendered visual preview, raw code inspector, copy to clipboard, or download.
7. **HTML/CSS Interactive Artifacts:** User can request an HTML artifact, which is rendered in the sandbox. Without a configured model, only the generic example calculator is available.

---

## 3. Acceptance Criteria
- [x] FastAPI backend and React frontend, with direct and Docker Compose startup paths.
- [x] Session/message/artifact/citation persistence using local SQLite or Compose PostgreSQL; optional metadata is stored per session.
- [x] Provider selection for Ollama, Anthropic Agent SDK, OpenAI, and excerpt-based fallback.
- [x] Recent session turns are passed to providers and recent user turns are included in retrieval queries.
- [x] Citations contain guest, episode, chunk-start timestamp, and an excerpt.
- [x] Model-backed Ship 30 prompt and Markdown/HTML artifact paths; fallback behavior is intentionally limited and labeled.
- [x] HTML iframe sandbox and Markdown sanitization; security still requires review before production use.
- [x] Backend automated tests pass locally. Manual UI scenarios and production PostgreSQL operation have not been independently verified.

Semantic retrieval, authenticated user identity, cloud production deployment, and a recorded demo remain outside the implemented prototype.
