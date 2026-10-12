import pytest
from src.export.exporter import ExportConfig, ModelExporter

def test_export_config_validation():
    cfg = ExportConfig(format="onnx", imgsz=768)
    cfg.validate()

    with pytest.raises(ValueError, match="Unsupported format"):
        invalid = ExportConfig(format="unsupported_format")
        invalid.validate()

    with pytest.raises(ValueError, match="multiple of 32"):
        invalid_size = ExportConfig(imgsz=750)
        invalid_size.validate()

def test_model_exporter_args():
    exporter = ModelExporter("best.pt", ExportConfig(format="onnx", imgsz=640))
    args = exporter.get_export_args()
    assert args["format"] == "onnx"
    assert args["imgsz"] == 640
