# SafaiOS Dataset v2.0 Construction Specification

**Project:** SafaiOS  
**Tagline:** "The Intelligence Behind Cleaner Cities."  
**Operating Principle:** "Detect. Act. Verify."  
**Document Version:** 1.0  
**Status:** DRAFT SPECIFICATION (PRE-CONSTRUCTION GATE)  
**Date:** October 8, 2026  

---

## Executive Overview

This specification establishes the mandatory architectural and quality rules that **MUST** be satisfied before `safaios_dataset_v2.0` can be created, frozen, and approved for training release.

---

## 1. Quantitative Target Thresholds

* **Training Set:** $\ge 10,000$ genuine, unique images
* **Validation Set:** $\ge 1,000$ genuine, unique images
* **Locked Test Set:** $\ge 1,000$ genuine, unique images
* **India Real-World Benchmark:** $\ge 100$ independent field images (target: 100–500+)
* **Total Dataset Scale:** $\ge 12,100$ unique images

---

## 2. Taxonomy & Class Coverage Rules

### Taxonomy Mapping (5 Material Classes)
* `0`: `plastic_bottle`
* `1`: `plastic_wrapper_bag`
* `2`: `paper_cardboard`
* `3`: `glass_bottle_container`
* `4`: `metal_can`

### Distribution Limits
* **Class Floor:** No single material class may represent less than **15%** of total dataset bounding boxes.
* **Class Ceiling:** No single material class may represent more than **30%** of total dataset bounding boxes.

---

## 3. Source & Domain Diversity Rules

* **Source Diversity:** No single external dataset source (e.g., Open Images) may contribute more than **50%** of total training images.
* **Domain Floor:** The dataset must span at least 6 terrestrial waste domains (`street`, `roadside`, `park`, `market`, `dumping_area`, `pedestrian_space`).
* **Domain Ceiling:** No single domain may represent more than **30%** of total dataset images.

---

## 4. Deduplication & Leakage Rules

* **Exact Deduplication:** SHA256 / MD5 hash matching across all splits. Zero exact duplicates allowed.
* **Near Deduplication:** Perceptual dHash fingerprinting. Images with Hamming distance $\le 6$ must be assigned to the same split or rejected.
* **Source-Group / Sequence Isolation:** Images originating from the same sequence, video stream, or capture session MUST remain grouped within the same split (train OR val OR test).

---

## 5. Provenance & Licensing Requirements

* **100% Provenance:** Manifest entries MUST include `image_id`, `sha256`, `md5`, `dhash`, `source_dataset`, `source_url`, `license`, `annotation_license`, `width`, `height`, `class_ids`, `domain`, and `difficulty`.
* **Licensing Clearance:** All ingested images MUST carry explicit non-restricted licenses (e.g., CC BY 4.0, CC BY 2.0, Public Domain). Datasets licensed under `CC BY-NC` (Non-Commercial) are strictly excluded from production commercial splits.

---

## 6. Annotation Integrity Standard

* **Normalized Bounds:** Bounding boxes must satisfy $0.0 \le x_c, y_c, w, h \le 1.0$ and $w \cdot h > 0$.
* **No Label Fabrication:** Single-class or generic class labels (`waste`, `bottle`, `box`) MUST NOT be mapped to material-specific classes without explicit, verifiable material sub-annotations.

---

## 7. Splitting Strategy & Versioning

* **Split Ratio:** 80% Train / 10% Validation / 10% Test.
* **Locked Test Protection:** The current locked test set (`data/test_locked/`) remains immutable and protected.
* **Manifest Freeze:** `safaios_dataset_v2.0` will be published as a frozen JSONL manifest with full hash verification.

---

```
==================================================
FINAL STATUS: DATASET NOT READY FOR TRAINING
DO NOT TRAIN YOLO
==================================================
```
