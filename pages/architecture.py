import streamlit as st
import streamlit.components.v1 as components

st.title("🏛️ Architecture")
st.caption("Technical design, Mermaid diagram, Palantir Foundry mapping with 30-day migration plan, and AWS deployment architecture.")
st.markdown("---")

tab_diagram, tab_components, tab_foundry, tab_aws, tab_prompts = st.tabs([
    "System Diagram", "Components", "Palantir Foundry Mapping", "AWS Architecture", "Prompt Engineering"
])

# ── Tab: System Diagram ───────────────────────────────────────────────────────
with tab_diagram:
    st.subheader("LangGraph Multi-Agent Pipeline — Live Diagram")

    mermaid_diagram = """
flowchart TD
    U([👤 User / Associate]) -->|Business Question| EO

    subgraph ORCH[Executive Orchestrator]
        direction LR
        CL[Classify Request] --> PL[Create Plan]
        PL --> RT[Route to Agents]
    end

    EO --- ORCH

    RT --> CP[📊 Community Performance]
    RT --> CD[🏗️ Construction Delay]
    RT --> FI[💰 Finance / Incentive]
    RT --> MC[📣 Marketing Campaign]
    RT --> VA[🏢 Vendor Approval]
    RT --> AP[👤 Associate Productivity]

    subgraph TOOLS[MCP Tool Layer — 11 tools]
        T1[get_community_metrics]
        T2[get_construction_delays]
        T3[calculate_incentive_impact]
        T4[generate_marketing_campaign]
        T5[get_vendor_profile / risk_score]
        T6[get_policy_workflow + RAG]
        T7[create_approval_request]
    end

    CP --> T1
    CD --> T2
    FI --> T3
    MC --> T4
    VA --> T5
    AP --> T6
    FI --> T7
    VA --> T7

    T1 & T2 & T3 & T4 & T5 & T6 & T7 --> DB[(PostgreSQL / SQLite)]
    AP --> RAG[(ChromaDB RAG Index)]

    CP & CD & FI & MC & VA & AP --> CG[🛡️ Critic / Governance Agent]
    CG -->|Validated + Risk Level| SYNTH[LLM Synthesis\nGPT-4o-mini / Bedrock / Claude]
    SYNTH --> AQ[✅ Approval Queue\nHuman-in-the-Loop]
    AQ --> AT[📋 Audit Trail]
    AQ --> MON[📊 Monitoring Dashboard]

    style ORCH fill:#dbeafe,stroke:#2563eb
    style TOOLS fill:#dcfce7,stroke:#16a34a
    style CG fill:#fef3c7,stroke:#d97706
    style AQ fill:#ede9fe,stroke:#7c3aed
"""

    components.html(f"""
<!DOCTYPE html>
<html>
<head>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<style>
  body {{ margin: 0; padding: 10px; background: white; font-family: sans-serif; }}
  .mermaid {{ max-width: 100%; }}
</style>
</head>
<body>
<div class="mermaid">
{mermaid_diagram}
</div>
<script>
  mermaid.initialize({{
    startOnLoad: true,
    theme: 'base',
    themeVariables: {{
      primaryColor: '#f0f9ff',
      primaryBorderColor: '#2563eb',
      fontFamily: 'sans-serif',
      fontSize: '13px'
    }}
  }});
</script>
</body>
</html>
""", height=720, scrolling=True)

    st.caption("Rendered with Mermaid.js. See also: ASCII diagram below.")

    with st.expander("ASCII diagram (copy-paste friendly)", expanded=False):
        st.markdown("""
```
User Request → Executive Orchestrator (LangGraph classify → route → synthesize → finalize)
  ↓
Specialist Agents (each skips if not selected)
  ├─ Community Performance  → get_community_metrics, get_inventory_status, get_lead_conversion
  ├─ Construction Delay     → get_construction_delays
  ├─ Finance / Incentive    → calculate_incentive_impact  [enforces 1.5% margin policy]
  ├─ Marketing Campaign     → generate_marketing_campaign
  ├─ Vendor Approval        → get_vendor_profile, get_vendor_risk_score  [blocks expired insurance]
  └─ Associate Productivity → get_policy_workflow  [ChromaDB RAG + OpenAI embeddings]
  ↓
MCP Tool Layer → PostgreSQL / SQLite + ChromaDB RAG Index
  ↓
Critic / Governance Agent  [validates evidence · enforces policies · assigns risk]
  ↓
LLM Synthesis  [GPT-4o-mini / Claude Haiku / AWS Bedrock]
  ↓
Finalize  [creates per-action approval_requests · writes audit_events]
  ↓
Approval Queue → Audit Trail → Monitoring Dashboard
```
""")

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
            f"<span style='background:rgba(128,128,128,0.1);border-radius:4px;padding:2px 8px;font-size:0.8rem;'>{category}</span>",
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
    st.subheader("30-Day Foundry Migration Plan")
    st.info(
        "Give me Foundry access on Day 1 and here is exactly what I deliver — "
        "week by week — translating this platform into native AIP.",
        icon="📅",
    )

    weeks = [
        {
            "week": "Week 1",
            "title": "Ontology + Data Layer",
            "foundry": "Foundry Object Types + Links",
            "ours": "PostgreSQL schema (13 tables)",
            "deliverable": (
                "Model Community, Vendor, Policy, AgentRun, ApprovalRequest as Foundry Object Types. "
                "Define Links between them (Community → Homes, AgentRun → ToolCalls). "
                "Import seed data via Foundry Pipeline. "
                "Output: Ontology with 8 object types, queryable from AIP."
            ),
        },
        {
            "week": "Week 2",
            "title": "Function Registry + Tool Layer",
            "foundry": "AIP Function Registry",
            "ours": "MCP Tool Registry (11 tools)",
            "deliverable": (
                "Register all 11 tool functions in Foundry's Function Registry with typed input/output schemas. "
                "Port the MCP server to Foundry Code Workspaces. "
                "Wire each function to the Ontology objects (get_community_metrics reads from Community object type). "
                "Output: 11 callable AIP Functions, testable from AIP Studio."
            ),
        },
        {
            "week": "Week 3",
            "title": "Agent Blueprints + Logic",
            "foundry": "AIP Agent Blueprints + AIP Logic",
            "ours": "LangGraph graph + agent_configs",
            "deliverable": (
                "Define each of the 8 specialist agents as AIP Agent Blueprints with persona, allowed functions, "
                "and approval rules. Port the LangGraph classification → routing → validation logic to AIP Logic. "
                "Connect the Critic Agent as a validation step before any AIP Action is surfaced. "
                "Output: Full multi-agent pipeline running natively in AIP."
            ),
        },
        {
            "week": "Week 4",
            "title": "AIP Actions + Governance",
            "foundry": "AIP Actions + Audit Log",
            "ours": "Approval Queue + audit_events",
            "deliverable": (
                "Build AIP Actions for every approved recommendation type: "
                "apply_incentive, launch_campaign, escalate_delay, approve_vendor. "
                "Wire approval rules (contract > $50K → manager approval, margin > 1.0% → CFO). "
                "Connect to Foundry Audit Log for immutable decision trail. "
                "Output: Full human-in-the-loop AIP platform, production-ready."
            ),
        },
    ]

    for w in weeks:
        with st.container(border=True):
            wl, wr = st.columns([1, 4])
            with wl:
                st.markdown(
                    f"<div style='background:var(--primary-color);color:white;border-radius:8px;"
                    f"padding:0.5rem;text-align:center;font-weight:700;'>{w['week']}</div>",
                    unsafe_allow_html=True,
                )
            with wr:
                st.markdown(f"**{w['title']}**")
                st.markdown(
                    f"<span style='font-size:0.82rem;opacity:0.55;'>"
                    f"Foundry: `{w['foundry']}` ← maps from: `{w['ours']}`</span>",
                    unsafe_allow_html=True,
                )
            st.markdown(f"*Deliverable:* {w['deliverable']}")

    st.markdown("---")
    st.subheader("The Core Principle")
    st.markdown("""
The primary difference between this platform and a native Foundry deployment is the runtime — Foundry is managed, proprietary, and enterprise-integrated. This platform is open, Python-first, and deployable anywhere.

**The architectural concepts, design decisions, and production concerns are identical.**

Every agent I've built here would work in AIP. Every approval rule I've defined maps to an AIP Action. Every tool in the MCP registry translates to a Foundry Function. The data model is already structured as an Ontology.

I designed it this way intentionally.
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

# ── Tab: Prompt Engineering ───────────────────────────────────────────────────
with tab_prompts:
    st.subheader("Prompt Engineering")
    st.caption(
        "The exact system prompts and user message templates powering every LLM call in the pipeline. "
        "Each prompt is designed to enforce evidence grounding, prevent hallucination, and produce parseable outputs."
    )

    st.markdown("### Design Principles")
    p1, p2, p3 = st.columns(3)
    with p1:
        st.markdown("**Single-output classification**")
        st.markdown(
            "<span style='font-size:0.85rem;opacity:0.65;'>"
            "Classify prompts return one word only — no explanation, no ambiguity. "
            "Output is machine-parseable without regex; rule-based fallback runs first."
            "</span>", unsafe_allow_html=True,
        )
    with p2:
        st.markdown("**Evidence-before-synthesis**")
        st.markdown(
            "<span style='font-size:0.85rem;opacity:0.65;'>"
            "The executive summary LLM receives pre-validated agent findings, not raw user input. "
            "A hard constraint ('Do not add claims not supported by the findings') closes the hallucination loop."
            "</span>", unsafe_allow_html=True,
        )
    with p3:
        st.markdown("**Deterministic governance**")
        st.markdown(
            "<span style='font-size:0.85rem;opacity:0.65;'>"
            "The Critic / Governance Agent makes zero LLM calls. "
            "Approval triggers and risk levels are deterministic Python lambdas — they cannot be convinced by natural language."
            "</span>", unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### Agent Prompts")

    with st.expander("**classify_node** — Request Classification (Executive Orchestrator)", expanded=True):
        lc, rc = st.columns([3, 2])
        with lc:
            st.markdown("**System prompt**")
            st.code(
                "Route this business question to the right analysis team at a national homebuilder.\n\n"
                "Respond with exactly one category name — nothing else.\n\n"
                "sales_ops  — community performance, sales targets, inventory, lead conversion.\n"
                "             Example: 'Why is Coral Bay behind target this month?'\n\n"
                "incentive  — pricing, discounts, margin impact, financial levers for sales.\n"
                "             Example: 'Can we offer 2% off to move stale homes?'\n\n"
                "vendor     — vendor approval, risk review, insurance, procurement.\n"
                "             Example: 'Should we approve Coastal Electrical for the contract?'\n\n"
                "workflow   — how-to questions, policies, step-by-step processes.\n"
                "             Example: 'How do I onboard a new subcontractor?'\n\n"
                "general    — strategy, market expansion, comparisons, or anything not clearly above.\n"
                "             Example: 'Which community should we use as a template for expansion?'\n\n"
                "One word only.",
                language="text",
            )
        with rc:
            st.markdown("**Design decisions**")
            for note in [
                "Concrete examples per category — LLM anchors to cases, not just descriptions",
                "`general` explicitly covers strategy and expansion — previously 'anything else'",
                "`One word only` — zero-parse output, no regex needed",
                "Rule-based classifier runs first; LLM only overrides when key is present",
            ]:
                st.markdown(f"- {note}")

    with st.expander("**generate_response_node** — Executive Synthesis (Executive Orchestrator)"):
        lc, rc = st.columns([3, 2])
        with lc:
            st.markdown("**System prompt**")
            st.code(
                "You are a senior operations analyst writing a briefing for the executive team\n"
                "of a national homebuilder.\n\n"
                "Using only the agent findings provided, write a 3 to 5 sentence executive summary.\n\n"
                "Structure:\n"
                "- First sentence: the core situation or problem, with specific numbers\n"
                "- Middle: root cause or key driver, referencing community names and data\n"
                "- Last sentence: recommended direction and any constraints that apply\n\n"
                "Rules:\n"
                "- Do not introduce any fact, number, or claim not present in the findings\n"
                "- Reference specific names, percentages, and figures from the data\n"
                "- Write in flowing prose — no bullet points, no headers\n\n"
                "Audience: CFO or COO. Direct, data-backed, no filler.",
                language="text",
            )
            st.markdown("**User message template**")
            st.code(
                "Business question: {user_prompt}\n\n"
                "Agent findings:\n"
                "[Community Performance Agent] {finding}\n"
                "[Finance / Incentive Agent] {finding}\n"
                "[Critic / Governance Agent] {finding}\n"
                "...",
                language="text",
            )
        with rc:
            st.markdown("**Design decisions**")
            for note in [
                "LLM receives validated agent findings, not raw user input — blocks prompt injection",
                "`Do not introduce any fact not in the findings` — hard evidence constraint",
                "Explicit 3-part structure: problem → root cause → recommendation",
                "`3-5 sentences` — more room for complex multi-agent runs than the old 3-4",
                "`Audience: CFO or COO` — one line that anchors tone and eliminates filler",
            ]:
                st.markdown(f"- {note}")

    with st.expander("**associate_productivity** — Corporate Workflow Advisor"):
        lc, rc = st.columns([3, 2])
        with lc:
            st.markdown("**System prompt**")
            st.code(
                "You are a corporate workflow advisor at a national homebuilder.\n\n"
                "An associate has asked a question about a process or policy.\n"
                "Answer using the policy steps provided.\n\n"
                "Requirements:\n"
                "- Answer directly in 2 to 3 sentences\n"
                "- Cite the policy name in your answer\n"
                "- State the approval threshold and who must sign off\n"
                "- If the policy steps do not fully answer the question, say so explicitly\n\n"
                "Professional tone. No bullet points.",
                language="text",
            )
            st.markdown("**User message template**")
            st.code(
                "Associate question: {user_prompt}\n\n"
                "Policy: {policy_title} ({business_function})\n"
                "Steps:\n"
                "1. {step_1}\n"
                "2. {step_2}\n"
                "...\n"
                "Approval threshold: ${threshold}\n"
                "Escalation rule: {escalation_rule}",
                language="text",
            )
        with rc:
            st.markdown("**Design decisions**")
            for note in [
                "Policy retrieved via ChromaDB RAG *before* the LLM call",
                "LLM answers from retrieved steps — not from training-data memory",
                "Approval thresholds injected explicitly — LLM cannot hallucinate them",
                "`Cite the policy name` — grounds the answer, prevents vague responses",
                "Explicit fallback instruction when policy doesn't cover the question",
            ]:
                st.markdown(f"- {note}")

    with st.expander("**critic_validate** — Governance Agent (No LLM — Deterministic)"):
        lc, rc = st.columns([3, 2])
        with lc:
            st.markdown("**No system prompt — pure Python:**")
            st.code(
                """APPROVAL_TRIGGERS = [
    ("incentive",           lambda tr: any(
        not r.get("blocked_by_policy")
        and abs(r.get("margin_impact_pct", 0)) >= 1.0
        for r in (tr.get("incentive") or {}).values()
    )),
    ("vendor_high_risk",    lambda tr: any(
        d["profile"]["risk_level"] == "high"
        for d in tr.get("vendor", {}).values()
    )),
    ("vendor_insurance",    lambda tr: any(
        d["profile"]["insurance_status"] != "current"
        for d in tr.get("vendor", {}).values()
    )),
    ("construction_10plus", lambda tr:
        tr.get("construction_delays", {})
          .get("total_affected_closings", 0) > 10),
    ("campaign",            lambda tr: "campaign" in tr),
]""",
                language="python",
            )
        with rc:
            st.markdown("**Why no LLM?**")
            st.markdown(
                "Governance decisions must be **deterministic and auditable**. "
                "An LLM-based critic could approve a high-risk vendor given a well-crafted prompt. "
                "These lambda rules cannot be convinced by natural language — the check is binary."
            )
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**What it checks:**")
            for note in [
                "Evidence completeness (were tool calls made?)",
                "Unsupported claims (findings without tool evidence)",
                "5 approval triggers: incentive, vendor risk, insurance, delays, campaigns",
                "Risk escalation: low → medium → high based on which triggers fire",
            ]:
                st.markdown(f"- {note}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("Source: `agents/executive.py` · `agents/associate_productivity.py` · `agents/critic.py`")

st.markdown("---")
st.caption("Built by Rodrigo Rosa — Software Engineer & Technical Founder")
