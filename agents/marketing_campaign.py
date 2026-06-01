from agents.state import AgentState
from tools.marketing_tools import generate_marketing_campaign

AGENT_NAME = "Marketing Campaign Agent"


def run(state: AgentState) -> dict:
    if AGENT_NAME not in state.get("selected_agents", []):
        return {}

    run_id = state.get("run_id")

    # Pick the most underperforming community from community data, or default to Coral Bay
    comms = state.get("tool_results", {}).get("community_metrics", {}).get("communities", [])
    under = [c for c in comms if not c.get("on_target")]
    community_name = under[0]["name"] if under else "Coral Bay"

    # Determine objective from what tools found
    inv = state.get("tool_results", {}).get("inventory", {})
    stale = inv.get("stale_count", 0) if inv else 0
    objective = "Move stale inventory" if stale > 5 else "Improve lead conversion rate"
    audience  = "Move-in-ready home seekers" if stale > 5 else "Warm leads who visited but haven't committed"

    campaign = generate_marketing_campaign(
        community_name=community_name,
        target_audience=audience,
        objective=objective,
        agent_name=AGENT_NAME,
        run_id=run_id,
    )

    finding = (
        f"Campaign brief generated for **{community_name}** — objective: {objective}. "
        f"Email, ad, and SMS copy ready. "
        f"Human approval required before launch."
    )

    return {
        "tool_results": {**state.get("tool_results", {}), "campaign": campaign},
        "agent_outputs": {
            **state.get("agent_outputs", {}),
            AGENT_NAME: {
                "icon": "📣",
                "finding": finding,
                "tools_called": ["generate_marketing_campaign"],
                "campaign": campaign,
            },
        },
        "approval_required": True,
    }
