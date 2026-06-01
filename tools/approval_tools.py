import json
import time
from datetime import datetime
from database.db import execute, query
from tools.base import log_tool_call


def create_approval_request(
    recommended_action: str,
    risk_level: str,
    required_approver: str,
    agent_run_id: int = None,
    community: str = None,
    flags: list = None,
    agent_name: str = "system",
    run_id: int = None,
) -> dict:
    t0 = time.time()
    try:
        # Generate sequential ID
        existing = query("SELECT COUNT(*) AS cnt FROM approval_requests")
        seq = existing[0]["cnt"] + 1
        req_id = f"APR-{seq:03d}"

        now = datetime.now().isoformat()
        execute("""
            INSERT OR IGNORE INTO approval_requests
              (id, agent_run_id, agent_name, recommended_action, risk_level,
               required_approver, status, created_at, community, flags_json)
            VALUES (:id,:run_id,:agent,:action,:risk,:approver,'pending',:now,:community,:flags)
        """, {
            "id": req_id, "run_id": agent_run_id, "agent": agent_name,
            "action": recommended_action, "risk": risk_level,
            "approver": required_approver, "now": now,
            "community": community or "",
            "flags": json.dumps(flags or []),
        })

        out = {
            "approval_request_id": req_id,
            "status": "pending",
            "routed_to": required_approver,
            "created_at": now,
        }
        ms = int((time.time() - t0) * 1000)
        log_tool_call("create_approval_request",
                      {"recommended_action": recommended_action, "risk_level": risk_level},
                      out, ms, True, agent_name=agent_name, run_id=run_id)
        return out
    except Exception as e:
        ms = int((time.time() - t0) * 1000)
        log_tool_call("create_approval_request",
                      {"recommended_action": recommended_action},
                      None, ms, False, str(e), agent_name, run_id)
        raise


def update_approval_decision(request_id: str, decision: str, reason: str = None) -> dict:
    now = datetime.now().isoformat()
    execute("""
        UPDATE approval_requests
        SET status = :status, decided_at = :now, decision_reason = :reason
        WHERE id = :id
    """, {"status": decision, "now": now, "reason": reason or "", "id": request_id})
    return {"id": request_id, "status": decision, "decided_at": now}


def get_approval_requests(status: str = None, risk_level: str = None, agent: str = None) -> list[dict]:
    clauses = ["1=1"]
    params = {}
    if status:
        clauses.append("status = :status")
        params["status"] = status
    if risk_level:
        clauses.append("risk_level = :risk_level")
        params["risk_level"] = risk_level
    if agent:
        clauses.append("agent_name = :agent")
        params["agent"] = agent
    where = " AND ".join(clauses)

    rows = query(f"""
        SELECT id, agent_name, recommended_action, risk_level, required_approver,
               status, created_at, decided_at, decision_reason, community, flags_json
        FROM approval_requests WHERE {where}
        ORDER BY created_at DESC
    """, params)

    result = []
    for r in rows:
        result.append({**r, "flags": json.loads(r["flags_json"] or "[]")})
    return result
