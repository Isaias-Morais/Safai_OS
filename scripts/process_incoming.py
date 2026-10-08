"""
SafaiOS Incoming Data Processing & Ingestion Pipeline
Processes raw incoming images and annotations placed in data/incoming/,
validates image integrity, checks MD5 deduplication against existing splits,
validates bounding box bounds, maps taxonomy, and writes a detailed ingestion report.
"""
import os
import sys
import json
import glob
import shutil
import hashlib
from pathlib import Path
from PIL import Image

INCOMING_DIR = Path("data/incoming")
TRAIN_DIR = Path("data/training")
VAL_DIR = Path("data/validation")
TEST_LOCKED_DIR = Path("data/test_locked")
REPORT_PATH = Path("reports/incoming_ingestion_report.json")

# SafaiOS 5-Class Object Taxonomy
TAXONOMY = {
    0: "plastic_bottle",
    1: "plastic_wrapper_bag",
    2: "paper_cardboard",
    3: "glass_bottle_container",
    4: "metal_can"
}

def get_existing_hashes():
    hashes = set()
    for sp in [TRAIN_DIR, VAL_DIR, TEST_LOCKED_DIR]:
        img_dir = sp / "images"
        if not img_dir.exists():
            continue
        for img_p in list(img_dir.glob("*.jpg")) + list(img_dir.glob("*.png")):
            try:
                with open(img_p, "rb") as f:
                    hashes.add(hashlib.md5(f.read()).hexdigest())
            except Exception:
                continue
    return hashes

def process_incoming():
    print("==================================================")
    print("  SafaiOS Incoming Dataset Processing Pipeline")
    print("==================================================")
    
    if not INCOMING_DIR.exists():
        print(f"Directory {INCOMING_DIR} does not exist.")
        return

    incoming_images = list(INCOMING_DIR.rglob("*.jpg")) + list(INCOMING_DIR.rglob("*.png")) + list(INCOMING_DIR.rglob("*.jpeg"))
    print(f"Discovered {len(incoming_images)} raw images in {INCOMING_DIR}.")

    existing_hashes = get_existing_hashes()
    print(f"Indexed {len(existing_hashes)} existing image hashes across splits for deduplication.")

    accepted = []
    rejected = []

    for img_p in incoming_images:
        rel_name = img_p.name
        # 1. Integrity check
        try:
            with Image.open(img_p) as img:
                img.verify()
            with Image.open(img_p) as img:
                w, h = img.size
        except Exception as e:
            rejected.append({"file": str(img_p), "reason": f"Corrupt image file: {e}"})
            continue

        # 2. Hash Deduplication
        try:
            with open(img_p, "rb") as f:
                img_hash = hashlib.md5(f.read()).hexdigest()
            if img_hash in existing_hashes:
                rejected.append({"file": str(img_p), "reason": "Duplicate image hash already exists in dataset"})
                continue
        except Exception as e:
            rejected.append({"file": str(img_p), "reason": f"Hash computation failed: {e}"})
            continue

        # 3. Label file check
        lbl_p = img_p.with_suffix(".txt")
        if not lbl_p.exists():
            rejected.append({"file": str(img_p), "reason": "Missing corresponding YOLO .txt label file"})
            continue

        # 4. Label contents validation
        valid_boxes = 0
        invalid_box = False
        with open(lbl_p, "r") as lf:
            lines = lf.readlines()
            for l_idx, line in enumerate(lines):
                parts = line.strip().split()
                if len(parts) != 5:
                    invalid_box = True
                    rejected.append({"file": str(img_p), "reason": f"Invalid label format on line {l_idx}: {line}"})
                    break
                
                c_id, xc, yc, bw, bh = int(parts[0]), float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
                if c_id not in TAXONOMY:
                    invalid_box = True
                    rejected.append({"file": str(img_p), "reason": f"Class ID {c_id} not in SafaiOS 5-Class taxonomy"})
                    break
                    
                if not (0.0 <= xc <= 1.0 and 0.0 <= yc <= 1.0 and 0.0 < bw <= 1.0 and 0.0 < bh <= 1.0):
                    invalid_box = True
                    rejected.append({"file": str(img_p), "reason": f"Bounding box out of bounds [0,1] on line {l_idx}"})
                    break
                valid_boxes += 1

        if invalid_box:
            continue

        if valid_boxes == 0:
            rejected.append({"file": str(img_p), "reason": "Zero valid bounding boxes in label file"})
            continue

        accepted.append({"file": str(img_p), "hash": img_hash, "boxes": valid_boxes})
        existing_hashes.add(img_hash)

    summary = {
        "discovered_images": len(incoming_images),
        "accepted_count": len(accepted),
        "rejected_count": len(rejected),
        "accepted": accepted,
        "rejected": rejected
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as rf:
        json.dump(summary, rf, indent=2)

    print("\n--- Ingestion Pipeline Audit Summary ---")
    print(f"Total Discovered: {len(incoming_images)}")
    print(f"Accepted:         {len(accepted)}")
    print(f"Rejected:         {len(rejected)}")
    print(f"Ingestion log saved to: {REPORT_PATH}")

if __name__ == "__main__":
    process_incoming()
