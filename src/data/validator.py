"""Validation utilities for YOLO annotation formatting and integrity."""
from typing import List, Tuple, Dict, Any
from pathlib import Path

def validate_yolo_annotation_line(line: str, num_classes: int = 5) -> Tuple[bool, str]:
    """Validates a single line of a YOLO format txt annotation file."""
    parts = line.strip().split()
    if not parts:
        return True, ""  # empty line ok

    if len(parts) != 5:
        return False, f"Expected 5 tokens (class cx cy w h), found {len(parts)}"

    try:
        cls_id = int(parts[0])
        cx = float(parts[1])
        cy = float(parts[2])
        w = float(parts[3])
        h = float(parts[4])
    except ValueError:
        return False, "Non-numeric token in annotation"

    if cls_id < 0 or cls_id >= num_classes:
        return False, f"Class ID {cls_id} out of range [0, {num_classes-1}]"

    for name, val in [("cx", cx), ("cy", cy), ("w", w), ("h", h)]:
        if val < 0.0 or val > 1.0:
            return False, f"Normalized coordinate {name}={val} out of bounds [0.0, 1.0]"

    if w <= 0.0 or h <= 0.0:
        return False, f"Width or height is zero or negative (w={w}, h={h})"

    return True, ""
