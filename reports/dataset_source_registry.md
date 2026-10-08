# SafaiOS Dataset Source Registry — Milestone 2C Update

**Date:** October 8, 2026  
**Project:** SafaiOS — *"The Intelligence Behind Cleaner Cities."*  
**Operating Principle:** *"Detect. Act. Verify."*  

---

## Source Verification & Approval Matrix

| Source Name | Canonical URL | Image Count | Image License | Annotation License | Commercial Use | Domain | Approval Status | Key Notes |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- | :---: | :--- |
| **TACO** | `https://github.com/pedropro/TACO` | 1,500 | CC BY 4.0 | CC BY 4.0 | Permitted | Street, Park, Public Area | **`VERIFIED_APPROVED`** | Baseline dataset (`safaios_dataset_v1.0`). |
| **Open Images V7** | `https://storage.googleapis.com/openimages` | 1,900,000+ | CC BY 2.0 | CC BY 4.0 | Permitted | Real-World Web, Outdoor | **`VERIFIED_APPROVED`** | Approved ONLY for `/m/05gqfk` (Plastic bag) & `/m/02jnhm` (Tin can). |
| **ZeroWaste** | `http://ai.bu.edu/zerowaste/` | 4,500 | CC BY-NC 4.0 | CC BY-NC 4.0 | Restricted | Industrial Conveyor Belt | **`REQUIRES_REVIEW`** | CC BY-NC 4.0 Non-Commercial release. Restricted from production commercial ingestion. |
| **MJU-Waste** | `https://github.com/mju-waste/mju-waste` | 2,475 | CC BY 4.0 Academic | CC BY 4.0 Academic | Permitted Academic | Tabletop, Indoor | **`VERIFIED_REJECTED`** | Forensically verified in Milestone 2C to be single-class (`waste` only). Claims of material sub-classes (`glass_bottle`, `paper_box`, `plastic_bottle`) were **INVALID SOURCE CLAIMS**. Rejected for 5-class training. |
| **TrashCan** | `https://irvlab.cs.umn.edu/resources/trashcan-dataset` | 7,212 | CC BY 4.0 | CC BY 4.0 | Permitted | Underwater Marine | **`VERIFIED_REJECTED`** | Rejected due to subsea marine domain mismatch for urban waste detection. |

---

## Approved & Rejected Class Mappings

### Approved High-Confidence Mappings:
1. **Open Images `/m/05gqfk` ("Plastic bag") $\rightarrow$ `plastic_wrapper_bag` (Class 1)** [Confidence: HIGH]
2. **Open Images `/m/02jnhm` ("Tin can") $\rightarrow$ `metal_can` (Class 4)** [Confidence: HIGH]
3. **TACO 60-Category Sub-classes $\rightarrow$ 5 SafaiOS Material Classes (Classes 0-4)** [Confidence: HIGH]

### Rejected / Invalid Mappings:
1. **MJU-Waste `waste` $\rightarrow$ `glass_bottle_container` / `paper_cardboard` / `plastic_bottle`** [INVALID SOURCE CLAIM — Single class `waste` only]
2. **Open Images `/m/04dr76w` ("Bottle") $\rightarrow$ `plastic_bottle` / `glass_bottle_container`** [REJECTED — Material ambiguous]
3. **Open Images `/m/025dyy` ("Box") $\rightarrow$ `paper_cardboard`** [REJECTED — Material ambiguous]
4. **Open Images `/m/02pv19` ("Stop sign") $\rightarrow$ `paper_cardboard`** [REJECTED — Semantic error]
5. **TrashCan Subsea Debris $\rightarrow$ SafaiOS Urban Benchmark** [REJECTED — Domain mismatch]
