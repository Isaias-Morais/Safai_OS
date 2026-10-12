# SafaiOS Detection API Specification

## Endpoints

### `POST /v1/detect`

Runs waste detection on an uploaded image.

**Request:** `multipart/form-data` with `file: image/jpeg`

**Response:**
```json
{
  "status": "success",
  "num_detections": 2,
  "inference_time_ms": 11.4,
  "detections": [
    {
      "class_id": 0,
      "class_name": "plastic_bottle",
      "confidence": 0.94,
      "box": {"xmin": 0.12, "ymin": 0.34, "xmax": 0.28, "ymax": 0.65}
    }
  ]
}
```
