"""metrics.py — In-memory metrics collector for Zone 3."""
import threading
import time
from collections import defaultdict


class MetricsCollector:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._total = 0
        self._decisions: dict[str, int] = defaultdict(int)
        self._queues: dict[str, int] = defaultdict(int)
        self._latencies: list[float] = []
        self._llm_latencies: list[float] = []

    def record(self, *, seriousness: str, queue: str, processing_time_ms: float, llm_latency_ms: float) -> None:
        with self._lock:
            self._total += 1
            self._decisions[seriousness] += 1
            self._queues[queue] += 1
            self._latencies.append(processing_time_ms)
            self._llm_latencies.append(llm_latency_ms)

    def snapshot(self) -> dict:
        with self._lock:
            lat = self._latencies
            llm = self._llm_latencies
            return {
                "total_requests": self._total,
                "decisions": dict(self._decisions),
                "queues": dict(self._queues),
                "performance": {
                    "avg_latency_ms": round(sum(lat) / len(lat), 1) if lat else 0.0,
                    "max_latency_ms": round(max(lat), 1) if lat else 0.0,
                    "avg_llm_latency_ms": round(sum(llm) / len(llm), 1) if llm else 0.0,
                },
            }


metrics_collector = MetricsCollector()
