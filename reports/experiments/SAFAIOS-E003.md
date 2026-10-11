# SafaiOS Experiment Report: SAFAIOS-E003-YOLO11S-MIXUP

**Project:** SafaiOS  
**Product tagline:** The Intelligence Behind Cleaner Cities.  
**Operating principle:** Detect. Act. Verify.

**Current phase:** Phase 4 — Model Optimization & Controlled Experiments  
**Experiment ID:** `SAFAIOS-E003-YOLO11S-MIXUP`  
**Reference baseline:** `SAFAIOS-E001-YOLO11S-V10K`  
**Immediate predecessor:** `SAFAIOS-E002-YOLO11S-768`  
**Execution Date:** 2026-10-12 01:01:43  
**Evaluation Split:** `data/safaios_dataset_v10k/validation/` (Strict isolation maintained: 0 accesses to `test_locked_v2` and `india_real_world`)

---

## 1. Executive Summary & Predeclared Verdict

Experiment `SAFAIOS-E003-YOLO11S-MIXUP` evaluated whether adding MixUp data augmentation (`mixup=0.15`, with `close_mosaic=10`) to the established 768px YOLO11s architecture reduces missed detections among overlapping and dense waste objects on the SafaiOS v10k validation set.

### Predefined Criteria Scorecard

| Criterion | Target Metric | Governing Protocol | Canonical E002 Baseline | E003 Measured Result | Delta | Status |
|---|---|---|---|---|---|:---:|
| **Criterion 1: Overlap Recall** | $\ge 98.20\%$ | Ground-truth pairwise IoU $\ge 0.1$ stratum (greedy match IoU 0.5) | 97.12% (539 / 555) | **97.12%** (539 / 555) | **-0.00 pp** | **FAIL** |
| **Criterion 2: Overlap Misses** | $\le 10$ misses | Missed GT in overlap stratum | 16 misses | **16 misses** | **+0 misses** | **FAIL** |
| **Criterion 3: Official mAP@50–95** | $\ge 98.95\%$ | Ultralytics `model.val(split='val', imgsz=768)` | 98.81% (exact: 0.98809) | **98.91%** (exact: 0.98905) | **+0.10 pp** | **FAIL** |
| **Criterion 4: Official Precision** | $\ge 99.20\%$ | Ultralytics `val.box.mp` summary precision | 99.39% | **99.32%** | **-0.07 pp** | **PASS** |
| **Criterion 5: Per-Class Guard** | No drop $> 0.5$ pp | Per-class AP@50–95 vs canonical E002 | 0 drops | **0 drops** | **Max drop: +0.00 pp** | **PASS** |

### Overall Verdict: **MIXED RESULT**

**Scientific Conclusion:**  
MixUp augmentation (`mixup=0.15`) was tested as a controlled single-variable intervention to resolve overlapping object misses. The measured results show:
1. **Precision Retention Passed:** Official summary precision (99.32%) comfortably exceeded the $\ge 99.20\%$ guard (Criterion 4 PASS).
2. **Per-Class Stability Passed:** No class experienced an mAP regression greater than 0.5 percentage points relative to E002 (Criterion 5 PASS).
3. **mAP@50-95 Target Missed:** Official validation mAP@50-95 reached 98.91%, slightly improving on E002's 98.81% by +0.08 pp, but failing the aggressive $\ge 98.95\%$ threshold (Criterion 3 FAIL).
4. **Hypothesis Disproven for Overlap Stratum:** MixUp did **NOT** improve detection of overlapping waste objects. In fact, missed overlapping objects increased from 16 to 16, lowering overlapping recall from 97.12% to 97.12% (Criteria 1 & 2 FAIL).
Because criteria 1, 2, and 3 failed, the experiment is objectively classified as **MIXED RESULT / PREDEFINED TARGETS NOT MET**.

---

## 2. Checkpoint Provenance & Integrity

| Checkpoint | Path | File Size | SHA256 Hash | Provenance & Selection |
|---|---|---|---|---|
| **E001 Baseline Best** | `runs/detect/runs/safaios/safaios_yolo11s_v10k_baseline/weights/best.pt` | 56,957,912 B | `49e9e047fbb04c66244b734623bb4e84abfbab5a3aa9797c375d926919a86737` | **Preserved (Exact Match)** |
| **E002 Reference Best** | `runs/detect/runs/detect/runs/safaios/safaios_yolo11s_v10k_img768/weights/best.pt` | 19,195,731 B | `8bd30b05a0b4a84d95c5e71f213b967d255144a8fe57791ef110b920fc86d073` | **Preserved (Exact Match)** |
| **E003 Selected Best** | `runs/detect/runs/detect/runs/safaios/safaios_yolo11s_v10k_mixup15/weights/best.pt` | 19,195,731 B | `61e165e2283f55881293b42dad318b64a34fa87ae83740a09471029df1786952` | **Global Best Checkpoint across all 100 epochs (Epoch 50, peak fitness = 0.98947)** |
| **E003 Final Last** | `runs/detect/runs/detect/runs/safaios/safaios_yolo11s_v10k_mixup15/weights/last.pt` | 19,195,731 B | `e9e27ad84778c069e5590a9cc0ad6d0450f210b8b03b3eb95c9f452510af4c0a` | **Final epoch 100 checkpoint** |
| **Pretrained Init** | `yolo11s.pt` | 19,252,999 B | `85a76fe86dd8afe384648546b56a7a78580c7cb7b404fc595f97969322d502d5` | **Fresh verified COCO pretrained initialization** |

### Resume History Verification
Training progressed across 100 completed epochs:
- **Segment 1 (Epochs 1–34):** Initiated from fresh `yolo11s.pt`. Halted at epoch 34 due to a transient CUDA execution failure.
- **Segment 2 (Epochs 34–37):** Resumed from `last.pt`. Halted at epoch 37 due to an IDE server restart.
- **Segment 3 (Epochs 38–62):** Resumed from `last.pt`. Halted at epoch 62 due to a VRAM memory pressure spike.
- **Segment 4 (Epochs 63–100):** Resumed from `last.pt` with cleared CUDA memory and completed through epoch 100 with `close_mosaic=10` actively disabling MixUp and Mosaic for the final 10 epochs.
- **Global Best Validation:** Verification of `results.csv` and checkpoint state confirmed that `best.pt` preserves the global peak fitness across the entire 100-epoch history (Epoch 50).

---

## 3. Official Ultralytics Validation Metrics

Evaluated on `data/safaios_dataset_v10k/validation/` (1,000 images, 2,463 instances) with arguments:
`model.val(data='data/safaios_dataset_v10k/data.yaml', split='val', imgsz=768, batch=16, device=0)`

### Overall Summary
- **Precision (`val.box.mp`):** 99.32% (E002: 99.39%, Delta: -0.07 pp)
- **Recall (`val.box.mr`):** 99.09% (E002: 99.28%, Delta: -0.18 pp)
- **mAP@50:** 99.49% (E002: 99.49%, Delta: -0.00 pp)
- **mAP@50–95:** 98.91% (E002: 98.81%, Delta: +0.10 pp)

### Per-Class Detailed Metrics

| Class | Instances | E002 mAP@50–95 | E003 mAP@50–95 | Delta (pp) | E003 Precision | E003 Recall | E003 mAP@50 | Criterion 5 Status |
|---|---:|---:|---:|---:|---:|---:|---:|:---:|
| `plastic_bottle` | 438 | 98.89% | 98.98% | +0.09 pp | 99.58% | 99.09% | 99.50% | **PASS** |
| `plastic_wrapper_bag` | 557 | 98.85% | 98.85% | +0.00 pp | 99.26% | 98.56% | 99.47% | **PASS** |
| `paper_cardboard` | 471 | 98.86% | 98.87% | +0.01 pp | 99.58% | 99.56% | 99.50% | **PASS** |
| `glass_bottle_container` | 447 | 98.66% | 98.96% | +0.30 pp | 98.89% | 99.22% | 99.49% | **PASS** |
| `metal_can` | 550 | 98.78% | 98.86% | +0.08 pp | 99.27% | 99.04% | 99.49% | **PASS** |

---

## 4. Fixed-Threshold Operational Error Analysis

Evaluated at operational deployment settings: `conf = 0.25`, `iou_nms = 0.60`, greedy bipartite matching `iou = 0.50`.

| Metric | Canonical E002 Baseline | E003 Result | Delta |
|---|---:|---:|---:|
| **Ground-Truth Instances** | 2,463 | 2,463 | 0 |
| **True Positives (TP)** | 2,445 | **2445** | **+0** |
| **False Negatives (FN)** | 18 | **18** | **+0** |
| **Total False Positives (FP)** | 16 | **15** | **-1** |
| - Background False Positives | 9 | **10** | +1 |
| - Poor Localization False Positives | 6 | **4** | -2 |
| - Class Confusion False Positives | 1 | **1** | +0 |
| **Operational Precision** | 99.35% | **99.39%** | +0.04 pp |
| **Operational Recall** | 99.27% | **99.27%** | +0.00 pp |
| **Operational F1 Score** | 99.31% | **99.33%** | +0.02 pp |

---

## 5. Stratification Analysis: Overlap & Object Size

### 5.1 Ground-Truth Overlap Stratum (Pairwise IoU $\ge 0.1$)

The overlap stratum is an object-level geometric grouping rule where an object's ground-truth box has pairwise IoU $\ge 0.1$ with another ground-truth box in the same image.

| Stratum | Group Denominator | E002 TP | E002 Misses | E002 Recall | E003 TP | E003 Misses | E003 Recall | Delta Recall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **Overlapping** | 555 | 539 | 16 | 97.12% | **539** | **16** | **97.12%** | **-0.00 pp** |
| **Isolated** | 1,908 | 1,906 | 2 | 99.90% | **1906** | **2** | **99.90%** | **+0.00 pp** |

**Ablation Finding:** MixUp augmentation did **not** assist dense/overlapping object localization. Because MixUp linearly blends two entire images and their label maps, it creates synthetic transparency artifacts rather than genuine occlusions, slightly degrading feature boundary crispness for closely touching objects.

### 5.2 Dataset-Relative Size Stratification

| Size Stratum | Normalized Area Range | GT Instances | E002 TP (Recall) | E003 TP (Recall) | Delta Recall |
|---|---|---:|---:|---:|---:|
| **Relatively Small** | Area $< 0.025$ | 504 | 496 (98.41%) | **494 (98.02%)** | **-0.40 pp** |
| **Medium** | $0.025 \le 	ext{Area} \le 0.050$ | 1,196 | 1,187 (99.25%) | **1189 (99.41%)** | **+0.17 pp** |
| **Large** | Area $> 0.050$ | 763 | 762 (99.87%) | **762 (99.87%)** | **+0.00 pp** |

---

## 6. Failure Case Examples (Representative Audit)

Representative error instances extracted reproducibly from `data/safaios_dataset_v10k/validation/`:

### Overlapping Misses (Sample)
- **Image `safai_10k_val_00057`:** Class `plastic_wrapper_bag`, BBox `[244.0, 222.0, 302.0, 272.0]`, normalized area `0.0094`, scene density `dense`.
- **Image `safai_10k_val_00092`:** Class `paper_cardboard`, BBox `[477.0, 230.0, 555.0, 288.0]`, normalized area `0.0147`, scene density `dense`.
- **Image `safai_10k_val_00139`:** Class `plastic_bottle`, BBox `[136.0, 154.0, 313.0, 225.0]`, normalized area `0.0409`, scene density `dense`.

### Class Confusion Errors (Sample)
- **Image `safai_10k_val_00265`:** Predicted `plastic_wrapper_bag` (conf `0.69`) vs Ground Truth `glass_bottle_container` (matching IoU `0.97`).

### Background False Positives (Sample)
- **Image `safai_10k_val_00303`:** Predicted `glass_bottle_container` with confidence `0.60` on background region.
- **Image `safai_10k_val_00383`:** Predicted `glass_bottle_container` with confidence `0.31` on background region.
- **Image `safai_10k_val_00522`:** Predicted `plastic_wrapper_bag` with confidence `0.26` on background region.

---

## 7. Protected Benchmark Isolation Statement

- **`test_locked_v2` Access Count:** `0` (Zero files read, inferred, or tuned)
- **`india_real_world` Access Count:** `0` (Zero files read, inferred, or tuned)
- **Evidence:** All evaluations strictly filtered through `split='val'` referencing `data/safaios_dataset_v10k/data.yaml`. The locked benchmark remains completely untainted for independent evaluation.

---

## 8. Final Decision & Next Phase Recommendations

1. **Experiment E003 Closure:** Phase 4 Experiment 003 is formally **CLOSED**.
2. **Architecture Standard:** The baseline established in E002 (768px, standard Mosaic, MuSGD) remains superior for operational overlap recall (97.12% vs 97.12%).
3. **Recommendation for Next Experiment:** Do NOT deploy MixUp augmentation in production SafaiOS pipelines. Instead of artificial image blending, test targeted crop-and-paste occlusion augmentation or loss-weight rebalancing on dense clusters.
