import streamlit as st
from datetime import datetime
from database.db import execute
from services.llm import has_llm

st.markdown("""
<style>
.tool-pill { display:inline-block; background:rgba(27,82,153,0.12); color:var(--primary-color);
             border:1px solid rgba(27,82,153,0.25); border-radius:4px;
             padding:2px 10px; font-size:0.78rem; font-weight:600; margin:2px; }
.critic-box { background:rgba(234,179,8,0.07); border:1px solid rgba(234,179,8,0.3);
              border-radius:8px; padding:1rem 1.2rem; }
.step-item { background:rgba(27,82,153,0.06); border-left:3px solid var(--primary-color);
             padding:0.4rem 0.75rem; margin:0.25rem 0;
             border-radius:0 6px 6px 0; font-size:0.88rem; }
</style>
""", unsafe_allow_html=True)

st.title("⚡ Executive Command Center")

llm_active = has_llm()
if llm_active:
    st.success("LLM active — agents will use AI to classify requests and synthesize findings.", icon="🤖")
else:
    st.info(
        "Running in **rule-based mode** — no API key detected. "
        "Add `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` to `.env` to enable LLM reasoning.",
        icon="ℹ️",
    )

st.caption("Ask a business question. The LangGraph pipeline routes to specialist agents, calls real tools, validates evidence, and synthesizes a recommendation.")
st.markdown("---")

# ── Prompt selection ──────────────────────────────────────────────────────────
PROMPTS = [
    "— select a prompt or type your own —",
    "Why are South Florida communities underperforming this month?",
    "Improve South Florida sales without reducing gross margin by more than 1.5%.",
    "Which vendor approvals need escalation?",
    "What workflow should an associate follow to onboard a new subcontractor?",
]

col_in, col_btn = st.columns([4, 1])
with col_in:
    selected = st.selectbox("Sample prompts", PROMPTS, label_visibility="collapsed")
    prompt = st.text_input(
        "Or type your own",
        value="" if selected == PROMPTS[0] else selected,
        placeholder="Ask about communities, vendors, workflows...",
        label_visibility="collapsed" if selected != PROMPTS[0] else "visible",
    )
with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    run_clicked = st.button("Run Analysis", type="primary", use_container_width=True)

if not run_clicked:
    st.markdown(
        "<div style='text-align:center;opacity:0.4;padding:3rem 0;'>"
        "Select a prompt and click <strong>Run Analysis</strong> to start the LangGraph pipeline."
        "</div>",
        unsafe_allow_html=True,
    )
    st.stop()

if not prompt.strip():
    st.warning("Please enter or select a prompt.")
    st.stop()

# ── Create DB run record ──────────────────────────────────────────────────────
run_id = execute("""
    INSERT INTO agent_runs (agent_name, user_prompt, status, started_at, risk_level, approval_required)
    VALUES ('Executive Orchestrator', :prompt, 'running', :ts, 'low', 0)
""", {"prompt": prompt, "ts": datetime.now().isoformat()})

# ── Build & cache the graph ───────────────────────────────────────────────────
@st.cache_resource
def get_graph():
    from agents.graph import build_graph
    return build_graph()

graph = get_graph()

initial_state = {
    "user_prompt":        prompt,
    "run_id":             run_id,
    "prompt_type":        "",
    "selected_agents":    [],
    "tool_results":       {},
    "agent_outputs":      {},
    "validation_result":  {},
    "approval_required":  False,
    "recommended_actions": [],
    "final_response":     "",
    "risk_level":         "low",
    "audit_metadata":     {},
    "error":              None,
}

st.markdown("---")
left, right = st.columns([3, 2], gap="large")

# ── Stream the graph — left column ────────────────────────────────────────────
with left:
    st.subheader("Agent Activity Feed")
    st.caption(f"Run ID: `RUN-{run_id:04d}` · LangGraph pipeline · Tools logging to database")

    final_state = {**initial_state}
    shown_agents: set = set()

    try:
        for event in graph.stream(initial_state, stream_mode="updates"):
            for node_name, update in event.items():
                if node_name in ("__end__", "__start__"):
                    continue

                # Accumulate state updates (merging dicts additively)
                if not update:
                    continue
                for k, v in update.items():
                    if isinstance(v, dict) and isinstance(final_state.get(k), dict):
                        final_state[k] = {**final_state.get(k, {}), **v}
                    elif v is not None:
                        final_state[k] = v

                # Show each new agent output as it arrives
                new_outputs = update.get("agent_outputs", {})
                for agent_name, output in new_outputs.items():
                    if agent_name in shown_agents:
                        continue
                    shown_agents.add(agent_name)

                    icon     = output.get("icon", "•")
                    tools    = output.get("tools_called", [])
                    finding  = output.get("finding", "")

                    with st.status(f"{icon} {agent_name}...", expanded=False) as s:
                        if tools:
                            pills = " ".join(
                                f'<span class="tool-pill">{t}</span>' for t in tools
                            )
                            st.markdown(f"**Tools called:** {pills}", unsafe_allow_html=True)

                        if finding:
                            st.markdown(f"**Finding:** {finding}")

                        # Show policy steps if present (Associate Productivity)
                        if output.get("policy_steps"):
                            st.markdown("**Policy workflow:**")
                            for step in output["policy_steps"][:5]:
                                st.markdown(
                                    f'<div class="step-item">{step}</div>',
                                    unsafe_allow_html=True,
                                )

                        s.update(
                            label=f"{icon} {agent_name} — complete",
                            state="complete",
                            expanded=False,
                        )

    except Exception as e:
        st.error(f"Graph execution error: {e}")
        execute("UPDATE agent_runs SET status='failed' WHERE id=:id", {"id": run_id})

    # ── Early exit if input was rejected ─────────────────────────────────────
    if not final_state.get("input_valid", True):
        execute(
            "UPDATE agent_runs SET status='failed', completed_at=:ts WHERE id=:id",
            {"ts": datetime.now().isoformat(), "id": run_id},
        )
        st.warning(
            final_state.get("final_response",
                "This platform handles homebuilder business operations only."),
            icon="🚫",
        )
        st.stop()

    # ── Critic summary box ────────────────────────────────────────────────────
    validation = final_state.get("validation_result", {})
    risk = final_state.get("risk_level", "low")
    approval = final_state.get("approval_required", False)

    st.markdown("<br>", unsafe_allow_html=True)
    n_tools = len(validation.get("tools_used", []))
    st.markdown(f"""
    <div class="critic-box">
    <strong>🛡️ Critic / Governance Validation</strong><br><br>
    <table style="width:100%;font-size:0.9rem;">
      <tr><td style="opacity:0.55;width:55%">Evidence coverage</td>
          <td><strong>{validation.get('evidence_coverage', 'Complete')}</strong></td></tr>
      <tr><td style="opacity:0.55;">Unsupported claims</td>
          <td><strong>{validation.get('unsupported_claims', 'None')}</strong></td></tr>
      <tr><td style="opacity:0.55;">Human approval required</td>
          <td><strong>{'Yes — ' + validation.get('approval_reason','') if approval else 'No'}</strong></td></tr>
      <tr><td style="opacity:0.55;">Risk level</td>
          <td><strong>{risk.capitalize()}</strong></td></tr>
      <tr><td style="opacity:0.55;">Tool calls logged to DB</td>
          <td><strong>{n_tools} unique tools</strong></td></tr>
      <tr><td style="opacity:0.55;">LLM mode</td>
          <td><strong>{'Active' if llm_active else 'Rule-based fallback'}</strong></td></tr>
    </table>
    </div>""", unsafe_allow_html=True)

# ── Right column — summary + actions ─────────────────────────────────────────
with right:
    risk_color = {"high": "#dc2626", "medium": "#d97706", "low": "#16a34a"}.get(risk, "#6b7280")
    st.subheader("Executive Summary")
    st.markdown(
        f"<span style='background:{risk_color};color:white;border-radius:4px;"
        f"padding:2px 10px;font-size:0.82rem;font-weight:700;'>RISK: {risk.upper()}</span>"
        + (" &nbsp;<span style='background:#2563eb;color:white;border-radius:4px;"
           "padding:2px 10px;font-size:0.82rem;'>LLM</span>" if llm_active else ""),
        unsafe_allow_html=True,
    )

    if approval:
        st.warning("Human approval required before actions can execute.", icon="⚠️")

    st.markdown("<br>", unsafe_allow_html=True)
    summary = final_state.get("final_response", "Analysis complete.")
    st.markdown(summary)

    # ── Campaign preview (if generated) ──────────────────────────────────────
    campaign_output = final_state.get("agent_outputs", {}).get("Marketing Campaign Agent", {})
    if campaign_output.get("campaign"):
        with st.expander("📣 Campaign Copy Preview"):
            camp = campaign_output["campaign"]
            st.markdown("**Email Subject / Body:**")
            st.text(camp.get("email_copy", ""))
            st.markdown("**Ad Copy:**")
            st.markdown(f"> {camp.get('ad_copy', '')}")
            st.markdown("**SMS:**")
            st.markdown(f"> {camp.get('sms_copy', '')}")

    # ── Recommended actions ───────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("Recommended Actions")
    actions = final_state.get("recommended_actions", [])
    created_aprs = final_state.get("audit_metadata", {}).get("created_aprs", [])

    if not actions:
        st.info("No specific actions generated.")
    else:
        for i, rec in enumerate(actions, 1):
            r   = rec.get("risk", "low")
            bg  = {"high": "rgba(220,38,38,0.1)", "medium": "rgba(217,119,6,0.1)", "low": "rgba(22,163,74,0.1)"}.get(r, "rgba(0,0,0,0.05)")
            bc  = {"high": "rgba(220,38,38,0.4)", "medium": "rgba(217,119,6,0.4)", "low": "rgba(22,163,74,0.4)"}.get(r, "rgba(0,0,0,0.15)")
            tag = (
                f" &nbsp;<span style='font-size:0.78rem;opacity:0.6;'>→ Approver: {rec['approver']}</span>"
                if rec.get("requires_approval")
                else " &nbsp;<span style='font-size:0.78rem;color:#16a34a;font-weight:600;'>Auto-proceed</span>"
            )
            st.markdown(
                f"<div style='background:{bg};border:1px solid {bc};border-radius:8px;padding:0.65rem 1rem;margin-bottom:0.4rem;'>"
                f"<strong>{i}.</strong> {rec['action']}{tag}</div>",
                unsafe_allow_html=True,
            )

    # ── APR notice ────────────────────────────────────────────────────────────
    if created_aprs:
        st.success(
            f"**{len(created_aprs)} approval request(s) created** and routed to the Approval Queue: "
            + ", ".join(f"`{a}`" for a in created_aprs),
            icon="📋",
        )

    # ── Run-level approval buttons ────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    from tools.audit_tools import log_audit_event
    if approval:
        st.markdown("**Approve entire run**")
        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("✅ Approve All", type="primary", use_container_width=True):
                execute(
                    "UPDATE agent_runs SET status='completed', risk_level=:r, approval_required=0 WHERE id=:id",
                    {"r": risk, "id": run_id},
                )
                log_audit_event("approval_decision", f"RUN-{run_id:04d} approved by user",
                                actor="user", risk_level=risk, approval_status="approved")
                st.success("Run approved. Individual APRs remain in the queue for per-action decisions.")
        with b2:
            if st.button("❌ Reject All", use_container_width=True):
                execute("UPDATE agent_runs SET status='failed' WHERE id=:id", {"id": run_id})
                log_audit_event("approval_decision", f"RUN-{run_id:04d} rejected by user",
                                actor="user", risk_level=risk, approval_status="rejected")
                st.error("Run rejected. Logged to audit trail.")
        with b3:
            if st.button("⬆️ Escalate", use_container_width=True):
                log_audit_event("escalation_triggered", f"RUN-{run_id:04d} escalated by user",
                                actor="user", risk_level=risk, approval_status="escalated")
                st.warning("Escalated to senior approver.")
    else:
        execute("UPDATE agent_runs SET status='completed', risk_level=:r WHERE id=:id",
                {"r": risk, "id": run_id})
        st.info("No human approval required for this run.")

    st.markdown("---")
    st.caption(
        f"Run ID: `RUN-{run_id:04d}` · "
        f"Agents: {len(shown_agents)} · "
        f"APRs created: {len(created_aprs)} · "
        f"View trace in Audit Trail"
    )
