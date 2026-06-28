"""
test_scoring_engine.py
======================
Unit tests for the Weighted Scoring Engine.

These tests do NOT require the SentenceTransformer model or any data files.
They test pure numeric logic only.
"""

import pytest
from services.scoring_engine import ScoringEngine


class TestScoringEngine:
    """Tests for ScoringEngine.compute_overall()."""

    def test_perfect_scores_return_one(self):
        """All fields at 1.0 should give overall 1.0."""
        engine = ScoringEngine()
        scores = {
            "drug": 1.0, "reaction": 1.0, "narrative": 1.0,
            "patient": 1.0, "date": 1.0, "age": 1.0, "gender": 1.0,
        }
        result = engine.compute_overall(scores)
        assert result == pytest.approx(1.0, abs=0.001)

    def test_zero_scores_return_zero(self):
        """All fields at 0.0 should give overall 0.0."""
        engine = ScoringEngine()
        scores = {
            "drug": 0.0, "reaction": 0.0, "narrative": 0.0,
            "patient": 0.0, "date": 0.0, "age": 0.0, "gender": 0.0,
        }
        result = engine.compute_overall(scores)
        assert result == pytest.approx(0.0, abs=0.001)

    def test_custom_weights(self):
        """Custom weights should override defaults."""
        weights = {"drug": 1.0, "reaction": 0.0}
        engine = ScoringEngine(weights=weights)
        scores = {"drug": 0.8, "reaction": 0.5}
        result = engine.compute_overall(scores)
        # Only drug contributes: 0.8 * 1.0 / 1.0 = 0.8
        assert result == pytest.approx(0.8, abs=0.001)

    def test_missing_field_defaults_to_zero(self):
        """A field in weights but missing from scores should count as 0."""
        weights = {"drug": 0.5, "reaction": 0.5}
        engine = ScoringEngine(weights=weights)
        scores = {"drug": 1.0}  # reaction is missing
        result = engine.compute_overall(scores)
        # (1.0 * 0.5 + 0.0 * 0.5) / 1.0 = 0.5
        assert result == pytest.approx(0.5, abs=0.001)

    def test_result_clamped_to_zero_one(self):
        """Result should never exceed [0, 1] even with unusual weights."""
        weights = {"drug": 2.0}  # weight > 1 (unusual but valid)
        engine = ScoringEngine(weights=weights)
        scores = {"drug": 1.0}
        result = engine.compute_overall(scores)
        assert 0.0 <= result <= 1.0

    def test_weights_property(self):
        """Weights property should return current configuration."""
        custom = {"drug": 0.6, "reaction": 0.4}
        engine = ScoringEngine(weights=custom)
        assert engine.weights == custom
