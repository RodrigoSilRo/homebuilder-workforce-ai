from agents.state import AgentState
from tools.construction_tools import get_construction_delays

AGENT_NAME = "Construction Delay Agent"


def run(state: AgentState) -> dict:
    if AGENT_NAME not in state.get("selected_agents", []):
        return {}

    run_id = state.get("run_id")

    delays = get_construction_delays(agent_name=AGENT_NAME, run_id=run_id)
    total  = delays["total_affected_closings"]
    parties = ", ".join(delays["responsible_parties"][:3]) if delays["responsible_parties"] else "Unknown"
    by_comm = delays.get("by_community", [])

    if total == 0:
        finding = "No active construction delays found."
    else:
        comm_parts = [f"{c['community']}: {c['affected_closings']} lots ({c['delays'][0]['delayed_days']}d delay)"
                      for c in by_comm[:3]]
        finding = (
            f"**{total} closings affected** across {len(by_comm)} communities. "
            + " | ".join(comm_parts)
            + f". Responsible parties: {parties}. "
            + ("**Escalation required** (>10 closings)." if delays["escalation_required"] else "No auto-escalation triggered.")
        )

    return {
        "tool_results": {**state.get("tool_results", {}), "construction_delays": delays},
        "agent_outputs": {
            **state.get("agent_outputs", {}),
            AGENT_NAME: {
                "icon": "🏗️",
                "finding": finding,
                "tools_called": ["get_construction_delays"],
            },
        },
    }
