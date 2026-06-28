"""
decision_engine.py
==================
Decision Engine + Hard Gate for Zone 2 – Duplicate Detection.

Decision Engine
---------------
Applies configurable thresholds to the overall similarity score and
returns a (decision, confidence) pair.

Confidence levels:
  > 0.95 → Very High
  0.90–0.94 → High
  0.80–0.89 → Medium
  0.70–0.79 → Low
  < 0.70    → N/A (Unique Case)

Hard Gate
---------
A pure routing function – NO AI logic here.
Maps (decision) → RoutingMetadata with:
  - next_zone       (machine-readable zone label)
  - route           (Proceed / Hold / Stop)
  - workflow_state  (for Person 6 Orchestrator)
  - next_action     (human-readable)

Person 6 integration:
The workflow_state field is the primary handoff point.
"""

import config
from core.logger import get_logger
from models.context import DuplicateContext, RoutingMetadata

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Confidence mapping
# ---------------------------------------------------------------------------

def _compute_confidence(similarity: float, decision: str) -> str:
    """
    Map a similarity score to a confidence label.

    Parameters
    ----------
    similarity : float
        Overall similarity score (0.0 – 1.0).
    decision : str
        The decision string (used to handle Unique Case separately).

    Returns
    -------
    str
        One of: 'Very High', 'High', 'Medium', 'Low', 'N/A'.
    """
    if decision == "Unique Case":
        return "N/A"
    if similarity >= 0.95:
        return "Very High"
    if similarity >= 0.90:
        return "High"
    if similarity >= 0.80:
        return "Medium"
    return "Low"


# ---------------------------------------------------------------------------
# Hard Gate routing table
# ---------------------------------------------------------------------------

_ROUTING_TABLE: dict[str, RoutingMetadata] = {
    "Duplicate": RoutingMetadata(
        next_zone="Closed",
        route="Stop",
        workflow_state="DUPLICATE_DETECTED",
        next_action="Stop Processing",
    ),
    "Possible Duplicate": RoutingMetadata(
        next_zone="ReviewQueue",
        route="Hold",
        workflow_state="PENDING_HUMAN_REVIEW",
        next_action="Reviewer Queue",
    ),
    "Unique Case": RoutingMetadata(
        next_zone="Zone3",
        route="Proceed",
        workflow_state="READY_FOR_TRIAGE",
        next_action="Proceed to Zone 3",
    ),
}


class DecisionEngine:
    """
    Applies similarity thresholds to produce a decision + confidence.

    Thresholds are read from config.py and can be overridden via
    environment variables for A/B testing or regulatory adjustments.
    """

    def __init__(
        self,
        threshold_duplicate: float | None = None,
        threshold_possible: float | None = None,
    ) -> None:
        self._thresh_dup = (
            threshold_duplicate
            if threshold_duplicate is not None
            else config.THRESHOLD_DUPLICATE
        )
        self._thresh_pos = (
            threshold_possible
            if threshold_possible is not None
            else config.THRESHOLD_POSSIBLE
        )

    def decide(self, ctx: DuplicateContext) -> tuple[str, str]:
        """
        Apply thresholds to ctx.overall_similarity and return
        (decision, confidence).

        Parameters
        ----------
        ctx : DuplicateContext
            Must have ctx.overall_similarity set by ScoringEngine.

        Returns
        -------
        tuple[str, str]
            (decision, confidence)
        """
        score = ctx.overall_similarity

        if score >= self._thresh_dup:
            decision = "Duplicate"
        elif score >= self._thresh_pos:
            decision = "Possible Duplicate"
        else:
            decision = "Unique Case"

        confidence = _compute_confidence(score, decision)

        logger.info(
            "Decision | case_id=%s | score=%.4f | decision=%s | confidence=%s",
            ctx.incoming_case.case_id,
            score,
            decision,
            confidence,
        )

        return decision, confidence


class HardGate:
    """
    Pure routing function – maps decisions to routing metadata.

    Contains NO AI logic.  Only a lookup into the routing table.
    This is intentional: the Hard Gate must be auditable and
    deterministic for regulatory compliance.
    """

    def route(self, ctx: DuplicateContext) -> RoutingMetadata:
        """
        Map ctx.decision to a RoutingMetadata object.

        Parameters
        ----------
        ctx : DuplicateContext
            Must have ctx.decision set by DecisionEngine.

        Returns
        -------
        RoutingMetadata
            Routing instructions for the Workflow Orchestrator.

        Raises
        ------
        KeyError
            If an unknown decision string is encountered (programming error).
        """
        routing = _ROUTING_TABLE.get(ctx.decision)

        if routing is None:
            logger.error(
                "HardGate received unknown decision: '%s'. Defaulting to ReviewQueue.",
                ctx.decision,
            )
            routing = _ROUTING_TABLE["Possible Duplicate"]

        logger.info(
            "Hard Gate | case_id=%s | decision=%s | workflow_state=%s | next_zone=%s",
            ctx.incoming_case.case_id,
            ctx.decision,
            routing.workflow_state,
            routing.next_zone,
        )

        return routing
