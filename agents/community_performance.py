from agents.state import AgentState
from tools.community_tools import get_community_metrics, get_inventory_status, get_lead_conversion

AGENT_NAME = "Community Performance Agent"


def run(state: AgentState) -> dict:
    if AGENT_NAME not in state.get("selected_agents", []):
        return {}

    prompt = state.get("user_prompt", "").lower()
    run_id = state.get("run_id")

    # Determine region scope from prompt
    region = None
    if "south florida" in prompt:
        region = "South Florida"
    elif "central florida" in prompt:
        region = "Central Florida"
    elif "texas" in prompt:
        region = "Texas"
    elif "carolina" in prompt:
        region = "Carolinas"

    tools_called = []
    tool_data = {}

    # Always pull community metrics
    metrics = get_community_metrics(region=region, agent_name=AGENT_NAME, run_id=run_id)
    tools_called.append("get_community_metrics")
    tool_data["community_metrics"] = metrics

    comms = metrics["communities"]
    under = [c for c in comms if not c["on_target"]]

    # Pull inventory for underperforming communities
    if under:
        community_name = under[0]["name"]
        inv = get_inventory_status(community_name, agent_name=AGENT_NAME, run_id=run_id)
        tools_called.append("get_inventory_status")
        tool_data["inventory"] = inv

    # Pull lead conversion
    conv = get_lead_conversion(region=region, agent_name=AGENT_NAME, run_id=run_id)
    tools_called.append("get_lead_conversion")
    tool_data["lead_conversion"] = conv

    # Format finding
    total = metrics["count"]
    summary_parts = [f"{c['name']}: {c['actual_monthly_sales']}/{c['target_monthly_sales']} target ({c['variance_pct']:+.0f}%)" for c in comms[:4]]
    finding = (
        f"Queried {total} {'South Florida ' if region == 'South Florida' else ''}communities. "
        f"{len(under)} below target. "
        + " | ".join(summary_parts)
    )
    if "inventory" in tool_data:
        inv = tool_data["inventory"]
        finding += f". **{inv['community']}**: {inv['stale_count']} stale homes (>{60} days), avg margin {inv['avg_gross_margin_pct']}%."

    return {
        "tool_results": {**state.get("tool_results", {}), **tool_data},
        "agent_outputs": {
            **state.get("agent_outputs", {}),
            AGENT_NAME: {
                "icon": "📊",
                "finding": finding,
                "tools_called": tools_called,
            },
        },
    }
