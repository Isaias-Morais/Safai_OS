# SafaiOS — Architecture & Engineering Specification

**Tagline:** The Intelligence Behind Cleaner Cities.  
**Operating Principle:** Detect. Act. Verify.

## 1. System Overview

SafaiOS is a high-throughput, edge-capable computer vision system purpose-built for real-time municipal and street waste detection, classification, and density monitoring.

```
+-----------------------------------------------------------+
|                     SafaiOS Pipeline                      |
+-----------------------------------------------------------+
|                                                           |
|  [ Video / Edge Camera ]                                  |
|            |                                              |
|            v                                              |
|  [ Preprocessing & Letterbox Resizing (768px) ]           |
|            |                                              |
|            v                                              |
|  [ YOLO11s Inference Backbone & Detection Head ]          |
|            |                                              |
|            v                                              |
|  [ Postprocessing & Class-Specific NMS (conf=0.25) ]      |
|            |                                              |
|            v                                              |
|  [ Waste Instance Tracking & Density Stratification ]     |
|            |                                              |
|            v                                              |
|  [ Municipal Telemetry & Verification API ]               |
+-----------------------------------------------------------+
```

## 2. Waste Taxonomy

| Class ID | Identifier | Target Real-World Material |
|:---:|---|---|
| 0 | `plastic_bottle` | PET water/beverage bottles, rigid plastic bottles |
| 1 | `plastic_wrapper_bag` | Thin film bags, snack packets, packaging films |
| 2 | `paper_cardboard` | Boxes, newspapers, paper cups, cartons |
| 3 | `glass_bottle_container` | Glass beverage bottles, jars |
| 4 | `metal_can` | Aluminium beverage cans, tin food cans |
