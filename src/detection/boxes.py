"""BoundingBox and Prediction representations with geometry and IoU calculations."""
from dataclasses import dataclass
from typing import Tuple, List, Optional
import math

@dataclass
class BoundingBox:
    xmin: float
    ymin: float
    xmax: float
    ymax: float
    format: str = "xyxy"

    def __post_init__(self):
        if self.xmin > self.xmax:
            self.xmin, self.xmax = self.xmax, self.xmin
        if self.ymin > self.ymax:
            self.ymin, self.ymax = self.ymax, self.ymin

    @property
    def width(self) -> float:
        return max(0.0, self.xmax - self.xmin)

    @property
    def height(self) -> float:
        return max(0.0, self.ymax - self.ymin)

    @property
    def area(self) -> float:
        return self.width * self.height

    def to_xywh(self) -> Tuple[float, float, float, float]:
        cx = (self.xmin + self.xmax) / 2.0
        cy = (self.ymin + self.ymax) / 2.0
        return (cx, cy, self.width, self.height)

    def to_xyxy(self) -> Tuple[float, float, float, float]:
        return (self.xmin, self.ymin, self.xmax, self.ymax)

    def iou(self, other: "BoundingBox") -> float:
        ixmin = max(self.xmin, other.xmin)
        iymin = max(self.ymin, other.ymin)
        ixmax = min(self.xmax, other.xmax)
        iymax = min(self.ymax, other.ymax)

        iw = max(0.0, ixmax - ixmin)
        ih = max(0.0, iymax - iymin)
        intersection = iw * ih

        union = self.area + other.area - intersection
        if union <= 0.0:
            return 0.0
        return intersection / union

    def clip(self, min_val: float = 0.0, max_val: float = 1.0) -> "BoundingBox":
        return BoundingBox(
            xmin=max(min_val, min(max_val, self.xmin)),
            ymin=max(min_val, min(max_val, self.ymin)),
            xmax=max(min_val, min(max_val, self.xmax)),
            ymax=max(min_val, min(max_val, self.ymax)),
        )

@dataclass
class Prediction:
    box: BoundingBox
    class_id: int
    confidence: float
    class_name: Optional[str] = None
