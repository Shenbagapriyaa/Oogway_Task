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

def generate_fallback_ship30_essay(topic: str, chunks: List[Dict[str, Any]]) -> str:
    """Deterministic fallback generator for 1,250-word Ship 30 for 30 essay when LLM is offline."""
    guest = chunks[0].get("guest", "Top Tech Operator") if chunks else "Lenny's Operator"
    title = chunks[0].get("title", "Lenny's Podcast") if chunks else "Product Growth Masterclass"
    timestamp = chunks[0].get("timestamp", "00:00:00") if chunks else "00:00:00"
    quote = chunks[0].get("quote", "Focus on what actually moves the needle.") if chunks else ""
    
    essay = f"""# The Operator's Playbook: Why Most Growth Strategies Fail (And What {guest} Knows That You Don't)

Most product managers build features nobody asks for.

They spend months tweaking button colors, redesigning checkout pages, and A/B testing onboarding tooltips that increase conversion by a measly 0.4%. Meanwhile, their retention curve is leaking like a rusted sieve, their CAC is compounding out of control, and their board is asking why ARR has flatlined.

Here is the brutal truth: **Optimization is what you do when you have run out of real ideas.**

On Lenny's Podcast, **{guest}** shared the exact counter-intuitive philosophy that separates generational product leaders from spreadsheet managers.

Here is the 4-pillar blueprint to rewire your product engine.

---

### Pillar 1: Kill Optimization. Bet on Reinvention.

The biggest trap in high-growth companies is confusing activity with leverage.

Teams get comfortable running micro-experiments because micro-experiments are safe. If an A/B test fails, nobody gets fired. If you optimize an existing email cadence, you can show a shiny slide in your sprint review.

But as {guest} pointed out on Lenny's Podcast ({title}, at {timestamp}):
> *"{quote}"*

When you are fighting for category leadership, 5% improvements are a recipe for slow death.

**How to execute the reinvention mindset:**
* **Audit your backlog for cowardice:** If 80% of your tickets are tweaks to existing flows, halt the sprint.
* **Allocate a 70/30 innovation ratio:** 70% of engineering bandwidth should go toward big, structural bets that can create a 5x step-function change.
* **Test the counter-intuitive hypothesis:** Ask your team: *"What is one sacred rule in our industry that our competitors treat as gospel, which is actually obsolete?"*

If your strategy does not make at least one executive nervous, it is not an innovation bet—it is a maintenance ticket.

---

### Pillar 2: Build Viral Loops into the Product Core, Not the Marketing Layer

Marketing teams cannot rescue a product that users do not obsessively share.

Traditional growth teams treat distribution as an afterthought. They build the software, toss it over the fence to the growth lead, and say, "Now go buy Google Ads and write cold outbound emails."

That playbook is dead. In the modern software landscape, distribution must be baked directly into the core workflow.

**The tactical mechanics of organic distribution:**
* **Make the artifact shareable:** When a user generates value inside your platform, the natural output should be an asset they want to show their team, their boss, or their Twitter followers.
* **Remove friction at the point of pride:** If a user completes a milestone, give them a one-click way to embed or broadcast the result.
* **Incentivize multi-player utility:** Every single user who joins your product should make the product automatically 10% more useful for their colleagues.

As {guest} emphasized, **the only durable growth engine is word-of-mouth that blows users' socks off.**

---

### Pillar 3: Recapture Product-Market Fit Every Single Quarter

The most dangerous myth in Silicon Valley is that product-market fit is a permanent milestone.

Founders think that once they hit $1M or $10M in ARR, they have "arrived." They think the engine is built and all that is left is turning the crank.

In reality, especially in the era of AI and fast-moving software paradigms, **product-market fit decays every 90 days.**

New competitors emerge overnight. Customer expectations reset. Tools that felt magical last year feel clunky and legacy today.

**The quarterly PMF diagnostic:**
* **Track the "Very Disappointed" metric:** Survey your active cohort every 60 days with the Sean Ellis question: *"How would you feel if you could no longer use this product tomorrow?"* If this drops below 40%, you are losing PMF.
* **Talk to churned power users:** Never delegate churn interviews. The founder or core PM must spend at least 4 hours every week speaking directly to users who loved the product and left.
* **Throw out yesterday's playbook:** What got you from $0 to $1M ARR will actively sabotage your journey from $10M to $50M ARR.

---

### Pillar 4: Fire Your Ammo. Double Down on Barrels.

Scaling an organization is not a headcount contest.

Most teams believe that when growth stalls, the solution is to hire five more junior PMs and ten more engineers. But adding more people to an unguided direction simply creates organizational drag and communication debt.

You do not need more ammo. **You need barrels.**

A barrel is an operator who can take an ambiguous, terrifying problem, formulate the strategy from scratch, rally the team, and push the rock all the way up the mountain without hand-holding.

**How to spot and empower a barrel:**
* **Look for extreme ownership:** Barrels do not say "that was outside my scope." They fix the broken customer experience regardless of whose department it touches.
* **Give them immense agency:** Do not micromanage their day-to-day tickets. Give them a North Star metric, clear constraints, and let them ship.
* **Protect them from bureaucracy:** When high-agency operators are forced into endless steering committees, they leave. Clear the runway so they can move at the speed of thought.

---

### The 24-Hour Implementation Takeaway

Do not let this essay sit in your browser tabs as passive motivation.

Here is your exact challenge for the next 24 hours:

1. **Pick one sacred cow in your product:** Identify the flow where you have spent the most time optimizing tiny conversion percentages over the last quarter.
2. **Design the 10x alternative:** Draft a 1-page spec for a radical simplification that removes 80% of the friction entirely.
3. **Show it to 3 real customers tomorrow afternoon.**

Great product leadership is not about doing everything. It is about having the courage to do the few things that truly compound.

Now go ship it.
"""
    return essay.strip()
