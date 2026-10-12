import pytest
from src.detection.boxes import BoundingBox, Prediction

def test_bounding_box_properties():
    box = BoundingBox(xmin=10.0, ymin=20.0, xmax=50.0, ymax=80.0)
    assert box.width == 40.0
    assert box.height == 60.0
    assert box.area == 2400.0

def test_bounding_box_inverted_coords():
    box = BoundingBox(xmin=50.0, ymin=80.0, xmax=10.0, ymax=20.0)
    assert box.xmin == 10.0
    assert box.xmax == 50.0
    assert box.ymin == 20.0
    assert box.ymax == 80.0

def test_bounding_box_to_xywh():
    box = BoundingBox(xmin=10.0, ymin=20.0, xmax=50.0, ymax=80.0)
    cx, cy, w, h = box.to_xywh()
    assert cx == 30.0
    assert cy == 50.0
    assert w == 40.0
    assert h == 60.0

def test_bounding_box_iou():
    b1 = BoundingBox(xmin=0.0, ymin=0.0, xmax=10.0, ymax=10.0)
    b2 = BoundingBox(xmin=0.0, ymin=0.0, xmax=10.0, ymax=10.0)
    assert pytest.approx(b1.iou(b2)) == 1.0

    b3 = BoundingBox(xmin=10.0, ymin=10.0, xmax=20.0, ymax=20.0)
    assert b1.iou(b3) == 0.0

    b4 = BoundingBox(xmin=5.0, ymin=0.0, xmax=15.0, ymax=10.0)
    # Area1: 100, Area2: 100, Inter: 5*10=50, Union: 150 -> IoU = 50/150 = 1/3
    assert pytest.approx(b1.iou(b4)) == 1.0 / 3.0

def test_prediction_creation():
    box = BoundingBox(xmin=0.1, ymin=0.2, xmax=0.5, ymax=0.6)
    pred = Prediction(box=box, class_id=0, confidence=0.95, class_name="plastic_bottle")
    assert pred.class_id == 0
    assert pred.confidence == 0.95
    assert pred.class_name == "plastic_bottle"
