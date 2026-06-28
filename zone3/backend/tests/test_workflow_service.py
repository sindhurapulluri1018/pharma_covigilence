"""
test_workflow_service.py
========================
Unit tests for WorkflowService state transitions.
"""

import pytest
import config
from models.request_models import TriageRequest
from models.context import TriageContext
from services.workflow_service import WorkflowService


def _make_ctx() -> TriageContext:
    case = TriageRequest(
        case_id="TEST001", patient_name="Test", age=40, gender="Male",
        drug="TestDrug", reaction="TestReaction",
        event_date="2025-01-01", report_text="Test.",
        workflow_state="READY_FOR_TRIAGE",
    )
    return TriageContext(incoming_case=case)


@pytest.fixture
def service():
    return WorkflowService()


class TestWorkflowTransitions:

    def test_success_transitions_to_ready_for_extraction(self, service):
        ctx = _make_ctx()
        service.transition(ctx, success=True)
        assert ctx.workflow_state == config.WF_READY_FOR_EXTRACTION

    def test_failure_transitions_to_triage_failed(self, service):
        ctx = _make_ctx()
        service.transition(ctx, success=False)
        assert ctx.workflow_state == config.WF_TRIAGE_FAILED

    def test_success_is_default(self, service):
        ctx = _make_ctx()
        service.transition(ctx)
        assert ctx.workflow_state == config.WF_READY_FOR_EXTRACTION

    def test_ready_for_extraction_constant(self):
        assert config.WF_READY_FOR_EXTRACTION == "READY_FOR_EXTRACTION"

    def test_triage_failed_constant(self):
        assert config.WF_TRIAGE_FAILED == "TRIAGE_FAILED"
