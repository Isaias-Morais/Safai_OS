"""Dataset summary generator and label distribution report script."""
import json
from pathlib import Path
from src.data.statistics import compute_class_distribution

TAXONOMY = {
    0: "plastic_bottle",
    1: "plastic_wrapper_bag",
    2: "paper_cardboard",
    3: "glass_bottle_container",
    4: "metal_can"
}

def generate_summary():
    val_labels_dir = Path("data/safaios_dataset_v10k/validation/labels")
    if not val_labels_dir.exists():
        print("Validation labels directory not found, using reference distribution.")
        return

    all_classes = []
    for txt in val_labels_dir.glob("*.txt"):
        with open(txt, "r") as f:
            for line in f:
                parts = line.strip().split()
                if parts:
                    all_classes.append(int(parts[0]))

    stats = compute_class_distribution(all_classes, num_classes=5)
    print("=== SafaiOS Validation Class Distribution Summary ===")
    print(f"Total instances: {stats['total_instances']}")
    for cid, name in TAXONOMY.items():
        cnt = stats['per_class'][cid]['count']
        prop = stats['per_class'][cid]['proportion'] * 100
        print(f"  [{cid}] {name}: {cnt} instances ({prop:.2f}%)")

if __name__ == "__main__":
    generate_summary()
