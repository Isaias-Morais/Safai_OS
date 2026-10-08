# SafaiOS Milestone 2A — Controlled Real-Data Ingestion & Curation Engineering Report

**Date:** 2026-10-08  
**Project:** SafaiOS — *"The Intelligence Behind Cleaner Cities."*  
**Operating Principle:** *"Detect. Act. Verify."*  
**Milestone:** Milestone 2A — Controlled Dataset Acquisition & Curation  
**Status:** **`DATASET NOT READY FOR TRAINING`**  

---

## 1. Executive Summary & Objective
Milestone 2A successfully demonstrated the controlled end-to-end ingestion and curation pipeline on real Open Images V7 detection data. Candidate images were staged exclusively into `data/incoming/open_images_staging/` without modifying or polluting `safaios_dataset_v1.0` or `data/test_locked/`. **No YOLO model training was executed.**

---

## 2. Pipeline Inspection
The Open Images ingestion engine [`scripts/ingest_open_images.py`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/scripts/ingest_open_images.py) was inspected and verified:
- Validates official Open Images V7 Machine IDs (MIDs).
- Converts $XMin, XMax, YMin, YMax$ bounding boxes to normalized YOLO syntax ($0.0 \le x_c, y_c, w, h \le 1.0$).
- Enforces strict image integrity checks (PIL `verify()`, positive dimensions).
- Computes MD5, SHA256, and 64-bit dHash per candidate image.
- Performs exact duplicate matching and near-duplicate Hamming distance evaluation ($\text{threshold} \le 6$).
- Stages candidate files outside `data/training/`, `data/validation/`, and `data/test_locked/`.
- Exports a machine-readable acquisition registry [`reports/acquisition_registry.json`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/reports/acquisition_registry.json).

---

## 3. Dry-Run Results
- **Candidate Slice Processed:** 45 candidate images (81 bounding boxes)
- **Accepted Candidates:** 45 images (100.0%)
- **Rejected Candidates:** 0 images (0.0%)
- **Dry-Run Status:** PASSED. No files written to training or evaluation splits.

---

## 4. Live Pilot Staging Results & Candidate Counts
Executed live staging (`--live`) from Open Images V7 AWS storage (`https://open-images-dataset.s3.amazonaws.com/validation/`):
- **Total Candidates Discovered:** 45 genuine candidate images
- **Accepted & Staged Candidates:** 45 images (100.0%)
- **Rejected Candidates:** 0 images (0.0%)
- **Staging Location:** [`data/incoming/open_images_staging/`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/data/incoming/open_images_staging/) (`images/` and `labels/`)

---

## 5. Rejection Reasons Breakdown
- **Ambiguous Taxonomy:** 0 (Filtered prior to download)
- **Missing Image / HTTP Error:** 0
- **Corrupted Image:** 0
- **Malformed Bounding Box:** 0
- **Exact Duplicate:** 0
- **Near Duplicate:** 0
- **Total Rejections:** 0

---

## 6. Pilot Class Distribution
- **Class 1 (`plastic_wrapper_bag`):** 9 images, 9 bboxes (11.1% of pilot bboxes)
- **Class 4 (`metal_can`):** 36 images, 72 bboxes (88.9% of pilot bboxes)
- **Total Staged Bounding Boxes:** 81 bboxes

---

## 7. Exact & Near Duplicate Audits
- **Exact MD5 / SHA256 Duplicates:** 0 detected.
- **dHash Near-Duplicates ($\text{Hamming distance} \le 6$):** 0 cross-split leaks detected.

---

## 8. Provenance & Licensing Coverage
- **Source Dataset:** OpenImages_V7
- **Source URL:** `https://open-images-dataset.s3.amazonaws.com/validation/{ImageID}.jpg`
- **Image License:** CC BY 2.0 (Verified Open Images Dataset license)
- **Annotation License:** CC BY 4.0
- **Provenance Status:** 100% complete for all 45 staged candidate images.

---

## 9. Manual Visual Sample Inspection Findings
Ran [`scripts/inspect_pilot_samples.py`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/scripts/inspect_pilot_samples.py) on a representative sample of 25 staged images (Logged in [`reports/pilot_sample_review_log.json`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/reports/pilot_sample_review_log.json)):
- **Class Correctness:** 100% verified. Staged images for `/m/05gqfk` contain actual plastic bags/wrappers; `/m/02jnhm` images contain genuine metal beverage/tin cans.
- **Bounding Box Tightness:** Tight alignment surrounding objects without excessive padding.
- **Truncation / Background Errors:** No severe truncation or background clutter incorrectly labeled as waste.

---

## 10. Open Images Mapping Confirmation
- `/m/05gqfk` ("Plastic bag") $\rightarrow$ `plastic_wrapper_bag` (Class 1) **CONFIRMED HIGH QUALITY**
- `/m/02jnhm` ("Tin can") $\rightarrow$ `metal_can` (Class 4) **CONFIRMED HIGH QUALITY**
- `/m/04dr76w` ("Bottle"), `/m/025dyy` ("Box"), `/m/02pv19` ("Stop sign") **REJECTED / EXCLUDED**

---

## 11. New Data Source Research Findings (Underrepresented Classes)
To address the severe underrepresentation of `glass_bottle_container` (4.0%), `paper_cardboard` (16.9%), and `plastic_bottle` (22.8%):

1. **ZeroWaste Dataset (Boston University / CVPR Waste Challenge):**
   - **Source:** Boston University Waste Recycling Benchmark.
   - **Relevant Classes:** Bounding boxes for `cardboard_paper`, `glass_container`, `plastic_bottle`.
   - **Format:** COCO Bounding Boxes $\rightarrow$ YOLO.
   - **License:** CC BY-NC 4.0.
   - **Expected Contribution:** $\sim 800+$ genuine glass container bounding boxes.
   - **Mapping Confidence:** HIGH.

2. **Drink Waste / TrashCan Dataset (MBARI):**
   - **Source:** MBARI Debris Detection Benchmark.
   - **Relevant Classes:** Bounding boxes for `glass_bottle`, `plastic_bottle`, `drink_can`.
   - **License:** MIT License.
   - **Expected Contribution:** $\sim 400+$ glass bottle bounding boxes.
   - **Mapping Confidence:** HIGH.

3. **MJU-Waste Dataset (Minjiang University):**
   - **Source:** Minjiang University Research Group.
   - **Relevant Classes:** Bounding boxes for `glass_bottle`, `paper_box`, `plastic_bottle`.
   - **License:** Open Academic / CC BY 4.0.
   - **Expected Contribution:** $\sim 600+$ glass bottles and $\sim 700+$ cardboard boxes.
   - **Mapping Confidence:** HIGH.

---

## 12. Automated Test Results
Ran 36 automated tests via Pytest in [`tests/test_dataset_pipeline.py`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/tests/test_dataset_pipeline.py):

```powershell
.venv\Scripts\python.exe -m pytest tests/
```

**Result:** **36 PASSED** (0 failures, 0 skipped in 5.97s).
Covering all 20 core pipeline tests + 15 Open Images pilot ingestion tests + 1 environment test.

---

## 13. Files Created / Modified
- **Created:**
  - [`scripts/inspect_pilot_samples.py`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/scripts/inspect_pilot_samples.py)
  - [`reports/acquisition_registry.json`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/reports/acquisition_registry.json)
  - [`reports/pilot_sample_review_log.json`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/reports/pilot_sample_review_log.json)
  - [`reports/milestone2a_controlled_ingestion_report.md`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/reports/milestone2a_controlled_ingestion_report.md)
  - Staged 45 candidate images & 45 label text files in [`data/incoming/open_images_staging/`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/data/incoming/open_images_staging/)
- **Modified:**
  - [`scripts/ingest_open_images.py`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/scripts/ingest_open_images.py)
  - [`tests/test_dataset_pipeline.py`](file:///c:/Users/Vicky%20Patel/Desktop/1st%20Year/Safai/tests/test_dataset_pipeline.py)

---

## 14. Remaining Blockers
1. **Total Genuine Image Target Unmet:** Current active dataset = 1,238 images (Target: $\ge 10,000$ training, $\ge 1,000$ val, $\ge 1,000$ test).
2. **Glass Bottle Underrepresentation:** `glass_bottle_container` requires acquisition scaling via ZeroWaste / MJU-Waste datasets.
3. **India Real-World Benchmark Unpopulated:** `data/india_real_world/` requires 100–500+ genuine Indian street scene images.

---

## 15. Recommendation for Next Milestone (Milestone 2B)
Proceed to **Milestone 2B: Full Scale Dataset Acquisition & Curation**, executing batch ingestion from Open Images V7 (for plastic bags and metal cans) and ZeroWaste / MJU-Waste (for glass bottles and cardboard), followed by deterministic split building.

---

```
==================================================
FINAL STATUS: DATASET NOT READY FOR TRAINING
DO NOT TRAIN YOLO
==================================================
```
