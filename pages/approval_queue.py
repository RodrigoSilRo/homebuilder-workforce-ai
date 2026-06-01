import streamlit as st
from datetime import datetime
from tools.approval_tools import get_approval_requests, update_approval_decision
from tools.audit_tools import log_audit_event
from services.approval_service import hours_pending, check_and_escalate_overdue, get_overdue_requests

st.title("✅ Approval Queue")
st.caption("Human-in-the-loop decisions. Every approval, rejection, or escalation is logged to the audit trail in real time.")
st.markdown("---")

# ── Auto-escalate overdue (runs silently on page load) ────────────────────────
auto_escalated = check_and_escalate_overdue()
if auto_escalated:
    st.warning(
        f"⬆️ **{len(auto_escalated)} request(s) auto-escalated** — pending > 24 hours: {', '.join(auto_escalated)}",
        icon="⏰",
    )

# ── Load from DB ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=5)
def load_approvals():
    return get_approval_requests()

approvals = load_approvals()

# ── Metrics ───────────────────────────────────────────────────────────────────
pending   = sum(1 for r in approvals if r["status"] == "pending")
approved  = sum(1 for r in approvals if r["status"] == "approved")
rejected  = sum(1 for r in approvals if r["status"] == "rejected")
escalated = sum(1 for r in approvals if r["status"] == "escalated")
overdue   = len(get_overdue_requests())

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Pending",   pending,   delta=f"{pending} need action" if pending else None,
          delta_color="inverse" if pending else "off")
c2.metric("Approved",  approved)
c3.metric("Rejected",  rejected)
c4.metric("Escalated", escalated)
c5.metric("Overdue",   overdue,   delta="Past 24h" if overdue else None,
          delta_color="inverse" if overdue else "off")

st.markdown("---")

# ── Filters ───────────────────────────────────────────────────────────────────
f1, f2, f3, f4 = st.columns(4)
with f1:
    status_f = st.selectbox("Status",     ["All", "pending", "approved", "rejected", "escalated"])
with f2:
    risk_f   = st.selectbox("Risk Level", ["All", "high", "medium", "low"])
with f3:
    agents   = sorted({r["agent_name"] for r in approvals if r["agent_name"]})
    agent_f  = st.selectbox("Agent", ["All"] + agents)
with f4:
    sort_by  = st.selectbox("Sort", ["Newest first", "Oldest first", "Risk (high → low)"])

filtered = [
    r for r in approvals
    if (status_f == "All" or r["status"] == status_f)
    and (risk_f  == "All" or r["risk_level"] == risk_f)
    and (agent_f == "All" or r["agent_name"] == agent_f)
]

if sort_by == "Oldest first":
    filtered = sorted(filtered, key=lambda r: r["created_at"])
elif sort_by == "Risk (high → low)":
    order = {"high": 0, "medium": 1, "low": 2}
    filtered = sorted(filtered, key=lambda r: order.get(r["risk_level"], 3))

st.markdown(f"**{len(filtered)} request{'s' if len(filtered) != 1 else ''} shown**")
st.markdown("<br>", unsafe_allow_html=True)

# ── Color maps ─────────────────────────────────────────────────────────────────
STATUS_COLORS = {
    "pending":   ("rgba(217,119,6,0.12)",  "#d97706", "⏳"),
    "approved":  ("rgba(22,163,74,0.12)",  "#16a34a", "✅"),
    "rejected":  ("rgba(220,38,38,0.12)",  "#dc2626", "🚫"),
    "escalated": ("rgba(124,58,237,0.12)", "#7c3aed", "⬆️"),
}
RISK_COLORS = {"high": "#dc2626", "medium": "#d97706", "low": "#16a34a"}

for req in filtered:
    bg, tc, icon = STATUS_COLORS.get(req["status"], ("#f9fafb", "#374151", "•"))
    rc  = RISK_COLORS.get(req["risk_level"], "#6b7280")
    hrs = hours_pending(req["created_at"]) if req["status"] == "pending" else 0
    is_overdue = hrs >= 24

    with st.container(border=True):
        hl, hr = st.columns([5, 2])
        with hl:
            overdue_tag = (
                f" &nbsp;<span style='background:#dc2626;color:white;border-radius:4px;"
                f"padding:1px 8px;font-size:0.72rem;font-weight:700;'>⏰ OVERDUE {hrs:.0f}h</span>"
                if is_overdue else ""
            )
            st.markdown(
                f"**{req['id']}** &nbsp;·&nbsp; {req['agent_name']} &nbsp;·&nbsp;"
                f"<span style='background:{rc};color:white;border-radius:4px;"
                f"padding:1px 8px;font-size:0.72rem;font-weight:700;'>RISK: {req['risk_level'].upper()}</span>"
                f" &nbsp;"
                f"<span style='background:{bg};color:{tc};border-radius:4px;"
                f"padding:1px 8px;font-size:0.72rem;font-weight:700;'>{icon} {req['status'].upper()}</span>"
                + overdue_tag,
                unsafe_allow_html=True,
            )
            community_str = f" · **{req['community']}**" if req.get("community") else ""
            pending_str   = f" · Pending **{hrs:.1f}h**" if req["status"] == "pending" and hrs > 0 else ""
            st.markdown(f"Created: {req['created_at']}{community_str}{pending_str}")
        with hr:
            st.markdown(f"**Approver:** {req['required_approver']}")
            if req.get("decided_at"):
                st.caption(f"Decided: {req['decided_at'][:16]}")

        st.markdown(f"**Action:** {req['recommended_action']}")

        if req.get("flags"):
            flags_html = " ".join(
                f"<span style='background:rgba(220,38,38,0.1);color:#dc2626;border:1px solid rgba(220,38,38,0.3);border-radius:4px;"
                f"padding:2px 9px;font-size:0.77rem;font-weight:600;margin:2px;'>! {f}</span>"
                for f in req["flags"]
            )
            st.markdown(flags_html, unsafe_allow_html=True)

        if req.get("decision_reason"):
            st.caption(f"Reason: {req['decision_reason']}")

        # Action buttons — only for pending
        if req["status"] == "pending":
            st.markdown("<br>", unsafe_allow_html=True)
            b1, b2, b3, b4, _ = st.columns([1, 1, 1, 1, 2])
            rid = req["id"]
            with b1:
                if st.button("✅ Approve", key=f"apr_{rid}", type="primary", use_container_width=True):
                    update_approval_decision(rid, "approved", "Approved via Approval Queue")
                    log_audit_event("approval_decision", f"{rid} approved by user",
                                    actor="user", agent_name=req["agent_name"],
                                    risk_level=req["risk_level"], approval_status="approved")
                    st.cache_data.clear()
                    st.rerun()
            with b2:
                if st.button("❌ Reject", key=f"rej_{rid}", use_container_width=True):
                    update_approval_decision(rid, "rejected", "Rejected via Approval Queue")
                    log_audit_event("approval_decision", f"{rid} rejected by user",
                                    actor="user", agent_name=req["agent_name"],
                                    risk_level=req["risk_level"], approval_status="rejected")
                    st.cache_data.clear()
                    st.rerun()
            with b3:
                if st.button("⬆️ Escalate", key=f"esc_{rid}", use_container_width=True):
                    from services.approval_service import ESCALATION_MAP
                    new_approver = ESCALATION_MAP.get(req["required_approver"], "COO")
                    update_approval_decision(rid, "escalated", f"Manually escalated to {new_approver}")
                    log_audit_event("escalation_triggered", f"{rid} manually escalated → {new_approver}",
                                    actor="user", agent_name=req["agent_name"],
                                    risk_level=req["risk_level"], approval_status="escalated")
                    st.cache_data.clear()
                    st.rerun()
            with b4:
                if is_overdue and st.button("📋 Request Info", key=f"info_{rid}", use_container_width=True):
                    log_audit_event("info_requested", f"{rid} — additional info requested",
                                    actor="user", agent_name=req["agent_name"],
                                    risk_level=req["risk_level"], approval_status="pending")
                    st.info("Information request logged to audit trail.")

st.markdown("---")

col_a, col_b = st.columns(2)
with col_a:
    if st.button("🔄 Refresh Queue", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
with col_b:
    if st.button("⬆️ Auto-escalate All Overdue", use_container_width=True):
        ids = check_and_escalate_overdue()
        st.cache_data.clear()
        if ids:
            st.success(f"Escalated: {', '.join(ids)}")
        else:
            st.info("No overdue requests found.")
        st.rerun()

st.caption(
    "Escalation rule: requests pending > 24 hours auto-escalate to the next approver level. "
    "All decisions are written to the database and logged to the Audit Trail."
)
