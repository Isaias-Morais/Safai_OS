"""Postprocessing utilities for prediction filtering and Non-Maximum Suppression."""
from typing import List
from src.detection.boxes import Prediction

def filter_by_confidence(predictions: List[Prediction], min_conf: float) -> List[Prediction]:
    """Filters predictions whose confidence score falls below min_conf."""
    return [p for p in predictions if p.confidence >= min_conf]

def filter_by_class(predictions: List[Prediction], allowed_classes: List[int]) -> List[Prediction]:
    """Filters predictions to only those in the allowed_classes set."""
    allowed = set(allowed_classes)
    return [p for p in predictions if p.class_id in allowed]

def apply_class_specific_nms(predictions: List[Prediction], iou_threshold: float = 0.5) -> List[Prediction]:
    """Applies greedy Non-Maximum Suppression per class."""
    by_class = {}
    for p in predictions:
        by_class.setdefault(p.class_id, []).append(p)

    kept = []
    for cls_id, preds in by_class.items():
        sorted_preds = sorted(preds, key=lambda x: x.confidence, reverse=True)
        suppressed = [False] * len(sorted_preds)

        for i in range(len(sorted_preds)):
            if suppressed[i]:
                continue
            kept.append(sorted_preds[i])
            for j in range(i + 1, len(sorted_preds)):
                if not suppressed[j]:
                    if sorted_preds[i].box.iou(sorted_preds[j].box) >= iou_threshold:
                        suppressed[j] = True
    return kept
