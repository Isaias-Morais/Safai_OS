"""
SafaiOS Model Training & Evaluation Engine (Phase 3 Baseline)
=============================================================
Executes YOLO11s baseline training against safaios_dataset_v10k, monitors validation metrics,
and exports comprehensive experiment reports.
"""

import argparse
import json
import os
import sys
import time
import yaml
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="SafaiOS YOLO Training Pipeline")
    parser.add_argument("--config", default="configs/training.yaml", help="Path to training config")
    parser.add_argument("--data", "--dataset", default="data/safaios_dataset_v10k/data.yaml", help="Path to dataset yaml")
    parser.add_argument("--model", default="yolo11s.pt", help="Pretrained model checkpoint")
    parser.add_argument("--epochs", type=int, default=100, help="Number of training epochs")
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    parser.add_argument("--imgsz", type=int, default=640, help="Input image resolution")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--device", default="0", help="CUDA device index or cpu")
    parser.add_argument("--project", default="runs/safaios", help="Output project directory")
    parser.add_argument("--name", default="safaios_yolo11s_v10k_baseline", help="Experiment run name")
    parser.add_argument("--resume", action="store_true", help="Resume training from last checkpoint")
    parser.add_argument("--mixup", type=float, default=0.0, help="MixUp augmentation probability")
    parser.add_argument("--close_mosaic", type=int, default=10, help="Disable mosaic & mixup in last N epochs")
    parser.add_argument("--exp_id", default=None, help="Experiment ID for reporting")
    args = parser.parse_args()

    print("=== SAFAIOS MODEL TRAINING ENGINE ===")
    print(f"Experiment ID: {args.exp_id or 'Baseline/Adhoc'}")
    print(f"Model Initialization: {args.model}")
    print(f"Dataset Configuration: {args.data}")
    print(f"Epochs: {args.epochs}, Batch: {args.batch}, ImgSz: {args.imgsz}, Seed: {args.seed}, Device: {args.device}")
    print(f"MixUp: {args.mixup}, Close Mosaic: {args.close_mosaic}")

    # Import PyTorch and Ultralytics
    import torch
    from ultralytics import YOLO

    device_name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
    print(f"Active Compute Device: {device_name}")

    start_time = time.time()
    start_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))

    save_dir = Path(args.project) / args.name
    last_weights = save_dir / "weights" / "last.pt"
    if not last_weights.exists():
        nested_last = Path("runs/detect") / args.project / args.name / "weights" / "last.pt"
        if nested_last.exists():
            last_weights = nested_last
            save_dir = nested_last.parent.parent

    if args.resume and last_weights.exists():
        print(f"Resuming training from checkpoint: {last_weights}")
        model = YOLO(str(last_weights))
        results = model.train(resume=True)
    else:
        model = YOLO(args.model)
        # Train model
        results = model.train(
            data=args.data,
            epochs=args.epochs,
            imgsz=args.imgsz,
            batch=args.batch,
            device=args.device,
            seed=args.seed,
            project=args.project,
            name=args.name,
            exist_ok=True,
            workers=4,
            save=True,
            plots=True,
            val=True,
            mixup=args.mixup,
            close_mosaic=args.close_mosaic
        )

    end_time = time.time()
    duration_sec = end_time - start_time
    duration_str = f"{int(duration_sec // 3600)}h {int((duration_sec % 3600) // 60)}m {int(duration_sec % 60)}s"

    print(f"\nTraining completed in {duration_str}!")
    
    if not (save_dir / "weights" / "best.pt").exists():
        nested_dir = Path("runs/detect") / args.project / args.name
        if (nested_dir / "weights" / "best.pt").exists():
            save_dir = nested_dir

    best_weights = save_dir / "weights" / "best.pt"
    last_weights = save_dir / "weights" / "last.pt"
    results_csv = save_dir / "results.csv"

    print(f"Best Weights Path: {best_weights}")
    print(f"Last Weights Path: {last_weights}")

    # Parse results.csv for final and best epoch metrics
    metrics = {
        "precision": 0.0,
        "recall": 0.0,
        "map50": 0.0,
        "map50_95": 0.0,
        "best_epoch": 0
    }
    
    if results_csv.exists():
        with open(results_csv, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]
        if len(lines) > 1:
            headers = [h.strip() for h in lines[0].split(",")]
            # Find column indices
            p_idx = next((i for i, h in enumerate(headers) if "metrics/precision" in h), -1)
            r_idx = next((i for i, h in enumerate(headers) if "metrics/recall" in h), -1)
            m50_idx = next((i for i, h in enumerate(headers) if "metrics/mAP50(B)" in h or "metrics/mAP50" in h), -1)
            m95_idx = next((i for i, h in enumerate(headers) if "metrics/mAP50-95(B)" in h or "metrics/mAP50-95" in h), -1)
            
            best_m95 = -1.0
            for row_idx, line in enumerate(lines[1:], start=1):
                parts = [p.strip() for p in line.split(",")]
                try:
                    val_m95 = float(parts[m95_idx]) if m95_idx != -1 else 0.0
                    val_m50 = float(parts[m50_idx]) if m50_idx != -1 else 0.0
                    val_p = float(parts[p_idx]) if p_idx != -1 else 0.0
                    val_r = float(parts[r_idx]) if r_idx != -1 else 0.0
                    
                    if val_m95 > best_m95:
                        best_m95 = val_m95
                        metrics["map50_95"] = round(val_m95, 4)
                        metrics["map50"] = round(val_m50, 4)
                        metrics["precision"] = round(val_p, 4)
                        metrics["recall"] = round(val_r, 4)
                        metrics["best_epoch"] = row_idx
                except (ValueError, IndexError):
                    pass

    # Ensure reports/experiments directory exists
    reports_exp_dir = Path("reports/experiments")
    reports_exp_dir.mkdir(parents=True, exist_ok=True)

    exp_id = args.exp_id or "SAFAIOS-E001-YOLO11S-V10K"
    exp_code = exp_id.split("-")[1] if "-" in exp_id else exp_id

    exp_data = {
        "experiment_id": exp_id,
        "experiment_name": args.name,
        "dataset_version": "safaios_dataset_v10k",
        "dataset_config": args.data,
        "model_initialization": args.model,
        "parameters": {
            "imgsz": args.imgsz,
            "batch_size": args.batch,
            "epochs": args.epochs,
            "seed": args.seed,
            "device": args.device,
            "gpu_name": device_name,
            "mixup": args.mixup,
            "close_mosaic": args.close_mosaic
        },
        "execution": {
            "start_time": start_time_str,
            "duration": duration_str,
            "completed_epochs": args.epochs,
            "best_epoch": metrics["best_epoch"],
            "best_weights": str(best_weights).replace("\\", "/"),
            "last_weights": str(last_weights).replace("\\", "/")
        },
        "validation_metrics": {
            "precision": metrics["precision"],
            "recall": metrics["recall"],
            "map50": metrics["map50"],
            "map50_95": metrics["map50_95"]
        },
        "isolation_status": {
            "test_locked_v2_evaluated": False,
            "india_real_world_evaluated": False
        },
        "status": f"{exp_id}_COMPLETE"
    }

    # Save JSON report
    json_path = reports_exp_dir / f"{exp_code}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(exp_data, f, indent=2)

    # Save Markdown experiment report
    md_path = reports_exp_dir / f"{exp_code}.md"
    md_content = f"""# SafaiOS Experiment Record: {exp_id}

**Experiment ID:** {exp_id}  
**Experiment Name:** {args.name}  
**Model Architecture:** YOLO11s (`{args.model}`)  
**Dataset Version:** `safaios_dataset_v10k` (10,000 training images)  
**Execution Status:** **{exp_id} COMPLETE**

---

## 1. Execution Summary

- **GPU Device:** {device_name}
- **Start Time:** {start_time_str}
- **Duration:** {duration_str}
- **Completed Epochs:** {args.epochs} / {args.epochs}
- **Best Epoch:** Epoch {metrics['best_epoch']} (Selected by Validation mAP@50-95)
- **Best Weights Checkpoint:** `{best_weights}`

---

## 2. Resolved Hyperparameters

- **Input Resolution (`imgsz`):** {args.imgsz}
- **Batch Size:** {args.batch}
- **Random Seed:** {args.seed}
- **Device Index:** {args.device}
- **MixUp:** {args.mixup}
- **Close Mosaic:** {args.close_mosaic}
- **Optimizer:** `auto`

---

## 3. Measured Validation Metrics (`validation/` Split)

- **Precision:** {metrics['precision']}
- **Recall:** {metrics['recall']}
- **mAP@50:** {metrics['map50']}
- **mAP@50-95:** {metrics['map50_95']}

---

## 4. Evaluation Isolation Verification

- **`test_locked_v2` Evaluated:** **NO** (0 inferences performed - SACRED & PROTECTED)
- **`india_real_world` Evaluated:** **NO** (0 inferences performed - INDEPENDENT BENCHMARK)

---

## 5. Official Result Status

```
{exp_id} COMPLETE
LOCKED TEST AND INDIA BENCHMARK UNTOUCHED
```
"""
    md_path.write_text(md_content, encoding="utf-8")

    # Only write phase3 report if this is explicitly E001
    if exp_id == "SAFAIOS-E001-YOLO11S-V10K":
        phase3_report_path = Path("reports/phase3_yolo11s_baseline_report.md")
        phase3_report_path.write_text(md_content, encoding="utf-8")

    print(f"\nExperiment records saved to:")
    print(f" - {json_path}")
    print(f" - {md_path}")

if __name__ == "__main__":
    main()
