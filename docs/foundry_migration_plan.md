# Palantir Foundry Migration Plan
## HomeBuilder Workforce AI → Native AIP Deployment

**Timeline:** 30 days from Foundry access  
**Output:** Production multi-agent AIP platform running on Lennar's Foundry instance

---

## Concept Mapping Reference

| This Platform | Foundry / AIP Equivalent | Status |
|---|---|---|
| PostgreSQL schema (13 tables) | Foundry Ontology (Object Types + Links) | Ready to port |
| MCP Tool Registry (11 tools) | AIP Function Registry | Ready to port |
| agent_configs table | AIP Agent Blueprints | Ready to port |
| LangGraph StateGraph | AIP Logic / Pipeline | Ready to port |
| Approval Queue + APRs | AIP Actions | Ready to port |
| Audit Trail (audit_events) | Foundry Audit Log | Ready to port |
| Agent Builder UI | AIP Studio | Ready to port |
| ChromaDB RAG Index | AIP Retrieval | Ready to port |
| Monitoring Dashboard | Foundry Operational Layer | Ready to port |
| Critic / Governance Agent | AIP Safety + Guardrails | Ready to port |

---

## Week 1: Foundry Ontology

**Goal:** All enterprise data modeled as typed Foundry objects.

**From:** PostgreSQL 13-table schema (communities, homes, leads, vendors, policies, etc.)

**Deliverables:**
- `Community` Object Type — region, sales targets, actuals, stale inventory count
- `Vendor` Object Type — risk score, insurance status, payment history, contract value
- `Policy` Object Type — business function, steps, approval threshold, escalation rule
- `ConstructionDelay` Object Type — severity, delayed_days, responsible_party
- `AgentRun` Object Type — prompt, status, risk_level, approval_required
- `ApprovalRequest` Object Type — recommended_action, risk_level, required_approver, status
- Links: Community → ConstructionDelay, AgentRun → ApprovalRequest, AgentRun → ToolCall
- Data import pipeline from existing PostgreSQL

**Success criterion:** All 6 communities, 5 vendors, 5 policies queryable from AIP Studio.

---

## Week 2: AIP Function Registry

**Goal:** All 11 tool functions registered and callable from AIP.

**From:** `tools/` Python modules + `mcp_server/server.py`

**Deliverables:**

| AIP Function | Source | Reads From |
|---|---|---|
| `get_community_metrics` | community_tools.py | Community Object Type |
| `get_inventory_status` | community_tools.py | Community + Home Object Types |
| `get_lead_conversion` | community_tools.py | Lead Object Type |
| `get_construction_delays` | construction_tools.py | ConstructionDelay Object Type |
| `calculate_incentive_impact` | finance_tools.py | Home Object Type + Policy |
| `get_vendor_profile` | vendor_tools.py | Vendor Object Type |
| `get_vendor_risk_score` | vendor_tools.py | Vendor Object Type |
| `get_policy_workflow` | policy_tools.py | Policy Object Type (+ RAG) |
| `create_approval_request` | approval_tools.py | Creates ApprovalRequest Object |
| `generate_marketing_campaign` | marketing_tools.py | Community Object Type |
| `create_executive_report` | audit_tools.py | AgentRun Object Type |

**Success criterion:** Each function callable from AIP Studio with typed inputs/outputs.

---

## Week 3: AIP Agent Blueprints + Logic

**Goal:** All 8 specialist agents defined as AIP Blueprints, pipeline running in AIP.

**From:** `agents/` Python modules + `agents/graph.py` (LangGraph StateGraph)

**Agent Blueprint definitions:**

```
Associate Productivity Blueprint
  Persona: Corporate Workflow Advisor
  Allowed functions: get_policy_workflow, create_approval_request
  Approval rule: Creates draft only — no auto-submit
  Safety rule: Never advise without citing a policy source

Vendor Approval Blueprint
  Persona: Procurement Risk Analyst
  Allowed functions: get_vendor_profile, get_vendor_risk_score, create_approval_request
  Approval rule: Required for contract > $50K, expired insurance, risk > 70
  Safety rule: Block expired insurance vendors — no exceptions

[... one Blueprint definition per agent ...]
```

**Pipeline (AIP Logic equivalent of LangGraph graph):**
```
classify_request → route_to_agents → [specialist agents] → critic_validate → synthesize → finalize
```

**Success criterion:** Full pipeline runs end-to-end in AIP Studio on a test prompt.

---

## Week 4: AIP Actions + Governance

**Goal:** Human-in-the-loop approval workflows live in Foundry.

**From:** `pages/approval_queue.py` + `services/approval_service.py`

**AIP Actions to define:**

| Action | Trigger condition | Required approver |
|---|---|---|
| `apply_incentive` | Finance agent recommends incentive | VP Sales or CFO (based on %) |
| `launch_campaign` | Marketing agent generates copy | Regional Marketing Director |
| `escalate_delay` | > 10 closings affected | Regional Operations Manager |
| `approve_vendor` | Vendor passes risk checks | Regional Ops Manager (> $50K) |
| `block_vendor` | Expired insurance or risk > 70 | VP Procurement |

**Approval rules wired as AIP guardrails:**
- Margin impact > 1.5%: hard block (no human can override in AIP Action)
- Vendor insurance expired: hard block until renewed
- Contract > $200K: VP Procurement required — no delegation
- Pending > 24h: auto-escalate to next approver level

**Audit integration:** Every AIP Action decision writes to Foundry Audit Log with actor, timestamp, risk level, and decision reason.

**Success criterion:** Full demo scenario runs on Foundry — approve/reject actions write to Ontology objects and Audit Log.

---

## What I'd Do Differently Native on Foundry

1. **Replace ChromaDB RAG** with Foundry's native document retrieval — better integration with Lennar's internal document corpus
2. **Event-triggered agents** — Foundry Pipelines can trigger agent runs on Ontology changes (e.g., when a delay is logged, the Construction Delay agent fires automatically)
3. **Deeper Ontology modeling** — in this platform, relationships are foreign keys. In Foundry, they're first-class Links with traversal queries
4. **Code Workspaces** — run the Python agent logic directly in Foundry's managed environment with access to all Lennar data

---

## Questions for Day 1

Before starting the migration, I'd want to understand:
1. Which Foundry modules does Lennar have licensed? (AIP Studio, Code Workspaces, AIP Actions?)
2. What data is already in the Foundry Ontology? (CRM, ERP, HRIS objects?)
3. What's the existing AIP SDK version?
4. Who owns the Foundry Function Registry — is there an existing review/approval process for registering new functions?
5. What are the data access policies — can agents read from production Ontology objects or only staging?

These answers determine whether Week 1 is Ontology design or Ontology extension.
