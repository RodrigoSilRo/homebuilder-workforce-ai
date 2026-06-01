import streamlit as st
from database.db import query
from services.llm import has_llm

st.markdown("""
<style>
.hero-title { font-size: 2.8rem; font-weight: 800; line-height: 1.2; }
.hero-sub { font-size: 1.15rem; color: #6b7280; margin-top: 0.5rem; }
.badge { display:inline-block; background:#f3f4f6; border:1px solid #e5e7eb;
         border-radius:6px; padding:4px 12px; margin:4px 4px 4px 0;
         font-size:0.82rem; font-weight:600; color:#374151; }
.feature-card { background:#f9fafb; border:1px solid #e5e7eb; border-radius:12px;
                padding:1.4rem; height:100%; }
.feature-title { font-weight:700; font-size:1.05rem; margin:0.5rem 0 0.25rem; }
.feature-desc { color:#6b7280; font-size:0.9rem; line-height:1.5; }
.divider { border:none; border-top:1px solid #e5e7eb; margin:2rem 0; }
.stat-number { font-size:2rem; font-weight:800; color:#111827; }
.stat-label { font-size:0.85rem; color:#6b7280; }
.phase-done { background:#dcfce7; border:1px solid #16a34a; border-radius:8px;
              padding:0.5rem 1rem; margin-bottom:0.4rem; }
.phase-pill { display:inline-block; background:#16a34a; color:white; border-radius:4px;
              padding:1px 8px; font-size:0.72rem; font-weight:700; margin-right:6px; }
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
col_hero, col_cta = st.columns([2, 1], gap="large")
with col_hero:
    st.markdown('<div class="hero-title">HomeBuilder Workforce AI</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-sub">The internal AI agent platform a national homebuilder would actually build — '
        'multi-agent orchestration, enterprise governance, human-in-the-loop approvals, and full auditability.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    badges = ["Python", "LangGraph", "MCP", "PostgreSQL", "LLM Tool Calling", "Human-in-the-Loop", "Observability", "Audit Trails"]
    st.markdown("".join(f'<span class="badge">{b}</span>' for b in badges), unsafe_allow_html=True)

with col_cta:
    st.markdown("<br><br>", unsafe_allow_html=True)
    llm_on = has_llm()
    if llm_on:
        st.success("LLM active — GPT-4o-mini or Claude Haiku", icon="🤖")
    else:
        st.info("Rule-based mode — add API key to .env for LLM", icon="ℹ️")

    if st.button("Launch Demo →", type="primary", use_container_width=True):
        st.switch_page("pages/executive_command.py")

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── Live DB stats ─────────────────────────────────────────────────────────────
try:
    stats = query("""
        SELECT
            (SELECT COUNT(*) FROM agent_runs)         AS runs,
            (SELECT COUNT(*) FROM tool_calls)         AS tools,
            (SELECT COUNT(*) FROM approval_requests)  AS aprs,
            (SELECT COUNT(*) FROM audit_events)       AS events
    """)
    s = stats[0] if stats else {}
except Exception:
    s = {}

c1, c2, c3, c4, c5 = st.columns(5)
c1.markdown(f'<div class="stat-number">8</div><div class="stat-label">AI Agents</div>',   unsafe_allow_html=True)
c2.markdown(f'<div class="stat-number">11</div><div class="stat-label">MCP Tools</div>',  unsafe_allow_html=True)
c3.markdown(f'<div class="stat-number">{s.get("runs", 0)}</div><div class="stat-label">Agent Runs</div>', unsafe_allow_html=True)
c4.markdown(f'<div class="stat-number">{s.get("tools", 0)}</div><div class="stat-label">Tool Calls</div>', unsafe_allow_html=True)
c5.markdown(f'<div class="stat-number">{s.get("events", 0)}</div><div class="stat-label">Audit Events</div>', unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── Feature Cards ─────────────────────────────────────────────────────────────
st.subheader("What this platform does")
st.markdown("<br>", unsafe_allow_html=True)
f1, f2, f3 = st.columns(3, gap="medium")

with f1:
    st.markdown("""<div class="feature-card">
      <div style="font-size:2rem;">👤</div>
      <div class="feature-title">Associate Productivity</div>
      <div class="feature-desc">Associates ask any question about workflows, forms, policies, and approvals.
      Agents retrieve the right policy, list required steps, identify approvers, and draft approval documents — in seconds.</div>
    </div>""", unsafe_allow_html=True)

with f2:
    st.markdown("""<div class="feature-card">
      <div style="font-size:2rem;">⚙️</div>
      <div class="feature-title">Corporate Workflow Automation</div>
      <div class="feature-desc">AI agents automate vendor onboarding, invoice routing, escalation triggers,
      and approval flows. Human-in-the-loop controls ensure no action executes without the right sign-off.</div>
    </div>""", unsafe_allow_html=True)

with f3:
    st.markdown("""<div class="feature-card">
      <div style="font-size:2rem;">📊</div>
      <div class="feature-title">Homebuilding Operations Intelligence</div>
      <div class="feature-desc">Specialist agents analyze community sales, stale inventory, lead conversion,
      construction delays, and margin impact — then synthesize an evidence-backed executive recommendation.</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── Build status ──────────────────────────────────────────────────────────────
st.subheader("Build Status — All Phases Complete")
st.markdown("<br>", unsafe_allow_html=True)

phases = [
    ("Phase 1", "Static Demo MVP", "Streamlit shell, 9 pages, mock data, simulated agent runs"),
    ("Phase 2", "Database + Tools", "PostgreSQL/SQLite schema, seed data, 8 real tool modules, tool call logging"),
    ("Phase 3", "LangGraph Agents", "10-node StateGraph, 8 specialist agents, LLM classification + synthesis"),
    ("Phase 4", "Approval + Audit", "Per-action APR routing, escalation rules engine, overdue detection"),
    ("Phase 5", "MCP Integration", "FastMCP server, 11 tools registered, Claude Desktop config"),
    ("Phase 6", "Monitoring + Evals", "4 eval cases, drift detection, pytest suite, run_evals CLI"),
    ("Phase 7", "Polish + Deploy", "README, Dockerfile, docker-compose, Render config, .gitignore"),
]

p_left, p_right = st.columns(2, gap="medium")
for i, (phase, title, desc) in enumerate(phases):
    col = p_left if i % 2 == 0 else p_right
    col.markdown(
        f'<div class="phase-done">'
        f'<span class="phase-pill">✓ {phase}</span>'
        f'<strong>{title}</strong><br>'
        f'<span style="color:#6b7280;font-size:0.85rem;">{desc}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── How it works ──────────────────────────────────────────────────────────────
st.subheader("How a run works")
st.markdown("<br>", unsafe_allow_html=True)
steps = [
    ("1", "Ask a question",        "Select or type a business question in the Executive Command Center."),
    ("2", "Agents investigate",    "LangGraph routes to specialist agents — each calls real database tools."),
    ("3", "Evidence collected",    "Every tool call is logged. No unsupported claims allowed."),
    ("4", "Critic validates",      "Governance Agent checks evidence, enforces policies, assigns risk."),
    ("5", "LLM synthesizes",       "GPT-4o-mini or Claude writes the executive summary from real data."),
    ("6", "You decide",            "Approve, reject, or escalate. Each decision writes to the audit trail."),
]
cols = st.columns(3)
for i, (num, title, desc) in enumerate(steps):
    with cols[i % 3]:
        st.markdown(
            f'<div style="padding:1rem 0;">'
            f'<div style="font-size:1.5rem;font-weight:800;color:#2563eb;">{num}</div>'
            f'<div style="font-weight:700;margin:0.25rem 0;">{title}</div>'
            f'<div style="color:#6b7280;font-size:0.88rem;">{desc}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── Agent roster ──────────────────────────────────────────────────────────────
st.subheader("The AI Workforce")
st.markdown("<br>", unsafe_allow_html=True)
agents = [
    ("🎯", "Executive Orchestrator",      "Coordinates all specialist agents and produces the final recommendation."),
    ("👤", "Associate Productivity",       "Answers policy and workflow questions for any corporate function."),
    ("🏢", "Vendor Approval",              "Automates vendor onboarding review and routes to the correct approver."),
    ("📊", "Community Performance",        "Analyzes sales, inventory, and lead data across communities."),
    ("💰", "Finance / Incentive",          "Models discount scenarios within margin constraints — enforces policy limits."),
    ("🏗️", "Construction Delay",          "Flags delays and auto-escalates when closings are at risk."),
    ("📣", "Marketing Campaign",           "Generates targeted campaign copy tied to real inventory and performance data."),
    ("🛡️", "Critic / Governance",         "Validates evidence, enforces policies, assigns risk levels."),
]
ag_cols = st.columns(4)
for i, (icon, name, desc) in enumerate(agents):
    with ag_cols[i % 4]:
        st.markdown(
            f'<div style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:10px;'
            f'padding:1rem;margin-bottom:1rem;min-height:130px;">'
            f'<div style="font-size:1.6rem;">{icon}</div>'
            f'<div style="font-weight:700;font-size:0.92rem;margin:0.4rem 0 0.25rem;">{name}</div>'
            f'<div style="color:#6b7280;font-size:0.82rem;line-height:1.4;">{desc}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown(
    "<div style='text-align:center;color:#9ca3af;font-size:0.85rem;padding:1rem 0;'>"
    "Built by <strong>Rodrigo Rosa</strong> — Software Engineer &amp; Technical Founder"
    "</div>",
    unsafe_allow_html=True,
)
