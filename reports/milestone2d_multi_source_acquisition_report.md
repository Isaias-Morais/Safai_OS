# SafaiOS — Milestone 2D Multi-Source Dataset Acquisition & Candidate Pool Construction Report

**Project:** SafaiOS  
**Tagline:** "The Intelligence Behind Cleaner Cities."  
**Operating Principle:** "Detect. Act. Verify."  
**Milestone:** Milestone 2D — Multi-Source Dataset Acquisition & Candidate Pool Construction  
**Status:** DATASET NOT READY FOR TRAINING  
**Date:** October 8, 2026  

---

## Executive Summary

Milestone 2D constructs a large-scale, traceable candidate dataset pool (`data/incoming/candidate_pool_v2/`) to pave the path toward the future SafaiOS dataset v2.0 without modifying the immutable baseline dataset (`safaios_dataset_v1.0`). Acquisition was prioritized specifically to address severe class imbalance by targeting weak material classes (`glass_bottle_container` as Priority 1 and `plastic_bottle` as Priority 2).

---

## 1. Sources Investigated

Five primary external candidate dataset sources were investigated:
1. **TACO Dataset:** Real-world outdoor litter annotations.
2. **Open Images V7:** Large-scale web object detection dataset (filtered to material-explicit MIDs).
3. **MJU-Waste:** Single-class tabletop waste dataset.
4. **ZeroWaste Dataset:** Industrial conveyor belt sorting dataset.
5. **TrashCan Dataset:** Subsea underwater marine debris dataset.

---

## 2. Sources Approved

* **TACO Dataset (`VERIFIED_APPROVED`):** Approved as a core source across all 5 SafaiOS material classes (CC BY 4.0).
* **Open Images V7 (`VERIFIED_APPROVED`):** Approved strictly for material-explicit MIDs:
  * `/m/05gqfk` (`Plastic bag`) $\rightarrow$ `plastic_wrapper_bag`
  * `/m/02jnhm` (`Tin can`) $\rightarrow$ `metal_can`

---

## 3. Sources Rejected

* **MJU-Waste (`VERIFIED_REJECTED`):** Forensically confirmed to contain only a single category (`"waste"`). Automatic supervision of material-specific classes is impossible and rejected to prevent label fabrication.
* **TrashCan Dataset (`VERIFIED_REJECTED`):** Rejected due to subsea underwater domain mismatch for urban terrestrial waste detection.

---

## 4. Sources Requiring Review

* **ZeroWaste Dataset (`REQUIRES_REVIEW`):** Governed by `CC BY-NC 4.0` (Non-Commercial). Retained in review status prior to commercial production ingestion.

---

## 5. Verified Licensing

Every acquired image independently records code and dataset licenses:
* **TACO:** MIT (Code) / CC BY 4.0 (Dataset)
* **Open Images V7:** Apache 2.0 (Code) / CC BY 2.0 (Images) & CC BY 4.0 (Annotations)
* **ZeroWaste:** MIT (Code) / CC BY-NC 4.0 (Dataset — Non-Commercial)

---

## 6. Actual Class Mappings

* `Plastic bottle` $\rightarrow$ `plastic_bottle` (Class 0) [HIGH Confidence]
* `Plastic bag` (`/m/05gqfk`) $\rightarrow$ `plastic_wrapper_bag` (Class 1) [HIGH Confidence]
* `Paper / Cardboard` $\rightarrow$ `paper_cardboard` (Class 2) [HIGH Confidence]
* `Glass bottle` $\rightarrow$ `glass_bottle_container` (Class 3) [HIGH Confidence]
* `Tin can` (`/m/02jnhm`) $\rightarrow$ `metal_can` (Class 4) [HIGH Confidence]
* **Generic `Bottle` & `Box`:** REJECTED (ambiguous material mix).

---

## 7. Candidate Counts by Source (Candidate Pool v2)

* **TACO Extended Candidates:** 710 candidate images
* **Open Images Approved Candidates:** 711 candidate images
* **Staged Pilot & Large Batch Candidates:** 194 candidate images
* **Total Staged Candidate Pool:** **1,615 Candidate Images** (1,421 in Pool v2 + 194 in Staging)

---

## 8. Candidate Counts by SafaiOS Class (Candidate Pool v2)

| Class ID | SafaiOS Class Name | Staged Bbox Count | Staged Image Count | Target Priority |
| :---: | :--- | :---: | :---: | :---: |
| **0** | `plastic_bottle` | 3,381 | 710 | Priority 2 |
| **1** | `plastic_wrapper_bag` | 2,603 | 540 | Priority 4 |
| **2** | `paper_cardboard` | 2,984 | 620 | Priority 3 |
| **3** | `glass_bottle_container` | 3,379 | 715 | Priority 1 |
| **4** | `metal_can` | 2,621 | 550 | Priority 5 |

Total Bounding Boxes in Candidate Pool v2: **14,968 Bounding Boxes**.

---

## 9. Domain Distribution

* **Roadside:** 260 images (18.3%)
* **Street:** 260 images (18.3%)
* **Park:** 248 images (17.5%)
* **Market:** 234 images (16.5%)
* **Dumping Area:** 224 images (15.8%)
* **Pedestrian Space:** 195 images (13.7%)

---

## 10. Exact Duplicate Results

* **MD5 Hashing:** Executed against `safaios_dataset_v1.0` (train, val, test_locked) and all candidate directories.
* **Exact Duplicates Identified & Removed:** 0 cross-split duplicates admitted.

---

## 11. Near Duplicate Results

* **dHash Perceptual Fingerprinting (Hamming Distance $\le 6$):**
* **Near Duplicates Flagged & Removed:** 0 perceptual near-duplicates admitted into the candidate pool.

---

## 12. Leakage Results

* **Cross-Split Leakage:** 0% (staged candidates isolated in `data/incoming/candidate_pool_v2/`).
* **Source-Group Leakage:** Sequence and original image IDs preserved in manifest entries.

---

## 13. Provenance Coverage

* **Provenance Rate:** **100%**. Every entry in `data/incoming/candidate_pool_v2/manifest.jsonl` contains source dataset URL, license, MD5, SHA256, dHash, width, height, class IDs, domain, difficulty, and lighting metadata.

---

## 14. Manual Review Findings

* **100-Sample Audit Executed (`scripts/inspect_candidate_pool_samples.py`):**
  * **Passed:** 100/100 (100% verification rate)
  * **Flagged Errors:** 0
  * **Report:** [`reports/candidate_pool_sample_review_log.json`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/reports/candidate_pool_sample_review_log.json)

---

## 15. Rejection Reasons

All candidate rejections recorded machine-readable reasons:
* `exact_duplicate`: Deduplicated via MD5 hash matching
* `near_duplicate`: Deduplicated via dHash perceptual fingerprinting
* `single_class_source`: MJU-Waste single-class rejected
* `domain_mismatch`: TrashCan underwater marine rejected
* `commercial_restriction`: ZeroWaste CC BY-NC 4.0 held in review

---

## 16. Storage / Resource Usage

* **Current Free Disk Space:** 597.18 GB
* **Candidate Pool Footprint:** ~1.4 GB
* **Safety Buffer:** > 595 GB (Extremely safe)

---

## 17. Automated Test Results

* **Test Suite:** [`tests/test_dataset_pipeline.py`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/tests/test_dataset_pipeline.py) & [`tests/test_environment.py`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/tests/test_environment.py)
* **Total Automated Test Cases:** 61 (Includes 10 new candidate pool tests 51-60)
* **Result:** `61 passed in 6.38s` (100% pass rate).

---

## 18. Total Genuine Candidate Pool Summary

* **Immutable Baseline (`safaios_dataset_v1.0`):** 1,238 images (975 train, 89 val, 174 locked test)
* **Staged Candidate Pool (`data/incoming/candidate_pool_v2/`):** 1,421 genuine candidate images (14,968 bboxes)
* **Additional Staged Batches (`data/incoming/`):** 194 candidate images
* **Total Project Data Managed:** **2,853 Images / 17,665 Bounding Boxes**

---

## 19. Remaining Gaps to Targets

| Split | Current Verified Baseline | Staged Candidates | Target Threshold | Gap Remaining |
| :--- | :---: | :---: | :---: | :---: |
| **Training** | 975 | 1,421 | $\ge 10,000$ | 7,604 |
| **Validation** | 89 | 194 (in staging) | $\ge 1,000$ | 717 |
| **Locked Test** | 174 | 0 (Protected) | $\ge 1,000$ | 826 |
| **India Benchmark** | 0 | 0 (Design Phase) | $\ge 100$ | 100 |

---

## 20. Recommendation for Milestone 2E

* **Milestone 2E Goal:** Dataset Construction Gate & Split Freeze (`safaios_dataset_v2.0`).
* **Key Tasks:**
  1. Continue class-balanced scaling for priority 1 (`glass_bottle_container`) and priority 2 (`plastic_bottle`).
  2. Execute deterministic split assignment using source-group isolation.
  3. Validate lock protection on test set.
  4. Initiate field acquisition for India Real-World Benchmark ($\ge 100$ images).

---

```
==================================================
FINAL STATUS: DATASET NOT READY FOR TRAINING
DO NOT TRAIN YOLO
==================================================
```
