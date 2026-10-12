# SafaiOS Experiment Record: SAFAIOS-E001-YOLO11S-V10K

**Experiment ID:** SAFAIOS-E001-YOLO11S-V10K  
**Experiment Name:** safaios_yolo11s_v10k_baseline  
**Model Architecture:** YOLO11s (`yolo11s.pt`)  
**Dataset Version:** `safaios_dataset_v10k` (10,000 training images)  
**Execution Status:** **PHASE 3 — EXPERIMENT 001 COMPLETE (FROZEN BASELINE)**

---

## 1. Execution Summary

- **GPU Device:** NVIDIA GeForce RTX 4060 Laptop GPU
- **Start Time:** 2026-10-10 18:29:45
- **Duration:** 3h 15m 45s
- **Completed Epochs:** 100 / 100
- **Best Epoch:** Epoch 62 (Physical baseline artifact preserved; transient Epoch 71 peak unpreserved due to resume overwrite)
- **Best Weights Checkpoint:** `runs/detect/runs/safaios/safaios_yolo11s_v10k_baseline/weights/best.pt`
- **Best Weights SHA256:** `49e9e047fbb04c66244b734623bb4e84abfbab5a3aa9797c375d926919a86737` (56,957,912 B)
- **Last Weights Checkpoint:** `runs/detect/runs/safaios/safaios_yolo11s_v10k_baseline/weights/last.pt`
- **Last Weights SHA256:** `5a357eb469a67a3fd09788ad42d0f038979bbf101a04e5140260ba3f688a18cd` (56,958,616 B)

---

## 2. Resolved Hyperparameters

- **Input Resolution (`imgsz`):** 640
- **Batch Size:** 16
- **Random Seed:** 42
- **Device Index:** 0
- **Optimizer:** `auto` (MuSGD)
- **MixUp:** 0.0

---

## 3. Measured Validation Metrics (`validation/` Split)

Evaluated directly at 640px against `data/safaios_dataset_v10k/validation/` (1,000 images, 2,463 instances):
- **Precision:** 0.9822 (exact: `0.9822008528219875`)
- **Recall:** 0.9824 (exact: `0.9823701889679468`)
- **mAP@50:** 0.9944 (exact: `0.9943545295825296`)
- **mAP@50-95:** 0.9840 (exact: `0.9840467317218876`)

### Per-Class Detailed Metrics
- `plastic_bottle`: mAP@50–95 = 0.9824
- `plastic_wrapper_bag`: mAP@50–95 = 0.9858
- `paper_cardboard`: mAP@50–95 = 0.9842
- `glass_bottle_container`: mAP@50–95 = 0.9841
- `metal_can`: mAP@50–95 = 0.9837

> **Audit & Verification Record:**  
> Full reconstruction and direct evaluation details are documented in [`SAFAIOS-E001-verification.md`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/reports/experiments/SAFAIOS-E001-verification.md).

---

## 4. Evaluation Isolation Verification

- **`test_locked_v2` Evaluated:** **NO** (0 inferences performed - SACRED & PROTECTED)
- **`india_real_world` Evaluated:** **NO** (0 inferences performed - INDEPENDENT BENCHMARK)

---

## 5. Official Result Status

```
PHASE 3 — EXPERIMENT 001 COMPLETE
YOLO11s BASELINE ESTABLISHED & FROZEN (mAP@50-95: 98.40%)
```
