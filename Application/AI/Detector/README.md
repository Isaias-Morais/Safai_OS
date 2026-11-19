# E002 Detector Adapter

Canonical checkpoint: `runs/detect/runs/detect/runs/safaios/safaios_yolo11s_v10k_img768/weights/best.pt`.

The adapter must use `configs/inference.yaml`, `DetectorConfig`, and `YOLOInferenceEngine`; it loads once in a server process and returns only validated object evidence.
