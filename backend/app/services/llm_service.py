import os
import asyncio
import httpx
import logging
from typing import List, Dict, Any, Optional, Tuple
from app.config import settings
from app.skills.ship30_writer import SHIP30_SYSTEM_PROMPT, generate_source_brief

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are The Lenny Growth Assistant, an authoritative AI product and growth partner trained on the transcripts of Lenny's Podcast.

CORE OPERATING PRINCIPLES:
1. GROUNDED CITATIONS: Base your strategic answers strictly on the insights, quotes, and case studies found in the provided transcript context. Always cite the operator by name, episode title, and timestamp when referencing their ideas.
2. KNOWLEDGE BOUNDARY: If the provided transcript context does not contain relevant insights on the user's question, acknowledge it directly and honestly (e.g., "Based on the available Lenny's Podcast transcripts, this specific topic is not covered. You might explore episodes on [related topics]..."). Do NOT hallucinate false quotes or attribute opinions to guests that are not in the context.
3. OPERATIONAL SPECIFICITY: Avoid generic business jargon. Provide concrete, practitioner-level frameworks, tactical metrics, and actionable advice.
4. ARTIFACTS: When asked to write an essay, guide, PRD, or build an interactive tool/calculator, produce a dedicated, comprehensive artifact formatted cleanly in Markdown or HTML/CSS.
"""

class LLMService:
    def __init__(self):
        self.ollama_base_url = settings.OLLAMA_BASE_URL
        self.ollama_model = settings.OLLAMA_MODEL

    async def check_ollama_health(self) -> Dict[str, Any]:
        """Check if local Ollama daemon is running and which models are installed."""
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(f"{self.ollama_base_url}/api/tags")
                if res.status_code == 200:
                    models = [m.get("name") for m in res.json().get("models", [])]
                    return {
                        "available": True,
                        "endpoint": self.ollama_base_url,
                        "models": models,
                        "active_model": self.ollama_model
                    }
        except Exception as e:
            logger.debug(f"Ollama check failed: {e}")
        
        return {
            "available": False,
            "endpoint": self.ollama_base_url,
            "models": [],
            "error": "Ollama is not reachable at localhost:11434"
        }

    def check_cloud_health(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        anthropic_status = {
            "available": bool(settings.ANTHROPIC_API_KEY),
            "model": settings.ANTHROPIC_MODEL,
            "has_key": bool(settings.ANTHROPIC_API_KEY)
        }
        openai_status = {
            "available": bool(settings.OPENAI_API_KEY),
            "model": settings.OPENAI_MODEL,
            "has_key": bool(settings.OPENAI_API_KEY)
        }
        return anthropic_status, openai_status

    async def generate_response(
        self,
        prompt: str,
        context_chunks: List[Dict[str, Any]],
        provider: Optional[str] = None,
        is_ship30: bool = False,
        is_html_artifact: bool = False,
        is_markdown_artifact: bool = False,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Tuple[str, str, Optional[Dict[str, str]]]:
        """
        Generate grounded assistant response.
        Returns: (response_text, model_identifier, optional_artifact_dict)
        """
        target_provider = (provider or settings.DEFAULT_PROVIDER).lower()
        context_str = self._format_context(context_chunks)

        # 1. Local Ollama Execution
        if target_provider == "ollama":
            ollama_health = await self.check_ollama_health()
            if ollama_health.get("available"):
                try:
                    return await self._call_ollama(
                        prompt, context_str, is_ship30, is_html_artifact, context_chunks, conversation_history,
                        is_markdown_artifact
                    )
                except Exception as e:
                    logger.warning(f"Ollama generation failed ({e}), falling back to deterministic engine.")
            else:
                logger.info("Ollama unavailable, routing to Grounded Fallback Engine.")

        # 2. Anthropic Claude Execution
        elif target_provider == "anthropic" and settings.ANTHROPIC_API_KEY:
            try:
                return await self._call_anthropic(
                    prompt, context_str, is_ship30, is_html_artifact, context_chunks, conversation_history,
                    is_markdown_artifact
                )
            except Exception as e:
                logger.warning(f"Anthropic generation failed ({e}), falling back.")

        # 3. OpenAI Execution
        elif target_provider == "openai" and settings.OPENAI_API_KEY:
            try:
                return await self._call_openai(
                    prompt, context_str, is_ship30, is_html_artifact, context_chunks, conversation_history,
                    is_markdown_artifact
                )
            except Exception as e:
                logger.warning(f"OpenAI generation failed ({e}), falling back.")

        # 4. Grounded Fallback Engine
        return self._generate_grounded_fallback(
            prompt, context_chunks, is_ship30, is_html_artifact, is_markdown_artifact
        )

    def _format_context(self, chunks: List[Dict[str, Any]]) -> str:
        if not chunks:
            return "No transcript excerpts matched this query."
        formatted = []
        for i, c in enumerate(chunks):
            formatted.append(
                f"[Excerpt {i+1}]\n"
                f"Guest: {c.get('guest')}\n"
                f"Episode: {c.get('title')}\n"
                f"Timestamp: {c.get('timestamp')}\n"
                f"Content: {c.get('text')}\n"
            )
        return "\n---\n".join(formatted)

    async def _call_ollama(
        self,
        prompt: str,
        context: str,
        is_ship30: bool,
        is_html_artifact: bool,
        chunks: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, str]]] = None,
        is_markdown_artifact: bool = False,
    ) -> Tuple[str, str, Optional[Dict[str, str]]]:
        system = SHIP30_SYSTEM_PROMPT if is_ship30 else SYSTEM_PROMPT
        user_msg = self._format_user_prompt(prompt, context, conversation_history)

        async with httpx.AsyncClient(timeout=120.0) as client:
            res = await client.post(
                f"{self.ollama_base_url}/api/generate",
                json={
                    "model": self.ollama_model,
                    "system": system,
                    "prompt": user_msg,
                    "stream": False
                }
            )
            res.raise_for_status()
            text = res.json().get("response", "")

            artifact = self._extract_artifact(text, is_ship30, is_html_artifact, prompt, chunks, is_markdown_artifact)
            return text, f"ollama/{self.ollama_model}", artifact

    async def _call_anthropic(
        self,
        prompt: str,
        context: str,
        is_ship30: bool,
        is_html_artifact: bool,
        chunks: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, str]]] = None,
        is_markdown_artifact: bool = False,
    ) -> Tuple[str, str, Optional[Dict[str, str]]]:
        from claude_agent_sdk import AssistantMessage, ClaudeAgentOptions, ResultMessage, TextBlock, query

        system = SHIP30_SYSTEM_PROMPT if is_ship30 else SYSTEM_PROMPT
        options = ClaudeAgentOptions(
            model=settings.ANTHROPIC_MODEL,
            system_prompt=system,
            tools=[],
            setting_sources=[],
            permission_mode="dontAsk",
            max_turns=1,
            env={"ANTHROPIC_API_KEY": settings.ANTHROPIC_API_KEY},
        )

        async def collect_response() -> str:
            response_parts = []
            async for message in query(
                prompt=self._format_user_prompt(prompt, context, conversation_history),
                options=options,
            ):
                if isinstance(message, AssistantMessage):
                    response_parts.extend(block.text for block in message.content if isinstance(block, TextBlock))
                elif isinstance(message, ResultMessage) and message.is_error:
                    raise RuntimeError("Claude Agent SDK returned an error")
            return "\n".join(response_parts).strip()

        response_text = await asyncio.wait_for(collect_response(), timeout=120.0)
        if not response_text:
            raise RuntimeError("Claude Agent SDK returned an empty response")
        artifact = self._extract_artifact(
            response_text, is_ship30, is_html_artifact, prompt, chunks, is_markdown_artifact
        )
        return response_text, f"anthropic/{settings.ANTHROPIC_MODEL}", artifact

    async def _call_openai(
        self,
        prompt: str,
        context: str,
        is_ship30: bool,
        is_html_artifact: bool,
        chunks: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, str]]] = None,
        is_markdown_artifact: bool = False,
    ) -> Tuple[str, str, Optional[Dict[str, str]]]:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY, timeout=120.0)
        system = SHIP30_SYSTEM_PROMPT if is_ship30 else SYSTEM_PROMPT
        messages = self._format_provider_messages(prompt, context, conversation_history)

        res = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{"role": "system", "content": system}, *messages]
        )
        text = res.choices[0].message.content or ""
        artifact = self._extract_artifact(text, is_ship30, is_html_artifact, prompt, chunks, is_markdown_artifact)
        return text, f"openai/{settings.OPENAI_MODEL}", artifact

    def _format_user_prompt(
        self, prompt: str, context: str, conversation_history: Optional[List[Dict[str, str]]]
    ) -> str:
        history = "\n".join(
            f"{message['role'].upper()}: {message['content']}"
            for message in (conversation_history or [])
        )
        return (
            f"TRANSCRIPT CONTEXT:\n{context}\n\n"
            f"CONVERSATION HISTORY:\n{history or 'No previous turns.'}\n\n"
            f"CURRENT USER REQUEST: {prompt}"
        )

    def _format_provider_messages(
        self, prompt: str, context: str, conversation_history: Optional[List[Dict[str, str]]]
    ) -> List[Dict[str, str]]:
        history = [
            {"role": message["role"], "content": message["content"]}
            for message in (conversation_history or [])
            if message.get("role") in {"user", "assistant"} and message.get("content")
        ]
        history.append({"role": "user", "content": self._format_user_prompt(prompt, context, [])})
        return history

    def _extract_artifact(
        self,
        text: str,
        is_ship30: bool,
        is_html_artifact: bool,
        prompt: str,
        chunks: List[Dict[str, Any]],
        is_markdown_artifact: bool = False,
    ) -> Optional[Dict[str, str]]:
        if is_ship30:
            return {
                "title": f"Ship 30 Essay: {prompt[:50]}...",
                "type": "markdown",
                "content": text
            }
        
        # Check for HTML code blocks
        if "```html" in text:
            parts = text.split("```html")
            if len(parts) > 1:
                html_code = parts[1].split("```")[0].strip()
                return {
                    "title": "Interactive Growth Artifact",
                    "type": "html",
                    "content": html_code
                }
        if is_markdown_artifact:
            return {
                "title": f"Document: {prompt[:50]}",
                "type": "markdown",
                "content": text
            }
        return None

    def _generate_grounded_fallback(
        self,
        prompt: str,
        chunks: List[Dict[str, Any]],
        is_ship30: bool,
        is_html_artifact: bool,
        is_markdown_artifact: bool = False,
    ) -> Tuple[str, str, Optional[Dict[str, str]]]:
        """Return only source-backed material when no language model is available."""
        if not chunks:
            text = (
                "I couldn't find a relevant excerpt in the available Lenny's Podcast transcripts. "
                "I don't have enough source material to answer this reliably."
            )
            return text, "grounded-fallback", None

        if is_ship30:
            essay_brief = generate_source_brief(prompt, chunks)
            msg = (
                "The language model is unavailable, so I have not filled in unsupported claims to reach 1,250 words. "
                "I prepared a short source-backed essay brief instead; the retrieved excerpts and attribution are in the Artifact Viewer."
            )
            return msg, "grounded-fallback", {
                "title": f"Source-backed essay brief: {prompt[:45]}",
                "type": "markdown",
                "content": essay_brief
            }

        if is_html_artifact:
            msg = (
                "The language model is unavailable. I can show the built-in generic calculator, but it is an example, "
                "not an artifact generated from or endorsed by the retrieved transcript."
            )
            return msg, "grounded-fallback", {
                "title": "Generic viral coefficient calculator example",
                "type": "html",
                "content": self._get_fallback_calculator_html("Example only")
            }

        if is_markdown_artifact:
            artifact_content = generate_source_brief(prompt, chunks)
            return (
                "The language model is unavailable. I created a Markdown source brief from the retrieved excerpts, "
                "without adding unsupported recommendations.",
                "grounded-fallback",
                {
                    "title": f"Source brief: {prompt[:45]}",
                    "type": "markdown",
                    "content": artifact_content,
                },
            )

        excerpts = []
        for chunk in chunks:
            excerpts.append(
                f"**{chunk['guest']}**, *{chunk['title']}* (`{chunk['timestamp']}`):\n\n"
                f"> {chunk['quote']}"
            )
        response = (
            "I found these relevant transcript excerpts. The fallback does not synthesize advice beyond what they say; "
            "use a configured language model for analysis or recommendations.\n\n"
            + "\n\n".join(excerpts)
        )
        return response, "grounded-fallback", None

    def _get_fallback_calculator_html(self, guest: str) -> str:
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Product Growth & Viral Loop Calculator</title>
<style>
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background: #0f172a;
    color: #f8fafc;
    margin: 0;
    padding: 24px;
    box-sizing: border-box;
  }}
  .card {{
    background: #1e293b;
    border-radius: 12px;
    padding: 24px;
    max-width: 500px;
    margin: 0 auto;
    box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    border: 1px solid #334155;
  }}
  h2 {{
    margin-top: 0;
    color: #38bdf8;
    font-size: 20px;
  }}
  .badge {{
    display: inline-block;
    padding: 4px 8px;
    background: #0369a1;
    color: #e0f2fe;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
    margin-bottom: 16px;
  }}
  .control {{
    margin-bottom: 16px;
  }}
  label {{
    display: block;
    font-size: 13px;
    margin-bottom: 6px;
    color: #94a3b8;
  }}
  input[type="range"] {{
    width: 100%;
    accent-color: #38bdf8;
  }}
  .metric-box {{
    background: #0f172a;
    border-radius: 8px;
    padding: 16px;
    margin-top: 20px;
    border: 1px solid #1e293b;
    text-align: center;
  }}
  .metric-val {{
    font-size: 32px;
    font-weight: 700;
    color: #10b981;
    margin: 8px 0;
  }}
  .metric-label {{
    font-size: 12px;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}
  .verdict {{
    margin-top: 12px;
    font-size: 13px;
    padding: 8px 12px;
    border-radius: 6px;
    background: #1e293b;
  }}
</style>
</head>
<body>
<div class="card">
  <div class="badge">LENNY GROWTH BENCHMARK • {guest.upper()}</div>
  <h2>Viral Coefficient (K-Factor) Model</h2>
  
  <div class="control">
    <label>Invites Sent Per Active User (i): <strong id="i-val">5</strong></label>
    <input type="range" id="invites" min="1" max="20" value="5" oninput="calculate()">
  </div>

  <div class="control">
    <label>Invite Acceptance Conversion % (c): <strong id="c-val">15%</strong></label>
    <input type="range" id="conversion" min="1" max="50" value="15" oninput="calculate()">
  </div>

  <div class="control">
    <label>Cycle Time in Days (t): <strong id="t-val">7 days</strong></label>
    <input type="range" id="cycle" min="1" max="30" value="7" oninput="calculate()">
  </div>

  <div class="metric-box">
    <div class="metric-label">Calculated Viral Coefficient (K)</div>
    <div class="metric-val" id="k-factor">0.75</div>
    <div class="verdict" id="verdict-box">Viral Loop is Sub-Critical (K &lt; 1.0). Growth decays without top-of-funnel acquisition.</div>
  </div>
</div>

<script>
function calculate() {{
  const invites = parseFloat(document.getElementById('invites').value);
  const conversion = parseFloat(document.getElementById('conversion').value) / 100.0;
  const cycle = parseInt(document.getElementById('cycle').value);

  document.getElementById('i-val').innerText = invites;
  document.getElementById('c-val').innerText = (conversion * 100).toFixed(0) + '%';
  document.getElementById('t-val').innerText = cycle + ' days';

  const k = invites * conversion;
  const kElement = document.getElementById('k-factor');
  kElement.innerText = k.toFixed(2);

  const verdict = document.getElementById('verdict-box');
  if (k >= 1.0) {{
    kElement.style.color = '#10b981';
    verdict.innerText = 'Super-Critical Virality (K >= 1.0)! True exponential viral growth unlocked.';
    verdict.style.color = '#34d399';
  }} else if (k >= 0.5) {{
    kElement.style.color = '#fbbf24';
    verdict.innerText = 'High Amplification (0.5 <= K < 1.0). Each paid user brings ' + k.toFixed(2) + ' free organic users.';
    verdict.style.color = '#fde68a';
  }} else {{
    kElement.style.color = '#f87171';
    verdict.innerText = 'Sub-Critical (K < 0.5). Product is primarily driven by paid/outbound channels.';
    verdict.style.color = '#fca5a5';
  }}
}}
calculate();
</script>
</body>
</html>"""

llm_service = LLMService()
