"""
metrics.py
==========
In-memory metrics collector for Zone 2 – Duplicate Detection.

Collects runtime statistics that Person 6 (Workflow Orchestrator) can
expose via a dashboard or monitoring endpoint.

Design
------
- In-memory only for now (resets on restart).
- Thread-safe using a simple lock.
- Structured as a singleton so all pipeline runs update the same counters.

Future extensibility
--------------------
Replace the in-memory dict with:
  - Prometheus counters / histograms
  - InfluxDB time-series
  - CloudWatch / Datadog metrics

Only this file changes.  The calling code is identical.
"""

import threading
import time
from dataclasses import dataclass, field
from typing import Dict

from core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class MetricsSnapshot:
    """Point-in-time snapshot of collected metrics."""

    total_requests: int = 0
    duplicate_count: int = 0
    possible_duplicate_count: int = 0
    unique_case_count: int = 0
    total_processing_time_ms: float = 0.0
    total_candidates_evaluated: int = 0
    total_similarity_sum: float = 0.0

    @property
    def duplicate_pct(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return round(self.duplicate_count / self.total_requests * 100, 1)

    @property
    def possible_pct(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return round(self.possible_duplicate_count / self.total_requests * 100, 1)

    @property
    def unique_pct(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return round(self.unique_case_count / self.total_requests * 100, 1)

    @property
    def avg_processing_time_ms(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return round(self.total_processing_time_ms / self.total_requests, 1)

    @property
    def avg_similarity(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return round(self.total_similarity_sum / self.total_requests, 4)

    @property
    def avg_candidates(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return round(self.total_candidates_evaluated / self.total_requests, 1)

    def to_dict(self) -> Dict:
        return {
            "total_requests": self.total_requests,
            "decisions": {
                "duplicate": {"count": self.duplicate_count, "pct": self.duplicate_pct},
                "possible_duplicate": {
                    "count": self.possible_duplicate_count,
                    "pct": self.possible_pct,
                },
                "unique": {"count": self.unique_case_count, "pct": self.unique_pct},
            },
            "performance": {
                "avg_processing_time_ms": self.avg_processing_time_ms,
                "avg_similarity_score": self.avg_similarity,
                "avg_candidates_evaluated": self.avg_candidates,
            },
        }


class MetricsCollector:
    """Thread-safe singleton metrics collector."""

    _instance: "MetricsCollector | None" = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls) -> "MetricsCollector":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._data = MetricsSnapshot()
        return cls._instance

    def record(
        self,
        decision: str,
        processing_time_ms: float,
        candidates_evaluated: int,
        overall_similarity: float,
    ) -> None:
        """
        Record metrics for one completed pipeline run.

        Parameters
        ----------
        decision : str
            One of 'Duplicate', 'Possible Duplicate', 'Unique Case'.
        processing_time_ms : float
            Total pipeline execution time in milliseconds.
        candidates_evaluated : int
            Number of candidates passed through the similarity engine.
        overall_similarity : float
            Final weighted similarity score.
        """
        with self._lock:
            d = self._data
            d.total_requests += 1
            d.total_processing_time_ms += processing_time_ms
            d.total_candidates_evaluated += candidates_evaluated
            d.total_similarity_sum += overall_similarity

            if decision == "Duplicate":
                d.duplicate_count += 1
            elif decision == "Possible Duplicate":
                d.possible_duplicate_count += 1
            else:
                d.unique_case_count += 1

        logger.debug(
            "Metrics recorded | decision=%s | time_ms=%.1f | candidates=%d",
            decision,
            processing_time_ms,
            candidates_evaluated,
        )

    def snapshot(self) -> Dict:
        """Return a point-in-time metrics snapshot as a dict."""
        with self._lock:
            return self._data.to_dict()

    def reset(self) -> None:
        """Reset all metrics (useful for testing)."""
        with self._lock:
            self._data = MetricsSnapshot()


# Module-level singleton
metrics_collector = MetricsCollector()
