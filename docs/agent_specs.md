# Agent Specifications — HomeBuilder Workforce AI

Version 1.0 | All agents route through the Critic / Governance Agent before surfacing any recommendation.

---

## 1. Executive Orchestrator

**Persona:** Senior Operations Strategist  
**Trigger:** Any user request submitted to the Executive Command Center  
**LangGraph nodes:** `classify_request → generate_response → finalize`

**Responsibilities:**
- Classify the request type (sales_ops / incentive / vendor / workflow / general)
- Select which specialist agents to activate
- Synthesize all agent findings into a coherent executive summary (LLM)
- Create per-action approval requests for any recommended action requiring human sign-off
- Write the run record and audit event to the database

**Approval rule:** Creates approval requests when Critic flags medium or high risk  
**Safety rule:** Never produce a recommendation without evidence from at least one tool call  
**Output format:** Executive Summary (prose) + Recommended Actions (structured list)

---

## 2. Associate Productivity Agent

**Persona:** Corporate Workflow Advisor  
**Trigger:** Any question about how to do something, what policy applies, or who needs to approve  
**Business systems:** HRIS, Policy Management, RAG Knowledge Base  
**LangGraph node:** `associate_productivity`

**Responsibilities:**
- Semantic RAG search over ChromaDB policy index (OpenAI text-embedding-3-small)
- Falls back to SQL LIKE search if RAG unavailable
- Retrieves step-by-step workflow, required approvers, approval thresholds, escalation rules
- Uses LLM to give a personalized, conversational answer when API key is available
- Surfaces policy_steps for display in the agent activity feed

**Tools:** `get_policy_workflow` (RAG-enhanced)  
**Approval rule:** Creates approval request drafts only — does not auto-submit  
**Safety rule:** Never advise an action without citing a policy source  
**Output format:** Conversational guidance + structured policy steps

---

## 3. Vendor Approval Agent

**Persona:** Procurement Risk Analyst  
**Trigger:** Any request to review, onboard, or assess a vendor  
**Business systems:** ERP / Procurement, Vendor Master Data  
**LangGraph node:** `vendor_approval`

**Responsibilities:**
- Retrieve vendor profile: category, insurance status, risk score, payment history, contract value
- Compute composite risk assessment
- Auto-create approval request for high-risk vendors (risk > 70, expired insurance, contract > $50K)
- Route to VP Procurement for blocked vendors; Regional Ops Manager for standard

**Tools:** `get_vendor_profile`, `get_vendor_risk_score`, `create_approval_request`  
**Approval rule:** Human approval required for contracts > $50K, expired insurance, or risk score > 70  
**Safety rule:** Never approve or recommend approval for a vendor with expired insurance  
**Escalation rule:** Escalate to VP Procurement if risk score > 70 and contract > $50K  
**Output format:** Vendor Assessment JSON + narrative finding

---

## 4. Community Performance Agent

**Persona:** Homebuilding Operations Analyst  
**Trigger:** Questions about community sales, inventory, lead conversion, or regional performance  
**Business systems:** CRM, Sales Operations, Inventory Management  
**LangGraph node:** `community_performance`

**Responsibilities:**
- Query community sales metrics vs. targets — compute variance %
- Retrieve inventory data for most underperforming community (stale homes, price bands, margin)
- Retrieve lead conversion funnel data
- Identify root causes: pricing, conversion, construction delays, or marketing effectiveness

**Tools:** `get_community_metrics`, `get_inventory_status`, `get_lead_conversion`  
**Approval rule:** Escalates if recommendations include incentives or customer-facing campaigns  
**Safety rule:** Never attribute underperformance to a single cause without data support for that cause  
**Output format:** Performance Report with variance data and identified root causes

---

## 5. Finance / Incentive Agent

**Persona:** Financial Impact Modeler  
**Trigger:** Any request involving pricing, discounts, incentives, or margin analysis  
**Business systems:** ERP / Finance, Pricing Engine  
**LangGraph node:** `finance_incentive`

**Responsibilities:**
- Model incentive scenarios (0.75%, 1.25%, 2.00%) against real inventory data
- Calculate revenue impact and margin impact per scenario
- Block scenarios exceeding 1.5% margin limit (hard policy rule — no exceptions)
- Flag scenarios between 1.0% and 1.5% for CFO approval
- Flag scenarios between 0.5% and 1.0% for VP Sales approval

**Tools:** `calculate_incentive_impact`  
**Approval rule:** Any margin impact ≥ 1.0% requires CFO or VP Sales approval  
**Safety rule:** Automatically block and flag any scenario exceeding 1.5% margin impact  
**Output format:** Incentive Scenario Comparison JSON with recommendation

---

## 6. Construction Delay Agent

**Persona:** Operations Risk Monitor  
**Trigger:** Any question about construction delays, project status, or closing risks  
**Business systems:** Project Management, Operations  
**LangGraph node:** `construction_delay`

**Responsibilities:**
- Retrieve active construction delays across communities
- Categorize by severity: low / medium / high / critical
- Count affected closings per community
- Auto-trigger escalation if total affected closings > 10
- Identify responsible parties

**Tools:** `get_construction_delays`, `create_approval_request`  
**Approval rule:** Auto-escalates delays > 14 days or affecting > 10 closings  
**Safety rule:** Never suppress or downgrade a reported delay severity  
**Output format:** Delay Risk Report with affected closing count and escalation status

---

## 7. Marketing Campaign Agent

**Persona:** Digital Campaign Strategist  
**Trigger:** Request to create campaign content or a marketing brief for a community  
**Business systems:** CRM, Marketing Platform  
**LangGraph node:** `marketing_campaign`

**Responsibilities:**
- Identify most underperforming community from community metrics
- Determine objective: stale inventory vs. lead conversion issue
- Generate campaign brief, email copy, ad copy, and SMS copy
- All content flagged as requiring human approval before launch

**Tools:** `generate_marketing_campaign`, `get_community_metrics`  
**Approval rule:** ALL customer-facing campaign content requires Regional Marketing Director approval  
**Safety rule:** Never mark campaign as executable without documented human approval  
**Output format:** Campaign Brief JSON + email/ad/SMS copy strings

---

## 8. Critic / Governance Agent

**Persona:** AI Safety & Compliance Auditor  
**Trigger:** Always runs as the final specialist step before LLM synthesis  
**LangGraph node:** `critic_validate`

**Responsibilities:**
- Count evidence (tool calls made before recommendation)
- Detect agents that produced findings without calling tools (unsupported claims)
- Evaluate 5 approval trigger rules:
  1. Incentive margin impact ≥ 1.0%
  2. Vendor insurance not current
  3. Vendor risk level = high
  4. Construction delays affecting > 10 closings
  5. Customer-facing campaign in recommended actions
- Assign risk level: low / medium / high
- Set `approval_required` flag
- Log validation result to audit trail

**Tools:** None (validates state, does not call external tools)  
**Approval rule:** Flags any run with medium or high risk for human review  
**Safety rule:** Block any recommendation where `unsupported_claims` is detected  
**Output format:** Validation Result JSON + narrative finding
