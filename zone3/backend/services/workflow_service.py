"""
workflow_service.py
===================
Manages workflow state transitions for Zone 3.

States
------
    READY_FOR_TRIAGE       → Input state (from Zone 2)
    TRIAGE_COMPLETE        → Intermediate (all stages passed)
    READY_FOR_EXTRACTION   → Output state (to Zone 4)
    TRIAGE_FAILED          → Error state (LLM failure or unhandled exception)
"""

import config
from core.logger import get_logger
from models.context import TriageContext

logger = get_logger(__name__)


class WorkflowService:
    """
    Stage 6 of the triage pipeline.

    Validates the incoming workflow state and sets the final outgoing state.
    """

    def transition(self, ctx: TriageContext, success: bool = True) -> None:
        """
        Apply workflow state transition.

        Parameters
        ----------
        ctx     : TriageContext
        success : bool — True if pipeline completed successfully, False if error
        """
        incoming = ctx.incoming_case.workflow_state if ctx.incoming_case else "UNKNOWN"

        if not success:
            ctx.workflow_state = config.WF_TRIAGE_FAILED
            logger.warning(
                "WorkflowTransition | %s → %s | case=%s",
                incoming, ctx.workflow_state,
                ctx.incoming_case.case_id if ctx.incoming_case else "?",
            )
            return

        ctx.workflow_state = config.WF_READY_FOR_EXTRACTION
        logger.info(
            "WorkflowTransition | %s → %s → %s | case=%s",
            incoming,
            config.WF_TRIAGE_COMPLETE,
            ctx.workflow_state,
            ctx.incoming_case.case_id,
        )
