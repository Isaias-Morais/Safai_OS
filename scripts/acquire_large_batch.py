"""
SafaiOS Milestone 2B Controlled Large Batch Acquisition Engine
Downloads, validates, deduplicates, and stages 1,000+ candidate images
from Open Images V7 into data/incoming/large_batch_staging/ for approved classes
(/m/05gqfk -> plastic_wrapper_bag, /m/02jnhm -> metal_can).
"""
import os
import sys
import json
import urllib.request
import argparse
import shutil
from pathlib import Path
from PIL import Image
from collections import Counter
from src.data.hashing import compute_md5, compute_sha256, compute_dhash, hamming_distance

APPROVED_MAPPING = {
    "/m/05gqfk": {"name": "Plastic bag", "safaios_class_id": 1, "safaios_class_name": "plastic_wrapper_bag"},
    "/m/02jnhm": {"name": "Tin can", "safaios_class_id": 4, "safaios_class_name": "metal_can"}
}

ANNOTATIONS_URL = "https://storage.googleapis.com/openimages/v6/oidv6-train-annotations-bbox.csv"
AWS_IMAGE_BASE_URL = "https://open-images-dataset.s3.amazonaws.com/train"

def check_disk_safety(required_gb=2.0):
    total, used, free = shutil.disk_usage(".")
    free_gb = free / (1024 ** 3)
    print(f"Disk Safety Check: Free space = {free_gb:.2f} GB (Required: {required_gb} GB)")
    if free_gb < required_gb:
        raise SystemError(f"Insufficient disk space! Free: {free_gb:.2f} GB, Required: {required_gb} GB")

def acquire_batch(max_images=1000, dry_run=False):
    print("=== SafaiOS Controlled Large Batch Acquisition Pipeline ===")
    print(f"Target Max Candidates: {max_images} | Mode: {'DRY-RUN' if dry_run else 'LIVE STAGING'}")
    
    check_disk_safety(required_gb=2.0)
    
    staging_dir = Path("data/incoming/large_batch_staging")
    img_staging = staging_dir / "images"
    lbl_staging = staging_dir / "labels"
    
    if not dry_run:
        img_staging.mkdir(parents=True, exist_ok=True)
        lbl_staging.mkdir(parents=True, exist_ok=True)

    print(f"Fetching Open Images validation bounding box CSV slice...")
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
                
                # Skip candidates already in pilot staging
                if f"openimages_{img_id}.jpg" in os.listdir("data/incoming/open_images_staging/images") if os.path.exists("data/incoming/open_images_staging/images") else False:
                    continue
                
                if mid in APPROVED_MAPPING:
                    try:
                        xmin, xmax, ymin, ymax = map(float, parts[4:8])
                        box = {
                            "mid": mid,
                            "safaios_class_id": APPROVED_MAPPING[mid]["safaios_class_id"],
                            "xmin": xmin, "xmax": xmax, "ymin": ymin, "ymax": ymax
                        }
                        if img_id not in candidates_by_img:
                            candidates_by_img[img_id] = []
                        candidates_by_img[img_id].append(box)
                        found_counts[mid] += 1
                        
                        if len(candidates_by_img) >= max_images:
                            break
                    except ValueError:
                        continue

    print(f"Discovered {len(candidates_by_img)} candidate images containing {sum(found_counts.values())} approved bounding boxes.")
    
    stats = {
        "candidate_images": len(candidates_by_img),
        "accepted_images": 0,
        "rejected_images": 0,
        "rejection_reasons": Counter(),
        "accepted_boxes_by_class": Counter(),
        "accepted_images_by_class": Counter(),
        "exact_duplicates": 0,
        "near_duplicates": 0,
        "corrupt_images": 0
    }
    
    existing_md5s = set()
    existing_dhashes = []
    
    # Pre-populate index from existing dataset splits & pilot staging
    for check_dir in ["data/training/images", "data/validation/images", "data/test_locked/images", "data/incoming/open_images_staging/images"]:
        cd_path = Path(check_dir)
        if cd_path.exists():
            for p in cd_path.glob("*.jpg"):
                try:
                    existing_md5s.add(compute_md5(p))
                    dh = compute_dhash(p)
                    if not dh.startswith("error"):
                        existing_dhashes.append(dh)
                except Exception:
                    pass

    print(f"Pre-populated deduplication index with {len(existing_md5s)} MD5s and {len(existing_dhashes)} dHashes.")
    
    staged_entries = []
    
    for idx, (img_id, boxes) in enumerate(candidates_by_img.items(), 1):
        img_url = f"{AWS_IMAGE_BASE_URL}/{img_id}.jpg"
        target_img_path = Path(f"scratch_temp_batch_{img_id}.jpg") if dry_run else img_staging / f"openimages_batch_{img_id}.jpg"
        
        # Download image
        try:
            req_img = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req_img) as resp:
                data = resp.read()
            with open(target_img_path, "wb") as f:
                f.write(data)
        except Exception as e:
            stats["rejected_images"] += 1
            stats["rejection_reasons"]["download_failed"] += 1
            continue

        # Integrity check
        try:
            with Image.open(target_img_path) as im:
                w, h = im.size
                im.verify()
            if w <= 0 or h <= 0:
                raise ValueError("Invalid resolution")
        except Exception:
            stats["rejected_images"] += 1
            stats["rejection_reasons"]["corrupt_image"] += 1
            stats["corrupt_images"] += 1
            if target_img_path.exists():
                target_img_path.unlink()
            continue

        # Exact and Near Deduplication
        md5_val = compute_md5(target_img_path)
        sha256_val = compute_sha256(target_img_path)
        dhash_val = compute_dhash(target_img_path)

        if md5_val in existing_md5s:
            stats["rejected_images"] += 1
            stats["rejection_reasons"]["exact_duplicate"] += 1
            stats["exact_duplicates"] += 1
            if target_img_path.exists():
                target_img_path.unlink()
            continue

        is_near_dup = False
        if not dhash_val.startswith("error"):
            for dh in existing_dhashes:
                if hamming_distance(dhash_val, dh) <= 6:
                    is_near_dup = True
                    break
        if is_near_dup:
            stats["rejected_images"] += 1
            stats["rejection_reasons"]["near_duplicate"] += 1
            stats["near_duplicates"] += 1
            if target_img_path.exists():
                target_img_path.unlink()
            continue

        # Convert bounding boxes to YOLO format
        yolo_lines = []
        classes_in_img = set()
        for box in boxes:
            xmin, xmax, ymin, ymax = box["xmin"], box["xmax"], box["ymin"], box["ymax"]
            if 0.0 <= xmin < xmax <= 1.0 and 0.0 <= ymin < ymax <= 1.0:
                bw = xmax - xmin
                bh = ymax - ymin
                if bw > 0 and bh > 0:
                    xc = (xmin + xmax) / 2.0
                    yc = (ymin + ymax) / 2.0
                    cid = box["safaios_class_id"]
                    yolo_lines.append(f"{cid} {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}")
                    classes_in_img.add(cid)
                    stats["accepted_boxes_by_class"][cid] += 1

        if not yolo_lines:
            stats["rejected_images"] += 1
            stats["rejection_reasons"]["no_valid_boxes"] += 1
            if target_img_path.exists():
                target_img_path.unlink()
            continue

        stats["accepted_images"] += 1
        for cid in classes_in_img:
            stats["accepted_images_by_class"][cid] += 1

        existing_md5s.add(md5_val)
        if not dhash_val.startswith("error"):
            existing_dhashes.append(dhash_val)

        if not dry_run:
            lbl_path = lbl_staging / f"openimages_batch_{img_id}.txt"
            with open(lbl_path, "w", encoding="utf-8") as lf:
                lf.write("\n".join(yolo_lines) + "\n")
        else:
            if target_img_path.exists():
                target_img_path.unlink()

        staged_entries.append({
            "image_id": f"openimages_batch_{img_id}",
            "filename": f"data/incoming/large_batch_staging/images/openimages_batch_{img_id}.jpg",
            "source_dataset": "OpenImages_V7",
            "original_source_id": img_id,
            "source_url": img_url,
            "license": "CC BY 2.0",
            "annotation_license": "CC BY 4.0",
            "sha256": sha256_val,
            "md5": md5_val,
            "perceptual_hash": dhash_val,
            "width": w, "height": h,
            "bbox_count": len(yolo_lines),
            "class_ids": sorted(list(classes_in_img)),
            "approval_status": "APPROVED_STAGED_BATCH_CANDIDATE"
        })

        if idx % 50 == 0 or idx == len(candidates_by_img):
            print(f"Processed {idx}/{len(candidates_by_img)} candidates... Accepted: {stats['accepted_images']}")

    acc_pct = (stats["accepted_images"] / max(1, stats["candidate_images"])) * 100.0
    rej_pct = (stats["rejected_images"] / max(1, stats["candidate_images"])) * 100.0

    print(f"\n=== LARGE BATCH INGESTION SUMMARY ===")
    print(f"Candidate Images: {stats['candidate_images']}")
    print(f"Accepted & Staged: {stats['accepted_images']} ({acc_pct:.1f}%)")
    print(f"Rejected: {stats['rejected_images']} ({rej_pct:.1f}%)")
    print(f"Rejection Reasons: {dict(stats['rejection_reasons'])}")

    report = {
        "pipeline": "SafaiOS Large Batch Ingestor",
        "dry_run": dry_run,
        "candidate_count": stats["candidate_images"],
        "accepted_count": stats["accepted_images"],
        "rejection_count": stats["rejected_images"],
        "acceptance_percentage": acc_pct,
        "rejection_percentage": rej_pct,
        "rejection_reasons": dict(stats["rejection_reasons"]),
        "class_distribution_boxes": dict(stats["accepted_boxes_by_class"]),
        "class_distribution_images": dict(stats["accepted_images_by_class"]),
        "staging_location": str(staging_dir),
        "status": "APPROVED_BATCH_STAGED"
    }

    report_path = Path("reports/large_batch_acquisition_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as rf:
        json.dump(report, rf, indent=2)

    print(f"Report exported to {report_path}")
    return stats

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SafaiOS Large Batch Ingestion Engine")
    parser.add_argument("--live", action="store_true", help="Run live staging")
    parser.add_argument("--max", type=int, default=500, help="Max candidates to acquire")
    args = parser.parse_args()
    
    acquire_batch(max_images=args.max, dry_run=not args.live)
