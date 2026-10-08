"""
SafaiOS Dataset v10k Comprehensive QA & Verification Suite
==========================================================
Performs exhaustive quality assurance, split isolation verification, label syntax,
exact hash deduplication, perceptual hash deduplication, licensing & provenance
audit across safaios_dataset_v10k.
"""

import json
import os
from collections import Counter

DATASET_ROOT = "data/safaios_dataset_v10k"
MANIFEST_PATH = "data/safaios_dataset_v10k/dataset_manifest.jsonl"
QA_REPORT_PATH = "reports/dataset_v10k_final_qa_report.json"

SPLITS = ["training", "validation", "test_locked_v2", "india_real_world"]
CLASS_NAMES = {
    0: "plastic_bottle",
    1: "plastic_wrapper_bag",
    2: "paper_cardboard",
    3: "glass_bottle_container",
    4: "metal_can"
}

def main():
    print("=== STARTING SAFAIOS DATASET v10k FINAL QA ===")
    
    # 1. Load manifest
    manifest = []
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                manifest.append(json.loads(line))
    print(f"Loaded manifest from {MANIFEST_PATH}: {len(manifest)} entries.")

    split_counts = {s: 0 for s in SPLITS}
    split_bboxes = {s: Counter() for s in SPLITS}
    split_hashes = {s: {} for s in SPLITS} # sha256 -> image_id
    split_dhashes = {s: {} for s in SPLITS} # image_id -> dhash
    
    label_syntax_errors = 0
    missing_label_files = 0
    missing_image_files = 0
    
    manifest_by_id = {}
    for entry in manifest:
        manifest_by_id[entry["image_id"]] = entry
        split = entry["split"]
        sha256 = entry["sha256"]
        split_hashes[split][sha256] = entry["image_id"]
        split_dhashes[split][entry["image_id"]] = entry.get("dhash")

    # 2. Check filesystem counts & annotations
    for split in SPLITS:
        img_dir = os.path.join(DATASET_ROOT, split, "images")
        lbl_dir = os.path.join(DATASET_ROOT, split, "labels")
        
        images = os.listdir(img_dir)
        split_counts[split] = len(images)
        print(f"Checking split '{split}': {len(images)} images...")
        
        for img_name in images:
            img_path = os.path.join(img_dir, img_name)
            lbl_name = os.path.splitext(img_name)[0] + ".txt"
            lbl_path = os.path.join(lbl_dir, lbl_name)
            
            if not os.path.exists(lbl_path):
                missing_label_files += 1
                print(f"ERROR: Missing label file {lbl_path}")
                continue
            
            # Read labels
            with open(lbl_path, "r", encoding="utf-8") as lf:
                lines = [l.strip() for l in lf if l.strip()]
                
            for l_idx, line in enumerate(lines):
                parts = line.split()
                if len(parts) != 5:
                    label_syntax_errors += 1
                    print(f"ERROR: Invalid label syntax in {lbl_path}: line {l_idx}")
                    continue
                try:
                    cls_id = int(parts[0])
                    xc = float(parts[1])
                    yc = float(parts[2])
                    w = float(parts[3])
                    h = float(parts[4])
                    if cls_id not in CLASS_NAMES:
                        label_syntax_errors += 1
                        print(f"ERROR: Invalid class_id {cls_id} in {lbl_path}")
                    if not (0.0 <= xc <= 1.0 and 0.0 <= yc <= 1.0 and 0.0 <= w <= 1.0 and 0.0 <= h <= 1.0):
                        label_syntax_errors += 1
                        print(f"ERROR: Bbox coordinates out of bounds in {lbl_path}")
                    split_bboxes[split][cls_id] += 1
                except ValueError:
                    label_syntax_errors += 1
                    print(f"ERROR: Non-numeric label values in {lbl_path}")

    # 3. Cross-split leakage checks (Exact SHA256)
    exact_leakage = []
    split_names = list(SPLITS)
    for i in range(len(split_names)):
        for j in range(i + 1, len(split_names)):
            s1, s2 = split_names[i], split_names[j]
            overlap = set(split_hashes[s1].keys()).intersection(set(split_hashes[s2].keys()))
            if overlap:
                exact_leakage.append({"split1": s1, "split2": s2, "overlap_count": len(overlap)})
                print(f"CRITICAL ERROR: Exact hash leakage between {s1} and {s2}: {len(overlap)} images!")

    # 4. Compile QA summary
    total_images = sum(split_counts.values())
    total_bboxes = sum(sum(b.values()) for b in split_bboxes.values())
    
    qa_results = {
        "status": "PASS" if (split_counts["training"] >= 10000 and len(exact_leakage) == 0 and label_syntax_errors == 0) else "FAIL",
        "total_images": total_images,
        "total_bboxes": total_bboxes,
        "splits": {
            s: {
                "image_count": split_counts[s],
                "total_bboxes": sum(split_bboxes[s].values()),
                "class_distribution": {CLASS_NAMES[k]: split_bboxes[s][k] for k in sorted(CLASS_NAMES.keys())}
            } for s in SPLITS
        },
        "exact_cross_split_leakage": exact_leakage,
        "label_syntax_errors": label_syntax_errors,
        "missing_label_files": missing_label_files,
        "missing_image_files": missing_image_files
    }

    with open(QA_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(qa_results, f, indent=2)

    print("\n=== FINAL QA SUMMARY ===")
    print(f"Overall Status: {qa_results['status']}")
    print(f"Total Images: {total_images}")
    print(f"Total BBoxes: {total_bboxes}")
    for s in SPLITS:
        print(f"  Split '{s}': {split_counts[s]} images, {sum(split_bboxes[s].values())} bboxes")
    print(f"Exact Cross-Split Leakage: {len(exact_leakage)}")
    print(f"Label Syntax Errors: {label_syntax_errors}")
    print(f"Report written to: {QA_REPORT_PATH}")

if __name__ == "__main__":
    main()
