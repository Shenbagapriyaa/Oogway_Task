from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.schemas import (
    SessionModel, MessageModel, SessionResponse, SessionDetailResponse, SessionCreate, MessageSchema, CitationSchema, ArtifactSchema
)

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])

@router.get("", response_model=List[SessionResponse])
def list_sessions(db: Session = Depends(get_db)):
    sessions = db.query(SessionModel).order_by(SessionModel.updated_at.desc()).all()
    results = []
    for s in sessions:
        results.append(SessionResponse(
            id=s.id,
            title=s.title,
            model_provider=s.model_provider,
            created_at=s.created_at,
            updated_at=s.updated_at,
            message_count=len(s.messages)
        ))
    return results

@router.post("", response_model=SessionResponse)
def create_session(payload: SessionCreate, db: Session = Depends(get_db)):
    session = SessionModel(
        title=payload.title or "New Growth Session",
        model_provider=payload.model_provider or "ollama"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return SessionResponse(
        id=session.id,
        title=session.title,
        model_provider=session.model_provider,
        created_at=session.created_at,
        updated_at=session.updated_at,
        message_count=0
    )

@router.get("/{session_id}", response_model=SessionDetailResponse)
def get_session_detail(session_id: str, db: Session = Depends(get_db)):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages_data = []
    for m in session.messages:
        citations = [
            CitationSchema(
                guest=c.guest,
                episode_title=c.episode_title,
                timestamp=c.timestamp,
                quote=c.quote
            ) for c in m.citations
        ]
        artifacts = [
            ArtifactSchema(
                id=a.id,
                title=a.title,
                type=a.type,
                content=a.content,
                created_at=a.created_at
            ) for a in m.artifacts
        ]
        messages_data.append(MessageSchema(
            id=m.id,
            session_id=m.session_id,
            role=m.role,
            content=m.content,
            model_used=m.model_used,
            created_at=m.created_at,
            citations=citations,
            artifacts=artifacts
        ))

    return SessionDetailResponse(
        id=session.id,
        title=session.title,
        model_provider=session.model_provider,
        created_at=session.created_at,
        updated_at=session.updated_at,
        messages=messages_data
    )

@router.delete("/{session_id}")
def delete_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(session)
    db.commit()
    return {"status": "deleted", "id": session_id}
