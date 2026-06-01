import time
from database.db import query
from tools.base import log_tool_call


_TEMPLATES = {
    "stale_inventory": {
        "brief": "Target buyers considering move-in-ready homes. Emphasize immediate availability, "
                 "no construction wait, and current incentive offer. Channels: email, social, digital.",
        "email": "Subject: Your Dream Home Is Ready Now — {community}\n\n"
                 "Hi [First Name],\n\nWe know you've been searching, and we want you to know: "
                 "your home at {community} is ready today. No waiting. No delays.\n\n"
                 "Move-in-ready homes starting from [price]. For a limited time, we're offering "
                 "[incentive]% toward closing costs or upgrades.\n\n"
                 "Schedule your private tour this weekend →\n\nThe {community} Team",
        "ad": "{community}: Move In This Weekend. "
              "Ready-to-close homes from [price]. Limited incentive available. Tour today.",
        "sms": "{community} — Ready homes available now. [Incentive] offer ends [date]. "
               "Reply TOUR for a same-week appointment.",
    },
    "lead_conversion": {
        "brief": "Re-engage warm leads who visited but haven't committed. Emphasize community lifestyle, "
                 "pricing transparency, and next-step clarity. Channels: email, retargeting.",
        "email": "Subject: Still Thinking About {community}? Let Us Help.\n\n"
                 "Hi [First Name],\n\nWe noticed you visited {community} recently — and we think "
                 "you're going to love what's new.\n\nWe've updated our available homes and have "
                 "an associate ready to walk you through exactly what fits your timeline and budget.\n\n"
                 "No pressure. Just clarity. Book a 20-minute call →\n\nThe {community} Team",
        "ad": "You visited {community}. Still looking? New homes available. "
              "Let's find your fit — schedule a call today.",
        "sms": "Hi [Name], it's {community}. Ready to talk through your options? "
               "Reply YES and we'll reach out today.",
    },
}


def generate_marketing_campaign(community_name: str, target_audience: str, objective: str,
                                  agent_name: str = "system", run_id: int = None) -> dict:
    t0 = time.time()
    try:
        # Fetch community context
        rows = query("""
            SELECT name, avg_price, stale_homes, lead_conversion_pct, actual_monthly_sales, target_monthly_sales
            FROM communities WHERE name = :name
        """, {"name": community_name})

        ctx = rows[0] if rows else {"name": community_name, "avg_price": 450000, "stale_homes": 0,
                                    "lead_conversion_pct": 15.0, "actual_monthly_sales": 10, "target_monthly_sales": 12}

        template_key = "lead_conversion" if "conversion" in objective.lower() else "stale_inventory"
        tmpl = _TEMPLATES[template_key]

        def fill(text):
            return (text.replace("{community}", community_name)
                        .replace("[price]", f"${ctx['avg_price']:,.0f}")
                        .replace("[incentive]", "1.25")
                        .replace("[date]", "month-end"))

        out = {
            "community": community_name,
            "objective": objective,
            "target_audience": target_audience,
            "campaign_brief": fill(tmpl["brief"]),
            "email_copy": fill(tmpl["email"]),
            "ad_copy": fill(tmpl["ad"]),
            "sms_copy": fill(tmpl["sms"]),
            "approval_required": True,
            "note": "All copy requires Regional Marketing Director approval before launch.",
        }
        ms = int((time.time() - t0) * 1000)
        log_tool_call("generate_marketing_campaign",
                      {"community_name": community_name, "objective": objective},
                      out, ms, True, agent_name=agent_name, run_id=run_id)
        return out
    except Exception as e:
        ms = int((time.time() - t0) * 1000)
        log_tool_call("generate_marketing_campaign",
                      {"community_name": community_name},
                      None, ms, False, str(e), agent_name, run_id)
        raise
