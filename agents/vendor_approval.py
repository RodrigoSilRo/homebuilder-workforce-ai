from agents.state import AgentState
from tools.vendor_tools import get_vendor_profile, get_vendor_risk_score
from tools.approval_tools import create_approval_request

AGENT_NAME = "Vendor Approval Agent"

# Vendors to review when running a general vendor scan
DEFAULT_VENDORS = ["Coastal Electrical LLC", "Gulf Coast Landscaping"]


def run(state: AgentState) -> dict:
    if AGENT_NAME not in state.get("selected_agents", []):
        return {}

    run_id = state.get("run_id")
    prompt = state.get("user_prompt", "").lower()

    # Detect specific vendor in prompt
    known_vendors = [
        "Coastal Electrical LLC", "Sunstate Roofing Group",
        "Premier Concrete Services", "Atlantic HVAC Partners", "Gulf Coast Landscaping",
    ]
    target_vendors = [v for v in known_vendors if v.lower() in prompt] or DEFAULT_VENDORS

    all_profiles = {}
    finding_parts = []
    tools_called = []
    high_risk_found = False

    for vendor_name in target_vendors:
        try:
            profile = get_vendor_profile(vendor_name, agent_name=AGENT_NAME, run_id=run_id)
            risk    = get_vendor_risk_score(vendor_name, agent_name=AGENT_NAME, run_id=run_id)
            tools_called += ["get_vendor_profile", "get_vendor_risk_score"]
            all_profiles[vendor_name] = {"profile": profile, "risk": risk}

            flag_str = f" | Flags: {', '.join(profile['flags'])}" if profile["flags"] else ""
            finding_parts.append(
                f"**{vendor_name}**: risk {profile['risk_score']} ({profile['risk_level'].upper()}), "
                f"insurance {profile['insurance_status'].upper()}, "
                f"contract ${profile['active_contract_value']:,.0f}{flag_str}"
            )

            if profile["risk_level"] == "high" or profile["insurance_status"] != "current":
                high_risk_found = True
                # Auto-create approval request for high-risk vendor
                create_approval_request(
                    recommended_action=f"Review and approve/reject {vendor_name} — {risk['recommendation']}",
                    risk_level=profile["risk_level"],
                    required_approver="VP Procurement",
                    agent_run_id=run_id,
                    community=None,
                    flags=profile["flags"],
                    agent_name=AGENT_NAME,
                    run_id=run_id,
                )
                tools_called.append("create_approval_request")

        except ValueError:
            finding_parts.append(f"{vendor_name}: not found in database")

    finding = " | ".join(finding_parts) if finding_parts else "No vendor data found."
    if high_risk_found:
        finding += " ⚠ Approval request created for high-risk vendor(s)."

    prev_risk = state.get("risk_level", "low")
    new_risk = "high" if high_risk_found else ("medium" if prev_risk == "low" else prev_risk)

    return {
        "tool_results": {**state.get("tool_results", {}), "vendor": all_profiles},
        "agent_outputs": {
            **state.get("agent_outputs", {}),
            AGENT_NAME: {
                "icon": "🏢",
                "finding": finding,
                "tools_called": list(dict.fromkeys(tools_called)),
            },
        },
        "risk_level": new_risk,
        "approval_required": state.get("approval_required", False) or high_risk_found,
    }
