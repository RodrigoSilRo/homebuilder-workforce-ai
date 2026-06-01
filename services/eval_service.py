"""
Eval Service — runs eval cases against the live LangGraph graph.

Each eval case defines a set of declarative checks against the final graph state.
Checks are deterministic (no LLM required) so evals run fast and reproducibly.
Results are written to eval_runs and eval_cases tables.
"""
import json
from datetime import datetime
from typing import Any

from database.db import execute, query


# ── State traversal ───────────────────────────────────────────────────────────

def _get_nested(obj: Any, path: list) -> Any:
    """Traverse a nested dict/list by path list. Returns None if not found."""
    for key in path:
        if obj is None:
            return None
        if isinstance(obj, dict):
            obj = obj.get(key)
        elif isinstance(obj, list):
            try:
                obj = obj[int(key)]
            except (IndexError, ValueError):
                return None
        else:
            return None
    return obj


# ── Check evaluators ──────────────────────────────────────────────────────────

def _run_check(check: dict, state: dict) -> dict:
    """Evaluate a single check against the final graph state. Returns {passed, description, detail}."""
    ctype = check["type"]
    desc  = check["description"]

    try:
        if ctype == "agent_present":
            agent = check["agent"]
            passed = agent in state.get("agent_outputs", {})
            detail = f"Found: {list(state.get('agent_outputs', {}).keys())}"

        elif ctype == "tool_result":
            path   = check["path"]
            expect = check["expected"]
            actual = _get_nested(state.get("tool_results", {}), path)
            passed = actual == expect
            detail = f"Expected {expect}, got {actual}"

        elif ctype == "tool_result_key_exists":
            path   = check["path"]
            actual = _get_nested(state.get("tool_results", {}), path)
            passed = actual is not None
            detail = f"Path tool_results.{'.'.join(str(p) for p in path)} = {type(actual).__name__}"

        elif ctype == "state_equals":
            key    = check["key"]
            expect = check["expected"]
            actual = state.get(key)
            passed = actual == expect
            detail = f"Expected {expect}, got {actual}"

        elif ctype == "state_in":
            key    = check["key"]
            values = check["values"]
            actual = state.get(key)
            passed = actual in values
            detail = f"Expected one of {values}, got {actual}"

        elif ctype == "state_nonempty":
            key    = check["key"]
            actual = state.get(key)
            passed = bool(actual)
            detail = f"Value: {str(actual)[:80]}"

        elif ctype == "tool_results_nonempty":
            tr     = state.get("tool_results", {})
            passed = len(tr) > 0
            detail = f"Tool results keys: {list(tr.keys())}"

        elif ctype == "agent_output_field":
            agent     = check["agent"]
            field     = check["field"]
            min_len   = check.get("min_length", 1)
            output    = state.get("agent_outputs", {}).get(agent, {})
            value     = output.get(field, [])
            passed    = isinstance(value, (list, str)) and len(value) >= min_len
            detail    = f"Field '{field}' length: {len(value) if value else 0}"

        elif ctype == "validation_field":
            field  = check["field"]
            expect = check["expected"]
            actual = state.get("validation_result", {}).get(field)
            passed = actual == expect
            detail = f"Expected {expect}, got {actual}"

        elif ctype == "aprs_created":
            # Check either audit_metadata.created_aprs OR agent finding mentions APR creation
            min_count = check.get("min_count", 1)
            created   = state.get("audit_metadata", {}).get("created_aprs", [])
            # Also accept if Vendor Approval Agent finding mentions "Approval request created"
            vendor_finding = state.get("agent_outputs", {}).get("Vendor Approval Agent", {}).get("finding", "")
            passed    = len(created) >= min_count or "Approval request created" in vendor_finding
            detail    = f"APRs in metadata: {created} | Vendor finding mentions APR: {'Approval request created' in vendor_finding}"

        elif ctype == "agent_output_contains":
            agent  = check["agent"]
            field  = check.get("field", "finding")
            needle = check["contains"]
            output = state.get("agent_outputs", {}).get(agent, {})
            value  = str(output.get(field, ""))
            passed = needle in value
            detail = f"Looking for '{needle}' in {field}: {'found' if passed else 'not found'}"

        else:
            passed = False
            detail = f"Unknown check type: {ctype}"

    except Exception as e:
        passed = False
        detail = f"Check error: {e}"

    return {
        "id":          check.get("id", "?"),
        "description": desc,
        "passed":      passed,
        "detail":      detail,
    }


# ── Eval runner ───────────────────────────────────────────────────────────────

def run_eval(eval_case: dict, graph=None) -> dict:
    """
    Run a single eval case against the LangGraph graph.
    Returns full result including per-check pass/fail and the final state.
    """
    if graph is None:
        from agents.graph import build_graph
        graph = build_graph()

    state = {"user_prompt": eval_case["prompt"], "run_id": None}
    final: dict = {}

    try:
        for event in graph.stream(state, stream_mode="updates"):
            for node, update in event.items():
                if node in ("__end__", "__start__") or not update:
                    continue
                for k, v in update.items():
                    if isinstance(v, dict) and isinstance(final.get(k), dict):
                        final[k] = {**final.get(k, {}), **v}
                    elif v is not None:
                        final[k] = v
        error = None
    except Exception as e:
        error = str(e)
        final = {}

    checks = eval_case.get("checks", [])
    check_results = [_run_check(c, final) for c in checks]

    passed       = all(r["passed"] for r in check_results) and error is None
    checks_ok    = sum(1 for r in check_results if r["passed"])
    pass_fail    = "PASS" if passed else "FAIL"

    # Persist to eval_runs
    now = datetime.now().isoformat()
    execute("""
        INSERT INTO eval_runs (eval_id, eval_name, prompt, pass_fail, checks_passed, checks_total, run_at, details_json)
        VALUES (:eid, :name, :prompt, :pf, :ok, :total, :ts, :details)
    """, {
        "eid":     eval_case["id"],
        "name":    eval_case["name"],
        "prompt":  eval_case["prompt"],
        "pf":      pass_fail,
        "ok":      checks_ok,
        "total":   len(check_results),
        "ts":      now,
        "details": json.dumps(check_results, default=str),
    })

    # Update eval_cases table with latest result
    execute(
        "UPDATE eval_cases SET pass_fail = :pf, notes = :notes WHERE id = :id",
        {"pf": pass_fail, "notes": f"Last run: {now[:16]} — {checks_ok}/{len(check_results)} checks passed", "id": eval_case["id"]},
    )

    return {
        "id":           eval_case["id"],
        "name":         eval_case["name"],
        "category":     eval_case.get("category", ""),
        "priority":     eval_case.get("priority", "medium"),
        "pass_fail":    pass_fail,
        "passed":       passed,
        "checks_passed": checks_ok,
        "checks_total": len(check_results),
        "check_results": check_results,
        "error":        error,
        "run_at":       now,
    }


def run_all_evals(graph=None) -> list[dict]:
    """Run all eval cases from eval_cases.json. Returns list of results."""
    import os
    cases_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "evals", "eval_cases.json")
    with open(cases_path) as f:
        cases = json.load(f)

    if graph is None:
        from agents.graph import build_graph
        graph = build_graph()

    return [run_eval(case, graph) for case in cases]


def get_eval_history(limit: int = 50) -> list[dict]:
    """Return recent eval run history from the DB."""
    return query("""
        SELECT eval_id, eval_name, pass_fail, checks_passed, checks_total, run_at
        FROM eval_runs
        ORDER BY run_at DESC
        LIMIT :lim
    """, {"lim": limit})


def get_eval_drift(eval_id: str, limit: int = 20) -> list[dict]:
    """Return pass/fail history for a specific eval (for drift chart)."""
    return query("""
        SELECT pass_fail, checks_passed, checks_total, run_at
        FROM eval_runs
        WHERE eval_id = :id
        ORDER BY run_at DESC
        LIMIT :lim
    """, {"id": eval_id, "lim": limit})
