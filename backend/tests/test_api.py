import pytest
import asyncio
import claude_agent_sdk
from claude_agent_sdk import AssistantMessage, TextBlock
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db
from app.services.retrieval_service import retrieval_service
from app.services.llm_service import llm_service

@pytest.fixture(scope="module")
def client():
    # Explicitly ensure db and retrieval are initialized for tests
    init_db()
    retrieval_service.initialize()
    with TestClient(app) as test_client:
        yield test_client

def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database_status"] == "connected"
    assert "The Lenny Growth Assistant" in data["app_name"]
    assert data["transcripts_indexed"] > 0
    assert "ollama" in data["models_available"]

def test_models_status_endpoint(client):
    response = client.get("/api/models/status")
    assert response.status_code == 200
    data = response.json()
    assert "ollama_status" in data
    assert "anthropic_status" in data
    assert "openai_status" in data

def test_transcripts_endpoint(client):
    response = client.get("/api/transcripts")
    assert response.status_code == 200
    data = response.json()
    assert data["total_episodes"] > 0
    assert len(data["episodes"]) > 0

def test_session_lifecycle(client):
    # 1. Create Session
    create_res = client.post("/api/sessions", json={"title": "Test PMF Session", "model_provider": "ollama"})
    assert create_res.status_code == 200
    session_data = create_res.json()
    session_id = session_data["id"]
    assert session_data["title"] == "Test PMF Session"

    # 2. List Sessions
    list_res = client.get("/api/sessions")
    assert list_res.status_code == 200
    sessions = list_res.json()
    assert any(s["id"] == session_id for s in sessions)

    # 3. Get Session Detail
    detail_res = client.get(f"/api/sessions/{session_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["id"] == session_id
    assert isinstance(detail["messages"], list)

    # 4. Delete Session
    del_res = client.delete(f"/api/sessions/{session_id}")
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "deleted"


def test_session_user_metadata_round_trip(client):
    metadata = {"team": "growth", "workspace": "product"}
    create_res = client.post("/api/sessions", json={
        "title": "Metadata test",
        "user_metadata": metadata
    })
    assert create_res.status_code == 200
    session_id = create_res.json()["id"]
    assert create_res.json()["user_metadata"] == metadata

    detail_res = client.get(f"/api/sessions/{session_id}")
    assert detail_res.status_code == 200
    assert detail_res.json()["user_metadata"] == metadata

    client.delete(f"/api/sessions/{session_id}")

def test_chat_grounded_response(client):
    payload = {
        "message": "What did Elena Verna say about AI companies and product-market fit?",
        "model_provider": "grounded-fallback"
    }
    res = client.post("/api/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "session_id" in data
    assert len(data["citations"]) > 0
    assert any("Elena" in c["guest"] for c in data["citations"])
    assert len(data["message"]) > 0


def test_chat_passes_previous_turns_as_context(client, monkeypatch):
    captured = {}

    async def fake_generate_response(**kwargs):
        captured.update(kwargs)
        return "Follow-up response", "test-model", None

    monkeypatch.setattr(llm_service, "generate_response", fake_generate_response)
    first = client.post("/api/chat", json={"message": "Explain Elena Verna's PMF idea"})
    session_id = first.json()["session_id"]

    second = client.post("/api/chat", json={
        "message": "What did she recommend doing next?",
        "session_id": session_id
    })

    assert second.status_code == 200
    assert {"role": "user", "content": "Explain Elena Verna's PMF idea"} in captured["conversation_history"]
    assert {"role": "assistant", "content": "Follow-up response"} in captured["conversation_history"]


def test_self_introduction_does_not_search_transcripts(client, monkeypatch):
    def fail_search(*args, **kwargs):
        pytest.fail("A self-introduction should not trigger transcript retrieval")

    monkeypatch.setattr(retrieval_service, "search", fail_search)
    response = client.post("/api/chat", json={
        "message": "Hi, I'm Priya. This is the Lenny Growth Assistant, built to help product and growth teams find useful advice in podcast transcripts.",
        "model_provider": "grounded-fallback",
    })

    assert response.status_code == 200
    assert response.json()["citations"] == []
    assert response.json()["model_used"] == "conversation-guidance"
    assert "Hi Priya" in response.json()["message"]
    assert "what product or growth question" in response.json()["message"]


def test_new_out_of_domain_question_does_not_reuse_old_retrieval_topic(client):
    first = client.post("/api/chat", json={
        "message": "What did Elena Verna say about product-market fit?",
        "model_provider": "grounded-fallback",
    })
    session_id = first.json()["session_id"]

    second = client.post("/api/chat", json={
        "message": "How do I bake sourdough bread?",
        "session_id": session_id,
        "model_provider": "grounded-fallback",
    })

    assert second.status_code == 200
    assert second.json()["citations"] == []
    assert "couldn't find a relevant excerpt" in second.json()["message"]


def test_chat_failure_returns_structured_error(client, monkeypatch):
    async def fail_chat(db, request):
        raise RuntimeError("sensitive internal detail")

    monkeypatch.setattr("app.routers.chat.agent_service.process_chat", fail_chat)
    response = client.post("/api/chat", json={"message": "Trigger a failure"})

    assert response.status_code == 500
    assert response.json()["detail"] == {
        "code": "chat_execution_failed",
        "message": "The assistant could not complete this request."
    }
    assert "sensitive internal detail" not in response.text


def test_explicit_markdown_request_creates_artifact():
    from app.services.agent_service import agent_service

    assert agent_service.detect_intent("Create a Markdown PRD brief") == (False, False, True)


def test_offline_markdown_artifact_is_a_source_brief():
    chunk = {
        "guest": "Elena Verna",
        "title": "Elena Verna on growth",
        "timestamp": "00:03:15",
        "quote": "Product-market fit is no longer a milestone.",
    }
    message, provider, artifact = llm_service._generate_grounded_fallback(
        "Create a Markdown product brief", [chunk], False, False, True
    )

    assert provider == "grounded-fallback"
    assert "without adding unsupported recommendations" in message
    assert artifact["type"] == "markdown"
    assert "Product-market fit is no longer a milestone" in artifact["content"]


def test_offline_ship30_artifact_uses_source_brief():
    chunk = {
        "guest": "Elena Verna",
        "title": "Elena Verna on growth",
        "timestamp": "01:03:43",
        "quote": "Every three months, we have to recapture our product-market fit.",
    }
    message, provider, artifact = llm_service._generate_grounded_fallback(
        "Write a Ship 30 essay about product-market fit", [chunk], True, False
    )

    assert provider == "grounded-fallback"
    assert "short source-backed essay brief" in message
    assert artifact["type"] == "markdown"
    assert "Every three months" in artifact["content"]


def test_anthropic_agent_sdk_route_disables_tools(monkeypatch):
    captured = {}

    async def fake_query(*, prompt, options):
        captured["prompt"] = prompt
        captured["options"] = options
        yield AssistantMessage(
            content=[TextBlock(text="Agent SDK answer")],
            model="test-model",
            session_id="test-session",
        )

    monkeypatch.setattr(claude_agent_sdk, "query", fake_query)

    result = asyncio.run(llm_service._call_anthropic(
        prompt="What next?",
        context="Guest: Example",
        is_ship30=False,
        is_html_artifact=False,
        chunks=[],
        conversation_history=[{"role": "user", "content": "Earlier question"}],
    ))

    assert result[0] == "Agent SDK answer"
    assert captured["options"].tools == []
    assert captured["options"].max_turns == 1
    assert "Earlier question" in captured["prompt"]
    assert "TRANSCRIPT CONTEXT" in captured["prompt"]
