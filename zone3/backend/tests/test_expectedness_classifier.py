"""
test_expectedness_classifier.py
================================
Unit tests for ExpectednessService label lookup.

No OpenAI calls — tests the mock label lookup only.

Key design assertion: mock_labels.json is ALWAYS the authority.
Even if ctx.llm_parsed contained an "expectedness" field, it must be ignored.
"""

import pytest
from models.context import TriageContext
from models.request_models import TriageRequest
from services.expectedness_classifier import ExpectednessService


@pytest.fixture
def clf():
    return ExpectednessService()


def _make_ctx(drug: str, reaction: str) -> TriageContext:
    """Helper: build a minimal TriageContext for a given drug + reaction."""
    request = TriageRequest(
        case_id="TEST001",
        workflow_state="READY_FOR_TRIAGE",
        patient_name="Test Patient",
        age=40,
        gender="Unknown",
        drug=drug,
        reaction=reaction,
        event_date="2025-01-01",
        report_text=f"Patient experienced {reaction} after taking {drug}.",
    )
    return TriageContext(incoming_case=request)


# ===========================================================================
# Label lookup (deterministic path)
# ===========================================================================

class TestLabelLookup:

    def test_known_reaction_is_expected(self, clf):
        result = clf._label_lookup("Paracetamol", "Skin Rash")
        assert result == "Expected"

    def test_known_reaction_case_insensitive(self, clf):
        result = clf._label_lookup("paracetamol", "skin rash")
        assert result == "Expected"

    def test_unknown_drug_is_unexpected(self, clf):
        result = clf._label_lookup("UnknownDrug999", "Skin Rash")
        assert result == "Unexpected"

    def test_unknown_reaction_for_known_drug_is_unexpected(self, clf):
        result = clf._label_lookup("Paracetamol", "Intracranial Bleeding")
        assert result == "Unexpected"

    def test_metformin_lactic_acidosis_expected(self, clf):
        result = clf._label_lookup("Metformin", "Lactic Acidosis")
        assert result == "Expected"

    def test_warfarin_bleeding_expected(self, clf):
        result = clf._label_lookup("Warfarin", "Haemorrhage")
        assert result == "Expected"

    def test_warfarin_rash_unexpected(self, clf):
        """Skin Rash is not a known Warfarin reaction."""
        result = clf._label_lookup("Warfarin", "Severe Skin Rash")
        assert result == "Unexpected"

    def test_amoxicillin_allergic_reaction_expected(self, clf):
        result = clf._label_lookup("Amoxicillin", "Allergic Reaction")
        assert result == "Expected"

    def test_fuzzy_match_partial_string(self, clf):
        """'Nausea and vomiting' should fuzzy-match 'Nausea' in the label."""
        result = clf._label_lookup("Paracetamol", "Nausea and vomiting after meal")
        assert result == "Expected"

    def test_future_hook_who_label_raises(self, clf):
        with pytest.raises(NotImplementedError):
            clf.load_from_who_label("Paracetamol")

    def test_future_hook_smpc_raises(self, clf):
        with pytest.raises(NotImplementedError):
            clf.load_from_smpc("Metformin")


# ===========================================================================
# LLM bypass assertion — the core design invariant
# ===========================================================================

class TestLLMBypass:
    """
    Confirm that the LLM result is NEVER used to determine expectedness.

    Even if ctx.llm_parsed contains an "expectedness" field, the label
    database must always win. This was the major architectural change.
    """

    def test_llm_expected_overridden_by_label(self, clf):
        """
        LLM says 'Expected', but Intracranial Bleeding is NOT on Paracetamol label.
        The label must win → Unexpected.
        """
        ctx = _make_ctx("Paracetamol", "Intracranial Bleeding")
        ctx.llm_parsed = {"expectedness": "Expected"}   # LLM says Expected
        ctx.llm_model_used = "gpt-4o"
        clf.classify(ctx)
        assert ctx.expectedness == "Unexpected", (
            "Label lookup must override LLM: Intracranial Bleeding is not on Paracetamol label"
        )
        assert ctx.expectedness_source == "Mock Product Label"

    def test_llm_unexpected_overridden_by_label(self, clf):
        """
        LLM says 'Unexpected', but Skin Rash IS on Paracetamol label.
        The label must win → Expected.
        """
        ctx = _make_ctx("Paracetamol", "Skin Rash")
        ctx.llm_parsed = {"expectedness": "Unexpected"}  # LLM says Unexpected
        ctx.llm_model_used = "gpt-4o"
        clf.classify(ctx)
        assert ctx.expectedness == "Expected", (
            "Label lookup must override LLM: Skin Rash IS on Paracetamol label"
        )
        assert ctx.expectedness_source == "Mock Product Label"

    def test_expectedness_source_is_always_label(self, clf):
        """expectedness_source must always be 'Mock Product Label', never an LLM name."""
        ctx = _make_ctx("Warfarin", "Haemorrhage")
        ctx.llm_parsed = {"expectedness": "Unexpected"}
        clf.classify(ctx)
        assert ctx.expectedness_source == "Mock Product Label"
        assert "LLM" not in ctx.expectedness_source
        assert "gpt" not in ctx.expectedness_source.lower()

    def test_no_llm_parsed_still_uses_label(self, clf):
        """If llm_parsed is empty, label lookup should still work normally."""
        ctx = _make_ctx("Metformin", "Lactic Acidosis")
        ctx.llm_parsed = {}
        clf.classify(ctx)
        assert ctx.expectedness == "Expected"
