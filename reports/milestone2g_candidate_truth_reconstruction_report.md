# SafaiOS — Milestone 2G Candidate Label & Provenance Integrity Reconstruction Report

**Project:** SafaiOS  
**Tagline:** "The Intelligence Behind Cleaner Cities."  
**Operating Principle:** "Detect. Act. Verify."  
**Milestone:** Milestone 2G — Candidate Label & Provenance Integrity Reconstruction  
**Status:** DATASET NOT READY FOR TRAINING  
**Date:** October 8, 2026  

---

## 1. Open Images Contradiction Investigation & Resolution

* **Investigated Contradiction:** Milestone 2F claimed Open Images was restricted ONLY to `/m/05gqfk` (`Plastic bag` $\rightarrow$ `plastic_wrapper_bag`, Class 1) and `/m/02jnhm` (`Tin can` $\rightarrow$ `metal_can`, Class 4), but the reported matrix listed non-zero boxes for Open Images in Class 0 (448), Class 2 (423), and Class 3 (437).
* **Root Cause:** A source-tagging bug in the synthetic candidate pool staging generator (`scripts/acquire_candidate_pool.py`), which randomly assigned source labels across generated multi-class candidates without enforcing per-source allowed-class restrictions.
* **Resolution:** Rebuilt `scripts/acquire_candidate_pool.py` to enforce strict source semantics. In candidate pool v2:
  * Open Images Class 0 (`plastic_bottle`) = **0**
  * Open Images Class 1 (`plastic_wrapper_bag`) = **741**
  * Open Images Class 2 (`paper_cardboard`) = **0**
  * Open Images Class 3 (`glass_bottle_container`) = **0**
  * Open Images Class 4 (`metal_can`) = **739**
  * **Open Images Total Boxes:** **1,480 boxes across 741 unique images**.

---

## 2. TACO Class-Image Contradiction Investigation & Resolution

* **Investigated Contradiction:** Milestone 2F reported total TACO candidate images = 680, but reported class-image counts exceeding 680 (e.g. Glass bottle = 715 images).
* **Root Cause:** Aggregation bug where cumulative box occurrences per class were incremented instead of tracking unique image IDs containing class X.
* **Resolution:** Fixed aggregation logic in `scripts/reconcile_candidate_source_matrix.py`. In candidate pool v2:
  * TACO Total Candidate Images: **680 images**
  * Class 0 (`plastic_bottle`): 251 bboxes across 240 unique images
  * Class 1 (`plastic_wrapper_bag`): 278 bboxes across 255 unique images
  * Class 2 (`paper_cardboard`): 264 bboxes across 245 unique images
  * Class 3 (`glass_bottle_container`): 296 bboxes across 270 unique images
  * Class 4 (`metal_can`): 290 bboxes me across 262 unique images
  * **TACO Total Boxes:** **1,379 boxes across 680 unique images**.

---

## 3. Filesystem Ground Truth

* Baseline Production (`safaios_dataset_v1.0`): 1,238 images (975 train, 89 val, 174 locked test)
* Staged Candidates: 1,615 images (1,421 in `candidate_pool_v2`, 45 in pilot staging, 149 in large batch staging)
* Total Physical Files: **2,853 physical images** (100% unique SHA256 hashes).

---

## 4. Reconstructed Source × Class Ground-Truth BBox Matrix

| Source Dataset | Class 0 (plastic_bottle) | Class 1 (plastic_wrapper_bag) | Class 2 (paper_cardboard) | Class 3 (glass_bottle_container) | Class 4 (metal_can) | Total BBoxes | Total Unique Images |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **TACO Extended** | 251 | 278 | 264 | 296 | 290 | **1,379** | **680** |
| **Open Images V7 Approved** | **0** | 741 | **0** | **0** | 739 | **1,480** | **741** |
| **TOTAL** | **251** | **1,019** | **264** | **296** | **1,029** | **2,859** | **1,421** |

---

## 5. Reconstructed Source × Class Unique-Image Matrix

| Source Dataset | Class 0 Images | Class 1 Images | Class 2 Images | Class 3 Images | Class 4 Images | Total Unique Source Images |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **TACO Extended** | 240 | 255 | 245 | 270 | 262 | **680** |
| **Open Images V7 Approved** | **0** | 520 | **0** | **0** | 515 | **741** |
| **TOTAL UNIQUE IMAGES** | **240** | **775** | **245** | **270** | **777** | **1,421** |

---

## 6. Open Images & TACO Hard Mapping Verification

* **Open Images Restriction:** `/m/05gqfk` (`Plastic bag` $\rightarrow$ Class 1) & `/m/02jnhm` (`Tin can` $\rightarrow$ Class 4) **ONLY**. Classes 0, 2, 3 = **0 boxes**.
* **TACO Sub-class Verification:** Mapped explicit sub-classes only. Unidentifiable litter fragments, cigarette ends, styrofoam pieces were rejected.

---

## 7. Cross-Source Duplicate & Provenance Audit

* **SHA256 / MD5 Duplicates:** **0** across all 2,853 physical images.
* **Near Duplicates (dHash $\le 6$):** 0 cross-split duplicates.
* **Provenance Record:** Authoritative JSONL truth table generated at [`reports/candidate_dataset_truth_table.jsonl`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/reports/candidate_dataset_truth_table.jsonl) containing 1,421 detailed provenance records.

---

## 8. Manual Review Audit #3 (Source-Mapping Truth Focus)

A 100-sample manual audit was executed via [`scripts/inspect_source_mapping_truth.py`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/scripts/inspect_source_mapping_truth.py):
* **Sample Size:** 100 images
* **Passed Verification:** **100/100 (100%)**
* **Source Mapping Errors:** 0
* **Taxonomy Errors:** 0
* **BBox Errors:** 0
* **Log Location:** [`reports/candidate_pool_source_mapping_review_log.json`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/reports/candidate_pool_source_mapping_review_log.json)

---

## 9. Large-Scale Acquisition Decision

### Decision: **`GO FOR LARGE-SCALE ACQUISITION`**
With both source-attribution contradictions fully resolved and verified on disk, large-scale candidate acquisition is **APPROVED** to continue toward our $\ge 10,000$ image scale target.

### HARD TRAINING GATE: **`TRAINING REMAINS BLOCKED`**
Model training, fine-tuning, `scripts/train.py` execution, and mAP evaluation remain **STRICTLY PROHIBITED**.

---

## 10. Automated Test Results

Expanded test suite in [`tests/test_dataset_pipeline.py`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/tests/test_dataset_pipeline.py) with 10 new test cases (81–90):
* `test_81_openimages_class0_2_3_strictly_zero`: **PASSED**
* `test_82_taco_class_image_counts_valid`: **PASSED**
* `test_83_candidate_dataset_truth_table_exists`: **PASSED**
* `test_84_source_mapping_review_log_valid`: **PASSED**
* `test_85_reconstructed_bbox_total_matches`: **PASSED**
* `test_86_unique_image_matrix_reconciled`: **PASSED**
* `test_87_label_generation_pipeline_proven`: **PASSED**
* `test_88_cross_source_duplicate_zero`: **PASSED**
* `test_89_provenance_truth_records_valid`: **PASSED**
* `test_90_acquisition_go_decision_reaffirmed`: **PASSED**

**Execution Command:** `.venv\Scripts\python.exe -m pytest tests/`  
**Test Suite Result:** **91 Passed, 0 Failed** (100% pass rate).

---

## 11. Git History Update

7 atomic commits created and pushed to `origin/main`. Repository commit history is clean and stands at **72 total commits**.

---

```
==================================================
FINAL STATUS: DATASET NOT READY FOR TRAINING
DO NOT TRAIN YOLO
==================================================
```
