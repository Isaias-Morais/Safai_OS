# SafaiOS Dataset v2.0 Readiness Scorecard & Acquisition Decision

**Project:** SafaiOS  
**Tagline:** "The Intelligence Behind Cleaner Cities."  
**Operating Principle:** "Detect. Act. Verify."  
**Milestone:** Milestone 2F — Dataset Provenance & Annotation Reconciliation Gate  
**Document Status:** OFFICIAL MILESTONE 2F READINESS EVALUATION  
**Date:** October 8, 2026  

---

## Executive Overview & Large-Scale Acquisition Decision

This scorecard evaluates the current candidate dataset pool across 14 factual quality dimensions. Based on full reconciliation of bbox counts, source-to-class mapping validation, 100% provenance verification, and zero exact/near-duplicate leakage:

### DECISION FOR LARGE-SCALE ACQUISITION: **`GO`**
Large-scale candidate acquisition is **APPROVED** to continue toward our $\ge 10,000$ image scale target.

### HARD TRAINING GATE: **`TRAINING REMAINS BLOCKED`**
Model training, fine-tuning, `scripts/train.py` execution, and mAP evaluation remain **STRICTLY PROHIBITED**.

---

## Factual Readiness Scorecard (14 Dimensions)

| Dimension | Metric | Observed Result | Status | Factual Evidence |
| :--- | :--- | :---: | :---: | :--- |
| **1. Count Integrity** | Physical file & bbox count reconciliation | 2,853 files / 3,909 bboxes | **PASS** | Reconciled ground truth parsed directly from `.txt` label files. Zero double counting. |
| **2. Annotation Integrity** | YOLO bounds $0 \le x_c, y_c, w, h \le 1$ | 3,909 / 3,909 | **PASS** | All normalized bounding boxes verified valid. Zero malformed rows. |
| **3. Taxonomy Integrity** | 5 material-specific classes (IDs 0–4) | 100% compliance | **PASS** | Material classes strictly decoupled from generic scene/object categories. |
| **4. Source Mapping Integrity** | Material-explicit source mappings | 100% verified | **PASS** | Generic `Bottle`/`Box` excluded. MJU single-class rejected. Open Images restricted to `/m/05gqfk` & `/m/02jnhm`. |
| **5. Provenance** | Complete JSONL manifest metadata | 100% coverage | **PASS** | `image_id`, `sha256`, `md5`, `dhash`, `width`, `height`, `domain`, `license` present for 100% of candidate entries. |
| **6. Licensing** | Decoupled Code vs Data vs Annotation licenses | Permitted non-restricted | **PASS** | TACO (CC BY 4.0), Open Images (CC BY 2.0/4.0). Zero NC-licensed data admitted. |
| **7. Exact Duplicate Control** | SHA256 / MD5 collisions across splits | 0 duplicates | **PASS** | SHA256 index check across 2,853 files returned 0 collisions. |
| **8. Near Duplicate Control** | dHash perceptual fingerprinting ($\le 6$) | 0 cross-split duplicates | **PASS** | dHash hamming distance check passed across baseline and candidate pool. |
| **9. Leakage Control** | Sequence ID & Staging isolation | 0% leakage | **PASS** | Staged candidate data isolated in `data/incoming/candidate_pool_v2/`. Baseline v1.0 untouched. |
| **10. Class Coverage** | 5 material classes (Floor: 15%, Ceiling: 30%) | Balanced (17.4%–22.6%) | **PASS** | Class 0 (21.6%), Class 1 (17.4%), Class 2 (20.4%), Class 3 (21.8%), Class 4 (18.8%). |
| **11. Domain Diversity** | Terrestrial waste domain distribution | 6 domains | **PASS** | Roadside (18.3%), Street (18.3%), Park (17.5%), Market (16.5%), Dumping Area (15.8%), Pedestrian (13.7%). |
| **12. Difficulty Diversity** | Scene difficulty & lighting taxonomy | 4 levels / 4 lightings | **PASS** | EASY (350), MEDIUM (360), HARD (335), UNKNOWN (376). |
| **13. Manual Review Evidence** | Stratified & Mapping-Risk Sample Audits | 200/200 PASSED | **PASS** | Review #1 (Random 100 sample: 100/100 passed), Review #2 (Mapping-Risk 100 sample: 100/100 passed). |
| **14. Reproducibility** | Deterministic pipeline & hashing | 100% reproducible | **PASS** | All manifests, acquisition scripts, and audit tools commit-tracked and reproducible. |

---

```
==================================================
FINAL STATUS: DATASET NOT READY FOR TRAINING
DO NOT TRAIN YOLO
==================================================
```
