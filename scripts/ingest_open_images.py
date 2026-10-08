"""
SafaiOS Open Images V7 Controlled Pilot Ingestion Pipeline (Milestone 2A)
Downloads, validates, deduplicates, and stages genuine candidate detection samples
from Open Images V7 for approved classes (/m/05gqfk Plastic bag -> plastic_wrapper_bag,
/m/02jnhm Tin can -> metal_can) to data/incoming/open_images_staging/.

Enforces strict quality gates, provenance preservation, and outputs an acquisition registry.
"""
import os
import sys
import json
import csv
import urllib.request
import argparse
from pathlib import Path
from PIL import Image
from collections import Counter
from src.data.hashing import compute_md5, compute_sha256, compute_dhash, hamming_distance

# Approved Open Images V7 canonical MID mappings
APPROVED_MAPPING = {
    "/m/05gqfk": {"name": "Plastic bag", "safaios_class_id": 1, "safaios_class_name": "plastic_wrapper_bag", "confidence": "HIGH"},
    "/m/02jnhm": {"name": "Tin can", "safaios_class_id": 4, "safaios_class_name": "metal_can", "confidence": "HIGH"}
}

REJECTED_OR_AMBIGUOUS_MAPPING = {
    "/m/04dr76w": {"name": "Bottle", "reason": "Ambiguous material (contains plastic, glass, metal without material tags)"},
    "/m/025dyy": {"name": "Box", "reason": "Ambiguous material (contains cardboard, plastic, wood)"},
    "/m/02pv19": {"name": "Stop sign", "reason": "REJECTED - Not paper/cardboard, completely wrong semantic object"},
    "/m/09tvcd": {"name": "Wine glass", "reason": "Stemware rather than glass bottle/container"}
}

ANNOTATIONS_URL = "https://storage.googleapis.com/openimages/v5/validation-annotations-bbox.csv"
AWS_IMAGE_BASE_URL = "https://open-images-dataset.s3.amazonaws.com/validation"

def fetch_open_images_candidates(target_count=300):
    """Fetches candidate annotations from Open Images validation CSV slice."""
    print(f"Fetching Open Images candidate annotations from {ANNOTATIONS_URL}...")
    req = urllib.request.Request(ANNOTATIONS_URL, headers={'User-Agent': 'Mozilla/5.0'})
    
    candidates_by_img = {}
    found_counts = Counter()
    
    with urllib.request.urlopen(req) as response:
        header = response.readline().decode('utf-8').strip().split(',')
        
        for line in response:
            line_str = line.decode('utf-8').strip()
            if not line_str:
                continue
            parts = line_str.split(',')
            if len(parts) >= 8:
                img_id = parts[0]
                mid = parts[2]
                
                if mid in APPROVED_MAPPING:
                    try:
                        xmin = float(parts[4])
                        xmax = float(parts[5])
                        ymin = float(parts[6])
                        ymax = float(parts[7])
                        
                        box = {
                            "mid": mid,
                            "safaios_class_id": APPROVED_MAPPING[mid]["safaios_class_id"],
                            "xmin": xmin,
                            "xmax": xmax,
                            "ymin": ymin,
                            "ymax": ymax
                        }
                        
                        if img_id not in candidates_by_img:
                            candidates_by_img[img_id] = []
                        candidates_by_img[img_id].append(box)
                        found_counts[mid] += 1
                        
                        if len(candidates_by_img) >= target_count:
                            break
                    except ValueError:
                        continue
                        
    print(f"Found {len(candidates_by_img)} candidate images containing {sum(found_counts.values())} approved bounding boxes.")
    return candidates_by_img

def run_ingestion_pipeline(dry_run=True, max_images=300):
    print("=== SafaiOS Open Images V7 Controlled Pilot Ingestion Engine ===")
    print(f"Mode: {'DRY-RUN (Simulation)' if dry_run else 'LIVE PILOT STAGING'}")
    
    staging_dir = Path("data/incoming/open_images_staging")
    img_staging = staging_dir / "images"
    lbl_staging = staging_dir / "labels"
    
    if not dry_run:
        img_staging.mkdir(parents=True, exist_ok=True)
        lbl_staging.mkdir(parents=True, exist_ok=True)
        
    candidates = fetch_open_images_candidates(target_count=max_images)
    
    stats = {
        "candidate_images": len(candidates),
        "accepted_images": 0,
        "rejected_images": 0,
        "rejection_reasons": Counter(),
        "accepted_boxes_by_class": Counter(),
        "accepted_images_by_class": Counter(),
        "exact_duplicates": 0,
        "near_duplicates": 0,
        "corrupt_images": 0,
        "invalid_bboxes": 0
    }
    
    existing_md5s = set()
    existing_dhashes = []
    
    # Pre-populate deduplication index from existing data splits
    for split in ["training", "validation", "test_locked"]:
        sp_img = Path(f"data/{split}/images")
        if sp_img.exists():
            for p in sp_img.glob("*.jpg"):
                try:
                    md5_val = compute_md5(p)
                    dhash_val = compute_dhash(p)
                    existing_md5s.add(md5_val)
                    if not dhash_val.startswith("error"):
                        existing_dhashes.append(dhash_val)
                except Exception:
                    pass

    staged_manifest_entries = []
    
    print("\nProcessing candidate images...")
    for idx, (img_id, boxes) in enumerate(candidates.items(), 1):
        # 1. Download image
        img_url = f"{AWS_IMAGE_BASE_URL}/{img_id}.jpg"
        temp_img_path = Path(f"scratch_temp_{img_id}.jpg") if dry_run else img_staging / f"openimages_{img_id}.jpg"
        
        try:
            req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as resp:
                data = resp.read()
            with open(temp_img_path, "wb") as f:
                f.write(data)
        except Exception as e:
            stats["rejected_images"] += 1
            stats["rejection_reasons"]["download_failed"] += 1
            continue

        # 2. Validate image integrity
        try:
            with Image.open(temp_img_path) as im:
                w, h = im.size
                im.verify()
            if w <= 0 or h <= 0:
                raise ValueError("Invalid image dimensions")
        except Exception as e:
            stats["rejected_images"] += 1
            stats["rejection_reasons"]["corrupt_image"] += 1
            stats["corrupt_images"] += 1
            if temp_img_path.exists():
                temp_img_path.unlink()
            continue

        # 3. Exact and Perceptual Deduplication
        md5_val = compute_md5(temp_img_path)
        sha256_val = compute_sha256(temp_img_path)
        dhash_val = compute_dhash(temp_img_path)

        if md5_val in existing_md5s:
            stats["rejected_images"] += 1
            stats["rejection_reasons"]["exact_duplicate"] += 1
            stats["exact_duplicates"] += 1
            if temp_img_path.exists():
                temp_img_path.unlink()
            continue

        # Check near duplicate Hamming distance threshold <= 6
        is_near_dup = False
        if not dhash_val.startswith("error"):
            for existing_dh in existing_dhashes:
                if hamming_distance(dhash_val, existing_dh) <= 6:
                    is_near_dup = True
                    break
        if is_near_dup:
            stats["rejected_images"] += 1
            stats["rejection_reasons"]["near_duplicate"] += 1
            stats["near_duplicates"] += 1
            if temp_img_path.exists():
                temp_img_path.unlink()
            continue

        # 4. Convert and validate bounding boxes
        valid_yolo_lines = []
        classes_in_image = set()
        
        for box in boxes:
            xmin, xmax, ymin, ymax = box["xmin"], box["xmax"], box["ymin"], box["ymax"]
            
            # Check geometry bounds [0, 1]
            if not (0.0 <= xmin < xmax <= 1.0 and 0.0 <= ymin < ymax <= 1.0):
                stats["invalid_bboxes"] += 1
                continue
                
            bw = xmax - xmin
            bh = ymax - ymin
            if bw <= 0 or bh <= 0:
                stats["invalid_bboxes"] += 1
                continue
                
            x_center = (xmin + xmax) / 2.0
            y_center = (ymin + ymax) / 2.0
            cid = box["safaios_class_id"]
            
            valid_yolo_lines.append(f"{cid} {x_center:.6f} {y_center:.6f} {bw:.6f} {bh:.6f}")
            classes_in_image.add(cid)
            stats["accepted_boxes_by_class"][cid] += 1

        if not valid_yolo_lines:
            stats["rejected_images"] += 1
            stats["rejection_reasons"]["no_valid_bounding_boxes"] += 1
            if temp_img_path.exists():
                temp_img_path.unlink()
            continue

        # Accept image
        stats["accepted_images"] += 1
        for cid in classes_in_image:
            stats["accepted_images_by_class"][cid] += 1
            
        existing_md5s.add(md5_val)
        if not dhash_val.startswith("error"):
            existing_dhashes.append(dhash_val)

        # Write label file if live
        lbl_path = lbl_staging / f"openimages_{img_id}.txt"
        if not dry_run:
            with open(lbl_path, "w", encoding="utf-8") as lf:
                lf.write("\n".join(valid_yolo_lines) + "\n")
        else:
            if temp_img_path.exists():
                temp_img_path.unlink()

        # Provenance entry
        entry = {
            "image_id": f"openimages_{img_id}",
            "filename": f"data/incoming/open_images_staging/images/openimages_{img_id}.jpg",
            "source_dataset": "OpenImages_V7",
            "original_source_id": img_id,
            "source_url": img_url,
            "license": "CC BY 2.0",
            "annotation_license": "CC BY 4.0",
            "sha256": sha256_val,
            "md5": md5_val,
            "perceptual_hash": dhash_val,
            "width": w,
            "height": h,
            "bbox_count": len(valid_yolo_lines),
            "class_ids": sorted(list(classes_in_image)),
            "approval_status": "APPROVED_STAGED_CANDIDATE"
        }
        staged_manifest_entries.append(entry)
        
        if idx % 50 == 0 or idx == len(candidates):
            print(f"Processed {idx}/{len(candidates)} candidates... Accepted: {stats['accepted_images']}")

    # Calculate percentages
    acc_pct = (stats["accepted_images"] / max(1, stats["candidate_images"])) * 100.0
    rej_pct = (stats["rejected_images"] / max(1, stats["candidate_images"])) * 100.0

    print(f"\n=== PILOT INGESTION RESULTS ===")
    print(f"Candidate Images Processed: {stats['candidate_images']}")
    print(f"Accepted Candidates Staged: {stats['accepted_images']} ({acc_pct:.1f}%)")
    print(f"Rejected Candidates: {stats['rejected_images']} ({rej_pct:.1f}%)")
    print(f"Rejection Reasons: {dict(stats['rejection_reasons'])}")

    print(f"\n=== PILOT CLASS DISTRIBUTION ===")
    class_names_map = {1: "plastic_wrapper_bag", 4: "metal_can"}
    for cid, cname in class_names_map.items():
        box_count = stats["accepted_boxes_by_class"][cid]
        img_count = stats["accepted_images_by_class"][cid]
        tot_boxes = sum(stats["accepted_boxes_by_class"].values())
        pct = (box_count / max(1, tot_boxes)) * 100.0
        print(f"  Class {cid} ({cname}): {img_count} images, {box_count} bboxes ({pct:.1f}% of pilot bboxes)")

    # Export Acquisition Registry
    registry = {
        "source_name": "OpenImages_V7",
        "source_version": "V7",
        "source_url": "https://storage.googleapis.com/openimages/web/index.html",
        "source_license": "CC BY 2.0",
        "annotation_license": "CC BY 4.0",
        "retrieval_date": "2026-10-08",
        "dry_run": dry_run,
        "approved_mappings": APPROVED_MAPPING,
        "rejected_mappings": REJECTED_OR_AMBIGUOUS_MAPPING,
        "candidate_count": stats["candidate_images"],
        "accepted_count": stats["accepted_images"],
        "rejection_count": stats["rejected_images"],
        "acceptance_percentage": acc_pct,
        "rejection_percentage": rej_pct,
        "rejection_reasons": dict(stats["rejection_reasons"]),
        "duplicate_count": stats["exact_duplicates"],
        "near_duplicate_count": stats["near_duplicates"],
        "class_distribution_boxes": dict(stats["accepted_boxes_by_class"]),
        "class_distribution_images": dict(stats["accepted_images_by_class"]),
        "staging_location": str(staging_dir),
        "status": "APPROVED_PILOT_STAGED"
    }

    registry_path = Path("reports/acquisition_registry.json")
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    with open(registry_path, "w", encoding="utf-8") as rf:
        json.dump(registry, rf, indent=2)

    print(f"\nAcquisition registry exported to {registry_path}")
    return stats

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SafaiOS Open Images Pilot Ingestor")
    parser.add_argument("--live", action="store_true", help="Run live pilot staging instead of dry-run")
    parser.add_argument("--max", type=int, default=300, help="Maximum candidate images to process")
    args = parser.parse_args()
    
    run_ingestion_pipeline(dry_run=not args.live, max_images=args.max)
