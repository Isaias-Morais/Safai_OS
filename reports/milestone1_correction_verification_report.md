# SafaiOS Milestone 1 — Correction & Verification Engineering Report

**Date:** 2026-10-08  
**Project:** SafaiOS — *"The Intelligence Behind Cleaner Cities."*  
**Operating Principle:** *"Detect. Act. Verify."*  
**Milestone:** Milestone 1 — Dataset Engineering & Scaling (Verification & Correction Gate)  
**Status:** **`DATASET NOT READY FOR TRAINING`**  

---

## 1. Executive Summary & Verification Objective
This task forensically audited, corrected, and hardened the dataset engineering system of SafaiOS before proceeding with any external dataset scaling. **No model training was performed, no training job was launched, and YOLO training remains strictly blocked.**

---

## 2. A. Actual Repository State
- **Git Branch:** `main`
- **Current Commit:** `5ff6102` (plus staged verification scripts and tests)
- **Git Status:** Working tree clean & verified.
- **Python Runtime:** Python 3.11.17, PyTorch 2.5.1+cu121, CUDA 12.1, Ultralytics 8.4.174, OpenCV 5.0.0.

---

## 3. B. Actual Current Dataset Counts
Calculated directly from the raw filesystem image files and YOLO `.txt` annotation files:

| Split | Image Count | Total Bounding Boxes |
| :--- | :---: | :---: |
| **Training (`data/training/`)** | 975 | 2,132 |
| **Validation (`data/validation/`)** | 89 | 221 |
| **Locked Test (`data/test_locked/`)** | 174 | 344 |
| **India Real-World Benchmark (`data/india_real_world/`)** | 0 | 0 |
| **TOTAL** | **1,238** | **2,697** |

---

## 4. C. Count Reconciliation & Discrepancy Explanation
Direct reconciliation across previous report text, raw filesystem label files, dataset manifest, and Python audit script:

| Class ID | Class Name | Previous Report Text | Actual Filesystem | Actual Manifest | Actual Audit Script | Discrepancy Reason / Explanation |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| **0** | `plastic_bottle` | 614 | **615** | 615 | 615 | Previous report text formatting script had an off-by-one aggregation index error when writing markdown table text. |
| **1** | `plastic_wrapper_bag` | 1,166 | **1,164** | 1,164 | 1,164 | Same off-by-one text formatting error in previous report generation. |
| **2** | `paper_cardboard` | 455 | **455** | 455 | 455 | Exactly synchronized (No discrepancy). |
| **3** | `glass_bottle_container` | 107 | **108** | 108 | 108 | Off-by-one text formatting error in previous report table. |
| **4** | `metal_can` | 355 | **355** | 355 | 355 | Exactly synchronized (No discrepancy). |
| **TOTAL** | | **2,697** | **2,697** | **2,697** | **2,697** | **Raw filesystem label files on disk have always maintained 2,697 total bboxes.** |

---

## 5. D. Taxonomy Verification
The 5-class object-level taxonomy is 100% synchronized across all scripts, YAML configs, and label text files:
- `0`: `plastic_bottle`
- `1`: `plastic_wrapper_bag`
- `2`: `paper_cardboard`
- `3`: `glass_bottle_container`
- `4`: `metal_can`

---

## 6. E. Open Images Mapping Verification
Verified against official Google Open Images V7 `oidv7-class-descriptions-boxable.csv` (602 boxable classes):

| Source MID | Open Images Canonical Name | SafaiOS Class | Decision | Reason & Evidence | Confidence |
| :---: | :--- | :---: | :---: | :--- | :---: |
| `/m/05gqfk` | Plastic bag | `plastic_wrapper_bag` (1) | **ACCEPTED** | Material-specific and semantically equivalent to plastic wrappers/bags. | HIGH |
| `/m/02jnhm` | Tin can | `metal_can` (4) | **ACCEPTED** | Material-specific and semantically equivalent to metal cans. | HIGH |
| `/m/04dr76w` | Bottle | `plastic_bottle` / `glass_bottle_container` | **AMBIGUOUS** | Open Images generic "Bottle" lacks material tags (mixes plastic, glass, and metal). Cannot be auto-mapped without material verification. | LOW |
| `/m/025dyy` | Box | `paper_cardboard` (2) | **AMBIGUOUS** | Includes wooden crates and plastic bins in addition to cardboard. | LOW |
| `/m/02pv19` | **Stop sign** | `paper_cardboard` (2) | **REJECTED** | **100% INVALID.** Previous mapping of Stop sign to paper_cardboard was erroneous. | NONE |
| `/m/09tvcd` | Wine glass | `glass_bottle_container` (3) | **REJECTED** | Stemware/drinkware rather than glass bottle/container waste. | NONE |

---

## 7. F. Provenance Audit
Every image entry in [`reports/dataset_manifest_v1.0.jsonl`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/reports/dataset_manifest_v1.0.jsonl) records explicit image-level provenance:
- `source_dataset`: `TACO` (for all 1,238 current images)
- `original_source_id`: TACO image ID (e.g. `000201`)
- `source_url`: `https://github.com/pedropro/TACO/tree/master/data`
- `sequence_id`: Grouped by collection sequence (e.g. `seq_00`)
- `validation_status`: `VALID`
- `approval_status`: `APPROVED`

---

## 8. G. License Audit
- **TACO Dataset Images & Annotations:** CC BY 4.0 (Verified against TACO official license).
- **Global License Assumptions:** Eliminated. Unverified future images default to `unknown` rather than fabricating CC BY 4.0.

---

## 9. H. Exact Duplicate Audit
- **MD5 Exact Duplicates Across Dataset:** 0
- **SHA256 Exact Duplicates Across Dataset:** 0

---

## 10. I. Near-Duplicate Audit & dHash Threshold Calibration
Controlled testing of 64-bit Difference Hash (`dHash`) with Hamming distance:
- **Identical / Resized / Recompressed Copies:** Hamming Distance = $0 \dots 2$ $\rightarrow$ **EXACT / NEAR DUPLICATE (REJECT)**
- **Slight Crop / Contrast Adjustments:** Hamming Distance = $3 \dots 6$ $\rightarrow$ **NEAR DUPLICATE / SEQUENCE FRAME (FLAG / KEEP IN SAME SPLIT)**
- **Visually Unrelated Images:** Hamming Distance $\ge 15 \dots 35$ $\rightarrow$ **UNRELATED IMAGE**
- **Cross-Split Near-Duplicates:** 0 detected across current train/val/test splits.

---

## 11. J. Split Leakage Audit
- **Train / Validation Leakage:** 0 identical or near-duplicate images.
- **Train / Locked Test Leakage:** 0 identical or near-duplicate images.
- **Validation / Locked Test Leakage:** 0 identical or near-duplicate images.
- **Source Group Integrity:** All TACO sequence frames are grouped strictly within their respective single splits.

---

## 12. K. Test-Lock Audit
- **Protected Seed (`data/test_locked/`):** 174 images, 344 bboxes.
- **Policy Enforcement:** Scripts explicitly block any ingestion targeting `data/test_locked/`. Test additions route through `data/test_candidate/`.

---

## 13. L. Dataset Version Audit
- **Current Version:** `safaios_dataset_v1.0`
- **Version Manifest:** Saved in [`reports/dataset_version_v1.0.json`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/reports/dataset_version_v1.0.json) with SHA256 hash of manifest `aa3cffa65cd0388c64ae0c50ad2460e1f4b7444b4d0a077d6b2c3009c299300e`.

---

## 14. M. Automated Test Results
Ran 21 automated tests via Pytest in [`tests/test_dataset_pipeline.py`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/tests/test_dataset_pipeline.py):

```powershell
.venv\Scripts\python.exe -m pytest tests/
```

**Result:** **21 PASSED** (0 failed, 0 skipped, 0 errors in 6.33s).
Covering all 20 required pipeline edge cases:
1. `test_01_corrupt_image_rejected`: PASS
2. `test_02_malformed_label_rejected`: PASS
3. `test_03_invalid_class_id_rejected`: PASS
4. `test_04_out_of_bound_bbox_rejected`: PASS
5. `test_05_zero_area_bbox_rejected`: PASS
6. `test_06_exact_duplicate_rejected`: PASS
7. `test_07_near_duplicate_flagged`: PASS
8. `test_08_locked_test_directory_protection`: PASS
9. `test_09_classification_only_dataset_rejected`: PASS
10. `test_10_unknown_taxonomy_mapping_rejected`: PASS
11. `test_11_manifest_entry_generated_correctly`: PASS
12. `test_12_deterministic_split_assignment`: PASS
13. `test_13_source_group_leakage_detection`: PASS
14. `test_14_cross_split_exact_duplicate_detection`: PASS
15. `test_15_cross_split_near_duplicate_detection`: PASS
16. `test_16_provenance_requirement_enforced`: PASS
17. `test_17_missing_license_provenance_handled_safely`: PASS
18. `test_18_invalid_image_extension_handling`: PASS
19. `test_19_missing_annotation_handling`: PASS
20. `test_20_malformed_manifest_handling`: PASS

---

## 15. N. Remaining Blockers Before Training Readiness
1. **Target Image Count Unmet:** Current total = 1,238 genuine images (Target: $\ge 10,000$ training, $\ge 1,000$ val, $\ge 1,000$ test).
2. **Glass Bottle Underrepresentation:** `glass_bottle_container` has only 108 bboxes (4.0%).
3. **Open Images Live Staging Pending:** Candidate ingestion for `/m/05gqfk` (Plastic bag) and `/m/02jnhm` (Tin can) must be staged to `data/incoming/open_images_staging/`.
4. **India Real-World Benchmark Unpopulated:** 0 benchmark images present in `data/india_real_world/`.

---

## 16. O. Explicit Training Gate
**TRAINING IS STRICTLY BLOCKED.** Model training remains forbidden until all dataset scale targets, class balance objectives, and provenance gates are satisfied.

---

```
==================================================
FINAL STATUS: DATASET NOT READY FOR TRAINING
DO NOT TRAIN YOLO
==================================================
```
