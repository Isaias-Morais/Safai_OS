# SafaiOS Dataset v2 Readiness Scorecard — Milestone 2I

**Project:** SafaiOS  
**Tagline:** "The Intelligence Behind Cleaner Cities."  
**Operating Principle:** "Detect. Act. Verify."  
**Milestone:** Milestone 2I — Dataset Inventory, Source Provenance & Candidate Pool Freeze Gate  
**Date:** October 9, 2026  
**Authoritative Readiness Status:** `DATASET NOT READY FOR TRAINING`  
**Candidate Pool Acquisition Gate:** `GO (CANDIDATE POOL FROZEN & VERIFIED)`  

---

## 1. 15-Dimension Evidence-Based Quality Evaluation

| # | Dimension | Measurement | Result | Status | Empirical Evidence |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **1** | **Inventory Integrity** | Physical file vs SHA256 hash match | 7,453 / 7,453 | `VERIFIED` | 100% match recorded in `reports/complete_dataset_inventory.json` |
| **2** | **Annotation Integrity** | Multi-class JSONL format (`annotations[]`) | 4,600 / 4,600 | `VERIFIED` | Formatted in `reports/candidate_dataset_truth_table.jsonl` |
| **3** | **Source Identity** | Canonical origin vs alias mapping | 4 / 4 Sources | `VERIFIED` | Documented in `reports/source_inventory_truth.json` |
| **4** | **Taxonomy Integrity** | SafaiOS 5-class material alignment | 5 / 5 Classes | `VERIFIED` | Material-explicit mappings; 0 generic class leakage |
| **5** | **Provenance Completeness** | Hash, license, source_url, source_class | 100.0% | `VERIFIED` | Recorded in `reports/provenance_integrity_report.json` |
| **6** | **Licensing Compliance** | Commercial use & redistribution status | 100.0% | `VERIFIED` | CC BY 4.0, CC BY-SA 4.0, and MIT licenses verified |
| **7** | **Exact Duplicate Control** | SHA256 & MD5 collision count | 0 Duplicates | `VERIFIED` | 0 exact duplicates across 7,453 physical files |
| **8** | **Near Duplicate Control** | Perceptual dHash distance <= 4 | 0 Collisions | `VERIFIED` | 0 cross-pool perceptual collisions |
| **9** | **Cross-Role Leakage** | Staging candidate vs Locked Test/India RW | 0 Collisions | `VERIFIED` | Locked test (174) & India RW (100) strictly isolated |
| **10** | **Source Diversity** | Max single-source dataset contribution | 35.8% | `VERIFIED` | No source exceeds 40% threshold |
| **11** | **Domain Diversity** | Terrestrial domain coverage | 10 Domains | `VERIFIED` | Roadside, market, street, public area, landfill, etc. |
| **12** | **Class Diversity** | Box count balance across 5 classes | ~2,900 / class | `VERIFIED` | Balanced material representation |
| **13** | **India Benchmark Isolation**| Independent real-world dataset pool | 100 Images | `VERIFIED` | `data/india_real_world/` held isolated |
| **14** | **Manual Review Evidence** | 250-sample stratified audit result | 250 / 250 | `VERIFIED` | 0.0% error rate in `reports/large_scale_acquisition_manual_review_log.json` |
| **15** | **Reproducibility** | Automated pytest validation suite | 101 / 101 | `VERIFIED` | 100% pass rate in `tests/test_dataset_pipeline.py` |

---

## 2. Hard Training Gate Decision

```
==================================================
LARGE-SCALE ACQUISITION DECISION: GO
CANDIDATE POOL FROZEN: YES (safaios_candidate_pool_2H)

DATASET NOT READY FOR TRAINING
DO NOT TRAIN YOLO
==================================================
```
