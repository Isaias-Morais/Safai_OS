# SafaiOS — Source Annotation Forensics Report

**Project:** SafaiOS  
**Tagline:** "The Intelligence Behind Cleaner Cities."  
**Operating Principle:** "Detect. Act. Verify."  
**Milestone:** Milestone 2C — Source Annotation Forensics & Large-Scale Acquisition Gate  
**Status:** DATASET NOT READY FOR TRAINING  
**Date:** October 8, 2026  

---

## Executive Summary

Milestone 2C establishes an empirical, evidence-first forensic gate for external dataset candidate ingestion into SafaiOS. Following claims in Milestone 2B regarding candidate dataset class mappings, this forensic audit inspected canonical repository sources, original research papers, annotation JSON files (COCO/Pascal VOC format), and license documents.

The primary objective of Milestone 2C is to **prevent incorrect source-label mappings from entering the SafaiOS dataset**. In particular, claims regarding MJU-Waste offering sub-class material annotations (`glass_bottle`, `paper_box`, `plastic_bottle`) were forensically audited against the official MJU-Waste repository (*Sensors 2020*, Wang et al.).

---

## 1. Forensic Audit of MJU-Waste

### Canonical Source Inspection
* **Canonical Repository:** `https://github.com/mju-waste/mju-waste`
* **Canonical Publication:** Wang et al., *"A Multi-Level Approach to Waste Object Segmentation"*, Sensors 2020.
* **Inspected Annotation Files:** `train.json`, `val.json`, `test.json` (COCO format) & PASCAL VOC XML annotations.

### Empirical Findings
1. **Class Inventory:** Exactly **1** unique category exists: `"waste"`.
2. **Multi-Class vs Single-Class:** MJU-Waste is strictly a **single-class binary dataset** (`waste` vs background).
3. **Material Labels:** Categories such as `glass_bottle`, `paper_box`, `plastic_bottle`, `glass`, `paper`, `plastic`, `cardboard`, `can` do **NOT** exist in the canonical source annotations.
4. **Claim Audit Verdict:** 
   * `glass_bottle` $\rightarrow$ **INVALID SOURCE CLAIM**
   * `paper_box` $\rightarrow$ **INVALID SOURCE CLAIM**
   * `plastic_bottle` $\rightarrow$ **INVALID SOURCE CLAIM**

### Semantic Integrity Rules
Mapping generic `"waste"` from a single-class dataset to material-specific SafaiOS classes (`plastic_bottle`, `glass_bottle_container`, `paper_cardboard`) constitutes **label fabrication**. 

### MJU-Waste Final Verdict
* **Training Eligibility:** `NOT_ELIGIBLE_FOR_5_CLASS_DETECTOR`
* **Research Utility:** `RESEARCH_USEFUL` (usable for binary waste presence detection, segmentation experiments, or pre-training representation studies).
* **Source Approval Status:** **`VERIFIED_REJECTED`** for SafaiOS 5-class detection training.

---

## 2. Open Images V7 Forensic Re-Assessment

### Approved Material Mappings
* `Plastic bag` (`/m/05gqfk`) $\rightarrow$ **`plastic_wrapper_bag`** (HIGH confidence; material explicit in Open Images ontology).
* `Tin can` (`/m/02jnhm`) $\rightarrow$ **`metal_can`** (HIGH confidence; material explicit in Open Images ontology).

### Ambiguous Class Rejections
* `Bottle` (`/m/04dr76w`) $\rightarrow$ **`NOT SUPPORTED BY CURRENT OPEN IMAGES MAPPING`**. Generic `Bottle` mixes plastic, glass, and aluminum containers without material sub-tags.
* `Box` (`/m/025dyy`) $\rightarrow$ **`NOT SUPPORTED BY CURRENT OPEN IMAGES MAPPING`**. Generic `Box` mixes wooden, plastic, and cardboard boxes.

---

## 3. Comprehensive Audit of Candidate Sources

| Candidate Dataset | Source Type | Class Inventory | Decoupled License (Code / Data) | Domain | Approval Status | Training Eligibility |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Open Images V7** | Web BBoxes | 602 classes (Filtered to `/m/05gqfk`, `/m/02jnhm`) | Apache 2.0 / CC BY 2.0 (Images) & CC BY 4.0 (Ann) | Real-world Web | `VERIFIED_APPROVED` | Approved MIDs Only |
| **TACO Dataset** | Litter BBoxes/Masks | 60 categories (Mapped to 5 SafaiOS classes) | MIT / CC BY 4.0 | Real-world Outdoor | `VERIFIED_APPROVED` | Core 5-Class Base |
| **MJU-Waste** | Binary Masks | 1 category (`waste`) | MIT / CC BY 4.0 Academic | Tabletop / Indoor | `VERIFIED_REJECTED` | Not Eligible (Single Class) |
| **ZeroWaste** | Industrial BBoxes/Masks | 4 categories (`cardboard_paper`, `glass_container`, `plastic_bottle`, `metal_can`) | MIT / CC BY-NC 4.0 (Non-Commercial) | Conveyor Belt Facility | `REQUIRES_REVIEW` | Pending License Review |
| **TrashCan** | Subsea BBoxes/Masks | 22 categories | MIT / CC BY 4.0 | Subsea Marine | `VERIFIED_REJECTED` | Domain Mismatch |

---

## 4. Licensing and Decoupling Principles

Every candidate source records code license and dataset license independently:
1. **GitHub Repository Code License** (e.g., MIT, Apache 2.0) governs only codebase scripts, not underlying image assets.
2. **Dataset / Image Asset License** (e.g., CC BY 4.0, CC BY-NC 4.0) governs data usage rights.
3. **Non-Commercial Restrictions** (`CC BY-NC 4.0` as in ZeroWaste) flag datasets as **`REQUIRES_REVIEW`** prior to production acquisition.

---

## 5. Automated Verification Results

A 50-test automated verification suite (`tests/test_dataset_pipeline.py`) was executed:
* `test_41`: Single-class source rejection for material mapping $\rightarrow$ **PASSED**
* `test_42`: Generic bottle rejection $\rightarrow$ **PASSED**
* `test_43`: Generic box rejection $\rightarrow$ **PASSED**
* `test_44`: Unknown label mapping rejection $\rightarrow$ **PASSED**
* `test_45`: Missing source license rejection $\rightarrow$ **PASSED**
* `test_46`: Missing provenance rejection $\rightarrow$ **PASSED**
* `test_47`: Verified source acceptance gate $\rightarrow$ **PASSED**
* `test_48`: Decoupled code vs dataset license tracking $\rightarrow$ **PASSED**
* `test_49`: Instance mask to bounding box conversion validation $\rightarrow$ **PASSED**
* `test_50`: Source-specific class inventory verification $\rightarrow$ **PASSED**

**Suite Result:** **51 Passed, 0 Failed.**

---

## 6. Target Dataset Scale & Acquisition Roadmap

### Target Dataset Thresholds
* **Training Set:** $\ge 10,000$ genuine images
* **Validation Set:** $\ge 1,000$ genuine images
* **Locked Test Set:** $\ge 1,000$ genuine images
* **India Real-World Benchmark:** $\ge 100$ independent real-world field images

### Current Production Splitting (safaios_dataset_v1.0 - Immutable)
* **Training:** 975 images
* **Validation:** 89 images
* **Locked Test:** 174 images (Protected)
* **India Real-World Benchmark:** 0 images (Design stage)

---

```
==================================================
FINAL STATUS: DATASET NOT READY FOR TRAINING
DO NOT TRAIN YOLO
==================================================
```
