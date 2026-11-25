import pytest
from src.api.schemas import DetectionBoxSchema, DetectionItemSchema, DetectionResponseSchema
from datetime import datetime, timezone
from pydantic import ValidationError
from src.schemas.health import ComponentStatus, HealthResponse

def test_detection_response_schema():
    box = DetectionBoxSchema(xmin=0.1, ymin=0.2, xmax=0.5, ymax=0.6)
    item = DetectionItemSchema(class_id=0, class_name="plastic_bottle", confidence=0.95, box=box)
    resp = DetectionResponseSchema(num_detections=1, inference_time_ms=12.4, detections=[item])

    assert resp.status == "success"
    assert resp.num_detections == 1
    assert resp.detections[0].class_name == "plastic_bottle"



def test_health_response_schema():
    payload = {
        "status": "healthy",
        "version": "1.0.0",
        "uptime_seconds": 120.0,
        "timestamp": datetime.now(timezone.utc),
        "model_loaded": True,
        "database": {
            "status": "healthy",
            "latency_ms": 35.0,
            "message": "Database operating normally"
        }
    }

    response = HealthResponse(**payload)

    assert response.status == "healthy"
    assert response.version == "1.0.0"
    assert response.uptime_seconds == 120.0
    assert response.model_loaded is True
    assert response.database.latency_ms == 35.0


def test_component_status_rejects_negative_latency():
    with pytest.raises(ValidationError):
        ComponentStatus(
            status="healthy",
            latency_ms=-10
        )
