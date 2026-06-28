"""
test_prompt_builder.py
======================
Unit tests for the ICH E2B(R3) prompt builder.
No I/O — pure function tests.
"""

import pytest
from models.request_models import TriageRequest
from services.prompt_builder import build_user_prompt, get_system_prompt


def _make_case(**kwargs) -> TriageRequest:
    defaults = dict(
        case_id="TEST001",
        patient_name="John Doe",
        age=45,
        gender="Male",
        drug="Paracetamol",
        reaction="Severe Skin Rash",
        event_date="2025-06-10",
        report_text="Patient developed severe skin rash after taking Paracetamol.",
        workflow_state="READY_FOR_TRIAGE",
    )
    defaults.update(kwargs)
    return TriageRequest(**defaults)


class TestSystemPrompt:

    def test_system_prompt_is_non_empty(self):
        prompt = get_system_prompt()
        assert len(prompt) > 100

    def test_system_prompt_contains_ich_criteria(self):
        prompt = get_system_prompt()
        for criterion in ["Death", "Life-threatening", "Hospitalization", "Disability", "Congenital"]:
            assert criterion in prompt, f"ICH criterion '{criterion}' missing from system prompt"

    def test_system_prompt_specifies_json_only(self):
        prompt = get_system_prompt()
        assert "JSON" in prompt

    def test_system_prompt_contains_schema(self):
        prompt = get_system_prompt()
        assert "seriousness" in prompt
        assert "seriousness_criteria" in prompt
        assert "expectedness" in prompt
        assert "confidence" in prompt

    def test_system_prompt_includes_expedited_rule(self):
        prompt = get_system_prompt()
        assert "expedited" in prompt.lower()


class TestUserPrompt:

    def test_user_prompt_contains_case_id(self):
        case = _make_case(case_id="CUSTOM001")
        prompt = build_user_prompt(case)
        assert "CUSTOM001" in prompt

    def test_user_prompt_contains_drug(self):
        case = _make_case(drug="Warfarin")
        prompt = build_user_prompt(case)
        assert "Warfarin" in prompt

    def test_user_prompt_contains_reaction(self):
        case = _make_case(reaction="Intracranial bleeding")
        prompt = build_user_prompt(case)
        assert "Intracranial bleeding" in prompt

    def test_user_prompt_contains_narrative(self):
        case = _make_case(report_text="Patient was admitted to ICU.")
        prompt = build_user_prompt(case)
        assert "Patient was admitted to ICU." in prompt

    def test_user_prompt_contains_age_and_gender(self):
        case = _make_case(age=72, gender="Female")
        prompt = build_user_prompt(case)
        assert "72" in prompt
        assert "Female" in prompt

    def test_user_prompt_requests_json_only(self):
        case = _make_case()
        prompt = build_user_prompt(case)
        assert "JSON" in prompt or "json" in prompt
