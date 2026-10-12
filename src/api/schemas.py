"""Lightweight dataclass request and response schemas for SafaiOS detection API."""
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class DetectionBoxSchema:
    xmin: float
    ymin: float
    xmax: float
    ymax: float

@dataclass
class DetectionItemSchema:
    class_id: int
    class_name: str
    confidence: float
    box: DetectionBoxSchema

@dataclass
class DetectionResponseSchema:
    num_detections: int
    inference_time_ms: float
    detections: List[DetectionItemSchema] = field(default_factory=list)
    status: str = "success"
