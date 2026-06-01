# Workflow Diagrams — HomeBuilder Workforce AI

Key business workflows implemented as agent automation pipelines.

---

## Workflow 1: Vendor Onboarding Approval

**Business trigger:** New subcontractor submitted for review  
**Agent:** Vendor Approval Agent  
**Policy:** Vendor Onboarding Policy (Procurement)

```
[Associate submits vendor request]
        ↓
[Vendor Approval Agent retrieves profile]
        ↓
   ┌────────────────────────────┐
   │ Risk Assessment            │
   │ • Insurance status         │
   │ • Risk score (0–100)       │
   │ • Payment history          │
   │ • Contract value           │
   └────────────┬───────────────┘
        ↓
   [Decision routing]
   ┌──────────────────────────────────────┐
   │ insurance = expired?  → BLOCK        │
   │ risk score ≥ 70?      → VP Procurement│
   │ contract > $200K?     → VP Procurement│
   │ contract > $50K?      → Regional Ops  │
   │ all clear?            → Standard route│
   └──────────────────────────────────────┘
        ↓
   [Approval request created in DB]
   [Routed to required approver]
        ↓
   [Approver: Approve / Reject / Escalate]
        ↓
   [Decision logged to Audit Trail]
   [Vendor status updated]
```

**Escalation rule:** If pending > 24 hours → auto-escalate to next approval level  
**SLA:** 5 business days for standard vendors

---

## Workflow 2: Community Performance Intervention

**Business trigger:** User asks about underperforming communities  
**Agents:** Executive Orchestrator → Community Performance → Construction Delay → Finance / Incentive → Marketing Campaign → Critic  
**Policy:** Incentive Approval Policy (Sales)

```
[User: "Why is South Florida underperforming?"]
        ↓
[Classify: sales_ops]
[Activate: Community Performance, Construction Delay, Finance, Marketing]
        ↓
[Community Performance Agent]
  → get_community_metrics(region="South Florida")
  → get_inventory_status(community="Coral Bay")
  → get_lead_conversion(region="South Florida")
  → Finding: 3 communities below target, 18 stale homes, conversion down
        ↓
[Construction Delay Agent]
  → get_construction_delays()
  → Finding: 14 closings at risk in Ocean Vista, 21-day delay
  → Auto-escalation triggered (> 10 closings)
        ↓
[Finance / Incentive Agent]
  → calculate_incentive_impact("Coral Bay", 0.75%)  → -0.75% margin  ✓
  → calculate_incentive_impact("Coral Bay", 1.25%)  → -1.25% margin  ✓ (needs VP Sales)
  → calculate_incentive_impact("Coral Bay", 2.00%)  → -2.00% margin  ✗ BLOCKED
        ↓
[Marketing Campaign Agent]
  → generate_marketing_campaign("Coral Bay", "Move stale inventory")
  → Campaign copy ready, pending human approval
        ↓
[Critic / Governance Agent]
  → Evidence: complete (5 tool calls)
  → Unsupported claims: none
  → Triggers: incentive (1.25%) + campaign = human approval required
  → Risk level: HIGH
        ↓
[LLM Synthesis → Executive Summary]
        ↓
[Finalize: create APR-XXX (1.25% incentive), APR-YYY (campaign)]
        ↓
[Approval Queue: VP Sales, Marketing Director review]
```

---

## Workflow 3: Associate Policy Lookup (RAG-Enhanced)

**Business trigger:** Associate asks a workflow or policy question  
**Agent:** Associate Productivity Agent  
**Retrieval:** ChromaDB semantic search + SQL fallback

```
[Associate: "How do I onboard a new subcontractor?"]
        ↓
[Classify: workflow]
[Activate: Associate Productivity Agent]
        ↓
[get_policy_workflow(business_process="onboard a new subcontractor")]
        ↓
   ┌─────────────────────────────────────────────┐
   │ RAG Path (if OpenAI key available):          │
   │  1. Embed query → text-embedding-3-small     │
   │  2. ChromaDB cosine search over policy index │
   │  3. Returns: Invoice Approval Policy (0.68) │
   │              Vendor Onboarding Policy (0.55) │
   └──────────────────┬──────────────────────────┘
                      ↓
   [SQL LIKE fallback for structured steps]
                      ↓
   [7-step workflow returned]
   [Required approvers identified]
   [Approval thresholds surfaced]
                      ↓
   [LLM writes personalized answer (if key available)]
                      ↓
   [Response delivered to associate]
   [Risk level: LOW — no approval required]
```

---

## Workflow 4: Invoice Approval Routing

**Business trigger:** Associate asks about invoice approval thresholds  
**Mapped corporate process:**

```
[Invoice submitted by vendor]
        ↓
[Project Manager verifies work completion]
        ↓
   ┌─────────────────────────────────────────┐
   │ Amount < $10,000    → PM approval        │
   │ $10,000 – $50,000   → Director Finance   │
   │ > $50,000           → VP Finance         │
   └─────────────────────────────────────────┘
        ↓
[Payment within 30 days of approval]
        ↓
[Escalation: delayed > 30 days or disputed → VP Finance notification]
```

---

## Workflow 5: Construction Delay Escalation

**Business trigger:** Construction delay logged in project management system  
**Agent:** Construction Delay Agent  
**Policy:** Construction Delay Escalation Policy (Operations)

```
[Superintendent logs delay with root cause]
        ↓
   ┌─────────────────────────────────────────────┐
   │ Delay < 7 days:    Superintendent resolves   │
   │ Delay 7–14 days:   Construction Manager      │
   │ Delay > 14 days:   Regional Ops Manager      │
   │ > 10 closings:     VP Operations (24h SLA)   │
   └─────────────────────────────────────────────┘
        ↓
[Customer notification for closing date impact]
        ↓
[Agent auto-creates escalation APR if threshold exceeded]
        ↓
[Audit event logged: escalation_triggered]
```
