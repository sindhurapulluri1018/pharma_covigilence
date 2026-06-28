"""
test_priority_router.py
=======================
Unit tests for the deterministic PriorityRouter.
No LLM calls required.
"""

import pytest
from models.request_models import TriageRequest
from models.context import TriageContext
from services.priority_router import PriorityRouter


def _make_ctx(seriousness: str, criteria: list[str]) -> TriageContext:
    case = TriageRequest(
        case_id="TEST001", patient_name="Test", age=40, gender="Male",
        drug="TestDrug", reaction="TestReaction",
        event_date="2025-01-01", report_text="Test narrative.",
        workflow_state="READY_FOR_TRIAGE",
    )
    ctx = TriageContext(incoming_case=case)
    ctx.seriousness = seriousness
    ctx.seriousness_criteria = criteria
    return ctx


@pytest.fixture
def router():
    return PriorityRouter()


class TestCriticalCases:

    def test_death_routes_to_critical(self, router):
        ctx = _make_ctx("Serious", ["Death"])
        router.route(ctx)
        assert ctx.queue == "Critical Queue"
        assert ctx.priority == "Critical"
        assert ctx.expedited_required is True

    def test_life_threatening_routes_to_critical(self, router):
        ctx = _make_ctx("Serious", ["Life-threatening"])
        router.route(ctx)
        assert ctx.queue == "Critical Queue"
        assert ctx.expedited_required is True

    def test_death_overrides_hospitalization(self, router):
        """Death + Hospitalization → Critical (not Expedited)."""
        ctx = _make_ctx("Serious", ["Hospitalization", "Death"])
        router.route(ctx)
        assert ctx.queue == "Critical Queue"


class TestExpeditedCases:

    def test_hospitalization_routes_to_expedited(self, router):
        ctx = _make_ctx("Serious", ["Hospitalization"])
        router.route(ctx)
        assert ctx.queue == "Expedited Queue"
        assert ctx.priority == "High"
        assert ctx.expedited_required is True

    def test_disability_routes_to_expedited(self, router):
        ctx = _make_ctx("Serious", ["Disability"])
        router.route(ctx)
        assert ctx.queue == "Expedited Queue"

    def test_congenital_anomaly_routes_to_expedited(self, router):
        ctx = _make_ctx("Serious", ["Congenital Anomaly"])
        router.route(ctx)
        assert ctx.queue == "Expedited Queue"

    def test_other_medically_important_routes_to_expedited(self, router):
        ctx = _make_ctx("Serious", ["Other Medically Important Condition"])
        router.route(ctx)
        assert ctx.queue == "Expedited Queue"


class TestStandardCases:

    def test_non_serious_routes_to_standard(self, router):
        ctx = _make_ctx("Non-serious", [])
        router.route(ctx)
        assert ctx.queue == "Standard Queue"
        assert ctx.priority == "Standard"
        assert ctx.expedited_required is False

    def test_empty_criteria_serious_routes_to_expedited(self, router):
        """Edge case: Serious with no specific criteria → Expedited (conservative)."""
        ctx = _make_ctx("Serious", [])
        router.route(ctx)
        assert ctx.queue == "Expedited Queue"


class TestNextZone:

    def test_next_zone_is_zone4(self, router):
        ctx = _make_ctx("Serious", ["Death"])
        router.route(ctx)
        assert ctx.next_zone == "Zone4"
