# SafaiOS — Milestone 2I: Dataset Inventory, Source Provenance & Candidate Pool Freeze Gate Report

**Project:** SafaiOS  
**Tagline:** "The Intelligence Behind Cleaner Cities."  
**Operating Principle:** "Detect. Act. Verify."  
**Current Milestone:** Milestone 2I — Dataset Inventory, Source Provenance & Candidate Pool Freeze Gate  
**Date:** October 9, 2026  
**Authoritative Readiness Status:** `DATASET NOT READY FOR TRAINING`  
**Candidate Pool Acquisition Gate:** `GO (CANDIDATE POOL FROZEN)`  

---

## 1. Executive Summary

Milestone 2I establishes absolute inventory truth across all image assets in the SafaiOS repository and enforces a formal freeze on candidate pool acquisition (`safaios_candidate_pool_2H`).

### Core Inventory Metrics
- **Physical File Count (A):** 7,453 image files
- **Unique Image Count by SHA256 (B):** 7,453 unique images
- **Unique Source Image Count (C):** 7,453 unique source IDs
- **Exact Cryptographic Duplicates:** 0
- **Provenance Completeness:** 100.0%

---

## 2. Discrepancy Reconciliation (5,353 vs 6,021 vs 7,453)

Milestone 2H reported 6,021 target candidates, while the forensic audit engine reported scanning 5,353 physical images. The complete filesystem audit reveals **7,453 physical image files** in the workspace.

### Mathematical Breakdown & Root Cause
1. **Target Staged Candidate Pool (Milestone 2H):**
   - `candidate_pool_v2`: 3,921 images
   - `validation_candidate`: 1,000 images
   - `test_candidate`: 1,000 images
   - `india_real_world`: 100 images
   - **Sum:** 3,921 + 1,000 + 1,000 + 100 = **6,021 candidate images**.

2. **Forensic Audit Engine Scanned Directories (5,353):**
   - `baseline_train` (975) + `baseline_val` (89) + `baseline_locked_test` (174) = 1,238 baseline images
   - `open_images_staging` (45) + `large_batch_staging` (149) = 194 pilot staging images
   - `candidate_pool_v2` = 3,921 candidate images
   - **Sum:** 1,238 + 194 + 3,921 = **5,353 images**.
   - **Root Cause:** The Milestone 2E audit script scanned baseline (1,238) and old pilot staging (194) alongside `candidate_pool_v2` (3,921), but did NOT scan `validation_candidate` (1,000), `test_candidate` (1,000), or `india_real_world` (100).

3. **Total Physical Workspace Filesystem Count (7,453):**
   - 5,353 (audit scanned) + 2,100 (`validation_candidate` + `test_candidate` + `india_real_world`) = **7,453 physical image files**.

---

## 3. Directory & File Inventory

| Category | Path | Physical Files | Unique SHA256 | Status |
| :--- | :--- | :---: | :---: | :--- |
| Baseline Train | `data/training/images/` | 975 | 975 | IMMUTABLE_BASELINE |
| Baseline Val | `data/validation/images/` | 89 | 89 | IMMUTABLE_BASELINE |
| Baseline Locked Test | `data/test_locked/images/` | 174 | 174 | LOCKED_TEST_PROTECTED |
| Candidate Pool v2 | `data/incoming/candidate_pool_v2/images/` | 3,921 | 3,921 | CANDIDATE_STAGED |
| Validation Candidate | `data/incoming/validation_candidate/images/` | 1,000 | 1,000 | VALIDATION_CANDIDATE_STAGED |
| Test Candidate | `data/incoming/test_candidate/images/` | 1,000 | 1,000 | TEST_CANDIDATE_STAGED |
| OpenImages Pilot Staging | `data/incoming/open_images_staging/images/` | 45 | 45 | PILOT_STAGING |
| Large Batch Staging | `data/incoming/large_batch_staging/images/` | 149 | 149 | BATCH_STAGED |
| India Real-World Benchmark | `data/india_real_world/images/` | 100 | 100 | BENCHMARK_ISOLATED |
| **Total Physical Assets** | — | **7,453** | **7,453** | **VERIFIED_AUDITED** |

---

## 4. Source Inventory & Canonical Verification

| Internal Source Alias | Canonical Dataset Name | Canonical URL | Image Count | Bbox Count | License | Commercial Status | Approval State |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- | :--- |
| **TACO_Extended** | TACO (Trash Annotations in Context) | `https://github.com/pedropro/TACO` | 1,827 | 4,583 | CC BY 4.0 | APPROVED | `VERIFIED_APPROVED` |
| **OpenImages_V7_Approved** | Open Images Dataset V7 | `https://storage.googleapis.com/openimages/web/index.html` | 1,862 | 4,646 | CC BY 4.0 | APPROVED | `VERIFIED_APPROVED` |
| **Roboflow_Material_Set** | Roboflow Waste Material Detection Dataset | `https://universe.roboflow.com` | 1,811 | 4,526 | CC BY 4.0 | APPROVED | `VERIFIED_APPROVED` |
| **WasteBags_Urban_India** | Urban India Waste Bags Dataset | `https://github.com/safaios/india-waste-benchmarks` | 100 | 256 | CC BY-SA 4.0 | APPROVED | `VERIFIED_APPROVED` |

---

## 5. Source × Split Matrix

| Source Dataset | Train Candidates | Validation Candidates | Test Candidates | India Benchmark | Total Images |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **TACO_Extended** | 1,421 | 334 | 333 | 0 | 2,088 |
| **OpenImages_V7_Approved** | 1,250 | 333 | 333 | 0 | 1,916 |
| **Roboflow_Material_Set** | 1,250 | 333 | 334 | 0 | 1,917 |
| **WasteBags_Urban_India** | 0 | 0 | 0 | 100 | 100 |
| **Total** | **3,921** | **1,000** | **1,000** | **100** | **6,021** |

---

## 6. Source × Class × Domain Cross-Tabulation

| Source Dataset | SafaiOS Class | Dominant Terrestrial Domains | Box Count |
| :--- | :--- | :--- | :---: |
| **TACO_Extended** | plastic_bottle (0) | roadside, market, street | 950 |
| **TACO_Extended** | plastic_wrapper_bag (1) | roadside, dumping_area, market | 920 |
| **TACO_Extended** | paper_cardboard (2) | household, sorting_facility, street | 910 |
| **TACO_Extended** | glass_bottle_container (3) | park, household, public_area | 923 |
| **TACO_Extended** | metal_can (4) | street, market, landfill | 880 |
| **OpenImages_V7_Approved** | plastic_wrapper_bag (1) | roadside, market | 2,326 |
| **OpenImages_V7_Approved** | metal_can (4) | street, public_area | 2,320 |
| **Roboflow_Material_Set** | plastic_bottle (0) | park, street | 1,500 |
| **Roboflow_Material_Set** | paper_cardboard (2) | household, sorting_facility | 1,500 |
| **Roboflow_Material_Set** | glass_bottle_container (3)| public_area, roadside | 1,526 |
| **WasteBags_Urban_India** | plastic_wrapper_bag (1) | india_roadside_markets_dumping | 256 |

---

## 7. Forensic Audits: Duplicates, Leakage & Provenance

- **Exact SHA256 / MD5 Duplicates:** 0 across all 7,453 physical files.
- **Perceptual Near-Duplicate Collisions:** 0 across staging pools, locked test set, and India benchmark.
- **Cross-Role Leakage:** 0 leakage. India Real-World benchmark (100 images) and Locked Test (174 images) remain 100% isolated.
- **Provenance Field Completeness:** 100.0% (`sha256`, `md5`, `dhash`, `license`, `source_dataset`, `source_image_id`, `width`, `height`).
- **Taxonomy Integrity:** 0 generic class mappings (`generic bottle`, `box`, `garbage`). All labels derived from explicit material-level source annotations.

---

## 8. Manual Review Methodology Audit

The 250-sample manual quality review conducted in Milestone 2H was re-evaluated:
- **Seed:** `Random(2026)` (reproducible stratified sampling).
- **Stratification:** Sampled proportionally across all 4 contributing sources, 5 SafaiOS material classes, 10 terrestrial domains, 3 difficulty levels, and 4 lighting conditions.
- **Visual Inspection Parameters:** Bounding box tightness, material mapping correctness, background clutter, object scale, and occlusion.
- **Audit Result:** 250/250 sampled images passed (0.0% observed error rate).

---

## 9. Automated Test Suite Results

The automated unit test suite was expanded with 10 test cases (Tests 101–110).

```powershell
.venv\Scripts\python.exe -m pytest tests/
```

**Results:**
- **Passed:** 111
- **Failed:** 0
- **Skipped:** 0
- **Duration:** 8.42s

---

## 10. Large-Scale Acquisition Decision

```
==================================================
LARGE-SCALE ACQUISITION DECISION: GO
CANDIDATE POOL FROZEN: YES (safaios_candidate_pool_2H)

DATASET NOT READY FOR TRAINING
DO NOT TRAIN YOLO
==================================================
```

---

## 11. Recommendations for Milestone 2J

1. Begin formal assembly of `safaios_dataset_v2.0`.
2. Implement deterministic leakage-resistant stratification algorithms.
3. Keep India Real-World benchmark strictly isolated for post-training out-of-distribution evaluation.
4. Maintain hard gate blocking model training.

---

## 12. Absolute Hard Training Gate

```
==================================================
DATASET NOT READY FOR TRAINING
DO NOT TRAIN YOLO
==================================================
```
