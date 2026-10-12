import logging
import re
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
    FOLLOW_UP_REFERENCES = {"he", "she", "it", "they", "them", "this", "that", "these", "those"}

    def is_follow_up_query(self, prompt: str) -> bool:
        words = set(re.findall(r"\b[a-z]+\b", prompt.lower()))
        return len(words) <= 18 and bool(words & self.FOLLOW_UP_REFERENCES)

    @staticmethod
    def is_greeting_intro(prompt: str) -> bool:
        lower = prompt.strip().lower()
        starts_with_greeting = bool(re.match(r"^(hi|hello|hey)\b", lower))
        introduces_self = bool(re.search(r"\bi(?:'m| am)\s+[a-z]", lower))
        asks_for_something = bool(re.search(
            r"\?|\b(what|who|when|where|why|how|can you|could you|please|tell me|explain|write|draft|create|build|summarize|compare|find me|search for|help me|need help)\b",
            lower,
        ))
        return starts_with_greeting and introduces_self and not asks_for_something

    def detect_intent(self, prompt: str, force_skill: Optional[str] = None) -> Tuple[bool, bool, bool]:
        """Detect writing-skill and artifact requests."""
        if force_skill == "ship30":
            return True, False, False
        if force_skill == "artifact_html":
            return False, True, False
        if force_skill == "artifact_markdown":
            return False, False, True

        lower = prompt.lower()
        is_ship30 = any(kw in lower for kw in ["ship 30", "ship30", "atomic essay", "1250 word", "write an essay", "write a post"])
        is_html = any(kw in lower for kw in ["calculator", "interactive", "html", "css", "dashboard", "prototype", "widget"])
        asks_to_create = any(kw in lower for kw in ["write", "draft", "create", "generate", "make"])
        is_markdown = not is_ship30 and asks_to_create and any(
            kw in lower for kw in ["markdown", "document", "brief", "prd", "playbook", "guide", "checklist"]
        )

        return is_ship30, is_html, is_markdown

    async def process_chat(self, db: Session, request: ChatRequest) -> ChatResponse:
        # 1. Resolve or Create Session
        session_id = request.session_id
        if not session_id:
            new_session = SessionModel(
                title=request.message[:45] + ("..." if len(request.message) > 45 else ""),
                model_provider=request.model_provider or "ollama",
                user_metadata=request.user_metadata or {}
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
                    model_provider=request.model_provider or "ollama",
                    user_metadata=request.user_metadata or {}
                )
                db.add(session_record)
                db.commit()
            elif request.user_metadata is not None:
                session_record.user_metadata = request.user_metadata
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

        previous_messages = (
            db.query(MessageModel)
            .filter(MessageModel.session_id == session_id, MessageModel.id != user_msg.id)
            .order_by(MessageModel.created_at.desc(), MessageModel.id.desc())
            .limit(12)
            .all()
        )
        conversation_history = [
            {"role": message.role, "content": message.content}
            for message in reversed(previous_messages)
            if message.role in {"user", "assistant"}
        ]

        is_intro = self.is_greeting_intro(request.message)
        if is_intro:
            name_match = re.search(r"\bi(?:'m| am)\s+([a-z][a-z'-]*)", request.message, re.IGNORECASE)
            name = name_match.group(1).title() if name_match else ""
            greeting = f"Hi {name}," if name else "Hi!"
            raw_text = f"{greeting} what product or growth question would you like to explore in the transcripts?"
            model_used = "conversation-guidance"
            raw_artifact = None
            chunks, citations = [], []
        else:
            raw_text = None
            model_used = None
            raw_artifact = None
            chunks, citations = [], []

        # 3. Intent Detection & Tool Selection
        is_ship30, is_html, is_markdown = self.detect_intent(request.message, request.force_skill)

        if raw_text is None:
            # Only carry the immediately preceding topic into an explicit follow-up.
            prior_questions = [
                message["content"] for message in conversation_history
                if message["role"] == "user" and not self.is_greeting_intro(message["content"])
            ]
            previous_question = prior_questions[-1] if prior_questions else None
            retrieval_context = (
                [previous_question]
                if previous_question and self.is_follow_up_query(request.message)
                else []
            )
            retrieval_query = " ".join([*retrieval_context, request.message])
            chunks, citations = retrieval_service.search(retrieval_query, top_k=4)

            # 5. LLM Synthesis
            raw_text, model_used, raw_artifact = await llm_service.generate_response(
                prompt=request.message,
                context_chunks=chunks,
                provider=request.model_provider,
                is_ship30=is_ship30,
                is_html_artifact=is_html,
                is_markdown_artifact=is_markdown,
                conversation_history=conversation_history
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
