import json
import streamlit as st
import pandas as pd
from tools.audit_tools import get_audit_events
from database.db import query

st.title("📋 Audit Trail")
st.caption("Complete, tamper-evident log of every agent action, tool call, approval decision, and escalation — sourced live from the database.")
st.markdown("---")

# ── Summary metrics ────────────────────────────────────────────────────────────
@st.cache_data(ttl=5)
def load_summary():
    return query("""
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN event_type = 'tool_called' THEN 1 ELSE 0 END) AS tool_calls,
            SUM(CASE WHEN event_type = 'approval_decision' THEN 1 ELSE 0 END) AS decisions,
            SUM(CASE WHEN event_type = 'escalation_triggered' THEN 1 ELSE 0 END) AS escalations,
            SUM(CASE WHEN risk_level = 'high' THEN 1 ELSE 0 END) AS high_risk
        FROM audit_events
    """)

summary = load_summary()
if summary:
    s = summary[0]
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Events",    s["total"])
    c2.metric("Tool Calls",      s["tool_calls"])
    c3.metric("Decisions",       s["decisions"])
    c4.metric("Escalations",     s["escalations"])
    c5.metric("High-Risk Events",s["high_risk"])
    st.markdown("---")

# ── Filters ───────────────────────────────────────────────────────────────────
all_events = get_audit_events(limit=300)

agents      = sorted({e["agent_name"] for e in all_events if e["agent_name"] and e["agent_name"] != "n/a"})
event_types = sorted({e["event_type"]  for e in all_events if e["event_type"]})

f1, f2, f3, f4 = st.columns(4)
with f1:
    agent_f  = st.selectbox("Agent",          ["All"] + agents)
with f2:
    etype_f  = st.selectbox("Event Type",     ["All"] + event_types)
with f3:
    risk_f   = st.selectbox("Risk Level",     ["All", "high", "medium", "low"])
with f4:
    status_f = st.selectbox("Approval Status",["All", "pending", "approved", "rejected", "escalated", "n/a"])

filtered = [
    e for e in all_events
    if (agent_f  == "All" or e["agent_name"]      == agent_f)
    and (etype_f == "All" or e["event_type"]       == etype_f)
    and (risk_f  == "All" or e["risk_level"]       == risk_f)
    and (status_f== "All" or e["approval_status"]  == status_f)
]

st.markdown(f"**{len(filtered)} event{'s' if len(filtered) != 1 else ''} shown** (of {len(all_events)} total) · Click any row to expand details")
st.markdown("<br>", unsafe_allow_html=True)

# ── Color maps ─────────────────────────────────────────────────────────────────
RISK_COLORS   = {"high": "#dc2626", "medium": "#d97706", "low": "#16a34a"}
STATUS_COLORS = {
    "approved":  ("rgba(22,163,74,0.1)",   "#16a34a"),
    "rejected":  ("rgba(220,38,38,0.1)",   "#dc2626"),
    "escalated": ("rgba(124,58,237,0.1)",  "#7c3aed"),
    "pending":   ("rgba(217,119,6,0.1)",   "#d97706"),
    "n/a":       ("rgba(128,128,128,0.1)", "#6b7280"),
}
EVENT_ICONS = {
    "agent_run_started":    "▶",
    "agent_run_completed":  "✓",
    "tool_called":          "⚙",
    "approval_requested":   "⏳",
    "approval_decision":    "✓",
    "escalation_triggered": "↑",
    "policy_enforced":      "◈",
    "validation_complete":  "◎",
    "info_requested":       "?",
}

for event in filtered:
    rc        = RISK_COLORS.get(event["risk_level"], "#6b7280")
    sbg, stc  = STATUS_COLORS.get(event["approval_status"], ("rgba(128,128,128,0.1)", "#6b7280"))
    eicon     = EVENT_ICONS.get(event["event_type"], "·")

    meta = {}
    try:
        meta = json.loads(event.get("metadata_json") or "{}")
    except Exception:
        pass

    label = (
        f"{eicon} &nbsp;`{event['event_type']}` &nbsp;·&nbsp; "
        f"**{event['agent_name']}** &nbsp;·&nbsp; "
        f"{event['timestamp'][:16]}"
    )

    with st.expander(label, expanded=False):
        rl, rr = st.columns([5, 2])
        with rl:
            st.markdown(
                f"**{event['id']}** &nbsp;·&nbsp;"
                f"<span style='color:{rc};font-weight:700;font-size:0.8rem;'> RISK: {event['risk_level'].upper()}</span>"
                f" &nbsp;"
                f"<span style='background:{sbg};color:{stc};border-radius:4px;"
                f"padding:1px 8px;font-size:0.75rem;font-weight:600;'>{event['approval_status'].upper()}</span>",
                unsafe_allow_html=True,
            )
            st.markdown(f"**Actor:** {event['actor']} &nbsp;·&nbsp; **Agent:** {event['agent_name']}")
        with rr:
            st.markdown(
                f"<div style='opacity:0.5;font-size:0.83rem;text-align:right;'>{event['timestamp']}</div>",
                unsafe_allow_html=True,
            )

        st.markdown(event["description"])

        # ── Rich metadata for agent_run_completed ─────────────────────────────
        if meta and event["event_type"] == "agent_run_completed":
            st.markdown("---")

            if meta.get("prompt"):
                st.markdown(
                    f"<div style='background:rgba(27,82,153,0.06);border-left:3px solid var(--primary-color);"
                    f"padding:0.4rem 0.75rem;border-radius:0 4px 4px 0;font-size:0.9rem;margin-bottom:0.75rem;'>"
                    f"<span style='opacity:0.55;font-size:0.75rem;text-transform:uppercase;letter-spacing:1px;'>Prompt</span><br>"
                    f"{meta['prompt']}</div>",
                    unsafe_allow_html=True,
                )

            cols_meta = st.columns([1, 1])
            with cols_meta[0]:
                if meta.get("agents_activated"):
                    st.markdown("**Agents activated**")
                    for a in meta["agents_activated"]:
                        st.markdown(f"- {a}")

            with cols_meta[1]:
                if meta.get("validation"):
                    v = meta["validation"]
                    st.markdown("**Governance validation**")
                    st.markdown(f"- Evidence: **{v.get('evidence_coverage', '—')}**")
                    st.markdown(f"- Unsupported claims: **{v.get('unsupported_claims', '—')}**")
                    if v.get("tools_used"):
                        st.markdown(f"- Tools used: {', '.join(v['tools_used'])}")
                    if v.get("approval_reason"):
                        st.markdown(f"- Approval: {v['approval_reason']}")

            if meta.get("agent_findings"):
                st.markdown("**Agent findings**")
                for agent_name, fd in meta["agent_findings"].items():
                    tools = fd.get("tools_called", [])
                    tools_str = (
                        " &nbsp;" + " ".join(
                            f"<span style='background:rgba(27,82,153,0.1);color:var(--primary-color);"
                            f"border-radius:3px;padding:1px 7px;font-size:0.74rem;font-weight:600;'>{t}</span>"
                            for t in tools
                        ) if tools else ""
                    )
                    st.markdown(
                        f"<div style='margin:0.35rem 0;'>"
                        f"<span style='font-weight:700;font-size:0.88rem;'>{agent_name}</span>{tools_str}</div>",
                        unsafe_allow_html=True,
                    )
                    if fd.get("finding"):
                        st.markdown(
                            f"<div style='background:rgba(128,128,128,0.06);border-left:3px solid rgba(128,128,128,0.25);"
                            f"padding:0.35rem 0.7rem;margin:0.1rem 0 0.5rem 0;border-radius:0 4px 4px 0;"
                            f"font-size:0.86rem;opacity:0.85;'>{fd['finding']}</div>",
                            unsafe_allow_html=True,
                        )

            if meta.get("recommended_actions"):
                st.markdown("**Recommended actions**")
                for rec in meta["recommended_actions"]:
                    r     = rec.get("risk", "low")
                    rc2   = RISK_COLORS.get(r, "#6b7280")
                    appr  = f" → Approver: {rec['approver']}" if rec.get("requires_approval") else " → Auto-proceed"
                    st.markdown(
                        f"<span style='color:{rc2};font-weight:700;font-size:0.78rem;'>[{r.upper()}]</span> "
                        f"{rec.get('action','')}"
                        f"<span style='opacity:0.5;font-size:0.82rem;'>{appr}</span>",
                        unsafe_allow_html=True,
                    )

            if meta.get("final_response"):
                st.markdown("**Executive summary**")
                st.info(meta["final_response"])

            if meta.get("created_aprs"):
                st.caption(f"APRs created: {', '.join(meta['created_aprs'])}")

st.markdown("---")

col_a, col_b = st.columns(2)
with col_a:
    if st.button("🔄 Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
with col_b:
    if filtered:
        df = pd.DataFrame(filtered)
        df = df.drop(columns=["metadata_json"], errors="ignore")
        st.download_button(
            "⬇️ Download CSV",
            data=df.to_csv(index=False),
            file_name="audit_trail.csv",
            mime="text/csv",
            use_container_width=True,
        )

st.caption("Every agent run, tool call, and approval decision is written here in real time. Immutable — no deletes.")
