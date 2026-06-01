-- HomeBuilder Workforce AI — PostgreSQL Schema
-- Use this when DATABASE_URL points to PostgreSQL (e.g., Render, AWS RDS)

CREATE TABLE IF NOT EXISTS communities (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    region TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    active_homes INTEGER DEFAULT 0,
    target_monthly_sales INTEGER DEFAULT 0,
    actual_monthly_sales INTEGER DEFAULT 0,
    avg_price REAL DEFAULT 0,
    avg_days_on_market REAL DEFAULT 0,
    gross_margin_pct REAL DEFAULT 0,
    stale_homes INTEGER DEFAULT 0,
    lead_volume INTEGER DEFAULT 0,
    lead_conversion_pct REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS homes (
    id SERIAL PRIMARY KEY,
    community_id INTEGER REFERENCES communities(id),
    lot_number TEXT,
    plan_name TEXT,
    price REAL,
    status TEXT,
    days_on_market INTEGER DEFAULT 0,
    completion_status TEXT,
    projected_close_date TEXT,
    gross_margin_pct REAL
);

CREATE TABLE IF NOT EXISTS leads (
    id SERIAL PRIMARY KEY,
    community_id INTEGER REFERENCES communities(id),
    source TEXT,
    created_at TEXT,
    status TEXT,
    converted INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS construction_delays (
    id SERIAL PRIMARY KEY,
    community_id INTEGER REFERENCES communities(id),
    lot_number TEXT,
    reason TEXT,
    severity TEXT,
    delayed_days INTEGER DEFAULT 0,
    responsible_party TEXT,
    status TEXT DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS marketing_campaigns (
    id SERIAL PRIMARY KEY,
    community_id INTEGER REFERENCES communities(id),
    channel TEXT,
    spend REAL DEFAULT 0,
    leads_generated INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    start_date TEXT,
    end_date TEXT
);

CREATE TABLE IF NOT EXISTS vendors (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT,
    region TEXT,
    insurance_status TEXT,
    risk_score INTEGER DEFAULT 0,
    payment_history_score INTEGER DEFAULT 0,
    active_contract_value REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS policies (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    business_function TEXT,
    steps_json TEXT,
    approval_threshold REAL DEFAULT 0,
    escalation_rule TEXT
);

CREATE TABLE IF NOT EXISTS agent_configs (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    business_function TEXT,
    persona TEXT,
    trigger_description TEXT,
    allowed_tools_json TEXT,
    approval_rule TEXT,
    escalation_rule TEXT,
    safety_rule TEXT,
    output_format TEXT,
    version TEXT DEFAULT '1.0',
    active INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS agent_runs (
    id SERIAL PRIMARY KEY,
    agent_name TEXT,
    user_prompt TEXT,
    status TEXT DEFAULT 'running',
    started_at TEXT,
    completed_at TEXT,
    final_response TEXT,
    risk_level TEXT,
    approval_required INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS tool_calls (
    id SERIAL PRIMARY KEY,
    agent_run_id INTEGER REFERENCES agent_runs(id),
    agent_name TEXT,
    tool_name TEXT NOT NULL,
    input_json TEXT,
    output_json TEXT,
    latency_ms INTEGER,
    success INTEGER DEFAULT 1,
    error_message TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS approval_requests (
    id TEXT PRIMARY KEY,
    agent_run_id INTEGER REFERENCES agent_runs(id),
    agent_name TEXT,
    recommended_action TEXT,
    risk_level TEXT,
    required_approver TEXT,
    status TEXT DEFAULT 'pending',
    created_at TEXT,
    decided_at TEXT,
    decision_reason TEXT,
    community TEXT,
    flags_json TEXT
);

CREATE TABLE IF NOT EXISTS audit_events (
    id TEXT PRIMARY KEY,
    timestamp TEXT,
    actor TEXT,
    agent_name TEXT,
    event_type TEXT,
    description TEXT,
    risk_level TEXT,
    approval_status TEXT,
    metadata_json TEXT
);

CREATE TABLE IF NOT EXISTS eval_cases (
    id TEXT PRIMARY KEY,
    name TEXT,
    prompt TEXT,
    expected_behavior TEXT,
    pass_fail TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS eval_runs (
    id SERIAL PRIMARY KEY,
    eval_id TEXT,
    eval_name TEXT,
    prompt TEXT,
    pass_fail TEXT,
    checks_passed INTEGER DEFAULT 0,
    checks_total INTEGER DEFAULT 0,
    run_at TEXT,
    details_json TEXT
);
