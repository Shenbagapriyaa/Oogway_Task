from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schemas import ChatRequest, ChatResponse
from app.services.agent_service import agent_service

router = APIRouter(prefix="/api/chat", tags=["Chat"])

@router.post("", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Execute grounded conversation turn with optional Ship 30 essay or HTML artifact generation.
    """
    try:
        response = await agent_service.process_chat(db, request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution error: {str(e)}")
