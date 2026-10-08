# SafaiOS — Milestone 2C Source Annotation Forensics Report

**Project:** SafaiOS  
**Tagline:** "The Intelligence Behind Cleaner Cities."  
**Operating Principle:** "Detect. Act. Verify."  
**Milestone:** Milestone 2C — Source Annotation Forensics & Large-Scale Acquisition Gate  
**Status:** DATASET NOT READY FOR TRAINING  
**Date:** October 8, 2026  

---

## 1. Current Repository State

* **Git Commit Hash:** Current `main` branch state verified.
* **Repository Working Tree:** Clean, no uncommitted temporary artifacts.
* **Current Production Dataset (`safaios_dataset_v1.0`):** Immutable.
  * **Training Set:** 975 images, 2,130 bboxes
  * **Validation Set:** 89 images, 187 bboxes
  * **Locked Test Set:** 174 images, 380 bboxes (Protected, zero modifications)
  * **India Benchmark Set:** 0 images (Design Phase)
* **Staged Candidate Pipeline (`data/incoming/`):**
  * `open_images_staging/`: 45 images staged (Pilot)
  * `large_batch_staging/`: 149 images staged
  * Total Staged Candidates: 194 candidate image/label pairs isolated from production splits.

---

## 2. MJU-Waste Forensic Analysis

In Milestone 2B, previous assumptions claimed that MJU-Waste provided three material categories: `glass_bottle`, `paper_box`, and `plastic_bottle`.

Under Milestone 2C, we conducted a primary forensic audit directly against official MJU-Waste canonical evidence:
* **Canonical Repository:** `https://github.com/mju-waste/mju-waste`
* **Canonical Paper:** Wang et al., *"A Multi-Level Approach to Waste Object Segmentation"*, Sensors 2020.
* **Annotation Files Inspected:** `train.json`, `val.json`, `test.json` (COCO JSON format) and Pascal VOC XML files.

---

## 3. Actual MJU Class Inventory

Forensic examination revealed:
* **Unique Categories:** Exactly **1** category (`"waste"`).
* **Class Names:** `"waste"` (ID 1).
* **Material Sub-categories:** None. Categories such as `glass_bottle`, `paper_box`, `plastic_bottle`, `glass`, `plastic`, `paper`, `cardboard`, `can` do **NOT** exist in the canonical MJU-Waste annotations.
* **Claim Audit:**
  * `glass_bottle` $\rightarrow$ **INVALID SOURCE CLAIM**
  * `paper_box` $\rightarrow$ **INVALID SOURCE CLAIM**
  * `plastic_bottle` $\rightarrow$ **INVALID SOURCE CLAIM**

---

## 4. Actual Annotation Structure

* **Format:** COCO JSON segmentation polygons (`segmentation`) & Pascal VOC binary masks.
* **Bounding Box Derivation:** Bounding boxes can be extracted deterministically from segmentation polygon vertices $[x_{\min}, y_{\min}, x_{\max}, y_{\max}]$.
* **Category Semantics:** Single-class binary mask (`waste` vs background).

---

## 5. MJU Mapping Decision

**Can MJU-Waste contribute directly to the current SafaiOS 5-class detector?**  
**NO.**

### Explanation
Mapping generic `"waste"` to material-specific SafaiOS classes (`plastic_bottle`, `glass_bottle_container`, `paper_cardboard`) constitutes **label fabrication**. Since MJU-Waste provides no material-specific semantic labels, automatic supervision for our 5-class taxonomy is impossible without unverified manual re-annotation.

### Distinction
* **RESEARCH-USEFUL:** Yes (usable for binary waste presence, segmentation benchmark experiments, pre-training representation studies).
* **TRAINING-ELIGIBLE:** No (rejected for 5-class SafaiOS detection detector).
* **Approval Status:** **`VERIFIED_REJECTED`** for production training pipeline.

---

## 6. Open Images Mapping Audit

### Approved Mappings
* `/m/05gqfk` (`Plastic bag`) $\rightarrow$ **`plastic_wrapper_bag`** (Class ID 1) — **VERIFIED_APPROVED**
* `/m/02jnhm` (`Tin can`) $\rightarrow$ **`metal_can`** (Class ID 4) — **VERIFIED_APPROVED**

### Ambiguous Class Rejections
* `/m/04dr76w` (`Bottle`) $\rightarrow$ **`NOT SUPPORTED BY CURRENT OPEN IMAGES MAPPING`** (Mixes plastic, glass, aluminum without material attributes).
* `/m/025dyy` (`Box`) $\rightarrow$ **`NOT SUPPORTED BY CURRENT OPEN IMAGES MAPPING`** (Mixes cardboard, plastic, wood without material attributes).

---

## 7. Other Candidate Source Audits

* **TACO Dataset:** Multi-class litter dataset (60 categories). Mapped to 5 SafaiOS material classes with high confidence. License: CC BY 4.0. Status: **`VERIFIED_APPROVED`**.
* **ZeroWaste Dataset:** 4 categories (`cardboard_paper`, `glass_container`, `plastic_bottle`, `metal_can`). Conveyor belt industrial environment. License: CC BY-NC 4.0 (Non-Commercial). Status: **`REQUIRES_REVIEW`**.
* **TrashCan Dataset:** 22 subsea marine debris categories. Underwater domain mismatch. Status: **`VERIFIED_REJECTED`**.

---

## 8. Licensing Findings

License decoupling is strictly enforced:
* **Code License $\neq$ Data License:** GitHub repository MIT/Apache licenses cover code scripts only. Image asset licenses must be verified independently.
* **Non-Commercial Exclusion:** Datasets licensed under `CC BY-NC` (e.g. ZeroWaste) are flagged as `REQUIRES_REVIEW` and excluded from commercial production pipeline ingestion.

---

## 9. Provenance Findings

Every acquired image must contain a complete provenance record:
* Canonical repository URL
* Dataset version
* Original image ID & license URL
* Deterministic hashing (MD5 & dHash)

Images lacking provenance or license metadata are rejected at the acquisition gate.

---

## 10. Source Approval States

| Source Dataset | Approval State | Training Eligibility | Primary Reason |
| :--- | :--- | :--- | :--- |
| **TACO Dataset** | `VERIFIED_APPROVED` | Core 5-Class Base | Explicit material annotations, CC BY 4.0 |
| **Open Images V7 (Filter)** | `VERIFIED_APPROVED` | Approved MIDs Only | Explicit material classes (`Plastic bag`, `Tin can`), CC BY 2.0/4.0 |
| **MJU-Waste** | `VERIFIED_REJECTED` | Not Eligible | Single-class `waste` only; claims of material sub-classes were invalid |
| **ZeroWaste** | `REQUIRES_REVIEW` | Pending Review | CC BY-NC 4.0 non-commercial license restriction |
| **TrashCan** | `VERIFIED_REJECTED` | Not Eligible | Subsea marine domain mismatch |

---

## 11. Acquisition Roadmap

To achieve scale targets ($\ge 10,000$ training images):

1. **Source 1: Open Images V7 (Targeted Download)**
   * Classes: `plastic_wrapper_bag` (`/m/05gqfk`), `metal_can` (`/m/02jnhm`)
   * Estimated Yield: ~4,500 images
2. **Source 2: Extended TACO Annotations**
   * Classes: `plastic_bottle`, `glass_bottle_container`, `paper_cardboard`, `plastic_wrapper_bag`, `metal_can`
   * Estimated Yield: ~1,500 images
3. **Source 3: Targeted Material Datasets (Roboflow Universe Verified Material Sets)**
   * Classes: Material-explicit `plastic_bottle`, `glass_bottle_container`, `paper_cardboard`
   * Estimated Yield: ~4,000 images
4. **Acquisition Strict Rule:** Deduplication against `safaios_dataset_v1.0` (MD5 exact match and dHash hamming distance $\le 6$).

---

## 12. India Real-World Benchmark Methodology

### Benchmark Requirements
* **Target Size:** $\ge 100$ independent real-world field test images.
* **Domain:** Indian street conditions, roadside dumping, urban markets, drain edges, public transit stops.
* **Environmental Variance:** Direct sunlight, night/low-light, heavy shadow, dust, clutter, high occlusion.
* **Data Privacy & Compliance:** No PII (faces/license plates anonymized or excluded), explicit photographic permission/rights recorded.
* **Split Protection:** Kept strictly outside training, validation, and locked test splits.

---

## 13. Automated Test Results

Executed complete 51-test suite (`tests/test_dataset_pipeline.py` & `tests/test_environment.py`):
* Test Case 41 (Single-class rejection): **PASSED**
* Test Case 42 (Generic bottle rejection): **PASSED**
* Test Case 43 (Generic box rejection): **PASSED**
* Test Case 44 (Unknown label rejection): **PASSED**
* Test Case 45 (Missing license rejection): **PASSED**
* Test Case 46 (Missing provenance rejection): **PASSED**
* Test Case 47 (Verified source gate): **PASSED**
* Test Case 48 (Decoupled license tracking): **PASSED**
* Test Case 49 (Mask to BBox conversion): **PASSED**
* Test Case 50 (Class inventory verification): **PASSED**

**Overall Test Suite Result:** `51 passed in 6.17s` (100% pass rate).

---

## 14. Remaining Blockers

1. **Material-Specific Supervision for `plastic_bottle`, `glass_bottle_container`, and `paper_cardboard`:** Generic Open Images `Bottle` and `Box` cannot be used. Verified material-specific sources must be ingested.
2. **ZeroWaste Licensing Review:** Commercial licensing clearance required for CC BY-NC 4.0 data.
3. **India Benchmark Field Collection:** Field acquisition protocol must be executed before final dataset release.

---

## 15. Recommendation for Next Milestone

* **Next Milestone:** Milestone 2D — Material-Specific Dataset Scaling & India Benchmark Baseline
* **Actions:**
  1. Ingest material-specific candidate images for `plastic_bottle`, `glass_bottle_container`, and `paper_cardboard`.
  2. Maintain strict isolation of candidate data in `data/incoming/`.
  3. Execute exact & near-duplicate filtering across all candidates.
  4. Begin India real-world benchmark collection protocol.

---

```
==================================================
FINAL STATUS: DATASET NOT READY FOR TRAINING
DO NOT TRAIN YOLO
==================================================
```
