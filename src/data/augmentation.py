"""Bounding box coordinate transformation utilities for data augmentation."""
from typing import Tuple
from src.detection.boxes import BoundingBox

def horizontal_flip_bbox(box: BoundingBox) -> BoundingBox:
    """Computes horizontally flipped normalized coordinates (x' = 1 - x)."""
    return BoundingBox(
        xmin=1.0 - box.xmax,
        ymin=box.ymin,
        xmax=1.0 - box.xmin,
        ymax=box.ymax
    )

def scale_bbox(box: BoundingBox, scale_x: float, scale_y: float) -> BoundingBox:
    """Scales a bounding box relative to its center."""
    cx, cy, w, h = box.to_xywh()
    new_w = w * scale_x
    new_h = h * scale_y
    return BoundingBox(
        xmin=max(0.0, cx - new_w / 2.0),
        ymin=max(0.0, cy - new_h / 2.0),
        xmax=min(1.0, cx + new_w / 2.0),
        ymax=min(1.0, cy + new_h / 2.0)
    )
