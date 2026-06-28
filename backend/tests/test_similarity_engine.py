"""
test_similarity_engine.py
=========================
Unit tests for SimilarityEngine field-level similarity methods.

Strategy
--------
- Non-semantic fields (patient, drug, age, gender, date) are tested
  directly — they require NO model or data files.
- Semantic fields (reaction, narrative) that call SentenceTransformer
  are tested via a lightweight mock that returns controllable embeddings,
  ensuring tests stay fast and deterministic.
"""

import math
import types
import pytest
import numpy as np

from models.request_models import IncomingCase
from models.context import DuplicateContext, FieldExplanations
from services.similarity_engine import SimilarityEngine


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_model_manager(embedding_matrix=None):
    """
    Build a minimal mock ModelManager whose encode() returns controllable
    numpy embeddings without loading any model.

    Parameters
    ----------
    embedding_matrix : list[list[float]] | None
        Two-row matrix for [text_a, text_b].  Defaults to orthogonal
        vectors (cosine similarity = 0).
    """
    if embedding_matrix is None:
        embedding_matrix = [[1.0, 0.0], [0.0, 1.0]]

    mm = types.SimpleNamespace()
    mm.encode = lambda texts, **kw: np.array(embedding_matrix, dtype=float)
    return mm


def _make_engine(embedding_matrix=None):
    """Return a SimilarityEngine backed by a mock model manager."""
    return SimilarityEngine(_make_model_manager(embedding_matrix))


def _make_context(drug="Paracetamol", reaction="Skin Rash",
                  patient_name="John Doe", age=45, gender="Male",
                  event_date="2025-06-10",
                  report_text="Patient developed a severe skin rash."):
    case = IncomingCase(
        case_id="TEST001",
        patient_name=patient_name,
        age=age,
        gender=gender,
        drug=drug,
        reaction=reaction,
        event_date=event_date,
        report_text=report_text,
    )
    return DuplicateContext(incoming_case=case)


# ---------------------------------------------------------------------------
# Patient name similarity
# ---------------------------------------------------------------------------

class TestPatientSimilarity:

    def setup_method(self):
        self.engine = _make_engine()

    def test_identical_names(self):
        score, reason = self.engine._patient_similarity("John Doe", "John Doe")
        assert score == pytest.approx(1.0, abs=0.01)

    def test_transposed_names_high_score(self):
        """token_sort_ratio handles name order transposition."""
        score, _ = self.engine._patient_similarity("John Doe", "Doe John")
        assert score >= 0.9

    def test_completely_different_names_low_score(self):
        score, _ = self.engine._patient_similarity("John Doe", "Maria Garcia")
        assert score < 0.5

    def test_minor_misspelling_still_high(self):
        score, _ = self.engine._patient_similarity("Sarah Wilson", "Sara Willson")
        assert score >= 0.75

    def test_explanation_is_string(self):
        _, reason = self.engine._patient_similarity("Alice", "Alice")
        assert isinstance(reason, str) and len(reason) > 0

    def test_partial_name_moderate_score(self):
        """Partial name entry should score moderately, not zero."""
        score, _ = self.engine._patient_similarity("John Doe", "John")
        assert score >= 0.4


# ---------------------------------------------------------------------------
# Drug similarity
# ---------------------------------------------------------------------------

class TestDrugSimilarity:

    def setup_method(self):
        self.engine = _make_engine()

    def test_exact_match(self):
        score, reason = self.engine._drug_similarity("Metformin", "Metformin")
        assert score == pytest.approx(1.0)
        assert "Exact match" in reason

    def test_case_insensitive_exact_match(self):
        score, _ = self.engine._drug_similarity("METFORMIN", "metformin")
        assert score == pytest.approx(1.0)

    def test_fuzzy_near_match(self):
        """Brand name vs INN-like spelling — should still score well."""
        score, _ = self.engine._drug_similarity("Paracetamol", "Paracetamoll")
        assert score >= 0.8

    def test_completely_different_drugs(self):
        score, _ = self.engine._drug_similarity("Metformin", "Warfarin")
        assert score < 0.5

    def test_explanation_is_string(self):
        _, reason = self.engine._drug_similarity("Metformin", "Metformin")
        assert isinstance(reason, str)


# ---------------------------------------------------------------------------
# Age similarity
# ---------------------------------------------------------------------------

class TestAgeSimilarity:

    def setup_method(self):
        self.engine = _make_engine()

    def test_same_age_is_one(self):
        score, _ = self.engine._age_similarity(45, 45)
        assert score == pytest.approx(1.0)

    def test_small_difference_near_one(self):
        score, _ = self.engine._age_similarity(45, 47)
        assert score >= 0.98

    def test_large_difference_low_score(self):
        score, _ = self.engine._age_similarity(20, 80)
        assert score < 0.2

    def test_moderate_difference(self):
        score, _ = self.engine._age_similarity(40, 50)
        assert 0.6 <= score <= 0.95

    def test_score_clamped_non_negative(self):
        score, _ = self.engine._age_similarity(0, 120)
        assert score >= 0.0


# ---------------------------------------------------------------------------
# Gender similarity
# ---------------------------------------------------------------------------

class TestGenderSimilarity:

    def setup_method(self):
        self.engine = _make_engine()

    def test_same_gender(self):
        score, reason = self.engine._gender_similarity("Male", "Male")
        assert score == pytest.approx(1.0)
        assert "Exact match" in reason

    def test_different_gender(self):
        score, reason = self.engine._gender_similarity("Male", "Female")
        assert score == pytest.approx(0.0)
        assert "mismatch" in reason.lower()

    def test_case_insensitive(self):
        score, _ = self.engine._gender_similarity("male", "MALE")
        assert score == pytest.approx(1.0)

    def test_unknown_gender_mismatch(self):
        score, _ = self.engine._gender_similarity("Unknown", "Male")
        assert score == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Date similarity
# ---------------------------------------------------------------------------

class TestDateSimilarity:

    def setup_method(self):
        self.engine = _make_engine()

    def test_same_date_is_one(self):
        score, _ = self.engine._date_similarity("2025-01-01", "2025-01-01")
        assert score == pytest.approx(1.0, abs=0.001)

    def test_close_dates_high_score(self):
        score, _ = self.engine._date_similarity("2025-01-01", "2025-01-05")
        assert score >= 0.85

    def test_far_dates_low_score(self):
        score, _ = self.engine._date_similarity("2020-01-01", "2025-06-01")
        assert score < 0.1

    def test_one_year_apart_moderate(self):
        score, _ = self.engine._date_similarity("2025-01-01", "2026-01-01")
        assert score < 0.5

    def test_explanation_mentions_days(self):
        _, reason = self.engine._date_similarity("2025-01-01", "2025-01-10")
        assert "day" in reason.lower()


# ---------------------------------------------------------------------------
# Reaction similarity (semantic — uses mock embeddings)
# ---------------------------------------------------------------------------

class TestReactionSimilarity:

    def test_identical_embeddings_score_one(self):
        """Parallel vectors → cosine similarity = 1.0."""
        engine = _make_engine([[1.0, 0.0], [1.0, 0.0]])
        score, _ = engine._reaction_similarity("Lactic Acidosis", "Lactic Acidosis")
        assert score == pytest.approx(1.0, abs=0.01)

    def test_orthogonal_embeddings_score_zero(self):
        """Orthogonal vectors → cosine similarity = 0.0."""
        engine = _make_engine([[1.0, 0.0], [0.0, 1.0]])
        score, _ = engine._reaction_similarity("Skin Rash", "Liver Failure")
        assert score == pytest.approx(0.0, abs=0.01)

    def test_score_clamped_to_zero_one(self):
        """Even with unusual embeddings the score must be in [0, 1]."""
        engine = _make_engine([[1.0, 0.0], [1.0, 0.0]])
        score, _ = engine._reaction_similarity("A", "B")
        assert 0.0 <= score <= 1.0

    def test_explanation_is_string(self):
        engine = _make_engine([[1.0, 0.0], [1.0, 0.0]])
        _, reason = engine._reaction_similarity("Nausea", "Nausea")
        assert isinstance(reason, str) and len(reason) > 0

    def test_high_similarity_explanation(self):
        engine = _make_engine([[1.0, 0.0], [1.0, 0.0]])
        _, reason = engine._reaction_similarity("Nausea", "Nausea")
        assert "similar" in reason.lower() or "identical" in reason.lower()


# ---------------------------------------------------------------------------
# Narrative similarity (semantic — uses mock embeddings)
# ---------------------------------------------------------------------------

class TestNarrativeSimilarity:

    def test_identical_narrative_embeddings(self):
        engine = _make_engine([[0.6, 0.8], [0.6, 0.8]])
        score, _ = engine._narrative_similarity("text A", "text A")
        assert score == pytest.approx(1.0, abs=0.01)

    def test_different_narrative_embeddings(self):
        engine = _make_engine([[1.0, 0.0], [0.0, 1.0]])
        score, _ = engine._narrative_similarity("text A", "text B")
        assert score == pytest.approx(0.0, abs=0.01)

    def test_explanation_contains_similarity_value(self):
        engine = _make_engine([[1.0, 0.0], [1.0, 0.0]])
        _, reason = engine._narrative_similarity("text A", "text A")
        assert "1.00" in reason or "similar" in reason.lower()


# ---------------------------------------------------------------------------
# Full compute() integration (non-semantic fields only)
# ---------------------------------------------------------------------------

class TestComputeIntegration:
    """
    Tests compute() end-to-end with mocked semantic embeddings.
    Validates that all 7 keys are present and within range.
    """

    def test_all_fields_returned(self):
        engine = _make_engine([[1.0, 0.0], [1.0, 0.0]])
        ctx = _make_context()
        candidate = {
            "patient_name": "John Doe", "drug": "Paracetamol",
            "reaction": "Skin Rash", "report_text": "Narrative text.",
            "age": 45, "gender": "Male", "event_date": "2025-06-10",
        }
        scores, explanations = engine.compute(ctx, candidate)
        assert set(scores.keys()) == {"patient", "drug", "reaction", "narrative", "age", "gender", "date"}
        for v in scores.values():
            assert 0.0 <= v <= 1.0

    def test_explanations_are_strings(self):
        engine = _make_engine([[1.0, 0.0], [1.0, 0.0]])
        ctx = _make_context()
        candidate = {
            "patient_name": "Other Name", "drug": "Metformin",
            "reaction": "Rash", "report_text": "Different narrative.",
            "age": 60, "gender": "Female", "event_date": "2024-01-01",
        }
        _, explanations = engine.compute(ctx, candidate)
        for field in ("patient", "drug", "reaction", "narrative", "age", "gender", "date"):
            assert isinstance(getattr(explanations, field), str)

    def test_perfect_candidate_all_ones(self):
        """Identical case should give near-perfect scores on non-semantic fields."""
        engine = _make_engine([[1.0, 0.0], [1.0, 0.0]])  # semantic = 1.0
        ctx = _make_context()
        candidate = {
            "patient_name": "John Doe", "drug": "Paracetamol",
            "reaction": "Skin Rash", "report_text": "Patient developed a severe skin rash.",
            "age": 45, "gender": "Male", "event_date": "2025-06-10",
        }
        scores, _ = engine.compute(ctx, candidate)
        assert scores["patient"] == pytest.approx(1.0, abs=0.01)
        assert scores["drug"] == pytest.approx(1.0)
        assert scores["age"] == pytest.approx(1.0)
        assert scores["gender"] == pytest.approx(1.0)
        assert scores["date"] == pytest.approx(1.0, abs=0.01)

    def test_missing_candidate_fields_dont_crash(self):
        """Candidate with missing fields should not raise — engine uses defaults."""
        engine = _make_engine([[1.0, 0.0], [0.0, 1.0]])
        ctx = _make_context()
        candidate = {}  # completely empty
        scores, _ = engine.compute(ctx, candidate)
        assert len(scores) == 7
