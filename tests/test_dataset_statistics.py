import pytest
from src.data.statistics import compute_class_distribution

def test_compute_class_distribution():
    labels = [0, 0, 1, 1, 1, 2, 3, 4]
    stats = compute_class_distribution(labels, num_classes=5)
    assert stats["total_instances"] == 8
    assert stats["per_class"][0]["count"] == 2
    assert stats["per_class"][1]["count"] == 3
    assert stats["imbalance_ratio"] == 3.0 / 1.0
