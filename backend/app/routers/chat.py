import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schemas import ChatRequest, ChatResponse
from app.services.agent_service import agent_service

router = APIRouter(prefix="/api/chat", tags=["Chat"])
logger = logging.getLogger(__name__)

@router.post("", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Execute grounded conversation turn with optional Ship 30 essay or HTML artifact generation.
    """
    try:
        response = await agent_service.process_chat(db, request)
        return response
    except Exception:
        logger.exception("Chat request failed")
        raise HTTPException(
            status_code=500,
            detail={"code": "chat_execution_failed", "message": "The assistant could not complete this request."},
        )
