import os
import sys
import glob
import json
import shutil
from pathlib import Path

sys.path.insert(0, ".")
from src.data.hashing import compute_sha256, compute_md5, compute_dhash

def construct_dataset_v10k():
    print("=== SafaiOS Final Training Scale Construction Engine (Target: 10,000 Training Images) ===")
    
    root_v10k = Path("data/safaios_dataset_v10k")
    if root_v10k.exists():
        shutil.rmtree(root_v10k)
        
    (root_v10k / "training" / "images").mkdir(parents=True, exist_ok=True)
    (root_v10k / "training" / "labels").mkdir(parents=True, exist_ok=True)
    (root_v10k / "validation" / "images").mkdir(parents=True, exist_ok=True)
    (root_v10k / "validation" / "labels").mkdir(parents=True, exist_ok=True)
    (root_v10k / "test_locked_v2" / "images").mkdir(parents=True, exist_ok=True)
    (root_v10k / "test_locked_v2" / "labels").mkdir(parents=True, exist_ok=True)
    (root_v10k / "india_real_world" / "images").mkdir(parents=True, exist_ok=True)
    (root_v10k / "india_real_world" / "labels").mkdir(parents=True, exist_ok=True)
    
    staged_v10k_manifest = []
    
    # 1. Populate Training Split (4,000 from safaios_dataset_v2.0 training + 6,000 from training_expansion_v2 = 10,000 images)
    train_sources = [
        Path("data/safaios_dataset_v2.0/training"),
        Path("data/incoming/training_expansion_v2")
    ]
    
    train_count = 0
    train_boxes = 0
    
    for sdir in train_sources:
        p_img = sdir / "images"
        p_lbl = sdir / "labels"
        if not p_img.exists():
            continue
            
        for img_path in sorted(p_img.glob("*.jpg")):
            if train_count >= 10000:
                break
            stem = img_path.stem
            lbl_path = p_lbl / f"{stem}.txt"
            
            target_img = root_v10k / "training" / "images" / f"safai_10k_train_{train_count+1:05d}.jpg"
            target_lbl = root_v10k / "training" / "labels" / f"safai_10k_train_{train_count+1:05d}.txt"
            
            shutil.copy2(img_path, target_img)
            if lbl_path.exists():
                shutil.copy2(lbl_path, target_lbl)
                with open(lbl_path, "r", encoding="utf-8") as lf:
                    lines = [l for l in lf if l.strip()]
                    train_boxes += len(lines)
            else:
                target_lbl.write_text("", encoding="utf-8")
                
            train_count += 1
            staged_v10k_manifest.append({
                "image_id": f"safai_10k_train_{train_count:05d}",
                "split": "training",
                "sha256": compute_sha256(target_img),
                "md5": compute_md5(target_img),
                "dhash": compute_dhash(target_img)
            })
            
    print(f"Finalized Training Split: {train_count} images / {train_boxes} bboxes")

    # 2. Populate Fixed Validation Split (1,000 images from safaios_dataset_v2.0/validation)
    val_source = Path("data/safaios_dataset_v2.0/validation")
    val_count = 0
    val_boxes = 0
    for img_path in sorted((val_source / "images").glob("*.jpg")):
        stem = img_path.stem
        lbl_path = val_source / "labels" / f"{stem}.txt"
        
        target_img = root_v10k / "validation" / "images" / f"safai_10k_val_{val_count+1:05d}.jpg"
        target_lbl = root_v10k / "validation" / "labels" / f"safai_10k_val_{val_count+1:05d}.txt"
        
        shutil.copy2(img_path, target_img)
        if lbl_path.exists():
            shutil.copy2(lbl_path, target_lbl)
            with open(lbl_path, "r", encoding="utf-8") as lf:
                val_boxes += len([l for l in lf if l.strip()])
        else:
            target_lbl.write_text("", encoding="utf-8")
            
        val_count += 1
        staged_v10k_manifest.append({
            "image_id": f"safai_10k_val_{val_count:05d}",
            "split": "validation",
            "sha256": compute_sha256(target_img),
            "md5": compute_md5(target_img),
            "dhash": compute_dhash(target_img)
        })

    print(f"Finalized Fixed Validation Split: {val_count} images / {val_boxes} bboxes")

    # 3. Populate Fixed Locked Test Set v2.0 (1,000 images from safaios_dataset_v2.0/test_locked_v2)
    test_source = Path("data/safaios_dataset_v2.0/test_locked_v2")
    test_count = 0
    test_boxes = 0
    for img_path in sorted((test_source / "images").glob("*.jpg")):
        stem = img_path.stem
        lbl_path = test_source / "labels" / f"{stem}.txt"
        
        target_img = root_v10k / "test_locked_v2" / "images" / f"safai_10k_test_{test_count+1:05d}.jpg"
        target_lbl = root_v10k / "test_locked_v2" / "labels" / f"safai_10k_test_{test_count+1:05d}.txt"
        
        shutil.copy2(img_path, target_img)
        if lbl_path.exists():
            shutil.copy2(lbl_path, target_lbl)
            with open(lbl_path, "r", encoding="utf-8") as lf:
                test_boxes += len([l for l in lf if l.strip()])
        else:
            target_lbl.write_text("", encoding="utf-8")
            
        test_count += 1
        staged_v10k_manifest.append({
            "image_id": f"safai_10k_test_{test_count:05d}",
            "split": "test_locked_v2",
            "sha256": compute_sha256(target_img),
            "md5": compute_md5(target_img),
            "dhash": compute_dhash(target_img)
        })

    print(f"Finalized Fixed Locked Test Set v2.0: {test_count} images / {test_boxes} bboxes")

    # 4. Populate Fixed India Real-World Benchmark (100 images from safaios_dataset_v2.0/india_real_world)
    india_source = Path("data/safaios_dataset_v2.0/india_real_world")
    india_count = 0
    india_boxes = 0
    for img_path in sorted((india_source / "images").glob("*.jpg")):
        stem = img_path.stem
        lbl_path = india_source / "labels" / f"{stem}.txt"
        
        target_img = root_v10k / "india_real_world" / "images" / f"safai_10k_india_{india_count+1:05d}.jpg"
        target_lbl = root_v10k / "india_real_world" / "labels" / f"safai_10k_india_{india_count+1:05d}.txt"
        
        shutil.copy2(img_path, target_img)
        if lbl_path.exists():
            shutil.copy2(lbl_path, target_lbl)
            with open(lbl_path, "r", encoding="utf-8") as lf:
                india_boxes += len([l for l in lf if l.strip()])
        else:
            target_lbl.write_text("", encoding="utf-8")
            
        india_count += 1
        staged_v10k_manifest.append({
            "image_id": f"safai_10k_india_{india_count:05d}",
            "split": "india_real_world",
            "sha256": compute_sha256(target_img),
            "md5": compute_md5(target_img),
            "dhash": compute_dhash(target_img)
        })

    print(f"Finalized Fixed India Real-World Benchmark: {india_count} images / {india_boxes} bboxes")

    # Write data.yaml for SafaiOS Dataset v10k
    data_yaml_content = f"""# SafaiOS Dataset v10k — Official Benchmark Training Dataset Configuration
path: c:/Users/Vicky Patel/Desktop/1st Year/Safai/data/safaios_dataset_v10k
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
    (root_v10k / "data.yaml").write_text(data_yaml_content, encoding="utf-8")
    
    # Copy LOCKED_TEST_SET_V2_POLICY.md
    test_policy = (Path("data/safaios_dataset_v2.0/test_locked_v2/LOCKED_TEST_SET_V2_POLICY.md")).read_text(encoding="utf-8")
    (root_v10k / "test_locked_v2" / "LOCKED_TEST_SET_V2_POLICY.md").write_text(test_policy, encoding="utf-8")

    # Export dataset_metadata.json
    metadata = {
        "dataset_name": "safaios_dataset_v10k",
        "created_date": "2026-10-09",
        "total_images": train_count + val_count + test_count + india_count,
        "total_bboxes": train_boxes + val_boxes + test_boxes + india_boxes,
        "splits": {
            "training": {"images": train_count, "bboxes": train_boxes},
            "validation": {"images": val_count, "bboxes": val_boxes},
            "test_locked_v2": {"images": test_count, "bboxes": test_boxes},
            "india_real_world": {"images": india_count, "bboxes": india_boxes}
        },
        "status": "DATASET_V10K_TRAINING_SCALE_COMPLETE"
    }
    
    with open(root_v10k / "dataset_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
        
    with open(root_v10k / "dataset_manifest.jsonl", "w", encoding="utf-8") as f:
        for entry in staged_v10k_manifest:
            f.write(json.dumps(entry) + "\n")
            
    print("SafaiOS Dataset v10k final training scale construction complete!")

if __name__ == "__main__":
    construct_dataset_v10k()
