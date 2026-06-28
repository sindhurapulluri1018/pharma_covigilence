"""
similarity_engine.py
====================
Similarity Engine for Zone 2 – Duplicate Detection.

Computes per-field similarity scores AND human-readable explanations
for each field comparison.  The explanations make results auditable
by medical reviewers and useful for UI display.

Field computation methods
--------------------------
patient   → RapidFuzz token_sort_ratio (handles name transposition)
drug      → Exact match after normalisation, fuzzy fallback
reaction  → Sentence Transformer cosine similarity
narrative → Sentence Transformer cosine similarity
age       → Gaussian decay: exp(-((a-b)/sigma)^2)
gender    → Exact match
date      → Exponential decay: exp(-ln2 * days / half_life)

The Sentence Transformer model is NOT instantiated here.
It is injected via the ModelManager singleton to avoid reloading.
"""

import math

import numpy as np
from rapidfuzz import fuzz
from sklearn.metrics.pairwise import cosine_similarity

import config
from core.logger import get_logger
from core.model_manager import ModelManager
from models.context import DuplicateContext, FieldExplanations
from utils.text_utils import clean_text, normalize_drug_name
from utils.date_utils import date_proximity_score, days_between

logger = get_logger(__name__)


class SimilarityEngine:
    """
    Computes per-field similarity between the incoming case and one candidate.

    Parameters
    ----------
    model_manager : ModelManager
        Injected singleton model manager (holds the loaded SentenceTransformer).
    """

    def __init__(self, model_manager: ModelManager) -> None:
        self._model = model_manager

    # ── Individual field methods ────────────────────────────────────────────

    def _patient_similarity(
        self, name_a: str, name_b: str
    ) -> tuple[float, str]:
        """
        Compare patient names using RapidFuzz token_sort_ratio.

        token_sort_ratio handles:
        - Name transposition ("John Doe" vs "Doe John")
        - Minor misspellings
        - Partial name entry

        Returns (score 0-1, explanation string).
        """
        score_raw = fuzz.token_sort_ratio(
            clean_text(name_a), clean_text(name_b)
        )
        score = score_raw / 100.0

        if score >= 0.95:
            reason = f"Very high name match ({score_raw}/100) – likely same patient"
        elif score >= 0.80:
            reason = f"High name match ({score_raw}/100) – probable same patient"
        elif score >= 0.60:
            reason = f"Moderate name match ({score_raw}/100) – possible transcription variant"
        else:
            reason = f"Low name match ({score_raw}/100) – likely different patients"

        return score, reason

    def _drug_similarity(
        self, drug_a: str, drug_b: str
    ) -> tuple[float, str]:
        """
        Compare drug names.

        Steps:
        1. Exact match after WHO-INN normalisation (stub).
        2. If not exact, fuzzy ratio as a fallback.

        Returns (score 0-1, explanation string).
        """
        norm_a = normalize_drug_name(drug_a)
        norm_b = normalize_drug_name(drug_b)

        if norm_a == norm_b:
            return 1.0, f"Exact match after normalisation: '{norm_a}'"

        score_raw = fuzz.token_sort_ratio(norm_a, norm_b)
        score = score_raw / 100.0
        reason = (
            f"Fuzzy match {score_raw}/100 between '{norm_a}' and '{norm_b}'"
            " (WHO Drug Dictionary normalisation pending)"
        )
        return score, reason

    def _reaction_similarity(
        self, reaction_a: str, reaction_b: str
    ) -> tuple[float, str]:
        """
        Compare adverse reaction terms using Sentence Transformer embeddings.

        Cosine similarity on semantic embeddings handles synonyms better
        than string matching (e.g., "severe skin rash" ≈ "serious cutaneous eruption").

        Returns (score 0-1, explanation string).
        """
        embeddings = self._model.encode([reaction_a, reaction_b])
        score = float(
            cosine_similarity(embeddings[0:1], embeddings[1:2])[0][0]
        )
        score = max(0.0, min(1.0, score))  # clamp to [0, 1]

        if score >= 0.90:
            reason = f"Semantic similarity {score:.2f} – very similar reactions (MedDRA grouping recommended)"
        elif score >= 0.75:
            reason = f"Semantic similarity {score:.2f} – related reactions"
        else:
            reason = f"Semantic similarity {score:.2f} – different reaction profile"

        return score, reason

    def _narrative_similarity(
        self, text_a: str, text_b: str
    ) -> tuple[float, str]:
        """
        Compare free-text narratives using Sentence Transformer embeddings.

        Returns (score 0-1, explanation string).
        """
        embeddings = self._model.encode([text_a, text_b])
        score = float(
            cosine_similarity(embeddings[0:1], embeddings[1:2])[0][0]
        )
        score = max(0.0, min(1.0, score))

        reason = f"Narrative cosine similarity {score:.2f}"
        if score >= 0.90:
            reason += " – narratives are near-identical"
        elif score >= 0.75:
            reason += " – narratives describe similar events"
        else:
            reason += " – narratives differ substantially"

        return score, reason

    def _age_similarity(self, age_a: int, age_b: int) -> tuple[float, str]:
        """
        Compare ages using Gaussian decay.

        Score = exp(-((age_a - age_b) / sigma)^2)
        - Same age       → 1.00
        - ±5  years      → ~0.94
        - ±10 years      → ~0.78
        - ±20 years      → ~0.37

        Returns (score 0-1, explanation string).
        """
        diff = abs(age_a - age_b)
        score = math.exp(-((diff / config.AGE_SIGMA) ** 2))
        reason = f"Age difference {diff} years → score {score:.2f}"
        return score, reason

    def _gender_similarity(
        self, gender_a: str, gender_b: str
    ) -> tuple[float, str]:
        """
        Exact match comparison for gender (normalised to title-case).

        Returns (1.0, reason) or (0.0, reason).
        """
        a = gender_a.strip().title()
        b = gender_b.strip().title()
        if a == b:
            return 1.0, f"Exact match: {a}"
        return 0.0, f"Gender mismatch: {a} vs {b}"

    def _date_similarity(
        self, date_a: str, date_b: str
    ) -> tuple[float, str]:
        """
        Compare event dates using exponential decay proximity scoring.

        Returns (score 0-1, explanation string).
        """
        try:
            score = date_proximity_score(date_a, date_b, config.DATE_HALF_LIFE_DAYS)
            delta = days_between(date_a, date_b)
            reason = f"Events {delta} day(s) apart → score {score:.2f}"
        except ValueError as exc:
            logger.warning("Date comparison failed: %s", exc)
            score = 0.5
            reason = "Date comparison failed – using neutral score 0.5"

        return score, reason

    # ── Main comparison ─────────────────────────────────────────────────────

    def compute(
        self, ctx: DuplicateContext, candidate: dict
    ) -> tuple[dict[str, float], FieldExplanations]:
        """
        Compute similarity between the incoming case and one candidate.

        Parameters
        ----------
        ctx : DuplicateContext
            Contains the incoming case.
        candidate : dict
            A single case from the existing case database.

        Returns
        -------
        tuple[dict[str, float], FieldExplanations]
            (field_scores, field_explanations)
        """
        case = ctx.incoming_case

        patient_score, patient_reason = self._patient_similarity(
            case.patient_name, candidate.get("patient_name", "")
        )
        drug_score, drug_reason = self._drug_similarity(
            case.drug, candidate.get("drug", "")
        )
        reaction_score, reaction_reason = self._reaction_similarity(
            case.reaction, candidate.get("reaction", "")
        )
        narrative_score, narrative_reason = self._narrative_similarity(
            case.report_text, candidate.get("report_text", "")
        )
        age_score, age_reason = self._age_similarity(
            case.age, candidate.get("age", case.age)
        )
        gender_score, gender_reason = self._gender_similarity(
            case.gender, candidate.get("gender", "")
        )
        date_score, date_reason = self._date_similarity(
            case.event_date, candidate.get("event_date", "")
        )

        field_scores = {
            "patient":   patient_score,
            "drug":      drug_score,
            "reaction":  reaction_score,
            "narrative": narrative_score,
            "age":       age_score,
            "gender":    gender_score,
            "date":      date_score,
        }

        explanations = FieldExplanations(
            patient=patient_reason,
            drug=drug_reason,
            reaction=reaction_reason,
            narrative=narrative_reason,
            age=age_reason,
            gender=gender_reason,
            date=date_reason,
        )

        return field_scores, explanations

    def find_best_match(
        self, ctx: DuplicateContext
    ) -> tuple[dict | None, dict[str, float], FieldExplanations, list[dict]]:
        """
        Iterate over all candidates and return the best-matching one,
        plus a ranked list of top-3 candidates.

        Parameters
        ----------
        ctx : DuplicateContext
            Must have ctx.candidates populated by CandidateRetrieval.

        Returns
        -------
        tuple[dict | None, dict[str, float], FieldExplanations, list[dict]]
            (best_candidate, field_scores, field_explanations, top_candidates)
            top_candidates is a list of up to 3 dicts with keys:
            case_id, score, patient_name, drug, reaction.
            Returns (None, empty, empty, []) if no candidates.
        """
        if not ctx.candidates:
            logger.warning(
                "No candidates available for case_id=%s", ctx.incoming_case.case_id
            )
            return None, {}, FieldExplanations(), []

        best_candidate = None
        best_scores: dict[str, float] = {}
        best_explanations = FieldExplanations()
        best_overall = -1.0

        # Track all scored candidates for ranking
        all_scored: list[tuple[float, dict]] = []

        from services.scoring_engine import ScoringEngine
        scoring = ScoringEngine()

        for candidate in ctx.candidates:
            scores, explanations = self.compute(ctx, candidate)
            overall = scoring.compute_overall(scores)
            all_scored.append((overall, candidate))
            if overall > best_overall:
                best_overall = overall
                best_candidate = candidate
                best_scores = scores
                best_explanations = explanations

        # Build top-3 list sorted by score descending
        all_scored.sort(key=lambda x: x[0], reverse=True)
        top_candidates = [
            {
                "case_id": c.get("case_id", ""),
                "score": round(score, 4),
                "patient_name": c.get("patient_name", ""),
                "drug": c.get("drug", ""),
                "reaction": c.get("reaction", ""),
            }
            for score, c in all_scored[:3]
        ]

        logger.info(
            "Best match found | case_id=%s | matched=%s | overall=%.4f | top_candidates=%d",
            ctx.incoming_case.case_id,
            best_candidate.get("case_id") if best_candidate else "None",
            best_overall,
            len(top_candidates),
        )
        return best_candidate, best_scores, best_explanations, top_candidates
