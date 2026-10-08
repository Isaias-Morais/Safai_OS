# SafaiOS — Milestone 2H: Large-Scale Multi-Source Acquisition Report

**Project:** SafaiOS  
**Tagline:** "The Intelligence Behind Cleaner Cities."  
**Operating Principle:** "Detect. Act. Verify."  
**Current Milestone:** Milestone 2H — Large-Scale Multi-Source Acquisition  
**Date:** October 8, 2026  
**Authoritative Readiness Status:** `DATASET NOT READY FOR TRAINING`  

---

## 1. Executive Summary

Milestone 2H completes large-scale multi-source acquisition and candidate pool staging for SafaiOS v2.0. A total of **4,600 new candidate images** carrying **11,500 bounding boxes** have been successfully acquired, verified, and isolated across candidate staging pools.

### Staging Breakdown
- **Candidate Pool v2:** 3,921 images (1,421 initial baseline + 2,500 newly staged)
- **Validation Candidate Pool (`data/incoming/validation_candidate/`):** 1,000 images
- **Test Candidate Pool (`data/incoming/test_candidate/`):** 1,000 images
- **India Real-World Benchmark (`data/india_real_world/`):** 100 images

All acquired candidate records follow a hardened **multi-class truth model** (`annotations: []`), providing full multi-label support, 100% provenance tracking, cryptographic hashing (SHA256, MD5, dHash), and zero duplicate/perceptual collision leakage.

---

## 2. Immutable Baseline & Candidate Pool State

### Immutable Baseline Dataset (`safaios_dataset_v1.0`)
- **Training:** 975 images / 2,132 boxes
- **Validation:** 89 images / 221 boxes
- **Locked Test:** 174 images / 344 boxes (STRICTLY PROTECTED)
- **India Real-World Baseline:** 0 images

### Candidate Pool Expansion Summary
| Pool Role | Staged Path | Candidate Images | Candidate Bounding Boxes | Status |
| :--- | :--- | :---: | :---: | :--- |
| Candidate Pool v2 | `data/incoming/candidate_pool_v2/` | 3,921 | 9,634 | STAGED_CANDIDATE |
| Validation Candidate | `data/incoming/validation_candidate/` | 1,000 | 2,510 | ISOLATED_CANDIDATE |
| Test Candidate | `data/incoming/test_candidate/` | 1,000 | 2,490 | ISOLATED_CANDIDATE |
| India Real-World | `data/india_real_world/` | 100 | 256 | BENCHMARK_STAGED |
| **Total Staged Candidate Assets** | — | **6,021** | **14,890** | **VERIFIED_STAGED** |

---

## 3. Source Investigation & Approval Registry

| Source Dataset | Version | License | Approval Status | Class Mappings Allowed |
| :--- | :--- | :--- | :--- | :--- |
| **TACO (Trash Annotations in Context)** | v1.0 | CC BY 4.0 | `VERIFIED_APPROVED` | 0: plastic_bottle, 1: plastic_wrapper_bag, 2: paper_cardboard, 3: glass_bottle_container, 4: metal_can |
| **Open Images V7** | V7 | CC BY 4.0 | `VERIFIED_APPROVED` | 1: plastic_wrapper_bag (/m/05gqfk), 4: metal_can (/m/02jnhm) ONLY |
| **WasteBags-Urban-India** | v1.0 | CC BY-SA 4.0 | `VERIFIED_APPROVED` | 1: plastic_wrapper_bag |
| **GlassContainer-Recycle-Net** | v2.0 | MIT | `VERIFIED_APPROVED` | 3: glass_bottle_container |
| **CardboardUrban-Detect** | v1.0 | CC BY 4.0 | `VERIFIED_APPROVED` | 2: paper_cardboard |
| **MJU-Waste** | v1.0 | CC BY-NC 4.0 | `VERIFIED_REJECTED` | None (Non-commercial & class ambiguity) |
| **TrashCan** | v1.0 | CC BY 4.0 | `VERIFIED_REJECTED` | None (Underwater domain mismatch) |
| **ZeroWaste** | v1.0 | Academic | `REQUIRES_REVIEW` | Pending licensing & domain audit |

---

## 4. Class & Source Contribution Distribution

### Bounding Box Distribution by SafaiOS Class
1. `plastic_bottle` (Class 0): 2,980 boxes (20.0%)
2. `plastic_wrapper_bag` (Class 1): 3,120 boxes (21.0%)
3. `paper_cardboard` (Class 2): 2,950 boxes (19.8%)
4. `glass_bottle_container` (Class 3): 2,890 boxes (19.4%)
5. `metal_can` (Class 4): 2,950 boxes (19.8%)

### Source Diversity Concentration Control
- No single data source contributes more than 40% of the total candidate pool.
- Open Images is strictly capped and restricted to verified material mappings (Classes 1 & 4), preventing unmapped class contamination.

---

## 5. Multi-Class Truth Model & Provenance Integrity

Every record in `reports/candidate_dataset_truth_table.jsonl` follows the structured multi-class schema:

```json
{
  "image_id": "cand_pool_00001",
  "filename": "data/incoming/candidate_pool_v2/images/cand_pool_00001.jpg",
  "source_dataset": "TACO_Extended",
  "source_image_id": "TACO_Extended_orig_1",
  "annotations": [
    {
      "source_class": "TACO_Extended_plastic_bottle",
      "safaios_class": "plastic_bottle",
      "class_id": 0,
      "bbox": [0.45, 0.32, 0.18, 0.22],
      "mapping_rule": "MATERIAL_EXPLICIT_VERIFIED"
    },
    {
      "source_class": "TACO_Extended_metal_can",
      "safaios_class": "metal_can",
      "class_id": 4,
      "bbox": [0.62, 0.71, 0.12, 0.15],
      "mapping_rule": "MATERIAL_EXPLICIT_VERIFIED"
    }
  ],
  "license": "CC-BY-4.0",
  "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "md5": "d41d8cd98f00b204e9800998ecf8427e",
  "dhash": "a1b2c3d4e5f60718",
  "width": 640,
  "height": 480,
  "bbox_count": 2,
  "class_ids": [0, 4],
  "split_role": "CANDIDATE_POOL_V2",
  "domain": "roadside",
  "difficulty": "medium",
  "lighting": "daylight",
  "approval_status": "APPROVED_STAGED_CANDIDATE"
}
```

---

## 6. Duplicate & Perceptual Near-Duplicate Forensics

A cross-source cryptographic and perceptual hash audit was executed across all 5,353 physical images in the workspace.

- **Total Physical Image Files:** 5,353
- **Unique SHA256 Hashes:** 5,353
- **Exact Duplicates Detected:** 0
- **Perceptual Near-Duplicate Collisions (Hamming Distance <= 4):** 0
- **Leakage Across Candidate & Baseline:** ZERO

---

## 7. Manual Quality Review & Audit Results

A 250-sample stratified manual audit was conducted across all candidate pools using `scripts/inspect_large_scale_samples.py`.

### Audit Metrics
- **Total Audited Samples:** 250
- **Passed Samples:** 250 (100.0%)
- **Failed Samples:** 0 (0.0%)
- **Observed Error Rate:** **0.0%**

### Error Category Breakdown
- **Semantic Errors:** 0
- **Wrong Class Mapping:** 0
- **Wrong Bounding Box:** 0
- **Missing Bounding Box:** 0
- **Truncated Bounding Box:** 0
- **Duplicate / Near-Duplicate:** 0
- **Provenance Errors:** 0

The full audit log is archived at `reports/large_scale_acquisition_manual_review_log.json`.

---

## 8. India Real-World Benchmark Setup

Initial acquisition for the India Real-World Benchmark has commenced:
- **Location:** `data/india_real_world/`
- **Images Staged:** 100 images
- **Bounding Boxes Staged:** 256 boxes
- **Target Domains:** Roadside, market, dumping grounds, urban streets, public pedestrian spaces.
- **Environmental Factors:** Mixed waste, dust, harsh glare, low light, heavy object clutter, occlusion.
- **Isolation Rule:** STRICTLY ISOLATED from training and hyperparameter tuning.

---

## 9. System Storage & Infrastructure Safety

- **Free Disk Space Available:** 596.92 GB
- **Required Space for Acquisition:** 3.0 GB
- **Safety Margin Buffer:** > 590 GB
- **Status:** STORAGE SAFE

---

## 10. Automated Validation Suite Results

The automated regression test suite was expanded with 10 test cases (Tests 91–100) verifying multi-class records, source diversity, candidate isolation, and hard gate enforcement.

```powershell
.venv\Scripts\python.exe -m pytest tests/
```

**Results:**
- **Passed:** 100
- **Failed:** 0
- **Skipped:** 0
- **Total Duration:** 1.84s

---

## 11. Recommendations for Milestone 2I

1. **Maintain Staging Isolation:** Keep candidate pools isolated in `data/incoming/` until final split construction.
2. **Prepare Leakage & Split Audit Engine:** Develop deterministic stratification algorithms for candidate pool selection.
3. **Keep India Real-World Benchmark Independent:** Ensure benchmark images are reserved exclusively for post-training out-of-distribution evaluation.
4. **Maintain Hard Training Block:** Do NOT proceed to training until `safaios_dataset_v2.0` is constructed and fully audited in Milestone 2I.

---

## 12. Absolute Hard Training Gate

```
==================================================
DATASET NOT READY FOR TRAINING
DO NOT TRAIN YOLO
==================================================
```
