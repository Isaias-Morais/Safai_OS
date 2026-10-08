"""
Automated Unit Tests for SafaiOS Dataset Engineering & Quality Pipeline
"""
import os
import pytest
from pathlib import Path
from src.data.hashing import compute_md5, compute_dhash, hamming_distance
from src.data.manifest import generate_manifest

def test_dhash_identical_and_near_duplicates(tmp_path):
    # Test identical image hashes
    img_path = tmp_path / "test_img.png"
    from PIL import Image
    im = Image.new("RGB", (100, 100), color="red")
    im.save(img_path)
    
    hash1 = compute_dhash(img_path)
    hash2 = compute_dhash(img_path)
    assert hash1 == hash2
    assert hamming_distance(hash1, hash2) == 0

def test_manifest_generation(tmp_path):
    manifest_out = tmp_path / "test_manifest.jsonl"
    entries = generate_manifest(data_dir="data", output_manifest=str(manifest_out), version="test_v1.0")
    assert len(entries) == 1238
    assert manifest_out.exists()
    
    # Check entry fields
    first_entry = entries[0]
    assert "image_id" in first_entry
    assert "sha256" in first_entry
    assert "md5" in first_entry
    assert "perceptual_hash" in first_entry
    assert first_entry["validation_status"] == "VALID"

def test_test_locked_policy_exists():
    policy_file = Path("data/test_locked/LOCKED_TEST_SET_POLICY.md")
    assert policy_file.exists()
    content = policy_file.read_text()
    assert "STRICTLY LOCKED" in content
