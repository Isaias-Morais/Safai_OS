"""Model serialization and export configuration helper."""
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class ExportConfig:
    format: str = "onnx"
    imgsz: int = 768
    half: bool = False
    opset: int = 17
    dynamic: bool = False
    simplify: bool = True

    def validate(self) -> None:
        valid_formats = {"onnx", "torchscript", "engine", "tflite"}
        if self.format not in valid_formats:
            raise ValueError(f"Unsupported format '{self.format}'. Must be one of {valid_formats}")
        if self.imgsz <= 0 or self.imgsz % 32 != 0:
            raise ValueError(f"imgsz must be positive multiple of 32, got {self.imgsz}")

class ModelExporter:
    def __init__(self, weights_path: str, config: Optional[ExportConfig] = None):
        self.weights_path = weights_path
        self.config = config or ExportConfig()
        self.config.validate()

    def get_export_args(self) -> Dict[str, Any]:
        return {
            "format": self.config.format,
            "imgsz": self.config.imgsz,
            "half": self.config.half,
            "opset": self.config.opset,
            "dynamic": self.config.dynamic,
            "simplify": self.config.simplify
        }
