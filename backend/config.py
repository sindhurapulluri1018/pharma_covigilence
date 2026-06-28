"""
config.py
=========
Centralised configuration for Zone 2 – Duplicate Detection Service.

All weights, thresholds, and tuning parameters live here so that
downstream services never contain magic numbers.  Override any value
via environment variables (pattern: PV_<KEY>) for production deployments.

Future extensibility
--------------------
- Replace JSON paths with PostgreSQL / MongoDB connection strings here.
- Swap model name for a fine-tuned BioBERT or MedBERT variant here.
- FAISS index path can be added here when vector search is introduced.
"""

import os

# ---------------------------------------------------------------------------
# Sentence Transformer model
# ---------------------------------------------------------------------------
# Switch to a domain-specific bio-medical model (e.g. "dmis-lab/biobert-base-cased-v1.2")
# by changing this single value.
EMBEDDING_MODEL: str = os.getenv("PV_EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# ---------------------------------------------------------------------------
# Data paths  (relative to backend/)
# ---------------------------------------------------------------------------
EXISTING_CASES_PATH: str = os.getenv(
    "PV_EXISTING_CASES_PATH", "data/existing_cases.json"
)
INCOMING_CASES_PATH: str = os.getenv(
    "PV_INCOMING_CASES_PATH", "data/incoming_cases.json"
)

# ---------------------------------------------------------------------------
# Candidate Retrieval filters
# ---------------------------------------------------------------------------
# Age window: ±N years around the incoming case's age
CANDIDATE_AGE_WINDOW: int = int(os.getenv("PV_CANDIDATE_AGE_WINDOW", "15"))

# Date window: ±N days around the incoming case's event date
CANDIDATE_DATE_WINDOW_DAYS: int = int(
    os.getenv("PV_CANDIDATE_DATE_WINDOW_DAYS", "180")
)

# Fuzzy drug match threshold (0-100, RapidFuzz score)
CANDIDATE_DRUG_FUZZY_THRESHOLD: int = int(
    os.getenv("PV_CANDIDATE_DRUG_FUZZY_THRESHOLD", "70")
)

# Maximum number of candidates to pass to the similarity engine
MAX_CANDIDATES: int = int(os.getenv("PV_MAX_CANDIDATES", "20"))

# Minimum candidates before reaction-keyword fallback is triggered
MIN_CANDIDATES_BEFORE_FALLBACK: int = int(
    os.getenv("PV_MIN_CANDIDATES_BEFORE_FALLBACK", "3")
)

# ---------------------------------------------------------------------------
# Similarity Engine tuning
# ---------------------------------------------------------------------------
# Half-life in days for the event-date proximity score
DATE_HALF_LIFE_DAYS: float = float(os.getenv("PV_DATE_HALF_LIFE_DAYS", "30.0"))

# Sigma for the age Gaussian decay (years)
AGE_SIGMA: float = float(os.getenv("PV_AGE_SIGMA", "20.0"))

# RapidFuzz minimum score for a name to be considered a match (0-100)
NAME_FUZZY_THRESHOLD: int = int(os.getenv("PV_NAME_FUZZY_THRESHOLD", "0"))

# ---------------------------------------------------------------------------
# Weighted Scoring Engine – field weights (must sum to 1.0)
# ---------------------------------------------------------------------------
FIELD_WEIGHTS: dict[str, float] = {
    "drug":      float(os.getenv("PV_WEIGHT_DRUG",      "0.25")),
    "reaction":  float(os.getenv("PV_WEIGHT_REACTION",  "0.25")),
    "narrative": float(os.getenv("PV_WEIGHT_NARRATIVE", "0.20")),
    "patient":   float(os.getenv("PV_WEIGHT_PATIENT",   "0.15")),
    "date":      float(os.getenv("PV_WEIGHT_DATE",      "0.10")),
    "age":       float(os.getenv("PV_WEIGHT_AGE",       "0.03")),
    "gender":    float(os.getenv("PV_WEIGHT_GENDER",    "0.02")),
}

# ---------------------------------------------------------------------------
# Decision Engine – similarity thresholds
# ---------------------------------------------------------------------------
THRESHOLD_DUPLICATE: float = float(
    os.getenv("PV_THRESHOLD_DUPLICATE", "0.90")
)
THRESHOLD_POSSIBLE: float = float(
    os.getenv("PV_THRESHOLD_POSSIBLE", "0.70")
)

# ---------------------------------------------------------------------------
# API settings
# ---------------------------------------------------------------------------
API_TITLE: str = "PV Zone 2 – Duplicate Detection API"
API_VERSION: str = "1.0.0"
API_DESCRIPTION: str = (
    "VigiMatch-inspired duplicate detection for Individual Case Safety Reports (ICSRs). "
    "Implements Candidate Retrieval → Similarity Engine → Weighted Scoring → "
    "Decision Engine → Hard Gate pipeline."
)

# CORS origins – add production frontend URL here
CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]
