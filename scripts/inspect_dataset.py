"""
SafaiOS Comprehensive Dataset Audit & Quality Inspection Pipeline
Inspects data/training, data/validation, data/test_locked, data/india_real_world for image integrity,
bounding box coordinate range [0.0, 1.0], zero-area boxes, MD5 duplicate hashes, sequence leakage,
class distributions, and object size distributions.
"""
import os
import sys
import yaml
import hashlib
from pathlib import Path
from PIL import Image

def audit_dataset(data_dir="data", config_path="configs/dataset.yaml"):
    print("==================================================")
    print("  SafaiOS Dataset Audit & Quality Inspection")
    print("==================================================")
    
    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f)

    classes = cfg["names"]
    num_classes = len(classes)
    print(f"Loaded Taxonomy ({num_classes} classes): {classes}")

    data_path = Path(data_dir)
    target_splits = {
        "training": data_path / "training",
        "validation": data_path / "validation",
        "test_locked": data_path / "test_locked",
        "india_real_world": data_path / "india_real_world"
    }
    
    report = {
        "total_images": 0,
        "total_labels": 0,
        "total_boxes": 0,
        "corrupt_images": [],
        "invalid_label_files": [],
        "zero_area_boxes": [],
        "out_of_bound_boxes": [],
        "duplicate_image_hashes": {},
        "split_leakage_detected": [],
        "class_counts": {c_id: 0 for c_id in classes.keys()},
        "box_size_distribution": {"small (<32x32)": 0, "medium (32x32 to 96x96)": 0, "large (>96x96)": 0},
        "split_counts": {}
    }
    
    split_hashes = {}

    for split_name, split_path in target_splits.items():
        img_dir = split_path / "images"
        lbl_dir = split_path / "labels"
        
        split_hashes[split_name] = set()
        
        if not img_dir.exists():
            print(f"Directory '{img_dir}' does not exist.")
            continue

        image_files = list(img_dir.glob("*.jpg")) + list(img_dir.glob("*.png")) + list(img_dir.glob("*.jpeg"))
        print(f"\n--- Auditing Split: {split_name.upper()} ({len(image_files)} images) ---")
        
        split_img_cnt = 0
        split_box_cnt = 0

        for img_path in image_files:
            report["total_images"] += 1
            split_img_cnt += 1
            
            # 1. Image Integrity & Resolution Check
            try:
                with Image.open(img_path) as img:
                    img.verify()
                with Image.open(img_path) as img:
                    width, height = img.size
                    
                    with open(img_path, "rb") as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                        split_hashes[split_name].add(file_hash)
                        
                        if file_hash in report["duplicate_image_hashes"]:
                            report["duplicate_image_hashes"][file_hash].append(str(img_path))
                        else:
                            report["duplicate_image_hashes"][file_hash] = [str(img_path)]
            except Exception as e:
                report["corrupt_images"].append({"path": str(img_path), "error": str(e)})
                continue

            # 2. Annotation Verification
            lbl_path = lbl_dir / f"{img_path.stem}.txt"
            if not lbl_path.exists():
                report["invalid_label_files"].append({"path": str(lbl_path), "error": "Missing label file"})
                continue
                
            report["total_labels"] += 1
            
            with open(lbl_path, "r") as lf:
                lines = lf.readlines()
                for line_idx, line in enumerate(lines):
                    parts = line.strip().split()
                    if len(parts) != 5:
                        report["invalid_label_files"].append({"path": str(lbl_path), "line": line_idx, "content": line})
                        continue
                    
                    c_id, x_c, y_c, w, h = int(parts[0]), float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
                    
                    if c_id not in classes:
                        report["invalid_label_files"].append({"path": str(lbl_path), "error": f"Unknown class ID {c_id}"})
                        continue
                        
                    if w <= 0.0 or h <= 0.0:
                        report["zero_area_boxes"].append({"path": str(lbl_path), "line": line_idx, "bbox": [x_c, y_c, w, h]})
                        continue
                        
                    if not (0.0 <= x_c <= 1.0 and 0.0 <= y_c <= 1.0 and 0.0 < w <= 1.0 and 0.0 < h <= 1.0):
                        report["out_of_bound_boxes"].append({"path": str(lbl_path), "line": line_idx, "bbox": [x_c, y_c, w, h]})
                    
                    report["total_boxes"] += 1
                    split_box_cnt += 1
                    report["class_counts"][c_id] += 1
                    
                    pix_w, pix_h = w * 640, h * 640
                    area = pix_w * pix_h
                    if area < 32 * 32:
                        report["box_size_distribution"]["small (<32x32)"] += 1
                    elif area <= 96 * 96:
                        report["box_size_distribution"]["medium (32x32 to 96x96)"] += 1
                    else:
                        report["box_size_distribution"]["large (>96x96)"] += 1

        report["split_counts"][split_name] = {"images": split_img_cnt, "boxes": split_box_cnt}

    # 3. Data Leakage Verification
    for s1 in ["training", "validation", "test_locked", "india_real_world"]:
        for s2 in ["training", "validation", "test_locked", "india_real_world"]:
            if s1 < s2:
                leak = split_hashes[s1].intersection(split_hashes[s2])
                if leak:
                    report["split_leakage_detected"].append(f"{s1.upper()} <-> {s2.upper()} Leakage: {len(leak)} hashes")

    # Output Audit Report Summary
    print("\n==================================================")
    print("  EMPIRICAL AUDIT SUMMARY RESULTS")
    print("==================================================")
    print(f"Total Images Inspected:       {report['total_images']}")
    print(f"Total Label Files Inspected:  {report['total_labels']}")
    print(f"Total Bounding Boxes:         {report['total_boxes']}")
    print(f"Corrupt Images Found:         {len(report['corrupt_images'])}")
    print(f"Invalid Label Files:          {len(report['invalid_label_files'])}")
    print(f"Zero-Area Boxes:              {len(report['zero_area_boxes'])}")
    print(f"Out-of-Bound BBoxes:          {len(report['out_of_bound_boxes'])}")
    print(f"Split Leakage Issues:         {len(report['split_leakage_detected'])}")
    
    duplicates = {k: v for k, v in report["duplicate_image_hashes"].items() if len(v) > 1}
    print(f"Duplicate Image Clusters:     {len(duplicates)}")
    
    print("\n--- Per-Split Image and Box Breakdown ---")
    for sp_name, cnts in report["split_counts"].items():
        print(f"  {sp_name:20s}: {cnts['images']:6d} images | {cnts['boxes']:6d} boxes")

    print("\n--- Per-Class Bounding Box Distribution ---")
    for c_id, c_name in classes.items():
        count = report["class_counts"].get(c_id, 0)
        print(f"  [{c_id}] {c_name:25s}: {count:6d} boxes")

    print("\n--- Bounding Box Size Distribution (at 640x640) ---")
    for size_cat, count in report["box_size_distribution"].items():
        print(f"  {size_cat:25s}: {count:6d} boxes")

    return report

if __name__ == "__main__":
    audit_dataset()
