"""YOLOInferenceEngine implementation wrapping Ultralytics YOLO models."""
from typing import List, Union
import numpy as np
from src.inference.base import BaseDetector, DetectorConfig
from src.detection.boxes import BoundingBox, Prediction

class YOLOInferenceEngine(BaseDetector):
    def __init__(self, config: DetectorConfig):
        super().__init__(config)
        self.model = None

    def load_model(self) -> None:
        from ultralytics import YOLO
        self.model = YOLO(self.config.weights_path)

    def predict(self, image: Union[str, np.ndarray]) -> List[Prediction]:
        if self.model is None:
            self.load_model()

        results = self.model.predict(
            source=image,
            imgsz=self.config.imgsz,
            conf=self.config.conf_threshold,
            iou=self.config.iou_threshold,
            device=self.config.device,
            half=self.config.half_precision,
            verbose=False
        )

        predictions = []
        if not results:
            return predictions

        res = results[0]
        boxes = res.boxes
        if boxes is None or len(boxes) == 0:
            return predictions

        orig_h, orig_w = res.orig_shape

        for i in range(len(boxes)):
            xyxy = boxes.xyxy[i].cpu().numpy()
            conf = float(boxes.conf[i].cpu().numpy())
            cls_id = int(boxes.cls[i].cpu().numpy())
            cls_name = self.model.names.get(cls_id, str(cls_id)) if hasattr(self.model, "names") else str(cls_id)

            bbox = BoundingBox(
                xmin=float(xyxy[0]) / orig_w,
                ymin=float(xyxy[1]) / orig_h,
                xmax=float(xyxy[2]) / orig_w,
                ymax=float(xyxy[3]) / orig_h
            )
            predictions.append(Prediction(box=bbox, class_id=cls_id, confidence=conf, class_name=cls_name))

        return predictions
