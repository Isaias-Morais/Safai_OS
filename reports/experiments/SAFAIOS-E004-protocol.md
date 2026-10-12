# SafaiOS Experiment Protocol & Feasibility Assessment: SAFAIOS-E004-YOLO11S-CUTMIX

**Project:** SafaiOS  
**Product Tagline:** The Intelligence Behind Cleaner Cities.  
**Operating Principle:** Detect. Act. Verify.  
**Experiment ID:** `SAFAIOS-E004-YOLO11S-CUTMIX` (Design & Feasibility Assessment Only)  
**Reference Experiment:** `SAFAIOS-E002-YOLO11S-768` (Canonical 768px Baseline)  
**Predecessor Experiment:** `SAFAIOS-E003-YOLO11S-MIXUP` (Closed Negative Finding for Linear Blending)  
**Phase:** Phase 4 — Model Optimization & Controlled Experiments  
**Decision & Status:** **NOT READY FOR TRAINING** (Implementation Limitation Discovered in Ultralytics 8.4.174)

---

## 1. Executive Summary & Feasibility Verdict

Experiment `SAFAIOS-E004` was proposed to evaluate whether data augmentation utilizing rectangular patches and partial visibility (specifically CutMix) could resolve persistent false negatives among overlapping waste objects in dense municipal scenes.

Before initiating any training or modifying configurations, a strict code audit of the installed **Ultralytics 8.4.174** training pipeline was conducted. The audit revealed a critical architectural limitation in the native Ultralytics CutMix implementation for multi-object detection:

> [!WARNING]
> **Implementation Limitation Discovered in Native Ultralytics `8.4.174`:**  
> While `cutmix: 0.0` is exposed in `ultralytics/cfg/default.yaml` and instantiated as `CutMix` in `ultralytics/data/augment.py`, the underlying implementation in `CutMix.get_params()` (lines 968–981) **explicitly filters out any candidate patch that touches an existing bounding box in the primary image (`ioa1.sum(axis=1) <= 0`)**.  
> In multi-object waste scenes (typically 3–10+ items per image), candidate rectangular patches almost always intersect an existing box. When all candidate attempts intersect a box, `params['skip'] = True` is triggered and CutMix is completely bypassed.  
> **Empirical verification on 3-object synthetic waste scenes demonstrated a 99% skip rate (99 of 100 trials skipped).**  
> Furthermore, in the <1% of trials where a patch is placed, it is strictly placed into unoccupied background space. **Primary objects in Image 1 are NEVER cut or partially occluded, and newly pasted objects do not overlap existing ones.**  
> Consequently, native CutMix in Ultralytics 8.4.174 is structurally incapable of testing the hypothesis of partial-visibility occlusion on waste objects.

**Formal Gate Decision:** **NOT READY FOR TRAINING**. In accordance with SafaiOS governance guidelines, we do not pass an ineffective parameter or silently execute an unverified transform. We present this feasibility audit and propose one viable alternative for approval before any training begins.

---

## 2. In-Depth Ultralytics 8.4.174 Implementation Audit

| Question / Requirement | Audit Finding | Concrete Code Evidence & Source Reference |
|---|---|---|
| **Does `cutmix` parameter exist?** | **YES** | Declared in `ultralytics/cfg/default.yaml:128` (`cutmix: 0.0`) and parsed into `hyp.cutmix`. |
| **Is it instantiated in detection transforms?** | **YES** | Instantiated in `ultralytics/data/augment.py:2906`: `CutMix(dataset, pre_transform=pre_transform, p=hyp.cutmix)` inside `v8_transforms`. |
| **How are cut regions and bounding boxes handled?** | **Selective Background Insertion** | `CutMix.get_params()` samples `num_areas = 3` candidate patches via `_rand_bbox(w, h)`: `ioa1 = bbox_ioa(cut_areas, labels['instances'].bboxes)`. Line 970 enforces: `idx = np.nonzero(ioa1.sum(axis=1) <= 0)[0]`. Any patch touching an existing box is rejected. |
| **Does it create partial-visibility examples?** | **NO (Zero occlusion of Image 1)** | Because `ioa1 <= 0` is required, Image 1's boxes are never covered. Image 1's instances (`labels['instances']`) are never clipped or altered. Pasted instances from Image 2 are clipped by the patch boundary, but they sit entirely in empty background regions. |
| **What is the empirical skip rate on multi-object scenes?** | **99.0% Skip Rate** | A synthetic benchmark of 100 trials on images containing 3 waste bounding boxes resulted in 99 skips and 1 application. On dense scenes, CutMix is virtually dead code. |
| **Does `close_mosaic=10` disable CutMix?** | **YES** | `ultralytics/data/dataset.py:384-394` (`close_mosaic`) explicitly resets `hyp.cutmix = 0.0` along with mosaic and mixup for epochs 91–100. |
| **Are segmentation masks required?** | **NO for CutMix, YES for CopyPaste** | `CutMix` operates on bounding boxes. However, Ultralytics `CopyPaste` (`copy_paste > 0.0`) requires instance polygon segments (`labels['instances'].segments`), which are unavailable in the detection-only v10k dataset. |
| **VRAM & Training Time Estimates** | **~6.5 GB VRAM, 3.25 hours** | Batch 16, 768px resolution, 100 epochs on NVIDIA RTX 4060 Laptop GPU. |

---

## 3. Scientific Hypothesis & Motivation

### 3.1 Context from E002 and E003
In Experiment 002 (768px resolution baseline), 16 of 18 remaining False Negatives (88.9%) were concentrated within the ground-truth bounding-box-overlap stratum (pairwise IoU $\ge 0.1$). Isolated objects achieved **99.90% recall** (1,906 / 1,908), while overlapping objects achieved only **97.12% recall** (539 / 555).

Experiment 003 tested linear whole-image blending (`mixup=0.15`). The experiment proved to be a negative finding:
- Overlapping recall was completely unchanged at **97.12%** (539 / 555).
- Overlapping misses remained identical at **16 misses**.
- mAP@50–95 improved by only +0.10 pp to 98.91% (failing the $\ge 98.95\%$ threshold).
- **Physical Reason:** MixUp creates translucent, semi-transparent ghosting artifacts across entire scenes rather than sharp, opaque boundaries. Real-world waste clutter consists of opaque objects physically occluding one another with crisp, hard-edged boundary truncations.

### 3.2 Hypothesis for Rectangular Occlusion Augmentation
Unlike linear blending, an augmentation that introduces **sharp, opaque rectangular cutouts** forces the feature pyramid network (FPN) and detection head to identify objects from partial, local textural cues (e.g., bottle necks, can rims, crushed cardboard edges) rather than relying on unbroken object silhouettes.

If an occlusion transform can reliably truncate 10%–30% of an object's visible area while maintaining the ground-truth box label:
1. The detector will learn robust representations invariant to partial occlusions.
2. Missed overlapping waste items in municipal heaps will drop from 16 to $\le 10$.
3. Overlap-stratum recall will increase to $\ge 98.20\%$.

---

## 4. Proposed Feasible Alternatives for Approval

Because native Ultralytics CutMix is non-functional for multi-object occlusion, we propose the following feasible alternatives for architectural review before E004 training:

### Option A: Albumentations `CoarseDropout` / `Cutout` (Recommended)
- **Mechanism:** Integrates directly into Ultralytics training via `v8_transforms` line 2907 (`Albumentations(p=1.0, transforms=...)`). Applies `A.CoarseDropout(max_holes=8, max_height=64, max_width=64, min_holes=2, p=0.3)`.
- **Advantage:** Drops opaque black/gray rectangular patches directly over the image, including on and around waste objects, without corrupting bounding-box labels. Directly stimulates partial-visibility feature learning.
- **Feasibility:** Fully supported by Albumentations without modifying core Ultralytics C-extensions or dataset loaders.

### Option B: Bounding-Box Aware CutMix Patch Engine
- **Mechanism:** A lightweight custom dataset wrapper that permits rectangular patches from secondary images to overwrite primary image regions even when bounding boxes intersect, with proportional label clipping or occluded label retention.
- **Advantage:** Preserves realistic waste textures within the occluding patch rather than synthetic black holes.
- **Requirement:** Requires a custom preprocessing transform script before training.

---

## 5. Controlled Configuration & Baseline Controls (If Approved)

If an alternative occlusion intervention is approved, E004 will be strictly controlled against canonical E002:

| Hyperparameter / Control | Canonical E002 Baseline | Proposed E004 Configuration | Status |
|---|:---:|:---:|:---:|
| **Model Initialization** | `yolo11s.pt` | `yolo11s.pt` (`85a76fe86dd8afe3...`) | **Identical Fresh Pretrained** |
| **Input Resolution (`imgsz`)** | 768 | 768 | **Identical** |
| **Batch Size** | 16 | 16 | **Identical** |
| **Completed Epochs** | 100 | 100 | **Identical** |
| **Mosaic Disabling (`close_mosaic`)** | 10 (Epochs 91–100) | 10 (Epochs 91–100) | **Identical** |
| **Random Seed** | 42 | 42 | **Identical (Deterministic)** |
| **Workers** | 4 | 4 | **Identical** |
| **Optimizer Policy** | `auto` (MuSGD, lr0=0.01) | `auto` (MuSGD, lr0=0.01) | **Identical** |
| **Momentum / Weight Decay** | 0.937 / 0.0005 | 0.937 / 0.0005 | **Identical** |
| **Dataset Split** | `safaios_dataset_v10k` | `safaios_dataset_v10k` | **Identical Frozen Dataset** |
| **MixUp Augmentation** | 0.0 | 0.0 | **Held Strictly at 0.0** |
| **Primary Intervention** | None (0.0) | **Approved Occlusion Augmentation** | **Single Isolated Variable** |
| **All Other Augmentations** | `mosaic=1.0, scale=0.5, fliplr=0.5, hsv=(0.015, 0.7, 0.4)` | Identical | **Held Constant** |

---

## 6. Predeclared Success Criteria & Evaluation Protocol

All criteria are locked prior to any model training and will not be adjusted post-hoc:

| Criterion | Target Metric | Predeclared Threshold | Canonical E002 Baseline | Governing Protocol |
|---|---|:---:|:---:|---|
| **Criterion 1** | Overlap Stratum Recall | **$\ge 98.20\%$** ($\ge 545$ / 555) | 97.12% (539 / 555) | Greedy bipartite matching (`conf=0.25`, `iou_nms=0.60`, match IoU 0.50) on ground-truth pairwise IoU $\ge 0.1$ stratum |
| **Criterion 2** | Overlap Stratum Misses | **$\le 10$ misses** | 16 misses | Greedy bipartite matching on pairwise IoU $\ge 0.1$ stratum |
| **Criterion 3** | Validation mAP@50–95 | **$\ge 98.95\%$** | 98.81% (`0.988092...`) | Official Ultralytics `model.val(data=..., split='val', imgsz=768)` multi-threshold metric |
| **Criterion 4** | Summary Precision Retention | **$\ge 99.20\%$** | 99.39% (`0.993886...`) | Official Ultralytics `val.box.mp` summary precision at optimal F1 threshold |
| **Criterion 5** | Per-Class Regression Guard | **No drop $> 0.5$ pp** | 0 regressions | Per-class AP@50–95 vs canonical E002 (`plastic_bottle`: 0.9889, `plastic_wrapper_bag`: 0.9885, `paper_cardboard`: 0.9886, `glass_bottle_container`: 0.9866, `metal_can`: 0.9878) |

### Operational Evaluation Thresholds
- Fixed confidence threshold: `conf = 0.25`
- Non-Maximum Suppression IoU: `iou = 0.60`
- Bipartite ground-truth assignment IoU: `iou = 0.50`
- Size tier thresholds: Small ($< 0.025$ normalized area), Medium ($0.025 \le \text{area} \le 0.050$), Large ($> 0.050$).

---

## 7. Strict Evaluation Isolation Statement

- **Evaluation Split:** `data/safaios_dataset_v10k/validation/` (1,000 images, 2,463 instances) only.
- **Protected Splits Policy:**  
  - `data/safaios_dataset_v10k/test_locked_v2/`: **STRICTLY FORBIDDEN** (0 reads, 0 inferences, 0 evaluations).
  - `data/safaios_dataset_v10k/india_real_world/`: **STRICTLY FORBIDDEN** (0 reads, 0 inferences, 0 evaluations).
- **Historical Records:** Checkpoints and reports for E001, E002, and E003 remain permanently preserved and unmodified.

---

## 8. Summary of Findings & Next Action Required

1. **Native `cutmix` in Ultralytics 8.4.174 is functionally inactive on multi-object scenes** (99% skip rate) and structurally unable to occlude primary objects.
2. **E004 training is NOT STARTED.**
3. **Action Required:** User review and approval of the proposed alternative (Albumentations `CoarseDropout` vs custom bbox-aware CutMix) before finalizing the runnable training configuration.
