import pytest
from src.detection.boxes import BoundingBox
from src.detection.stratification import compute_pairwise_overlap_stratum, compute_relative_size_tier

def test_pairwise_overlap_stratum():
    b1 = BoundingBox(0.0, 0.0, 1.0, 1.0)
    b2 = BoundingBox(0.5, 0.0, 1.5, 1.0)  # Significant overlap
    b3 = BoundingBox(5.0, 5.0, 6.0, 6.0)  # Distant isolated box

    strata = compute_pairwise_overlap_stratum([b1, b2, b3], overlap_threshold=0.1)
    assert strata == ["overlapping", "overlapping", "isolated"]

def test_relative_size_tier():
    small = BoundingBox(0.0, 0.0, 0.1, 0.1)  # area = 0.01 < 0.025
    med = BoundingBox(0.0, 0.0, 0.2, 0.2)    # area = 0.04
    large = BoundingBox(0.0, 0.0, 0.3, 0.3)  # area = 0.09 > 0.050

    assert compute_relative_size_tier(small) == "small_relative"
    assert compute_relative_size_tier(med) == "medium_relative"
    assert compute_relative_size_tier(large) == "large_relative"
