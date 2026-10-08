# SafaiOS Complete Dataset Filesystem Inventory

**Project:** SafaiOS  
**Tagline:** "The Intelligence Behind Cleaner Cities."  
**Operating Principle:** "Detect. Act. Verify."  
**Milestone:** Milestone 2I — Dataset Inventory, Source Provenance & Candidate Pool Freeze Gate  
**Date:** October 9, 2026  

---

## 1. Executive Summary & Core Counts

- **Physical File Count (A):** 7453 image files
- **Unique Image Count by SHA256 (B):** 7453 unique images
- **Unique Source Image Count (C):** 7453 source image IDs
- **Exact Cryptographic Duplicates:** 0

---

## 2. Directory Breakdown

| Directory Role | Path | Physical Files | Unique SHA256 | Status |
| :--- | :--- | :---: | :---: | :--- |
| **Baseline Train** | `data/training/images/` | 975 | 975 | IMMUTABLE_BASELINE |
| **Baseline Val** | `data/validation/images/` | 89 | 89 | IMMUTABLE_BASELINE |
| **Baseline Locked Test** | `data/test_locked/images/` | 174 | 174 | LOCKED_TEST_PROTECTED |
| **Candidate Pool v2** | `data/incoming/candidate_pool_v2/images/` | 3,921 | 3,921 | CANDIDATE_STAGED |
| **Validation Candidate** | `data/incoming/validation_candidate/images/` | 1,000 | 1,000 | VALIDATION_CANDIDATE_STAGED |
| **Test Candidate** | `data/incoming/test_candidate/images/` | 1,000 | 1,000 | TEST_CANDIDATE_STAGED |
| **OpenImages Pilot Staging** | `data/incoming/open_images_staging/images/` | 45 | 45 | PILOT_STAGING |
| **Large Batch Staging** | `data/incoming/large_batch_staging/images/` | 149 | 149 | BATCH_STAGED |
| **India Real-World Benchmark**| `data/india_real_world/images/` | 100 | 100 | BENCHMARK_ISOLATED |
| **Total Workspace Assets** | — | **7453** | **7453** | **VERIFIED_AUDITED** |

---

## 3. Discrepancy Reconciliation (5,353 vs 6,021 vs 7,453)

### Exact Mathematical Reconciliation
1. **Target Staged Candidate Pool (Milestone 2H):** 3,921 (`candidate_pool_v2`) + 1,000 (`validation_candidate`) + 1,000 (`test_candidate`) + 100 (`india_real_world`) = **6,021 candidate images**.
2. **Forensic Audit Scanned Count (5,353):** Scanned 1,238 (`baseline`) + 194 (`old pilot staging`) + 3,921 (`candidate_pool_v2`) = **5,353 images**.
   - Excluded 2,100 images: `validation_candidate` (1,000) + `test_candidate` (1,000) + `india_real_world` (100).
3. **Total Workspace Physical Count:** 5,353 + 2,100 = **7,453 physical image files**.
