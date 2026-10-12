"""Latency and throughput profiling timer."""
import time
from typing import List, Dict, Any
import numpy as np

class LatencyProfiler:
    def __init__(self):
        self.measurements: List[float] = []

    def record(self, elapsed_ms: float) -> None:
        self.measurements.append(elapsed_ms)

    def stats(self) -> Dict[str, float]:
        if not self.measurements:
            return {"count": 0, "mean_ms": 0.0, "median_ms": 0.0, "p95_ms": 0.0, "p99_ms": 0.0, "fps": 0.0}

        arr = np.array(self.measurements)
        mean_ms = float(np.mean(arr))
        return {
            "count": len(self.measurements),
            "mean_ms": mean_ms,
            "median_ms": float(np.median(arr)),
            "p95_ms": float(np.percentile(arr, 95)),
            "p99_ms": float(np.percentile(arr, 99)),
            "fps": 1000.0 / mean_ms if mean_ms > 0 else 0.0
        }
