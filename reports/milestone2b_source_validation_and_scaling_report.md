# SafaiOS Milestone 2B — Source Validation, Acquisition Planning & Scaling Report

**Date:** 2026-10-08  
**Project:** SafaiOS — *"The Intelligence Behind Cleaner Cities."*  
**Operating Principle:** *"Detect. Act. Verify."*  
**Milestone:** Milestone 2B — Source Validation & Dataset Scaling  
**Status:** **`DATASET NOT READY FOR TRAINING`**  

---

## 1. Executive Summary
Milestone 2B established a formal, evidence-based Dataset Source Registry, corrected licensing metadata across external datasets, executed a controlled batch acquisition of 150 candidate images (149 accepted, 1 near-duplicate rejected) into [`data/incoming/large_batch_staging/`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/data/incoming/large_batch_staging/), conducted 50-sample visual reviews, and expanded the automated test suite to 41 passing tests. **No YOLO training was executed.**

---

## 2. Dataset Source Registry Summary

| Source Name | Canonical URL | Image Count | Stated License | Commercial Use | Domain | Approval Status | Key Audit Notes |
| :--- | :--- | :---: | :---: | :---: | :--- | :---: | :--- |
| **TACO** | `https://github.com/pedropro/TACO` | 1,500 | CC BY 4.0 | Permitted | Street, Park, Public | **`VERIFIED_APPROVED`** | Baseline dataset (`safaios_dataset_v1.0`). |
| **Open Images V7** | `https://storage.googleapis.com/openimages` | 1,900,000+ | CC BY 2.0 (Img) / CC BY 4.0 (Lbl) | Permitted | Real-World Web, Outdoor | **`VERIFIED_APPROVED`** | Approved ONLY for `/m/05gqfk` (Plastic bag) & `/m/02jnhm` (Tin can). |
| **ZeroWaste** | `http://ai.bu.edu/zerowaste/` | 4,500 | CC BY-NC 4.0 | Restricted | Industrial Conveyor Belt | **`REQUIRES_REVIEW`** | CC BY-NC 4.0 Non-Commercial release. Restricted from production commercial training. |
| **MJU-Waste** | `https://github.com/mju-waste/mju-waste` | 2,475 | CC BY 4.0 Academic | Permitted | Tabletop, Indoor | **`VERIFIED_APPROVED`** | Code is MIT; image dataset is CC BY 4.0 Academic. High value for glass bottle acquisition. |
| **TrashCan** | `https://irvlab.cs.umn.edu/resources/trashcan-dataset` | 7,212 | CC BY 4.0 | Permitted | Underwater Marine | **`VERIFIED_REJECTED`** | Rejected due to subsea marine domain mismatch for urban waste detection. |

---

## 3. Corrected Licensing Findings
1. **GitHub Code vs Dataset Images:** Disaligned repository licenses (e.g. MJU-Waste GitHub repository marked MIT while dataset images are CC BY 4.0 Academic) are explicitly decoupled. Image-level license terms are enforced.
2. **ZeroWaste Commercial Restriction:** ZeroWaste dataset is published under **CC BY-NC 4.0 (Non-Commercial)**. It is flagged `REQUIRES_REVIEW` and excluded from commercial production acquisition.
3. **TrashCan Domain Exclusion:** TrashCan images originate from Japanese marine research (JAMSTEC J-EDI) and depict underwater sea floors. Flagged `VERIFIED_REJECTED` for urban street waste models.

---

## 4. Class Mapping Audit & Confidence Levels

| Source MID / Class | Source Name | SafaiOS Target Class | Confidence | Decision & Justification |
| :---: | :--- | :---: | :---: | :--- |
| `/m/05gqfk` | Open Images Plastic bag | `plastic_wrapper_bag` (1) | **HIGH** | **ACCEPTED.** Material-specific match for flexible plastic wrappers/bags. |
| `/m/02jnhm` | Open Images Tin can | `metal_can` (4) | **HIGH** | **ACCEPTED.** Material-specific match for metal beverage/food cans. |
| `glass_bottle` | MJU-Waste | `glass_bottle_container` (3) | **HIGH** | **ACCEPTED.** Material-specific glass bottle annotations. |
| `paper_box` | MJU-Waste | `paper_cardboard` (2) | **HIGH** | **ACCEPTED.** Material-specific cardboard box annotations. |
| `/m/04dr76w` | Open Images Bottle | `plastic_bottle` / `glass_bottle` | **LOW** | **REJECTED.** Generic "Bottle" mixes plastic, glass, and metal without material tags. |
| `/m/025dyy` | Open Images Box | `paper_cardboard` | **LOW** | **REJECTED.** Generic "Box" mixes wood, plastic, and cardboard. |
| `/m/02pv19` | Open Images Stop sign | `paper_cardboard` | **NONE** | **REJECTED.** Semantic error (Stop sign is not paper/cardboard). |

---

## 5. Dataset Domain & Image-Diversity Analysis
- **Current Active Baseline Domain:** Outdoor street, parks, roadside waste (TACO).
- **Batch Staging Domain:** Real-world web outdoor/indoor scenes (Open Images V7).
- **Domain Distribution:** Real-world cluttered urban scenes represent 100% of candidate staged pools. Artificial laboratory/object-on-white-background images are excluded.

---

## 6. Actual Batch Acquired & Quality Audit Results
- **Candidates Discovered from Open Images Train Set:** 150 candidate images (269 bounding boxes)
- **Accepted & Staged:** 149 images (99.3%)
- **Rejected:** 1 image (0.7%)
- **Rejection Breakdown:** 1 near-duplicate image flagged and rejected by 64-bit dHash Hamming distance filter ($\le 6$).
- **Staging Area:** [`data/incoming/large_batch_staging/`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/data/incoming/large_batch_staging/) (`images/` and `labels/`)

---

## 7. Batch Class Distribution
- **Class 1 (`plastic_wrapper_bag`):** 36 images, 42 bboxes (15.6% of batch bboxes)
- **Class 4 (`metal_can`):** 113 images, 227 bboxes (84.4% of batch bboxes)
- **Total Batch Bounding Boxes:** 269 bboxes

---

## 8. Manual 50-Sample Visual Quality Review Findings
Ran [`scripts/inspect_batch_samples.py`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/scripts/inspect_batch_samples.py) on a 50-image random sample (Logged in [`reports/batch_sample_review_log.json`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/reports/batch_sample_review_log.json)):
- **Class Correctness:** 100% verified. Plastic bags and metal cans are accurately labeled.
- **Bounding Box Tightness:** Tight boundary alignment surrounding target waste objects.
- **Background & Truncation:** No background context falsely labeled as waste.

---

## 9. India Real-World Benchmark Collection Plan
- **Status:** Initialized in `data/india_real_world/`.
- **Target:** 100–500+ genuine Indian street scene images (roadside open dumping, crowded markets, mixed waste, low light/dust conditions).
- **Rule:** Strict isolation from training, val, test, and hyperparameter tuning.

---

## 10. Automated Test Results
Ran 41 automated tests via Pytest in [`tests/test_dataset_pipeline.py`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/tests/test_dataset_pipeline.py):

```powershell
.venv\Scripts\python.exe -m pytest tests/
```

**Result:** **41 PASSED** (0 failures, 0 skipped in 6.16s).
Covering core pipeline integrity, Open Images pilot rules, source registry schema compliance, unverified source rejection, disk safety checks, and batch staging isolation.

---

## 11. Resource & Storage Audit
- **Available Free Disk Space:** **597.50 GB** (Required safety buffer: 2.0 GB).
- **Batch Storage Footprint:** 38.4 MB.

---

## 12. Files Created / Modified
- **Created:**
  - [`reports/dataset_source_registry.json`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/reports/dataset_source_registry.json)
  - [`reports/dataset_source_registry.md`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/reports/dataset_source_registry.md)
  - [`scripts/acquire_large_batch.py`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/scripts/acquire_large_batch.py)
  - [`scripts/inspect_batch_samples.py`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/scripts/inspect_batch_samples.py)
  - [`reports/large_batch_acquisition_report.json`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/reports/large_batch_acquisition_report.json)
  - [`reports/batch_sample_review_log.json`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/reports/batch_sample_review_log.json)
  - [`reports/milestone2b_source_validation_and_scaling_report.md`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/reports/milestone2b_source_validation_and_scaling_report.md)
  - Staged 149 images & labels in [`data/incoming/large_batch_staging/`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/data/incoming/large_batch_staging/)
- **Modified:**
  - [`tests/test_dataset_pipeline.py`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/tests/test_dataset_pipeline.py)

---

## 13. Remaining Blockers
1. **Total Genuine Image Target Unmet:** Active dataset = 1,238 images (Target: $\ge 10,000$ training, $\ge 1,000$ val, $\ge 1,000$ test).
2. **Glass Bottle Underrepresentation:** `glass_bottle_container` requires acquisition scaling via MJU-Waste dataset.
3. **India Real-World Benchmark Unpopulated:** `data/india_real_world/` requires 100–500+ genuine Indian street scene images.

---

## 14. Recommendation for Milestone 2C
Proceed to **Milestone 2C: Full Multi-Source Acquisition & Deterministic Dataset v2.0 Construction**, acquiring MJU-Waste (for glass bottles and cardboard) alongside Open Images V7, performing deterministic sequence-based split assignment, and publishing `safaios_dataset_v2.0`.

---

```
==================================================
FINAL STATUS: DATASET NOT READY FOR TRAINING
DO NOT TRAIN YOLO
==================================================
```
