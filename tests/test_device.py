import pytest
from src.utils.device import get_optimal_device, get_device_summary

def test_get_optimal_device():
    dev = get_optimal_device()
    assert dev in ["0", "cpu"]

def test_get_device_summary():
    summary = get_device_summary()
    assert "cuda_available" in summary
    assert "current_device" in summary
