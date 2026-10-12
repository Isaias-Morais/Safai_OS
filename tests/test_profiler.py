import pytest
from src.utils.profiler import LatencyProfiler

def test_latency_profiler():
    prof = LatencyProfiler()
    for val in [10.0, 12.0, 15.0, 20.0, 25.0]:
        prof.record(val)

    stats = prof.stats()
    assert stats["count"] == 5
    assert stats["mean_ms"] == pytest.approx(16.4)
    assert stats["median_ms"] == pytest.approx(15.0)
    assert stats["fps"] == pytest.approx(1000.0 / 16.4)
