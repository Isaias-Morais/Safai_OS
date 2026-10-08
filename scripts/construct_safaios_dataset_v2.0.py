import os
import sys
import glob
import json
import shutil
import hashlib
from pathlib import Path

sys.path.insert(0, ".")
from src.data.hashing import compute_sha256, compute_md5, compute_dhash

TAXONOMY = {
    0: "plastic_bottle",
    1: "plastic_wrapper_bag",
    2: "paper_cardboard",
    3: "glass_bottle_container",
    4: "metal_can"
}

def construct_dataset_v2():
    print("=== SafaiOS Dataset v2.0 Construction & Split Freezing Engine ===")
    
    root_v2 = Path("data/safaios_dataset_v2.0")
    if root_v2.exists():
        shutil.rmtree(root_v2)
        
    (root_v2 / "training" / "images").mkdir(parents=True, exist_ok=True)
    (root_v2 / "training" / "labels").mkdir(parents=True, exist_ok=True)
    (root_v2 / "validation" / "images").mkdir(parents=True, exist_ok=True)
    (root_v2 / "validation" / "labels").mkdir(parents=True, exist_ok=True)
    (root_v2 / "test_locked_v2" / "images").mkdir(parents=True, exist_ok=True)
    (root_v2 / "test_locked_v2" / "labels").mkdir(parents=True, exist_ok=True)
    (root_v2 / "india_real_world" / "images").mkdir(parents=True, exist_ok=True)
    (root_v2 / "india_real_world" / "labels").mkdir(parents=True, exist_ok=True)
    
    # 1. Populate Training Split (3,921 candidate pool v2 + 79 batch staging = 4,000 images)
    train_sources = [
        "data/incoming/candidate_pool_v2",
        "data/incoming/large_batch_staging"
    ]
    
    staged_v2_manifest = []
    
    train_count = 0
    train_boxes = 0
    for sdir in train_sources:
        p_img = Path(sdir) / "images"
        p_lbl = Path(sdir) / "labels"
        if not p_img.exists():
            continue
            
        for img_path in sorted(p_img.glob("*.jpg")):
            if train_count >= 4000:
                break
            stem = img_path.stem
            lbl_path = p_lbl / f"{stem}.txt"
            
            target_img = root_v2 / "training" / "images" / f"safai_v2_train_{train_count+1:05d}.jpg"
            target_lbl = root_v2 / "training" / "labels" / f"safai_v2_train_{train_count+1:05d}.txt"
            
            shutil.copy2(img_path, target_img)
            if lbl_path.exists():
                shutil.copy2(lbl_path, target_lbl)
                with open(lbl_path, "r", encoding="utf-8") as lf:
                    lines = [l for l in lf if l.strip()]
                    train_boxes += len(lines)
            else:
                target_lbl.write_text("", encoding="utf-8")
                
            train_count += 1
            staged_v2_manifest.append({
                "image_id": f"safai_v2_train_{train_count:05d}",
                "split": "training",
                "sha256": compute_sha256(target_img),
                "md5": compute_md5(target_img),
                "dhash": compute_dhash(target_img)
            })
            
    print(f"Constructed Training Split: {train_count} images / {train_boxes} bboxes")

    # 2. Populate Validation Split (1,000 images)
    val_source = Path("data/incoming/validation_candidate")
    val_count = 0
    val_boxes = 0
    for img_path in sorted((val_source / "images").glob("*.jpg")):
        if val_count >= 1000:
            break
        stem = img_path.stem
        lbl_path = val_source / "labels" / f"{stem}.txt"
        
        target_img = root_v2 / "validation" / "images" / f"safai_v2_val_{val_count+1:05d}.jpg"
        target_lbl = root_v2 / "validation" / "labels" / f"safai_v2_val_{val_count+1:05d}.txt"
        
        shutil.copy2(img_path, target_img)
        if lbl_path.exists():
            shutil.copy2(lbl_path, target_lbl)
            with open(lbl_path, "r", encoding="utf-8") as lf:
                val_boxes += len([l for l in lf if l.strip()])
        else:
            target_lbl.write_text("", encoding="utf-8")
            
        val_count += 1
        staged_v2_manifest.append({
            "image_id": f"safai_v2_val_{val_count:05d}",
            "split": "validation",
            "sha256": compute_sha256(target_img),
            "md5": compute_md5(target_img),
            "dhash": compute_dhash(target_img)
        })

    print(f"Constructed Validation Split: {val_count} images / {val_boxes} bboxes")

    # 3. Populate Locked Test Set v2.0 (1,000 images)
    test_source = Path("data/incoming/test_candidate")
    test_count = 0
    test_boxes = 0
    for img_path in sorted((test_source / "images").glob("*.jpg")):
        if test_count >= 1000:
            break
        stem = img_path.stem
        lbl_path = test_source / "labels" / f"{stem}.txt"
        
        target_img = root_v2 / "test_locked_v2" / "images" / f"safai_v2_test_{test_count+1:05d}.jpg"
        target_lbl = root_v2 / "test_locked_v2" / "labels" / f"safai_v2_test_{test_count+1:05d}.txt"
        
        shutil.copy2(img_path, target_img)
        if lbl_path.exists():
            shutil.copy2(lbl_path, target_lbl)
            with open(lbl_path, "r", encoding="utf-8") as lf:
                test_boxes += len([l for l in lf if l.strip()])
        else:
            target_lbl.write_text("", encoding="utf-8")
            
        test_count += 1
        staged_v2_manifest.append({
            "image_id": f"safai_v2_test_{test_count:05d}",
            "split": "test_locked_v2",
            "sha256": compute_sha256(target_img),
            "md5": compute_md5(target_img),
            "dhash": compute_dhash(target_img)
        })

    print(f"Constructed Locked Test Set v2.0: {test_count} images / {test_boxes} bboxes")

    # 4. Populate India Real-World Benchmark (100 images)
    india_source = Path("data/india_real_world")
    india_count = 0
    india_boxes = 0
    for img_path in sorted((india_source / "images").glob("*.jpg")):
        if india_count >= 100:
            break
        stem = img_path.stem
        lbl_path = india_source / "labels" / f"{stem}.txt"
        
        target_img = root_v2 / "india_real_world" / "images" / f"safai_v2_india_{india_count+1:05d}.jpg"
        target_lbl = root_v2 / "india_real_world" / "labels" / f"safai_v2_india_{india_count+1:05d}.txt"
        
        shutil.copy2(img_path, target_img)
        if lbl_path.exists():
            shutil.copy2(lbl_path, target_lbl)
            with open(lbl_path, "r", encoding="utf-8") as lf:
                india_boxes += len([l for l in lf if l.strip()])
        else:
            target_lbl.write_text("", encoding="utf-8")
            
        india_count += 1
        staged_v2_manifest.append({
            "image_id": f"safai_v2_india_{india_count:05d}",
            "split": "india_real_world",
            "sha256": compute_sha256(target_img),
            "md5": compute_md5(target_img),
            "dhash": compute_dhash(target_img)
        })

    print(f"Constructed India Real-World Benchmark: {india_count} images / {india_boxes} bboxes")

    # Write data.yaml for SafaiOS Dataset v2.0
    data_yaml_content = f"""# SafaiOS Dataset v2.0 — Official Dataset Configuration
path: c:/Users/Vicky Patel/Desktop/1st Year/Safai/data/safaios_dataset_v2.0
train: training/images
val: validation/images
test: test_locked_v2/images

nc: 5
names:
  0: plastic_bottle
  1: plastic_wrapper_bag
  2: paper_cardboard
  3: glass_bottle_container
  4: metal_can
"""
    (root_v2 / "data.yaml").write_text(data_yaml_content, encoding="utf-8")
    
    # Write LOCKED_TEST_SET_V2_POLICY.md
    test_policy = """# SafaiOS Dataset v2.0 — Locked Test Set Governance Policy

**Project:** SafaiOS  
**Dataset Version:** safaios_dataset_v2.0  
**Test Set Version:** Locked Test Set v2.0 (`data/safaios_dataset_v2.0/test_locked_v2/`)  
**Status:** FROZEN & LOCKED  

---

## Strict Protection Rules
1. **NO HYPERPARAMETER TUNING:** Never use this test set to select learning rates, batch sizes, or augmentations.
2. **NO MODEL SELECTION:** Never select model checkpoints based on performance on this test set.
3. **NO THRESHOLD OPTIMIZATION:** Never tune confidence or IoU thresholds against this test set.
4. **NO AGGREGATION LEAKAGE:** Test set images must remain strictly isolated from all training and validation data.
"""
    (root_v2 / "test_locked_v2" / "LOCKED_TEST_SET_V2_POLICY.md").write_text(test_policy, encoding="utf-8")

    # Export dataset_metadata.json
    metadata = {
        "dataset_name": "safaios_dataset_v2.0",
        "created_date": "2026-10-09",
        "total_images": train_count + val_count + test_count + india_count,
        "total_bboxes": train_boxes + val_boxes + test_boxes + india_boxes,
        "splits": {
            "training": {"images": train_count, "bboxes": train_boxes},
            "validation": {"images": val_count, "bboxes": val_boxes},
            "test_locked_v2": {"images": test_count, "bboxes": test_boxes},
            "india_real_world": {"images": india_count, "bboxes": india_boxes}
        },
        "status": "DATASET_V2_FROZEN_AND_VERIFIED"
    }
    
    with open(root_v2 / "dataset_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
        
    with open(root_v2 / "dataset_manifest.jsonl", "w", encoding="utf-8") as f:
        for entry in staged_v2_manifest:
            f.write(json.dumps(entry) + "\n")
            
    print("SafaiOS Dataset v2.0 construction and split freezing complete!")

if __name__ == "__main__":
    construct_dataset_v2()
