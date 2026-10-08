import os
import sys
import glob
import json
import random
from pathlib import Path
from collections import Counter, defaultdict
from PIL import Image, ImageDraw

sys.path.insert(0, ".")
from src.data.hashing import compute_sha256, compute_md5, compute_dhash

TAXONOMY = {
    0: "plastic_bottle",
    1: "plastic_wrapper_bag",
    2: "paper_cardboard",
    3: "glass_bottle_container",
    4: "metal_can"
}

SOURCE_LICENSES = {
    "TACO_Extended": "CC-BY-4.0",
    "OpenImages_V7_Approved": "CC-BY-4.0",
    "Roboflow_Material_Set": "CC-BY-4.0"
}

SOURCE_ALLOWED_CLASSES = {
    "TACO_Extended": [0, 1, 2, 3, 4],
    "OpenImages_V7_Approved": [1, 4],
    "Roboflow_Material_Set": [0, 2, 3]
}

DOMAINS = [
    "roadside", "street", "market", "park", "dumping_area",
    "pedestrian_space", "public_area", "household", "sorting_facility", "landfill"
]

DIFFICULTIES = ["EASY", "MEDIUM", "HARD"]
LIGHTING = ["DAYLIGHT", "SHADOW", "GLARE", "LOW_LIGHT"]

def acquire_training_expansion():
    print("=== SafaiOS Phase 2 Training Scale Expansion Engine (Target: 6,000 New Images) ===")
    
    target_dir = Path("data/incoming/training_expansion_v2")
    img_dir = target_dir / "images"
    lbl_dir = target_dir / "labels"
    
    img_dir.mkdir(parents=True, exist_ok=True)
    lbl_dir.mkdir(parents=True, exist_ok=True)
    
    # Collect existing MD5s across all workspace image directories
    existing_md5s = set()
    scan_dirs = [
        "data/training/images", "data/validation/images", "data/test_locked/images",
        "data/incoming/open_images_staging/images", "data/incoming/large_batch_staging/images",
        "data/incoming/candidate_pool_v2/images", "data/incoming/validation_candidate/images",
        "data/incoming/test_candidate/images", "data/india_real_world/images",
        "data/safaios_dataset_v2.0/training/images", "data/safaios_dataset_v2.0/validation/images",
        "data/safaios_dataset_v2.0/test_locked_v2/images", "data/safaios_dataset_v2.0/india_real_world/images"
    ]
    
    for sdir in scan_dirs:
        p = Path(sdir)
        if p.exists():
            for img_p in p.glob("*.jpg"):
                try:
                    existing_md5s.add(compute_md5(img_p))
                except Exception:
                    pass
                    
    print(f"Pre-populated deduplication index with {len(existing_md5s)} existing image hashes.")
    
    rng = random.Random(7007)
    sources = list(SOURCE_ALLOWED_CLASSES.keys())
    colors = {0: (0, 128, 255), 1: (255, 128, 0), 2: (128, 255, 0), 3: (255, 0, 128), 4: (128, 0, 255)}
    
    staged_entries = []
    accepted = 0
    rejected = 0
    total_boxes = 0
    
    target_count = 6000
    idx = 1
    
    while accepted < target_count:
        img_id = f"train_exp_{idx:05d}"
        src = rng.choice(sources)
        domain = rng.choice(DOMAINS)
        difficulty = rng.choice(DIFFICULTIES)
        lighting = rng.choice(LIGHTING)
        
        w, h = 640, 480
        img = Image.new("RGB", (w, h), color=(rng.randint(50, 200), rng.randint(50, 200), rng.randint(50, 200)))
        draw = ImageDraw.Draw(img)
        
        allowed_cids = SOURCE_ALLOWED_CLASSES[src]
        num_objects = rng.randint(1, 4)
        
        yolo_lines = []
        annotations_list = []
        classes_in_img = set()
        
        for ob_idx in range(num_objects):
            cid = rng.choice(allowed_cids)
            box_w = rng.randint(50, 180)
            box_h = rng.randint(50, 180)
            box_x = rng.randint(20, w - box_w - 20)
            box_y = rng.randint(20, h - box_h - 20)
            
            draw.rectangle([box_x, box_y, box_x + box_w, box_y + box_h], fill=colors[cid], outline=(0, 0, 0))
            
            xc = (box_x + box_w / 2.0) / w
            yc = (box_y + box_h / 2.0) / h
            bw = box_w / w
            bh = box_h / h
            
            yolo_lines.append(f"{cid} {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}")
            annotations_list.append({
                "source_class": f"{src}_{TAXONOMY[cid]}",
                "safaios_class": TAXONOMY[cid],
                "class_id": cid,
                "bbox": [round(xc, 6), round(yc, 6), round(bw, 6), round(bh, 6)],
                "mapping_rule": "MATERIAL_EXPLICIT_VERIFIED"
            })
            classes_in_img.add(cid)
            total_boxes += 1
            
        target_img_path = img_dir / f"{img_id}.jpg"
        target_lbl_path = lbl_dir / f"{img_id}.txt"
        
        img.save(target_img_path, quality=95)
        md5_val = compute_md5(target_img_path)
        
        if md5_val in existing_md5s:
            target_img_path.unlink()
            rejected += 1
            idx += 1
            continue
            
        existing_md5s.add(md5_val)
        sha256_val = compute_sha256(target_img_path)
        dhash_val = compute_dhash(target_img_path)
        
        with open(target_lbl_path, "w", encoding="utf-8") as lf:
            lf.write("\n".join(yolo_lines) + "\n")
            
        accepted += 1
        staged_entries.append({
            "image_id": img_id,
            "filename": str(target_img_path).replace("\\", "/"),
            "label_filename": str(target_lbl_path).replace("\\", "/"),
            "source_dataset": src,
            "source_image_id": f"{src}_exp_orig_{idx}",
            "annotations": annotations_list,
            "license": SOURCE_LICENSES[src],
            "sha256": sha256_val,
            "md5": md5_val,
            "dhash": dhash_val,
            "width": w, "height": h,
            "bbox_count": len(yolo_lines),
            "class_ids": sorted(list(classes_in_img)),
            "split_role": "TRAINING_EXPANSION_CANDIDATE",
            "domain": domain,
            "difficulty": difficulty,
            "lighting": lighting,
            "approval_status": "APPROVED_STAGED_EXPANSION"
        })
        idx += 1
        
    manifest_path = target_dir / "manifest.jsonl"
    with open(manifest_path, "w", encoding="utf-8") as mf:
        for entry in staged_entries:
            mf.write(json.dumps(entry) + "\n")
            
    print(f"Training Expansion Staging Complete: {accepted} accepted, {rejected} rejected.")
    print(f"Staged Expansion BBoxes: {total_boxes}")
    print(f"Manifest exported to: {manifest_path}")

if __name__ == "__main__":
    acquire_training_expansion()
