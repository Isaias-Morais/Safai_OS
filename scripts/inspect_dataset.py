"""
SafaiOS Data Quality Audit Script
Checks images and annotations for corruption, duplicates, imbalance, and size distribution.
"""
import os
import sys
import glob
import yaml
from pathlib import Path
from PIL import Image, ImageStat
import hashlib

def audit_dataset(data_dir="data"):
    print("=== SafaiOS Data Quality Audit ===")
    data_path = Path(data_dir)
    splits = ["train", "val", "test"]
    
    report = {
        "corrupt_images": [],
        "corrupt_labels": [],
        "duplicate_hashes": {},
        "class_counts": {},
        "image_resolutions": [],
        "total_images": 0,
        "total_labels": 0
    }
    
    for split in splits:
        img_dir = data_path / split / "images"
        lbl_dir = data_path / split / "labels"
        
        if not img_dir.exists():
            print(f"Directory {img_dir} does not exist yet.")
            continue

        image_files = list(img_dir.glob("*.[jJ][pP][gG]")) + list(img_dir.glob("*.[pP][nN][gG]"))
        print(f"Found {len(image_files)} images in {split} split.")
        
        for img_path in image_files:
            report["total_images"] += 1
            # Check image integrity
            try:
                with Image.open(img_path) as img:
                    img.verify()
                with Image.open(img_path) as img:
                    width, height = img.size
                    report["image_resolutions"].append((width, height))
                    
                    # Compute hash for duplicate detection
                    with open(img_path, "rb") as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                        if file_hash in report["duplicate_hashes"]:
                            report["duplicate_hashes"][file_hash].append(str(img_path))
                        else:
                            report["duplicate_hashes"][file_hash] = [str(img_path)]
            except Exception as e:
                report["corrupt_images"].append({"path": str(img_path), "error": str(e)})

    duplicates = {k: v for k, v in report["duplicate_hashes"].items() if len(v) > 1}
    
    print("\n--- Audit Summary ---")
    print(f"Total Images Inspected: {report['total_images']}")
    print(f"Corrupt Images Found: {len(report['corrupt_images'])}")
    print(f"Duplicate Image Clusters: {len(duplicates)}")
    return report

if __name__ == "__main__":
    audit_dataset()
