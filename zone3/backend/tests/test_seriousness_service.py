"""
test_seriousness_service.py
============================
Tests for FallbackClassifier (keyword-based) in core/llm_manager.py,
and for ResponseParser validation logic.

These tests do NOT call OpenAI — they exercise the fallback path and
response parser directly.

Negation tests verify the fix for: "patient was not hospitalized"
should NOT trigger the Hospitalization criterion.
"""

import pytest
from core.llm_manager import FallbackClassifier, ResponseParser


@pytest.fixture
def clf():
    return FallbackClassifier()


# ===========================================================================
# FallbackClassifier — Positive keyword tests
# ===========================================================================

class TestFallbackDeathCriteria:

    def test_death_keyword(self, clf):
        result = clf.classify("The patient died following cardiac arrest.")
        assert result["seriousness"] == "Serious"
        assert "Death" in result["seriousness_criteria"]

    def test_fatal_keyword(self, clf):
        result = clf.classify("Fatal outcome was reported.")
        assert "Death" in result["seriousness_criteria"]

    def test_deceased_keyword(self, clf):
        result = clf.classify("Patient was found deceased at home.")
        assert "Death" in result["seriousness_criteria"]


class TestFallbackLifeThreatening:

    def test_life_threatening_keyword(self, clf):
        result = clf.classify("The reaction was life-threatening and required ICU admission.")
        assert "Life-threatening" in result["seriousness_criteria"]

    def test_cardiac_arrest_keyword(self, clf):
        result = clf.classify("Patient suffered cardiac arrest during infusion.")
        assert "Life-threatening" in result["seriousness_criteria"]

    def test_icu_keyword(self, clf):
        result = clf.classify("Patient was transferred to the ICU immediately.")
        assert "Life-threatening" in result["seriousness_criteria"]


class TestFallbackHospitalization:

    def test_hospitalized_keyword(self, clf):
        result = clf.classify("Patient was hospitalized for 3 days.")
        assert "Hospitalization" in result["seriousness_criteria"]

    def test_admitted_keyword(self, clf):
        result = clf.classify("Patient was admitted to hospital.")
        assert "Hospitalization" in result["seriousness_criteria"]

    def test_emergency_room_keyword(self, clf):
        result = clf.classify("Patient visited the emergency room due to the reaction.")
        assert "Hospitalization" in result["seriousness_criteria"]


class TestFallbackDisability:

    def test_disability_keyword(self, clf):
        result = clf.classify("The patient suffered permanent disability.")
        assert "Disability" in result["seriousness_criteria"]

    def test_permanent_damage_keyword(self, clf):
        result = clf.classify("Irreversible damage to the kidneys was reported.")
        assert "Disability" in result["seriousness_criteria"]

    def test_paralysis_keyword(self, clf):
        result = clf.classify("Patient developed lower limb paralysis.")
        assert "Disability" in result["seriousness_criteria"]


class TestFallbackCongenital:

    def test_congenital_keyword(self, clf):
        result = clf.classify("Congenital heart defect was observed in the neonate.")
        assert "Congenital Anomaly" in result["seriousness_criteria"]

    def test_birth_defect_keyword(self, clf):
        result = clf.classify("A birth defect was reported following in-utero exposure.")
        assert "Congenital Anomaly" in result["seriousness_criteria"]


class TestFallbackNonSerious:

    def test_mild_rash_is_non_serious(self, clf):
        result = clf.classify("Patient developed a mild skin rash that resolved on its own.")
        assert result["seriousness"] == "Non-serious"
        assert result["seriousness_criteria"] == []

    def test_headache_is_non_serious(self, clf):
        result = clf.classify("Patient reported mild headache after taking the medication.")
        assert result["seriousness"] == "Non-serious"

    def test_nausea_is_non_serious(self, clf):
        result = clf.classify("Patient experienced nausea and vomiting for 2 days.")
        assert result["seriousness"] == "Non-serious"


class TestFallbackConfidence:

    def test_serious_confidence_above_threshold(self, clf):
        result = clf.classify("Patient died following administration.")
        assert result["confidence"] >= 0.7

    def test_non_serious_confidence_above_threshold(self, clf):
        result = clf.classify("Mild rash resolved spontaneously.")
        assert result["confidence"] >= 0.7

    def test_explanation_is_string(self, clf):
        result = clf.classify("Patient was hospitalized for 5 days.")
        assert isinstance(result["explanation"], str) and len(result["explanation"]) > 0


# ===========================================================================
# Negation tests — the core bug fix
# ===========================================================================

class TestFallbackNegation:
    """
    Verify that negative phrasing suppresses keyword matches.

    These tests represent the bug that was fixed: "Patient was not hospitalized"
    was previously triggering Hospitalization because "hospitali" is a substring.
    """

    def test_negated_hospitalization_not_triggered(self, clf):
        result = clf.classify("Patient was not hospitalized.")
        assert "Hospitalization" not in result["seriousness_criteria"], (
            "'not hospitalized' must NOT trigger Hospitalization"
        )

    def test_negated_hospitalization_full_sentence(self, clf):
        result = clf.classify(
            "No hospitalization was required. Patient was treated as outpatient."
        )
        assert "Hospitalization" not in result["seriousness_criteria"]

    def test_negated_life_threatening(self, clf):
        result = clf.classify(
            "No evidence of life-threatening condition was observed during examination."
        )
        assert "Life-threatening" not in result["seriousness_criteria"], (
            "'no evidence of life-threatening' must NOT trigger Life-threatening"
        )

    def test_negated_icu(self, clf):
        result = clf.classify("Patient did not require ICU admission.")
        assert "Life-threatening" not in result["seriousness_criteria"]

    def test_negated_disability(self, clf):
        result = clf.classify("Patient recovered fully without permanent damage.")
        assert "Disability" not in result["seriousness_criteria"], (
            "'without permanent damage' must NOT trigger Disability"
        )

    def test_negated_admitted(self, clf):
        result = clf.classify("Patient was never admitted to hospital.")
        assert "Hospitalization" not in result["seriousness_criteria"]

    def test_positive_after_negation_context_still_triggers(self, clf):
        """A positive occurrence after an unrelated negation should still match."""
        result = clf.classify(
            "No fever was reported. However, the patient was hospitalized for 3 days."
        )
        assert "Hospitalization" in result["seriousness_criteria"]


# ===========================================================================
# ResponseParser tests
# ===========================================================================

class TestResponseParser:

    def test_valid_serious_output(self):
        raw = {
            "seriousness": "Serious",
            "seriousness_criteria": ["Hospitalization", "Death"],
            "confidence": 0.92,
            "explanation": "Patient was hospitalized and later died.",
        }
        s, criteria, conf, exp = ResponseParser.parse_seriousness(raw)
        assert s == "Serious"
        assert "Hospitalization" in criteria
        assert "Death" in criteria
        assert conf == 0.92
        assert "hospitalized" in exp.lower()

    def test_invalid_seriousness_defaults_to_non_serious(self):
        raw = {"seriousness": "Unknown"}
        s, criteria, conf, exp = ResponseParser.parse_seriousness(raw)
        assert s == "Non-serious"

    def test_invalid_criteria_are_filtered(self):
        raw = {
            "seriousness": "Serious",
            "seriousness_criteria": ["Hospitalization", "Invalid Criterion"],
            "confidence": 0.8,
            "explanation": "Test",
        }
        _, criteria, _, _ = ResponseParser.parse_seriousness(raw)
        assert "Invalid Criterion" not in criteria
        assert "Hospitalization" in criteria

    def test_serious_with_no_criteria_gets_fallback(self):
        raw = {"seriousness": "Serious", "seriousness_criteria": []}
        _, criteria, _, _ = ResponseParser.parse_seriousness(raw)
        assert "Other Medically Important Condition" in criteria

    def test_confidence_is_clamped(self):
        raw = {"seriousness": "Non-serious", "confidence": 1.5}
        _, _, conf, _ = ResponseParser.parse_seriousness(raw)
        assert conf == 1.0

        raw2 = {"seriousness": "Non-serious", "confidence": -0.5}
        _, _, conf2, _ = ResponseParser.parse_seriousness(raw2)
        assert conf2 == 0.0

    def test_missing_fields_use_defaults(self):
        s, criteria, conf, exp = ResponseParser.parse_seriousness({})
        assert s == "Non-serious"
        assert criteria == []
        assert conf == 0.75
        assert exp == ""
