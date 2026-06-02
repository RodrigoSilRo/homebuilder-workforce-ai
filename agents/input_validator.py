"""
Input Validator — first node in the LangGraph pipeline.

Checks whether the prompt is a valid homebuilder business question before
routing to any specialist agents or calling any tools.

Strategy:
  1. Rule-based keyword check  (fast, free, handles obvious cases)
  2. LLM single-word check     (fallback for ambiguous inputs, costs one call)
  3. Default: reject if neither passes
"""
from agents.state import AgentState
from services.llm import chat, has_llm

DOMAIN_KEYWORDS = {
    # Properties / inventory
    "community", "communities", "home", "homes", "house", "houses",
    "lot", "lots", "inventory", "stale", "available",
    # Sales
    "sales", "sale", "sell", "selling", "sold", "close", "closing", "closings",
    "lead", "leads", "conversion", "pipeline",
    # Vendors / procurement
    "vendor", "vendors", "subcontractor", "subcontractors", "contractor",
    "contract", "insurance", "onboard", "onboarding",
    # Construction
    "construction", "build", "building", "delay", "delays",
    "permit", "inspection", "schedule",
    # Finance
    "incentive", "incentives", "discount", "pricing", "margin", "margins",
    "revenue", "cost", "budget", "finance", "financial",
    # Marketing
    "marketing", "campaign", "campaigns",
    # Policy / governance
    "policy", "policies", "workflow", "workflows", "procedure",
    "approval", "approve", "escalate", "escalation",
    "risk", "compliance", "governance", "audit",
    # People
    "associate", "associates", "employee",
    # Geography (seeded communities / regions)
    "florida", "texas", "carolinas",
    "coral bay", "palm grove", "ocean vista",
    "cypress trails", "willow creek", "lakeside",
    # Strategy / growth / expansion
    "market", "markets", "expand", "expansion", "expand",
    "growth", "grow", "strategy", "strategic",
    "opportunity", "opportunities", "idea", "ideas",
    "international", "region", "regional", "geographic",
    "launch", "enter", "target", "competitive", "business",
    "operations", "proposal",
    # Generic intent words that make sense in context
    "improve", "underperform", "performance", "analyze",
    "analysis", "report", "review", "recommend",
}


def validate_input(state: AgentState) -> dict:
    prompt = (state.get("user_prompt") or "").lower().strip()

    if not prompt:
        return {"input_valid": False}

    # ── Rule-based: one matching domain keyword is enough ─────────────────────
    if any(kw in prompt for kw in DOMAIN_KEYWORDS):
        return {"input_valid": True}

    # ── LLM fallback for ambiguous prompts ────────────────────────────────────
    if has_llm():
        result = chat(
            system=(
                "You are a gatekeeper for an internal AI platform used by a national homebuilder.\n\n"
                "Examples of VALID questions:\n"
                "- 'Why is Coral Bay 39% below sales target?' → VALID\n"
                "- 'Can we expand operations to the Brazilian market?' → VALID\n"
                "- 'Which vendor contracts need escalation this week?' → VALID\n"
                "- 'What is our gross margin policy for incentive pricing?' → VALID\n"
                "- 'How do I onboard a new subcontractor?' → VALID\n\n"
                "Examples of INVALID questions:\n"
                "- 'What is the best chocolate cake recipe?' → INVALID\n"
                "- 'Who won the Super Bowl last year?' → INVALID\n"
                "- 'How should I invest my personal savings?' → INVALID\n\n"
                "Rule: answer VALID for any homebuilder business question — operations, strategy, "
                "finance, people, vendors, construction, or market decisions.\n"
                "Answer INVALID only for content clearly unrelated to business.\n"
                "When in doubt → VALID.\n\n"
                "Answer with exactly one word: VALID or INVALID."
            ),
            user=prompt,
        )
        if result and result.strip().upper() == "VALID":
            return {"input_valid": True}

    return {"input_valid": False}
