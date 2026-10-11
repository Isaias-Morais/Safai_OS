# SafaiOS Experiment Protocol: SAFAIOS-E003-YOLO11S-MIXUP

**Project:** SafaiOS  
**Tagline:** The Intelligence Behind Cleaner Cities.  
**Operating Principle:** Detect. Act. Verify.  
**Experiment ID:** `SAFAIOS-E003-YOLO11S-MIXUP`  
**Reference Experiment:** `SAFAIOS-E002-YOLO11S-768`  
**Phase:** Phase 4 — Model Optimization & Experimentation  
**Status:** **E003 EXPERIMENT PROTOCOL READY** (Pre-execution Design Gate)  

---

## 1. Context & Motivation

In the empirical error analysis of Experiment 002 (`SAFAIOS-E002-YOLO11S-768`):
- Overall performance at 768px was superior to the 640px baseline across all metrics (mAP@50-95: 98.81%, Precision: 99.39%, Recall: 99.28%).
- Total false positives dropped by **73.3%** (60 $\rightarrow$ 16).
- However, detailed spatial stratification revealed that **16 out of 18 (88.9%) of all remaining False Negatives occur on overlapping waste objects** (pairwise IoU $\ge 0.1$).
- While isolated objects achieved **99.90% recall** (1,906 / 1,908), overlapping objects achieved only **97.12% recall** (539 / 555).
- Both E001 and E002 had MixUp augmentation disabled (`mixup: 0.0`). The network has therefore received zero training signal on resolving blended or semi-occluded overlapping instances.

---

## 2. Experiment Identity & Hypothesis

- **Experiment Identifier:** `SAFAIOS-E003-YOLO11S-MIXUP`
- **Experiment Name:** `safaios_yolo11s_v10k_mixup15`
- **Hypothesis:**  
  Introducing moderate MixUp augmentation (`mixup=0.15`), which linearly blends two training images and their bounding box labels during the first 90 epochs (with `close_mosaic=10` disabling it for final convergence), will teach the YOLO11s feature backbone and detection head to disentangle overlapping, co-located visual features. This will specifically reduce overlapping-object false negatives (from 16 down to $\le 10$) and increase overall validation mAP@50-95 without degrading precision.

---

## 3. Controlled Experimental Configuration

To isolate the effect of MixUp, exactly **ONE primary variable** is altered relative to E002:

### Primary Variable Changed:
- `mixup`: **0.15** (vs. E002 baseline: **0.0**)

### Variables Held Strictly Constant:
| Parameter | Value | Rationale |
| :--- | :---: | :--- |
| **Model Initialization** | `yolo11s.pt` | Fresh pretrained weights (NOT fine-tuning E001/E002 checkpoints) |
| **Input Resolution (`imgsz`)** | **768** | Provisional baseline confirmed by E002 |
| **Batch Size** | 16 | Fixed memory & gradient scale |
| **Epochs** | 100 | Standard 100-epoch trajectory |
| **Mosaic Disabling (`close_mosaic`)**| 10 | Disables mosaic & mixup in epochs 91–100 for clean convergence |
| **Random Seed** | 42 | Strict reproducibility |
| **Optimizer Policy** | `auto` (MuSGD) | Same optimizer policy as E001 and E002 |
| **Learning Rate Schedule** | `lr0=0.01`, `lrf=0.01` | Identical cosine/linear decay schedule |
| **Workers** | 4 | Stable concurrency on Windows CUDA |
| **Device** | CUDA GPU 0 | Single RTX 4060 Laptop GPU |
| **Dataset Configuration** | `data/safaios_dataset_v10k/data.yaml` | Strictly frozen dataset (10,000 train, 1,000 val) |
| **Other Augmentations** | `mosaic=1.0`, `scale=0.5`, `fliplr=0.5`, `hsv_h=0.015`, `hsv_s=0.7`, `hsv_v=0.4` | Unchanged |

---

## 4. Evaluation Protocol & Dataset Restrictions

> [!CAUTION]
> **Strict Evaluation Restrictions:**  
> All evaluation, validation, error inspection, and stopping decisions for Experiment 003 must be conducted exclusively against the fixed validation split:  
> `data/safaios_dataset_v10k/validation/`  
> 
> Under NO circumstances may inference, validation, tuning, or predictions be run against:  
> - `data/safaios_dataset_v10k/test_locked_v2/`  
> - `data/safaios_dataset_v10k/india_real_world/`  
> Both remain **100% UNTOUCHED**.

### Operating Evaluation Settings:
- Validation image size: **768px**
- Official metrics: standard `model.val(data=..., split='val', imgsz=768)`
- Operational evaluation: `conf=0.25`, `iou=0.60`, matching IoU threshold = 0.50

---

## 5. Expected Measurable Effects & Success Criteria

### Target Metrics:
1. **Overlapping Object Recall:**  
   - E002 Baseline: **97.12%** (539 / 555)
   - E003 Target: **$\ge 98.20\%$** ($\ge 545$ / 555)
2. **Overlapping False Negatives:**  
   - E002 Baseline: **16 missed items**
   - E003 Target: **$\le 10$ missed items** (at least 37.5% reduction in overlapping misses)
3. **Validation mAP@50–95:**  
   - E002 Baseline: **98.81%**
   - E003 Target: **$\ge 98.95\%$**
4. **Precision Retention:**  
   - E002 Baseline: **99.39%**
   - E003 Target: **$\ge 99.20\%$** (ensuring synthetic blends do not cause hallucinated predictions)
5. **No Per-Class Regressions:**  
   - No individual class experiences a $>0.5\%$ drop in mAP@50-95.

---

## 6. Execution & Reproducibility Plan

### Dedicated Output Directory:
`runs/detect/runs/safaios/safaios_yolo11s_v10k_mixup15/`

### Execution Command (When Authorized):
```powershell
$env:PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
.venv\Scripts\python.exe scripts/train.py `
  --config configs/training.yaml `
  --data data/safaios_dataset_v10k/data.yaml `
  --model yolo11s.pt `
  --epochs 100 `
  --batch 16 `
  --imgsz 768 `
  --seed 42 `
  --device 0 `
  --workers 4 `
  --project runs/detect/runs/safaios `
  --name safaios_yolo11s_v10k_mixup15 `
  --mixup 0.15
```

### Resource Requirements:
- **GPU:** NVIDIA GeForce RTX 4060 Laptop GPU (8GB VRAM)
- **VRAM Estimate:** ~5.70 GB VRAM
- **Estimated Duration:** ~3.2 hours (~3.5 iterations/sec over 100 epochs)
- **Disk Footprint:** ~1.5 GB for checkpoints and run outputs (gitignored)

---

## 7. Status Declarations

```
E002 ANALYSIS COMPLETE
E003 EXPERIMENT PROTOCOL READY
LOCKED TEST AND INDIA BENCHMARK UNTOUCHED
```
