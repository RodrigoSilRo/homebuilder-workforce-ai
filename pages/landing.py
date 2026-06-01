import streamlit as st
from database.db import query
from services.llm import has_llm

st.markdown("""
<style>
.hero-title {
    font-size: 2.8rem; font-weight: 700; line-height: 1.15;
    color: #1B3868; letter-spacing: -0.5px;
}
.hero-sub {
    font-size: 1.05rem; color: #4A5568; margin-top: 0.75rem;
    line-height: 1.7; max-width: 540px;
}
.kpi-card {
    background: #FFFFFF; border: 1px solid #E2E8F0;
    border-top: 3px solid #1B3868; border-radius: 8px;
    padding: 1.1rem 1rem; text-align: center;
}
.kpi-number { font-size: 2rem; font-weight: 700; color: #1B3868; line-height: 1; }
.kpi-label {
    font-size: 0.72rem; color: #718096; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.8px; margin-top: 0.35rem;
}
.section-label {
    font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 1.8px; color: #1B3868; margin-bottom: 0.25rem;
}
.feature-card {
    background: #F7F9FC; border: 1px solid #E2E8F0;
    border-radius: 10px; padding: 1.5rem; height: 100%;
}
.feature-title { font-weight: 700; font-size: 0.97rem; margin: 0.55rem 0 0.35rem; color: #1A202C; }
.feature-desc { color: #4A5568; font-size: 0.87rem; line-height: 1.6; }
.agent-card {
    background: #FFFFFF; border: 1px solid #E2E8F0;
    border-radius: 8px; padding: 1rem 1.1rem;
    margin-bottom: 0.75rem; min-height: 110px;
}
.step-num { font-size: 1.5rem; font-weight: 800; color: #1B3868; line-height: 1; }
.step-title { font-weight: 700; font-size: 0.93rem; margin: 0.3rem 0 0.2rem; color: #1A202C; }
.step-desc { color: #4A5568; font-size: 0.84rem; line-height: 1.5; }
.divider { border: none; border-top: 1px solid #E2E8F0; margin: 2rem 0; }
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
col_hero, col_cta = st.columns([2, 1], gap="large")
with col_hero:
    st.markdown('<div class="hero-title">HomeBuilder<br>Workforce AI</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-sub">A multi-agent AI platform purpose-built for homebuilder operations — '
        'intelligent automation for sales, procurement, construction, and associate workflows, '
        'with enterprise governance and full auditability.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Open Command Center →", type="primary"):
        st.switch_page("pages/executive_command.py")

with col_cta:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    if has_llm():
        st.success("LLM active — GPT-4o-mini / Claude Haiku", icon="🤖")
    else:
        st.info("Rule-based mode — add API key for LLM", icon="ℹ️")

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── KPI bar ───────────────────────────────────────────────────────────────────
try:
    stats = query("""
        SELECT
            (SELECT COUNT(*) FROM agent_runs)        AS runs,
            (SELECT COUNT(*) FROM tool_calls)        AS tools,
            (SELECT COUNT(*) FROM approval_requests) AS aprs,
            (SELECT COUNT(*) FROM audit_events)      AS events
    """)
    s = stats[0] if stats else {}
except Exception:
    s = {}

c1, c2, c3, c4, c5 = st.columns(5)
for col, num, label in [
    (c1, "8",                     "AI Agents"),
    (c2, "11",                    "MCP Tools"),
    (c3, str(s.get("runs",  0)), "Agent Runs"),
    (c4, str(s.get("tools", 0)), "Tool Calls"),
    (c5, str(s.get("events",0)), "Audit Events"),
]:
    col.markdown(
        f'<div class="kpi-card">'
        f'<div class="kpi-number">{num}</div>'
        f'<div class="kpi-label">{label}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── Capabilities ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Platform Capabilities</div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

f1, f2, f3 = st.columns(3, gap="medium")
with f1:
    st.markdown("""<div class="feature-card">
      <div style="font-size:1.6rem;">👤</div>
      <div class="feature-title">Associate Productivity</div>
      <div class="feature-desc">Associates ask any question about workflows, forms, policies, and approvals.
      Agents retrieve the right policy, list required steps, identify approvers, and draft documents — in seconds.</div>
    </div>""", unsafe_allow_html=True)
with f2:
    st.markdown("""<div class="feature-card">
      <div style="font-size:1.6rem;">⚙️</div>
      <div class="feature-title">Workflow Automation</div>
      <div class="feature-desc">AI agents automate vendor onboarding, invoice routing, escalation triggers,
      and approval flows. Human-in-the-loop controls ensure no action executes without the right sign-off.</div>
    </div>""", unsafe_allow_html=True)
with f3:
    st.markdown("""<div class="feature-card">
      <div style="font-size:1.6rem;">📊</div>
      <div class="feature-title">Operations Intelligence</div>
      <div class="feature-desc">Specialist agents analyze community sales, stale inventory, lead conversion,
      construction delays, and margin impact — delivering evidence-backed executive recommendations.</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── How it works ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">How It Works</div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

steps = [
    ("1", "Ask a question",     "Select or type a business question in the Executive Command Center."),
    ("2", "Agents investigate", "LangGraph routes to specialist agents — each calls real database tools."),
    ("3", "Evidence collected", "Every tool call is logged. No unsupported claims allowed."),
    ("4", "Critic validates",   "Governance Agent checks evidence, enforces policies, assigns risk."),
    ("5", "LLM synthesizes",    "GPT-4o-mini or Claude writes the executive summary from real data."),
    ("6", "You decide",         "Approve, reject, or escalate. Each decision writes to the audit trail."),
]
cols = st.columns(3)
for i, (num, title, desc) in enumerate(steps):
    with cols[i % 3]:
        st.markdown(
            f'<div style="padding:0.9rem 0.2rem;">'
            f'<div class="step-num">{num}</div>'
            f'<div class="step-title">{title}</div>'
            f'<div class="step-desc">{desc}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── Agent roster ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">AI Workforce</div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

agents = [
    ("🎯", "Executive Orchestrator",  "Coordinates specialist agents and produces the final recommendation."),
    ("👤", "Associate Productivity",   "Answers policy and workflow questions for any corporate function."),
    ("🏢", "Vendor Approval",          "Automates vendor onboarding review, routes to the correct approver."),
    ("📊", "Community Performance",    "Analyzes sales, inventory, and lead data across communities."),
    ("💰", "Finance / Incentive",      "Models discount scenarios within margin constraints."),
    ("🏗️", "Construction Delay",      "Flags delays and auto-escalates when closings are at risk."),
    ("📣", "Marketing Campaign",       "Generates targeted campaign copy tied to real performance data."),
    ("🛡️", "Critic / Governance",     "Validates evidence, enforces policies, assigns risk levels."),
]
ag_cols = st.columns(4)
for i, (icon, name, desc) in enumerate(agents):
    with ag_cols[i % 4]:
        st.markdown(
            f'<div class="agent-card">'
            f'<div style="font-size:1.4rem;">{icon}</div>'
            f'<div style="font-weight:700;font-size:0.9rem;margin:0.4rem 0 0.2rem;color:#1A202C;">{name}</div>'
            f'<div style="color:#4A5568;font-size:0.8rem;line-height:1.4;">{desc}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown(
    "<div style='text-align:center;color:#A0AEC0;font-size:0.82rem;padding:0.5rem 0;'>"
    "Built by <strong>Rodrigo Rosa</strong> — Software Engineer &amp; Technical Founder"
    "</div>",
    unsafe_allow_html=True,
)
