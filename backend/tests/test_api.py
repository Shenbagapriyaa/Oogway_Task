import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db
from app.services.retrieval_service import retrieval_service

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
