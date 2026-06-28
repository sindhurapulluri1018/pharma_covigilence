"""
scoring_engine.py
=================
Weighted Scoring Engine for Zone 2 – Duplicate Detection.

Combines individual field similarity scores into a single overall
similarity value using configurable weights from config.py.

Design
------
Weights are read from config.py (not hardcoded here).
Changing the weight of any field requires only a config.py edit
or an environment variable override – no code change needed.

Weights sum to 1.0 (validated at startup).
"""

import config
from core.logger import get_logger

logger = get_logger(__name__)


class ScoringEngine:
    """
    Computes the overall weighted similarity score from field scores.

    Parameters
    ----------
    weights : dict[str, float] or None
        Field weights.  If None, reads from config.FIELD_WEIGHTS.
        Passing weights directly is useful for unit testing.
    """

    def __init__(self, weights: dict[str, float] | None = None) -> None:
        self._weights = weights if weights is not None else config.FIELD_WEIGHTS
        self._validate_weights()

    def _validate_weights(self) -> None:
        """Warn if weights do not sum to 1.0 (tolerance: ±0.001)."""
        total = sum(self._weights.values())
        if abs(total - 1.0) > 0.001:
            logger.warning(
                "Field weights sum to %.4f instead of 1.0. "
                "Scores will be normalised automatically.",
                total,
            )

    def compute_overall(self, field_scores: dict[str, float]) -> float:
        """
        Compute the weighted overall similarity score.

        Missing fields default to 0.0.  If weights do not sum to 1.0,
        the result is normalised to maintain a 0–1 range.

        Parameters
        ----------
        field_scores : dict[str, float]
            Per-field similarity scores from the Similarity Engine.

        Returns
        -------
        float
            Overall similarity score in [0.0, 1.0].
        """
        total_weight = sum(self._weights.values())
        if total_weight == 0:
            return 0.0

        weighted_sum = sum(
            self._weights.get(field, 0.0) * score
            for field, score in field_scores.items()
        )

        overall = weighted_sum / total_weight

        logger.debug(
            "Scoring | weighted_sum=%.4f | total_weight=%.4f | overall=%.4f",
            weighted_sum,
            total_weight,
            overall,
        )

        return round(max(0.0, min(1.0, overall)), 4)

    @property
    def weights(self) -> dict[str, float]:
        """Read-only view of the current weights."""
        return dict(self._weights)
