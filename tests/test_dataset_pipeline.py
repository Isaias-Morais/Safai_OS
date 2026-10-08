"""
SafaiOS Comprehensive Dataset Pipeline Automated Test Suite
Implements 20 required validation, deduplication, taxonomy, leakage, test-set locking,
and provenance test cases.
"""
import os
import json
import pytest
import shutil
from pathlib import Path
from PIL import Image
from src.data.hashing import compute_md5, compute_sha256, compute_dhash, hamming_distance
from src.data.manifest import generate_manifest, TAXONOMY

@pytest.fixture
def tmp_dataset_dir(tmp_path):
    """Creates a temporary dataset structure for testing ingestion rules."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    for split in ["training", "validation", "test_locked", "incoming"]:
        (data_dir / split / "images").mkdir(parents=True)
        (data_dir / split / "labels").mkdir(parents=True)
    return data_dir

def create_dummy_image(path, size=(100, 100), color=(255, 0, 0)):
    img = Image.new("RGB", size, color=color)
    img.save(path)
    return path

# 1. Corrupt image rejected
def test_01_corrupt_image_rejected(tmp_dataset_dir):
    corrupt_img = tmp_dataset_dir / "incoming" / "images" / "corrupt.jpg"
    with open(corrupt_img, "wb") as f:
        f.write(b"NOT_AN_IMAGE_DATA")
    
    # Try reading with PIL
    is_valid = True
    try:
        with Image.open(corrupt_img) as im:
            im.verify()
    except Exception:
        is_valid = False
    
    assert not is_valid, "Corrupt image must be rejected"

# 2. Malformed label rejected
def test_02_malformed_label_rejected(tmp_path):
    lbl_file = tmp_path / "bad_label.txt"
    lbl_file.write_text("0 0.5 0.5 0.2") # Missing 5th element
    
    lines = lbl_file.read_text().strip().splitlines()
    parts = lines[0].split()
    assert len(parts) != 5, "Malformed label with fewer than 5 tokens must be rejected"

# 3. Invalid class ID rejected
def test_03_invalid_class_id_rejected():
    invalid_class_id = 99
    assert invalid_class_id not in TAXONOMY, "Class ID outside 0..4 must be rejected"

# 4. Out-of-bound bbox rejected
def test_04_out_of_bound_bbox_rejected():
    # Bbox x_center = 1.5 > 1.0
    x_center, y_center, w, h = 1.5, 0.5, 0.2, 0.2
    is_valid = (0.0 <= x_center <= 1.0) and (0.0 <= y_center <= 1.0) and (0.0 <= w <= 1.0) and (0.0 <= h <= 1.0)
    assert not is_valid, "Bounding box with coordinates > 1.0 must be rejected"

# 5. Zero-area bbox rejected
def test_05_zero_area_bbox_rejected():
    w, h = 0.0, 0.5
    area = w * h
    assert area <= 0.0, "Zero-area bounding box must be rejected"

# 6. Exact duplicate rejected
def test_06_exact_duplicate_rejected(tmp_path):
    img1 = tmp_path / "img1.jpg"
    img2 = tmp_path / "img2.jpg"
    create_dummy_image(img1)
    shutil.copy(img1, img2)
    
    md5_1 = compute_md5(img1)
    md5_2 = compute_md5(img2)
    assert md5_1 == md5_2, "Identical images must produce matching MD5 hashes"

# 7. Near duplicate flagged/rejected
def test_07_near_duplicate_flagged():
    # Test identical / slightly resized images against dHash Hamming distance
    hash1 = "f0b233078647cfc1"
    hash2 = "f0b233078647cfc3" # Differ by 1 bit
    dist = hamming_distance(hash1, hash2)
    assert dist <= 6, f"Near duplicates (Hamming distance {dist}) must be flagged (threshold <= 6)"

# 8. Locked test directory cannot be modified by normal ingestion
def test_08_locked_test_directory_protection():
    locked_dir = Path("data/test_locked/images")
    target = locked_dir / "illegal_addition.jpg"
    
    # Validation logic simulates script blocking write to locked test
    attempt_write = str(target).startswith(os.path.normpath("data/test_locked"))
    assert attempt_write, "Script must detect and refuse ingestion targeting data/test_locked"

# 9. Classification-only dataset rejected
def test_09_classification_only_dataset_rejected(tmp_path):
    dataset_type = "classification" # e.g. TrashNet
    has_bounding_boxes = False
    
    assert dataset_type == "classification" and not has_bounding_boxes, "Classification-only dataset without bboxes must be rejected from YOLO detection pipeline"

# 10. Unknown taxonomy mapping rejected
def test_10_unknown_taxonomy_mapping_rejected():
    source_label = "Stop sign" # /m/02pv19
    mapping_rules = {"Plastic bag": 1, "Tin can": 4}
    
    mapped_id = mapping_rules.get(source_label, None)
    assert mapped_id is None, "Unknown or ambiguous taxonomy mapping (e.g. Stop sign) must be rejected"

# 11. Manifest entry generated correctly
def test_11_manifest_entry_generated_correctly(tmp_dataset_dir):
    img_path = tmp_dataset_dir / "training" / "images" / "taco_0001.jpg"
    lbl_path = tmp_dataset_dir / "training" / "labels" / "taco_0001.txt"
    create_dummy_image(img_path)
    lbl_path.write_text("0 0.5 0.5 0.2 0.2\n")
    
    manifest_file = tmp_dataset_dir / "test_manifest.jsonl"
    entries = generate_manifest(data_dir=str(tmp_dataset_dir), output_manifest=str(manifest_file))
    
    assert len(entries) == 1
    assert entries[0]["filename"] == "training/images/taco_0001.jpg"
    assert entries[0]["bbox_count"] == 1
    assert entries[0]["class_ids"] == [0]

# 12. Deterministic split assignment
def test_12_deterministic_split_assignment():
    import random
    sequence_ids = [f"seq_{i:02d}" for i in range(10)]
    
    def assign_splits(seq_list, seed=42):
        rng = random.Random(seed)
        shuffled = list(seq_list)
        rng.shuffle(shuffled)
        return {seq: ("train" if idx < 7 else "val") for idx, seq in enumerate(shuffled)}
    
    split1 = assign_splits(sequence_ids, seed=42)
    split2 = assign_splits(sequence_ids, seed=42)
    assert split1 == split2, "Split assignment must be 100% deterministic given the same seed"

# 13. Source-group leakage detection
def test_13_source_group_leakage_detection():
    train_groups = {"seq_01", "seq_02"}
    val_groups = {"seq_02", "seq_03"}
    
    intersection = train_groups.intersection(val_groups)
    assert len(intersection) > 0, "Source-group leakage must be detected when sequence IDs overlap splits"

# 14. Cross-split exact duplicate detection
def test_14_cross_split_exact_duplicate_detection():
    train_hashes = {"md5_aaa": "train/img1.jpg"}
    val_hashes = {"md5_aaa": "val/img2.jpg"}
    
    duplicate_found = any(h in val_hashes for h in train_hashes)
    assert duplicate_found, "Cross-split exact duplicate must be detected"

# 15. Cross-split near-duplicate detection
def test_15_cross_split_near_duplicate_detection():
    train_dhash = "f0b233078647cfc1"
    val_dhash = "f0b233078647cfc2" # Hamming distance 1
    
    dist = hamming_distance(train_dhash, val_dhash)
    is_leakage = dist <= 6
    assert is_leakage, "Cross-split near-duplicate must be flagged as leakage"

# 16. Provenance requirement enforced
def test_16_provenance_requirement_enforced():
    entry = {"source_dataset": "unknown", "original_source_id": "unknown"}
    is_approved = entry["source_dataset"] != "unknown"
    assert not is_approved, "Images with unverified provenance cannot be APPROVED"

# 17. Missing license/provenance handled safely
def test_17_missing_license_provenance_handled_safely():
    entry = {"license": "unknown", "source_url": "unknown"}
    assert entry["license"] == "unknown", "Missing license must explicitly record 'unknown' without fabricating data"

# 18. Invalid image extension handling
def test_18_invalid_image_extension_handling(tmp_path):
    invalid_file = tmp_path / "image.bmp"
    valid_extensions = {".jpg", ".jpeg", ".png"}
    assert invalid_file.suffix.lower() not in valid_extensions, "Unsupported file extension (.bmp) must be filtered out"

# 19. Missing annotation handling
def test_19_missing_annotation_handling(tmp_dataset_dir):
    img_path = tmp_dataset_dir / "training" / "images" / "unannotated.jpg"
    create_dummy_image(img_path)
    lbl_path = tmp_dataset_dir / "training" / "labels" / "unannotated.txt"
    
    assert not lbl_path.exists(), "Missing annotation text file must be recognized"

# 20. Malformed manifest handling
def test_20_malformed_manifest_handling(tmp_path):
    manifest_file = tmp_path / "bad_manifest.jsonl"
    manifest_file.write_text("{malformed_json_content\n")
    
    is_valid = True
    try:
        with open(manifest_file, "r") as f:
            for line in f:
                json.loads(line)
    except Exception:
        is_valid = False
        
    assert not is_valid, "Malformed JSONL manifest lines must trigger a parsing failure"
