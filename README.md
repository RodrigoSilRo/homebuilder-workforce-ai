# HomeBuilder Workforce AI

**A production-style Python multi-agent platform for homebuilding operations, corporate workflow automation, and associate productivity.**

Built with LangGraph, MCP, PostgreSQL, OpenAI/Claude API, Streamlit, and human-in-the-loop approval workflows.

---

## One-Sentence Pitch

HomeBuilder Workforce AI is a Python-based multi-agent platform for homebuilding companies that helps associates navigate workflows, automate corporate processes, analyze operational data, and execute human-approved actions through monitored, auditable AI agents.

---

## Why This Exists

This platform demonstrates production-grade AI agent engineering applied to enterprise homebuilding operations. It is designed to show how AI agents can be deployed across corporate functions — not as a chatbot, but as a structured, governed workforce of specialized agents that operate within defined policies, require human approval for high-risk decisions, and leave a complete audit trail.

Every design decision maps to a real production concern:

- LangGraph for reliable, observable multi-agent orchestration
- PostgreSQL for enterprise-grade data persistence
- MCP for standardized tool integration (callable from Claude Desktop, Cursor, or any MCP client)
- Human-in-the-loop approval queues with escalation rules
- Declarative eval cases with a drift detection dashboard
- Governance agent that validates evidence before any recommendation is surfaced

---

## Architecture

```
User Request
    ↓
Executive Orchestrator (LangGraph classify node)
    ↓
Specialist Agents (run in sequence, skip if not selected)
  ├── Community Performance Agent   → get_community_metrics, get_inventory_status, get_lead_conversion
  ├── Construction Delay Agent      → get_construction_delays
  ├── Finance / Incentive Agent     → calculate_incentive_impact
  ├── Marketing Campaign Agent      → generate_marketing_campaign
  ├── Vendor Approval Agent         → get_vendor_profile, get_vendor_risk_score
  └── Associate Productivity Agent  → get_policy_workflow
    ↓
Critic / Governance Agent (validates evidence, assigns risk, enforces policies)
    ↓
LLM Synthesis (GPT-4o-mini or Claude Haiku — or rule-based if no key)
    ↓
Finalize Node (creates per-action approval requests, logs to DB)
    ↓
Approval Queue → Audit Trail → Monitoring Dashboard
```

**MCP Tool Layer** sits between agents and data — all 11 tools are callable via `python -m mcp_server.server` from any MCP-compatible client.

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI | Streamlit |
| Agent orchestration | LangGraph 1.2 |
| LLM | OpenAI GPT-4o-mini / Anthropic Claude Haiku (configurable) |
| Tool protocol | Python MCP SDK (FastMCP) |
| Database | PostgreSQL (production) / SQLite (local dev, auto-configured) |
| ORM / queries | SQLAlchemy 2.0 |
| Validation | Pydantic (agent state) |
| Data viz | Plotly |
| Testing | pytest |
| Containerization | Docker + Docker Compose |
| Deployment | Render / Railway / Fly.io |
| Language | Python 3.11+ |

---

## Features

### Agent Operations
- **Executive Command Center** — prompt → LangGraph pipeline → live agent activity feed → evidence-backed recommendation → approve/reject/escalate
- **Agent Marketplace** — 8 pre-built agents with defined roles, tools, approval rules, and example prompts
- **Agent Builder** — define new agent configurations (name, persona, tools, approval rules, escalation rules, safety rules)

### Governance
- **Approval Queue** — per-action approval requests with overdue detection, auto-escalation after 24h, decision logging
- **Audit Trail** — immutable event log of every agent run, tool call, approval decision, and escalation

### Platform
- **MCP Tool Registry** — 11 tools registered with FastMCP, callable from Claude Desktop or any MCP client
- **Monitoring Dashboard** — KPIs, 30-day run chart, tool latency, eval pass/fail history, drift detection
- **Architecture** — system diagram, component table, Palantir Foundry mapping

### Eval Suite
- 4 declarative eval cases (margin constraint, vendor risk, associate workflow, unsupported claim guardrail)
- CLI runner (`python -m evals.run_evals`) and pytest suite (`pytest evals/test_agent_flows.py`)
- Results persisted to `eval_runs` table for drift detection

---

## Local Setup

**Requirements:** Python 3.11+, pip

```bash
git clone https://github.com/your-username/homebuilder-workforce-ai
cd homebuilder-workforce-ai

pip install -r requirements.txt

# Copy and fill in your API key (optional — app works without one)
cp .env.example .env

# Start the app (auto-seeds DB on first run)
python -m streamlit run app.py
```

Open http://localhost:8501

---

## Environment Variables

```bash
# LLM (optional — app runs in rule-based mode without a key)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...    # Alternative to OpenAI

# Database (optional — SQLite used by default for local dev)
DATABASE_URL=postgresql://user:password@localhost:5432/homebuilder
```

---

## Database Setup

The database is auto-initialized and seeded on first app startup. To manually seed:

```bash
python -m database.seed_data
```

**Seeded data:**
- 6 communities (South Florida, Central Florida, Texas, Carolinas)
- 239 homes with realistic days-on-market and margin data
- 525 leads with community-specific conversion rates
- 19 active construction delays (Ocean Vista critical, Willow Creek medium)
- 5 vendors (Coastal Electrical LLC flagged: expired insurance, risk score 78)
- 5 policies (vendor onboarding, invoice approval, marketing campaign, construction delay, incentive)
- 47 historical agent runs + 150+ tool call records for monitoring charts
- 6 approval requests across all risk levels
- 15 audit events with full event type coverage
- 4 eval cases

**PostgreSQL migration:** Set `DATABASE_URL` in `.env` and the app uses it automatically. Schema is compatible with both SQLite and PostgreSQL.

---

## Agent Architecture

Each specialist agent:
1. Checks whether it's in `selected_agents` — if not, passes through the graph node without executing
2. Calls its tools (all tool calls are logged to `tool_calls` table automatically)
3. Formats findings into a structured output dict
4. Updates shared `AgentState` (tool_results, agent_outputs, risk_level, approval_required)

The **Critic / Governance Agent** always runs last before synthesis:
- Validates evidence coverage (were tools called before any claim?)
- Detects unsupported attributions
- Evaluates 5 approval trigger rules (incentive > 1.0% margin, vendor insurance expired, >10 closings affected, customer-facing campaign, vendor contract > $50K)
- Assigns risk level and approval_required flag

---

## MCP Tools

All 11 tools are exposed via the MCP server. Connect from Claude Desktop by adding to your config:

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

**Available tools:**
`get_community_metrics` · `get_inventory_status` · `get_lead_conversion` · `get_construction_delays` · `calculate_incentive_impact` · `get_vendor_profile` · `get_vendor_risk_score` · `get_policy_workflow` · `create_approval_request` · `generate_marketing_campaign` · `create_executive_report`

---

## Monitoring & Governance

**Monitoring Dashboard** tracks:
- Total agent runs, success rate, failed tool calls, avg latency
- Agent runs over time (30-day chart)
- Tool latency and reliability per tool
- Approval rate, escalation rate
- Eval pass/fail history and drift detection chart

**Approval Rules:**
- Contract value > $50,000 → Regional Operations Manager approval
- Contract value > $200,000 → VP Procurement approval
- Margin impact > 0.5% → VP Sales approval
- Margin impact > 1.0% → CFO approval
- Margin impact > 1.5% → blocked by policy
- Customer-facing campaign → Marketing Director approval
- Vendor insurance expired → blocked until renewed
- Construction delay > 10 closings → VP Operations notification

**Escalation Rules:**
- Pending approval > 24 hours → auto-escalate to next approver level
- High-risk vendor → immediate VP Procurement routing
- Critical construction delay → auto-escalate

---

## Running Evals

```bash
# Run all evals with verbose output
python -m evals.run_evals --verbose

# Run a specific eval
python -m evals.run_evals --eval EVAL-001

# Run as pytest
pytest evals/test_agent_flows.py -v
```

**Eval cases:**
- `EVAL-001` — Margin Constraint Enforcement (Finance, CRITICAL)
- `EVAL-002` — Vendor Approval High Risk (Procurement, CRITICAL)
- `EVAL-003` — Associate Workflow Guidance (Compliance, HIGH)
- `EVAL-004` — Unsupported Claim Guardrail (Governance, HIGH)

---

## Docker

**Local (SQLite):**
```bash
docker build -t homebuilder-workforce-ai .
docker run -p 8501:8501 -e OPENAI_API_KEY=sk-... homebuilder-workforce-ai
```

**With PostgreSQL:**
```bash
docker compose up
```

---

## Deployment

**Render (recommended for demo):**
```bash
# Push to GitHub, connect repo to Render, set env vars in dashboard
# render.yaml is pre-configured
```

**Railway:**
```bash
railway login
railway init
railway up
```

**Fly.io:**
```bash
fly launch
fly secrets set OPENAI_API_KEY=sk-...
fly deploy
```

---

## Demo Script

### Demo 1 — Associate Productivity
**Prompt:** *What workflow should an associate follow to onboard a new subcontractor?*

Watch the Associate Productivity Agent retrieve the 7-step vendor onboarding policy from the DB, identify required approvers, and surface the escalation rules.

### Demo 2 — Homebuilding Operations
**Prompt:** *Why are South Florida communities underperforming this month?*

Watch Community Performance, Construction Delay, and Marketing agents fire in sequence. The Critic validates evidence. The LLM synthesizes a data-backed executive summary. Approval requests are auto-created for the campaign recommendation.

### Demo 3 — Vendor Risk
**Prompt:** *Which vendor approvals need escalation?*

Coastal Electrical LLC is flagged: expired insurance, risk score 78, $72K contract. High-risk routing fires automatically. Check the Approval Queue — a new APR appears.

### Demo 4 — Governance
Show: Approval Queue → approve an action → Audit Trail → see the decision logged → Monitoring Dashboard → run all evals.

---

## Future Improvements

- pgvector RAG for semantic policy retrieval
- AWS Bedrock as LLM backend option
- Full dynamic Agent Builder (live graph compilation)
- Auth layer (Streamlit + JWT or Clerk)
- PDF executive report export
- Slack/Teams notification webhooks for approval requests
- A/B eval comparison across LLM model versions
- Palantir Foundry AIP Actions integration

---

## Author

Built by **Rodrigo Rosa** — Software Engineer & Technical Founder

> HomeBuilder Workforce AI is a production-style multi-agent platform designed around enterprise homebuilding operations. It demonstrates how AI agents can support associate productivity, vendor approvals, operational intelligence, human-in-the-loop workflows, MCP-based tool integration, monitoring, governance, and auditability.
