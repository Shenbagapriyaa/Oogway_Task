import logging
from fastapi import APIRouter
from app.config import settings
from app.database import engine
from app.services.retrieval_service import retrieval_service
from app.services.llm_service import llm_service
from app.services.ingestion_service import ingestion_service
from app.models.schemas import HealthStatus, ModelStatusResponse

router = APIRouter(prefix="/api", tags=["System & Health"])
logger = logging.getLogger(__name__)

@router.get("/health", response_model=HealthStatus)
def health_check():
    db_type = "PostgreSQL" if "postgresql" in str(engine.url) else "SQLite"
    chunks_count = len(retrieval_service.retriever.chunks) if retrieval_service.is_initialized else len(ingestion_service.chunks)
    try:
        with engine.connect():
            database_status = "connected"
    except Exception:
        logger.exception("Database health check failed")
        database_status = "unavailable"

    return HealthStatus(
        status="healthy" if database_status == "connected" else "degraded",
        database_status=database_status,
        app_name=settings.APP_NAME,
        version=settings.VERSION,
        database=db_type,
        transcripts_indexed=chunks_count,
        models_available=["ollama", "anthropic", "openai", "grounded-fallback"]
    )

@router.get("/models/status", response_model=ModelStatusResponse)
async def model_status():
    ollama_stat = await llm_service.check_ollama_health()
    anthropic_stat, openai_stat = llm_service.check_cloud_health()

    return ModelStatusResponse(
        current_provider=settings.DEFAULT_PROVIDER,
        available_providers=["ollama", "anthropic", "openai", "grounded-fallback"],
        ollama_status=ollama_stat,
        anthropic_status=anthropic_stat,
        openai_status=openai_stat
    )

@router.get("/transcripts")
def list_transcripts():
    """List loaded podcast episodes with metadata."""
    if not retrieval_service.is_initialized:
        retrieval_service.initialize()
    
    episodes = {}
    for c in retrieval_service.retriever.chunks:
        title = c.get("title")
        if title not in episodes:
            episodes[title] = {
                "title": title,
                "guest": c.get("guest"),
                "date": c.get("date"),
                "chunks_count": 0
            }
        episodes[title]["chunks_count"] += 1

    return {
        "total_episodes": len(episodes),
        "total_chunks": len(retrieval_service.retriever.chunks),
        "episodes": list(episodes.values())
    }
