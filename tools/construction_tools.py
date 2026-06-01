import time
from database.db import query
from tools.base import log_tool_call


def get_construction_delays(community_name: str = None, severity: str = None,
                             agent_name: str = "system", run_id: int = None) -> dict:
    t0 = time.time()
    params = {}
    clauses = ["1=1"]
    if community_name:
        clauses.append("c.name = :name")
        params["name"] = community_name
    if severity:
        clauses.append("d.severity = :severity")
        params["severity"] = severity
    where = " AND ".join(clauses)

    try:
        rows = query(f"""
            SELECT d.id, c.name AS community, c.region, d.lot_number,
                   d.reason, d.severity, d.delayed_days, d.responsible_party, d.status
            FROM construction_delays d
            JOIN communities c ON d.community_id = c.id
            WHERE d.status = 'active' AND {where}
            ORDER BY d.severity DESC, d.delayed_days DESC
        """, params)

        severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}

        # Group by community
        by_community: dict = {}
        for r in rows:
            cn = r["community"]
            if cn not in by_community:
                by_community[cn] = {"community": cn, "region": r["region"],
                                    "delays": [], "affected_closings": 0}
            by_community[cn]["delays"].append(r)
            by_community[cn]["affected_closings"] += 1

        summary = list(by_community.values())
        total_affected = sum(c["affected_closings"] for c in summary)
        responsible_parties = list({r["responsible_party"] for r in rows})

        out = {
            "delays": rows,
            "by_community": summary,
            "total_affected_closings": total_affected,
            "responsible_parties": responsible_parties,
            "escalation_required": total_affected > 10,
        }
        ms = int((time.time() - t0) * 1000)
        log_tool_call("get_construction_delays",
                      {"community_name": community_name, "severity": severity},
                      out, ms, True, agent_name=agent_name, run_id=run_id)
        return out
    except Exception as e:
        ms = int((time.time() - t0) * 1000)
        log_tool_call("get_construction_delays", {"community_name": community_name},
                      None, ms, False, str(e), agent_name, run_id)
        raise
