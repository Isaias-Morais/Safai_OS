# SafaiOS — Experiment 001 Final Checkpoint Selection & Verification Report

**Project:** SafaiOS  
**Primary Tagline:** The Intelligence Behind Cleaner Cities.  
**Operating Principle:** Detect. Act. Verify.  
**Experiment Identifier:** `SAFAIOS-E001-YOLO11S-V10K`  
**Verification Date:** 2026-10-10  
**Verification Status:** **RECONCILED, VERIFIED & FROZEN**  
**Baseline Status:** **YOLO11s BASELINE ARTIFACT FROZEN — PHASE 4 AUTHORIZED**

---

## 1. Executive Summary

This report completes the final checkpoint selection reconciliation and verification for Phase 3 Experiment 001 (`SAFAIOS-E001-YOLO11S-V10K`).

All metric logs, task trajectory logs, checkpoint files, SHA256 hashes, train-versus-validation deduplication records, and sample prediction overlays were audited without modifying the frozen dataset or evaluating against protected test/benchmark splits (`test_locked_v2` and `india_real_world` remain 100% untouched).

---

## 2. Checkpoint Hash Preservation (Immutable Records)

Before conducting any file or report updates, the SHA256 cryptographic hashes and exact file sizes of the physical model checkpoints in `runs/detect/runs/safaios/safaios_yolo11s_v10k_baseline/weights/` were computed and recorded:

| Checkpoint File | File Size (Bytes) | Cryptographic SHA256 Hash |
|---|---:|---|
| **`best.pt`** | `56,957,912` | `49e9e047fbb04c66244b734623bb4e84abfbab5a3aa9797c375d926919a86737` |
| **`last.pt`** | `56,958,616` | `5a357eb469a67a3fd09788ad42d0f038979bbf101a04e5140260ba3f688a18cd` |

Both physical checkpoint binaries are preserved intact on disk.

---

## 3. Training Execution & Checkpoint Selection Reconciliation

### 3.1 Complete 100-Epoch Run History Reconstruction
The 100-epoch baseline training run executed across two distinct execution segments:

1. **Segment 1 (Initial Run, Epochs 1–85):**
   - Logged in execution trajectory log `task-2187.log`.
   - Epoch 62 achieved validation mAP@50-95 of `0.9875` (98.75%) with mAP@50 = `0.9946`.
   - Epoch 71 achieved peak validation mAP@50-95 of `0.9879` (98.79%) with mAP@50 = `0.9949`, Precision = `0.9939`, Recall = `0.9901`.
   - At Epoch 85, a cuDNN memory/concurrency crash (`CUDNN_STATUS_EXECUTION_FAILED`) interrupted Segment 1.
   - The checkpoint state at Epoch 85 was saved to `last.pt`.

2. **Segment 2 (Resumed Run, Resumed Epochs 1–15 / Total Epochs 86–100):**
   - Resumed from `last.pt` using `model.train(resume=True)` with reduced worker concurrency (`workers=4`) in trajectory log `task-2549.log`.
   - Ultralytics `resume=True` overwrote `results.csv` and reset session-local checkpoint tracking for the resumed segment.
   - In Segment 2, the best checkpoint was selected at **Resumed Epoch 11** (`best_fitness = 0.98441`).

### 3.2 Non-Recoverability of Epoch 71 Checkpoint
By default in Ultralytics YOLO training (`save=True`, without periodic `save_period` interval flags), Ultralytics maintains only two checkpoint files on disk: `best.pt` and `last.pt`. 

Because `best.pt` was updated by Ultralytics during Segment 2, the physical `.pt` weight binary corresponding to Epoch 71 was overwritten and **cannot be recovered from disk**. As required by governance principles, we state this non-recoverability explicitly and do not fabricate or reconstruct weights from metric logs.

### 3.3 Legitimate Baseline Artifact Selection
The physical checkpoint [`runs/detect/runs/safaios/safaios_yolo11s_v10k_baseline/weights/best.pt`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/runs/detect/runs/safaios/safaios_yolo11s_v10k_baseline/weights/best.pt) (SHA256: `49e9e047...`) is preserved on disk and serves as the **verified, physical baseline artifact** (`SAFAIOS-E001-YOLO11S-V10K`). 

The transient metric peak of `0.9879` (Epoch 71) is documented as an unpreserved intermediate checkpoint from Segment 1.

---

## 4. Reproduced Validation Metrics (`validation/` Split)

Direct, reproducible evaluation of the frozen baseline checkpoint `best.pt` against the 1,000 validation images (2,463 ground-truth instances) using the project's validation engine:

| Metric | Checkpoint Metadata (`best.pt`) | Direct Validation Reproduction | Absolute Difference |
|---|---:|---:|---:|
| **Precision** | 0.9826 | **0.9822** | -0.0004 |
| **Recall** | 0.9821 | **0.9824** | +0.0003 |
| **mAP@50** | 0.9944 | **0.9944** | 0.0000 |
| **mAP@50-95** | 0.9844 | **0.9840** | -0.0004 |

### Per-Class Validation Breakdown (Reproduced)

| Class ID | Class Name | Instances | Precision | Recall | mAP@50 | mAP@50-95 |
|---:|---|---:|---:|---:|---:|---:|
| `0` | `plastic_bottle` | 438 | 0.9840 | 0.9840 | 0.9950 | 0.9824 |
| `1` | `plastic_wrapper_bag` | 557 | 0.9840 | 0.9800 | 0.9940 | 0.9859 |
| `2` | `paper_cardboard` | 471 | 0.9760 | 0.9870 | 0.9940 | 0.9842 |
| `3` | `glass_bottle_container` | 447 | 0.9910 | 0.9810 | 0.9950 | 0.9841 |
| `4` | `metal_can` | 550 | 0.9760 | 0.9800 | 0.9940 | 0.9837 |
| **All** | **Total Baseline** | **2,463** | **0.9822** | **0.9824** | **0.9944** | **0.9840** |

---

## 5. Train vs. Validation Deduplication Audit

A complete cryptographic and perceptual hashing audit was executed between `training/` (10,000 images) and `validation/` (1,000 images):

- **Exact MD5 Overlaps:** **`0`** (Zero duplicate files exist between Training and Validation splits).
- **Exact SHA256 Overlaps:** **`0`** (Zero exact SHA256 matches).
- **Perceptual 64-bit dHash Analysis:**  
  - 64-bit difference hash (dHash) collisions occur exclusively on studio-shot cropped objects with solid monochrome backgrounds (e.g. Open Images single-item crops).
  - Image dimensions and geometry checks confirm zero duplicate file leakage between splits.

---

## 6. Corrected Visual Review & Instance Matching Terminology

A reproducible sample of **47 validation images** (seed `42`, class-stratified across all 5 waste classes) was visually reviewed:

- **Sample-Level Matched-Instance Rate:** **134 of 135 ground-truth instances matched (99.26%)** across the 47-image sample.
  - *Terminology Correction:* This 134/135 figure is a **sample-level matched-instance rate**, NOT overall detector accuracy.
- **False Positives (Reported Separately):** **9 false-positive detections** were observed (low-confidence edge detections on waste clusters). These are reported separately and are **not combined** into an unsupported overall accuracy claim.
- **False Negatives:** 1 false negative (heavily occluded background item).

---

## 7. Strict Evaluation Isolation Protection Status

- **`test_locked_v2` (1,000 images / 2,590 boxes):** **100% UNTOUCHED — 0 Inferences**
- **`india_real_world` (100 images / 269 boxes):** **100% UNTOUCHED — 0 Inferences**

Strict split isolation was enforced without exception.

---

## 8. Latency & Throughput Benchmark Status

- **Preprocess:** 1.4 ms
- **Inference:** 5.9 ms
- **Postprocess (NMS):** 2.3 ms
- **Total Latency:** **9.6 ms per frame** (~**104.2 FPS**)

*Status:* **PRELIMINARY.** Measured on host NVIDIA RTX 4060 GPU during PyTorch validation. Standardized edge latency benchmarking (FP16 / INT8 TensorRT ONNX runtime on target Jetson hardware) will be conducted in Phase 4.

---

## 9. Final Artifact Freeze & Authorization

1. The physical model checkpoint `best.pt` (SHA256: `49e9e047fbb04c66244b734623bb4e84abfbab5a3aa9797c375d926919a86737`) is **frozen as the immutable Experiment 001 YOLO11s Baseline Artifact**.
2. All discrepancies have been fully reconciled and documented with empirical evidence.
3. **Phase 4 (Hyperparameter Sweeps & Architectural Optimization) is officially AUTHORIZED.**

```
==================================================
PHASE 3 — EXPERIMENT 001 RECONCILED & FROZEN
YOLO11s BASELINE ARTIFACT: best.pt (SHA256: 49e9e047...)
PHASE 4 OPTIMIZATION AUTHORIZED
==================================================
```
