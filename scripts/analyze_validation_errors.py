"""
SafaiOS Validation Error Analysis & Comparison Engine
Phase 4: Detailed comparison between E001 (640px) and E002 (768px) on validation/ split.
"""

import json
import hashlib
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

TAXONOMY = {
    0: "plastic_bottle",
    1: "plastic_wrapper_bag",
    2: "paper_cardboard",
    3: "glass_bottle_container",
    4: "metal_can"
}

E001_WEIGHTS = "runs/detect/runs/safaios/safaios_yolo11s_v10k_baseline/weights/best.pt"
E001_EXPECTED_HASH = "49e9e047fbb04c66244b734623bb4e84abfbab5a3aa9797c375d926919a86737"

E002_WEIGHTS = "runs/detect/runs/detect/runs/safaios/safaios_yolo11s_v10k_img768/weights/best.pt"
E002_EXPECTED_HASH = "8bd30b05a0b4a84d95c5e71f213b967d255144a8fe57791ef110b920fc86d073"

DATA_YAML = "data/safaios_dataset_v10k/data.yaml"
VAL_IMAGES_DIR = Path("data/safaios_dataset_v10k/validation/images")
VAL_LABELS_DIR = Path("data/safaios_dataset_v10k/validation/labels")


def compute_sha256(filepath):
    p = Path(filepath)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().lower()


def compute_iou(boxA, boxB):
    # box format: [x1, y1, x2, y2]
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interW = max(0.0, xB - xA)
    interH = max(0.0, yB - yA)
    interArea = interW * interH

    boxAArea = max(0.0, (boxA[2] - boxA[0]) * (boxA[3] - boxA[1]))
    boxBArea = max(0.0, (boxB[2] - boxB[0]) * (boxB[3] - boxB[1]))

    unionArea = boxAArea + boxBArea - interArea
    if unionArea <= 0:
        return 0.0
    return interArea / unionArea


def load_ground_truth():
    gt_data = {}
    label_files = sorted(list(VAL_LABELS_DIR.glob("*.txt")))
    for lf in label_files:
        stem = lf.stem
        img_file = VAL_IMAGES_DIR / f"{stem}.jpg"
        if not img_file.exists():
            img_file = VAL_IMAGES_DIR / f"{stem}.png"
        
        with Image.open(img_file) as im:
            w_img, h_img = im.size

        boxes = []
        with open(lf, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 5:
                    cls_id = int(parts[0])
                    xc, yc, w_norm, h_norm = map(float, parts[1:5])
                    
                    x1 = (xc - w_norm / 2.0) * w_img
                    y1 = (yc - h_norm / 2.0) * h_img
                    x2 = (xc + w_norm / 2.0) * w_img
                    y2 = (yc + h_norm / 2.0) * h_img

                    area_px = (w_norm * w_img) * (h_norm * h_img)
                    area_norm = w_norm * h_norm
                    
                    # 1. Standard COCO normalized proxy:
                    # COCO small: area < 32^2 on 640x640 = area_norm < 0.0025
                    # COCO medium: 32^2 <= area <= 96^2 = 0.0025 <= area_norm <= 0.0225
                    # COCO large: area > 96^2 = area_norm > 0.0225
                    if area_norm < 0.0025:
                        coco_size_cat = "small"
                    elif area_norm <= 0.0225:
                        coco_size_cat = "medium"
                    else:
                        coco_size_cat = "large"

                    # 2. Dataset-relative size tiers (empirical distribution of SafaiOS dataset):
                    # Relatively Small: area_norm < 0.025 (< 2.5% image area)
                    # Medium: 0.025 <= area_norm <= 0.050 (2.5% to 5.0% image area)
                    # Large: area_norm > 0.050 (> 5.0% image area)
                    if area_norm < 0.025:
                        dataset_size_cat = "small_relative"
                    elif area_norm <= 0.050:
                        dataset_size_cat = "medium_relative"
                    else:
                        dataset_size_cat = "large_relative"

                    boxes.append({
                        "class_id": cls_id,
                        "class_name": TAXONOMY[cls_id],
                        "bbox_norm": [xc, yc, w_norm, h_norm],
                        "bbox_xyxy": [x1, y1, x2, y2],
                        "area_px": area_px,
                        "area_norm": area_norm,
                        "coco_size_cat": coco_size_cat,
                        "dataset_size_cat": dataset_size_cat
                    })

        # Calculate max pairwise overlap for each GT box
        n = len(boxes)
        for i in range(n):
            max_iou = 0.0
            for j in range(n):
                if i != j:
                    iou = compute_iou(boxes[i]["bbox_xyxy"], boxes[j]["bbox_xyxy"])
                    if iou > max_iou:
                        max_iou = iou
            boxes[i]["max_overlap_iou"] = max_iou
            boxes[i]["overlap_cat"] = "overlapping" if max_iou >= 0.1 else "isolated"
            boxes[i]["scene_density"] = "single" if n == 1 else ("sparse" if n <= 3 else "dense")

        gt_data[stem] = {
            "image_stem": stem,
            "image_path": str(img_file),
            "width": w_img,
            "height": h_img,
            "boxes": boxes
        }
    return gt_data


def run_model_inference(model, imgsz, conf_thresh=0.25, iou_thresh=0.6):
    print(f"\n--- Running Full Validation Inference (imgsz={imgsz}, conf={conf_thresh}, iou={iou_thresh}) ---")
    results = model.predict(
        source=str(VAL_IMAGES_DIR),
        imgsz=imgsz,
        conf=conf_thresh,
        iou=iou_thresh,
        device=0,
        verbose=False,
        batch=16
    )

    preds_by_stem = {}
    for r in results:
        stem = Path(r.path).stem
        preds = []
        if r.boxes is not None and len(r.boxes) > 0:
            xyxy = r.boxes.xyxy.cpu().numpy()
            conf = r.boxes.conf.cpu().numpy()
            cls = r.boxes.cls.cpu().numpy().astype(int)

            for i in range(len(xyxy)):
                cls_id = int(cls[i])
                preds.append({
                    "class_id": cls_id,
                    "class_name": TAXONOMY.get(cls_id, f"unknown_{cls_id}"),
                    "bbox_xyxy": [float(xyxy[i][0]), float(xyxy[i][1]), float(xyxy[i][2]), float(xyxy[i][3])],
                    "confidence": float(conf[i])
                })
        preds_by_stem[stem] = preds
    return preds_by_stem


def match_and_analyze(gt_data, preds_data, iou_thresh=0.5):
    """
    Match predictions to ground truth per image using greedy IoU.
    Compute detailed stratifications: size, class, density, overlap.
    """
    total_gt = 0
    total_preds = 0
    
    tp_count = 0
    fn_count = 0
    fp_confusion_count = 0
    fp_localization_count = 0
    fp_background_count = 0

    confusion_matrix = np.zeros((6, 6), dtype=int) # 0-4 classes, index 5 is background

    by_class = {c: {"gt": 0, "tp": 0, "fn": 0, "fp": 0} for c in range(5)}
    by_coco_size = {"small": {"gt": 0, "tp": 0, "fn": 0},
                    "medium": {"gt": 0, "tp": 0, "fn": 0},
                    "large": {"gt": 0, "tp": 0, "fn": 0}}
    by_dataset_size = {"small_relative": {"gt": 0, "tp": 0, "fn": 0},
                       "medium_relative": {"gt": 0, "tp": 0, "fn": 0},
                       "large_relative": {"gt": 0, "tp": 0, "fn": 0}}
    by_density = {"single": {"gt": 0, "tp": 0, "fn": 0},
                  "sparse": {"gt": 0, "tp": 0, "fn": 0},
                  "dense": {"gt": 0, "tp": 0, "fn": 0}}
    by_overlap = {"isolated": {"gt": 0, "tp": 0, "fn": 0},
                  "overlapping": {"gt": 0, "tp": 0, "fn": 0}}

    failure_cases = {
        "false_negatives": [],
        "false_positives_background": [],
        "class_confusions": [],
        "localization_errors": [],
        "small_relative_failures": [],
        "dense_scene_failures": []
    }

    for stem, gt_info in gt_data.items():
        gt_boxes = gt_info["boxes"]
        preds = preds_data.get(stem, [])
        total_gt += len(gt_boxes)
        total_preds += len(preds)

        for b in gt_boxes:
            c = b["class_id"]
            csz = b["coco_size_cat"]
            dsz = b["dataset_size_cat"]
            dens = b["scene_density"]
            ov = b["overlap_cat"]
            by_class[c]["gt"] += 1
            by_coco_size[csz]["gt"] += 1
            by_dataset_size[dsz]["gt"] += 1
            by_density[dens]["gt"] += 1
            by_overlap[ov]["gt"] += 1

        matched_gt = set()
        matched_preds = set()

        # Sort predictions by confidence descending
        sorted_preds_idx = sorted(range(len(preds)), key=lambda k: preds[k]["confidence"], reverse=True)

        for p_idx in sorted_preds_idx:
            p = preds[p_idx]
            best_iou = 0.0
            best_gt_idx = -1

            for g_idx, g in enumerate(gt_boxes):
                if g_idx in matched_gt:
                    continue
                iou = compute_iou(p["bbox_xyxy"], g["bbox_xyxy"])
                if iou > best_iou:
                    best_iou = iou
                    best_gt_idx = g_idx

            if best_iou >= iou_thresh:
                matched_gt_box = gt_boxes[best_gt_idx]
                if p["class_id"] == matched_gt_box["class_id"]:
                    # True Positive
                    matched_gt.add(best_gt_idx)
                    matched_preds.add(p_idx)
                    tp_count += 1
                    c = p["class_id"]
                    by_class[c]["tp"] += 1
                    by_coco_size[matched_gt_box["coco_size_cat"]]["tp"] += 1
                    by_dataset_size[matched_gt_box["dataset_size_cat"]]["tp"] += 1
                    by_density[matched_gt_box["scene_density"]]["tp"] += 1
                    by_overlap[matched_gt_box["overlap_cat"]]["tp"] += 1
                    confusion_matrix[c, c] += 1
                else:
                    # Class Confusion
                    matched_preds.add(p_idx)
                    fp_confusion_count += 1
                    by_class[p["class_id"]]["fp"] += 1
                    confusion_matrix[matched_gt_box["class_id"], p["class_id"]] += 1
                    failure_cases["class_confusions"].append({
                        "stem": stem,
                        "pred_class": p["class_name"],
                        "gt_class": matched_gt_box["class_name"],
                        "pred_bbox": p["bbox_xyxy"],
                        "gt_bbox": matched_gt_box["bbox_xyxy"],
                        "confidence": p["confidence"],
                        "iou": best_iou
                    })
            elif best_iou >= 0.1:
                # Poor localization
                matched_preds.add(p_idx)
                fp_localization_count += 1
                by_class[p["class_id"]]["fp"] += 1
                matched_gt_box = gt_boxes[best_gt_idx]
                failure_cases["localization_errors"].append({
                    "stem": stem,
                    "pred_class": p["class_name"],
                    "gt_class": matched_gt_box["class_name"],
                    "pred_bbox": p["bbox_xyxy"],
                    "gt_bbox": matched_gt_box["bbox_xyxy"],
                    "confidence": p["confidence"],
                    "iou": best_iou
                })
            else:
                # Background False Positive
                matched_preds.add(p_idx)
                fp_background_count += 1
                by_class[p["class_id"]]["fp"] += 1
                confusion_matrix[5, p["class_id"]] += 1 # 5 = background
                failure_cases["false_positives_background"].append({
                    "stem": stem,
                    "pred_class": p["class_name"],
                    "pred_bbox": p["bbox_xyxy"],
                    "confidence": p["confidence"]
                })

        # Check Unmatched Ground Truth (False Negatives)
        for g_idx, g in enumerate(gt_boxes):
            if g_idx not in matched_gt:
                fn_count += 1
                c = g["class_id"]
                by_class[c]["fn"] += 1
                by_coco_size[g["coco_size_cat"]]["fn"] += 1
                by_dataset_size[g["dataset_size_cat"]]["fn"] += 1
                by_density[g["scene_density"]]["fn"] += 1
                by_overlap[g["overlap_cat"]]["fn"] += 1
                confusion_matrix[c, 5] += 1 # 5 = background / missed

                fn_entry = {
                    "stem": stem,
                    "class_name": g["class_name"],
                    "class_id": g["class_id"],
                    "coco_size_cat": g["coco_size_cat"],
                    "dataset_size_cat": g["dataset_size_cat"],
                    "area_px": g["area_px"],
                    "area_norm": g["area_norm"],
                    "scene_density": g["scene_density"],
                    "overlap_cat": g["overlap_cat"],
                    "gt_bbox": g["bbox_xyxy"]
                }
                failure_cases["false_negatives"].append(fn_entry)
                if g["dataset_size_cat"] == "small_relative":
                    failure_cases["small_relative_failures"].append(fn_entry)
                if g["scene_density"] == "dense":
                    failure_cases["dense_scene_failures"].append(fn_entry)

    total_fp = fp_confusion_count + fp_localization_count + fp_background_count

    return {
        "total_gt": total_gt,
        "total_preds": total_preds,
        "tp": tp_count,
        "fn": fn_count,
        "fp_total": total_fp,
        "fp_confusion": fp_confusion_count,
        "fp_localization": fp_localization_count,
        "fp_background": fp_background_count,
        "precision_op": tp_count / (tp_count + total_fp) if (tp_count + total_fp) > 0 else 0.0,
        "recall_op": tp_count / total_gt if total_gt > 0 else 0.0,
        "by_class": by_class,
        "by_coco_size": by_coco_size,
        "by_dataset_size": by_dataset_size,
        "by_density": by_density,
        "by_overlap": by_overlap,
        "confusion_matrix": confusion_matrix.tolist(),
        "failure_cases": failure_cases
    }


def main():
    print("=" * 70)
    print("SAFAIOS PHASE 4: VALIDATION ERROR ANALYSIS & COMPARISON ENGINE")
    print("=" * 70)

    # 1. Verify Hashes
    print("\n[Step 1] Verifying Checkpoint SHA256 Hashes...")
    h1 = compute_sha256(E001_WEIGHTS)
    h2 = compute_sha256(E002_WEIGHTS)

    assert h1 == E001_EXPECTED_HASH, f"E001 hash mismatch: got {h1}"
    assert h2 == E002_EXPECTED_HASH, f"E002 hash mismatch: got {h2}"
    print(f"  E001 baseline best.pt: {h1} [VERIFIED]")
    print(f"  E002 ablation best.pt: {h2} [VERIFIED]")

    # 2. Run Official ultralytics model.val() on validation split only
    from ultralytics import YOLO

    print("\n[Step 2] Executing Official Validation Evaluation (split='val')...")
    print("  -> Evaluating E001 Baseline (imgsz=640)...")
    model_e001 = YOLO(E001_WEIGHTS)
    val_e001 = model_e001.val(data=DATA_YAML, split="val", imgsz=640, device=0, verbose=False)

    print("  -> Evaluating E002 Ablation (imgsz=768)...")
    model_e002 = YOLO(E002_WEIGHTS)
    val_e002 = model_e002.val(data=DATA_YAML, split="val", imgsz=768, device=0, verbose=False)

    e001_metrics = {
        "precision": float(val_e001.box.mp),
        "recall": float(val_e001.box.mr),
        "map50": float(val_e001.box.map50),
        "map50_95": float(val_e001.box.map),
        "per_class": {
            TAXONOMY[i]: {
                "precision": float(val_e001.box.p[i]),
                "recall": float(val_e001.box.r[i]),
                "map50": float(val_e001.box.ap50[i]),
                "map50_95": float(val_e001.box.ap[i])
            } for i in range(5)
        }
    }

    e002_metrics = {
        "precision": float(val_e002.box.mp),
        "recall": float(val_e002.box.mr),
        "map50": float(val_e002.box.map50),
        "map50_95": float(val_e002.box.map),
        "per_class": {
            TAXONOMY[i]: {
                "precision": float(val_e002.box.p[i]),
                "recall": float(val_e002.box.r[i]),
                "map50": float(val_e002.box.ap50[i]),
                "map50_95": float(val_e002.box.ap[i])
            } for i in range(5)
        }
    }

    print("\n=== Validation Results Summary (Official model.val) ===")
    print(f"E001 (640px): P={e001_metrics['precision']:.4f}, R={e001_metrics['recall']:.4f}, mAP50={e001_metrics['map50']:.4f}, mAP50-95={e001_metrics['map50_95']:.4f}")
    print(f"E002 (768px): P={e002_metrics['precision']:.4f}, R={e002_metrics['recall']:.4f}, mAP50={e002_metrics['map50']:.4f}, mAP50-95={e002_metrics['map50_95']:.4f}")

    # 3. Load Ground Truth Annotations
    print("\n[Step 3] Loading Validation Ground Truth & Computing Spatial Attributes...")
    gt_data = load_ground_truth()
    print(f"  Loaded {len(gt_data)} images, total GT boxes: {sum(len(v['boxes']) for v in gt_data.values())}")

    # 4. Generate Predictions at operational thresholds (conf=0.25, iou=0.6)
    print("\n[Step 4] Running Comparative Operational Inference (conf=0.25, iou=0.6)...")
    preds_e001 = run_model_inference(model_e001, imgsz=640, conf_thresh=0.25, iou_thresh=0.6)
    preds_e002 = run_model_inference(model_e002, imgsz=768, conf_thresh=0.25, iou_thresh=0.6)

    # 5. Box Matching and Error Analysis
    print("\n[Step 5] Performing Detailed Instance-Level Matching & Stratification...")
    analysis_e001 = match_and_analyze(gt_data, preds_e001, iou_thresh=0.5)
    analysis_e002 = match_and_analyze(gt_data, preds_e002, iou_thresh=0.5)

    # 6. Save Failure Visualizations with deterministic seed
    np.random.seed(42)
    output_fig_dir = Path("reports/figures/error_analysis")
    output_fig_dir.mkdir(parents=True, exist_ok=True)

    print("\n[Step 6] Generating Reproducible Failure Visualizations...")
    # Visualize top failure examples from E002
    sample_fns = analysis_e002["failure_cases"]["false_negatives"][:4]
    for idx, fn in enumerate(sample_fns):
        stem = fn["stem"]
        img_p = Path(gt_data[stem]["image_path"])
        with Image.open(img_p) as im:
            draw = ImageDraw.Draw(im)
            gbox = fn["gt_bbox"]
            draw.rectangle(gbox, outline="lime", width=3)
            draw.text((gbox[0], max(0, gbox[1]-15)), f"GT:{fn['class_name']} ({fn['dataset_size_cat']})", fill="lime")
            for p in preds_e002.get(stem, []):
                pbox = p["bbox_xyxy"]
                draw.rectangle(pbox, outline="red", width=2)
                draw.text((pbox[0], max(0, pbox[1]-15)), f"Pred:{p['class_name']} {p['confidence']:.2f}", fill="red")
            im.save(output_fig_dir / f"fn_sample_{idx+1}_{stem}.jpg")

    sample_conf = analysis_e002["failure_cases"]["class_confusions"][:4]
    for idx, cf in enumerate(sample_conf):
        stem = cf["stem"]
        img_p = Path(gt_data[stem]["image_path"])
        with Image.open(img_p) as im:
            draw = ImageDraw.Draw(im)
            gbox = cf["gt_bbox"]
            draw.rectangle(gbox, outline="lime", width=3)
            draw.text((gbox[0], max(0, gbox[1]-15)), f"GT:{cf['gt_class']}", fill="lime")
            pbox = cf["pred_bbox"]
            draw.rectangle(pbox, outline="orange", width=2)
            draw.text((pbox[0], max(0, pbox[1]-15)), f"Confused:{cf['pred_class']} {cf['confidence']:.2f}", fill="orange")
            im.save(output_fig_dir / f"confusion_sample_{idx+1}_{stem}.jpg")

    # Small relative comparison examples (where E001 missed but E002 detected)
    e001_fn_stems = {fn["stem"] for fn in analysis_e001["failure_cases"]["small_relative_failures"]}
    e002_tp_stems = {stem for stem in gt_data if any(b["dataset_size_cat"] == "small_relative" for b in gt_data[stem]["boxes"])} - {fn["stem"] for fn in analysis_e002["failure_cases"]["small_relative_failures"]}
    recovered_stems = list(e001_fn_stems.intersection(e002_tp_stems))
    print(f"  Small relative cases missed by E001 but recovered by E002: {len(recovered_stems)}")

    for idx, stem in enumerate(recovered_stems[:3]):
        img_p = Path(gt_data[stem]["image_path"])
        with Image.open(img_p) as im:
            draw = ImageDraw.Draw(im)
            for g in gt_data[stem]["boxes"]:
                if g["dataset_size_cat"] == "small_relative":
                    draw.rectangle(g["bbox_xyxy"], outline="lime", width=3)
                    draw.text((g["bbox_xyxy"][0], max(0, g["bbox_xyxy"][1]-15)), f"GT:{g['class_name']}(small_rel)", fill="lime")
            for p in preds_e002.get(stem, []):
                draw.rectangle(p["bbox_xyxy"], outline="cyan", width=2)
                draw.text((p["bbox_xyxy"][0], p["bbox_xyxy"][1]+2), f"E002:{p['class_name']} {p['confidence']:.2f}", fill="cyan")
            im.save(output_fig_dir / f"small_recovered_{idx+1}_{stem}.jpg")

    # Save comprehensive results JSON
    analysis_record = {
        "dataset_evaluated": "data/safaios_dataset_v10k/validation",
        "validation_image_count": len(gt_data),
        "validation_box_count": sum(len(v["boxes"]) for v in gt_data.values()),
        "e001_baseline": {
            "weights": E001_WEIGHTS,
            "sha256": h1,
            "imgsz": 640,
            "official_metrics": e001_metrics,
            "operational_analysis": {
                "tp": analysis_e001["tp"],
                "fn": analysis_e001["fn"],
                "fp_total": analysis_e001["fp_total"],
                "fp_confusion": analysis_e001["fp_confusion"],
                "fp_localization": analysis_e001["fp_localization"],
                "fp_background": analysis_e001["fp_background"],
                "precision_op": analysis_e001["precision_op"],
                "recall_op": analysis_e001["recall_op"],
                "by_class": analysis_e001["by_class"],
                "by_coco_size": analysis_e001["by_coco_size"],
                "by_dataset_size": analysis_e001["by_dataset_size"],
                "by_density": analysis_e001["by_density"],
                "by_overlap": analysis_e001["by_overlap"],
                "confusion_matrix": analysis_e001["confusion_matrix"],
                "failure_cases": analysis_e001["failure_cases"]
            }
        },
        "e002_ablation": {
            "weights": E002_WEIGHTS,
            "sha256": h2,
            "imgsz": 768,
            "official_metrics": e002_metrics,
            "operational_analysis": {
                "tp": analysis_e002["tp"],
                "fn": analysis_e002["fn"],
                "fp_total": analysis_e002["fp_total"],
                "fp_confusion": analysis_e002["fp_confusion"],
                "fp_localization": analysis_e002["fp_localization"],
                "fp_background": analysis_e002["fp_background"],
                "precision_op": analysis_e002["precision_op"],
                "recall_op": analysis_e002["recall_op"],
                "by_class": analysis_e002["by_class"],
                "by_coco_size": analysis_e002["by_coco_size"],
                "by_dataset_size": analysis_e002["by_dataset_size"],
                "by_density": analysis_e002["by_density"],
                "by_overlap": analysis_e002["by_overlap"],
                "confusion_matrix": analysis_e002["confusion_matrix"],
                "failure_cases": analysis_e002["failure_cases"]
            }
        },
        "small_relative_recovery_count": len(recovered_stems)
    }

    out_json = Path("reports/experiments/SAFAIOS-E002-error-analysis.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(analysis_record, f, indent=2)

    print(f"\n[Step 7] Analysis results saved to {out_json}")
    print("\n--- Key Comparison Highlights ---")
    print(f"Overall Recall @ 0.25 conf: E001={analysis_e001['recall_op']:.4f} -> E002={analysis_e002['recall_op']:.4f}")
    
    # Dataset-relative size recall
    s1 = analysis_e001["by_dataset_size"]["small_relative"]
    s2 = analysis_e002["by_dataset_size"]["small_relative"]
    print(f"Relatively Small (<2.5% area) Recall: E001={s1['tp']/s1['gt']:.4f} ({s1['tp']}/{s1['gt']}) -> E002={s2['tp']/s2['gt']:.4f} ({s2['tp']}/{s2['gt']}) [Delta: +{(s2['tp']/s2['gt'] - s1['tp']/s1['gt'])*100:.2f}%]")

    m1 = analysis_e001["by_dataset_size"]["medium_relative"]
    m2 = analysis_e002["by_dataset_size"]["medium_relative"]
    print(f"Medium (2.5%-5.0% area) Recall: E001={m1['tp']/m1['gt']:.4f} ({m1['tp']}/{m1['gt']}) -> E002={m2['tp']/m2['gt']:.4f} ({m2['tp']}/{m2['gt']}) [Delta: +{(m2['tp']/m2['gt'] - m1['tp']/m1['gt'])*100:.2f}%]")

    l1 = analysis_e001["by_dataset_size"]["large_relative"]
    l2 = analysis_e002["by_dataset_size"]["large_relative"]
    print(f"Large (>5.0% area) Recall: E001={l1['tp']/l1['gt']:.4f} ({l1['tp']}/{l1['gt']}) -> E002={l2['tp']/l2['gt']:.4f} ({l2['tp']}/{l2['gt']}) [Delta: +{(l2['tp']/l2['gt'] - l1['tp']/l1['gt'])*100:.2f}%]")

    d1 = analysis_e001["by_density"]["dense"]
    d2 = analysis_e002["by_density"]["dense"]
    print(f"Dense-Scene (>=4 objs) Recall: E001={d1['tp']/d1['gt']:.4f} ({d1['tp']}/{d1['gt']}) -> E002={d2['tp']/d2['gt']:.4f} ({d2['tp']}/{d2['gt']})")

    o1 = analysis_e001["by_overlap"]["overlapping"]
    o2 = analysis_e002["by_overlap"]["overlapping"]
    print(f"Overlapping Objects Recall: E001={o1['tp']/o1['gt']:.4f} ({o1['tp']}/{o1['gt']}) -> E002={o2['tp']/o2['gt']:.4f} ({o2['tp']}/{o2['gt']})")

    print(f"False Positives Total: E001={analysis_e001['fp_total']} -> E002={analysis_e002['fp_total']}")
    print(f"  Class Confusion FP: E001={analysis_e001['fp_confusion']} -> E002={analysis_e002['fp_confusion']}")
    print(f"  Localization FP: E001={analysis_e001['fp_localization']} -> E002={analysis_e002['fp_localization']}")
    print(f"  Background FP: E001={analysis_e001['fp_background']} -> E002={analysis_e002['fp_background']}")
    print("\nError analysis execution complete.")


if __name__ == "__main__":
    main()
