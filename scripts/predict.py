"""
SafaiOS Single Image / Directory Inference Script
Runs inference on unseen images and visualizes bounding boxes, classes, and confidence scores.
"""
import argparse
from pathlib import Path

def run_prediction(source_path, weights_path="models/checkpoints/safaios_baseline/weights/best.pt", conf=0.25):
    print("=== SafaiOS Waste Predictor ===")
    print(f"Loading weights: {weights_path}")
    print(f"Processing source: {source_path}")
    
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
    results = model.predict(source=source_path, conf=conf, save=True, project="reports", name="predictions")
    print(f"Prediction complete. Results saved in reports/predictions")
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SafaiOS Predictor")
    parser.add_argument("--source", required=True, help="Path to image or directory")
    parser.add_argument("--weights", default="models/checkpoints/safaios_baseline/weights/best.pt")
    parser.add_argument("--conf", type=float, default=0.25)
    args = parser.parse_args()

    run_prediction(args.source, args.weights, args.conf)
