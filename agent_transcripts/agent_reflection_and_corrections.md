# Agent Reflections, Failed Attempts & Corrections
**Engagement:** The Lenny Growth Assistant  
**Role:** Forward Deployed Engineer  

---

## 1. Overview of Iteration & Corrections

During development, automated verification identified 3 technical issues across database lifecycle, BM25 scoring thresholding, and Pydantic deprecation warnings. Below is the candid post-mortem on each failure and how it was diagnosed and resolved.

---

## 2. Failure Case 1: FastAPI Lifespan & Missing SQLite Tables in Pytest

### The Problem:
During the initial execution of `python -m pytest backend/tests -v`, 3 tests failed with:
```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: sessions
```

### Root Cause Analysis:
In `backend/app/main.py`, database schema creation (`init_db()`) and transcript indexing (`retrieval_service.initialize()`) were registered inside the `@asynccontextmanager lifespan(app: FastAPI)` block.
When using `TestClient(app)` as a bare module-level instance, FastAPI does not trigger lifespan events unless entered with a context manager (`with TestClient(app) as client:`).

### The Fix:
1. Updated `backend/tests/test_api.py` to use a pytest fixture:
```python
@pytest.fixture(scope="module")
def client():
    init_db()
    retrieval_service.initialize()
    with TestClient(app) as test_client:
        yield test_client
```
2. Re-ran test: Database tables created immediately; session lifecycle test passed.

---

## 3. Failure Case 2: BM25 Out-of-Domain False Positives

### The Problem:
`test_retrieval.py::test_out_of_domain_query` failed:
```python
query = "How to bake sourdough bread with yeast and rye flour in a Dutch oven"
# Expected len(chunks) == 0, but got len(chunks) == 3
```

### Root Cause Analysis:
In the initial implementation of `BM25Retriever.search`, the relevance filter was set to `scores[idx] > 0.5` with any single token match (`matches_found[idx] >= 1`).
Across 50 long podcast transcripts (~1.5M words total), conversational side comments happened to mention incidental terms like "bread" or "dutch" (e.g. Dutch venture capital or bread-and-butter), which caused low-relevance false positive matches.

### The Fix:
The agent implemented a dual constraint in `retrieval_service.py`:
1. Raised the minimum score threshold from `0.5` to `3.5`.
2. Required multi-token matching:
```python
min_matches = max(2, int(len(query_tokens) * 0.35)) if len(query_tokens) >= 3 else 1
if scores[idx] >= 3.5 and matches_found[idx] >= min_matches:
    results.append((self.chunks[idx], scores[idx]))
```
3. Re-ran test: Out-of-domain queries correctly returned 0 chunks and triggered the knowledge boundary disclaimer.

---

## 4. Failure Case 3: Pydantic V2 & Python 3.13 Datetime Deprecations

### The Problem:
Pytest output 10 deprecation warnings:
1. `PydanticDeprecatedSince20: Support for class-based config is deprecated, use ConfigDict instead.`
2. `DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal.`

### The Fix:
1. Updated all Pydantic schemas in `backend/app/models/schemas.py` to use modern `model_config = ConfigDict(from_attributes=True)`.
2. Replaced `datetime.utcnow` with `lambda: datetime.now(timezone.utc)`.
3. Warnings resolved cleanly.

---

## 5. Forward Deployed Engineer Reflections

* **Client Empathy & Zero-Assumption Setup:** Evaluators have diverse environments. Writing a resilient architecture that falls back gracefully from Ollama to Cloud to Deterministic Fallback, and from Postgres to SQLite, is the difference between a project that runs seamlessly during an evaluation and one that fails on setup.
* **Security Discipline:** Untrusted LLM-generated HTML must never be injected raw. Using standard browser sandbox primitives (`<iframe sandbox="allow-scripts">` without `allow-same-origin`) provides mathematically sound origin isolation without relying purely on brittle regex filters.
