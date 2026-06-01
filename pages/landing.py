import streamlit as st
from database.db import query
from services.llm import has_llm

st.markdown("""
<style>
.hero-eyebrow {
    font-size: 0.68rem; font-weight: 700; letter-spacing: 2.5px;
    text-transform: uppercase; color: var(--primary-color); margin-bottom: 0.6rem;
}
.hero-title {
    font-size: 2.5rem; font-weight: 700; line-height: 1.15; letter-spacing: -0.5px;
    margin-bottom: 0.8rem;
}
.hero-sub {
    font-size: 1rem; line-height: 1.75; opacity: 0.65; max-width: 500px;
}
.section-label {
    font-size: 0.68rem; font-weight: 700; letter-spacing: 2.5px;
    text-transform: uppercase; color: var(--primary-color); margin-bottom: 0.75rem;
}
.cap-card {
    border-left: 3px solid var(--primary-color);
    padding: 0.1rem 0 0.1rem 1rem;
    margin-bottom: 0.5rem;
}
.cap-title { font-weight: 700; font-size: 0.95rem; margin-bottom: 0.2rem; }
.cap-desc { font-size: 0.86rem; opacity: 0.65; line-height: 1.6; }
.step-row {
    display: flex; align-items: flex-start; gap: 1rem; padding: 0.6rem 0;
    border-bottom: 1px solid rgba(128,128,128,0.12);
}
.step-num {
    font-size: 0.72rem; font-weight: 700; color: var(--primary-color);
    background: rgba(27,82,153,0.1); border-radius: 4px;
    padding: 2px 7px; flex-shrink: 0; margin-top: 2px;
}
.step-body {}
.step-title { font-weight: 700; font-size: 0.9rem; }
.step-desc { font-size: 0.84rem; opacity: 0.6; margin-top: 0.1rem; }
.agent-row {
    display: flex; align-items: flex-start; gap: 0.75rem;
    padding: 0.65rem 0; border-bottom: 1px solid rgba(128,128,128,0.1);
}
.agent-initial {
    width: 30px; height: 30px; border-radius: 5px; flex-shrink: 0;
    background: var(--primary-color); color: white;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.7rem; font-weight: 800; letter-spacing: 0.5px;
}
.agent-name { font-weight: 700; font-size: 0.88rem; }
.agent-desc { font-size: 0.82rem; opacity: 0.6; margin-top: 0.1rem; line-height: 1.45; }
.divider { border: none; border-top: 1px solid rgba(128,128,128,0.15); margin: 1.75rem 0; }
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
col_hero, col_cta = st.columns([5, 2], gap="large")
with col_hero:
    st.markdown('<div class="hero-eyebrow">AI Agent Platform</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">HomeBuilder Workforce AI</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-sub">Multi-agent orchestration for homebuilder operations — '
        'intelligent automation across sales, procurement, construction, and associate workflows '
        'with enterprise governance and full auditability.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Open Command Center →", type="primary"):
        st.switch_page("pages/executive_command.py")

with col_cta:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    if has_llm():
        st.success("LLM active")
    else:
        st.info("Rule-based mode — add API key for LLM")

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
c1.metric("AI Agents",    "8")
c2.metric("MCP Tools",    "11")
c3.metric("Agent Runs",   s.get("runs",  0))
c4.metric("Tool Calls",   s.get("tools", 0))
c5.metric("Audit Events", s.get("events",0))

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── Capabilities ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Platform Capabilities</div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

f1, f2, f3 = st.columns(3, gap="large")
with f1:
    st.markdown("""<div class="cap-card">
      <div class="cap-title">Associate Productivity</div>
      <div class="cap-desc">Associates ask any question about workflows, forms, policies, and approvals.
      Agents retrieve the right policy, list required steps, identify approvers, and draft documents — in seconds.</div>
    </div>""", unsafe_allow_html=True)

with f2:
    st.markdown("""<div class="cap-card">
      <div class="cap-title">Workflow Automation</div>
      <div class="cap-desc">AI agents automate vendor onboarding, invoice routing, escalation triggers,
      and approval flows. Human-in-the-loop controls ensure no action executes without the right sign-off.</div>
    </div>""", unsafe_allow_html=True)

with f3:
    st.markdown("""<div class="cap-card">
      <div class="cap-title">Operations Intelligence</div>
      <div class="cap-desc">Specialist agents analyze community sales, stale inventory, lead conversion,
      construction delays, and margin impact — delivering evidence-backed executive recommendations.</div>
    </div>""", unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── How it works ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">How It Works</div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

col_steps, col_agents = st.columns([1, 1], gap="large")

with col_steps:
    steps = [
        ("01", "Ask a question",     "Select or type a business question in the Executive Command Center."),
        ("02", "Agents investigate", "LangGraph routes to specialist agents — each calls real database tools."),
        ("03", "Evidence collected", "Every tool call is logged. No unsupported claims allowed."),
        ("04", "Critic validates",   "Governance Agent checks evidence, enforces policies, assigns risk."),
        ("05", "LLM synthesizes",    "GPT-4o-mini or Claude writes the executive summary from real data."),
        ("06", "You decide",         "Approve, reject, or escalate. Each decision writes to the audit trail."),
    ]
    for num, title, desc in steps:
        st.markdown(
            f'<div class="step-row">'
            f'<span class="step-num">{num}</span>'
            f'<div class="step-body">'
            f'<div class="step-title">{title}</div>'
            f'<div class="step-desc">{desc}</div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

# ── Agent roster ──────────────────────────────────────────────────────────────
with col_agents:
    st.markdown('<div class="section-label">AI Workforce</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    agents = [
        ("EO", "Executive Orchestrator",  "Coordinates specialist agents, produces final recommendations."),
        ("AP", "Associate Productivity",   "Answers policy and workflow questions for any corporate function."),
        ("VA", "Vendor Approval",          "Automates vendor onboarding review, routes to the correct approver."),
        ("CP", "Community Performance",    "Analyzes sales, inventory, and lead data across communities."),
        ("FI", "Finance / Incentive",      "Models discount scenarios within margin constraints."),
        ("CD", "Construction Delay",       "Flags delays and auto-escalates when closings are at risk."),
        ("MC", "Marketing Campaign",       "Generates targeted campaign copy tied to real performance data."),
        ("CG", "Critic / Governance",      "Validates evidence, enforces policies, assigns risk levels."),
    ]
    for initials, name, desc in agents:
        st.markdown(
            f'<div class="agent-row">'
            f'<div class="agent-initial">{initials}</div>'
            f'<div><div class="agent-name">{name}</div>'
            f'<div class="agent-desc">{desc}</div></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown(
    "<div style='text-align:center;opacity:0.35;font-size:0.8rem;padding:0.5rem 0;'>"
    "Built by <strong>Rodrigo Rosa</strong> — Software Engineer &amp; Technical Founder"
    "</div>",
    unsafe_allow_html=True,
)
