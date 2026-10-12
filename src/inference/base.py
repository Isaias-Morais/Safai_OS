"""Abstract Base Detector interface and configuration schemas."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Union
import numpy as np
from src.detection.boxes import Prediction

@dataclass
class DetectorConfig:
    weights_path: str
    imgsz: int = 768
    conf_threshold: float = 0.25
    iou_threshold: float = 0.60
    device: str = "cpu"
    half_precision: bool = False

class BaseDetector(ABC):
    def __init__(self, config: DetectorConfig):
        self.config = config

    @abstractmethod
    def load_model(self) -> None:
        """Loads and initializes the model weights."""
        pass

    @abstractmethod
    def predict(self, image: Union[str, np.ndarray]) -> List[Prediction]:
        """Performs detection on a single image and returns predictions."""
        pass
