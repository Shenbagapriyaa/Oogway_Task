from datetime import datetime, timezone
import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field, ConfigDict

try:
    from app.database import Base
except ImportError:
    from ..database import Base

def utc_now():
    return datetime.now(timezone.utc)

# ==========================================
# SQLAlchemy ORM Models
# ==========================================

class SessionModel(Base):
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False, default="New Growth Session")
    model_provider = Column(String(50), nullable=False, default="ollama")
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    messages = relationship("MessageModel", back_populates="session", cascade="all, delete-orphan", order_by="MessageModel.created_at")


class MessageModel(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    model_used = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    session = relationship("SessionModel", back_populates="messages")
    artifacts = relationship("ArtifactModel", back_populates="message", cascade="all, delete-orphan")
    citations = relationship("CitationModel", back_populates="message", cascade="all, delete-orphan")


class ArtifactModel(Base):
    __tablename__ = "artifacts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(String(36), ForeignKey("messages.id"), nullable=False)
    title = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # 'markdown' or 'html'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utc_now)

    message = relationship("MessageModel", back_populates="artifacts")


class CitationModel(Base):
    __tablename__ = "citations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(String(36), ForeignKey("messages.id"), nullable=False)
    guest = Column(String(255), nullable=False)
    episode_title = Column(String(255), nullable=False)
    timestamp = Column(String(50), nullable=False)
    quote = Column(Text, nullable=False)

    message = relationship("MessageModel", back_populates="citations")


# ==========================================
# Pydantic Schemas for API Contracts (Pydantic v2 Clean)
# ==========================================

class CitationSchema(BaseModel):
    guest: str = Field(description="Guest speaker name")
    episode_title: str = Field(description="Title of the podcast episode")
    timestamp: str = Field(description="Timestamp or time range in the podcast")
    quote: str = Field(description="Verifiable excerpt from the transcript")

    model_config = ConfigDict(from_attributes=True)


class ArtifactSchema(BaseModel):
    id: Optional[str] = None
    title: str = Field(description="Artifact title or headline")
    type: str = Field(description="'markdown' or 'html'")
    content: str = Field(description="Complete rendered content of the artifact")
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class MessageSchema(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    model_used: Optional[str] = None
    created_at: datetime
    citations: List[CitationSchema] = Field(default_factory=list)
    artifacts: List[ArtifactSchema] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class SessionCreate(BaseModel):
    title: Optional[str] = "New Growth Session"
    model_provider: Optional[str] = "ollama"


class SessionResponse(BaseModel):
    id: str
    title: str
    model_provider: str
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)


class SessionDetailResponse(BaseModel):
    id: str
    title: str
    model_provider: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageSchema] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, description="User prompt or question")
    session_id: Optional[str] = Field(default=None, description="Existing session UUID, or null to auto-create")
    model_provider: Optional[str] = Field(default=None, description="Override model provider: 'ollama', 'anthropic', 'openai'")
    force_skill: Optional[str] = Field(default=None, description="Directly trigger skill: 'ship30' or 'artifact_html'")


class ChatResponse(BaseModel):
    session_id: str
    message: str
    citations: List[CitationSchema] = Field(default_factory=list)
    artifact: Optional[ArtifactSchema] = None
    model_used: str
    created_at: datetime


class ModelStatusResponse(BaseModel):
    current_provider: str
    available_providers: List[str] = Field(default_factory=list)
    ollama_status: Dict[str, Any] = Field(default_factory=dict)
    anthropic_status: Dict[str, Any] = Field(default_factory=dict)
    openai_status: Dict[str, Any] = Field(default_factory=dict)


class HealthStatus(BaseModel):
    status: str
    app_name: str
    version: str
    database: str
    transcripts_indexed: int
    models_available: List[str] = Field(default_factory=list)
