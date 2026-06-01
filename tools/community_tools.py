import time
from database.db import query
from tools.base import log_tool_call


def get_community_metrics(region: str = None, community_name: str = None,
                           agent_name: str = "system", run_id: int = None) -> dict:
    t0 = time.time()
    params = {}
    clauses = []
    if region:
        clauses.append("region = :region")
        params["region"] = region
    if community_name:
        clauses.append("name = :name")
        params["name"] = community_name
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""

    try:
        rows = query(f"""
            SELECT id, name, region, city, state,
                   active_homes, target_monthly_sales, actual_monthly_sales,
                   avg_price, avg_days_on_market, gross_margin_pct,
                   stale_homes, lead_volume, lead_conversion_pct
            FROM communities {where}
            ORDER BY CAST(actual_monthly_sales AS REAL) / target_monthly_sales ASC
        """, params)

        result = []
        for r in rows:
            variance = ((r["actual_monthly_sales"] - r["target_monthly_sales"]) /
                        r["target_monthly_sales"]) * 100
            result.append({**r, "variance_pct": round(variance, 1),
                           "on_target": r["actual_monthly_sales"] >= r["target_monthly_sales"]})

        out = {"communities": result, "count": len(result)}
        ms = int((time.time() - t0) * 1000)
        log_tool_call("get_community_metrics", {"region": region, "community_name": community_name},
                      out, ms, True, agent_name=agent_name, run_id=run_id)
        return out
    except Exception as e:
        ms = int((time.time() - t0) * 1000)
        log_tool_call("get_community_metrics", {"region": region, "community_name": community_name},
                      None, ms, False, str(e), agent_name, run_id)
        raise


def get_inventory_status(community_name: str, stale_days_threshold: int = 60,
                          agent_name: str = "system", run_id: int = None) -> dict:
    t0 = time.time()
    try:
        rows = query("""
            SELECT h.lot_number, h.plan_name, h.price, h.status,
                   h.days_on_market, h.completion_status, h.gross_margin_pct
            FROM homes h
            JOIN communities c ON h.community_id = c.id
            WHERE c.name = :name
            ORDER BY h.days_on_market DESC
        """, {"name": community_name})

        stale = [r for r in rows if r["days_on_market"] >= stale_days_threshold]
        active = [r for r in rows if r["status"] != "closed"]

        avg_margin = (sum(r["gross_margin_pct"] for r in active) / len(active)) if active else 0
        price_bands = {"under_400k": 0, "400k_500k": 0, "500k_600k": 0, "over_600k": 0}
        for r in active:
            p = r["price"]
            if p < 400000:       price_bands["under_400k"] += 1
            elif p < 500000:     price_bands["400k_500k"] += 1
            elif p < 600000:     price_bands["500k_600k"] += 1
            else:                price_bands["over_600k"] += 1

        out = {
            "community": community_name,
            "total_active": len(active),
            "stale_homes": stale,
            "stale_count": len(stale),
            "avg_gross_margin_pct": round(avg_margin, 1),
            "price_bands": price_bands,
        }
        ms = int((time.time() - t0) * 1000)
        log_tool_call("get_inventory_status", {"community_name": community_name, "stale_days_threshold": stale_days_threshold},
                      out, ms, True, agent_name=agent_name, run_id=run_id)
        return out
    except Exception as e:
        ms = int((time.time() - t0) * 1000)
        log_tool_call("get_inventory_status", {"community_name": community_name},
                      None, ms, False, str(e), agent_name, run_id)
        raise


def get_lead_conversion(community_name: str = None, region: str = None,
                         days_back: int = 30, agent_name: str = "system", run_id: int = None) -> dict:
    t0 = time.time()
    params = {}
    clauses = ["1=1"]
    if community_name:
        clauses.append("c.name = :name")
        params["name"] = community_name
    if region:
        clauses.append("c.region = :region")
        params["region"] = region
    where = " AND ".join(clauses)

    try:
        rows = query(f"""
            SELECT c.name AS community, c.lead_volume, c.lead_conversion_pct,
                   COUNT(l.id) AS total_leads,
                   SUM(l.converted) AS converted_leads,
                   l.source
            FROM communities c
            LEFT JOIN leads l ON l.community_id = c.id
            WHERE {where}
            GROUP BY c.id, l.source
        """, params)

        communities: dict = {}
        for r in rows:
            cn = r["community"]
            if cn not in communities:
                communities[cn] = {
                    "community": cn,
                    "lead_volume": r["lead_volume"],
                    "conversion_rate_pct": r["lead_conversion_pct"],
                    "sources": {},
                }
            if r["source"]:
                communities[cn]["sources"][r["source"]] = {
                    "leads": r["total_leads"],
                    "converted": r["converted_leads"],
                }

        out = {"results": list(communities.values()), "count": len(communities)}
        ms = int((time.time() - t0) * 1000)
        log_tool_call("get_lead_conversion", {"community_name": community_name, "region": region, "days_back": days_back},
                      out, ms, True, agent_name=agent_name, run_id=run_id)
        return out
    except Exception as e:
        ms = int((time.time() - t0) * 1000)
        log_tool_call("get_lead_conversion", {"community_name": community_name},
                      None, ms, False, str(e), agent_name, run_id)
        raise
