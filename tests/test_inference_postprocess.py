import pytest
from src.detection.boxes import BoundingBox, Prediction
from src.inference.postprocess import filter_by_confidence, filter_by_class, apply_class_specific_nms

def test_filter_by_confidence():
    b = BoundingBox(0, 0, 1, 1)
    preds = [
        Prediction(b, 0, 0.9),
        Prediction(b, 0, 0.4),
        Prediction(b, 0, 0.2)
    ]
    filtered = filter_by_confidence(preds, min_conf=0.3)
    assert len(filtered) == 2
    assert all(p.confidence >= 0.3 for p in filtered)

def test_apply_class_specific_nms():
    b1 = BoundingBox(0, 0, 1, 1)
    b2 = BoundingBox(0.1, 0.1, 1.0, 1.0)  # High overlap with b1
    b3 = BoundingBox(5, 5, 6, 6)           # Disjoint

    preds = [
        Prediction(b1, class_id=0, confidence=0.9),
        Prediction(b2, class_id=0, confidence=0.7),  # Should be suppressed
        Prediction(b3, class_id=0, confidence=0.8),  # Kept
        Prediction(b1, class_id=1, confidence=0.6),  # Different class, kept
    ]
    kept = apply_class_specific_nms(preds, iou_threshold=0.5)
    assert len(kept) == 3
