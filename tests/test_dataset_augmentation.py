import pytest
from src.detection.boxes import BoundingBox
from src.data.augmentation import horizontal_flip_bbox, scale_bbox

def test_horizontal_flip():
    box = BoundingBox(xmin=0.1, ymin=0.2, xmax=0.4, ymax=0.6)
    flipped = horizontal_flip_bbox(box)
    assert pytest.approx(flipped.xmin) == 0.6
    assert pytest.approx(flipped.xmax) == 0.9
    assert pytest.approx(flipped.ymin) == 0.2
    assert pytest.approx(flipped.ymax) == 0.6

def test_scale_bbox():
    box = BoundingBox(xmin=0.2, ymin=0.2, xmax=0.4, ymax=0.4)
    scaled = scale_bbox(box, scale_x=2.0, scale_y=2.0)
    # Original center: (0.3, 0.3), width: 0.2, height: 0.2
    # Scaled width: 0.4, height: 0.4 -> xmin: 0.1, xmax: 0.5
    assert pytest.approx(scaled.xmin) == 0.1
    assert pytest.approx(scaled.xmax) == 0.5
