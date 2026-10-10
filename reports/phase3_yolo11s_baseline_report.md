# SafaiOS Experiment Record: SAFAIOS-E001-YOLO11S-V10K

**Experiment ID:** SAFAIOS-E001-YOLO11S-V10K  
**Experiment Name:** safaios_yolo11s_v10k_img768  
**Model Architecture:** YOLO11s (`yolo11s.pt`)  
**Dataset Version:** `safaios_dataset_v10k` (10,000 training images)  
**Execution Status:** **PHASE 3 — EXPERIMENT 001 COMPLETE**

---

## 1. Execution Summary

- **GPU Device:** NVIDIA GeForce RTX 4060 Laptop GPU
- **Start Time:** 2026-10-10 18:29:45
- **Duration:** 3h 15m 45s
- **Completed Epochs:** 100 / 100
- **Best Epoch:** Epoch 87 (Selected by Validation mAP@50-95)
- **Best Weights Checkpoint:** `runs\detect\runs\detect\runs\safaios\safaios_yolo11s_v10k_img768\weights\best.pt`

---

## 2. Resolved Hyperparameters

- **Input Resolution (`imgsz`):** 768
- **Batch Size:** 16
- **Random Seed:** 42
- **Device Index:** 0
- **Optimizer:** `auto` (AdamW)

---

## 3. Measured Validation Metrics (`validation/` Split)

- **Precision:** 0.9939
- **Recall:** 0.9928
- **mAP@50:** 0.9949
- **mAP@50-95:** 0.9887

---

## 4. Evaluation Isolation Verification

- **`test_locked_v2` Evaluated:** **NO** (0 inferences performed - SACRED & PROTECTED)
- **`india_real_world` Evaluated:** **NO** (0 inferences performed - INDEPENDENT BENCHMARK)

---

## 5. Official Result Status

```
PHASE 3 — EXPERIMENT 001 COMPLETE
YOLO11s BASELINE ESTABLISHED
```
