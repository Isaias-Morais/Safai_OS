# SafaiOS Experiment Record: SAFAIOS-E002-YOLO11S-768

**Experiment ID:** `SAFAIOS-E002-YOLO11S-768`  
**Reference Experiment:** `SAFAIOS-E001-YOLO11S-V10K`  
**Experiment Name:** `safaios_yolo11s_v10k_img768`  
**Model Architecture:** YOLO11s (`yolo11s.pt`)  
**Dataset Version:** `safaios_dataset_v10k` (10,000 training images, 1,000 validation images)  
**Execution Status:** **EXPERIMENT 002 COMPLETE**

---

## 1. Execution Summary

- **GPU Device:** NVIDIA GeForce RTX 4060 Laptop GPU (8GB VRAM)
- **PyTorch / Ultralytics:** PyTorch `2.5.1+cu121`, Ultralytics `8.4.174`
- **Completed Epochs:** 100 / 100
- **Best Epoch:** Epoch 87 (Selected by Validation mAP@50-95)
- **Best Checkpoint Path:** `runs/detect/runs/detect/runs/safaios/safaios_yolo11s_v10k_img768/weights/best.pt`
- **Best Checkpoint SHA256:** `8bd30b05a0b4a84d95c5e71f213b967d255144a8fe57791ef110b920fc86d073`
- **Last Checkpoint Path:** `runs/detect/runs/detect/runs/safaios/safaios_yolo11s_v10k_img768/weights/last.pt`
- **Last Checkpoint SHA256:** `38c7e9872d2622adb03a73980b00ca81435c27417eb434e7782091094efe742d`

---

## 2. Controlled Configuration

- **Input Resolution (`imgsz`):** 768 (vs E001: 640)
- **Batch Size:** 16
- **Epochs:** 100
- **Random Seed:** 42
- **Workers:** 4
- **Resolved Optimizer:** `MuSGD(lr=0.01, momentum=0.937)` with parameter groups: 81 weight (decay=0.0), 88 weight (decay=0.0005), 87 bias (decay=0.0)
- **Model Initialization:** Original pretrained `yolo11s.pt` (NOT fine-tuned from E001)

---

## 3. Measured Validation Metrics (`validation/` Split)

| Metric | E001 Baseline (640px) | E002 Ablation (768px) | Absolute Delta | Relative Gain |
| :--- | :---: | :---: | :---: | :---: |
| **Precision** | 98.22% | **99.40%** | +1.18% | +1.20% |
| **Recall** | 98.24% | **99.30%** | +1.06% | +1.08% |
| **mAP@50** | 99.44% | **99.50%** | +0.06% | +0.06% |
| **mAP@50–95** | 98.40% | **98.90%** | **+0.50%** | **+0.51%** |

### Per-Class Validation Breakdown (E002 @ 768px)

| Class ID | Class Name | Instances | Precision | Recall | mAP@50 | mAP@50–95 |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| 0 | `plastic_bottle` | 438 | 0.995 | 0.993 | 0.995 | 0.990 |
| 1 | `plastic_wrapper_bag` | 557 | 0.996 | 0.987 | 0.995 | 0.988 |
| 2 | `paper_cardboard` | 471 | 0.997 | 0.998 | 0.995 | 0.990 |
| 3 | `glass_bottle_container` | 447 | 0.989 | 0.993 | 0.995 | 0.988 |
| 4 | `metal_can` | 550 | 0.992 | 0.993 | 0.995 | 0.988 |
| **All** | **Overall** | **2,463** | **0.994** | **0.993** | **0.995** | **0.989** |

---

## 4. Resource & Operational Overhead

- **Peak GPU Memory:** 5.67 GB VRAM (fits comfortably within 8GB VRAM footprint).
- **Inference Latency:** 3.9ms per image (5.4ms total including pre/post processing; ~185 FPS on RTX 4060 Laptop GPU).

---

## 5. Benchmark Isolation Verification

- **`test_locked_v2` Evaluated:** **NO** (0 inferences performed - SACRED & UNTOUCHED)
- **`india_real_world` Evaluated:** **NO** (0 inferences performed - INDEPENDENT BENCHMARK UNTOUCHED)

---

## 6. Official Status Declarations

```
EXPERIMENT 002 COMPLETE
LOCKED TEST AND INDIA BENCHMARK UNTOUCHED
```
