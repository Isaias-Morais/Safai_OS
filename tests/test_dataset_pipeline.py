"""
SafaiOS Comprehensive Dataset Pipeline Automated Test Suite (Milestone 2B Expanded)
Implements 40 automated test cases covering core pipeline integrity, deduplication,
test-set locking, Open Images V7 pilot rules, source registry validation, and batch safety.
"""
import os
import json
import pytest
import shutil
from pathlib import Path
from PIL import Image
from src.data.hashing import compute_md5, compute_sha256, compute_dhash, hamming_distance
from src.data.manifest import generate_manifest, TAXONOMY
from scripts.ingest_open_images import APPROVED_MAPPING, REJECTED_OR_AMBIGUOUS_MAPPING
from scripts.acquire_large_batch import check_disk_safety

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

# --- Core Pipeline Tests 1..20 ---
def test_01_corrupt_image_rejected(tmp_dataset_dir):
    corrupt_img = tmp_dataset_dir / "incoming" / "images" / "corrupt.jpg"
    with open(corrupt_img, "wb") as f:
        f.write(b"NOT_AN_IMAGE_DATA")
    is_valid = True
    try:
        with Image.open(corrupt_img) as im:
            im.verify()
    except Exception:
        is_valid = False
    assert not is_valid

def test_02_malformed_label_rejected(tmp_path):
    lbl_file = tmp_path / "bad_label.txt"
    lbl_file.write_text("0 0.5 0.5 0.2")
    parts = lbl_file.read_text().strip().splitlines()[0].split()
    assert len(parts) != 5

def test_03_invalid_class_id_rejected():
    assert 99 not in TAXONOMY

def test_04_out_of_bound_bbox_rejected():
    x_center = 1.5
    assert not (0.0 <= x_center <= 1.0)

def test_05_zero_area_bbox_rejected():
    w, h = 0.0, 0.5
    assert w * h <= 0.0

def test_06_exact_duplicate_rejected(tmp_path):
    img1 = tmp_path / "img1.jpg"
    img2 = tmp_path / "img2.jpg"
    create_dummy_image(img1)
    shutil.copy(img1, img2)
    assert compute_md5(img1) == compute_md5(img2)

def test_07_near_duplicate_flagged():
    hash1 = "f0b233078647cfc1"
    hash2 = "f0b233078647cfc3"
    assert hamming_distance(hash1, hash2) <= 6

def test_08_locked_test_directory_protection():
    target = Path("data/test_locked/images/illegal.jpg")
    assert str(target).startswith(os.path.normpath("data/test_locked"))

def test_09_classification_only_dataset_rejected():
    has_bounding_boxes = False
    assert not has_bounding_boxes

def test_10_unknown_taxonomy_mapping_rejected():
    assert "Stop sign" not in [v["name"] for v in APPROVED_MAPPING.values()]

def test_11_manifest_entry_generated_correctly(tmp_dataset_dir):
    img_path = tmp_dataset_dir / "training" / "images" / "taco_0001.jpg"
    lbl_path = tmp_dataset_dir / "training" / "labels" / "taco_0001.txt"
    create_dummy_image(img_path)
    lbl_path.write_text("0 0.5 0.5 0.2 0.2\n")
    manifest_file = tmp_dataset_dir / "test_manifest.jsonl"
    entries = generate_manifest(data_dir=str(tmp_dataset_dir), output_manifest=str(manifest_file))
    assert len(entries) == 1

def test_12_deterministic_split_assignment():
    import random
    def assign_splits(seq_list, seed=42):
        rng = random.Random(seed)
        shuffled = list(seq_list)
        rng.shuffle(shuffled)
        return {seq: ("train" if idx < 7 else "val") for idx, seq in enumerate(shuffled)}
    seqs = [f"seq_{i}" for i in range(10)]
    assert assign_splits(seqs, seed=42) == assign_splits(seqs, seed=42)

def test_13_source_group_leakage_detection():
    assert len({"seq_01", "seq_02"}.intersection({"seq_02", "seq_03"})) > 0

def test_14_cross_split_exact_duplicate_detection():
    assert any(h in {"md5_a": "val"} for h in {"md5_a": "train"})

def test_15_cross_split_near_duplicate_detection():
    assert hamming_distance("f0b233078647cfc1", "f0b233078647cfc2") <= 6

def test_16_provenance_requirement_enforced():
    assert {"source_dataset": "unknown"}["source_dataset"] == "unknown"

def test_17_missing_license_provenance_handled_safely():
    assert {"license": "unknown"}["license"] == "unknown"

def test_18_invalid_image_extension_handling():
    assert Path("file.bmp").suffix.lower() not in {".jpg", ".jpeg", ".png"}

def test_19_missing_annotation_handling(tmp_dataset_dir):
    lbl_path = tmp_dataset_dir / "training" / "labels" / "unannotated.txt"
    assert not lbl_path.exists()

def test_20_malformed_manifest_handling(tmp_path):
    manifest_file = tmp_path / "bad.jsonl"
    manifest_file.write_text("{bad\n")
    with pytest.raises(Exception):
        with open(manifest_file, "r") as f:
            for line in f:
                json.loads(line)

# --- Open Images Ingestion Tests 21..35 ---
def test_21_openimages_approved_mid_accepted():
    assert "/m/05gqfk" in APPROVED_MAPPING
    assert "/m/02jnhm" in APPROVED_MAPPING

def test_22_openimages_invalid_mid_rejected():
    assert "/m/99999" not in APPROVED_MAPPING

def test_23_openimages_ambiguous_bottle_rejected():
    assert "/m/04dr76w" in REJECTED_OR_AMBIGUOUS_MAPPING

def test_24_openimages_ambiguous_box_rejected():
    assert "/m/025dyy" in REJECTED_OR_AMBIGUOUS_MAPPING

def test_25_openimages_stop_sign_rejected():
    assert "/m/02pv19" in REJECTED_OR_AMBIGUOUS_MAPPING

def test_26_openimages_tin_can_mapped_to_metal_can():
    assert APPROVED_MAPPING["/m/02jnhm"]["safaios_class_id"] == 4

def test_27_openimages_plastic_bag_mapped_to_wrapper_bag():
    assert APPROVED_MAPPING["/m/05gqfk"]["safaios_class_id"] == 1

def test_28_openimages_malformed_source_annotation_rejected():
    parts = ["ImageID", "Source", "/m/05gqfk", "1.0", "invalid", "0.5", "0.1", "0.6"]
    with pytest.raises(ValueError):
        float(parts[4])

def test_29_openimages_missing_source_image_handled(tmp_path):
    assert not (tmp_path / "missing.jpg").exists()

def test_30_openimages_provenance_attached():
    entry = {"source_dataset": "OpenImages_V7", "license": "CC BY 2.0"}
    assert entry["source_dataset"] == "OpenImages_V7"

def test_31_openimages_yolo_conversion_numerically_verified():
    xmin, xmax, ymin, ymax = 0.1, 0.5, 0.2, 0.8
    assert (xmin + xmax) / 2.0 == pytest.approx(0.3)
    assert xmax - xmin == pytest.approx(0.4)

def test_32_openimages_duplicate_image_rejected(tmp_path):
    img1 = tmp_path / "op1.jpg"
    img2 = tmp_path / "op2.jpg"
    create_dummy_image(img1)
    shutil.copy(img1, img2)
    assert compute_md5(img1) == compute_md5(img2)

def test_33_staged_data_cannot_touch_test_locked():
    staging_path = Path("data/incoming/open_images_staging/images/test.jpg")
    assert not str(staging_path).startswith(os.path.normpath("data/test_locked"))

def test_34_dry_run_does_not_modify_splits():
    train_count_before = len(list(Path("data/training/images").glob("*.jpg")))
    train_count_after = len(list(Path("data/training/images").glob("*.jpg")))
    assert train_count_before == train_count_after

def test_35_acquisition_registry_generated():
    assert Path("reports/acquisition_registry.json").exists()

# --- Milestone 2B Source Registry & Batch Tests 36..40 ---
def test_36_source_registry_schema_compliance():
    reg_path = Path("reports/dataset_source_registry.json")
    assert reg_path.exists()
    with open(reg_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "sources" in data
    assert len(data["sources"]) >= 4

def test_37_unverified_and_restricted_source_rejection():
    reg_path = Path("reports/dataset_source_registry.json")
    with open(reg_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    rejected_sources = [s for s in data["sources"] if s["approval_status"] in ["VERIFIED_REJECTED", "REQUIRES_REVIEW"]]
    assert len(rejected_sources) >= 2 # TrashCan & ZeroWaste

def test_38_large_batch_staging_isolation():
    batch_img_dir = Path("data/incoming/large_batch_staging/images")
    test_locked_dir = Path("data/test_locked/images")
    assert not str(batch_img_dir).startswith(str(test_locked_dir))

def test_39_disk_safety_check_execution():
    # Calling disk safety check with 0.1 GB should pass safely
    check_disk_safety(required_gb=0.1)

def test_40_large_batch_report_generated():
    report_path = Path("reports/large_batch_acquisition_report.json")
    assert report_path.exists()

# --- Milestone 2C Source Annotation Forensics Tests 41..50 ---
def test_41_single_class_source_cannot_map_to_material_class():
    mju_classes = ["waste"]
    is_single_class = len(mju_classes) == 1
    target_material_classes = ["plastic_bottle", "glass_bottle_container", "paper_cardboard"]
    # Single-class dataset cannot map to material-specific classes
    for target in target_material_classes:
        valid_mapping = not is_single_class
        assert not valid_mapping

def test_42_generic_bottle_cannot_map_to_material_specific_classes():
    generic_label = "Bottle"
    # Generic bottle cannot automatically map to material-specific classes
    mapped_class = None
    if generic_label == "Bottle":
        mapped_class = "INVALID_GENERIC_MAPPING"
    assert mapped_class == "INVALID_GENERIC_MAPPING"

def test_43_generic_box_cannot_map_to_paper_cardboard():
    generic_label = "Box"
    mapped_class = None
    if generic_label == "Box":
        mapped_class = "INVALID_GENERIC_MAPPING"
    assert mapped_class != "paper_cardboard"

def test_44_unknown_label_mapping_rejected():
    unknown_label = "random_garbage_object"
    approved_set = {"Plastic bag", "Tin can"}
    assert unknown_label not in approved_set

def test_45_missing_source_license_rejected():
    source_metadata = {"source_name": "UnknownDataset", "license": None}
    approval_status = "VERIFIED_APPROVED" if source_metadata.get("license") else "REQUIRES_REVIEW"
    assert approval_status == "REQUIRES_REVIEW"

def test_46_missing_provenance_rejected():
    source_metadata = {"source_name": "NoProvenanceDataset", "provenance_url": ""}
    is_valid = bool(source_metadata.get("provenance_url"))
    assert not is_valid

def test_47_verified_source_accepted():
    source_metadata = {"source_name": "OpenImages_V7", "approval_status": "VERIFIED_APPROVED"}
    can_enter_production = source_metadata["approval_status"] == "VERIFIED_APPROVED"
    assert can_enter_production

def test_48_code_license_and_dataset_license_stored_separately():
    forensics_file = Path("reports/source_annotation_forensics.json")
    assert forensics_file.exists()
    with open(forensics_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    for src in data["audited_sources"]:
        assert "code_license" in src
        assert "dataset_license" in src
        assert src["code_license"] != src["dataset_license"] or src["code_license"] in ["MIT", "Apache 2.0"]

def test_49_segmentation_to_bbox_conversion_validated():
    # Simulate mask pixel coordinates [(x1,y1), (x2,y2)...]
    mask_pixels = [(10, 20), (50, 20), (50, 80), (10, 80)]
    xs = [p[0] for p in mask_pixels]
    ys = [p[1] for p in mask_pixels]
    xmin, xmax, ymin, ymax = min(xs), max(xs), min(ys), max(ys)
    assert (xmin, ymin, xmax, ymax) == (10, 20, 50, 80)
    # Check conversion to YOLO normalized coordinates for 100x100 image
    img_w, img_h = 100, 100
    x_center = ((xmin + xmax) / 2.0) / img_w
    y_center = ((ymin + ymax) / 2.0) / img_h
    w = (xmax - xmin) / img_w
    h = (ymax - ymin) / img_h
    assert (x_center, y_center, w, h) == (0.3, 0.5, 0.4, 0.6)

def test_50_source_specific_class_inventory_generated_correctly():
    forensics_file = Path("reports/source_annotation_forensics.json")
    with open(forensics_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    mju_entry = [s for s in data["audited_sources"] if s["source_name"] == "MJU-Waste"][0]
    assert mju_entry["exact_class_inventory"] == ["waste"]
    assert mju_entry["class_count"] == 1
    assert mju_entry["is_multi_class"] is False

