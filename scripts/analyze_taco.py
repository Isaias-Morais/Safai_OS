"""
TACO Dataset Inspector & Taxonomy Mapping Audit
Fetches official TACO annotations schema and computes class distributions,
bounding box size statistics, and maps TACO categories to SafaiOS Taxonomy.
"""
import os
import json
import urllib.request
from pathlib import Path

TACO_ANNOTATIONS_URL = "https://raw.githubusercontent.com/pedropro/TACO/master/data/annotations.json"
LOCAL_ANNOTATIONS_PATH = Path("data/raw/taco_annotations.json")

def download_taco_meta():
    LOCAL_ANNOTATIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not LOCAL_ANNOTATIONS_PATH.exists():
        print(f"Downloading TACO metadata from {TACO_ANNOTATIONS_URL}...")
        urllib.request.urlretrieve(TACO_ANNOTATIONS_URL, LOCAL_ANNOTATIONS_PATH)
        print("Download complete.")
    else:
        print("TACO metadata already downloaded.")

def analyze_taco():
    download_taco_meta()
    with open(LOCAL_ANNOTATIONS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    images = data["images"]
    annotations = data["annotations"]
    categories = {cat["id"]: cat["name"] for cat in data["categories"]}
    super_categories = {cat["id"]: cat["supercategory"] for cat in data["categories"]}

    print(f"Total Images in TACO: {len(images)}")
    print(f"Total Annotations in TACO: {len(annotations)}")
    print(f"Total Fine-Grained Categories: {len(categories)}")

    cat_counts = {}
    bbox_areas = []
    
    for ann in annotations:
        cat_id = ann["category_id"]
        cat_name = categories.get(cat_id, "Unknown")
        cat_counts[cat_name] = cat_counts.get(cat_name, 0) + 1
        
        bbox = ann["bbox"] # [x, y, width, height]
        bbox_areas.append(bbox[2] * bbox[3])

    print("\n--- TACO Fine-Grained Class Counts (Top 20) ---")
    sorted_cats = sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)
    for cat, count in sorted_cats[:20]:
        print(f"  {cat}: {count}")

    # Map to proposed SafaiOS Taxonomy
    taxonomy_mapping = {
        "Clear plastic bottle": "plastic_bottle",
        "Other plastic bottle": "plastic_bottle",
        "Plastic bottle cap": "plastic_bottle",
        "Drink can": "metal_can",
        "Other can": "metal_can",
        "Plastic film": "plastic_wrapper_bag",
        "Plastic bag & wrapper": "plastic_wrapper_bag",
        "Corrugated carton": "paper_cardboard",
        "Paper": "paper_cardboard",
        "Glass bottle": "glass_bottle_container",
        "Glass jar": "glass_bottle_container",
        "Food waste": "organic_food_waste",
        "Cigarette": "sanitary_medical_waste",
        "Unlabeled litter": "mixed_waste"
    }

    safaios_counts = {}
    for cat_id, cat_name in categories.items():
        count = cat_counts.get(cat_name, 0)
        super_cat = super_categories.get(cat_id, "")
        
        # Simple rule-based mapping heuristic for audit
        mapped = "mixed_waste"
        if "bottle" in cat_name.lower() and "plastic" in cat_name.lower():
            mapped = "plastic_bottle"
        elif "bottle" in cat_name.lower() and "glass" in cat_name.lower():
            mapped = "glass_bottle_container"
        elif "can" in cat_name.lower():
            mapped = "metal_can"
        elif "wrapper" in cat_name.lower() or "bag" in cat_name.lower() or "film" in cat_name.lower() or "sachet" in cat_name.lower():
            mapped = "plastic_wrapper_bag"
        elif "carton" in cat_name.lower() or "paper" in cat_name.lower() or "cup" in cat_name.lower():
            mapped = "paper_cardboard"
        elif "food" in cat_name.lower() or "organic" in cat_name.lower():
            mapped = "organic_food_waste"

        safaios_counts[mapped] = safaios_counts.get(mapped, 0) + count

    print("\n--- Mapped SafaiOS Taxonomy Counts (TACO Subset) ---")
    for s_cat, count in sorted(safaios_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {s_cat}: {count} annotations")

    return {
        "num_images": len(images),
        "num_annotations": len(annotations),
        "fine_categories": len(categories),
        "safaios_mapped_counts": safaios_counts
    }

if __name__ == "__main__":
    analyze_taco()
