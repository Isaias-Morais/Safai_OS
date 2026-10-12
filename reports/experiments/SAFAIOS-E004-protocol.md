# SafaiOS Experiment Protocol & Feasibility Assessment: SAFAIOS-E004-YOLO11S-COARSEDROPOUT

**Project:** SafaiOS  
**Product Tagline:** *The Intelligence Behind Cleaner Cities.*  
**Operating Principle:** *Detect. Act. Verify.*  
**Experiment ID:** `SAFAIOS-E004-YOLO11S-COARSEDROPOUT`  
**Reference Experiment:** `SAFAIOS-E002-YOLO11S-768` (Canonical 768px Frozen Baseline)  
**Predecessor Experiment:** `SAFAIOS-E003-YOLO11S-MIXUP` (Closed Negative Finding for Linear Whole-Image Blending)  
**Phase:** Phase 4 — Model Optimization & Controlled Experiments  
**Status & Formal Gate Decision:** **READY FOR TRAINING** (All implementations, optimizer alignments, preflight visual tests, and criteria verified)  
**Strict Operational Rule:** Protocol freeze only. **Do NOT initiate training.**

---

## 1. Executive Summary & Gate Decision

Experiment `SAFAIOS-E004` evaluates whether data augmentation utilizing rectangular patch visual erasure (**Albumentations CoarseDropout**) improves detection robustness and partial-feature recognition on dense municipal waste scenes, specifically within the challenging overlapping-object stratum.

### 1.1 Gate Decision: READY FOR TRAINING
All feasibility prerequisites, environment configurations, and protocol requirements have been satisfied:
1. **Implementation Feasibility Verified:** Installed Ultralytics `8.4.174` and Albumentations `2.0.8` integration verified in the local environment.
2. **Optimizer Mismatch Reconciled:** Corrected optimizer from placeholder `SGD` to match E002's exact resolved `MuSGD` (`lr0=0.01`, `lrf=0.01`, `momentum=0.937`, `weight_decay=0.0005`, `warmup_epochs=3.0`, `cos_lr=False`).
3. **Augmentation Preservation Guaranteed:** Explicitly passing `hyp.augmentations = [A.CoarseDropout(...)]` ensures that baseline E002 transforms are preserved and default Albumentations transforms (Blur, CLAHE, ToGray, which were inactive in E002) remain inactive.
4. **Non-Training Visual Feasibility Confirmed:** Preflight on 100 training images (239 ground-truth boxes) proved that the selected "Moderate" configuration (8%–18% hole size, 1–2 holes, fill=114) delivers meaningful partial erasure on 10.0% of objects with **0.00% severe occlusion (>75%)** and **0.00% object obliteration (>90%)**, avoiding label noise.
5. **Success Criteria Corrected & Frozen:** Corrected the isolated-object stratum threshold to a mathematically consistent pair: **Recall $\ge 99.80\%$ ($\ge 1,905 / 1,908$, $\le 3$ misses)**.

---

## 2. Scientific Framing, Hypothesis & Limitations

### 2.1 Scientific Hypothesis
In Experiment 002 (768px baseline), 16 of the 18 remaining False Negatives (88.9%) were concentrated in the ground-truth bounding-box overlap stratum (pairwise $\text{IoU} \ge 0.1$). Isolated objects achieved **99.90% recall** (1,906 / 1,908), whereas overlapping objects achieved only **97.12% recall** (539 / 555).

Experiment 003 demonstrated that linear whole-image blending (`mixup=0.15`) was ineffective (overlap recall unchanged at 97.12%, 16 misses) because translucent alpha-blending creates ethereal ghosting rather than crisp boundary occlusion.

**E004 Core Hypothesis:** By introducing sharp, rectangular cutouts filled with neutral background values, the network is penalized for over-relying on complete, unbroken object silhouettes and is forced to learn local textural representations (bottle necks, can rims, crushed cardboard seams). We test whether this partial-feature robustness improves the observed overlap-stratum detection metric.

### 2.2 Critical Scientific Limitations & Explicit Disclaimers
> [!IMPORTANT]
> **Rectangular Visual Erasure Does NOT Equal Real Physical Waste Overlap:**
> 1. CoarseDropout erases rectangular patches using neutral grey fill `(114, 114, 114)`. It does **not** synthesize real waste-on-waste contact, realistic 3D depth layering, material interpenetration, or real-world lighting/shadow boundary interactions.
> 2. We do **not** claim this transform generates realistic overlapping objects, nor do we promise guaranteed improvement on overlap recall.
> 3. This experiment is strictly an empirical test of whether robustness to partial visual erasure translates to higher recall in dense, co-located waste clutter. Predeclared success criteria strictly govern whether the hypothesis is supported or rejected.

---

## 3. Implementation Audit & Feasibility Findings

### 3.1 Why Native Ultralytics CutMix Was Rejected
A code audit of installed Ultralytics `8.4.174` revealed an architectural barrier in native `CutMix`:
- `CutMix.get_params()` (`ultralytics/data/augment.py:968–981`) evaluates candidate patches against Image 1's bounding boxes: `ioa1 = bbox_ioa(cut_areas, labels['instances'].bboxes)`.
- Line 970 enforces: `idx = np.nonzero(ioa1.sum(axis=1) <= 0)[0]`. Any candidate patch that touches any existing box is discarded.
- In multi-object waste scenes, candidate patches virtually always intersect an object. If all 3 attempts intersect a box, `params['skip'] = True` is triggered.
- **Empirical verification on multi-object scenes demonstrated a 99.0% skip rate.** In the <1% where placed, patches sit strictly in empty background. Primary objects are **never occluded or cut**.
- Setting `cutmix > 0.0` would have resulted in hollow training with near-zero augmentation signal.

### 3.2 Albumentations Integration Audit (Ultralytics 8.4.174 + Albumentations 2.0.8)

| Technical Requirement | Audit Finding | Concrete Code Evidence & Source Reference |
|---|---|---|
| **Installed Versions** | Ultralytics `8.4.174`, Albumentations `2.0.8` | Verified in `.venv` environment. |
| **`CoarseDropout` Constructor** | `A.CoarseDropout(num_holes_range=(1, 2), hole_height_range=(0.08, 0.18), hole_width_range=(0.08, 0.18), fill=(114, 114, 114), fill_mask=None, p=0.5)` | Albumentations 2.0.8 signature verified via `inspect.signature`. |
| **Wrapper Invocation** | Instantiated via `Albumentations` class in `ultralytics/data/augment.py:2140–2321` and called at line 2907 in `v8_transforms`. | `Albumentations(p=1.0, transforms=getattr(hyp, 'augmentations', None), flip_idx=flip_idx)`. |
| **Transform Class Type** | `DualTransform` | In Albumentations 2.0.8, `CoarseDropout` inherits from `BaseDropout` $\to$ `DualTransform`. |
| **Bounding-Box Preservation** | **100% Exact Preservation** | Because `self.contains_spatial = True`, Ultralytics configures `A.Compose(T, bbox_params=A.BboxParams(format='yolo'))`. CoarseDropout drops pixel values within holes while returning bounding boxes unaltered. Empirical test verified: `np.allclose(out_bboxes, orig_bboxes) == True`. Zero boxes are clipped or dropped. |
| **Augmentation Isolation** | **Defaults Overridden** | In E002, Albumentations was not installed (`self.transform = None`, zero transforms applied). Passing `transforms = [A.CoarseDropout(...)]` explicitly overrides the default list (`Blur`, `MedianBlur`, `ToGray`, `CLAHE`), keeping all extraneous transforms at $p=0.0$. |

---

## 4. Non-Training Visual Feasibility Preflight Results

To calibrate hole sizes without leaking validation data, a preflight test was executed on a fixed, reproducible sample of **100 training images** (239 ground-truth bounding boxes) from `data/safaios_dataset_v10k/training/images`.

Three parameter configurations were evaluated:

| Metric | Config 1: Conservative (5%–12%) | Config 2: Moderate (8%–18%) [SELECTED] | Config 3: Aggressive (10%–25%, 2–4 holes) |
|---|---|---|---|
| **Hole Count Range** | 1–2 holes | **1–2 holes** | 2–4 holes |
| **Hole Size Range (relative)** | 5%–12% height/width | **8%–18% height/width** | 10%–25% height/width |
| **Images Applied ($p=1.0$)** | 100 / 100 (100.0%) | **100 / 100 (100.0%)** | 100 / 100 (100.0%) |
| **Boxes Touched / Affected** | 29 / 239 (12.1%) | **41 / 239 (17.2%)** | 103 / 239 (43.1%) |
| **Meaningful Partial Erasure (15%–75% area)** | 6 / 239 (2.5%) | **24 / 239 (10.0%)** | 54 / 239 (22.6%) |
| **Severely Occluded (>75% area covered)** | 0 / 239 (0.00%) | **0 / 239 (0.00%)** | 5 / 239 (2.09%) |
| **Almost Obliterated (>90% area covered)** | 0 / 239 (0.00%) | **0 / 239 (0.00%)** | 2 / 239 (0.84%) |
| **Mean Coverage (affected boxes)** | 10.2% | **21.2%** | 27.8% |
| **Median Coverage (affected boxes)** | 8.3% | **18.2%** | 24.3% |
| **90th Percentile Coverage** | 17.6% | **41.7%** | 58.6% |
| **Feasibility Verdict** | Too mild (only 2.5% meaningful partial erasure) | **OPTIMAL: Meaningful partial disruption with 0% obliteration** | Destructive: completely erases small objects, creating false-negative label noise |

### 4.1 Selected Configuration Justification
**Config 2 ("Moderate", 8%–18%)** was selected and frozen:
- It creates meaningful partial visual disruption (15%–75% box area covered) on 10.0% of objects.
- Exactly **0.00% of objects** suffer severe occlusion (>75%) or obliteration (>90%). Ground-truth bounding box labels remain valid without training the model on completely invisible targets.
- Fill color `(114, 114, 114)` matches the neutral letterbox padding standard in YOLO, preventing extreme black-pixel gradient shocks.
- Visual inspection artifact: [SAFAIOS-E004-coarsedropout-preflight.png](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/reports/experiments/figures/SAFAIOS-E004-coarsedropout-preflight.png).

---

## 5. Augmentation Schedule & Optimizer Alignment

### 5.1 Augmentation Schedule
- **Schedule Definition:** `CoarseDropout` remains active at probability $p = 0.5$ across **all 100 epochs**.
- **Interaction with `close_mosaic=10`:** In Ultralytics `8.4.174` (`ultralytics/data/dataset.py:384–394`), `close_mosaic` explicitly zeroes `hyp.mosaic=0.0`, `hyp.copy_paste=0.0`, `hyp.mixup=0.0`, and `hyp.cutmix=0.0` for epochs 91–100, but does not alter `hyp.augmentations`.
- Therefore, Mosaic is cleanly closed for the final 10 epochs (matching E002), while CoarseDropout provides consistent feature-dropout regularization throughout the entire schedule.

### 5.2 Optimizer Reconciliation with Frozen E002
Direct inspection of E002's `args.yaml` and `best.pt` metadata resolved the earlier discrepancy:

| Hyperparameter | E002 Saved Run (`args.yaml` & `best.pt`) | Draft E004 Protocol | E004 Reconciled Setting | Status |
|---|---|---|---|---|
| **Optimizer** | `MuSGD` | `SGD` | `MuSGD` | **RECONCILED** |
| **Initial Learning Rate (`lr0`)** | `0.01` | `0.01` | `0.01` | **MATCHED** |
| **Final Learning Rate Factor (`lrf`)** | `0.01` | `0.01` | `0.01` | **MATCHED** |
| **Momentum** | `0.937` | `0.937` | `0.937` | **MATCHED** |
| **Weight Decay** | `0.0005` | `0.0005` | `0.0005` | **MATCHED** |
| **Warmup Epochs** | `3.0` | `3.0` | `3.0` | **MATCHED** |
| **Warmup Momentum** | `0.8` | `0.8` | `0.8` | **MATCHED** |
| **Warmup Bias LR** | `0.0` | `0.0` | `0.0` | **MATCHED** |
| **Cosine LR (`cos_lr`)** | `False` | `False` | `False` | **MATCHED** |

---

## 6. Predeclared Success Criteria & Evaluation Protocol

All criteria are strictly evaluated on `data/safaios_dataset_v10k/validation/` (1,000 images, 2,463 ground-truth objects).

| Criterion | Target Metric | Canonical E002 Baseline | E004 Predeclared Threshold | Evaluation Protocol & Decision Rule |
|---|---|---|---|---|
| **SC-1** | Overlap Stratum Recall ($\text{IoU} \ge 0.1$) | **97.12%** (539 / 555) | **$\ge 97.66\%$** ($\ge 542 / 555$) | Primary Target: reduce overlap misses by $\ge 3$ ($\le 13$ misses) under operational greedy bipartite matching ($\text{conf}=0.25$, $\text{match IoU}=0.50$). |
| **SC-2** | Overlap Stratum Misses | **16 misses** | **$\le 13$ misses** | Primary Target: absolute false-negative count in overlap stratum. |
| **SC-3** | Official COCO mAP@50–95 | **98.81%** (`0.9880925887293113`) | **$\ge 98.85\%$** | Preserve or improve global ranking accuracy across all validation images. |
| **SC-4** | Official Summary Precision | **99.39%** (`0.9938867079653775`) | **$\ge 99.20\%$** | Bound false-positive inflation at optimal F1 confidence threshold. |
| **SC-5** | Isolated Stratum Recall Guard ($\text{IoU} < 0.1$) | **99.90%** (1,906 / 1,908, 2 misses) | **$\ge 99.80\%$** ($\ge 1,905 / 1,908$, $\le 3$ misses) | Mathematically consistent: $1,905 / 1,908 = 99.843\% \ge 99.80\%$, allowing at most 3 misses to protect clean scenes. |
| **SC-6** | Per-Class mAP@50–95 Regression Guard | Bottle: 98.89%, Bag: 98.85%, Cardboard: 98.86%, Glass: 98.66%, Can: 98.78% | No individual class drop $> 0.50\text{ pp}$ | Guard against catastrophic forgetting or class-specific degradation. |

---

## 7. Controlled Experimental Configuration Summary

- **Experiment Identifier:** `SAFAIOS-E004-YOLO11S-COARSEDROPOUT`
- **Model Checkpoint:** Fresh `yolo11s.pt` (`SHA256: 85a76fe86dd8afe384648546b56a7a78580c7cb7b404fc595f97969322d502d5`)
- **Dataset:** [data.yaml](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/data/safaios_dataset_v10k/data.yaml)
- **Resolution:** `768px` (`imgsz=768`)
- **Batch Size:** `16`
- **Epochs:** `100` (`close_mosaic=10`)
- **Optimizer:** `MuSGD` (`lr0=0.01`, `lrf=0.01`, `momentum=0.937`, `weight_decay=0.0005`, `warmup_epochs=3.0`, `cos_lr=False`)
- **Seed & Determinism:** `seed=42`, `deterministic=True`
- **Primary Intervention:** `Albumentations CoarseDropout(num_holes_range=(1, 2), hole_height_range=(0.08, 0.18), hole_width_range=(0.08, 0.18), fill=(114, 114, 114), p=0.5)`
- **Material Baseline Controls:** `mosaic=1.0`, `mixup=0.0`, `cutmix=0.0`, `copy_paste=0.0`, `scale=0.5`, `fliplr=0.5`, `hsv_h=0.015`, `hsv_s=0.7`, `hsv_v=0.4`.

### Strict Benchmark Isolation
- `test_locked_v2`: **LOCKED & ISOLATED** (0 accesses, 0 inferences, 0 file reads).
- `india_real_world`: **SACRED & ISOLATED** (0 accesses, 0 inferences, 0 file reads).
- Historical experiments E001, E002, and E003 remain frozen and untouched.

---

## 8. Final Status & Gate Review

> **FORMAL DECISION: READY FOR TRAINING**  
> All design, feasibility, environment, optimizer, preflight visual, and success-criteria verifications are complete and frozen.  
> **TRAINING IS NOT STARTED.** The protocol and feasibility findings are submitted for final stakeholder review.
