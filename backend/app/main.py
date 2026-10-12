import logging
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.services.retrieval_service import retrieval_service
from app.routers import chat, sessions, health

class JsonLogFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload)


handler = logging.StreamHandler()
handler.setFormatter(JsonLogFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger("lenny-assistant")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing The Lenny Growth Assistant...")
    # Initialize Database
    try:
        init_db()
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

    # Build or Load Transcript Search Index
    try:
        retrieval_service.initialize()
        logger.info(f"Loaded {len(retrieval_service.retriever.chunks)} transcript chunks into knowledge base.")
    except Exception as e:
        logger.error(f"Failed to build transcript index: {e}")

    yield
    logger.info("Shutting down Lenny Growth Assistant.")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="AI-powered growth and product assistant grounded in Lenny's Podcast transcripts.",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(chat.router)
app.include_router(sessions.router)
app.include_router(health.router)

@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "status": "ready"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
