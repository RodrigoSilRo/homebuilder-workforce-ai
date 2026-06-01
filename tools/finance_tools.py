import time
from database.db import query
from tools.base import log_tool_call


def calculate_incentive_impact(community_name: str, incentive_pct: float,
                                selected_home_ids: list = None,
                                agent_name: str = "system", run_id: int = None) -> dict:
    t0 = time.time()
    try:
        # Fetch target homes
        rows = query("""
            SELECT h.id, h.price, h.gross_margin_pct, h.status, h.days_on_market
            FROM homes h
            JOIN communities c ON h.community_id = c.id
            WHERE c.name = :name AND h.status IN ('available', 'under_contract')
        """, {"name": community_name})

        if selected_home_ids:
            rows = [r for r in rows if r["id"] in selected_home_ids]

        if not rows:
            raise ValueError(f"No active homes found for {community_name}")

        total_revenue = sum(r["price"] for r in rows)
        incentive_amount = total_revenue * (incentive_pct / 100)
        avg_margin = sum(r["gross_margin_pct"] for r in rows) / len(rows)
        margin_impact = -incentive_pct  # 1-for-1 impact (simplified)
        new_margin = avg_margin + margin_impact

        policy_limit = 1.5
        requires_approval = abs(margin_impact) >= 1.0
        blocked = abs(margin_impact) > policy_limit
        approval_level = (
            "CFO" if abs(margin_impact) > 1.0
            else "VP Sales" if abs(margin_impact) >= 0.5
            else "Sales Director"
        )

        out = {
            "community": community_name,
            "incentive_pct": incentive_pct,
            "homes_targeted": len(rows),
            "total_revenue_base": round(total_revenue),
            "incentive_amount": round(incentive_amount),
            "avg_gross_margin_pct": round(avg_margin, 1),
            "margin_impact_pct": round(margin_impact, 2),
            "projected_new_margin_pct": round(new_margin, 1),
            "policy_approval_required": requires_approval,
            "blocked_by_policy": blocked,
            "approval_level": approval_level,
            "policy_limit_pct": policy_limit,
            "recommendation": (
                "BLOCKED — exceeds policy margin limit" if blocked
                else f"Permitted with {approval_level} approval"
            ),
        }
        ms = int((time.time() - t0) * 1000)
        log_tool_call("calculate_incentive_impact",
                      {"community_name": community_name, "incentive_pct": incentive_pct},
                      out, ms, True, agent_name=agent_name, run_id=run_id)
        return out
    except Exception as e:
        ms = int((time.time() - t0) * 1000)
        log_tool_call("calculate_incentive_impact",
                      {"community_name": community_name, "incentive_pct": incentive_pct},
                      None, ms, False, str(e), agent_name, run_id)
        raise
