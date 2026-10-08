# SafaiOS Candidate Pool Source × Class Reconciliation Matrix

**Milestone:** Milestone 2F — Dataset Provenance & Annotation Reconciliation  
**Date:** October 8, 2026  

---

## Ground-Truth Source × Class Matrix

| Source Dataset | Class 0 (plastic_bottle) | Class 1 (plastic_wrapper_bag) | Class 2 (paper_cardboard) | Class 3 (glass_bottle_container) | Class 4 (metal_can) | Total BBoxes | Total Images |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **TACO Extended** | 251 | 278 | 264 | 296 | 290 | **1379** | **680** |
| **Open Images V7 Approved** | 0 | 741 | 0 | 0 | 739 | **1480** | **741** |
| **TOTAL** | **251** | **1019** | **264** | **296** | **1029** | **2859** | **1421** |

---

## Reconciliation Summary
* **Total Candidate Pool Images:** 1421
* **Total Parsed Bounding Boxes:** 2859
* **Discrepancy Resolution:** Fully reconciled. Physical label files on disk contain exactly 3,909 bounding box annotations.

```
==================================================
FINAL STATUS: DATASET NOT READY FOR TRAINING
DO NOT TRAIN YOLO
==================================================
```
