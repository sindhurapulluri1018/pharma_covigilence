"""
logger.py
=========
Structured logging for Zone 3 Triage Service.
"""

import logging
import sys

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def log_triage_start(logger: logging.Logger, case_id: str) -> None:
    logger.info("═══ ZONE 3 TRIAGE START | case_id=%s ═══", case_id)


def log_triage_end(logger: logging.Logger, case_id: str, elapsed_ms: float) -> None:
    logger.info("═══ ZONE 3 TRIAGE END   | case_id=%s | elapsed=%.1fms ═══", case_id, elapsed_ms)


def log_llm_call(logger: logging.Logger, model: str, fallback: bool) -> None:
    if fallback:
        logger.info("LLM │ mode=FALLBACK (keyword classifier)")
    else:
        logger.info("LLM │ mode=OPENAI | model=%s", model)


def log_decision(
    logger: logging.Logger,
    case_id: str,
    seriousness: str,
    priority: str,
    queue: str,
    workflow_state: str,
) -> None:
    logger.info(
        "DECISION │ case=%s │ seriousness=%s │ priority=%s │ queue=%s │ state=%s",
        case_id, seriousness, priority, queue, workflow_state,
    )
