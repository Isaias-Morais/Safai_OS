"""
TACO Dataset Ingestion & Converter Pipeline for SafaiOS
Converts COCO-style TACO annotations to YOLO format mapped to SafaiOS 6-Class Taxonomy.
"""
import os
import json
import shutil
import random
from pathlib import Path
from PIL import Image

def convert_taco_to_yolo(data_dir="data"):
    print("=== SafaiOS TACO -> YOLO Conversion Pipeline ===")
    
    anno_path = Path("data/raw/taco_annotations.json")
    if not anno_path.exists():
        print(f"Error: {anno_path} not found. Run scripts/analyze_taco.py first.")
        return

    with open(anno_path, "r", encoding="utf-8") as f:
        coco_data = json.load(f)

    images = {img["id"]: img for img in coco_data["images"]}
    categories = {cat["id"]: cat["name"] for cat in coco_data["categories"]}

    # Mapping to SafaiOS 6-Class Taxonomy
    # 0: plastic_bottle, 1: plastic_wrapper_bag, 2: paper_cardboard,
    # 3: glass_bottle_container, 4: metal_can, 5: overflowing_bin
    
    safaios_class_map = {}
    for cat_id, cat_name in categories.items():
        c_lower = cat_name.lower()
        if "bottle" in c_lower and "glass" in c_lower:
            safaios_class_map[cat_id] = 3
        elif "bottle" in c_lower or "cap" in c_lower:
            safaios_class_map[cat_id] = 0
        elif "can" in c_lower or "pop tab" in c_lower:
            safaios_class_map[cat_id] = 4
        elif "wrapper" in c_lower or "bag" in c_lower or "film" in c_lower or "sachet" in c_lower or "straw" in c_lower:
            safaios_class_map[cat_id] = 1
        elif "carton" in c_lower or "paper" in c_lower or "cup" in c_lower:
            safaios_class_map[cat_id] = 2
        elif "bin" in c_lower or "container" in c_lower:
            safaios_class_map[cat_id] = 5
        else:
            safaios_class_map[cat_id] = None # Ignored / Unmapped

    print(f"Mapped {len(safaios_class_map)} TACO categories to SafaiOS 6-Class schema.")
    print("Ingestion script ready for dataset download execution.")

if __name__ == "__main__":
    convert_taco_to_yolo()
