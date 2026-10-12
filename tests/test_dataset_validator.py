import pytest
from src.data.validator import validate_yolo_annotation_line

def test_validate_yolo_valid_line():
    ok, err = validate_yolo_annotation_line("0 0.5 0.5 0.2 0.3", num_classes=5)
    assert ok
    assert err == ""

def test_validate_yolo_out_of_bounds_class():
    ok, err = validate_yolo_annotation_line("7 0.5 0.5 0.2 0.3", num_classes=5)
    assert not ok
    assert "Class ID 7 out of range" in err

def test_validate_yolo_out_of_bounds_coord():
    ok, err = validate_yolo_annotation_line("0 1.2 0.5 0.2 0.3", num_classes=5)
    assert not ok
    assert "out of bounds" in err
