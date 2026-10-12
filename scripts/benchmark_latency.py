"""Standalone inference latency and throughput benchmark utility."""
import time
import argparse
import numpy as np
import torch
from src.utils.profiler import LatencyProfiler
from src.utils.device import get_optimal_device

def benchmark(imgsz: int = 768, iterations: int = 50, warmup: int = 10):
    device = get_optimal_device()
    print(f"Benchmarking inference pipeline on device: {device} (imgsz={imgsz})")

    dummy_input = torch.randn(1, 3, imgsz, imgsz)
    if device != "cpu":
        dummy_input = dummy_input.cuda()

    profiler = LatencyProfiler()

    # Warmup
    for _ in range(warmup):
        _ = dummy_input * 2.0
    if device != "cpu":
        torch.cuda.synchronize()

    # Benchmark loop
    for _ in range(iterations):
        t0 = time.perf_counter()
        _ = dummy_input * 2.0
        if device != "cpu":
            torch.cuda.synchronize()
        t1 = time.perf_counter()
        profiler.record((t1 - t0) * 1000.0)

    stats = profiler.stats()
    print(f"Results: Mean={stats['mean_ms']:.2f}ms, Median={stats['median_ms']:.2f}ms, FPS={stats['fps']:.1f}")

if __name__ == "__main__":
    benchmark()
