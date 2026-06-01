"""
Executive Orchestrator — three graph nodes:
  classify_node       → classifies request, selects agents
  generate_response_node → LLM synthesis of all agent findings
  finalize_node       → writes run record to DB, logs audit event
"""
from datetime import datetime

from agents.state import AgentState
from services.llm import chat, has_llm
from tools.audit_tools import log_audit_event
from database.db import execute

# ── Agent routing map ─────────────────────────────────────────────────────────

AGENT_MAP = {
    "sales_ops":  ["Community Performance Agent", "Construction Delay Agent", "Marketing Campaign Agent"],
    "incentive":  ["Community Performance Agent", "Finance / Incentive Agent", "Marketing Campaign Agent"],
    "vendor":     ["Vendor Approval Agent"],
    "workflow":   ["Associate Productivity Agent"],
    "general":    ["Community Performance Agent", "Construction Delay Agent"],
}

# ── Node: classify_request ────────────────────────────────────────────────────

def classify_node(state: AgentState) -> dict:
    prompt = state["user_prompt"]
    p = prompt.lower()

    # Rule-based classification (always runs; LLM can override)
    # Question-style prompts ("what workflow", "how do I") → workflow, regardless of other keywords
    if any(k in p for k in ["what workflow", "how do i", "how to", "what steps", "what process", "what should"]):
        ptype = "workflow"
    elif any(k in p for k in ["vendor", "insurance", "coastal", "onboard vendor"]):
        ptype = "vendor"
    elif any(k in p for k in ["workflow", "policy", "onboard", "associate", "subcontract"]):
        ptype = "workflow"
    elif any(k in p for k in ["margin", "incentive", "discount", "improve sales", "without reducing"]):
        ptype = "incentive"
    else:
        ptype = "sales_ops"

    # LLM classification override
    if has_llm():
        llm_result = chat(
            system=(
                "Classify the user request into EXACTLY one category. "
                "Respond with only the category word, nothing else.\n"
                "Categories: sales_ops, incentive, vendor, workflow, general\n"
                "sales_ops = about community performance, sales metrics, or underperformance\n"
                "incentive = about pricing, discounts, or improving sales within margin constraints\n"
                "vendor = about vendor approval, onboarding, or risk review\n"
                "workflow = about how to do something, policies, or step-by-step guidance\n"
                "general = anything else"
            ),
            user=prompt,
        )
        if llm_result and llm_result.strip() in AGENT_MAP:
            ptype = llm_result.strip()

    selected = AGENT_MAP.get(ptype, AGENT_MAP["sales_ops"])

    log_audit_event(
        "agent_run_started",
        f"Graph initiated — type: {ptype} | agents: {', '.join(selected)}",
        actor="Executive Orchestrator",
        agent_name="Executive Orchestrator",
        risk_level="low",
    )

    return {
        "prompt_type": ptype,
        "selected_agents": selected,
        "tool_results": {},
        "agent_outputs": {
            "Executive Orchestrator": {
                "icon": "🎯",
                "finding": (
                    f"Request classified as **{ptype}**. "
                    f"{'LLM routing active.' if has_llm() else 'Rule-based routing (no LLM key configured).'} "
                    f"Activating: {', '.join(selected)}."
                ),
                "tools_called": [],
            }
        },
        "validation_result": {},
        "recommended_actions": [],
        "approval_required": False,
        "risk_level": "low",
    }


# ── Node: generate_response ────────────────────────────────────────────────────

def generate_response_node(state: AgentState) -> dict:
    outputs = state.get("agent_outputs", {})
    tool_results = state.get("tool_results", {})
    prompt = state["user_prompt"]
    validation = state.get("validation_result", {})

    # Build context from agent findings (exclude orchestrator itself)
    finding_lines = [
        f"[{agent}] {out['finding']}"
        for agent, out in outputs.items()
        if agent != "Executive Orchestrator" and out.get("finding")
    ]
    context = "\n".join(finding_lines)

    # LLM synthesis
    summary = None
    if has_llm() and context:
        summary = chat(
            system=(
                "You are a senior executive analyst at a national homebuilder. "
                "Using the agent findings provided, write a concise 3-4 sentence executive summary. "
                "Be specific with data points (numbers, percentages, names). "
                "State the key problem, root cause, and recommended direction. "
                "Do not add claims not supported by the findings. "
                "Do not use bullet points — write flowing prose."
            ),
            user=f"Business question: {prompt}\n\nAgent findings:\n{context}",
        )

    # Rule-based fallback
    if not summary:
        if finding_lines:
            summary = "Analysis complete. " + " ".join(
                line.split("] ", 1)[-1].split(".")[0] + "."
                for line in finding_lines[:3]
            )
        else:
            summary = "Analysis complete. See agent findings for details."

    # Build recommended actions from tool results
    actions = _build_actions(state)

    return {
        "final_response": summary,
        "recommended_actions": actions,
    }


def _build_actions(state: AgentState) -> list:
    tr = state.get("tool_results", {})
    actions = []

    if "incentive" in tr:
        r125 = tr["incentive"].get("1.25", {})
        if r125 and not r125.get("blocked_by_policy"):
            actions.append({
                "action": f"Apply 1.25% incentive on {r125.get('homes_targeted', 0)} stale Coral Bay homes",
                "risk": "medium", "requires_approval": True, "approver": "VP Sales",
            })

    if "campaign" in tr:
        actions.append({
            "action": "Launch 'Move In This Summer' digital campaign — email + social",
            "risk": "low", "requires_approval": True, "approver": "Regional Marketing Director",
        })

    if "construction_delays" in tr:
        n = tr["construction_delays"].get("total_affected_closings", 0)
        if n > 0:
            actions.append({
                "action": f"Escalate construction delays — {n} closings at risk",
                "risk": "high", "requires_approval": False, "approver": "Auto-escalated",
            })

    if "vendor" in tr:
        # tr["vendor"] is {vendor_name: {profile: {...}, risk: {...}}}
        for vendor_name, vdata in tr["vendor"].items():
            profile = vdata.get("profile", {})
            if profile.get("risk_level") == "high":
                actions.append({
                    "action": f"Block {vendor_name} — resolve insurance and risk issues before approval",
                    "risk": "high", "requires_approval": True, "approver": "VP Procurement",
                })

    if "policy" in tr:
        pol = (tr["policy"].get("policies") or [{}])[0]
        actions.append({
            "action": f"Follow {pol.get('title', 'policy')} — confirm contract value for correct approval routing",
            "risk": "low", "requires_approval": False, "approver": "n/a",
        })

    if not actions:
        actions.append({
            "action": "Review agent findings and align on next steps with your team",
            "risk": "low", "requires_approval": False, "approver": "n/a",
        })

    return actions


# ── Node: finalize ────────────────────────────────────────────────────────────

def finalize_node(state: AgentState) -> dict:
    from tools.approval_tools import create_approval_request

    risk     = state.get("risk_level", "low")
    approval = state.get("approval_required", False)
    run_id   = state.get("run_id")
    actions  = state.get("recommended_actions", [])
    tr       = state.get("tool_results", {})

    # Detect community from tool results
    comms = tr.get("community_metrics", {}).get("communities", [])
    under = [c for c in comms if not c.get("on_target")]
    community = under[0]["name"] if under else None

    # Create one approval_request per action that requires it
    created_aprs = []
    for rec in actions:
        if not rec.get("requires_approval"):
            continue
        try:
            result = create_approval_request(
                recommended_action=rec["action"],
                risk_level=rec["risk"],
                required_approver=rec["approver"],
                agent_run_id=run_id,
                community=community,
                flags=[f"Risk: {rec['risk']}", f"Approver: {rec['approver']}"],
                agent_name="Executive Orchestrator",
                run_id=run_id,
            )
            created_aprs.append(result["approval_request_id"])
            log_audit_event(
                "approval_requested",
                f"APR created: {result['approval_request_id']} — {rec['action'][:60]}",
                actor="Executive Orchestrator",
                agent_name="Executive Orchestrator",
                risk_level=rec["risk"],
                approval_status="pending",
            )
        except Exception:
            pass

    final_response = state.get("final_response", "")
    outputs        = state.get("agent_outputs", {})
    validation     = state.get("validation_result", {})

    if run_id:
        execute(
            "UPDATE agent_runs SET status='completed', risk_level=:r, approval_required=:a, "
            "completed_at=:ts, final_response=:resp WHERE id=:id",
            {
                "r": risk, "a": 1 if approval else 0,
                "ts": datetime.now().isoformat(),
                "resp": final_response, "id": run_id,
            },
        )

    log_audit_event(
        "agent_run_completed",
        f"Graph run complete — risk: {risk}, {len(created_aprs)} approval request(s) created",
        actor="Executive Orchestrator",
        agent_name="Executive Orchestrator",
        risk_level=risk,
        approval_status="pending" if approval else "n/a",
        metadata={
            "prompt":       state.get("user_prompt", ""),
            "prompt_type":  state.get("prompt_type", ""),
            "agents_activated": state.get("selected_agents", []),
            "agent_findings": {
                name: {
                    "finding":      out.get("finding", ""),
                    "tools_called": out.get("tools_called", []),
                }
                for name, out in outputs.items()
                if out.get("finding") and name != "Executive Orchestrator"
            },
            "validation": {
                "evidence_coverage":  validation.get("evidence_coverage", ""),
                "tools_used":         validation.get("tools_used", []),
                "unsupported_claims": validation.get("unsupported_claims", ""),
                "approval_reason":    validation.get("approval_reason", ""),
            },
            "recommended_actions": [
                {
                    "action":            r["action"],
                    "risk":              r["risk"],
                    "approver":          r.get("approver", "n/a"),
                    "requires_approval": r.get("requires_approval", False),
                }
                for r in actions
            ],
            "created_aprs":   created_aprs,
            "final_response": final_response,
        },
    )

    return {
        "audit_metadata": {
            "completed": True,
            "risk_level": risk,
            "approval_required": approval,
            "created_aprs": created_aprs,
        }
    }
