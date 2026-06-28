"""
app.py
======
FastAPI entry point for Zone 3 Triage Service.

Run with:
    uvicorn app:app --reload --host 0.0.0.0 --port 8001

API docs: http://localhost:8001/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import config
from core.logger import get_logger
from routers.triage_router import router as triage_router

logger = get_logger("app")

app = FastAPI(
    title="Zone 3 – Triage Service",
    description=(
        "AI-powered ICSR triage using ICH E2B(R3) criteria. "
        "Classifies seriousness, expectedness, and priority for each adverse event report."
    ),
    version=config.PIPELINE_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS – allow Zone 3 frontend (port 5174) and Zone 2 frontend (port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(triage_router)


@app.get("/", include_in_schema=False)
def root():
    return {
        "service": "Zone 3 – Triage Service",
        "version": config.PIPELINE_VERSION,
        "mode": "FALLBACK" if config.FALLBACK_MODE else f"OpenAI ({config.LLM_MODEL})",
        "docs": "/docs",
    }


@app.on_event("startup")
def startup_event():
    mode = "FALLBACK (keyword classifier)" if config.FALLBACK_MODE else f"OpenAI ({config.LLM_MODEL})"
    logger.info("═══ Zone 3 Triage Service starting up | mode=%s ═══", mode)
    if config.FALLBACK_MODE:
        logger.warning("⚠  No OPENAI_API_KEY detected. Running in FALLBACK mode.")
        logger.warning("   Set OPENAI_API_KEY in zone3/backend/.env to enable real LLM calls.")
