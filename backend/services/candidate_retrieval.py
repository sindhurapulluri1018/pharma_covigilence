"""
candidate_retrieval.py
======================
Candidate Retrieval Engine for Zone 2 – Duplicate Detection.

Architecture
------------
This module implements the Strategy Pattern for candidate retrieval:

    ┌──────────────────────────────────┐
    │  AbstractCandidateRetriever      │  ← interface
    └──────────────────────────────────┘
              ▲              ▲
              │              │
    ┌─────────────┐  ┌───────────────────┐
    │JSONRetriever│  │FAISSRetriever      │ (future)
    └─────────────┘  └───────────────────┘

The DuplicateService depends ONLY on AbstractCandidateRetriever.
Switching to FAISS or Elasticsearch requires creating a new class only.

Filtering logic (JSONRetriever)
--------------------------------
Stage 1 – Drug filter     (exact match then fuzzy, threshold configurable)
Stage 2 – Reaction filter (keyword overlap, reduces irrelevant same-drug cases)
Stage 3 – Age window      (±N years, configurable)
Stage 4 – Date window     (±N days, configurable)
Stage 5 – Fallback        (if < MIN_CANDIDATES, relaxes to reaction-only)

Result   – up to MAX_CANDIDATES cases, sorted by drug+reaction relevance.
"""

from abc import ABC, abstractmethod

from rapidfuzz import fuzz

import config
from core.logger import get_logger
from models.context import DuplicateContext
from repositories.case_repository import AbstractCaseRepository
from utils.text_utils import (
    clean_text,
    keyword_overlap_score,
    normalize_drug_name,
)
from utils.date_utils import is_within_window, parse_date

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Abstract strategy interface
# ---------------------------------------------------------------------------

class AbstractCandidateRetriever(ABC):
    """
    Strategy interface for candidate retrieval.

    All retrievers must implement retrieve(), which populates
    ctx.candidates from the incoming case data.
    """

    @abstractmethod
    def retrieve(self, ctx: DuplicateContext) -> list[dict]:
        """
        Retrieve candidate cases for comparison.

        Parameters
        ----------
        ctx : DuplicateContext
            Pipeline context (reads ctx.incoming_case).

        Returns
        -------
        list[dict]
            Candidate cases to pass to the Similarity Engine.
        """
        ...


# ---------------------------------------------------------------------------
# JSON strategy implementation
# ---------------------------------------------------------------------------

class JSONCandidateRetriever(AbstractCandidateRetriever):
    """
    Retrieves candidates by filtering the in-memory JSON case list.

    The repository provides the data; this class applies domain logic.

    Parameters
    ----------
    repository : AbstractCaseRepository
        Injected data access object.
    """

    def __init__(self, repository: AbstractCaseRepository) -> None:
        self._repo = repository

    # ── Helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _drug_matches(incoming_drug: str, existing_drug: str) -> bool:
        """Return True if drugs are sufficiently similar."""
        norm_in = normalize_drug_name(incoming_drug)
        norm_ex = normalize_drug_name(existing_drug)
        if norm_in == norm_ex:
            return True
        score = fuzz.token_sort_ratio(norm_in, norm_ex)
        return score >= config.CANDIDATE_DRUG_FUZZY_THRESHOLD

    @staticmethod
    def _reaction_overlaps(incoming_reaction: str, existing_reaction: str) -> bool:
        """Return True if reaction keyword overlap is meaningful (>20%)."""
        overlap = keyword_overlap_score(incoming_reaction, existing_reaction)
        return overlap > 0.20

    @staticmethod
    def _age_in_window(incoming_age: int, existing_age: int | None) -> bool:
        """Return True if ages are within the configured window."""
        if existing_age is None:
            return True  # missing age → don't filter out
        return abs(incoming_age - existing_age) <= config.CANDIDATE_AGE_WINDOW

    @staticmethod
    def _date_in_window(incoming_date: str, existing_date: str | None) -> bool:
        """Return True if event dates are within the configured window."""
        if not existing_date:
            return True  # missing date → don't filter out
        try:
            return is_within_window(
                incoming_date, existing_date, config.CANDIDATE_DATE_WINDOW_DAYS
            )
        except ValueError:
            return True  # unparseable date → don't filter out

    # ── Main retrieval ─────────────────────────────────────────────────

    def retrieve(self, ctx: DuplicateContext) -> list[dict]:
        """
        Apply multi-stage filtering to return candidate cases.

        Filtering order
        ---------------
        1. Drug match     (most discriminating filter)
        2. Reaction keywords (eliminates irrelevant same-drug cases)
        3. Age window
        4. Date window
        5. Fallback to reaction-only if fewer than MIN_CANDIDATES remain

        Parameters
        ----------
        ctx : DuplicateContext

        Returns
        -------
        list[dict]
            Up to MAX_CANDIDATES candidate cases.
        """
        case = ctx.incoming_case
        all_cases = self._repo.get_all_cases()

        logger.info(
            "Candidate retrieval start | case_id=%s | pool_size=%d",
            case.case_id,
            len(all_cases),
        )

        # Stage 1: Drug match
        drug_matched = [
            c for c in all_cases if self._drug_matches(case.drug, c.get("drug", ""))
        ]
        logger.debug("After drug filter: %d cases", len(drug_matched))

        # Stage 2: Reaction keyword overlap
        reaction_filtered = [
            c
            for c in drug_matched
            if self._reaction_overlaps(case.reaction, c.get("reaction", ""))
        ]
        logger.debug("After reaction filter: %d cases", len(reaction_filtered))

        # Stage 3: Age window
        age_filtered = [
            c
            for c in reaction_filtered
            if self._age_in_window(case.age, c.get("age"))
        ]
        logger.debug("After age filter: %d cases", len(age_filtered))

        # Stage 4: Date window
        date_filtered = [
            c
            for c in age_filtered
            if self._date_in_window(case.event_date, c.get("event_date"))
        ]
        logger.debug("After date filter: %d cases", len(date_filtered))

        candidates = date_filtered

        # Stage 5: Fallback – if too few candidates, loosen to reaction-only
        if len(candidates) < config.MIN_CANDIDATES_BEFORE_FALLBACK:
            logger.info(
                "Fallback triggered: only %d candidates after full filtering; "
                "relaxing to reaction-keyword-only",
                len(candidates),
            )
            reaction_only = [
                c
                for c in all_cases
                if self._reaction_overlaps(case.reaction, c.get("reaction", ""))
                and c not in candidates
            ]
            candidates = candidates + reaction_only

        # Cap and return
        candidates = candidates[: config.MAX_CANDIDATES]

        logger.info(
            "Candidate retrieval complete | case_id=%s | candidates=%d",
            case.case_id,
            len(candidates),
        )
        return candidates


# ---------------------------------------------------------------------------
# Future strategy stubs
# ---------------------------------------------------------------------------

# class FAISSCandidateRetriever(AbstractCandidateRetriever):
#     """
#     Future: retrieves candidates via FAISS approximate nearest-neighbour
#     search on pre-computed embeddings of existing cases.
#
#     Steps:
#     1. Encode incoming case using ModelManager.
#     2. Query FAISS index for top-K nearest neighbours.
#     3. Return matching cases from the repository by ID.
#     """
#     def retrieve(self, ctx: DuplicateContext) -> list[dict]: ...

# class ElasticSearchCandidateRetriever(AbstractCandidateRetriever):
#     """Future: retrieves candidates via Elasticsearch BM25 + KNN."""
#     def retrieve(self, ctx: DuplicateContext) -> list[dict]: ...
