from agents.state import AgentState
from tools.finance_tools import calculate_incentive_impact

AGENT_NAME = "Finance / Incentive Agent"
MARGIN_LIMIT = 1.5


def run(state: AgentState) -> dict:
    if AGENT_NAME not in state.get("selected_agents", []):
        return {}

    run_id = state.get("run_id")
    # Use underperforming community from community metrics if available
    comms = state.get("tool_results", {}).get("community_metrics", {}).get("communities", [])
    target_community = next((c["name"] for c in comms if not c.get("on_target")), "Coral Bay")

    results = {}
    finding_parts = []
    tools_called = []
    risk_level = "low"

    for pct in [0.75, 1.25, 2.00]:
        r = calculate_incentive_impact(target_community, pct, agent_name=AGENT_NAME, run_id=run_id)
        tools_called.append("calculate_incentive_impact")
        key = f"{pct:.2f}"
        results[key] = r
        impact = r["margin_impact_pct"]
        blocked = r["blocked_by_policy"]
        label = "BLOCKED" if blocked else f"→ {r['approval_level']} approval"
        finding_parts.append(f"{pct:.2f}%: impact {impact:.2f}% margin {label}")
        if not blocked and abs(impact) >= 1.0:
            risk_level = "medium"

    finding = (
        f"Modeled 3 scenarios for **{target_community}**: "
        + " | ".join(finding_parts)
        + f". 2.00% scenario blocked — exceeds {MARGIN_LIMIT}% policy limit."
    )

    approval_required = any(
        not r.get("blocked_by_policy") and abs(r["margin_impact_pct"]) >= 1.0
        for r in results.values()
    )

    prev_risk = state.get("risk_level", "low")
    new_risk = "medium" if risk_level == "medium" or prev_risk == "medium" else prev_risk

    return {
        "tool_results": {**state.get("tool_results", {}), "incentive": results},
        "agent_outputs": {
            **state.get("agent_outputs", {}),
            AGENT_NAME: {
                "icon": "💰",
                "finding": finding,
                "tools_called": list(dict.fromkeys(tools_called)),  # deduplicate
            },
        },
        "risk_level": new_risk,
        "approval_required": state.get("approval_required", False) or approval_required,
    }
