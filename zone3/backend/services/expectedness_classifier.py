"""
expectedness_classifier.py
==========================
Determines whether a reported adverse reaction is Expected or Unexpected
by comparing it against the approved mock product label (mock_labels.json).

Design decision
---------------
Expectedness is ALWAYS determined by the label database — the LLM is never
consulted. This mirrors how real pharmacovigilance systems work: the SmPC,
USPI, or company safety label is the authoritative reference, not an AI model.

Future hooks:
    load_from_who_label(drug) → WHO Drug Label
    load_from_smpc(drug)      → SmPC Database
    load_from_uspi(drug)      → USPI Database
"""

import json
import os

from rapidfuzz import fuzz

from core.logger import get_logger
from models.context import TriageContext

logger = get_logger(__name__)

_LABELS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "mock_labels.json")
_FUZZY_THRESHOLD = 70  # Minimum fuzzy match score (0–100) to consider a reaction "expected"


def _load_labels() -> dict[str, list[str]]:
    try:
        with open(_LABELS_PATH, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning("mock_labels.json not found – all reactions will be Unexpected")
        return {}


_LABELS: dict[str, list[str]] = _load_labels()


class ExpectednessService:
    """
    Stage 4 of the triage pipeline.

    Compares the incoming reaction against the mock product label database
    using case-insensitive fuzzy matching. mock_labels.json is always the
    authoritative source — the LLM result is never used for this decision.

    Writes to ctx
    -------------
        expectedness        : "Expected" | "Unexpected"
        expectedness_source : "Mock Product Label"
    """

    def classify(self, ctx: TriageContext) -> None:
        drug = ctx.incoming_case.drug
        reaction = ctx.incoming_case.reaction

        # Always use the label database — deterministic, auditable, LLM-independent.
        ctx.expectedness = self._label_lookup(drug, reaction)
        ctx.expectedness_source = "Mock Product Label"

        logger.info(
            "Expectedness | source=MockLabel | drug=%s | reaction=%s | result=%s",
            drug, reaction, ctx.expectedness,
        )

    @staticmethod
    def _label_lookup(drug: str, reaction: str) -> str:
        """
        Check if the reaction is listed for the drug in the mock label.

        Tries exact match first, then case-insensitive fuzzy match.

        Parameters
        ----------
        drug     : str – suspect drug name (INN or brand)
        reaction : str – reported adverse reaction

        Returns
        -------
        "Expected" if the reaction is on the label, "Unexpected" otherwise.
        """
        # Normalise drug name for lookup (case-insensitive)
        normalised = drug.strip().lower()
        label_reactions = None
        for label_drug, reactions in _LABELS.items():
            if label_drug.lower() == normalised:
                label_reactions = reactions
                break

        if label_reactions is None:
            # Drug not in mock label DB — conservative: Unexpected
            return "Unexpected"

        # Fuzzy match reaction against all label reactions
        for label_reaction in label_reactions:
            score = fuzz.partial_ratio(reaction.lower(), label_reaction.lower())
            if score >= _FUZZY_THRESHOLD:
                return "Expected"

        return "Unexpected"

    # ── Future hooks ──────────────────────────────────────────────────────────

    @staticmethod
    def load_from_who_label(drug: str) -> list[str]:  # noqa: ARG004
        """Future: Load known reactions from WHO Drug Label database."""
        raise NotImplementedError("WHO Drug Label integration not yet implemented.")

    @staticmethod
    def load_from_smpc(drug: str) -> list[str]:  # noqa: ARG004
        """Future: Load known reactions from SmPC database."""
        raise NotImplementedError("SmPC integration not yet implemented.")

    @staticmethod
    def load_from_uspi(drug: str) -> list[str]:  # noqa: ARG004
        """Future: Load known reactions from USPI database."""
        raise NotImplementedError("USPI integration not yet implemented.")


# ---------------------------------------------------------------------------
# Backward-compatibility alias
# ---------------------------------------------------------------------------
# Remove this alias once all direct references to ExpectednessClassifier are gone.
ExpectednessClassifier = ExpectednessService
