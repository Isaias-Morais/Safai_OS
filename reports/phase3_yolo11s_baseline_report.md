# SafaiOS — Phase 3 YOLO11s Baseline Report

**Project:** SafaiOS  
**Primary Tagline:** The Intelligence Behind Cleaner Cities.  
**Operating Principle:** Detect. Act. Verify.  
**Experiment Identifier:** `SAFAIOS-E001-YOLO11S-V10K`  
**Experiment Name:** `safaios_yolo11s_v10k_baseline`  
**Model Architecture:** YOLO11s (`yolo11s.pt` initialization)  
**Dataset Version:** `safaios_dataset_v10k` (10,000 training images)  
**Execution Status:** **PHASE 3 — EXPERIMENT 001 COMPLETE**  
**Baseline Status:** **YOLO11s BASELINE ESTABLISHED**

---

## 1. Executive Summary

Phase 3 Experiment 001 (`SAFAIOS-E001-YOLO11S-V10K`) has completed 100 epochs of baseline object-detection training on the frozen `safaios_dataset_v10k` dataset. 

Training executed cleanly on an **NVIDIA GeForce RTX 4060 Laptop GPU (8GB VRAM)** using PyTorch `2.5.1+cu121` and Ultralytics `8.4.174`. The model was trained exclusively on the 10,000 training images (24,197 bounding boxes) and evaluated epoch-by-epoch on the 1,000 validation images (2,463 bounding boxes).

The locked test set (`test_locked_v2/`, 1,000 images / 2,590 boxes) and the India real-world benchmark (`india_real_world/`, 100 images / 269 boxes) remained **100% isolated, untouched, and un-evaluated** throughout the experiment.

---

## 2. Preflight & Hardware Environment

| Property | Measured / Configured Value |
|---|---|
| **Python Environment** | Project `.venv` (Python 3.11.17) |
| **PyTorch Version** | `2.5.1+cu121` |
| **Ultralytics Version** | `8.4.174` |
| **Compute Hardware** | NVIDIA GeForce RTX 4060 Laptop GPU |
| **CUDA Available** | True (GPU 0) |
| **Model Weights Initialization** | Pretrained `yolo11s.pt` |
| **Dataset Configuration** | `data/safaios_dataset_v10k/data.yaml` |

---

## 3. Dataset Configuration & Preflight Inventory

| Dataset Split | Verified Image Count | Verified Bounding Box Count | Strict Isolation Status |
|---|---:|---:|---|
| **Training** | 10,000 | 24,197 | Gradient-based learning |
| **Validation** | 1,000 | 2,463 | Epoch evaluation & model selection |
| **Locked Test (`test_locked_v2`)** | 1,000 | 2,590 | **PROTECTED — 0 Inferences** |
| **India Benchmark (`india_real_world`)** | 100 | 269 | **PROTECTED — 0 Inferences** |

### Verified Class Map (5 Classes)
- `0`: `plastic_bottle`
- `1`: `plastic_wrapper_bag`
- `2`: `paper_cardboard`
- `3`: `glass_bottle_container`
- `4`: `metal_can`

---

## 4. Immutable Training Hyperparameters

- **Model:** YOLO11s (`9,414,735` parameters / `21.4 GFLOPs`)
- **Dataset:** `data/safaios_dataset_v10k/data.yaml`
- **Input Resolution (`imgsz`):** `640`
- **Batch Size:** `16`
- **Epochs:** `100`
- **Random Seed:** `42`
- **Optimizer:** `auto` (AdamW, `lr0=0.01`, `lrf=0.01`, `weight_decay=0.0005`)
- **Device:** `CUDA GPU 0`

---

## 5. Measured Validation Performance Metrics (`validation/` Split)

Validation metrics evaluated against the 1,000 validation images (2,463 ground-truth instances):

### Overall Model Performance
- **Precision:** `0.9822` (98.22%)
- **Recall:** `0.9824` (98.24%)
- **mAP@50:** `0.9944` (99.44%)
- **mAP@50-95:** `0.9840` (98.40%)
- **Peak Training mAP@50-95:** `0.9879` (Recorded at Epoch 71)

### Per-Class Detailed Performance Breakdown

| Class ID | Class Name | Instances | Precision | Recall | mAP@50 | mAP@50-95 |
|---:|---|---:|---:|---:|---:|---:|
| `0` | `plastic_bottle` | 438 | 0.9840 | 0.9840 | 0.9950 | 0.9824 |
| `1` | `plastic_wrapper_bag` | 557 | 0.9840 | 0.9800 | 0.9940 | 0.9859 |
| `2` | `paper_cardboard` | 471 | 0.9760 | 0.9870 | 0.9940 | 0.9842 |
| `3` | `glass_bottle_container` | 447 | 0.9910 | 0.9810 | 0.9950 | 0.9841 |
| `4` | `metal_can` | 550 | 0.9760 | 0.9800 | 0.9940 | 0.9837 |
| **All** | **Total Baseline** | **2,463** | **0.9822** | **0.9824** | **0.9944** | **0.9840** |

---

## 6. Hardware Throughput & Edge Deployment Profile

| Latency Metric | Measured Time (ms per frame) | Equivalent Rate |
|---|---:|---:|
| **Preprocess** | 1.4 ms | - |
| **Inference** | 5.9 ms | - |
| **Postprocess (NMS)** | 2.3 ms | - |
| **Total Frame Latency** | **9.6 ms** | **104.2 FPS** |

*Measured on NVIDIA RTX 4060 GPU at batch size 1, FP32/FP16 precision.*

---

## 7. Analysis & Interpretations

1. **Class Performance:**  
   - All 5 waste categories demonstrate exceptional baseline detection performance (`mAP@50` >= 99.4% across all classes).
   - `glass_bottle_container` achieved the highest Precision (99.10%), reflecting distinct visual boundaries and rigid transparency shapes.
   - `paper_cardboard` achieved the highest Recall (98.70%), showing strong robustness to deformation.
   - `metal_can` and `paper_cardboard` exhibited slight precision trade-offs (97.60%), likely due to minor specular reflection and crumpled edge ambiguity.

2. **Confusion Matrix Insights:**  
   - Inter-class confusion is near zero across the validation set.
   - Ground-truth background false-positive rate is under 1.8%, demonstrating clean background discrimination.

3. **Baseline Scope & Disclaimer:**  
   - This experiment establishes the pure **YOLO11s architectural baseline** on `safaios_dataset_v10k`.
   - High validation scores confirm dataset consistency and strong model convergence.
   - **Crucially:** These metrics evaluate benchmark performance on the curated validation distribution. Generalization claims to real-world Indian urban waste conditions (`india_real_world`) must be independently evaluated in subsequent Phase 3 / Phase 4 testing.

---

## 8. Preserved Artifacts & Output Paths

- **Best Checkpoint Weights:** [`runs/detect/runs/safaios/safaios_yolo11s_v10k_baseline/weights/best.pt`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/runs/detect/runs/safaios/safaios_yolo11s_v10k_baseline/weights/best.pt)
- **Last Checkpoint Weights:** [`runs/detect/runs/safaios/safaios_yolo11s_v10k_baseline/weights/last.pt`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/runs/detect/runs/safaios/safaios_yolo11s_v10k_baseline/weights/last.pt)
- **Training Results CSV:** [`runs/detect/runs/safaios/safaios_yolo11s_v10k_baseline/results.csv`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/runs/detect/runs/safaios/safaios_yolo11s_v10k_baseline/results.csv)
- **JSON Record:** [`reports/experiments/SAFAIOS-E001.json`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/reports/experiments/SAFAIOS-E001.json)
- **Markdown Record:** [`reports/experiments/SAFAIOS-E001.md`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/reports/experiments/SAFAIOS-E001.md)

---

## 9. Formal Status Declaration

**PHASE 3 — EXPERIMENT 001 COMPLETE**

**YOLO11s BASELINE ESTABLISHED**
