"""
SafaiOS Model Training Script
Trains a YOLO waste detection model using configured dataset and hyperparameters.
"""
import argparse
import yaml
from pathlib import Path

def train_model(config_path="configs/training.yaml", dataset_path="configs/dataset.yaml"):
    print("=== SafaiOS Model Training Pipeline ===")
    print(f"Loading training config: {config_path}")
    print(f"Loading dataset config: {dataset_path}")
    
    # Delayed import of ultralytics to allow environment checks first
    try:
        from ultralytics import YOLO
    except ImportError:
        print("Ultralytics is not installed in the environment. Please run environment setup.")
        return

    with open(config_path, "r") as f:
        train_cfg = yaml.safe_load(f)

    model_variant = train_cfg["model"]["variant"]
    print(f"Initializing YOLO model from variant: {model_variant}")
    model = YOLO(model_variant)

    results = model.train(
        data=dataset_path,
        epochs=train_cfg["training"]["epochs"],
        imgsz=train_cfg["model"]["input_size"],
        batch=train_cfg["training"]["batch_size"],
        device=train_cfg["training"]["device"],
        seed=train_cfg["training"]["seed"],
        project="models/checkpoints",
        name="safaios_baseline",
        exist_ok=True
    )
    print("Training complete! Results saved in models/checkpoints/safaios_baseline")
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SafaiOS YOLO Training")
    parser.add_argument("--config", default="configs/training.yaml", help="Path to training config")
    parser.add_argument("--dataset", default="configs/dataset.yaml", help="Path to dataset config")
    args = parser.parse_args()

    train_model(args.config, args.dataset)
