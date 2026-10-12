"""Greedy bipartite matching engine for object detection ground-truth assignment."""
from typing import List, Tuple, Dict, Any
from src.detection.boxes import BoundingBox, Prediction

class GreedyMatcher:
    def __init__(self, iou_threshold: float = 0.5):
        self.iou_threshold = iou_threshold

    def match(
        self,
        ground_truths: List[Tuple[BoundingBox, int]],
        predictions: List[Prediction]
    ) -> Dict[str, Any]:
        """Matches predictions to ground truths using greedy highest-confidence bipartite matching.
        
        ground_truths: list of (BoundingBox, class_id)
        predictions: list of Prediction
        """
        # Sort predictions by confidence descending
        sorted_preds = sorted(predictions, key=lambda p: p.confidence, reverse=True)

        matched_gt = set()
        matched_pred = set()
        tp_matches = []
        fp_confusions = []
        fp_localizations = []

        for p_idx, pred in enumerate(sorted_preds):
            best_iou = 0.0
            best_gt_idx = -1
            best_gt_cls = -1

            for gt_idx, (gt_box, gt_cls) in enumerate(ground_truths):
                if gt_idx in matched_gt:
                    continue
                iou = pred.box.iou(gt_box)
                if iou > best_iou:
                    best_iou = iou
                    best_gt_idx = gt_idx
                    best_gt_cls = gt_cls

            if best_gt_idx != -1 and best_iou >= self.iou_threshold:
                if pred.class_id == best_gt_cls:
                    matched_gt.add(best_gt_idx)
                    matched_pred.add(p_idx)
                    tp_matches.append((p_idx, best_gt_idx, best_iou))
                else:
                    matched_pred.add(p_idx)
                    fp_confusions.append((p_idx, best_gt_idx, best_iou))
            elif best_gt_idx != -1 and 0.1 <= best_iou < self.iou_threshold:
                matched_pred.add(p_idx)
                fp_localizations.append((p_idx, best_gt_idx, best_iou))

        # Background false positives are remaining unmatched predictions
        fp_background = [p_idx for p_idx in range(len(sorted_preds)) if p_idx not in matched_pred]
        fn_unmatched_gt = [gt_idx for gt_idx in range(len(ground_truths)) if gt_idx not in matched_gt]

        return {
            "tp_count": len(tp_matches),
            "fn_count": len(fn_unmatched_gt),
            "fp_total": len(sorted_preds) - len(tp_matches),
            "fp_background": len(fp_background),
            "fp_localization": len(fp_localizations),
            "fp_confusion": len(fp_confusions),
            "matched_pairs": tp_matches,
            "missed_gt_indices": fn_unmatched_gt
        }
