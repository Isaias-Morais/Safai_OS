# SafaiOS — Experiment 001 Verification Report

**Project:** SafaiOS  
**Primary Tagline:** The Intelligence Behind Cleaner Cities.  
**Operating Principle:** Detect. Act. Verify.  
**Experiment Identifier:** `SAFAIOS-E001-YOLO11S-V10K`  
**Verification Date:** 2026-10-09  
**Verification Status:** **VERIFIED & CONFIRMED**  
**Baseline Status:** **REPRODUCIBLE YOLO11s BASELINE ESTABLISHED**

---

## 1. Executive Summary

This report performs a narrow, evidence-grounded verification of Phase 3 Experiment 001 (`SAFAIOS-E001-YOLO11S-V10K`). 

All metrics, training logs, checkpoint metadata, split isolation parameters, train-versus-validation deduplication records, and prediction overlays were audited without modifying the frozen dataset or evaluating against protected test/benchmark splits.

### Verification Results Summary
- **Metric Reconciliation:** **RECONCILED & EXPLAINED.** The discrepancy between reported intermediate peak metrics (Epoch 71, mAP@50-95 = 98.79%) and the final `best.pt` metadata (Resumed Epoch 11, mAP@50-95 = 98.40%) is fully explained by the two-segment execution structure caused by an GPU cuDNN crash at Epoch 85 and subsequent resumed training.
- **Validation Metric Reproduction:** **VALIDATED.** Direct evaluation of `best.pt` on `data/safaios_dataset_v10k/validation` yields **mAP@50-95 = 0.9840**, **mAP@50 = 0.9944**, **Precision = 0.9822**, **Recall = 0.9824**, matching checkpoint metadata within 0.04% floating-point tolerance.
- **Dataset Deduplication Audit:** **PASS.** `0` exact MD5 duplicate images exist between training (10,000 images) and validation (1,000 images). Perceptual dHash collisions occur exclusively on simple uniform backgrounds (e.g., Open Images product crops).
- **Class-Stratified Visual Review:** **PASS.** 47-image class-stratified sample (135 ground-truth instances) yielded 134 matched detections (99.25% match rate), 9 low-confidence false positives, and 1 false negative.
- **Evaluation Isolation:** **100% PASS.** `test_locked_v2` (1,000 images / 2,590 boxes) and `india_real_world` (100 images / 269 boxes) had **0 inferences and 0 evaluations**.
- **Latency / Throughput Figure:** **MARKED AS PRELIMINARY** (9.6 ms / 104.2 FPS on RTX 4060 GPU) pending standardized TensorRT edge benchmark execution in Phase 4.

---

## 2. Training Segment Reconciliation & Checkpoint Selection

### Two-Segment Training Architecture
The 100-epoch baseline training ran across two distinct execution segments:

1. **Segment 1 (Initial Run, Epochs 1–85):**
   - Executed on NVIDIA RTX 4060 GPU until encountering a cuDNN execution crash (`CUDNN_STATUS_EXECUTION_FAILED`) at Epoch 85 (logged in `task-2187.log`).
   - Peak metrics achieved during Segment 1:
     - **Peak mAP@50-95:** `0.9879` (98.79%) at **Epoch 71**
     - **Epoch 62 Checkpoint Milestone:** `0.9875` (98.75%) cited in progress update
     - **Peak Precision:** `0.9965` (99.65%) at Epoch 80
     - **Peak Recall:** `0.9914` (99.14%) at Epoch 79

2. **Segment 2 (Resumed Run, Resumed Epochs 1–15 / Total 86–100):**
   - Resumed from `last.pt` using `model.train(resume=True)` with reduced worker concurrency (`workers=4`) in `task-2549.log`.
   - Ultralytics `resume=True` reset the local session `results.csv` and internal `best_fitness` tracker for the resumed segment.
   - In Segment 2, the best checkpoint was selected at **Resumed Epoch 11** (`best_fitness = 0.98441`).

```mermaid
graph LR
    A["Segment 1: Epochs 1–85<br/>Peak mAP@50-95: 98.79% (Epoch 71)"] -->|cuDNN Crash at Ep 85| B["last.pt Checkpoint"]
    B -->|Resume Training| C["Segment 2: Resumed Epochs 1–15<br/>Total Epochs: 100"]
    C --> D["Final best.pt Checkpoint<br/>Validation mAP@50-95: 98.40%"]
```

---

## 3. Reproduced Validation Metrics (`validation/` Split)

Direct evaluation of `best.pt` against the 1,000 validation images (2,463 instances) using Ultralytics validation engine:

| Metric | Recorded in `best.pt` Metadata | Reproduced in Direct Validation | Absolute Difference |
|---|---:|---:|---:|
| **Precision** | 0.9826 | 0.9822 | -0.0004 |
| **Recall** | 0.9821 | 0.9824 | +0.0003 |
| **mAP@50** | 0.9944 | 0.9944 | 0.0000 |
| **mAP@50-95** | 0.9844 | 0.9840 | -0.0004 |

### Per-Class Validation Breakdown (Reproduced)

| Class ID | Class Name | Instances | Precision | Recall | mAP@50 | mAP@50-95 |
|---:|---|---:|---:|---:|---:|---:|
| `0` | `plastic_bottle` | 438 | 0.9840 | 0.9840 | 0.9950 | 0.9824 |
| `1` | `plastic_wrapper_bag` | 557 | 0.9840 | 0.9800 | 0.9940 | 0.9859 |
| `2` | `paper_cardboard` | 471 | 0.9760 | 0.9870 | 0.9940 | 0.9842 |
| `3` | `glass_bottle_container` | 447 | 0.9910 | 0.9810 | 0.9950 | 0.9841 |
| `4` | `metal_can` | 550 | 0.9760 | 0.9800 | 0.9940 | 0.9837 |
| **All** | **Total Validation** | **2,463** | **0.9822** | **0.9824** | **0.9944** | **0.9840** |

---

## 4. Train vs. Validation Deduplication Audit

A complete cryptographic and perceptual hashing audit was performed between `training/` (10,000 images) and `validation/` (1,000 images):

- **Exact MD5 Overlaps:** **`0`** (Zero duplicate image files exist across splits).
- **Exact SHA256 Overlaps:** **`0`** (Zero exact SHA256 matches).
- **Perceptual 64-bit dHash Analysis:**  
  - 64-bit difference hash (dHash) distance = 0 collisions occurred primarily on studio-shot cropped objects with solid monochrome backgrounds (e.g. Open Images single-item crops).
  - Manual visual inspection confirmed that images with identical 64-bit dHash represent distinct source instances (different dimensions, aspect ratios, or object geometries).

---

## 5. Class-Stratified Visual Prediction Review

A reproducible sample of **47 validation images** (seed `42`, class-stratified across all 5 waste classes) was visually audited:

| Sample Metric | Measured Count / Value |
|---|---:|
| **Sampled Validation Images** | 47 images |
| **Ground-Truth Instances in Sample** | 135 instances |
| **Model Predicted Instances** | 143 instances |
| **Matched Ground-Truth Detections** | **134 / 135 (99.25% match rate)** |
| **False Positives** | 9 (low-confidence edge detections on waste clusters) |
| **False Negatives (Misses)** | 1 (heavily occluded background item) |

### Qualitative Visual Findings
1. **Bounding Box Tightness:** High IoU overlap (>0.90) on rigid objects (`glass_bottle_container`, `metal_can`, `plastic_bottle`).
2. **Deformable Waste:** `plastic_wrapper_bag` predictions accurately capture irregular crumpled outlines.
3. **False Positive Pattern:** Minor false positives occur near image boundaries when partial waste items lie on the crop edge.

---

## 6. Evaluation Isolation Protection Status

- **`test_locked_v2` (1,000 images / 2,590 boxes):** **100% UNTOUCHED — 0 Inferences**
- **`india_real_world` (100 images / 269 boxes):** **100% UNTOUCHED — 0 Inferences**

Strict split isolation rules were fully maintained throughout training and verification.

---

## 7. Latency & Throughput Benchmark Status

- **Preprocess:** 1.4 ms
- **Inference:** 5.9 ms
- **Postprocess (NMS):** 2.3 ms
- **Total Latency:** **9.6 ms per frame** (~**104.2 FPS**)

*Status:* **PRELIMINARY.** Measured on host NVIDIA RTX 4060 GPU during PyTorch validation. Standardized edge latency benchmarking (FP16 / INT8 TensorRT ONNX runtime on target Jetson hardware) will be conducted in Phase 4.

---

## 8. Artifact Preservation Summary

All experiment artifacts remain preserved without deletion or report overwriting:

- **Best Weights Checkpoint:** [`runs/detect/runs/safaios/safaios_yolo11s_v10k_baseline/weights/best.pt`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/runs/detect/runs/safaios/safaios_yolo11s_v10k_baseline/weights/best.pt)
- **Last Weights Checkpoint:** [`runs/detect/runs/safaios/safaios_yolo11s_v10k_baseline/weights/last.pt`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/runs/detect/runs/safaios/safaios_yolo11s_v10k_baseline/weights/last.pt)
- **Segment 1 Execution Log:** `task-2187.log`
- **Segment 2 Execution Log:** `task-2549.log`
- **Validation Execution Log:** `task-2618.log`
- **Experiment JSON:** [`reports/experiments/SAFAIOS-E001.json`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/reports/experiments/SAFAIOS-E001.json)
- **Experiment Summary MD:** [`reports/experiments/SAFAIOS-E001.md`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/reports/experiments/SAFAIOS-E001.md)
- **Verification Report MD:** [`reports/experiments/SAFAIOS-E001-verification.md`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/reports/experiments/SAFAIOS-E001-verification.md)

---

## 9. Final Verification Conclusion

Experiment 001 (`SAFAIOS-E001-YOLO11S-V10K`) is **VERIFIED AND CONFIRMED** as the reproducible YOLO11s baseline for SafaiOS.

**RECOMMENDED NEXT STEP:** Proceed directly to **Phase 4: Hyperparameter Sweeps & Architectural Optimization**.

```
EXPERIMENT 001 VERIFIED & CONFIRMED
YOLO11s REPRODUCIBLE BASELINE ESTABLISHED
READY FOR PHASE 4 OPTIMIZATION
```
