"""Pydantic request and response schemas for SafaiOS detection API."""
from typing import List, Optional
from pydantic import BaseModel, Field

class DetectionBoxSchema(BaseModel):
    xmin: float = Field(..., ge=0.0, le=1.0)
    ymin: float = Field(..., ge=0.0, le=1.0)
    xmax: float = Field(..., ge=0.0, le=1.0)
    ymax: float = Field(..., ge=0.0, le=1.0)

class DetectionItemSchema(BaseModel):
    class_id: int = Field(..., ge=0, le=4)
    class_name: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    box: DetectionBoxSchema

class DetectionResponseSchema(BaseModel):
    status: str = "success"
    num_detections: int
    inference_time_ms: float
    detections: List[DetectionItemSchema]
