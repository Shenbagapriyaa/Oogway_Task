# The Lenny Growth Assistant

This is a small full-stack assistant for searching Lenny’s Podcast transcripts and turning relevant excerpts into a chat response, a Ship 30 for 30-style essay, or an HTML artifact. It is built for the Forward Deployed Engineer take-home: the goal is to make the knowledge base easy to try, inspect, and run locally.

The repository includes a FastAPI backend, a React/Vite frontend, 50 transcript files, and a PostgreSQL service for Docker Compose. For a lightweight local run, the backend uses SQLite. Ollama is the intended local model; Anthropic and OpenAI can also be selected when API keys are configured.

## What works today

- Chat requests retrieve up to four transcript chunks and return citations with the guest, episode title, timestamp, and an excerpt.
- The Ship 30 skill provides a writing prompt for configured LLMs. If no model is available, fallback returns a short, cited source brief rather than claiming to produce a full-length essay.
- The artifact pane displays Markdown and HTML beside the conversation. HTML is rendered in an iframe with `sandbox="allow-scripts"` and no `allow-same-origin`.
- Sessions, optional user metadata, messages, citations, and artifacts are stored in the database. The session API supports creating, listing, reading, and deleting sessions.
- Recent conversation turns are included in provider prompts; recent user questions are also included in follow-up retrieval queries.
- The model selector offers Ollama, Anthropic, OpenAI, and the deterministic grounded fallback. If a selected model cannot be used, the backend falls back rather than returning a model response error.

There are a few important boundaries to be aware of when evaluating the project:

- Retrieval is lexical BM25 with a guest-name boost. It does not currently use embeddings or semantic/vector search.
- The application routes intents itself. Anthropic requests use Claude Agent SDK with built-in tools disabled; Ollama and OpenAI use their provider APIs directly.
- Local development defaults to SQLite. PostgreSQL is configured in Docker Compose, rather than being the local default.
- The deterministic fallback returns retrieved excerpts without adding advice. Its offline essay/document output is a short source brief; the built-in offline calculator is a generic example, not transcript-derived.
- Prompt constraints and citations improve traceability, but cannot guarantee every model-generated claim is supported. Check the cited transcript before relying on an answer.
- Transcript search is lexical BM25, not semantic or vector search.

These distinctions matter because several are narrower than the original assignment asks for. They are listed here so an evaluator can see what the implementation does without having to infer it from the code.

## Requirements

- Python 3.10 or newer
- Node.js 18 or newer and npm
- Ollama for model-backed local responses (optional for starting the app; the fallback can be used without it)
- Docker Desktop with Compose, if you prefer the containerized setup

## Run locally

From the repository root, install the Python and frontend dependencies. On Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements.txt
npm --prefix frontend install
Copy-Item .env.example backend/.env
```

The local backend process runs with `backend/` as its working directory, so its settings load `backend/.env`. The example defaults to Ollama and SQLite. If you do not want to use environment-file settings for local development, the same values can be set in your shell.

Install and start Ollama, then fetch the model configured in `backend/.env`:

```powershell
ollama pull llama3.2
```

Start the API and frontend together:

```powershell
python run.py
```

Open [http://localhost:5173](http://localhost:5173). The API docs are at [http://localhost:8000/docs](http://localhost:8000/docs), and the health endpoint is [http://localhost:8000/api/health](http://localhost:8000/api/health). Press `Ctrl+C` in the runner terminal to stop both processes.

On macOS or Linux, use `python3` and `source .venv/bin/activate` for the corresponding setup commands; the remaining commands are the same.

## Run with Docker Compose

From the repository root, copy the example file to `.env` so Compose can read optional cloud API keys, then start the services:

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Compose starts the frontend, FastAPI backend, PostgreSQL, and an Ollama container. The Ollama container does not download a model automatically. In a second terminal, pull the configured model once:

```powershell
docker compose exec ollama ollama pull llama3.2
```

The app is at [http://localhost:5173](http://localhost:5173), the API at [http://localhost:8000](http://localhost:8000), and PostgreSQL is exposed on port `5432`. The Compose file contains development database credentials; do not reuse them for a deployed or shared environment. Stop the stack with `Ctrl+C`, or run `docker compose down` in another terminal. `docker compose down -v` also deletes the database and model volumes.

## Models and configuration

The environment variables are listed in `.env.example`.

| Variable | Purpose |
|---|---|
| `DEFAULT_PROVIDER` | Default provider (`ollama`, `anthropic`, or `openai`) when a request does not choose one. |
| `OLLAMA_BASE_URL` | Ollama API address. Use `http://localhost:11434` for the direct local runner; Compose sets the service address for its backend. |
| `OLLAMA_MODEL` | Local model name, default `llama3.2`. Pull it with Ollama before selecting it. |
| `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL` | Optional Anthropic credentials and model. |
| `OPENAI_API_KEY`, `OPENAI_MODEL` | Optional OpenAI credentials and model. |
| `DATABASE_URL` | Optional PostgreSQL URL for direct backend runs. If unset, the app uses local SQLite. Compose supplies its own PostgreSQL URL. |

The selected provider is visible in the top navigation. Anthropic runs through Claude Agent SDK with built-in tools disabled; Ollama and OpenAI use their HTTP/API clients. A missing cloud key, unavailable Ollama instance, or provider call failure routes to the deterministic fallback. The fallback shows retrieved excerpts and makes no synthesized claims. Offline HTML uses a generic calculator example.

Do not commit `.env` files or put API keys in frontend code. For direct local runs, place settings in `backend/.env`; for Compose, place optional cloud keys in the root `.env`.

## Knowledge base and citations

Transcript Markdown files live in `backend/data/transcripts/`. At startup, the ingestion service reads frontmatter and timestamped speaker turns, combines turns into chunks of about 400 words with a one-turn overlap, and writes the result to `backend/data/index_cache.json`. The cache is loaded on later starts; remove it to force a rebuild. The current corpus contains 50 transcript files.

The retrieval service ranks chunks with BM25 and boosts guest-name matches. It returns up to four qualifying chunks. Citations include the guest, episode title, the chunk’s starting timestamp, and a short excerpt. The index is local JSON; it is not a hosted vector database, and there is no automatic remote transcript refresh.

## API overview

All API endpoints are served by FastAPI on port `8000`.

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/chat` | Send a message, optional session ID, provider, and optional skill trigger. |
| `GET` | `/api/sessions` | List saved sessions. |
| `POST` | `/api/sessions` | Create a session. |
| `GET` | `/api/sessions/{session_id}` | Read a session and its messages, citations, and artifacts. |
| `DELETE` | `/api/sessions/{session_id}` | Delete a session and its related records. |
| `GET` | `/api/models/status` | Check Ollama and configured cloud providers. |
| `GET` | `/api/transcripts` | List indexed episode metadata. |
| `GET` | `/api/health` | Return application, database type, database connection status, and index status. |

The interactive OpenAPI documentation is available at `/docs`. Chat input is validated as non-empty; application failures are logged and returned with a stable error code and message.

## Artifact safety

Generated HTML is inspected by the backend and rendered in an iframe with `sandbox="allow-scripts"`, without `allow-same-origin`. That keeps the preview on an opaque origin and separates it from the parent page’s DOM and storage. The HTML also receives a restrictive Content Security Policy intended to block network connections and other embedding. The sanitizer is a lightweight pattern-based filter, not a general HTML security sanitizer, so the iframe boundary is the primary isolation control.

Markdown is parsed with `marked` and sanitized with DOMPurify before it is inserted into chat or the artifact viewer. This blocks unsafe markup and attributes, but still warrants security review before production use.

## Tests

Run the backend tests from the repository root:

```powershell
python -m pytest backend/tests -v
```

There are 18 backend tests covering health and model status, session persistence and metadata, chat history and error responses, provider routing, retrieval, source-brief fallback, and selected HTML sandbox protections. The Agent SDK route test is mocked; it does not make a live Anthropic request. The tests use the configured database engine and do not replace a separate PostgreSQL integration test. The frontend has a production build check but no automated component test suite.

For a browser walkthrough, see [manual_test_plan.md](manual_test_plan.md). The browser checks are intentionally marked not run until someone performs them interactively.

## Project notes

- [PRD.md](PRD.md) describes the user, success measures, scope, assumptions, and risks.
- [architecture.md](architecture.md) documents the current components, data flow, persistence, and artifact isolation.
- [design.md](design.md) covers the interface and interaction design.
- [agent_transcripts/](agent_transcripts/) contains development-session notes.
- [demo_guide.md](demo_guide.md) is a suggested outline for the demo recording; the video itself still needs to be recorded and uploaded separately.

## Troubleshooting

**The UI opens, but replies say Ollama is unavailable.** Start Ollama and confirm the configured model is installed with `ollama list`. For Docker Compose, pull it in the `ollama` service as shown above. If the selected model cannot be reached, the app uses its deterministic fallback.

**The frontend cannot reach the API.** Check that both processes started and that ports `5173` and `8000` are available. The Vite development server proxies `/api` requests to the backend.

**A cloud provider uses the fallback instead.** Confirm the API key is in the correct environment file and restart the backend. Direct local runs read `backend/.env`; Docker Compose reads the root `.env` for cloud keys.

**The transcript index looks stale.** Stop the backend, remove `backend/data/index_cache.json`, then start it again to rebuild the cache from the Markdown files.

**The database is unavailable.** A direct local run normally uses SQLite. Compose starts PostgreSQL and waits for its health check before starting the backend. The application does not currently perform a database readiness check in `/api/health`.

## Attribution

Lenny’s Podcast transcripts and related interview content belong to their respective owners. This project is an internal-assistant prototype for the take-home assignment, not an official Lenny’s product.
