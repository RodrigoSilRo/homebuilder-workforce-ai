import time
from database.db import query
from tools.base import log_tool_call

CONTRACT_APPROVAL_THRESHOLD = 50000
RISK_SCORE_THRESHOLD = 70


def get_vendor_profile(vendor_name: str, agent_name: str = "system", run_id: int = None) -> dict:
    t0 = time.time()
    try:
        rows = query("""
            SELECT id, name, category, region, insurance_status,
                   risk_score, payment_history_score, active_contract_value
            FROM vendors WHERE name = :name
        """, {"name": vendor_name})

        if not rows:
            raise ValueError(f"Vendor not found: {vendor_name}")

        v = rows[0]
        flags = []
        if v["insurance_status"] != "current":
            flags.append(f"Insurance status: {v['insurance_status']}")
        if v["risk_score"] >= RISK_SCORE_THRESHOLD:
            flags.append(f"High risk score: {v['risk_score']}")
        if v["active_contract_value"] > CONTRACT_APPROVAL_THRESHOLD:
            flags.append(f"Contract value ${v['active_contract_value']:,.0f} exceeds $50K threshold")

        out = {**v, "flags": flags,
               "approval_required": len(flags) > 0,
               "risk_level": "high" if v["risk_score"] >= 70 else "medium" if v["risk_score"] >= 40 else "low"}
        ms = int((time.time() - t0) * 1000)
        log_tool_call("get_vendor_profile", {"vendor_name": vendor_name},
                      out, ms, True, agent_name=agent_name, run_id=run_id)
        return out
    except Exception as e:
        ms = int((time.time() - t0) * 1000)
        log_tool_call("get_vendor_profile", {"vendor_name": vendor_name},
                      None, ms, False, str(e), agent_name, run_id)
        raise


def get_vendor_risk_score(vendor_name: str, agent_name: str = "system", run_id: int = None) -> dict:
    t0 = time.time()
    try:
        rows = query("""
            SELECT name, insurance_status, risk_score, payment_history_score, active_contract_value
            FROM vendors WHERE name = :name
        """, {"name": vendor_name})

        if not rows:
            raise ValueError(f"Vendor not found: {vendor_name}")

        v = rows[0]
        score = v["risk_score"]
        risk_factors = []
        if v["insurance_status"] != "current":
            risk_factors.append("Expired or missing insurance certificate")
        if score >= 70:
            risk_factors.append(f"High composite risk score ({score}/100)")
        if v["payment_history_score"] < 75:
            risk_factors.append(f"Below-average payment history ({v['payment_history_score']}/100)")
        if v["active_contract_value"] > CONTRACT_APPROVAL_THRESHOLD:
            risk_factors.append(f"Contract value exceeds approval threshold")

        risk_label = "high" if score >= 70 else "medium" if score >= 40 else "low"
        recommendation = (
            "Do not approve — resolve insurance and risk issues first" if score >= 70 or v["insurance_status"] != "current"
            else "Approve with standard monitoring" if score < 40
            else "Approve with enhanced monitoring"
        )

        out = {
            "vendor": vendor_name,
            "risk_score": score,
            "risk_level": risk_label,
            "risk_factors": risk_factors,
            "payment_history_score": v["payment_history_score"],
            "recommendation": recommendation,
        }
        ms = int((time.time() - t0) * 1000)
        log_tool_call("get_vendor_risk_score", {"vendor_name": vendor_name},
                      out, ms, True, agent_name=agent_name, run_id=run_id)
        return out
    except Exception as e:
        ms = int((time.time() - t0) * 1000)
        log_tool_call("get_vendor_risk_score", {"vendor_name": vendor_name},
                      None, ms, False, str(e), agent_name, run_id)
        raise
