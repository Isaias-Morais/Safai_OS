# SafaiOS — Phase 3 Training Plan & Execution Protocol

**Project:** SafaiOS  
**Tagline:** "The Intelligence Behind Cleaner Cities."  
**Operating Principle:** "Detect. Act. Verify."  
**Phase:** Phase 3 — YOLO11s Baseline Training  
**Dataset Version:** `safaios_dataset_v10k` (10,000 training images)  
**Model Architecture:** YOLO11s (`yolo11s.pt`)  
**Phase 3 Status:** **PHASE 3 READY TO BEGIN** (Training NOT YET executed)

---

## 1. Overview & Objectives

Phase 3 establishes the official baseline object detection model for SafaiOS using the newly finalized 10,000-image dataset (`safaios_dataset_v10k`). 

The primary goals of Phase 3 are:
1. Train a clean, reproducible YOLO11s baseline detector across the 5 canonical SafaiOS classes.
2. Monitor training dynamics, loss convergence, and validation mAP metrics exclusively on the 1,000-image `validation` split.
3. Keep the 1,000-image `test_locked_v2` and 100-image `india_real_world` benchmark sets strictly locked and untouched.

---

## 2. Dataset & Split Configuration

- **Dataset Config Path:** `data/safaios_dataset_v10k/data.yaml`
- **Training Set:** `training/images` (10,000 images / 24,197 bounding boxes)
- **Validation Set:** `validation/images` (1,000 images / 2,463 bounding boxes)
- **Locked Test Set v2.0:** `test_locked_v2/images` (1,000 images - **EXCLUDED FROM TRAINING/TUNING**)
- **India Real-World Benchmark:** `india_real_world/images` (100 images - **EXCLUDED FROM TRAINING/TUNING**)

### Target Taxonomy Mapping (5 Classes)
- `0`: `plastic_bottle`
- `1`: `plastic_wrapper_bag`
- `2`: `paper_cardboard`
- `3`: `glass_bottle_container`
- `4`: `metal_can`

---

## 3. Training Hyperparameters & Execution Protocol

| Parameter | Configuration Value | Description / Rationale |
| :--- | :--- | :--- |
| **Model Weight** | `yolo11s.pt` | Official YOLO11 small baseline weights |
| **Dataset Config** | `data/safaios_dataset_v10k/data.yaml` | Finalized 10k dataset YAML |
| **Image Resolution (`imgsz`)** | `640` | Standard 640x640 input resolution |
| **Batch Size (`batch`)** | `16` | Standard batch size for stability |
| **Epochs (`epochs`)** | `100` | Full 100-epoch baseline run |
| **Optimizer (`optimizer`)** | `auto` | Auto-selected optimizer (AdamW / SGD) |
| **Initial Learning Rate (`lr0`)** | `0.01` | Standard initial learning rate |
| **Final Learning Rate (`lrf`)** | `0.01` | Learning rate decay factor |
| **Random Seed (`seed`)** | `42` | Fixed seed for strict reproducibility |
| **Device (`device`)** | `0` (or `cpu` if fallback) | GPU acceleration |
| **Workers (`workers`)** | `8` | Parallel data loading threads |
| **Experiment Name (`name`)** | `safaios_yolo11s_v10k_baseline` | Standard run identifier |
| **Save Directory** | `runs/detect/safaios_yolo11s_v10k_baseline` | Output weights & log directory |

---

## 4. Evaluation & Model Selection Policy

1. **Allowed Evaluation Splits During Training:**
   - `training`: Loss logging & training metrics.
   - `validation`: Early stopping, validation loss, mAP@50, and mAP@50-95 monitoring.
2. **Prohibited Evaluation Splits During Baseline Training:**
   - `test_locked_v2`: Sacred test set. Zero evaluations permitted during model development.
   - `india_real_world`: Real-world deployment benchmark. Zero evaluations permitted during baseline training.
3. **Checkpoint Selection Policy:**
   - Save `best.pt` based on maximum validation mAP@50-95.
   - Save `last.pt` at epoch 100 completion.

---

## 5. Execution Entry Point

The baseline training job will be launched via:
```bash
python scripts/train.py --config data/safaios_dataset_v10k/data.yaml --model yolo11s.pt --epochs 100 --batch 16 --imgsz 640 --seed 42 --name safaios_yolo11s_v10k_baseline
```

*(Note: Training script `scripts/train.py` remains unexecuted until Phase 3 execution is formally initiated.)*
