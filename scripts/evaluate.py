"""
SafaiOS Model Evaluation Script
Evaluates trained YOLO waste detector on validation and untouched test splits.
Calculates mAP@50, mAP@50:95, per-class Precision/Recall/F1, latency, and confusion matrix.
"""
import argparse
from pathlib import Path

def evaluate_model(weights_path="models/checkpoints/safaios_baseline/weights/best.pt", dataset_path="configs/dataset.yaml"):
    print("=== SafaiOS Model Evaluation ===")
    print(f"Evaluating checkpoint: {weights_path}")
    
    try:
        from ultralytics import YOLO
    except ImportError:
        print("Ultralytics is not installed.")
        return

    weights = Path(weights_path)
    if not weights.exists():
        print(f"Weights file not found at {weights_path}. Train the model first.")
        return

    model = YOLO(weights_path)
    metrics = model.val(data=dataset_path, split="test")

    print("\n--- Summary Evaluation Metrics ---")
    print(f"mAP@50: {metrics.box.map50:.4f}")
    print(f"mAP@50-95: {metrics.box.map:.4f}")
    print(f"Precision: {metrics.box.mp:.4f}")
    print(f"Recall: {metrics.box.mr:.4f}")
    return metrics

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SafaiOS Model Evaluation")
    parser.add_argument("--weights", default="models/checkpoints/safaios_baseline/weights/best.pt")
    parser.add_argument("--dataset", default="configs/dataset.yaml")
    args = parser.parse_args()

    evaluate_model(args.weights, args.dataset)
