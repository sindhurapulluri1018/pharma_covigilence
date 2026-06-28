"""
config.py
=========
All configuration for Zone 3 Triage Service.

Override any value via environment variables or a .env file in zone3/backend/.

Required:
    OPENAI_API_KEY=sk-...   (set this in .env or environment)
"""

import os
from dotenv import load_dotenv

# Load .env from the same directory as this file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# ── OpenAI / LLM ─────────────────────────────────────────────────────────────
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.1"))
LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "512"))
LLM_TOP_P: float = float(os.getenv("LLM_TOP_P", "1.0"))

# Fallback mode activates automatically when no API key is configured
FALLBACK_MODE: bool = not bool(OPENAI_API_KEY)

# ── Triage thresholds ─────────────────────────────────────────────────────────
CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.70"))

# ── Priority routing rules ────────────────────────────────────────────────────
CRITICAL_CRITERIA: list[str] = ["Death", "Life-threatening"]
EXPEDITED_CRITERIA: list[str] = ["Hospitalization", "Disability", "Congenital Anomaly"]
# Everything else → Standard

PRIORITY_MAP: dict = {
    "Critical":  {"priority": "Critical",  "queue": "Critical Queue",  "expedited_required": True},
    "Expedited": {"priority": "High",      "queue": "Expedited Queue", "expedited_required": True},
    "Standard":  {"priority": "Standard",  "queue": "Standard Queue",  "expedited_required": False},
}

# ── Workflow states ───────────────────────────────────────────────────────────
WF_READY_FOR_TRIAGE:     str = "READY_FOR_TRIAGE"
WF_TRIAGE_COMPLETE:      str = "TRIAGE_COMPLETE"
WF_READY_FOR_EXTRACTION: str = "READY_FOR_EXTRACTION"
WF_TRIAGE_FAILED:        str = "TRIAGE_FAILED"

# ── Service metadata ──────────────────────────────────────────────────────────
PIPELINE_VERSION: str = "1.0.0"
NEXT_ZONE: str = "Zone4"
SERVICE_NAME: str = "Zone3-Triage"
