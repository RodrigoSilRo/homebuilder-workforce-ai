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

st.markdown(f"**{len(filtered)} event{'s' if len(filtered) != 1 else ''} shown** (of {len(all_events)} total in database)")
st.markdown("<br>", unsafe_allow_html=True)

# ── Color maps ─────────────────────────────────────────────────────────────────
RISK_COLORS   = {"high": "#dc2626", "medium": "#d97706", "low": "#16a34a"}
STATUS_COLORS = {
    "approved":  ("#dcfce7", "#166534"),
    "rejected":  ("#fee2e2", "#991b1b"),
    "escalated": ("#ede9fe", "#5b21b6"),
    "pending":   ("#fef3c7", "#92400e"),
    "n/a":       ("#f3f4f6", "#6b7280"),
}
EVENT_ICONS = {
    "agent_run_started":    "▶",
    "agent_run_completed":  "✓",
    "tool_called":          "🔧",
    "approval_requested":   "⏳",
    "approval_decision":    "✅",
    "escalation_triggered": "⬆️",
    "policy_enforced":      "🛡️",
    "validation_complete":  "🔍",
    "info_requested":       "ℹ️",
}

for event in filtered:
    rc  = RISK_COLORS.get(event["risk_level"], "#6b7280")
    sbg, stc = STATUS_COLORS.get(event["approval_status"], ("#f3f4f6", "#6b7280"))
    eicon = EVENT_ICONS.get(event["event_type"], "•")

    with st.container(border=True):
        rl, rr = st.columns([5, 2])
        with rl:
            st.markdown(
                f"**{event['id']}** &nbsp;·&nbsp; `{event['event_type']}` {eicon} &nbsp;·&nbsp;"
                f"<span style='color:{rc};font-weight:700;font-size:0.8rem;'>RISK: {event['risk_level'].upper()}</span>"
                f" &nbsp;"
                f"<span style='background:{sbg};color:{stc};border-radius:4px;"
                f"padding:1px 8px;font-size:0.75rem;font-weight:600;'>{event['approval_status'].upper()}</span>",
                unsafe_allow_html=True,
            )
            st.markdown(f"**Actor:** {event['actor']} &nbsp;·&nbsp; **Agent:** {event['agent_name']}")
        with rr:
            st.markdown(
                f"<div style='color:#6b7280;font-size:0.83rem;text-align:right;'>{event['timestamp']}</div>",
                unsafe_allow_html=True,
            )
        st.markdown(event["description"])

st.markdown("---")

col_a, col_b = st.columns(2)
with col_a:
    if st.button("🔄 Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
with col_b:
    if filtered:
        df = pd.DataFrame(filtered)
        st.download_button(
            "⬇️ Download CSV",
            data=df.to_csv(index=False),
            file_name="audit_trail.csv",
            mime="text/csv",
            use_container_width=True,
        )

st.caption("Every agent run, tool call, and approval decision is written here in real time. Immutable — no deletes.")
