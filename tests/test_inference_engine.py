import pytest
from unittest.mock import MagicMock
from src.inference.base import DetectorConfig
from src.inference.engine import YOLOInferenceEngine

def test_detector_config_defaults():
    cfg = DetectorConfig(weights_path="dummy.pt")
    assert cfg.imgsz == 768
    assert cfg.conf_threshold == 0.25
    assert cfg.device == "cpu"
    assert not cfg.half_precision

def test_yolo_inference_engine_lazy_load():
    cfg = DetectorConfig(weights_path="dummy.pt")
    engine = YOLOInferenceEngine(cfg)
    assert engine.model is None
