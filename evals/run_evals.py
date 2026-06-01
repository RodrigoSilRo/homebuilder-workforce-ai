"""
CLI eval runner — runs all eval cases and prints a summary report.

Usage:
    python -m evals.run_evals
    python -m evals.run_evals --eval EVAL-001
    python -m evals.run_evals --verbose
"""
import sys
import os
import argparse
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import init_db
from services.eval_service import run_all_evals, run_eval


def _color(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"

GREEN  = "32"
RED    = "31"
YELLOW = "33"
BOLD   = "1"


def print_result(result: dict, verbose: bool = False):
    icon    = "✅" if result["passed"] else "❌"
    pct     = f"{result['checks_passed']}/{result['checks_total']}"
    pri     = result.get("priority", "").upper()
    pri_color = RED if pri == "CRITICAL" else YELLOW if pri == "HIGH" else "37"

    print(f"\n{icon}  {_color(result['id'], BOLD)} — {result['name']}")
    print(f"   Category: {result['category']}  |  Priority: {_color(pri, pri_color)}")
    print(f"   Result:   {_color(result['pass_fail'], GREEN if result['passed'] else RED)}  ({pct} checks passed)")

    if verbose or not result["passed"]:
        for check in result["check_results"]:
            mark = _color("  ✓", GREEN) if check["passed"] else _color("  ✗", RED)
            print(f"{mark}  {check['description']}")
            if not check["passed"]:
                print(f"       → {check['detail']}")

    if result.get("error"):
        print(f"   {_color('ERROR: ' + result['error'], RED)}")


def main():
    parser = argparse.ArgumentParser(description="HomeBuilder Workforce AI — Eval Runner")
    parser.add_argument("--eval", help="Run a specific eval by ID (e.g. EVAL-001)")
    parser.add_argument("--verbose", action="store_true", help="Show all check details")
    args = parser.parse_args()

    print(_color("\n=== HomeBuilder Workforce AI -- Eval Suite ===\n", BOLD))

    init_db()

    if args.eval:
        cases_path = os.path.join(os.path.dirname(__file__), "eval_cases.json")
        with open(cases_path) as f:
            all_cases = json.load(f)
        cases = [c for c in all_cases if c["id"] == args.eval]
        if not cases:
            print(f"Eval ID '{args.eval}' not found.")
            sys.exit(1)
        from agents.graph import build_graph
        graph = build_graph()
        results = [run_eval(cases[0], graph)]
    else:
        print("Running all 4 eval cases...\n")
        results = run_all_evals()

    for r in results:
        print_result(r, verbose=args.verbose)

    total    = len(results)
    passed   = sum(1 for r in results if r["passed"])
    failed   = total - passed
    pass_pct = round(passed / total * 100) if total else 0

    print(f"\n{'-'*50}")
    print(_color(f"  Results: {passed}/{total} passed ({pass_pct}%)", BOLD))

    if failed:
        print(_color(f"  {failed} eval(s) FAILED — see details above", RED))
        sys.exit(1)
    else:
        print(_color("  All evals passed ✅", GREEN))
        sys.exit(0)


if __name__ == "__main__":
    main()
