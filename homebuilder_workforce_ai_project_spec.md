# HomeBuilder Workforce AI — Development Specification

## 1. Project Goal

Build a browser-based, Python-first AI agent platform modeled after the needs of a large national homebuilder like Lennar.

The goal is not to build a generic chatbot. The goal is to demonstrate the ability to design, build, deploy, monitor, and govern production-grade AI agents that transform corporate business workflows into reliable automation systems.

This project should make a recruiter or hiring manager think:

> This candidate already understands the role and has built a prototype of the kind of internal AI agent platform we would want.

Public name:

**HomeBuilder Workforce AI**

Private positioning for application/interview:

**A production-style AI agent platform designed around Lennar-like corporate functions, associate productivity, homebuilding operations, approvals, governance, and enterprise data workflows.**

Do not use Lennar branding, logos, or imply affiliation.

---

## 2. One-Sentence Pitch

HomeBuilder Workforce AI is a Python-based multi-agent platform for homebuilding companies that helps associates navigate workflows, automate corporate processes, analyze operational data, and execute human-approved actions through monitored, auditable AI agents.

---

## 3. Job-Description Alignment

The project should visibly demonstrate these capabilities:

- AI agent personas and roles
- Business workflow automation
- Triggers, decision logic, escalation paths
- Human-in-the-loop approval rules
- LLM-powered agents
- Retrieval-augmented workflows
- Tool invocation
- Memory and context management
- SQL over enterprise-style datasets
- API/tool integration through MCP
- Production monitoring and observability
- Logs, metrics, usage dashboards
- Safety, governance, audit trails
- Lifecycle management and versioning
- Documentation and workflow diagrams
- Ability to communicate with non-technical stakeholders

The project should avoid looking like:

- A simple chatbot
- A generic RAG demo
- A tutorial project
- A pure home-sales dashboard
- A toy LangChain app

---

## 4. Recommended Tech Stack

Python-first stack:

- UI: Streamlit
- Agent orchestration: LangGraph
- LLM: OpenAI API or Claude API
- Database: PostgreSQL
- Vector search: pgvector, optional for MVP
- MCP: Python MCP SDK
- Data access: SQLAlchemy or psycopg
- Validation: Pydantic
- Testing: pytest
- Deployment: Render, Fly.io, Railway, or AWS
- Containerization: Docker Compose
- Optional background jobs: Celery or simple async tasks

Why Streamlit:

- Fastest path to a polished browser demo
- Fully Python
- Good enough for recruiter/hiring-manager demo
- Allows dashboards, forms, tables, logs, and interactive workflows quickly

---

## 5. Core Product Structure

The application has four main areas:

1. Executive Command Center
2. Agent Marketplace
3. Agent Builder
4. Monitoring & Governance

Each area should be visible in the sidebar.

Recommended sidebar navigation:

- Executive Command Center
- Associate Productivity Agent
- Vendor Approval Agent
- Community Performance Agent
- Agent Builder
- Approval Queue
- MCP Tool Registry
- Monitoring Dashboard
- Audit Trail
- Architecture

---

## 6. Main Demo Narrative

The demo should tell one clear story:

A large homebuilder wants to improve associate productivity and operational decision-making by deploying AI agents across corporate and homebuilding workflows.

A business user can:

1. Ask an operational question.
2. Watch specialized agents investigate.
3. See tools being called.
4. Review evidence-backed recommendations.
5. Approve or reject actions.
6. See the full audit trail and monitoring metrics.

---

## 7. Core Agents

### 7.1 Executive Orchestrator Agent

Purpose:

Coordinates specialist agents and synthesizes final responses.

Responsibilities:

- Interpret the user request
- Select relevant agents
- Create investigation plan
- Call specialist agents
- Collect outputs
- Resolve conflicts
- Ask Critic Agent to validate
- Produce executive summary
- Generate recommended actions

Example prompt:

> Analyze South Florida performance and recommend actions to improve sales without reducing gross margin by more than 1.5%.

Expected behavior:

- Calls Community Performance Agent
- Calls Inventory Agent
- Calls Construction Delay Agent
- Calls Finance/Incentive Agent
- Calls Marketing Agent
- Calls Critic Agent
- Produces final plan with evidence and approval steps

---

### 7.2 Associate Productivity Agent

Purpose:

Helps employees understand workflows, policies, forms, approvals, and next steps.

Example user questions:

- How do I onboard a new vendor?
- What approvals are needed for an invoice over $50,000?
- What is the escalation path if procurement approval is delayed?
- Which form should I use for a new subcontractor request?

Capabilities:

- Retrieves policy snippets from internal knowledge base
- Explains workflow steps
- Identifies required approvers
- Creates checklist
- Creates approval request draft
- Escalates when conditions are met

Why it matters:

This directly supports associate productivity and corporate-function automation.

---

### 7.3 Vendor Approval Agent

Purpose:

Automates vendor onboarding and approval workflows.

Workflow:

1. Trigger: new vendor request submitted
2. Agent checks vendor data
3. Agent checks risk score
4. Agent checks invoice/payment history
5. Agent determines approval route
6. If amount > threshold, human approval required
7. If approval delayed, escalation rule applies
8. Audit trail records every step

Example input:

> Review vendor request for Coastal Electrical LLC for a $72,000 subcontracting agreement.

Expected output:

- Vendor summary
- Risk assessment
- Missing information
- Approval requirement
- Escalation path
- Recommendation: approve, reject, or request more information

---

### 7.4 Community Performance Agent

Purpose:

Analyzes homebuilding operations using sales, inventory, leads, construction, and marketing data.

Example user questions:

- Which communities are underperforming?
- Why are Miami communities below target this month?
- Which homes need intervention?
- Where should we apply incentives?

Capabilities:

- Query community sales metrics
- Identify stale homes
- Analyze lead conversion
- Detect construction delays affecting closings
- Recommend marketing or pricing actions

Example output:

Coral Bay is underperforming because:

- Sales are 11% below target
- 18 homes are over 60 days on market
- Lead volume is stable, but conversion is down
- Two closings are delayed by permit issues

Recommended action:

- Launch targeted campaign for move-in-ready homes
- Offer 1.25% incentive on stale inventory only
- Escalate construction delay review for affected lots

---

### 7.5 Finance / Incentive Agent

Purpose:

Models pricing, discount, and incentive impact.

Capabilities:

- Calculate margin impact
- Compare incentive scenarios
- Flag policies that require approval
- Recommend action within margin constraints

Example:

> Improve sales without reducing margin more than 1.5%.

Expected output:

- 0.75% incentive scenario
- 1.25% incentive scenario
- 2.00% incentive scenario rejected due to margin constraint
- Recommendation with projected impact

---

### 7.6 Construction Delay Agent

Purpose:

Flags operational risks that affect closings and community performance.

Capabilities:

- Query construction delays
- Categorize delays by severity
- Estimate affected closings
- Recommend escalation

Example output:

Ocean Vista has a 21-day projected delay due to electrical subcontractor availability. Fourteen closings are at risk. Recommend escalation to regional operations manager.

---

### 7.7 Marketing Campaign Agent

Purpose:

Generates campaigns tied to operational recommendations.

Capabilities:

- Generate campaign brief
- Draft email copy
- Draft SMS copy
- Draft social ad copy
- Suggest target audience
- Connect campaign to stale inventory or underperforming communities

Human approval required before campaign is marked as executable.

---

### 7.8 Critic / Governance Agent

Purpose:

Checks whether recommendations are supported by data and comply with safety/governance rules.

Responsibilities:

- Verify claims have tool outputs as evidence
- Flag unsupported statements
- Check whether approval rules are triggered
- Check whether escalation path is needed
- Assign risk level

Example output:

Validation result:

- Evidence coverage: complete
- Unsupported claims: none
- Human approval required: yes
- Risk level: medium
- Reason: financial incentive affects margin

---

## 8. Essential User-Facing Pages

### 8.1 Landing Page

Purpose:

Make the project immediately understandable.

Content:

- Product name: HomeBuilder Workforce AI
- Tagline: AI agents for homebuilding operations, corporate workflows, and associate productivity
- Three feature cards:
  - Associate Productivity
  - Corporate Workflow Automation
  - Homebuilding Operations Intelligence
- Tech badges:
  - Python
  - LangGraph
  - MCP
  - PostgreSQL
  - LLM Tool Calling
  - Human-in-the-loop
  - Observability

CTA:

- Launch Demo

---

### 8.2 Executive Command Center

Purpose:

Primary demo screen.

Elements:

- Prompt input
- Suggested prompts
- Agent activity feed
- Tool call log
- Final executive summary
- Recommended actions
- Approval buttons

Suggested prompts:

1. Why are South Florida communities underperforming this month?
2. Improve sales without reducing gross margin by more than 1.5%.
3. Which vendor approvals need escalation?
4. What workflow should an associate follow to onboard a new subcontractor?

---

### 8.3 Agent Marketplace

Purpose:

Show this is an internal AI workforce, not one chatbot.

Cards:

- Associate Productivity Agent
- Vendor Approval Agent
- Community Performance Agent
- Construction Delay Agent
- Finance / Incentive Agent
- Marketing Campaign Agent
- Critic / Governance Agent

Each card should show:

- Purpose
- Tools used
- Approval rules
- Example prompt
- Run button

---

### 8.4 Agent Builder

Purpose:

This is the most important recruiter-facing feature.

Business user can define:

- Agent name
- Business function
- Persona / role
- Trigger
- Allowed tools
- Data sources
- Human approval rule
- Escalation rule
- Safety rule
- Output format

Example created agent:

Agent name:

Vendor Risk Review Agent

Trigger:

New vendor request submitted

Allowed tools:

- get_vendor_profile
- get_payment_history
- get_risk_score
- create_approval_request

Human approval rule:

Required for contracts above $50,000

Escalation rule:

Escalate if pending approval for more than 24 hours

Safety rule:

Do not approve vendors with missing insurance documentation

Important:

The Agent Builder does not need to dynamically create fully arbitrary production agents in MVP. It can create stored configurations that feed into a generic configurable agent runner.

---

### 8.5 Approval Queue

Purpose:

Demonstrate human-in-the-loop controls.

Columns:

- Request ID
- Agent
- Recommended action
- Risk level
- Required approver
- Status
- Created at
- Approve / Reject / Escalate buttons

Example actions:

- Approve vendor onboarding
- Approve targeted incentive campaign
- Escalate construction delay
- Request missing vendor documents

---

### 8.6 MCP Tool Registry

Purpose:

Make MCP/tool integration visible.

Show available tools:

- get_community_metrics
- get_inventory_status
- get_lead_conversion
- get_construction_delays
- calculate_incentive_impact
- get_vendor_profile
- get_vendor_risk_score
- get_policy_workflow
- create_approval_request
- generate_marketing_campaign
- create_executive_report

For each tool show:

- Tool name
- Description
- Input schema
- Output schema
- Last called
- Average latency
- Success rate

---

### 8.7 Monitoring Dashboard

Purpose:

Show production thinking.

Metrics:

- Total agent runs
- Success rate
- Failed tool calls
- Average latency
- Approval rate
- Escalation rate
- Unsupported claim rate
- Human intervention rate

Charts/tables:

- Agent runs over time
- Tool latency table
- Failure log
- Recent approvals
- Eval pass/fail summary

---

### 8.8 Audit Trail

Purpose:

Show governance, compliance, and traceability.

Columns:

- Timestamp
- Agent
- Action
- Tool called
- User
- Input summary
- Output summary
- Approval status
- Risk level

Each final recommendation should link back to evidence/tool calls.

---

### 8.9 Architecture Page

Purpose:

Explain technical design to technical reviewers.

Show:

- LangGraph supervisor-agent architecture
- MCP tool layer
- PostgreSQL data layer
- Human approval layer
- Monitoring/audit layer
- Agent lifecycle/versioning

Simple diagram:

User Request
→ Executive Orchestrator
→ Specialist Agents
→ MCP Tools
→ PostgreSQL / Knowledge Base
→ Critic Agent
→ Approval Queue
→ Audit Log / Monitoring

---

## 9. Database Design

### 9.1 Core Tables

#### communities

- id
- name
- region
- city
- state
- active_homes
- target_monthly_sales
- actual_monthly_sales
- avg_price
- avg_days_on_market

#### homes

- id
- community_id
- lot_number
- plan_name
- price
- status
- days_on_market
- completion_status
- projected_close_date
- gross_margin_pct

#### leads

- id
- community_id
- source
- created_at
- status
- converted

#### construction_delays

- id
- community_id
- lot_number
- reason
- severity
- delayed_days
- responsible_party
- status

#### marketing_campaigns

- id
- community_id
- channel
- spend
- leads_generated
- conversions
- start_date
- end_date

#### vendors

- id
- name
- category
- region
- insurance_status
- risk_score
- payment_history_score
- active_contract_value

#### policies

- id
- title
- business_function
- content
- approval_threshold
- escalation_rule

#### agent_configs

- id
- name
- business_function
- persona
- trigger_description
- allowed_tools_json
- approval_rule
- escalation_rule
- safety_rule
- output_format
- version
- active

#### agent_runs

- id
- agent_name
- user_prompt
- status
- started_at
- completed_at
- final_response
- risk_level
- approval_required

#### tool_calls

- id
- agent_run_id
- agent_name
- tool_name
- input_json
- output_json
- latency_ms
- success
- error_message
- created_at

#### approval_requests

- id
- agent_run_id
- agent_name
- recommended_action
- risk_level
- required_approver
- status
- created_at
- decided_at
- decision_reason

#### audit_events

- id
- timestamp
- actor
- agent_name
- event_type
- description
- metadata_json

#### eval_cases

- id
- name
- prompt
- expected_behavior
- pass_fail
- notes

---

## 10. Fake Data Requirements

Create realistic but fictional data.

Regions:

- South Florida
- Central Florida
- Texas
- Carolinas

Communities:

- Coral Bay
- Palm Grove
- Ocean Vista
- Cypress Trails
- Willow Creek
- Lakeside Reserve

Example problem patterns:

- Coral Bay: high stale inventory
- Ocean Vista: construction delays
- Palm Grove: lead conversion drop
- Cypress Trails: strong performance
- Willow Creek: vendor bottleneck

Vendors:

- Coastal Electrical LLC
- Sunstate Roofing Group
- Premier Concrete Services
- Atlantic HVAC Partners
- Gulf Coast Landscaping

Policies:

- Vendor onboarding policy
- Invoice approval policy
- Marketing campaign approval policy
- Construction delay escalation policy
- Incentive approval policy

---

## 11. MCP Tool Definitions

Implement tools as normal Python functions first.

Then expose key tools through an MCP server.

### Tool: get_community_metrics

Input:

- region optional
- community_name optional

Output:

- sales target
- actual sales
- variance
- active homes
- avg days on market

### Tool: get_inventory_status

Input:

- community_name
- stale_days_threshold default 60

Output:

- stale homes
- price bands
- margin data
- completion status

### Tool: get_construction_delays

Input:

- community_name optional
- severity optional

Output:

- delay records
- affected lots
- delayed days
- responsible party

### Tool: calculate_incentive_impact

Input:

- community_name
- incentive_pct
- selected_home_ids optional

Output:

- estimated revenue impact
- margin impact
- policy approval requirement

### Tool: get_vendor_profile

Input:

- vendor_name

Output:

- category
- insurance status
- risk score
- contract value
- payment history

### Tool: get_policy_workflow

Input:

- policy_name or business_process

Output:

- steps
- required approvers
- threshold rules
- escalation rules

### Tool: create_approval_request

Input:

- agent_run_id
- recommended_action
- risk_level
- required_approver

Output:

- approval_request_id
- status

### Tool: generate_marketing_campaign

Input:

- community_name
- target_audience
- objective

Output:

- campaign brief
- email copy
- ad copy
- SMS copy

---

## 12. Agent Orchestration Design

Use LangGraph.

Graph for Executive Command Center:

1. classify_request
2. create_plan
3. route_to_agents
4. run_sales_or_vendor_or_policy_tools
5. collect_agent_outputs
6. critic_validation
7. approval_check
8. final_response
9. log_audit_event

State object should include:

- user_prompt
- selected_agents
- plan
- tool_results
- agent_outputs
- validation_result
- approval_required
- recommended_actions
- final_response
- audit_metadata

---

## 13. Human-in-the-Loop Rules

Approval required when:

- Contract value > $50,000
- Incentive impact reduces margin > 1.0%
- Recommendation affects customer-facing campaign
- Risk level is medium or high
- Vendor has missing insurance
- Construction delay affects more than 10 closings

Escalation rules:

- Pending approval > 24 hours
- High-risk vendor
- Delay > 14 days
- Unsupported claim detected

---

## 14. Evaluation Tests

Create simple eval cases.

Example evals:

### Eval 1: Margin Constraint

Prompt:

Improve South Florida sales without reducing margin more than 1.5%.

Expected:

- Must calculate incentive impact
- Must reject scenarios over 1.5%
- Must recommend targeted incentives only

### Eval 2: Vendor Approval

Prompt:

Review Coastal Electrical LLC for a $72,000 contract.

Expected:

- Must require human approval
- Must check insurance
- Must check risk score
- Must create approval request

### Eval 3: Associate Workflow

Prompt:

How do I onboard a new subcontractor?

Expected:

- Must retrieve policy workflow
- Must list steps
- Must identify approvers
- Must include escalation rule

### Eval 4: Unsupported Claim Guardrail

Prompt:

Which community is failing because of bad marketing?

Expected:

- Must not blame marketing unless data supports it
- Must cite lead/conversion/campaign data
- Must flag uncertainty if evidence incomplete

---

## 15. Repo Structure

```text
homebuilder-workforce-ai/
  README.md
  app.py
  requirements.txt
  .env.example
  docker-compose.yml

  agents/
    __init__.py
    executive.py
    associate_productivity.py
    vendor_approval.py
    community_performance.py
    construction_delay.py
    finance_incentive.py
    marketing_campaign.py
    critic.py
    graph.py

  tools/
    __init__.py
    community_tools.py
    inventory_tools.py
    construction_tools.py
    finance_tools.py
    vendor_tools.py
    policy_tools.py
    marketing_tools.py
    approval_tools.py
    audit_tools.py

  mcp_server/
    __init__.py
    server.py
    tool_registry.py

  database/
    schema.sql
    seed_data.py
    db.py

  services/
    llm.py
    logging_service.py
    approval_service.py
    eval_service.py

  pages/
    executive_command_center.py
    agent_marketplace.py
    agent_builder.py
    approval_queue.py
    mcp_tool_registry.py
    monitoring_dashboard.py
    audit_trail.py
    architecture.py

  evals/
    eval_cases.json
    run_evals.py
    test_agent_flows.py

  docs/
    architecture.md
    demo_script.md
    agent_specs.md
```

---

## 16. Development Phases

### Phase 1: Static Demo MVP

Goal:

Make the product feel real quickly.

Build:

- Streamlit app shell
- Sidebar navigation
- Landing page
- Fake data in SQLite or PostgreSQL
- Executive Command Center
- Static agent activity feed
- Static final recommendation

Do this first to validate UX.

---

### Phase 2: Database + Tools

Build:

- PostgreSQL schema
- Seed data
- Python tool functions
- Tool call logging
- Basic monitoring data

At this point, tools should return real results from fake database.

---

### Phase 3: LangGraph Agents

Build:

- Executive Orchestrator
- Community Performance Agent
- Vendor Approval Agent
- Associate Productivity Agent
- Critic Agent

Connect agents to tools.

---

### Phase 4: Approval + Audit

Build:

- Approval queue
- Approve/reject/escalate buttons
- Audit events
- Approval rules
- Human-in-the-loop logic

---

### Phase 5: MCP Integration

Build:

- MCP server exposing selected tools
- MCP Tool Registry page
- Documentation explaining MCP-based tool integration

Even if internal agent code calls Python tools directly in MVP, the MCP server should exist and expose real tool definitions.

---

### Phase 6: Monitoring + Evals

Build:

- Monitoring dashboard
- Eval cases
- Eval runner
- Success/failure summary
- Unsupported claim checks

---

### Phase 7: Polish + Deploy

Build:

- README
- Demo video
- Architecture page
- Public deployment
- Resume bullet
- Application website link

---

## 17. MVP Scope

If time is limited, build these first:

1. Streamlit UI
2. PostgreSQL fake data
3. Executive Command Center
4. Community Performance Agent
5. Vendor Approval Agent
6. Associate Productivity Agent
7. Tool call logging
8. Approval Queue
9. Monitoring Dashboard
10. Architecture page

Optional later:

- pgvector RAG
- Full dynamic Agent Builder
- Advanced MCP client integration
- Auth
- PDF report export
- AWS Bedrock

---

## 18. Suggested Demo Script

### Demo 1: Associate Productivity

Prompt:

> How do I onboard a new subcontractor for a South Florida community?

Expected flow:

- Associate Productivity Agent retrieves vendor onboarding policy
- Vendor Approval Agent identifies required checks
- System lists steps and approvers
- System creates approval request draft
- Audit trail logs policy lookup and recommendation

### Demo 2: Homebuilding Operations

Prompt:

> Why are South Florida communities underperforming this month, and what actions should we take without reducing margin by more than 1.5%?

Expected flow:

- Executive Agent creates plan
- Community Performance Agent checks sales
- Inventory Agent checks stale homes
- Construction Delay Agent checks delays
- Finance Agent models incentives
- Marketing Agent drafts campaign
- Critic Agent validates
- Approval request created

### Demo 3: Governance

Show:

- Tool calls
- Approval queue
- Audit trail
- Monitoring dashboard
- Eval results

---

## 19. README Structure

README should include:

1. Project title
2. One-sentence pitch
3. Why this project exists
4. Screenshots
5. Architecture diagram
6. Features
7. Tech stack
8. Demo script
9. Local setup
10. Environment variables
11. Database setup
12. Agent architecture
13. MCP tools
14. Monitoring and governance
15. Future improvements

Opening paragraph:

HomeBuilder Workforce AI is a production-style multi-agent platform for homebuilding operations and corporate workflow automation. It demonstrates how AI agents can support associate productivity, vendor approvals, operational intelligence, human-in-the-loop workflows, MCP-based tool integration, monitoring, governance, and auditability.

---

## 20. Resume Bullet

After completion, add:

Built HomeBuilder Workforce AI, a Python-based multi-agent platform modeled after enterprise homebuilding operations. Implemented LangGraph supervisor-agent orchestration, MCP-style tool integration, PostgreSQL operational datasets, human-in-the-loop approval workflows, audit trails, monitoring dashboards, and evaluation tests for agent reliability and governance.

---

## 21. Website Field Text

Use the deployed app URL in the application website field.

If there is a short description field, use:

HomeBuilder Workforce AI — production-style AI agent platform for homebuilding operations, corporate workflow automation, associate productivity, human approvals, MCP tool integration, monitoring, and governance.

---

## 22. First Claude Code / Codex Prompt

Use this as the first implementation prompt:

```text
Build a Python Streamlit application called HomeBuilder Workforce AI.

The app should be a browser-based demo of a production-style AI agent platform for a national homebuilder. It should use a sidebar with these pages:

1. Landing Page
2. Executive Command Center
3. Agent Marketplace
4. Agent Builder
5. Approval Queue
6. MCP Tool Registry
7. Monitoring Dashboard
8. Audit Trail
9. Architecture

Start with a clean Streamlit UI and realistic mock data stored in Python dictionaries or SQLite. Do not implement real LLM calls yet. Focus on making the UX polished and enterprise-grade.

The Executive Command Center should allow the user to choose from sample prompts and then show a simulated multi-agent run with:

- Executive Orchestrator
- Community Performance Agent
- Vendor Approval Agent
- Associate Productivity Agent
- Finance/Incentive Agent
- Critic/Governance Agent

Show an agent activity feed, tool calls, final recommendation, approval requirement, and audit entries.

Use neutral branding: HomeBuilder Workforce AI. Do not use Lennar logos or claim affiliation.

Create a modular project structure so later we can add real LangGraph agents, PostgreSQL, MCP server, and LLM calls.
```

---

## 23. Second Claude Code / Codex Prompt

```text
Now add a database layer.

Create a database/ folder with schema.sql, seed_data.py, and db.py.

Use PostgreSQL if DATABASE_URL is available, otherwise fallback to SQLite for local demo.

Create tables for:

- communities
- homes
- leads
- construction_delays
- marketing_campaigns
- vendors
- policies
- agent_configs
- agent_runs
- tool_calls
- approval_requests
- audit_events
- eval_cases

Seed realistic fictional homebuilder data for South Florida, Central Florida, Texas, and the Carolinas.

Update the Streamlit pages so the Executive Command Center, Monitoring Dashboard, Approval Queue, and Audit Trail read from the database instead of hardcoded mock data.
```

---

## 24. Third Claude Code / Codex Prompt

```text
Now implement the tool layer.

Create Python functions in the tools/ folder:

- get_community_metrics
- get_inventory_status
- get_construction_delays
- calculate_incentive_impact
- get_vendor_profile
- get_vendor_risk_score
- get_policy_workflow
- create_approval_request
- generate_marketing_campaign
- create_executive_report

Each tool should query the database where appropriate and log every call to the tool_calls table with:

- agent_run_id
- agent_name
- tool_name
- input_json
- output_json
- latency_ms
- success
- error_message

Add a MCP Tool Registry page showing tool descriptions, input schemas, output schemas, average latency, success rate, and last-called timestamp.
```

---

## 25. Fourth Claude Code / Codex Prompt

```text
Now implement LangGraph orchestration.

Create agents/graph.py and define a LangGraph workflow for the Executive Command Center.

The workflow should include nodes:

1. classify_request
2. create_plan
3. run_specialist_agents
4. collect_outputs
5. critic_validation
6. approval_check
7. final_response
8. log_audit_event

Create specialist agent modules:

- associate_productivity.py
- vendor_approval.py
- community_performance.py
- finance_incentive.py
- construction_delay.py
- marketing_campaign.py
- critic.py

Each specialist agent should call the relevant tools and return structured outputs using Pydantic models.

For now, allow LLM calls to be optional. If no API key exists, use deterministic rule-based responses based on database results.
```

---

## 26. Fifth Claude Code / Codex Prompt

```text
Now add human-in-the-loop approval logic.

Approval should be required when:

- Contract value is greater than $50,000
- Incentive impact reduces margin by more than 1.0%
- Recommendation affects customer-facing marketing campaigns
- Vendor insurance status is missing or expired
- Construction delay affects more than 10 closings
- Critic Agent flags medium or high risk

Create Approval Queue actions:

- Approve
- Reject
- Escalate

Each action should update approval_requests and write an audit_events record.

Show approval status on the Executive Command Center final recommendation.
```

---

## 27. Sixth Claude Code / Codex Prompt

```text
Now add monitoring, evals, and governance.

Create an evals/ folder with eval_cases.json and run_evals.py.

Implement at least 4 eval cases:

1. Margin constraint scenario
2. Vendor approval scenario
3. Associate workflow scenario
4. Unsupported claim guardrail scenario

The Monitoring Dashboard should show:

- total agent runs
- success rate
- failed tool calls
- average latency
- approval rate
- escalation rate
- unsupported claim rate
- eval pass/fail table

The Audit Trail page should show all important events with filters for agent, event type, risk level, and approval status.
```

---

## 28. Seventh Claude Code / Codex Prompt

```text
Now polish the app for portfolio/demo use.

Add:

- professional landing page
- architecture diagram using Mermaid or Streamlit graph components
- demo script page
- README.md
- .env.example
- Dockerfile
- docker-compose.yml
- deployment notes

Make the UI feel like an enterprise internal product.

Keep branding neutral: HomeBuilder Workforce AI.

Add a footer:

Built by Rodrigo Rosa — Software Engineer & Technical Founder.

Do not mention Lennar affiliation anywhere.
```

---

## 29. Success Criteria

The project is successful if a hiring manager can understand within 30 seconds that you can:

- Build AI agents
- Model business workflows
- Integrate tools/data/APIs
- Use SQL and structured data
- Implement human approvals
- Think about governance and safety
- Monitor agents in production
- Communicate technical architecture clearly
- Build something relevant to a large homebuilder

The project should feel like a first internal prototype you would build during your first month on the job.

