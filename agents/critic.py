"""
Critic / Governance Agent — validates evidence, enforces policies, assigns risk level.
Always runs as the final specialist step before response synthesis.
"""
from agents.state import AgentState
from tools.audit_tools import log_audit_event

AGENT_NAME = "Critic / Governance Agent"

# Governance rules
APPROVAL_TRIGGERS = [
    ("incentive",           lambda tr: any(
        not r.get("blocked_by_policy") and abs(r.get("margin_impact_pct", 0)) >= 1.0
        for r in (tr.get("incentive") or {}).values()
    )),
    ("vendor_high_risk",    lambda tr: any(
        d.get("profile", {}).get("risk_level") == "high"
        for d in (tr.get("vendor") or {}).values()
    )),
    ("vendor_insurance",    lambda tr: any(
        d.get("profile", {}).get("insurance_status") != "current"
        for d in (tr.get("vendor") or {}).values()
    )),
    ("construction_10plus", lambda tr: (tr.get("construction_delays") or {}).get("total_affected_closings", 0) > 10),
    ("campaign",            lambda tr: "campaign" in tr),
]

RISK_ELEVATORS = {
    "vendor_high_risk":    "high",
    "vendor_insurance":    "high",
    "construction_10plus": "high",
    "incentive":           "medium",
    "campaign":            "low",
}


def validate(state: AgentState) -> dict:
    outputs = state.get("agent_outputs", {})
    tool_results = state.get("tool_results", {})

    # Count evidence
    agents_with_findings = [a for a, o in outputs.items() if o.get("finding") and a != AGENT_NAME]
    tools_used = []
    for out in outputs.values():
        tools_used.extend(out.get("tools_called", []))

    evidence_complete = len(agents_with_findings) > 0 and len(tools_used) > 0

    # Check unsupported claims (simple heuristic: any agent found something without tools)
    agents_without_tools = [a for a, o in outputs.items()
                             if a not in ("Executive Orchestrator", AGENT_NAME) and not o.get("tools_called")]
    unsupported = len(agents_without_tools) > 0

    # Evaluate approval triggers
    triggered = [name for name, fn in APPROVAL_TRIGGERS if fn(tool_results)]
    approval_required = len(triggered) > 0

    # Determine risk level
    risk = state.get("risk_level", "low")
    for trigger in triggered:
        level = RISK_ELEVATORS.get(trigger, "low")
        if level == "high":
            risk = "high"
            break
        if level == "medium" and risk == "low":
            risk = "medium"

    # Approval reason
    approval_reason = (
        f"Required: {', '.join(triggered)}" if triggered
        else "No approval required"
    )

    validation = {
        "evidence_coverage": "Complete" if evidence_complete else "Incomplete",
        "agents_with_evidence": agents_with_findings,
        "tools_used": list(set(tools_used)),
        "tool_call_count": len(tools_used),
        "unsupported_claims": "Detected" if unsupported else "None",
        "approval_required": approval_required,
        "approval_reason": approval_reason,
        "risk_level": risk,
    }

    finding = (
        f"Evidence: {'complete' if evidence_complete else 'incomplete'} ({len(tools_used)} tool calls). "
        f"Unsupported claims: {'detected — flagging' if unsupported else 'none'}. "
        f"Approval required: {'YES — ' + approval_reason if approval_required else 'No'}. "
        f"Risk level: **{risk.upper()}**."
    )

    log_audit_event(
        "validation_complete",
        f"Critic validated: evidence={validation['evidence_coverage']}, risk={risk}, approval={approval_required}",
        actor=AGENT_NAME, agent_name=AGENT_NAME,
        risk_level=risk,
        approval_status="pending" if approval_required else "n/a",
    )

    return {
        "validation_result": validation,
        "risk_level": risk,
        "approval_required": approval_required,
        "agent_outputs": {
            **state.get("agent_outputs", {}),
            AGENT_NAME: {
                "icon": "🛡️",
                "finding": finding,
                "tools_called": [],
            },
        },
    }
