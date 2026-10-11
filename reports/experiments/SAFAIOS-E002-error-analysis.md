# SafaiOS — Phase 4: Validation Error Analysis & Comparison (E001 vs. E002)

**Project:** SafaiOS  
**Tagline:** The Intelligence Behind Cleaner Cities.  
**Operating Principle:** Detect. Act. Verify.  
**Reference Baseline:** `SAFAIOS-E001-YOLO11S-V10K` (640px)  
**Latest Ablation:** `SAFAIOS-E002-YOLO11S-768` (768px)  
**Dataset Split Evaluated:** `data/safaios_dataset_v10k/validation/` (1,000 images, 2,463 ground-truth objects)  
**Execution Date:** October 11, 2026  

---

## Executive Summary

This report delivers an in-depth empirical error analysis comparing the frozen baseline detector **E001** (`best.pt`, 640px) against the resolution ablation detector **E002** (`best.pt`, 768px) on the 1,000-image validation split of `safaios_dataset_v10k`.

The analysis was conducted under strict protocol:
- Both model checkpoints were verified by their SHA256 hashes before evaluation.
- Neither `test_locked_v2` nor `india_real_world` was accessed or evaluated at any point (**100% UNTOUCHED**).
- Evaluation utilized identical, documented evaluation parameters (`split='val'`, IoU threshold = 0.5 for true-positive matching, operational confidence threshold = 0.25).
- Error cases were stratified by ground-truth bounding-box size, class, scene object density, and object overlap.

### Core Discoveries:
1. **Dramatic False Positive Reduction:** E002 cut total operational false positives by **73.3%** (from 60 in E001 down to 16 in E002). Background false alarms (hallucinating trash on non-waste pavement, curbs, or foliage) dropped by **82.4%** (from 51 down to 9).
2. **Per-Class Precision Nuance:** Overall class-averaged precision improved by +1.17% (from 98.22% to 99.39%), with precision improving in 4 of 5 classes. However, `glass_bottle_container` precision slightly declined from **99.10%** in E001 to **98.91%** in E002 (-0.19%). Conversely, recall and mAP@50–95 improved across **all five classes**.
3. **Evaluation of the Small-Object Hypothesis:**
   - Under standard COCO absolute small-object threshold (`area < 32^2 px` in 640x640 normalized space, or `area_norm < 0.0025`), the validation set contains **0** objects (minimum normalized area is 0.0083). Thus, under strict COCO terminology, the small-object claim cannot be established.
   - When stratified by dataset-relative tiers (`area_norm < 0.025`, lower quartile of SafaiOS dataset): E002 improved recall from **98.02% (494/504)** to **98.41% (496/504)** (+0.40%), recovering 4 small/distant items completely missed by E001.
4. **Ground-Truth Bounding-Box-Overlap Stratum (Geometric Proxy):**
   - Objects with pairwise bounding-box IoU $< 0.1$ achieved near-perfect detection: **99.90% recall** (1,906 / 1,908 TP; only 2 FN).
   - In contrast, objects in the **ground-truth bounding-box-overlap stratum** (pairwise IoU $\ge 0.1$) exhibited reduced recall: **97.12% recall** (539 / 555 TP; **16 FN**).
   - **Crucially: 16 out of 18 (88.9%) of all remaining False Negatives in E002 occur within this overlapping-box stratum.**
   - *Methodological Note:* Pairwise 2D bounding-box IoU $\ge 0.1$ serves strictly as a **geometric proxy**, not direct physical proof of 3D physical occlusion or mechanical causation.
5. **Metric Provenance & Reconciliation:**
   - The canonical official validation performance of the frozen E002 checkpoint (`best.pt`, SHA256: `8bd30b05a0b4a84d95c5e71f213b967d255144a8fe57791ef110b920fc86d073`) evaluated on the validation split is **mAP@50–95 = 98.81%** (exact float: `0.9880925887293113`), Precision = 99.39%, Recall = 99.28%, mAP@50 = 99.49%.
   - E002's earlier 98.90% figure was rounded from an intermediate epoch log (epoch 87 logged `mAP50-95(B) = 0.98867`, displayed as `0.989` in earlier summary tables), whereas 98.81% (`0.9880925887293113`) is the directly validated metric obtained by running `model.val(data=..., split='val', imgsz=768)` on the frozen selected `best.pt` checkpoint. The difference reflects the distinction between an intermediate in-training epoch evaluation log and the standalone post-training validation of the saved checkpoint weights, rather than arithmetic rounding alone.

---

## 1. Checkpoint Verification & Provenance

Both checkpoints were verified via cryptographic SHA256 hash before loading:

| Experiment | Checkpoint Path | Verified SHA256 Hash | Status |
| :--- | :--- | :--- | :---: |
| **E001 Baseline** | `runs/detect/runs/safaios/safaios_yolo11s_v10k_baseline/weights/best.pt` | `49e9e047fbb04c66244b734623bb4e84abfbab5a3aa9797c375d926919a86737` | **FROZEN & VERIFIED** |
| **E002 Ablation** | `runs/detect/runs/detect/runs/safaios/safaios_yolo11s_v10k_img768/weights/best.pt` | `8bd30b05a0b4a84d95c5e71f213b967d255144a8fe57791ef110b920fc86d073` | **FROZEN & VERIFIED** |

---

## 2. Fair Quantitative Comparison (Official Validation Split)

### 2.1 Official Ultralytics Validation Metrics (`model.val`)

Both models evaluated on `data/safaios_dataset_v10k/validation/images` (`split='val'`, standard multi-threshold evaluation):

| Metric | E001 Baseline (640px) | E002 Ablation (768px) | Absolute Delta | Relative Gain |
| :--- | :---: | :---: | :---: | :---: |
| **Precision** | 98.22% | **99.39%** | **+1.17%** | +1.19% |
| **Recall** | 98.24% | **99.28%** | **+1.04%** | +1.06% |
| **mAP@50** | 99.44% | **99.49%** | **+0.05%** | +0.05% |
| **mAP@50–95** | 98.40% | **98.81%** | **+0.41%** | +0.42% |

### 2.2 Per-Class Detailed Breakdown

| Class ID | Class Name | Ground Truth Count | E001 Prec | E002 Prec | E001 Rec | E002 Rec | E001 mAP50-95 | E002 mAP50-95 | mAP Delta |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | `plastic_bottle` | 438 | 98.42% | **99.54%** | 98.40% | **99.25%** | 98.24% | **98.89%** | **+0.65%** |
| 1 | `plastic_wrapper_bag` | 557 | 98.38% | **99.61%** | 97.99% | **98.74%** | 98.58% | **98.85%** | **+0.27%** |
| 2 | `paper_cardboard` | 471 | 97.56% | **99.71%** | 98.73% | **99.79%** | 98.42% | **98.86%** | **+0.44%** |
| 3 | `glass_bottle_container` | 447 | **99.10%** | 98.91% | 98.12% | **99.33%** | 98.41% | **98.66%** | **+0.25%** |
| 4 | `metal_can` | 550 | 97.64% | **99.17%** | 97.95% | **99.27%** | 98.37% | **98.78%** | **+0.41%** |
| **All** | **Overall** | **2,463** | **98.22%** | **99.39%** | **98.24%** | **99.28%** | **98.40%** | **98.81%** | **+0.41%** |

---

## 3. Operational Threshold Error Matching (`conf=0.25`, `iou=0.6`)

### 3.1 Methodological Distinction: Official vs. Operational Metrics
- **Official Metrics (Section 2):** Derived from standard `model.val()`:
  - **mAP (mAP@50 and mAP@50–95):** Area under the Precision-Recall curve computed across multi-threshold IoU levels (COCO standard IoU 0.50:0.95:0.05).
  - **Official Summary Precision & Recall:** Point estimates evaluated at the optimal confidence threshold that maximizes the F1 score on the validation curve, macro-averaged across classes (`val.box.mp` and `val.box.mr`).
- **Operational Metrics (Section 3):** Computed at a fixed operational deployment threshold (`conf=0.25`, NMS `iou=0.60`, matching threshold `iou=0.50`) via greedy bipartite one-to-one matching between predictions and ground-truth bounding boxes. Operational metrics reflect discrete deployment counts and operational rates:
  - $\text{Operational Precision} = \frac{\text{TP}}{\text{TP} + \text{FP}} = \frac{2445}{2445 + 16} = 99.35\%$
  - $\text{Operational Recall} = \frac{\text{TP}}{\text{TP} + \text{FN}} = \frac{2445}{2445 + 18} = 99.27\%$
  - $\text{Operational F1} = 2 \times \frac{\text{Prec} \times \text{Rec}}{\text{Prec} + \text{Rec}} = 99.31\%$

Using standard deployment inference parameters (`conf=0.25`, `iou=0.6`, matching threshold IoU = 0.5):

| Error Category | E001 Baseline (640px) | E002 Ablation (768px) | Change | Interpretation |
| :--- | :---: | :---: | :---: | :--- |
| **True Positives (TP)** | 2,442 | **2,445** | +3 | More valid ground truth objects detected |
| **False Negatives (FN)** | 21 | **18** | **-3 (-14.3%)** | Fewer missed trash instances |
| **Total False Positives (FP)** | 60 | **16** | **-44 (-73.3%)** | Huge drop in spurious detections |
| ↳ **Background FP** | 51 | **9** | **-42 (-82.4%)** | Higher resolution eliminates pavement texture confusion |
| ↳ **Poor Localization FP** | 9 | **6** | -3 (-33.3%) | Sharper boundary regressions |
| ↳ **Class Confusion FP** | 0 | **1** | +1 | 1 metal can confused with plastic wrapper |
| **Operational Precision** | 97.60% | **99.35%** | **+1.75%** | Much cleaner predictions |
| **Operational Recall** | 99.15% | **99.27%** | **+0.12%** | Near complete coverage |
| **Operational F1** | 98.37% | **99.31%** | **+0.94%** | Balanced operational gain |

### 3.2 Confusion Matrix (E002 @ 768px)

Columns = Predicted Classes (0..4, Background=5); Rows = Ground Truth Classes (0..4, Background=5):

| Ground Truth \ Predicted | `plastic_bottle` (0) | `plastic_wrapper_bag` (1) | `paper_cardboard` (2) | `glass_bottle` (3) | `metal_can` (4) | Background / Missed (5) | Total GT |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **0: plastic_bottle** | **435** | 0 | 0 | 0 | 0 | 3 | 438 |
| **1: plastic_wrapper_bag** | 0 | **551** | 0 | 0 | 0 | 6 | 557 |
| **2: paper_cardboard** | 0 | 0 | **470** | 0 | 0 | 1 | 471 |
| **3: glass_bottle_container** | 0 | 0 | 0 | **444** | 0 | 3 | 447 |
| **4: metal_can** | 0 | 1 | 0 | 0 | **545** | 5 | 550 |
| **5: Background False Positives**| 3 | 0 | 1 | 3 | 2 | — | 9 FP |

*Note: Class confusion is remarkably low in both models (only 1 occurrence in E002: a crumpled foil can detected as a wrapper).*

---

## 4. Difficult Object Stratification

### 4.1 Bounding Box Size Stratification

We investigated object size using two distinct definitions:

1. **Standard COCO Absolute Thresholds** (`area_norm < 0.0025` corresponding to $<32^2$ pixels on 640x640):
   - **Ground Truth Count:** **0 objects**.
   - **Small-Object Claim Assessment:** The claim that 768px specifically improved "standard COCO small objects" is **NOT SUPPORTED**, because the dataset does not contain objects below 0.0025 normalized area (minimum is 0.0083).
2. **Dataset-Relative Size Tiers** (Empirical distribution of SafaiOS municipal waste objects):
   - **Relatively Small** (`area_norm < 0.025`, $<2.5\%$ image area, 504 items):
     - E001 Recall: 98.02% (494 / 504)
     - E002 Recall: **98.41%** (496 / 504) $\rightarrow$ **+0.40% gain**.
     - 4 previously missed small items were recovered by E002 (`safai_10k_val_00163`, `safai_10k_val_00758`, `safai_10k_val_00343`, `safai_10k_val_00062`).
   - **Medium** (`0.025 \le area_norm \le 0.050`, 2.5% to 5.0% image area, 1,196 items):
     - E001 Recall: 99.16% (1,186 / 1,196)
     - E002 Recall: **99.25%** (1,187 / 1,196) $\rightarrow$ **+0.08% gain**.
   - **Large** (`area_norm > 0.050`, $>5.0\%$ image area, 763 items):
     - E001 Recall: 99.87% (762 / 763)
     - E002 Recall: 99.87% (762 / 763) $\rightarrow$ **0.00% delta** (both models missed only 1 object).

### 4.2 Scene Density Stratification (Object Count per Image)

| Density Tier | Objects in Image | Total GT Boxes | E001 Recall | E002 Recall | E002 False Negatives |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Single** | 1 | 261 | **100.0%** (261/261) | **100.0%** (261/261) | 0 |
| **Sparse** | 2 – 3 | 1,250 | 99.36% (1,242/1,250) | 99.36% (1,242/1,250) | 8 |
| **Dense** | $\ge 4$ | 952 | 98.63% (939/952) | **98.95%** (942/952) | 10 |

*Dense scenes exhibit almost double the miss rate of sparse scenes.*

### 4.3 Ground-Truth Bounding-Box-Overlap Stratum (Geometric Proxy)

We measured the maximum pairwise 2D IoU of each ground-truth bounding box with all other ground-truth bounding boxes within the same image:

| Overlap Stratum | Pairwise IoU | Total GT Boxes | E001 Recall | E002 Recall | E002 Missed Objects |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Isolated Objects** | $< 0.1$ | 1,908 | **100.0%** (1,908/1,908) | **99.90%** (1,906/1,908) | 2 |
| **Ground-Truth Bounding-Box-Overlap Stratum** | $\ge 0.1$ | 555 | 96.22% (534/555) | **97.12%** (539/555) | **16** |

> [!CRITICAL]
> **Key Finding:**  
> **16 out of 18 (88.9%) of all remaining False Negatives in E002 occur within the ground-truth bounding-box-overlap stratum.**  
> *Methodological Caveat:* Pairwise bounding-box IoU $\ge 0.1$ is an empirical **geometric proxy** based on planar bounding-box overlap, **not proof of physical 3D occlusion or mechanical causation**. While overlapping 2D boxes frequently correlate with visual clutter and partial occlusion in street scenes, the metric strictly measures bounding-box intersection.

---

## 5. Review of Representative Failure Cases

Visualizations were rendered with fixed random seed `seed=42` and stored in `reports/figures/error_analysis/`:

1. **Overlapping False Negatives:**
   - `fn_sample_1_safai_10k_val_00057.jpg`: A `metal_can` closely overlapping a `plastic_wrapper_bag`; the model detects the bag with high confidence but misses the can underneath.
   - `fn_sample_2_safai_10k_val_00092.jpg`: Multi-object cluster where two adjacent crushed bottles share high bounding box intersection; only the larger bottle is regressed.
   - `fn_sample_3_safai_10k_val_00096.jpg`: Dense pile of wrappers; internal small wrapper boundary swallowed by the larger wrapper envelope.
2. **Small Relative Object Recovery in E002:**
   - `small_recovered_1_safai_10k_val_00163.jpg`: Distant small plastic bottle near curb; E001 failed to generate any anchor above 0.25 confidence at 640px, but E002 regressed it cleanly at 768px with 0.74 confidence.
   - `small_recovered_2_safai_10k_val_00758.jpg`: Flattened can in gravel; recovered cleanly at 768px.
3. **Class Confusion Example:**
   - `confusion_sample_1_safai_10k_val_00657.jpg`: Heavily crumpled metallic snack wrapper predicted as `plastic_wrapper_bag` (confidence 0.62) while ground truth labeled as `metal_can`. Highly ambiguous boundary.

---

## 6. Synthesis & Recommended Next Step (Experiment 003)

### Why 768px Must Be Retained
E002 at 768px demonstrated marked improvements over the E001 baseline:
- +1.17% overall Precision (improving in 4 of 5 classes; glass container precision saw a minor shift from 99.10% to 98.91% while recall and mAP@50-95 improved across all 5 classes)
- +1.04% overall Recall (improving across all 5 classes)
- +0.41% mAP@50-95 (improving across all 5 classes)
- 73.3% reduction in False Positives (82.4% reduction in background false alarms)
- Better feature resolution for small/distant waste items (+0.40% recall in lower size tier).

### What Is the Remaining Bottleneck?
The remaining error surface is **concentrated in the ground-truth bounding-box-overlap stratum (88.9% of all misses)**.
Both E001 and E002 were trained with **`mixup: 0.0`** and **`copy_paste: 0.0`**. Mosaic augmentation stitches 4 distinct scenes into 4 quadrants, but does NOT blend or superimpose items.

### Recommended Single Controlled Intervention for Experiment 003:
**Test MixUp Augmentation (`mixup: 0.15`) as an Empirical Intervention**

- **Empirical Hypothesis (Testable Intervention, Not a Guaranteed Fix):**  
  MixUp is framed as a **testable empirical hypothesis**, not a guaranteed fix for overlap errors. By linearly blending training image pairs, MixUp creates synthetic overlapping instances with semi-transparent boundaries. Whether this synthetic augmentation translates to improved discrimination of real occluded waste instances requires rigorous empirical verification against the frozen validation split.
- **Ultralytics Augmentation Semantics & Scheduling:**  
  In the installed version (`ultralytics 8.4.174`):
  - `mixup=0.15` indicates an independent **15% probability per sample batch** of applying MixUp with another randomly drawn training image.
  - When combined with `close_mosaic=10` over 100 epochs, MixUp is active during **epochs 1 to 90**.
  - In **epochs 91 to 100**, `close_mosaic` triggers `dataset.close_mosaic()`, which sets `hyp.mixup = 0.0` and `hyp.mosaic = 0.0`. Augmentations are disabled for the final 10 epochs, ensuring the network converges and calibrates on natural, unmixed imagery.
- **Controlled Configuration:**
  - Hold resolution constant at **768px** (the validated E002 configuration).
  - Hold architecture constant at **YOLO11s** (`yolo11s.pt` initialization).
  - Hold batch size (`16`), epochs (`100`), seed (`42`), optimizer (`MuSGD`), and dataset constant.
  - Change **only one variable:** `mixup = 0.15` (from `0.0`).
- **Predefined Success Criteria:**
  1. Overlapping-object recall: $\ge 98.20\%$ (from E002 baseline 97.12%)
  2. Overlapping misses: $\le 10$ (from E002 baseline 16)
  3. Validation mAP@50–95: $\ge 98.95\%$ (from E002 canonical baseline 98.81%)
  4. Precision: $\ge 99.20\%$ (guarding against hallucinated blends)
  5. No per-class mAP@50–95 drop $> 0.5\%$.

---

## 7. Status Declarations

```
E002 ANALYSIS COMPLETE
LOCKED TEST AND INDIA BENCHMARK UNTOUCHED
```
