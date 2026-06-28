"""
priority_router.py
==================
Deterministic priority routing based on ICH E2B(R3) seriousness criteria.

No LLM involved — pure rule-based logic for auditability and reliability.

Routing Rules
-------------
    Death / Life-threatening          → Critical Queue  (priority: Critical)
    Hospitalization / Disability /
    Congenital Anomaly                → Expedited Queue (priority: High)
    Non-serious / Other               → Standard Queue  (priority: Standard)
"""

import config
from core.logger import get_logger
from models.context import TriageContext

logger = get_logger(__name__)


class PriorityRouter:
    """
    Stage 5 of the triage pipeline.

    Applies deterministic routing rules based on seriousness criteria.

    Writes to ctx:
        priority, queue, expedited_required, next_zone
    """

    def route(self, ctx: TriageContext) -> None:
        tier = self._determine_tier(ctx.seriousness, ctx.seriousness_criteria)
        rule = config.PRIORITY_MAP[tier]

        ctx.priority = rule["priority"]
        ctx.queue = rule["queue"]
        ctx.expedited_required = rule["expedited_required"]
        ctx.next_zone = config.NEXT_ZONE

        logger.info(
            "Priority | tier=%s | priority=%s | queue=%s | expedited=%s",
            tier, ctx.priority, ctx.queue, ctx.expedited_required,
        )

    @staticmethod
    def _determine_tier(seriousness: str, criteria: list[str]) -> str:
        """Return 'Critical', 'Expedited', or 'Standard' based on ICH rules."""
        if seriousness == "Non-serious":
            return "Standard"

        # Check critical criteria first (highest severity)
        for c in criteria:
            if c in config.CRITICAL_CRITERIA:
                return "Critical"

        # Check expedited criteria
        for c in criteria:
            if c in config.EXPEDITED_CRITERIA:
                return "Expedited"

        # Serious but no specific criteria (Other Medically Important Condition)
        return "Expedited"
