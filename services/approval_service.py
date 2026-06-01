"""
Approval Service — escalation rules engine.

Rules (from spec):
- Contract value > $50,000        → human approval required
- Margin impact > 1.0%            → VP Sales approval
- Customer-facing campaign        → Marketing Director approval
- Vendor insurance expired/missing → VP Procurement, block until resolved
- Construction delay > 10 closings → auto-escalate to VP Operations
- Pending > 24 hours              → escalate to senior approver
"""
from datetime import datetime, timedelta
from database.db import query, execute
from tools.audit_tools import log_audit_event

ESCALATION_HOURS = 24

ESCALATION_MAP = {
    "VP Sales":                    "CFO",
    "Regional Marketing Director": "VP Marketing",
    "VP Procurement":              "COO",
    "Regional Operations Manager": "VP Operations",
    "Sales Director":              "VP Sales",
}


def check_and_escalate_overdue() -> list[dict]:
    """
    Find pending APRs older than ESCALATION_HOURS and escalate them.
    Returns list of escalated request IDs.
    """
    cutoff = (datetime.now() - timedelta(hours=ESCALATION_HOURS)).isoformat()
    overdue = query("""
        SELECT id, agent_name, recommended_action, risk_level, required_approver, created_at
        FROM approval_requests
        WHERE status = 'pending' AND created_at < :cutoff
    """, {"cutoff": cutoff})

    escalated = []
    for req in overdue:
        new_approver = ESCALATION_MAP.get(req["required_approver"], "COO")
        execute("""
            UPDATE approval_requests
            SET status = 'escalated',
                required_approver = :approver,
                decided_at = :now,
                decision_reason = 'Auto-escalated: pending > 24 hours'
            WHERE id = :id
        """, {"approver": new_approver, "now": datetime.now().isoformat(), "id": req["id"]})

        log_audit_event(
            "escalation_triggered",
            f"{req['id']} auto-escalated to {new_approver} — pending > {ESCALATION_HOURS}h",
            actor="approval_service",
            agent_name=req["agent_name"],
            risk_level=req["risk_level"],
            approval_status="escalated",
        )
        escalated.append(req["id"])

    return escalated


def get_overdue_requests() -> list[dict]:
    """Return pending APRs that have exceeded the escalation threshold."""
    cutoff = (datetime.now() - timedelta(hours=ESCALATION_HOURS)).isoformat()
    return query("""
        SELECT id, agent_name, recommended_action, risk_level, required_approver, created_at
        FROM approval_requests
        WHERE status = 'pending' AND created_at < :cutoff
        ORDER BY created_at ASC
    """, {"cutoff": cutoff})


def hours_pending(created_at_str: str) -> float:
    """Return how many hours an APR has been pending."""
    try:
        created = datetime.fromisoformat(created_at_str)
        return (datetime.now() - created).total_seconds() / 3600
    except Exception:
        return 0.0


def apply_approval_rules(
    contract_value: float = 0,
    margin_impact_pct: float = 0,
    is_customer_facing: bool = False,
    vendor_insurance_status: str = "current",
    closings_affected: int = 0,
) -> dict:
    """
    Evaluate approval rules and return routing decision.
    Used by the Vendor Approval and Finance agents to pre-validate.
    """
    flags       = []
    approver    = "Sales Director"
    risk_level  = "low"
    blocked     = False

    if vendor_insurance_status != "current":
        flags.append("Vendor insurance not current — block until resolved")
        approver   = "VP Procurement"
        risk_level = "high"
        blocked    = True

    if closings_affected > 10:
        flags.append(f"Construction delay affects {closings_affected} closings — VP Operations required")
        approver   = "VP Operations"
        risk_level = "high"

    if contract_value > 200_000:
        flags.append("Contract > $200K — VP Procurement required")
        approver   = "VP Procurement"
        risk_level = "high"
    elif contract_value > 50_000:
        flags.append("Contract > $50K — Regional Ops Manager required")
        if risk_level == "low":
            approver   = "Regional Operations Manager"
            risk_level = "medium"

    if abs(margin_impact_pct) > 1.5:
        flags.append("Margin impact > 1.5% — blocked by policy")
        blocked    = True
        risk_level = "high"
    elif abs(margin_impact_pct) > 1.0:
        flags.append("Margin impact > 1.0% — CFO approval required")
        approver   = "CFO"
        risk_level = "high"
    elif abs(margin_impact_pct) > 0.5:
        flags.append("Margin impact > 0.5% — VP Sales approval required")
        approver   = "VP Sales"
        if risk_level == "low":
            risk_level = "medium"

    if is_customer_facing:
        flags.append("Customer-facing action — Marketing Director sign-off required")

    return {
        "requires_approval": len(flags) > 0,
        "blocked": blocked,
        "approver": approver,
        "risk_level": risk_level,
        "flags": flags,
    }
