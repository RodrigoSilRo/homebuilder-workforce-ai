# HomeBuilder Workforce AI

> A production-ready internal AI agent platform for a national homebuilder — built to demonstrate exactly what the **Agent Builder** role requires: multi-agent orchestration, enterprise data workflows, human-in-the-loop governance, MCP tool integration, and production observability.

**Live demo:** [homebuilder-workforce-ai.onrender.com](https://homebuilder-workforce-ai.onrender.com)

---

## The Business Problem This Solves

A large homebuilder runs thousands of operational decisions every week — vendor approvals, community performance reviews, construction delay escalations, incentive authorizations, associate workflow questions. Today most of these require manual research, email chains, and spreadsheets.

This platform deploys specialized AI agents to automate the investigation, synthesize the evidence, enforce the policies, and route to the right human for final approval — reducing decision cycle time while maintaining full governance and auditability.

**This is not a chatbot. It is an internal AI workforce.**

---

## What It Demonstrates

Every item on the Agent Builder job description is directly implemented:

| Responsibility | Implementation |
|---|---|
| Agent personas, roles, workflows | 8 specialist agents with defined personas, tools, and approval rules |
| Decision logic, triggers, escalation paths | LangGraph 10-node pipeline, 24h auto-escalation, risk-tier routing |
| Human-in-the-loop rules | Per-action approval requests, Approve/Reject/Escalate with full audit |
| LLMs + RAG + orchestration tools | GPT-4o-mini / Claude / AWS Bedrock + ChromaDB semantic policy search |
| Tool invocations + API integration | 11 MCP tools, logged on every call, callable from Claude Desktop |
| Monitoring / observability | Live dashboard: agent runs, tool latency, eval pass rates, drift detection |
| Governance, audit trails, output safety | Critic agent, immutable audit_events table, policy enforcement |
| Agent lifecycle + versioning | agent_configs table with version field, Agent Builder UI |
| Documentation + workflow diagrams | See `docs/` folder: agent specs, workflow diagrams, Foundry migration plan |

---

## Architecture

```
User Request
    ↓
Executive Orchestrator  [LangGraph classify → route → synthesize → finalize]
    ↓
Specialist Agents  [run in parallel lanes, skip if not selected]
  ├─ Community Performance  →  get_community_metrics, get_inventory_status, get_lead_conversion
  ├─ Construction Delay     →  get_construction_delays
  ├─ Finance / Incentive    →  calculate_incentive_impact  [enforces 1.5% margin limit]
  ├─ Marketing Campaign     →  generate_marketing_campaign
  ├─ Vendor Approval        →  get_vendor_profile, get_vendor_risk_score  [blocks expired insurance]
  └─ Associate Productivity →  get_policy_workflow  [RAG: ChromaDB + OpenAI embeddings]
    ↓
Critic / Governance Agent  [validates evidence, enforces policies, assigns risk]
    ↓
LLM Synthesis  [GPT-4o-mini / Claude Haiku / AWS Bedrock — swappable via services/llm.py]
    ↓
Finalize  [creates per-action approval_requests, writes to audit_events]
    ↓
Approval Queue → Audit Trail → Monitoring Dashboard
```

Full architecture diagram (Mermaid + Palantir Foundry mapping): see **Architecture** page in the app.

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| UI | Streamlit | Python-native, enterprise-ready, fast to iterate |
| Agent orchestration | LangGraph 1.2 | Production-grade StateGraph, observable, deterministic |
| Tool protocol | Python MCP SDK (FastMCP) | Model Context Protocol — connects to Claude Desktop, Cursor, any MCP client |
| RAG | ChromaDB + OpenAI text-embedding-3-small | Semantic policy retrieval — closes the "retrieval-augmented frameworks" requirement |
| LLM | OpenAI → Anthropic → AWS Bedrock | Priority routing, same interface via `services/llm.py` |
| Database | PostgreSQL (prod) / SQLite (local) | Same SQLAlchemy queries, same schema — zero config locally |
| Evals | pytest + custom declarative runner | 4 eval cases, 20 tests, 4/4 passing |
| Deployment | Docker Compose + Render | `render.yaml` pre-configured |

---

## Quick Start (Local)

```bash
git clone https://github.com/RodrigoSilRo/homebuilder-workforce-ai
cd homebuilder-workforce-ai

pip install -r requirements.txt

# Add your OpenAI key (app runs without it in rule-based mode)
cp .env.example .env
# Edit .env: OPENAI_API_KEY=sk-...

# Start — auto-seeds DB and RAG index on first run
python -m streamlit run app.py
```

Open http://localhost:8501

---

## Demo: Three Scenarios

### 1. Homebuilding Operations
> *"Why are South Florida communities underperforming this month, and what can we do without reducing gross margin by more than 1.5%?"*

Watch: Community Performance → Construction Delay → Finance → Marketing agents fire in sequence. Finance agent blocks the 2.0% incentive scenario on policy. Critic validates evidence. LLM writes the executive summary from real data. Approval requests are auto-created for the recommended actions.

### 2. Vendor Risk
> *"Which vendor approvals need escalation?"*

Watch: Vendor Approval agent flags Coastal Electrical LLC — expired insurance, risk score 78, $72K contract. Three escalation triggers fire. An approval request is auto-routed to VP Procurement. Check the Approval Queue immediately after.

### 3. Associate Productivity + Governance
> *"What workflow should an associate follow to onboard a new subcontractor?"*

Watch: Associate Productivity agent performs semantic RAG search over the policy knowledge base. Returns the 7-step Vendor Onboarding workflow with approval thresholds and escalation rules. No LLM hallucination — every claim is grounded in a policy record from the database. Then show: Audit Trail → Monitoring Dashboard → Run All Evals.

---

## Palantir Foundry Readiness

This platform maps 1:1 to Palantir AIP concepts by design:

| This Platform | Foundry / AIP Equivalent |
|---|---|
| Approval Queue | AIP Actions |
| MCP Tool Registry | Function Registry |
| agent_configs table | AIP Agent Blueprints |
| LangGraph StateGraph | AIP Logic / Pipeline |
| PostgreSQL schema | Foundry Ontology |
| Audit Trail | Foundry Audit Log |
| Agent Builder UI | AIP Studio |

See `docs/foundry_migration_plan.md` for the full 30-day translation plan.

---

## Running Evals

```bash
# All 4 eval cases — 4/4 passing
python -m evals.run_evals --verbose

# pytest suite — 20 tests
pytest evals/test_agent_flows.py -v
```

**Eval cases:**
- `EVAL-001` — Margin constraint enforcement (blocks 2.0% incentive) — PASS
- `EVAL-002` — Vendor approval high risk (expired insurance → blocks) — PASS
- `EVAL-003` — Associate workflow guidance (RAG policy retrieval) — PASS
- `EVAL-004` — Unsupported claim guardrail (Critic requires evidence) — PASS

---

## MCP Server (Claude Desktop Integration)

```bash
# Start the MCP server
python -m mcp_server.server

# Add to Claude Desktop (~/.claude/claude_desktop_config.json):
```
```json
{
  "mcpServers": {
    "homebuilder-workforce-ai": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "/path/to/homebuilder-workforce-ai"
    }
  }
}
```

Then ask Claude: *"Use get_community_metrics for South Florida"* — it calls your local database and returns real data.

---

## Docker

```bash
# Local with PostgreSQL
docker compose up

# Single container (SQLite)
docker build -t homebuilder-workforce-ai .
docker run -p 8501:8501 -e OPENAI_API_KEY=sk-... homebuilder-workforce-ai
```

---

## Environment Variables

```bash
OPENAI_API_KEY=sk-...           # Primary LLM — GPT-4o-mini
ANTHROPIC_API_KEY=sk-ant-...    # Alternative — Claude Haiku
AWS_ACCESS_KEY_ID=...           # AWS Bedrock option
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
AWS_BEDROCK_MODEL=anthropic.claude-haiku-4-5-20251001-v1:0
DATABASE_URL=postgresql://...   # Production PostgreSQL (SQLite default locally)
```

---

## Documentation

```
docs/
  agent_specs.md          — Full specification for all 8 agents
  workflow_diagrams.md    — Key workflow diagrams (vendor onboarding, incentive approval, etc.)
  demo_script.md          — Structured demo walkthrough
  foundry_migration_plan.md — 30-day plan to deploy this on Palantir Foundry
```

---

## Built By

**Rodrigo Rosa** — Software Engineer & Technical Founder

> HomeBuilder Workforce AI is a production-style multi-agent platform that demonstrates how AI agents can be deployed responsibly across enterprise homebuilding operations — with proper governance, human oversight, and the kind of auditability that legal and compliance teams actually require.
