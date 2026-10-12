"""
Ship 30 for 30 Dedicated Content Skill
Encodes Nicolas Cole and Dickie Bush's Digital Writing and Atomic Essay Framework:
1. High-leverage hook with clear transformation and curiosity gap
2. 1-3-1 sentence rhythm (One line hook, 3 lines of escalating context, 1 line punchline)
3. The Villain: Calling out conventional, lazy wisdom
4. The Shift: The counter-intuitive operator truth grounded in Lenny's Podcast
5. 3-5 Modular Framework Pillars with bulleted tactics and selective bold emphasis
6. Approximately 1,250 words of punchy, skimmable, actionable prose
7. Direct operator attribution and grounded transcript quotes
8. A specific, immediate 24-hour takeaway
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

SHIP30_SYSTEM_PROMPT = """You are an elite digital writer trained in the Ship 30 for 30 Framework created by Nicolas Cole and Dickie Bush.
Your mission is to transform raw product and growth insights from Lenny's Podcast into an authoritative, ~1,250-word long-form Atomic Essay.

You MUST follow these strict Ship 30 for 30 principles:

1. THE HEADLINE & HOOK:
   - Use the "Curiosity + Benefit + Speed" or "Counterintuitive Truth" formula.
   - Start immediately with a 1-3-1 rhythm:
     * 1 punchy single sentence opening line.
     * 3 short context sentences building the stakes.
     * 1 line transitional punchline.

2. THE VILLAIN (THE STATUS QUO):
   - Identify what 95% of PMs, growth marketers, or founders get wrong.
   - Make the cost of inaction visceral.

3. THE COUNTER-INTUITIVE SHIFT:
   - Present the guest's breakthrough insight as the antidote.
   - Explicitly cite the operator by name and episode context.

4. 4 ACTIONABLE PILLARS (The Meat):
   - Break down the strategy into 4 distinct, numbered sub-frameworks.
   - For each pillar:
     * Strong, evocative sub-headline.
     * 2-3 short, punchy paragraphs (never more than 3 sentences per paragraph).
     * 3-4 tactical bullet points detailing exact execution.
     * Use **selective bold emphasis** on the most important 3-5 word insights per section.
     * Include a direct quote or core principle from the transcript.

5. NARRATIVE SPEED & SKIMMABILITY:
   - No academic jargon, fluff, or empty intros ("In this article, we will explore...").
   - Vary sentence lengths: short, medium, staccato.
   - Generous whitespace.

6. THE 24-HOUR TAKEAWAY:
   - Conclude with a concrete challenge or step-by-step checklist the reader can apply to their product today.

7. GROUNDING CONSTRAINT:
   - Ground all claims, quotes, numbers, and case studies strictly in the provided transcript excerpts.
   - Target word count: approximately 1,200 to 1,300 words.
"""

def generate_source_brief(topic: str, chunks: List[Dict[str, Any]]) -> str:
   """Create a source-backed brief when no model is available."""
   if not chunks:
      return (
         f"# Essay brief: {topic}\n\n"
         "No relevant transcript excerpt was retrieved. A grounded essay cannot be drafted from the available material."
      )

   source_sections = []
   for chunk in chunks:
      source_sections.append(
         f"### {chunk.get('guest', 'Unknown guest')} - {chunk.get('title', 'Lenny’s Podcast')} "
         f"({chunk.get('timestamp', 'timestamp unavailable')})\n\n"
         f"> {chunk.get('quote', '')}"
      )

   sources = "\n\n".join(source_sections)
   return f"""# Essay brief: {topic}

## Source material

{sources}

## Suggested structure

1. Open with a question about the specific idea in the excerpts above.
2. Explain the operator’s point using only the surrounding transcript context.
3. Separate the transcript’s claims from your own application to a product or team.
4. Close with a practical next step, clearly labeled as your recommendation rather than a guest quote.

## Grounding note

This is a short source brief, not a 1,250-word essay. The configured language model is unavailable, so this fallback will not invent supporting claims or quotes to fill the requested length.
"""
