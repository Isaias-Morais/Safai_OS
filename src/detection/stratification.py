"""Evaluation stratification utilities for scale tiers and overlap density."""
from typing import List, Dict, Any, Tuple
from src.detection.boxes import BoundingBox

def compute_pairwise_overlap_stratum(
    boxes: List[BoundingBox],
    overlap_threshold: float = 0.1
) -> List[str]:
    """Classifies each box as 'overlapping' or 'isolated' based on max pairwise IoU."""
    n = len(boxes)
    if n <= 1:
        return ["isolated"] * n

    labels = ["isolated"] * n
    for i in range(n):
        for j in range(i + 1, n):
            iou = boxes[i].iou(boxes[j])
            if iou >= overlap_threshold:
                labels[i] = "overlapping"
                labels[j] = "overlapping"
    return labels

def compute_relative_size_tier(
    box: BoundingBox,
    small_cutoff: float = 0.025,
    large_cutoff: float = 0.050
) -> str:
    """Classifies box into dataset-relative size tier by normalized area."""
    area = box.area
    if area < small_cutoff:
        return "small_relative"
    elif area <= large_cutoff:
        return "medium_relative"
    return "large_relative"
