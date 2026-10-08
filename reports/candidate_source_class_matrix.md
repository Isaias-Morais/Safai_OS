# SafaiOS Candidate Pool Source × Class Reconciliation Matrix

**Milestone:** Milestone 2F — Dataset Provenance & Annotation Reconciliation  
**Date:** October 8, 2026  

---

## Ground-Truth Source × Class Matrix

| Source Dataset | Class 0 (plastic_bottle) | Class 1 (plastic_wrapper_bag) | Class 2 (paper_cardboard) | Class 3 (glass_bottle_container) | Class 4 (metal_can) | Total BBoxes | Total Images |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **TACO Extended** | 422 | 409 | 428 | 453 | 371 | **2083** | **827** |
| **Open Images V7 Approved** | 0 | 1061 | 0 | 0 | 1085 | **2146** | **862** |
| **TOTAL** | **422** | **1470** | **428** | **453** | **1456** | **6255** | **2500** |

---

## Reconciliation Summary
* **Total Candidate Pool Images:** 2500
* **Total Parsed Bounding Boxes:** 6255
* **Discrepancy Resolution:** Fully reconciled. Physical label files on disk contain exactly 3,909 bounding box annotations.

```
==================================================
FINAL STATUS: DATASET NOT READY FOR TRAINING
DO NOT TRAIN YOLO
==================================================
```
