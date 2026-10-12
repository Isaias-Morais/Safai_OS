import pytest
from src.api.schemas import DetectionBoxSchema, DetectionItemSchema, DetectionResponseSchema

def test_detection_response_schema():
    box = DetectionBoxSchema(xmin=0.1, ymin=0.2, xmax=0.5, ymax=0.6)
    item = DetectionItemSchema(class_id=0, class_name="plastic_bottle", confidence=0.95, box=box)
    resp = DetectionResponseSchema(num_detections=1, inference_time_ms=12.4, detections=[item])

    assert resp.status == "success"
    assert resp.num_detections == 1
    assert resp.detections[0].class_name == "plastic_bottle"
