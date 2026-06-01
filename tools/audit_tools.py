import json
from datetime import datetime
from database.db import execute, query


def log_audit_event(
    event_type: str,
    description: str,
    actor: str = "system",
    agent_name: str = "system",
    risk_level: str = "low",
    approval_status: str = "n/a",
    metadata: dict = None,
) -> str:
    rows = query("SELECT COUNT(*) AS cnt FROM audit_events")
    seq = rows[0]["cnt"] + 1
    event_id = f"AUD-{seq:03d}"
    now = datetime.now().isoformat()

    execute("""
        INSERT INTO audit_events
          (id, timestamp, actor, agent_name, event_type, description,
           risk_level, approval_status, metadata_json)
        VALUES (:id,:ts,:actor,:agent,:etype,:desc,:risk,:appr,:meta)
    """, {
        "id": event_id, "ts": now, "actor": actor, "agent": agent_name,
        "etype": event_type, "desc": description,
        "risk": risk_level, "appr": approval_status,
        "meta": json.dumps(metadata or {}),
    })
    return event_id


def get_audit_events(agent: str = None, event_type: str = None,
                     risk_level: str = None, approval_status: str = None,
                     limit: int = 100) -> list[dict]:
    clauses = ["1=1"]
    params = {}
    if agent and agent != "n/a":
        clauses.append("agent_name = :agent")
        params["agent"] = agent
    if event_type:
        clauses.append("event_type = :etype")
        params["etype"] = event_type
    if risk_level:
        clauses.append("risk_level = :risk")
        params["risk"] = risk_level
    if approval_status:
        clauses.append("approval_status = :appr")
        params["appr"] = approval_status
    where = " AND ".join(clauses)

    return query(f"""
        SELECT id, timestamp, actor, agent_name, event_type, description,
               risk_level, approval_status, metadata_json
        FROM audit_events
        WHERE {where}
        ORDER BY timestamp DESC
        LIMIT :lim
    """, {**params, "lim": limit})


def create_executive_report(agent_run_id: int, findings: list, recommendations: list,
                             risk_level: str = "medium", approval_required: bool = True) -> dict:
    summary = f"Analysis complete. {len(findings)} findings. {len(recommendations)} recommended actions. Risk: {risk_level}."
    log_audit_event(
        "agent_run_completed",
        f"Executive report generated — {len(recommendations)} actions, risk: {risk_level}",
        actor="Executive Orchestrator",
        agent_name="Executive Orchestrator",
        risk_level=risk_level,
        approval_status="pending" if approval_required else "n/a",
    )
    return {
        "agent_run_id": agent_run_id,
        "executive_summary": summary,
        "key_findings": findings,
        "recommended_actions": recommendations,
        "risk_level": risk_level,
        "approval_required": approval_required,
    }
