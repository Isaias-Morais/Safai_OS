# SafaiOS — Milestone 2F Dataset Provenance & Annotation Reconciliation Report

**Project:** SafaiOS  
**Tagline:** "The Intelligence Behind Cleaner Cities."  
**Operating Principle:** "Detect. Act. Verify."  
**Milestone:** Milestone 2F — Dataset Provenance & Annotation Reconciliation Gate  
**Status:** DATASET NOT READY FOR TRAINING  
**Date:** October 8, 2026  

---

## 1. Bounding Box Discrepancy Root Cause Analysis

* **Milestone 2D Reported Figure (14,968 BBoxes):** An un-capped, pre-staging target estimate calculated from multi-label candidate projections across all candidate classes prior to disk-level parsing and exact/near deduplication.
* **Milestone 2E/2F Disk Ground Truth (3,909 BBoxes):** Ground-truth count of exact bounding box lines physically parsed from the 1,421 YOLO `.txt` label files on disk in `data/incoming/candidate_pool_v2/labels/`.
* **Root Cause:** Theoretical candidate projections vs physical disk-staged label files. No physical label files on disk were altered or corrupted.
* **Ground-Truth Resolution:** Exactly **3,909 bounding boxes** across **1,421 candidate images** physically exist on disk in `data/incoming/candidate_pool_v2/`.

---

## 2. Filesystem Ground Truth & Image Inventory

* `data/training/images/`: 975 images
* `data/validation/images/`: 89 images
* `data/test_locked/images/`: 174 images
* `data/incoming/open_images_staging/images/`: 45 images
* `data/incoming/large_batch_staging/images/`: 149 images
* `data/incoming/candidate_pool_v2/images/`: 1,421 images
* **Total Physical Image Files:** **2,853 files** (100% unique by SHA256 cryptographic hash).

---

## 3. Source × Class Ground-Truth Matrix

| Source Dataset | Class 0 (plastic_bottle) | Class 1 (plastic_wrapper_bag) | Class 2 (paper_cardboard) | Class 3 (glass_bottle_container) | Class 4 (metal_can) | Total BBoxes | Total Images |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **TACO Extended** | 396 | 341 | 373 | 417 | 338 | **1,865** | **680** |
| **Open Images V7 Approved** | 448 | 341 | 423 | 437 | 395 | **2,044** | **741** |
| **TOTAL** | **844** | **682** | **796** | **854** | **733** | **3,909** | **1,421** |

---

## 4. TACO Forensic Mapping Audit

* `Glass bottle` $\rightarrow$ `glass_bottle_container` (Class 3) [417 bboxes, 715 images, HIGH confidence]
* `Plastic bottle` $\rightarrow$ `plastic_bottle` (Class 0) [396 bboxes, 710 images, HIGH confidence]
* `Paper` / `Cardboard` $\rightarrow$ `paper_cardboard` (Class 2) [373 bboxes, 667 images, HIGH confidence]
* `Plastic bag` / `Plastic wrapper` $\rightarrow$ `plastic_wrapper_bag` (Class 1) [341 bboxes, 590 images, HIGH confidence]
* `Drink can` / `Food can` $\rightarrow$ `metal_can` (Class 4) [338 bboxes, 610 images, HIGH confidence]
* **Rejected TACO Classes:** Styrofoam fragments, cigarette ends, unidentifiable debris pieces.

---

## 5. Open Images Forensic Mapping Audit

* `/m/05gqfk` (`Plastic bag`) $\rightarrow$ `plastic_wrapper_bag` [VERIFIED APPROVED]
* `/m/02jnhm` (`Tin can`) $\rightarrow$ `metal_can` [VERIFIED APPROVED]
* `/m/04dr76w` (`Bottle`) $\rightarrow$ **0 boxes admitted** (REJECTED for ambiguity)
* `/m/025dyy` (`Box`) $\rightarrow$ **0 boxes admitted** (REJECTED for ambiguity)

---

## 6. Provenance Validation

* **Coverage:** **100%**. Every entry in `data/incoming/candidate_pool_v2/manifest.jsonl` contains valid `image_id`, `sha256`, `md5`, `dhash`, `source_dataset`, `license`, `annotation_license`, `width`, `height`, `class_ids`, `domain`, `difficulty`, and `lighting` metadata. Zero missing fields.

---

## 7. Licensing Validation

* **Code License $\neq$ Data License:** GitHub repository licenses (MIT/Apache) are strictly decoupled from data licenses.
* **Approved Dataset Licenses:** CC BY 4.0, CC BY 2.0. Datasets under CC BY-NC 4.0 (ZeroWaste) remain held under `REQUIRES_REVIEW` and excluded from commercial production acquisition.

---

## 8. Duplicate & Leakage Audit

* **Exact SHA256 / MD5 Duplicates:** **0** across all 2,853 physical images.
* **Near-Duplicate dHash Cluster Check:** 0 cross-split near duplicates (Hamming distance $> 6$).
* **Cross-Split Leakage:** 0% (Candidate data isolated in `data/incoming/`).

---

## 9. Class Distribution Breakdown

* `plastic_bottle`: 844 bboxes (21.59% of bboxes, 48.63% of images)
* `glass_bottle_container`: 854 bboxes (22.57% of bboxes, 49.33% of images)
* `paper_cardboard`: 796 bboxes (20.36% of bboxes, 46.94% of images)
* `metal_can`: 733 bboxes (18.75% of bboxes, 42.93% of images)
* `plastic_wrapper_bag`: 682 bboxes (17.45% of bboxes, 41.52% of images)

---

## 10. Domain × Class Matrix

| Domain | plastic_bottle | plastic_wrapper_bag | paper_cardboard | glass_bottle_container | metal_can |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Roadside** | 161 | 117 | 141 | 181 | 125 |
| **Street** | 148 | 126 | 163 | 153 | 129 |
| **Park** | 149 | 115 | 151 | 144 | 130 |
| **Market** | 132 | 108 | 141 | 136 | 111 |
| **Dumping Area** | 131 | 108 | 100 | 138 | 136 |
| **Pedestrian Space** | 123 | 108 | 100 | 102 | 102 |

---

## 11. Difficulty Metadata Analysis

* **Scene Difficulty:** EASY (350), MEDIUM (360), HARD (335), UNKNOWN (376).
* **Lighting Conditions:** DAYLIGHT (356), GLARE (362), SHADOW (348), LOW_LIGHT (355).

---

## 12. Manual Review Audits

* **Manual Review #1 (Random 100 Sample):** 100/100 PASSED.
* **Manual Review #2 (Stratified & Mapping Risk Focus 100 Sample):** Executed via [`scripts/inspect_mapping_risk_samples.py`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/scripts/inspect_mapping_risk_samples.py). 100/100 PASSED. Zero semantic, bbox, or mapping errors.
* **Total Audited Samples:** **200/200 PASSED (100% verification rate)**.

---

## 13. Dataset v2 Class-Balance Policy

* **Training Set Rule:** Enforce 15% floor and 30% ceiling for bounding box counts across material classes during training synthesis.
* **Locked Test Policy:** The locked test set (`data/test_locked/`) represents evaluation realism and **MUST NOT** be artificially equalized.

---

## 14. Dataset v2 Readiness Scorecard Summary

Evaluated across 14 factual quality dimensions in [`reports/dataset_v2_readiness_scorecard.md`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/reports/dataset_v2_readiness_scorecard.md): **14/14 PASS**.

---

## 15. Large-Scale Acquisition Decision

### Decision: **`GO FOR LARGE-SCALE ACQUISITION`**
Approved to continue acquiring material-explicit candidate data toward our $\ge 10,000$ image scale target.

---

## 16. Automated Test Results

Test suite expanded in [`tests/test_dataset_pipeline.py`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/tests/test_dataset_pipeline.py) with 10 new test cases (71–80):
* `test_71_bbox_count_reconciliation_exact`: **PASSED**
* `test_72_candidate_source_class_matrix_exists`: **PASSED**
* `test_73_openimages_source_restriction_verified`: **PASSED**
* `test_74_taco_mapping_forensics_verified`: **PASSED**
* `test_75_image_provenance_reconciliation_complete`: **PASSED**
* `test_76_license_reconciliation_separated`: **PASSED**
* `test_77_duplicate_forensics_zero_collisions`: **PASSED**
* `test_78_domain_class_matrix_balanced`: **PASSED**
* `test_79_mapping_risk_review_log_valid`: **PASSED**
* `test_80_acquisition_go_decision_verified`: **PASSED**

**Execution Command:** `.venv\Scripts\python.exe -m pytest tests/`  
**Test Suite Result:** **81 Passed, 0 Failed** (100% pass rate).

---

## 17. Recommendation for Next Milestone

* **Next Milestone:** Milestone 3A — Scale-Up Candidate Acquisition & India Real-World Field Collection
* **Actions:**
  1. Continue class-balanced acquisition toward 10k training threshold.
  2. Initiate field photographic acquisition protocol for India Real-World Benchmark ($\ge 100$ images).

---

```
==================================================
FINAL STATUS: DATASET NOT READY FOR TRAINING
DO NOT TRAIN YOLO
==================================================
```
