# Demo Script — HomeBuilder Workforce AI

A structured walkthrough for recruiting demos. Total time: ~12 minutes.
Three scenarios that cover all key capabilities.

---

## Setup (30 seconds)

Open the app at the deployed URL. Confirm:
- Green "LLM active" banner is visible (requires OPENAI_API_KEY in environment)
- The sidebar shows all 9 pages

Opening line:
> "This platform is a production prototype of what I'd build in the first month as an Agent Builder at a national homebuilder. It's not a chatbot — it's an AI workforce. Let me show you three scenarios."

---

## Demo 1: Homebuilding Operations Intelligence (5 minutes)

**Page:** Executive Command Center

**Select prompt:** *"Why are South Florida communities underperforming this month, and what can we do without reducing gross margin by more than 1.5%?"*

**Click:** Run Analysis

**Narrate as agents fire:**
- "The Executive Orchestrator classifies this as a sales_ops + incentive request and routes to four specialist agents."
- "Community Performance agent calls three real database tools — it's reading from actual seeded data, not hardcoded responses."
- "Construction Delay agent flags Ocean Vista — 14 closings at risk, responsible party identified."
- "Finance agent models three incentive scenarios. Watch — it automatically blocks the 2.0% scenario because our policy limit is 1.5%. That's a hard guardrail, not a soft suggestion."
- "Critic agent validates: 5 tool calls, no unsupported claims, medium risk."
- "GPT-4o-mini synthesizes the final executive summary from real data."

**Point to the right panel:**
- "Two approval requests were auto-created — one for VP Sales, one for the Marketing Director. Let's go check the Approval Queue."

**Navigate to Approval Queue, approve one, reject one.**

**Key point:** "Every decision writes to the audit trail in real time. Nothing happens without a human sign-off, and nothing disappears."

---

## Demo 2: Vendor Risk Governance (3 minutes)

**Page:** Executive Command Center

**Select prompt:** *"Which vendor approvals need escalation?"*

**Narrate:**
- "Vendor Approval agent checks our two pending vendors."
- "Coastal Electrical LLC: risk score 78, expired insurance, $72K contract. Three escalation triggers."
- "Watch the finding — it says 'Approval request created for high-risk vendor.' That's already in the queue."

**Navigate to Approval Queue:**
- "Here it is — APR flagged HIGH, routed to VP Procurement. The flags show exactly why: expired insurance, high risk score, contract over $50K."

**Key point:** "In a real deployment, this would trigger a Slack/Teams notification and a 24-hour escalation timer. If no one acts in 24 hours, it auto-escalates to the next approver level."

---

## Demo 3: Governance + Observability (4 minutes)

**Page:** Audit Trail
- "Every tool call, every approval decision, every agent run — logged here. Immutable. Filterable. Exportable."
- Filter by `approval_decision` → show the decisions you just made.

**Page:** Monitoring Dashboard → Evaluations tab
- "This is the part most AI demos skip — evals."
- Click **Run All Evals**.
- "Four declarative eval cases. They test real agent behavior against real data — no mocking. Margin constraint enforcement, vendor risk detection, policy retrieval accuracy, unsupported claim guardrail."
- "All four pass. If I break something in the codebase, the eval suite catches it before it ships."

**Page:** MCP Tool Registry
- "All 11 tools are also exposed via the Model Context Protocol. I can connect this to Claude Desktop and call `get_community_metrics` directly from a chat window. Or any MCP-compatible client."

**Page:** Architecture → Palantir Foundry Mapping tab
- "I know Palantir Foundry is central to Lennar's tech stack. I designed this platform with the same paradigm — AIP Actions map to our Approval Queue, Foundry Ontology maps to our database schema, Agent Blueprints map to our agent_configs. I have a 30-day translation plan ready."

---

## Closing (30 seconds)

> "This is what I'd ship in month one. Everything here runs on real data, enforces real policies, requires real human approvals, and leaves a complete audit trail. The agents, the governance rules, the approval workflows — these aren't demo fixtures. They're production patterns."

---

## Q&A Prep

**"Have you used Palantir Foundry?"**
> "Not directly — Foundry requires enterprise access. But I designed this platform with the AIP paradigm intentionally. I have a 30-day migration plan that translates every component. Give me Foundry access and I'm productive in week one."

**"How does this scale to real Lennar systems?"**
> "The data layer swaps to PostgreSQL with no code changes — just a DATABASE_URL. The tools would read from real ERP/CRM systems via API instead of our seeded database. The agent logic, governance rules, and approval workflows stay identical."

**"What would you add next?"**
> "pgvector for semantic search over internal documents — Lennar has a lot of policy and training content. A feedback loop where rejected actions improve future agent prompts. And Foundry's event triggers — agents that fire automatically on data changes, not just on user request."
