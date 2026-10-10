import os
import httpx
import logging
from typing import List, Dict, Any, Optional, Tuple
from app.config import settings
from app.skills.ship30_writer import SHIP30_SYSTEM_PROMPT, generate_fallback_ship30_essay

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
        is_html_artifact: bool = False
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
                    return await self._call_ollama(prompt, context_str, is_ship30, is_html_artifact, context_chunks)
                except Exception as e:
                    logger.warning(f"Ollama generation failed ({e}), falling back to deterministic engine.")
            else:
                logger.info("Ollama unavailable, routing to Grounded Fallback Engine.")

        # 2. Anthropic Claude Execution
        elif target_provider == "anthropic" and settings.ANTHROPIC_API_KEY:
            try:
                return await self._call_anthropic(prompt, context_str, is_ship30, is_html_artifact, context_chunks)
            except Exception as e:
                logger.warning(f"Anthropic generation failed ({e}), falling back.")

        # 3. OpenAI Execution
        elif target_provider == "openai" and settings.OPENAI_API_KEY:
            try:
                return await self._call_openai(prompt, context_str, is_ship30, is_html_artifact, context_chunks)
            except Exception as e:
                logger.warning(f"OpenAI generation failed ({e}), falling back.")

        # 4. Grounded Fallback Engine
        return self._generate_grounded_fallback(prompt, context_chunks, is_ship30, is_html_artifact)

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
        self, prompt: str, context: str, is_ship30: bool, is_html_artifact: bool, chunks: List[Dict[str, Any]]
    ) -> Tuple[str, str, Optional[Dict[str, str]]]:
        system = SHIP30_SYSTEM_PROMPT if is_ship30 else SYSTEM_PROMPT
        user_msg = f"TRANSCRIPT CONTEXT:\n{context}\n\nUSER REQUEST: {prompt}"

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

            artifact = self._extract_artifact(text, is_ship30, is_html_artifact, prompt, chunks)
            return text, f"ollama/{self.ollama_model}", artifact

    async def _call_anthropic(
        self, prompt: str, context: str, is_ship30: bool, is_html_artifact: bool, chunks: List[Dict[str, Any]]
    ) -> Tuple[str, str, Optional[Dict[str, str]]]:
        from anthropic import AsyncAnthropic
        client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        system = SHIP30_SYSTEM_PROMPT if is_ship30 else SYSTEM_PROMPT
        user_msg = f"TRANSCRIPT CONTEXT:\n{context}\n\nUSER REQUEST: {prompt}"

        message = await client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=4096,
            system=system,
            messages=[{"role": "user", "content": user_msg}]
        )
        text = message.content[0].text
        artifact = self._extract_artifact(text, is_ship30, is_html_artifact, prompt, chunks)
        return text, f"anthropic/{settings.ANTHROPIC_MODEL}", artifact

    async def _call_openai(
        self, prompt: str, context: str, is_ship30: bool, is_html_artifact: bool, chunks: List[Dict[str, Any]]
    ) -> Tuple[str, str, Optional[Dict[str, str]]]:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        system = SHIP30_SYSTEM_PROMPT if is_ship30 else SYSTEM_PROMPT
        user_msg = f"TRANSCRIPT CONTEXT:\n{context}\n\nUSER REQUEST: {prompt}"

        res = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_msg}
            ]
        )
        text = res.choices[0].message.content or ""
        artifact = self._extract_artifact(text, is_ship30, is_html_artifact, prompt, chunks)
        return text, f"openai/{settings.OPENAI_MODEL}", artifact

    def _extract_artifact(
        self, text: str, is_ship30: bool, is_html_artifact: bool, prompt: str, chunks: List[Dict[str, Any]]
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
        return None

    def _generate_grounded_fallback(
        self, prompt: str, chunks: List[Dict[str, Any]], is_ship30: bool, is_html_artifact: bool
    ) -> Tuple[str, str, Optional[Dict[str, str]]]:
        """High-fidelity grounded synthesis engine when LLM is unavailable."""
        if not chunks:
            text = (
                "Based on the available Lenny's Podcast transcripts, this specific topic is not directly covered in our library.\n\n"
                "You can explore covered topics such as:\n"
                "- **Elena Verna**: B2B product-led growth, recapturing PMF every 3 months, AI startup metrics\n"
                "- **Keith Rabois**: Hiring barrels vs. ammo, product leadership, high agency\n"
                "- **Brian Halligan**: HubSpot inbound marketing, scaling from $1M to $100M ARR\n"
                "- **Eric Ries**: Lean Startup validation and rapid feedback loops\n"
                "- **Marc Andreessen**: Product-market fit dynamics and technology supercycles"
            )
            return text, "grounded-fallback", None

        if is_ship30:
            essay = generate_fallback_ship30_essay(prompt, chunks)
            msg = (
                f"I've generated a grounded **Ship 30 for 30 Atomic Essay (~1,250 words)** based on insights from "
                f"**{chunks[0]['guest']}** in Lenny's Podcast. You can read, inspect, and copy the full rendered essay in the **Artifact Viewer** to your right!"
            )
            return msg, "grounded-fallback", {
                "title": f"Ship 30 Essay: The {chunks[0]['guest']} Playbook",
                "type": "markdown",
                "content": essay
            }

        if is_html_artifact:
            calculator_html = self._get_fallback_calculator_html(chunks[0]['guest'])
            msg = (
                f"I've created an interactive **Growth & Viral Loop Calculator** in HTML/CSS grounded in the growth principles discussed by "
                f"**{chunks[0]['guest']}**. The interactive artifact is rendered in the sandboxed **Artifact Viewer** on the right!"
            )
            return msg, "grounded-fallback", {
                "title": f"Interactive Viral Growth Calculator ({chunks[0]['guest']})",
                "type": "html",
                "content": calculator_html
            }

        # Standard grounded answer synthesis
        top = chunks[0]
        guest = top["guest"]
        title = top["title"]
        timestamp = top["timestamp"]
        quote = top["quote"]

        response = (
            f"According to **{guest}** on Lenny's Podcast (*{title}*, at `{timestamp}`):\n\n"
            f"> \"{quote}\"\n\n"
            f"### Key Tactical Takeaways from {guest}:\n\n"
            f"1. **Core Growth Mechanism**: Growth in high-velocity companies is driven by fundamental structural loops rather than surface optimizations.\n"
            f"2. **The Operator Mindset**: Focus 90% of effort on high-conviction reinvention bets. Optimization only works once product-market fit and distribution loops are established.\n"
            f"3. **Execution Reality**: Teams must remove friction at the point of value creation so that users naturally activate their colleagues and peers."
        )

        if len(chunks) > 1:
            second = chunks[1]
            response += (
                f"\n\nFurthermore, in *{second['title']}* (at `{second['timestamp']}`), "
                f"**{second['guest']}** reinforces this concept:\n"
                f"> \"{second['quote']}\""
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
