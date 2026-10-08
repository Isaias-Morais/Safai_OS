"""
SafaiOS Machine-Readable Dataset Manifest Generator
Scans dataset splits, computes hashes, extracts image & bbox metadata,
and exports traceable JSONL manifest.
"""
import os
import json
import yaml
from pathlib import Path
from PIL import Image
from src.data.hashing import compute_md5, compute_sha256, compute_dhash

TAXONOMY = {
    0: "plastic_bottle",
    1: "plastic_wrapper_bag",
    2: "paper_cardboard",
    3: "glass_bottle_container",
    4: "metal_can"
}

def generate_manifest(data_dir="data", output_manifest="reports/dataset_manifest_v1.0.jsonl", version="safaios_dataset_v1.0"):
    print(f"=== Generating Dataset Manifest ({version}) ===")
    data_path = Path(data_dir)
    target_splits = ["training", "validation", "test_locked", "india_real_world"]
    
    entries = []
    global_idx = 1

    for split in target_splits:
        sp_path = data_path / split
        img_dir = sp_path / "images"
        lbl_dir = sp_path / "labels"
        
        if not img_dir.exists():
            continue

        image_files = list(img_dir.glob("*.jpg")) + list(img_dir.glob("*.png")) + list(img_dir.glob("*.jpeg"))
        
        for img_p in image_files:
            lbl_p = lbl_dir / f"{img_p.stem}.txt"
            
            # Extract basic dimensions & hashes
            try:
                with Image.open(img_p) as im:
                    w, h = im.size
                md5_val = compute_md5(img_p)
                sha256_val = compute_sha256(img_p)
                dhash_val = compute_dhash(img_p)
                val_status = "VALID"
            except Exception as e:
                val_status = f"CORRUPT_{e}"
                w, h = 0, 0
                md5_val, sha256_val, dhash_val = "error", "error", "error"

            # Parse bounding boxes
            bbox_count = 0
            class_ids = set()
            class_names = set()
            
            if lbl_p.exists():
                with open(lbl_p, "r") as lf:
                    for line in lf:
                        parts = line.strip().split()
                        if len(parts) == 5:
                            c_id = int(parts[0])
                            bbox_count += 1
                            if c_id in TAXONOMY:
                                class_ids.add(c_id)
                                class_names.add(TAXONOMY[c_id])

            # Determine source dataset provenance
            source_dataset = "TACO" if "taco_" in img_p.name else "unknown"
            orig_id = img_p.stem.replace("taco_", "") if source_dataset == "TACO" else "unknown"
            
            entry = {
                "image_id": f"safaios_img_{global_idx:07d}",
                "filename": f"{split}/images/{img_p.name}",
                "source_dataset": source_dataset,
                "original_source_id": orig_id,
                "source_url": "unknown", # Not fabricated
                "license": "CC BY 4.0" if source_dataset == "TACO" else "unknown",
                "annotation_license": "CC BY 4.0" if source_dataset == "TACO" else "unknown",
                "annotation_format": "yolo_normalized",
                "sha256": sha256_val,
                "md5": md5_val,
                "perceptual_hash": dhash_val,
                "width": w,
                "height": h,
                "bbox_count": bbox_count,
                "class_ids": sorted(list(class_ids)),
                "class_names": sorted(list(class_names)),
                "split": split,
                "sequence_id": f"seq_{orig_id[:2]}" if source_dataset == "TACO" else "seq_unknown",
                "dataset_version": version,
                "validation_status": val_status,
                "approval_status": "APPROVED" if val_status == "VALID" else "REJECTED"
            }
            entries.append(entry)
            global_idx += 1

    Path(output_manifest).parent.mkdir(parents=True, exist_ok=True)
    with open(output_manifest, "w", encoding="utf-8") as out_f:
        for entry in entries:
            out_f.write(json.dumps(entry) + "\n")

    print(f"Manifest written with {len(entries)} traceable image entries to {output_manifest}.")
    return entries

if __name__ == "__main__":
    generate_manifest()
