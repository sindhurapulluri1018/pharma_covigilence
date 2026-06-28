"""
test_decision_engine.py
=======================
Unit tests for Decision Engine and Hard Gate.

These tests do NOT require any external dependencies.
"""

import pytest
from models.request_models import IncomingCase
from models.context import DuplicateContext
from services.decision_engine import DecisionEngine, HardGate


def _make_context(similarity: float) -> DuplicateContext:
    """Helper: build a minimal context with the given similarity score."""
    case = IncomingCase(
        case_id="TEST001",
        patient_name="Test Patient",
        age=40,
        gender="Male",
        drug="TestDrug",
        reaction="TestReaction",
        event_date="2025-01-01",
        report_text="Test narrative.",
    )
    ctx = DuplicateContext(incoming_case=case)
    ctx.overall_similarity = similarity
    return ctx


class TestDecisionEngine:
    """Tests for DecisionEngine.decide()."""

    def setup_method(self):
        self.engine = DecisionEngine(
            threshold_duplicate=0.90,
            threshold_possible=0.70,
        )

    def test_high_similarity_is_duplicate(self):
        ctx = _make_context(0.95)
        decision, confidence = self.engine.decide(ctx)
        assert decision == "Duplicate"
        assert confidence in ("Very High", "High")

    def test_mid_similarity_is_possible_duplicate(self):
        ctx = _make_context(0.80)
        decision, confidence = self.engine.decide(ctx)
        assert decision == "Possible Duplicate"
        assert confidence in ("Medium", "High")

    def test_low_similarity_is_unique(self):
        ctx = _make_context(0.50)
        decision, confidence = self.engine.decide(ctx)
        assert decision == "Unique Case"
        assert confidence == "N/A"

    def test_exact_duplicate_threshold(self):
        ctx = _make_context(0.90)
        decision, _ = self.engine.decide(ctx)
        assert decision == "Duplicate"

    def test_exact_possible_threshold(self):
        ctx = _make_context(0.70)
        decision, _ = self.engine.decide(ctx)
        assert decision == "Possible Duplicate"

    def test_very_high_confidence(self):
        ctx = _make_context(0.97)
        _, confidence = self.engine.decide(ctx)
        assert confidence == "Very High"

    def test_high_confidence(self):
        ctx = _make_context(0.92)
        _, confidence = self.engine.decide(ctx)
        assert confidence == "High"

    def test_medium_confidence(self):
        ctx = _make_context(0.82)
        _, confidence = self.engine.decide(ctx)
        assert confidence == "Medium"

    def test_low_confidence(self):
        ctx = _make_context(0.72)
        _, confidence = self.engine.decide(ctx)
        assert confidence == "Low"


class TestHardGate:
    """Tests for HardGate.route()."""

    def setup_method(self):
        self.gate = HardGate()

    def test_duplicate_routes_to_stop(self):
        ctx = _make_context(0.95)
        ctx.decision = "Duplicate"
        routing = self.gate.route(ctx)
        assert routing.route == "Stop"
        assert routing.workflow_state == "DUPLICATE_DETECTED"
        assert routing.next_zone == "Closed"

    def test_possible_duplicate_routes_to_hold(self):
        ctx = _make_context(0.80)
        ctx.decision = "Possible Duplicate"
        routing = self.gate.route(ctx)
        assert routing.route == "Hold"
        assert routing.workflow_state == "PENDING_HUMAN_REVIEW"
        assert routing.next_zone == "ReviewQueue"

    def test_unique_case_routes_to_proceed(self):
        ctx = _make_context(0.50)
        ctx.decision = "Unique Case"
        routing = self.gate.route(ctx)
        assert routing.route == "Proceed"
        assert routing.workflow_state == "READY_FOR_TRIAGE"
        assert routing.next_zone == "Zone3"

    def test_unknown_decision_falls_back_safely(self):
        ctx = _make_context(0.50)
        ctx.decision = "UNKNOWN_STATE"
        # Should not raise, should fall back to review queue
        routing = self.gate.route(ctx)
        assert routing is not None
        assert routing.route in ("Stop", "Hold", "Proceed")
