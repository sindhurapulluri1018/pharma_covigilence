"""
logger.py
=========
Centralised structured logging for Zone 2 – Duplicate Detection.

Every stage of the pipeline logs through this module so that all log
entries share a consistent format and can be correlated by case_id.

Usage
-----
    from core.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Candidates retrieved", extra={"case_id": "TEMP001", "count": 12})
"""

import logging
import sys
from typing import Optional


# ---------------------------------------------------------------------------
# Log format
# ---------------------------------------------------------------------------
_LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _build_handler() -> logging.StreamHandler:
    """Build a stdout stream handler with the standard format."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))
    return handler


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Return a named logger configured with the Zone 2 standard format.

    Calling this with the same name always returns the same logger
    instance (standard Python behaviour), so it is safe to call at
    module level.

    Parameters
    ----------
    name : str
        Logger name – use __name__ to get the module name automatically.
    level : int
        Logging level (default: INFO).

    Returns
    -------
    logging.Logger
        Configured logger.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.addHandler(_build_handler())
        logger.setLevel(level)
        logger.propagate = False

    return logger


# ---------------------------------------------------------------------------
# Pipeline stage logger helpers
# ---------------------------------------------------------------------------

def log_pipeline_start(logger: logging.Logger, case_id: str) -> None:
    """Log the beginning of a duplicate-check pipeline run."""
    logger.info("=" * 60)
    logger.info("PIPELINE START | case_id=%s", case_id)


def log_candidates(logger: logging.Logger, case_id: str, count: int) -> None:
    """Log the number of candidates retrieved."""
    logger.info("CANDIDATE RETRIEVAL | case_id=%s | candidates=%d", case_id, count)


def log_similarity(
    logger: logging.Logger,
    case_id: str,
    matched_id: str,
    field_scores: dict,
    overall: float,
) -> None:
    """Log per-field and overall similarity scores."""
    logger.info(
        "SIMILARITY | case_id=%s | best_match=%s | overall=%.4f | fields=%s",
        case_id,
        matched_id,
        overall,
        field_scores,
    )


def log_decision(
    logger: logging.Logger,
    case_id: str,
    decision: str,
    confidence: str,
    next_action: str,
) -> None:
    """Log the final decision and routing action."""
    logger.info(
        "DECISION | case_id=%s | decision=%s | confidence=%s | action=%s",
        case_id,
        decision,
        confidence,
        next_action,
    )


def log_pipeline_end(logger: logging.Logger, case_id: str, elapsed_ms: float) -> None:
    """Log the completion of a pipeline run."""
    logger.info(
        "PIPELINE END | case_id=%s | elapsed_ms=%.1f",
        case_id,
        elapsed_ms,
    )
    logger.info("=" * 60)
