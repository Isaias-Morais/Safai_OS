# E002 ML Integration Contract

Selected model: E002 YOLO11s, 768px, five classes, checkpoint SHA-256 `8bd30b05a0b4a84d95c5e71f213b967d255144a8fe57791ef110b920fc86d073`.

Use `configs/inference.yaml`: confidence `0.25`, NMS IoU `0.60`; operational matching IoU `0.50` is evaluation-only. Verify the hash at service startup and fail closed on mismatch. Classes are IDs 0–4: `plastic_bottle`, `plastic_wrapper_bag`, `paper_cardboard`, `glass_bottle_container`, `metal_can`.

Input: authenticated server-side multipart image; accept JPEG/PNG only after content sniffing, dimension/pixel and byte limits (limits are an open deployment decision), malware/storage scanning, and temporary-file cleanup. `YOLOInferenceEngine.predict` returns `src.detection.boxes.Prediction` (`box`, `class_id`, `confidence`, `class_name`), with its `BoundingBox` normalized as `xmin/ymin/xmax/ymax`. The application adapter maps it without changing semantics to `src.api.schemas.DetectionResponseSchema`: `status`, `num_detections`, `inference_time_ms`, and `DetectionItemSchema` values (`class_id`, `class_name`, `confidence`, `box`). Validate finite values, known classes, `0≤confidence≤1`, and ordered in-range boxes.

Load `YOLOInferenceEngine` once per inference worker. Enforce request timeout, bounded concurrency, structured error codes, request IDs, GPU-health checks, and CPU fallback policy before deployment. Never return internal paths/exceptions to clients. E002 mean GPU latency is 13.48ms (P50 14.22ms, P95 18.79ms, RTX 4060); this excludes API/upload latency. No validated ONNX/TensorRT artifact exists.

Independent results remain separate: locked test 98.79% mAP50–95; India real-world 97.56% mAP50–95. E004 is a completed negative result for its overlap target and is not the deployed model.
