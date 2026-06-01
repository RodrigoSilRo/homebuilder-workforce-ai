from typing import TypedDict


class AgentState(TypedDict, total=False):
    # Input
    user_prompt: str
    run_id: int

    # Classification
    prompt_type: str          # sales_ops | incentive | vendor | workflow | general
    selected_agents: list     # which specialist agents should run

    # Data collected by specialist agents
    tool_results: dict        # raw tool outputs keyed by tool name
    agent_outputs: dict       # per-agent findings: {agent_name: {icon, finding, tools_called}}

    # Governance
    validation_result: dict   # critic output: evidence_coverage, risk_level, etc.
    approval_required: bool
    risk_level: str           # low | medium | high

    # Final output
    recommended_actions: list # [{action, risk, requires_approval, approver}]
    final_response: str       # executive summary (LLM-generated or rule-based)

    # Metadata
    audit_metadata: dict
    error: str
