"""
app.py
======
FastAPI application entry point for Zone 2 – Duplicate Detection.

Startup sequence
----------------
1. Load configuration
2. Load SentenceTransformer model via ModelManager (singleton)
3. Load existing cases via JSONCaseRepository (singleton)
4. Build JSONCandidateRetriever with the repository
5. Build DuplicateService with all dependencies injected
6. Register router

This file is the composition root – all dependency wiring happens here.
Services are never instantiated elsewhere (they receive dependencies
through their constructors).

Running
-------
    uvicorn app:app --reload --host 0.0.0.0 --port 8000
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import config
from core.logger import get_logger
from core.model_manager import model_manager
from repositories.case_repository import JSONCaseRepository
from routers.duplicate_router import router as duplicate_router, set_duplicate_service
from services.candidate_retrieval import JSONCandidateRetriever
from services.duplicate_service import DuplicateService

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Application lifespan (startup / shutdown)
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle:
    - Startup: load model and data, wire dependencies.
    - Shutdown: log clean exit.
    """
    logger.info("=" * 60)
    logger.info("Zone 2 – Duplicate Detection Service starting up")
    logger.info("=" * 60)

    # ── Step 1: Load embedding model ──────────────────────────────────
    logger.info("Loading embedding model: %s", config.EMBEDDING_MODEL)
    model_manager.load(config.EMBEDDING_MODEL)

    # ── Step 2: Load case database ────────────────────────────────────
    cases_path = os.path.join(os.path.dirname(__file__), config.EXISTING_CASES_PATH)
    repository = JSONCaseRepository(cases_path)
    logger.info("Case database loaded: %d cases", repository.count())

    # ── Step 3: Wire services ─────────────────────────────────────────
    retriever = JSONCandidateRetriever(repository)
    service = DuplicateService(
        repository=repository,
        retriever=retriever,
        model_manager=model_manager,
    )
    set_duplicate_service(service)

    logger.info("All services initialised. Ready to accept requests.")
    logger.info("=" * 60)

    yield  # Application runs here

    logger.info("Zone 2 – Duplicate Detection Service shutting down.")


# ---------------------------------------------------------------------------
# FastAPI application instance
# ---------------------------------------------------------------------------

app = FastAPI(
    title=config.API_TITLE,
    version=config.API_VERSION,
    description=config.API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────
app.include_router(duplicate_router)


# ---------------------------------------------------------------------------
# Root endpoint
# ---------------------------------------------------------------------------

@app.get("/", tags=["Root"])
def root():
    """API root – confirm the service is running."""
    return {
        "service": config.API_TITLE,
        "version": config.API_VERSION,
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "check": "POST /duplicate/check",
            "health": "GET  /duplicate/health",
            "metrics": "GET  /duplicate/metrics",
        },
    }
