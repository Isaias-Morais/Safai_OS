# SafaiOS Dataset Engineering & Scaling Report — Milestone 1

**Date:** 2026-10-08  
**Project:** SafaiOS — "The Intelligence Behind Cleaner Cities."  
**Operating Principle:** Detect. Act. Verify.  
**Milestone:** Milestone 1 — Dataset Engineering & Scaling  
**Status:** DATASET NOT READY FOR TRAINING  

---

## 1. What Was Inspected
The complete repository structure, script suite, dataset configs, label files, and data directories were forensically audited to establish ground truth:
- **Repository Tree & Structure:** Verified `data/incoming/`, `data/training/`, `data/validation/`, `data/test_locked/`, and `data/india_real_world/`.
- **Scripts:** Audited [`scripts/process_incoming.py`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/scripts/process_incoming.py), [`scripts/ingest_taco_yolo.py`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/scripts/ingest_taco_yolo.py), [`scripts/inspect_dataset.py`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/scripts/inspect_dataset.py).
- **Configurations:** Inspected [`configs/dataset.yaml`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/configs/dataset.yaml) and [`configs/training.yaml`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/configs/training.yaml).
- **Taxonomy:** Confirmed 5-class object-level taxonomy is synchronized across all scripts, YAML configs, and YOLO label files:
  - `0`: `plastic_bottle`
  - `1`: `plastic_wrapper_bag`
  - `2`: `paper_cardboard`
  - `3`: `glass_bottle_container`
  - `4`: `metal_can`

---

## 2. What Was Changed
1. **Perceptual Deduplication Engine Built:** Created [`src/data/hashing.py`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/src/data/hashing.py) supporting MD5, SHA256, and 64-bit dHash (Difference Hash) with Hamming distance matching (threshold <= 6 for near-duplicate identification).
2. **Dataset Manifest System Implemented:** Created [`src/data/manifest.py`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/src/data/manifest.py) generating line-delimited JSON manifest [`reports/dataset_manifest_v1.0.jsonl`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/reports/dataset_manifest_v1.0.jsonl) with 1,238 entries detailing sha256, md5, perceptual_hash, width, height, bbox_count, class_ids, split, license, and provenance.
3. **Data Lifecycle Pipeline Hardened:** Refactored [`scripts/process_incoming.py`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/scripts/process_incoming.py) with full state transition enforcement (`RAW -> DISCOVERED -> VALIDATED -> ANNOTATED -> QUALITY_CHECKED -> DEDUPLICATED -> APPROVED -> SPLIT_ASSIGNED -> DATASET_VERSION`).
4. **Test-Set Locking Policy Enforced:** Protected `data/test_locked/` with [`data/test_locked/LOCKED_TEST_SET_POLICY.md`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/data/test_locked/LOCKED_TEST_SET_POLICY.md) and introduced `data/test_candidate/` for safe future expansion.
5. **India Real-World Benchmark Isolated:** Created `data/india_real_world/` structure and [`data/india_real_world/README.md`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/data/india_real_world/README.md) strictly for domain transfer benchmarking.
6. **Open Images V7 Mapping Defined:** Created mapping strategy for Open Images V7 bounding boxes to SafaiOS 5-class taxonomy.
7. **Automated Test Suite Built:** Created [`tests/test_dataset_pipeline.py`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/tests/test_dataset_pipeline.py) covering validation, deduplication, taxonomy checks, test set protection, and deterministic split logic.

---

## 3. Files Created / Modified
- **Created:**
  - [`src/data/hashing.py`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/src/data/hashing.py)
  - [`src/data/manifest.py`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/src/data/manifest.py)
  - [`data/test_locked/LOCKED_TEST_SET_POLICY.md`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/data/test_locked/LOCKED_TEST_SET_POLICY.md)
  - [`data/india_real_world/README.md`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/data/india_real_world/README.md)
  - [`tests/test_dataset_pipeline.py`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/tests/test_dataset_pipeline.py)
  - [`reports/dataset_manifest_v1.0.jsonl`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/reports/dataset_manifest_v1.0.jsonl)
- **Modified:**
  - [`scripts/process_incoming.py`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/scripts/process_incoming.py)
  - [`scripts/inspect_dataset.py`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/scripts/inspect_dataset.py)
  - [`configs/dataset.yaml`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/configs/dataset.yaml)

---

## 4. Actual Image Counts
- **Training Set (`data/training/images`):** 975 images
- **Validation Set (`data/validation/images`):** 89 images
- **Locked Test Set (`data/test_locked/images`):** 174 images
- **India Real-World Benchmark (`data/india_real_world/images`):** 0 images (structure initialized, awaiting genuine field images)
- **Total Genuine Images:** 1,238 images (Target: >= 12,100 total)

---

## 5. Actual Bounding Box Counts
- **Training Set:** 2,132 bboxes
- **Validation Set:** 221 bboxes
- **Locked Test Set:** 344 bboxes
- **Total Bounding Boxes:** 2,697 bboxes

---

## 6. Class Distribution
- **Class 0 (`plastic_bottle`):** 614 bboxes (22.8%)
- **Class 1 (`plastic_wrapper_bag`):** 1,166 bboxes (43.2%)
- **Class 2 (`paper_cardboard`):** 455 bboxes (16.9%)
- **Class 3 (`glass_bottle_container`):** 107 bboxes (4.0%)  *(CRITICAL UNDERREPRESENTATION)*
- **Class 4 (`metal_can`):** 355 bboxes (13.2%)

---

## 7. Exact Duplicate Results
- **MD5 Exact Duplicates Across Dataset:** 0
- **SHA256 Exact Duplicates Across Dataset:** 0

---

## 8. Near-Duplicate Results
- **dHash Perceptual Clusters (Hamming distance <= 6):** Audited across all 1,238 images.
- **Cross-Split Near-Duplicates:** 0 detected.
- **Within-Split Sequences:** Near-sequential video frames identified within TACO source sequences and preserved strictly within single splits.

---

## 9. Leakage Results
- **Train / Validation Leakage:** 0 identical or near-duplicate images.
- **Train / Locked Test Leakage:** 0 identical or near-duplicate images.
- **Validation / Locked Test Leakage:** 0 identical or near-duplicate images.

---

## 10. Source / Provenance Coverage
- **TACO Dataset (CC BY 4.0):** 1,238 images (100% of current version).
- **Unknown / Unverified Provenance Images:** 0.

---

## 11. Licensing Verification Status
- **TACO Images & Bounding Boxes:** CC BY 4.0 (Verified & Documented).
- **TrashNet:** EXCLUDED from YOLO detection training (classification-only without bounding boxes).

---

## 12. Split Strategy
- **Grouping Logic:** Source sequence / dataset collection ID grouping.
- **Deterministic Seed:** 42.
- **Split Ratio Target:** ~80% Train / ~10% Validation / ~10% Test.

---

## 13. Test-Set Protection Status
- **Status:** STRICTLY LOCKED (`data/test_locked/`).
- **Policy Enforcement:** Automated scripts explicitly block `data/test_locked/` modification. Future additions must route through `data/test_candidate/` and an explicit one-time freeze command.

---

## 14. India Real-World Benchmark Status
- **Status:** Initialized (`data/india_real_world/`).
- **Image Count:** 0 images currently present. Requires 100–500+ genuine Indian street/waste images prior to evaluation.

---

## 15. Dataset Version Status
- **Current Version:** `safaios_dataset_v1.0`
- **Tracked In:** [`reports/dataset_manifest_v1.0.jsonl`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/reports/dataset_manifest_v1.0.jsonl)
- **Version Integrity:** Hash-indexed manifest tracking SHA256 + dHash for all 1,238 images.

---

## 16. Tests Executed and Results
- **Command Executed:** `.venv\Scripts\python.exe -m pytest tests/`
- **Result:** **4 PASSED** (0 failures, 0 errors).
  - `test_valid_bbox_and_taxonomy`: PASS
  - `test_dhash_near_duplicate_detection`: PASS
  - `test_test_locked_isolation_policy`: PASS
  - `test_manifest_generation`: PASS

---

## 17. Remaining Blockers
1. **Training Target Unmet:** Current total genuine images = 1,238 (Target: >= 10,000 training, >= 1,000 val, >= 1,000 test).
2. **Severe Class Imbalance:** `glass_bottle_container` represents only 4.0% of total annotations (107 bboxes).
3. **Open Images Ingestion Pending:** Open Images V7 bounding boxes for `glass_bottle_container`, `metal_can`, and `paper_cardboard` must be fetched and processed.
4. **India Real-World Benchmark Unpopulated:** 0 benchmark images currently present.

---

## 18. Whether Training Is Allowed
**NO.** Training is strictly forbidden until all dataset scale, distribution, and gate requirements are genuinely satisfied.

---

```
==================================================
FINAL STATUS: DATASET NOT READY FOR TRAINING
DO NOT TRAIN YOLO
==================================================
```
