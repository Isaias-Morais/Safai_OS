"""
SafaiOS Comprehensive Dataset Audit & Quality Inspection Pipeline
Checks for corrupt images, invalid YOLO annotations, out-of-bound bounding boxes,
duplicate image hashes, near-duplicate sequence leakage, class imbalances, and object size ratios.
"""
import os
import sys
import glob
import yaml
import hashlib
from pathlib import Path
from PIL import Image, ImageStat

def audit_yolo_dataset(data_dir="data", config_path="configs/dataset.yaml"):
    print("==================================================")
    print("  SafaiOS Dataset Audit & Quality Inspection")
    print("==================================================")
    
    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f)

    classes = cfg["names"]
    num_classes = len(classes)
    print(f"Loaded Taxonomy ({num_classes} classes): {classes}")

    data_path = Path(data_dir)
    splits = ["train", "val", "test"]
    
    report = {
        "total_images": 0,
        "total_labels": 0,
        "total_boxes": 0,
        "corrupt_images": [],
        "invalid_label_files": [],
        "out_of_bound_boxes": [],
        "duplicate_image_hashes": {},
        "split_leakage_detected": [],
        "class_counts": {c_id: 0 for c_id in classes.keys()},
        "box_size_distribution": {"small (<32x32)": 0, "medium (32x32 to 96x96)": 0, "large (>96x96)": 0},
        "resolutions": []
    }
    
    split_hashes = {"train": set(), "val": set(), "test": set()}

    for split in splits:
        img_dir = data_path / split / "images"
        lbl_dir = data_path / split / "labels"
        
        if not img_dir.exists():
            print(f"Split path '{img_dir}' does not exist yet. Run dataset ingestion first.")
            continue

        image_files = list(img_dir.glob("*.jpg")) + list(img_dir.glob("*.png")) + list(img_dir.glob("*.jpeg"))
        print(f"\n--- Auditing Split: {split.upper()} ({len(image_files)} images) ---")
        
        for img_path in image_files:
            report["total_images"] += 1
            
            # 1. Verify Image Integrity & Resolution
            try:
                with Image.open(img_path) as img:
                    img.verify()
                with Image.open(img_path) as img:
                    width, height = img.size
                    report["resolutions"].append((width, height))
                    
                    # Compute MD5 file hash for duplicate & leakage detection
                    with open(img_path, "rb") as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                        split_hashes[split].add(file_hash)
                        
                        if file_hash in report["duplicate_image_hashes"]:
                            report["duplicate_image_hashes"][file_hash].append(str(img_path))
                        else:
                            report["duplicate_image_hashes"][file_hash] = [str(img_path)]
            except Exception as e:
                report["corrupt_images"].append({"path": str(img_path), "error": str(e)})
                continue

            # 2. Verify Matching YOLO Bounding Box Annotations
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
                    
                    # Validate class ID
                    if c_id not in classes:
                        report["invalid_label_files"].append({"path": str(lbl_path), "error": f"Unknown class ID {c_id}"})
                        continue
                        
                    # Validate BBox range [0.0, 1.0]
                    if not (0.0 <= x_c <= 1.0 and 0.0 <= y_c <= 1.0 and 0.0 < w <= 1.0 and 0.0 < h <= 1.0):
                        report["out_of_bound_boxes"].append({"path": str(lbl_path), "line": line_idx, "bbox": [x_c, y_c, w, h]})
                    
                    report["total_boxes"] += 1
                    report["class_counts"][c_id] += 1
                    
                    # BBox area in pixels relative to 640x640 input
                    pix_w, pix_h = w * 640, h * 640
                    area = pix_w * pix_h
                    if area < 32 * 32:
                        report["box_size_distribution"]["small (<32x32)"] += 1
                    elif area <= 96 * 96:
                        report["box_size_distribution"]["medium (32x32 to 96x96)"] += 1
                    else:
                        report["box_size_distribution"]["large (>96x96)"] += 1

    # 3. Check Split Data Leakage
    train_val_leak = split_hashes["train"].intersection(split_hashes["val"])
    train_test_leak = split_hashes["train"].intersection(split_hashes["test"])
    val_test_leak = split_hashes["val"].intersection(split_hashes["test"])
    
    if train_val_leak:
        report["split_leakage_detected"].append(f"Train-Val Leakage: {len(train_val_leak)} hashes")
    if train_test_leak:
        report["split_leakage_detected"].append(f"Train-Test Leakage: {len(train_test_leak)} hashes")
    if val_test_leak:
        report["split_leakage_detected"].append(f"Val-Test Leakage: {len(val_test_leak)} hashes")

    # Audit Report Summary Output
    print("\n==================================================")
    print("  AUDIT SUMMARY RESULTS")
    print("==================================================")
    print(f"Total Images Inspected:       {report['total_images']}")
    print(f"Total Label Files Inspected:  {report['total_labels']}")
    print(f"Total Bounding Boxes:         {report['total_boxes']}")
    print(f"Corrupt Images Found:         {len(report['corrupt_images'])}")
    print(f"Invalid Label Files:          {len(report['invalid_label_files'])}")
    print(f"Out-of-Bound BBoxes:          {len(report['out_of_bound_boxes'])}")
    print(f"Split Leakage Issues:         {len(report['split_leakage_detected'])}")
    
    duplicates = {k: v for k, v in report["duplicate_image_hashes"].items() if len(v) > 1}
    print(f"Duplicate Image Clusters:     {len(duplicates)}")
    
    print("\n--- Per-Class Bounding Box Distribution ---")
    for c_id, c_name in classes.items():
        count = report["class_counts"].get(c_id, 0)
        print(f"  [{c_id}] {c_name:25s}: {count:6d} boxes")

    print("\n--- Bounding Box Size Distribution (at 640x640) ---")
    for size_cat, count in report["box_size_distribution"].items():
        print(f"  {size_cat:25s}: {count:6d} boxes")

    return report

if __name__ == "__main__":
    audit_yolo_dataset()
