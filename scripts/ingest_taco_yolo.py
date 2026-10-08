"""
TACO Dataset Multi-Threaded Ingestion, Conversion & Anti-Leakage Splitting Pipeline
Downloads images via Flickr URLs, converts COCO annotations to normalized YOLO format,
maps classes to SafaiOS 5-Class Object Taxonomy, performs sequence-aware 80/10/10 splitting,
and populates data/train, data/val, data/test.
"""
import os
import sys
import json
import shutil
import random
import urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image

TACO_ANNOTATIONS_URL = "https://raw.githubusercontent.com/pedropro/TACO/master/data/annotations.json"
RAW_DIR = Path("data/raw")
DATA_DIR = Path("data")

# 5-Class Object Taxonomy Mapping
# 0: plastic_bottle, 1: plastic_wrapper_bag, 2: paper_cardboard, 3: glass_bottle_container, 4: metal_can
SAFAIOS_TAXONOMY = {
    0: "plastic_bottle",
    1: "plastic_wrapper_bag",
    2: "paper_cardboard",
    3: "glass_bottle_container",
    4: "metal_can"
}

def map_taco_category(cat_name):
    c = cat_name.lower()
    if "bottle" in c and "glass" in c:
        return 3 # glass_bottle_container
    elif "glass" in c and "jar" in c:
        return 3 # glass_bottle_container
    elif "bottle" in c or "cap" in c:
        return 0 # plastic_bottle
    elif "can" in c or "pop tab" in c:
        return 4 # metal_can
    elif any(w in c for w in ["film", "wrapper", "bag", "sachet", "straw", "disposable plastic cup", "plastic lid"]):
        return 1 # plastic_wrapper_bag
    elif any(w in c for w in ["carton", "paper", "cardboard", "paper cup", "tissue"]):
        return 2 # paper_cardboard
    return None # Unmapped / Excluded

def download_single_image(img_info, raw_dest_path):
    if raw_dest_path.exists() and raw_dest_path.stat().st_size > 0:
        return True, raw_dest_path
    
    urls = [img_info.get("flickr_url"), img_info.get("flickr_640_url")]
    for url in urls:
        if not url:
            continue
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp, open(raw_dest_path, "wb") as f:
                f.write(resp.read())
            return True, raw_dest_path
        except Exception:
            continue
    return False, raw_dest_path

def run_ingestion():
    print("==================================================")
    print("  SafaiOS TACO Ingestion & YOLO Conversion")
    print("==================================================")
    
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    anno_path = RAW_DIR / "taco_annotations.json"
    
    if not anno_path.exists():
        print("Downloading TACO annotations JSON...")
        urllib.request.urlretrieve(TACO_ANNOTATIONS_URL, anno_path)

    with open(anno_path, "r", encoding="utf-8") as f:
        coco = json.load(f)

    images = {img["id"]: img for img in coco["images"]}
    categories = {cat["id"]: cat["name"] for cat in coco["categories"]}
    
    # Group annotations by image_id
    img_annotations = {}
    for ann in coco["annotations"]:
        img_id = ann["image_id"]
        cat_id = ann["category_id"]
        cat_name = categories.get(cat_id, "")
        mapped_cls = map_taco_category(cat_name)
        
        if mapped_cls is not None:
            if img_id not in img_annotations:
                img_annotations[img_id] = []
            img_annotations[img_id].append({
                "class_id": mapped_cls,
                "bbox": ann["bbox"] # [x, y, width, height]
            })

    print(f"Total TACO Images in Annotations: {len(images)}")
    print(f"Images with Target 5-Class BBoxes: {len(img_annotations)}")

    # Clean & create target split directories
    for split in ["train", "val", "test"]:
        sp_img = DATA_DIR / split / "images"
        sp_lbl = DATA_DIR / split / "labels"
        sp_img.mkdir(parents=True, exist_ok=True)
        sp_lbl.mkdir(parents=True, exist_ok=True)

    # Sequence-aware batch grouping to prevent leakage across frames
    batch_groups = {}
    for img_id, img_info in images.items():
        if img_id not in img_annotations:
            continue
        rel_path = img_info["file_name"]
        batch_id = rel_path.split("/")[0] if "/" in rel_path else "batch_0"
        if batch_id not in batch_groups:
            batch_groups[batch_id] = []
        batch_groups[batch_id].append(img_info)

    print(f"Grouped images into {len(batch_groups)} batch sequences for leakage-free splitting.")

    # 80 / 10 / 10 Split across batch groups
    random.seed(42)
    batch_keys = list(batch_groups.keys())
    random.shuffle(batch_keys)
    
    n_batches = len(batch_keys)
    train_cutoff = int(n_batches * 0.8)
    val_cutoff = int(n_batches * 0.9)
    
    train_batches = set(batch_keys[:train_cutoff])
    val_batches = set(batch_keys[train_cutoff:val_cutoff])
    test_batches = set(batch_keys[val_cutoff:])

    # Multi-threaded image downloads
    download_tasks = []
    with ThreadPoolExecutor(max_workers=16) as executor:
        for batch_id, img_list in batch_groups.items():
            for img_info in img_list:
                rel_path = img_info["file_name"]
                raw_dest_path = RAW_DIR / rel_path
                raw_dest_path.parent.mkdir(parents=True, exist_ok=True)
                download_tasks.append(executor.submit(download_single_image, img_info, raw_dest_path))

        print(f"Downloading {len(download_tasks)} images concurrently...")
        success_count = 0
        for future in as_completed(download_tasks):
            success, _ = future.result()
            if success:
                success_count += 1

    print(f"Successfully downloaded {success_count} / {len(download_tasks)} images.")

    # Convert annotations & copy into Train / Val / Test
    counts = {"train": 0, "val": 0, "test": 0}
    box_counts = {"train": 0, "val": 0, "test": 0}

    for batch_id, img_list in batch_groups.items():
        if batch_id in train_batches:
            split = "train"
        elif batch_id in val_batches:
            split = "val"
        else:
            split = "test"

        for img_info in img_list:
            img_id = img_info["id"]
            rel_path = img_info["file_name"]
            img_raw_path = RAW_DIR / rel_path

            if not img_raw_path.exists() or img_raw_path.stat().st_size == 0:
                continue

            try:
                with Image.open(img_raw_path) as im:
                    img_w, img_h = im.size
            except Exception:
                continue

            ext = img_raw_path.suffix.lower()
            clean_name = f"taco_{img_id:06d}{ext}"
            dest_img = DATA_DIR / split / "images" / clean_name
            dest_lbl = DATA_DIR / split / "labels" / f"taco_{img_id:06d}.txt"

            shutil.copy(img_raw_path, dest_img)

            yolo_lines = []
            for ann in img_annotations[img_id]:
                c_id = ann["class_id"]
                bx, by, bw, bh = ann["bbox"]
                
                # Convert COCO (x_min, y_min, w, h) to normalized YOLO (x_center, y_center, w, h)
                x_center = (bx + bw / 2.0) / img_w
                y_center = (by + bh / 2.0) / img_h
                norm_w = bw / img_w
                norm_h = bh / img_h
                
                x_center = max(0.0, min(1.0, x_center))
                y_center = max(0.0, min(1.0, y_center))
                norm_w = max(0.0, min(1.0, norm_w))
                norm_h = max(0.0, min(1.0, norm_h))
                
                yolo_lines.append(f"{c_id} {x_center:.6f} {y_center:.6f} {norm_w:.6f} {norm_h:.6f}")
                box_counts[split] += 1

            with open(dest_lbl, "w") as lf:
                lf.write("\n".join(yolo_lines) + "\n")
                
            counts[split] += 1

    print("\n==================================================")
    print("  INGESTION & CONVERSION COMPLETED")
    print("==================================================")
    print(f"TRAIN Split: {counts['train']} images, {box_counts['train']} bboxes")
    print(f"VAL Split:   {counts['val']} images, {box_counts['val']} bboxes")
    print(f"TEST Split:  {counts['test']} images, {box_counts['test']} bboxes")
    print(f"TOTAL:       {sum(counts.values())} images, {sum(box_counts.values())} bboxes")

if __name__ == "__main__":
    run_ingestion()
