import pytest
from src.detection.boxes import BoundingBox, Prediction
from src.detection.matcher import GreedyMatcher

def test_greedy_matcher_perfect_match():
    matcher = GreedyMatcher(iou_threshold=0.5)
    gts = [
        (BoundingBox(0.0, 0.0, 1.0, 1.0), 0),
        (BoundingBox(2.0, 2.0, 3.0, 3.0), 1),
    ]
    preds = [
        Prediction(BoundingBox(0.0, 0.0, 1.0, 1.0), class_id=0, confidence=0.9),
        Prediction(BoundingBox(2.0, 2.0, 3.0, 3.0), class_id=1, confidence=0.8),
    ]
    res = matcher.match(gts, preds)
    assert res["tp_count"] == 2
    assert res["fn_count"] == 0
    assert res["fp_total"] == 0

def test_greedy_matcher_confusion_and_miss():
    matcher = GreedyMatcher(iou_threshold=0.5)
    gts = [
        (BoundingBox(0.0, 0.0, 1.0, 1.0), 0),
        (BoundingBox(2.0, 2.0, 3.0, 3.0), 1),
    ]
    # Prediction on box 1 has wrong class_id (2 instead of 0)
    preds = [
        Prediction(BoundingBox(0.0, 0.0, 1.0, 1.0), class_id=2, confidence=0.9),
    ]
    res = matcher.match(gts, preds)
    assert res["tp_count"] == 0
    assert res["fp_confusion"] == 1
    assert res["fn_count"] == 2
