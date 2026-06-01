import json
import time
from database.db import query
from tools.base import log_tool_call


def get_policy_workflow(policy_name: str = None, business_process: str = None,
                         agent_name: str = "system", run_id: int = None) -> dict:
    """
    Retrieves policy workflow for a business process.
    Uses semantic RAG search when ChromaDB is available, falls back to SQL LIKE search.
    """
    t0 = time.time()
    search_term = (policy_name or business_process or "").lower()

    try:
        # ── RAG path ──────────────────────────────────────────────────────────
        rag_results = []
        rag_used    = False
        try:
            from services.rag_service import semantic_policy_search, rag_available
            if rag_available() and search_term:
                rag_results = semantic_policy_search(search_term, n=3)
                rag_used    = True
        except Exception:
            pass

        # ── SQL path (always runs to get full structured data) ────────────────
        rows = query("""
            SELECT id, title, business_function, steps_json, approval_threshold, escalation_rule
            FROM policies
            WHERE LOWER(title) LIKE :term OR LOWER(business_function) LIKE :term
            ORDER BY id
        """, {"term": f"%{search_term}%"})

        # If RAG found something SQL didn't, merge by title
        if rag_results and not rows:
            rag_titles = {r["title"].lower() for r in rag_results if r["type"] == "policy"}
            rows = query("""
                SELECT id, title, business_function, steps_json, approval_threshold, escalation_rule
                FROM policies ORDER BY id
            """)
            rows = [r for r in rows if r["title"].lower() in rag_titles] or rows

        results = []
        for r in rows:
            steps = json.loads(r["steps_json"]) if r["steps_json"] else []
            results.append({
                "id":                r["id"],
                "title":             r["title"],
                "business_function": r["business_function"],
                "steps":             steps,
                "required_approvers": _extract_approvers(steps),
                "approval_threshold": r["approval_threshold"],
                "escalation_rule":   r["escalation_rule"],
            })

        out = {
            "policies":    results,
            "count":       len(results),
            "search_term": search_term,
            "retrieval":   "rag+sql" if rag_used else "sql",
            "rag_matches": [
                {"title": r["title"], "relevance": r["relevance_score"], "function": r["function"]}
                for r in rag_results
            ] if rag_used else [],
        }

        ms = int((time.time() - t0) * 1000)
        log_tool_call("get_policy_workflow",
                      {"policy_name": policy_name, "business_process": business_process,
                       "retrieval_mode": out["retrieval"]},
                      out, ms, True, agent_name=agent_name, run_id=run_id)
        return out

    except Exception as e:
        ms = int((time.time() - t0) * 1000)
        log_tool_call("get_policy_workflow",
                      {"policy_name": policy_name, "business_process": business_process},
                      None, ms, False, str(e), agent_name, run_id)
        raise


def _extract_approvers(steps: list) -> list:
    keywords = ["approval", "approves", "notified", "required", "vp", "director", "manager"]
    return [step for step in steps if any(k in step.lower() for k in keywords)]
