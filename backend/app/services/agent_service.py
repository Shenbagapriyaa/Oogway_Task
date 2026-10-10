import logging
import uuid
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models.schemas import (
    SessionModel, MessageModel, ArtifactModel, CitationModel,
    ChatRequest, ChatResponse, CitationSchema, ArtifactSchema
)
from app.services.retrieval_service import retrieval_service
from app.services.llm_service import llm_service
from app.services.security_service import security_service

logger = logging.getLogger(__name__)

class AgentService:
    def detect_intent(self, prompt: str, force_skill: Optional[str] = None) -> Tuple[bool, bool]:
        """Detect whether to invoke Ship 30 skill or HTML artifact generator."""
        if force_skill == "ship30":
            return True, False
        if force_skill == "artifact_html":
            return False, True

        lower = prompt.lower()
        is_ship30 = any(kw in lower for kw in ["ship 30", "ship30", "atomic essay", "1250 word", "write an essay", "write a post"])
        is_html = any(kw in lower for kw in ["calculator", "interactive", "html", "css", "dashboard", "prototype", "widget"])

        return is_ship30, is_html

    async def process_chat(self, db: Session, request: ChatRequest) -> ChatResponse:
        # 1. Resolve or Create Session
        session_id = request.session_id
        if not session_id:
            new_session = SessionModel(
                title=request.message[:45] + ("..." if len(request.message) > 45 else ""),
                model_provider=request.model_provider or "ollama"
            )
            db.add(new_session)
            db.commit()
            db.refresh(new_session)
            session_id = new_session.id
        else:
            session_record = db.query(SessionModel).filter(SessionModel.id == session_id).first()
            if not session_record:
                session_record = SessionModel(
                    id=session_id,
                    title=request.message[:45] + ("..." if len(request.message) > 45 else ""),
                    model_provider=request.model_provider or "ollama"
                )
                db.add(session_record)
                db.commit()

        # 2. Persist User Message
        user_msg = MessageModel(
            session_id=session_id,
            role="user",
            content=request.message,
            model_used=request.model_provider
        )
        db.add(user_msg)
        db.commit()

        # 3. Intent Detection & Tool Selection
        is_ship30, is_html = self.detect_intent(request.message, request.force_skill)

        # 4. Knowledge Base Hybrid Retrieval
        chunks, citations = retrieval_service.search(request.message, top_k=4)

        # 5. LLM Synthesis
        raw_text, model_used, raw_artifact = await llm_service.generate_response(
            prompt=request.message,
            context_chunks=chunks,
            provider=request.model_provider,
            is_ship30=is_ship30,
            is_html_artifact=is_html
        )

        # 6. Artifact Sanitization & Processing
        final_artifact = None
        if raw_artifact:
            art_type = raw_artifact.get("type", "markdown")
            art_content = raw_artifact.get("content", "")
            art_title = raw_artifact.get("title", "Generated Artifact")

            if art_type == "html":
                sanitized_html, warnings = security_service.sanitize_html_artifact(art_content)
                art_content = sanitized_html
                if warnings:
                    logger.info(f"Sanitized HTML artifact warnings: {warnings}")

            final_artifact = ArtifactSchema(
                id=str(uuid.uuid4()),
                title=art_title,
                type=art_type,
                content=art_content
            )

        # 7. Persist Assistant Message, Citations, and Artifacts
        assistant_msg = MessageModel(
            session_id=session_id,
            role="assistant",
            content=raw_text,
            model_used=model_used
        )
        db.add(assistant_msg)
        db.commit()
        db.refresh(assistant_msg)

        # Persist Citations
        for c in citations:
            cit_model = CitationModel(
                message_id=assistant_msg.id,
                guest=c.guest,
                episode_title=c.episode_title,
                timestamp=c.timestamp,
                quote=c.quote
            )
            db.add(cit_model)

        # Persist Artifact
        if final_artifact:
            art_model = ArtifactModel(
                id=final_artifact.id,
                message_id=assistant_msg.id,
                title=final_artifact.title,
                type=final_artifact.type,
                content=final_artifact.content
            )
            db.add(art_model)

        db.commit()

        return ChatResponse(
            session_id=session_id,
            message=raw_text,
            citations=citations,
            artifact=final_artifact,
            model_used=model_used,
            created_at=assistant_msg.created_at
        )

agent_service = AgentService()
