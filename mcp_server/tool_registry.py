"""
MCP Tool Registry — maps tool names to Python functions and defines their schemas.
Used by server.py to register tools with FastMCP.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Optional


# ── Tool function imports (lazy, inside functions to keep startup fast) ────────

def _community():
    from tools.community_tools import get_community_metrics, get_inventory_status, get_lead_conversion
    return get_community_metrics, get_inventory_status, get_lead_conversion

def _construction():
    from tools.construction_tools import get_construction_delays
    return get_construction_delays

def _finance():
    from tools.finance_tools import calculate_incentive_impact
    return calculate_incentive_impact

def _vendor():
    from tools.vendor_tools import get_vendor_profile, get_vendor_risk_score
    return get_vendor_profile, get_vendor_risk_score

def _policy():
    from tools.policy_tools import get_policy_workflow
    return get_policy_workflow

def _approval():
    from tools.approval_tools import create_approval_request
    return create_approval_request

def _marketing():
    from tools.marketing_tools import generate_marketing_campaign
    return generate_marketing_campaign

def _audit():
    from tools.audit_tools import create_executive_report
    return create_executive_report


# ── Tool implementations (registered with FastMCP in server.py) ───────────────

def tool_get_community_metrics(region: Optional[str] = None, community_name: Optional[str] = None) -> dict:
    """
    Returns sales performance metrics for homebuilding communities.
    Includes target vs. actual monthly sales, variance %, average days on market,
    gross margin, stale home count, and lead conversion rate.
    Filter by region (e.g. 'South Florida', 'Texas') or exact community name.
    """
    fn, _, _ = _community()
    return fn(region=region, community_name=community_name, agent_name="mcp_client")


def tool_get_inventory_status(community_name: str, stale_days_threshold: int = 60) -> dict:
    """
    Returns active home inventory for a community.
    Includes stale homes (over threshold days on market), price bands,
    average gross margin, and completion status breakdown.
    """
    _, fn, _ = _community()
    return fn(community_name=community_name, stale_days_threshold=stale_days_threshold, agent_name="mcp_client")


def tool_get_lead_conversion(community_name: Optional[str] = None, region: Optional[str] = None, days_back: int = 30) -> dict:
    """
    Returns lead funnel data including volume, conversion rate %, and source breakdown.
    Filter by community name or region. days_back sets the lookback window (default 30).
    """
    _, _, fn = _community()
    return fn(community_name=community_name, region=region, days_back=days_back, agent_name="mcp_client")


def tool_get_construction_delays(community_name: Optional[str] = None, severity: Optional[str] = None) -> dict:
    """
    Returns active construction delays with severity, affected lot count, responsible parties,
    and estimated delay duration. severity filter: low | medium | high | critical.
    Includes total affected closings and whether escalation is required (>10 closings).
    """
    fn = _construction()
    return fn(community_name=community_name, severity=severity, agent_name="mcp_client")


def tool_calculate_incentive_impact(community_name: str, incentive_pct: float) -> dict:
    """
    Models the revenue and gross margin impact of a proposed incentive percentage on a community.
    Returns: homes targeted, revenue base, incentive cost, margin impact %,
    whether the scenario is blocked by policy (>1.5% limit), and required approval level.
    """
    fn = _finance()
    return fn(community_name=community_name, incentive_pct=incentive_pct, agent_name="mcp_client")


def tool_get_vendor_profile(vendor_name: str) -> dict:
    """
    Returns vendor profile including category, insurance status, risk score (0-100),
    payment history score, active contract value, and compliance flags.
    Flags contracts > $50K and expired/missing insurance automatically.
    """
    fn, _ = _vendor()
    return fn(vendor_name=vendor_name, agent_name="mcp_client")


def tool_get_vendor_risk_score(vendor_name: str) -> dict:
    """
    Returns composite vendor risk assessment: risk score, risk level (low/medium/high),
    individual risk factors, payment history score, and approval recommendation.
    """
    _, fn = _vendor()
    return fn(vendor_name=vendor_name, agent_name="mcp_client")


def tool_get_policy_workflow(policy_name: Optional[str] = None, business_process: Optional[str] = None) -> dict:
    """
    Returns the step-by-step workflow for a business process or named policy.
    Includes required approvers, approval thresholds, and escalation rules.
    Search by policy title (e.g. 'Vendor Onboarding') or business process description.
    """
    fn = _policy()
    return fn(policy_name=policy_name, business_process=business_process, agent_name="mcp_client")


def tool_create_approval_request(
    recommended_action: str,
    risk_level: str,
    required_approver: str,
    community: Optional[str] = None,
) -> dict:
    """
    Creates a human-in-the-loop approval request and routes it to the specified approver.
    risk_level: low | medium | high.
    Returns the approval_request_id, status, and routing confirmation.
    The request appears immediately in the Approval Queue UI.
    """
    fn = _approval()
    return fn(
        recommended_action=recommended_action,
        risk_level=risk_level,
        required_approver=required_approver,
        community=community,
        agent_name="mcp_client",
    )


def tool_generate_marketing_campaign(community_name: str, target_audience: str, objective: str) -> dict:
    """
    Generates a complete campaign brief, email copy, ad copy, and SMS copy for a community.
    objective examples: 'Move stale inventory', 'Improve lead conversion rate'.
    All generated content requires human approval before launch.
    """
    fn = _marketing()
    return fn(community_name=community_name, target_audience=target_audience, objective=objective, agent_name="mcp_client")


def tool_create_executive_report(run_id: int, risk_level: str = "medium", approval_required: bool = True) -> dict:
    """
    Synthesizes agent outputs into a structured executive report.
    Logs the report generation to the audit trail.
    Returns a summary, key findings, recommended actions, and governance metadata.
    """
    fn = _audit()
    return fn(
        agent_run_id=run_id,
        findings=["Analysis complete via MCP client"],
        recommendations=["Review findings and take action"],
        risk_level=risk_level,
        approval_required=approval_required,
    )


# ── Registry metadata (used by the Streamlit MCP Tool Registry page) ──────────

REGISTERED_TOOLS = [
    "get_community_metrics",
    "get_inventory_status",
    "get_lead_conversion",
    "get_construction_delays",
    "calculate_incentive_impact",
    "get_vendor_profile",
    "get_vendor_risk_score",
    "get_policy_workflow",
    "create_approval_request",
    "generate_marketing_campaign",
    "create_executive_report",
]
