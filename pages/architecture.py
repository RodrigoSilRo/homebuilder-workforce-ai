import streamlit as st

st.title("🏛️ Architecture")
st.caption("Technical design, component overview, Palantir Foundry mapping, and AWS deployment architecture.")
st.markdown("---")

tab_diagram, tab_components, tab_foundry, tab_aws, tab_phases = st.tabs([
    "System Diagram", "Components", "Palantir Foundry Mapping", "AWS Architecture", "Build Phases"
])

# ── Tab: System Diagram ───────────────────────────────────────────────────────
with tab_diagram:
    st.subheader("LangGraph Multi-Agent Pipeline")
    st.markdown("""
```
┌─────────────────────────────────────────────────────────────────────┐
│                        Streamlit UI (9 pages)                        │
│  Landing · Command Center · Marketplace · Builder · Queue · Audit   │
└────────────────────────────┬────────────────────────────────────────┘
                             │ user request
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│              Executive Orchestrator (LangGraph Supervisor)           │
│         classify_request → create_plan → route_to_agents            │
└──────┬──────────┬──────────┬──────────┬──────────┬──────────────────┘
       │          │          │          │          │
       ▼          ▼          ▼          ▼          ▼
  Associate   Vendor    Community   Finance   Construction  Marketing
 Productivity Approval  Performance Incentive    Delay      Campaign
   Agent      Agent      Agent      Agent       Agent       Agent
       │          │          │          │          │          │
       └──────────┴──────────┴──────────┴──────────┴──────────┘
                                    │ tool calls
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  MCP Tool Layer (FastMCP server)                     │
│  get_community_metrics · get_inventory_status · get_lead_conversion  │
│  get_construction_delays · calculate_incentive_impact · get_vendor_  │
│  profile · get_policy_workflow (RAG+SQL) · create_approval_request   │
│  generate_marketing_campaign · create_executive_report               │
└────────────────────────────┬────────────────────────────────────────┘
                             │ queries
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│         PostgreSQL / SQLite Data Layer (13 tables)                   │
│  communities · homes · leads · vendors · policies · delays           │
│  agent_runs · tool_calls · approval_requests · audit_events          │
│  eval_cases · eval_runs · agent_configs                              │
└─────────────────────────────────────────────────────────────────────┘
                    │                          │
                    ▼                          ▼
┌──────────────────────────┐    ┌─────────────────────────────────────┐
│  ChromaDB (RAG Index)    │    │  Critic / Governance Agent           │
│  Policy embeddings       │    │  Evidence validation · Risk scoring  │
│  Semantic retrieval      │    │  Policy enforcement · Safety checks  │
└──────────────────────────┘    └──────────────────┬──────────────────┘
                                                   │
                                                   ▼
                                ┌─────────────────────────────────────┐
                                │  Human-in-the-Loop Approval Layer   │
                                │  Per-action APRs · Approval Queue   │
                                │  24h auto-escalation · Decision log │
                                └──────────────────┬──────────────────┘
                                                   │
                                                   ▼
                                ┌─────────────────────────────────────┐
                                │  Audit Log · Monitoring · Evals     │
                                │  Every action logged · Drift detect  │
                                │  4 eval cases · CLI + pytest runner  │
                                └─────────────────────────────────────┘
```
    """)

# ── Tab: Components ───────────────────────────────────────────────────────────
with tab_components:
    st.subheader("Platform Components")

    components = [
        ("Streamlit",        "UI",              "Browser-based frontend — 9 pages, forms, charts, and live agent activity feeds."),
        ("LangGraph 1.2",    "Orchestration",   "Supervisor-agent StateGraph. 10 nodes: classify → 6 specialists → critic → synthesize → finalize → END."),
        ("Python MCP SDK",   "Tool Protocol",   "FastMCP server exposes all 11 tools over MCP — callable from Claude Desktop, Cursor, or any MCP client."),
        ("ChromaDB",         "RAG",             "Semantic policy retrieval using local MiniLM embeddings or OpenAI text-embedding-3-small. Falls back to SQL."),
        ("PostgreSQL",       "Data Layer",      "13-table schema — communities, homes, leads, vendors, policies, runs, tool_calls, approvals, audit events."),
        ("SQLite",           "Local Dev DB",    "Auto-configured when DATABASE_URL is not set. Same schema, same queries — no setup required."),
        ("OpenAI API",       "LLM",             "GPT-4o-mini for classification and executive synthesis. Fallback: Anthropic Claude Haiku, then AWS Bedrock."),
        ("AWS Bedrock",      "LLM (Cloud)",     "Claude Haiku or other foundation models via Bedrock. Configured with AWS_ACCESS_KEY_ID + AWS_BEDROCK_MODEL."),
        ("SQLAlchemy 2.0",   "ORM",             "Database abstraction — same Python code works against SQLite and PostgreSQL without modification."),
        ("Pydantic",         "Validation",       "AgentState TypedDict validates all node inputs/outputs. Tool schemas validated at MCP layer."),
        ("Docker Compose",   "Infra",           "App + PostgreSQL + MCP server as 3 separate services. One command local environment."),
        ("pytest",           "Testing",          "20 tests across 4 test classes. Declarative checks against real graph output — no mocking."),
    ]

    for name, category, desc in components:
        cols = st.columns([1.5, 1.2, 5])
        cols[0].markdown(f"**{name}**")
        cols[1].markdown(
            f"<span style='background:#f3f4f6;border-radius:4px;padding:2px 8px;font-size:0.8rem;'>{category}</span>",
            unsafe_allow_html=True,
        )
        cols[2].markdown(desc)

# ── Tab: Palantir Foundry Mapping ─────────────────────────────────────────────
with tab_foundry:
    st.subheader("Palantir Foundry / AIP Mapping")
    st.info(
        "This platform is architecturally equivalent to a Palantir AIP deployment. "
        "Every concept maps directly — the implementation differs but the paradigm is identical.",
        icon="🔗",
    )

    st.markdown("### Core Concept Mapping")

    mapping = [
        {
            "ours":    "Approval Queue + per-action APRs",
            "foundry": "AIP Actions",
            "detail":  "AIP Actions are the human-in-the-loop execution layer in Foundry. Our Approval Queue does exactly this — agents recommend actions, humans approve/reject/escalate, decisions are logged. Each APR maps to an AIP Action instance with routing, risk level, and audit trail.",
        },
        {
            "ours":    "MCP Tool Registry (11 tools via FastMCP)",
            "foundry": "AIP Function Registry",
            "detail":  "Foundry's Function Registry defines callable functions that AIP agents can invoke with validated inputs and outputs. Our MCP server does the same — 11 tools with JSON schemas, callable from any MCP client or directly from the LangGraph agents.",
        },
        {
            "ours":    "PostgreSQL Schema (13 tables)",
            "foundry": "Foundry Ontology (Object Types + Links)",
            "detail":  "The Foundry Ontology is a typed, linked data model of enterprise objects. Our 13-table schema is the equivalent — Community, Vendor, Policy, AgentRun, ToolCall, ApprovalRequest are all typed entities with defined relationships between them.",
        },
        {
            "ours":    "agent_configs table (name, tools, approval_rule, version)",
            "foundry": "AIP Agent Blueprints",
            "detail":  "AIP Agent Blueprints define reusable agent configurations — role, tools, triggers, safety rules. Our agent_configs table stores exactly this. The Agent Builder page is the UI equivalent of the Foundry Blueprint editor.",
        },
        {
            "ours":    "LangGraph StateGraph (10-node pipeline)",
            "foundry": "Foundry Pipeline / AIP Logic",
            "detail":  "AIP Logic defines the reasoning flow — how agents process inputs, call functions, and produce outputs. Our LangGraph graph is the equivalent: classify → route → specialist agents → critic → synthesize → finalize, with state passed between nodes.",
        },
        {
            "ours":    "Audit Trail (audit_events table)",
            "foundry": "Foundry Audit Log",
            "detail":  "Foundry maintains an immutable audit log of all object changes and action executions. Our audit_events table is the equivalent — every agent run, tool call, approval decision, and escalation is logged with actor, timestamp, and risk level.",
        },
        {
            "ours":    "Monitoring Dashboard + eval_runs table",
            "foundry": "Foundry Operational Layer + AIP Metrics",
            "detail":  "Foundry's operational tooling tracks agent performance, function call latency, and action success rates. Our Monitoring Dashboard reads from agent_runs, tool_calls, and eval_runs to show the same — plus drift detection across eval runs.",
        },
        {
            "ours":    "Critic / Governance Agent",
            "foundry": "AIP Safety & Guardrails",
            "detail":  "Foundry AIP has built-in guardrails that validate agent outputs against defined safety policies. Our Critic Agent does this explicitly — validates evidence coverage, checks unsupported claims, enforces approval thresholds, and assigns risk levels before any recommendation surfaces.",
        },
        {
            "ours":    "Agent Builder page (form → agent_configs)",
            "foundry": "Foundry Code Workspaces + AIP Studio",
            "detail":  "AIP Studio is the no-code/low-code interface for configuring agents in Foundry. Our Agent Builder page is the equivalent — business users define agent name, persona, tools, approval rules, and safety constraints without writing code.",
        },
        {
            "ours":    "ChromaDB RAG (semantic policy search)",
            "foundry": "Foundry AIP Retrieval (Document Search)",
            "detail":  "Foundry AIP includes document retrieval capabilities for grounding agent responses in enterprise knowledge bases. Our ChromaDB layer does the same for policies — semantic search finds the most relevant policy before the Associate Productivity Agent answers.",
        },
    ]

    for item in mapping:
        with st.expander(f"`{item['ours']}` → **{item['foundry']}**", expanded=False):
            st.markdown(item["detail"])

    st.markdown("---")
    st.subheader("Why This Matters for Lennar")
    st.markdown("""
Lennar's Agent Builder role specifically requires experience with **Palantir Foundry AIP** —
*Code Workspaces, AIP SDK, AIP Actions*.

This platform demonstrates that I understand the AIP paradigm deeply:

- **AIP Actions** (our Approval Queue) — the human-in-the-loop execution model where agents recommend, humans decide
- **Function Registry** (our MCP tools) — typed, validated, callable functions with schemas
- **Foundry Ontology** (our database schema) — enterprise data modeled as typed objects with relationships
- **AIP Agent Blueprints** (our Agent Builder) — reusable, configurable agent definitions
- **AIP Safety** (our Critic Agent) — governance, evidence validation, and output safety built in

The primary technical difference: Foundry is a proprietary platform with a managed runtime.
This platform is open, Python-first, and deployable anywhere.
The architectural concepts, design decisions, and production concerns are identical.
    """)

# ── Tab: AWS Architecture ─────────────────────────────────────────────────────
with tab_aws:
    st.subheader("AWS Deployment Architecture")

    st.markdown("""
```
┌─────────────────────────────────────────────────────────────────┐
│                        AWS Cloud                                 │
│                                                                 │
│  ┌─────────────┐    ┌─────────────────────────────────────┐    │
│  │   Route 53  │───▶│        Application Load Balancer     │    │
│  └─────────────┘    └──────────────────┬──────────────────┘    │
│                                        │                        │
│                     ┌──────────────────▼──────────────────┐    │
│                     │         ECS Fargate (App)            │    │
│                     │   python -m streamlit run app.py     │    │
│                     └──────────────────┬──────────────────┘    │
│                                        │                        │
│          ┌─────────────────────────────┼──────────────────┐    │
│          │                             │                   │    │
│  ┌───────▼────────┐        ┌───────────▼──────┐  ┌───────▼──┐ │
│  │   RDS Postgres  │        │  AWS Bedrock      │  │   S3     │ │
│  │  (db layer)    │        │  Claude / Titan    │  │ (assets) │ │
│  └────────────────┘        └──────────────────┘  └──────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    ECS Fargate (MCP)                     │   │
│  │         python -m mcp_server.server --transport http     │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```
    """)

    st.markdown("### AWS Services Used")
    aws_services = [
        ("AWS Bedrock",         "LLM provider — Claude Haiku, Claude Sonnet, or Titan models. Configured via AWS_BEDROCK_MODEL env var. Same llm.py interface as OpenAI/Anthropic."),
        ("Amazon RDS (PostgreSQL)", "Production database. Same SQLAlchemy queries — just set DATABASE_URL to the RDS connection string."),
        ("ECS Fargate",          "Serverless container runtime for the Streamlit app and MCP server. Dockerfile is production-ready."),
        ("Application Load Balancer", "Routes traffic to ECS tasks. HTTPS termination + health checks via /_stcore/health."),
        ("S3",                   "Static assets, model artifacts, or ChromaDB index storage if using persistent embeddings."),
        ("CloudWatch",           "Logs and metrics from ECS tasks. Can be wired to the Monitoring Dashboard via CloudWatch API."),
        ("Lambda",               "Optional: trigger agent runs on schedule (e.g., nightly community performance digest) or on S3 events."),
    ]
    for service, desc in aws_services:
        cols = st.columns([2, 5])
        cols[0].markdown(f"**{service}**")
        cols[1].markdown(desc)

    st.markdown("---")
    st.markdown("**To enable AWS Bedrock as LLM:**")
    st.code("""# Add to .env
AWS_ACCESS_KEY_ID=your_key_id
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
AWS_BEDROCK_MODEL=anthropic.claude-haiku-4-5-20251001-v1:0""", language="bash")

# ── Tab: Build Phases ──────────────────────────────────────────────────────────
with tab_phases:
    st.subheader("Development Phases")

    phases = [
        ("Phase 1", "Static Demo MVP",            "Streamlit shell, 9 pages, mock data, simulated agent runs"),
        ("Phase 2", "Database + Tools",            "13-table schema, seed data, 8 real tool modules, tool call logging"),
        ("Phase 3", "LangGraph Agents",            "10-node StateGraph, 8 specialist agents, LLM classification + synthesis"),
        ("Phase 4", "Approval + Audit",            "Per-action APR routing, escalation rules engine, 24h auto-escalation"),
        ("Phase 5", "MCP Integration",             "FastMCP server, 11 tools registered, Claude Desktop config"),
        ("Phase 6", "Monitoring + Evals",          "4 eval cases, drift detection, pytest suite, CLI runner — 4/4 passing"),
        ("Phase 7", "Polish + Deploy",             "README, Dockerfile, docker-compose, Render config"),
        ("Phase 8", "RAG + Bedrock + Foundry",     "ChromaDB semantic policy search, AWS Bedrock LLM, ERP/CRM/HRIS language, full Foundry mapping"),
    ]

    for phase, title, desc in phases:
        st.markdown(
            f"<div style='background:#dcfce7;border:1px solid #16a34a;border-radius:8px;"
            f"padding:0.7rem 1rem;margin-bottom:0.5rem;'>"
            f"<strong>✅ {phase}</strong> — {title}<br>"
            f"<span style='color:#6b7280;font-size:0.87rem;'>{desc}</span></div>",
            unsafe_allow_html=True,
        )

st.markdown("---")
st.caption("Built by Rodrigo Rosa — Software Engineer & Technical Founder")
