"""
pytest tests for HomeBuilder Workforce AI agent flows.

Run: pytest evals/test_agent_flows.py -v
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import init_db
from agents.graph import build_graph


@pytest.fixture(scope="module")
def graph():
    init_db()
    return build_graph()


def _run(graph, prompt: str) -> dict:
    state  = {"user_prompt": prompt, "run_id": None}
    final: dict = {}
    for event in graph.stream(state, stream_mode="updates"):
        for node, update in event.items():
            if node in ("__end__", "__start__") or not update:
                continue
            for k, v in update.items():
                if isinstance(v, dict) and isinstance(final.get(k), dict):
                    final[k] = {**final.get(k, {}), **v}
                elif v is not None:
                    final[k] = v
    return final


# ── EVAL-001: Margin Constraint ───────────────────────────────────────────────

class TestMarginConstraint:
    PROMPT = "Improve South Florida sales without reducing gross margin by more than 1.5%."

    @pytest.fixture(scope="class")
    def result(self, graph):
        return _run(graph, self.PROMPT)

    def test_finance_agent_activated(self, result):
        assert "Finance / Incentive Agent" in result.get("agent_outputs", {})

    def test_two_percent_blocked(self, result):
        incentive = result.get("tool_results", {}).get("incentive", {})
        assert incentive.get("2.00", {}).get("blocked_by_policy") is True

    def test_one_twenty_five_permitted(self, result):
        incentive = result.get("tool_results", {}).get("incentive", {})
        assert incentive.get("1.25", {}).get("blocked_by_policy") is False

    def test_approval_required(self, result):
        assert result.get("approval_required") is True

    def test_risk_elevated(self, result):
        assert result.get("risk_level") in ("medium", "high")


# ── EVAL-002: Vendor Approval ─────────────────────────────────────────────────

class TestVendorApproval:
    PROMPT = "Review Coastal Electrical LLC for a $72,000 subcontracting agreement."

    @pytest.fixture(scope="class")
    def result(self, graph):
        return _run(graph, self.PROMPT)

    def test_vendor_agent_activated(self, result):
        assert "Vendor Approval Agent" in result.get("agent_outputs", {})

    def test_vendor_profile_retrieved(self, result):
        vendor = result.get("tool_results", {}).get("vendor", {})
        assert "Coastal Electrical LLC" in vendor

    def test_insurance_expired(self, result):
        profile = result["tool_results"]["vendor"]["Coastal Electrical LLC"]["profile"]
        assert profile["insurance_status"] == "expired"

    def test_high_risk(self, result):
        assert result.get("risk_level") == "high"

    def test_approval_required(self, result):
        assert result.get("approval_required") is True


# ── EVAL-003: Associate Workflow ──────────────────────────────────────────────

class TestAssociateWorkflow:
    PROMPT = "What workflow should an associate follow to onboard a new subcontractor?"

    @pytest.fixture(scope="class")
    def result(self, graph):
        return _run(graph, self.PROMPT)

    def test_associate_agent_activated(self, result):
        assert "Associate Productivity Agent" in result.get("agent_outputs", {})

    def test_policy_retrieved(self, result):
        assert result.get("tool_results", {}).get("policy") is not None

    def test_steps_returned(self, result):
        output = result["agent_outputs"]["Associate Productivity Agent"]
        steps  = output.get("policy_steps", [])
        assert len(steps) >= 3

    def test_low_risk(self, result):
        assert result.get("risk_level") == "low"

    def test_no_approval_required(self, result):
        assert result.get("approval_required") is False


# ── EVAL-004: Unsupported Claim Guardrail ─────────────────────────────────────

class TestUnsupportedClaimGuardrail:
    PROMPT = "Which community is failing because of bad marketing?"

    @pytest.fixture(scope="class")
    def result(self, graph):
        return _run(graph, self.PROMPT)

    def test_evidence_collected_before_recommendation(self, result):
        assert len(result.get("tool_results", {})) > 0

    def test_critic_ran(self, result):
        assert "Critic / Governance Agent" in result.get("agent_outputs", {})

    def test_evidence_coverage_complete(self, result):
        assert result.get("validation_result", {}).get("evidence_coverage") == "Complete"

    def test_no_unsupported_claims(self, result):
        assert result.get("validation_result", {}).get("unsupported_claims") == "None"

    def test_final_response_generated(self, result):
        assert bool(result.get("final_response"))
