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
                "You are a domain validator for an internal homebuilder operations platform. "
                "The platform handles: community sales, vendor approvals, construction delays, "
                "incentive pricing, marketing campaigns, associate workflow guidance, "
                "and governance/compliance.\n"
                "Respond with VALID if the question is related to these topics. "
                "Respond with INVALID for everything else.\n"
                "Answer with only one word: VALID or INVALID."
            ),
            user=prompt,
        )
        if result and result.strip().upper() == "VALID":
            return {"input_valid": True}

    return {"input_valid": False}
