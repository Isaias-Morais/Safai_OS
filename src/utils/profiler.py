"""Latency and throughput profiling timer using Python standard library."""
from typing import List, Dict, Any
import math

class LatencyProfiler:
    def __init__(self):
        self.measurements: List[float] = []

    def record(self, elapsed_ms: float) -> None:
        self.measurements.append(elapsed_ms)

    def stats(self) -> Dict[str, float]:
        if not self.measurements:
            return {"count": 0, "mean_ms": 0.0, "median_ms": 0.0, "p95_ms": 0.0, "p99_ms": 0.0, "fps": 0.0}

        sorted_m = sorted(self.measurements)
        n = len(sorted_m)
        mean_ms = sum(sorted_m) / n
        median_ms = sorted_m[n // 2] if n % 2 != 0 else (sorted_m[n // 2 - 1] + sorted_m[n // 2]) / 2.0

        p95_idx = min(n - 1, int(math.ceil(0.95 * n)) - 1)
        p99_idx = min(n - 1, int(math.ceil(0.99 * n)) - 1)

        return {
            "count": n,
            "mean_ms": mean_ms,
            "median_ms": median_ms,
            "p95_ms": sorted_m[max(0, p95_idx)],
            "p99_ms": sorted_m[max(0, p99_idx)],
            "fps": 1000.0 / mean_ms if mean_ms > 0 else 0.0
        }
