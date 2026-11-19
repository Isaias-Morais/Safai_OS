"""Guarded training entry point for SAFAIOS-E004-YOLO11S-COARSEDROPOUT.

The default action is a non-training preflight.  Full training can only start
when the caller explicitly supplies ``--execute-training``.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
E002_ARGS_PATH = ROOT / "runs/detect/runs/detect/runs/safaios/safaios_yolo11s_v10k_img768/args.yaml"
DATA_YAML_PATH = ROOT / "data/safaios_dataset_v10k/data.yaml"
MODEL_PATH = "yolo11s.pt"
EXPERIMENT_ID = "SAFAIOS-E004-YOLO11S-COARSEDROPOUT"
EXPERIMENT_NAME = "safaios_yolo11s_v10k_coarsedropout"
OUTPUT_PROJECT = "runs/safaios"
ALBUMENTATIONS_VERSION = "2.0.8"

# These are the E002 controls that must remain fixed for E004.  Output paths,
# model initialization and the one CoarseDropout intervention are intentionally
# separate from this baseline control set.
E002_CONTROL_KEYS = (
    "epochs", "patience", "batch", "imgsz", "save", "save_period", "cache",
    "device", "workers", "pretrained", "cls_remap", "optimizer", "verbose",
    "seed", "deterministic", "single_cls", "rect", "cos_lr", "close_mosaic",
    "amp", "fraction", "profile", "freeze", "multi_scale", "compile",
    "channels_last", "overlap_mask", "mask_ratio", "dropout", "val", "split",
    "save_json", "conf", "iou", "max_det", "quantize", "dnn", "plots", "nms",
    "augment", "agnostic_nms", "classes", "retina_masks", "embed", "show",
    "save_frames", "save_txt", "save_conf", "save_crop", "show_labels", "show_conf",
    "show_boxes", "line_width", "lr0", "lrf", "momentum", "weight_decay",
    "warmup_epochs", "warmup_momentum", "warmup_bias_lr", "box", "cls", "cls_pw",
    "dfl", "nbs", "hsv_h", "hsv_s", "hsv_v", "degrees", "translate", "scale",
    "shear", "perspective", "flipud", "fliplr", "bgr", "mosaic", "mixup", "cutmix",
    "copy_paste", "copy_paste_mode", "auto_augment", "erasing",
)


def build_coarse_dropout():
    """Return exactly the frozen E004 Albumentations transform."""
    os.environ.setdefault("NO_ALBUMENTATIONS_UPDATE", "1")
    import albumentations as A

    if A.__version__ != ALBUMENTATIONS_VERSION:
        raise RuntimeError(
            f"E004 requires albumentations=={ALBUMENTATIONS_VERSION}; found {A.__version__}."
        )
    return A.CoarseDropout(
        num_holes_range=(1, 2),
        hole_height_range=(0.08, 0.18),
        hole_width_range=(0.08, 0.18),
        fill=(114, 114, 114),
        fill_mask=None,
        p=0.5,
    )


def load_e002_controls(path: Path = E002_ARGS_PATH) -> dict[str, Any]:
    """Load the recorded E002 controls instead of duplicating guessed settings."""
    if not path.is_file():
        raise FileNotFoundError(f"Frozen E002 args.yaml not found: {path}")
    controls = yaml.safe_load(path.read_text(encoding="utf-8"))
    missing = [key for key in E002_CONTROL_KEYS if key not in controls]
    if missing:
        raise RuntimeError(f"Frozen E002 configuration is missing controls: {', '.join(missing)}")
    return {key: controls[key] for key in E002_CONTROL_KEYS}


def build_training_overrides() -> dict[str, Any]:
    """Build E004 overrides from E002, changing only the declared experiment identity."""
    overrides = load_e002_controls()
    overrides.update(
        {
            "task": "detect",
            "mode": "train",
            "model": MODEL_PATH,  # E004 protocol requires fresh pretrained initialization.
            "data": str(DATA_YAML_PATH.relative_to(ROOT)),
            "project": OUTPUT_PROJECT,
            "name": EXPERIMENT_NAME,
            "exist_ok": False,  # Never overwrite an existing E004 run.
            "resume": False,
        }
    )
    return overrides


def load_training_and_validation_data() -> dict[str, Any]:
    """Load only training/validation paths; protected benchmark paths are never resolved."""
    raw = yaml.safe_load(DATA_YAML_PATH.read_text(encoding="utf-8"))
    root = ROOT / raw["path"]
    return {
        "path": str(root),
        "train": str(root / raw["train"]),
        "val": str(root / raw["val"]),
        "nc": raw["nc"],
        "names": raw["names"],
    }


def _set_training_augmentation(args: SimpleNamespace) -> None:
    """Install the custom transform where Ultralytics v8_transforms reads it."""
    args.augmentations = [build_coarse_dropout()]


def create_e004_trainer():
    """Return a trainer that injects CoarseDropout only while building train data."""
    from ultralytics.models.yolo.detect import DetectionTrainer

    class E004DetectionTrainer(DetectionTrainer):
        def build_dataset(self, img_path: str, mode: str = "train", batch: int | None = None):
            if mode == "train":
                _set_training_augmentation(self.args)
            return super().build_dataset(img_path, mode=mode, batch=batch)

    return E004DetectionTrainer


def _find_albumentations_transform(dataset):
    return next(
        (
            transform
            for transform in dataset.transforms.transforms
            if transform.__class__.__name__ == "Albumentations"
        ),
        None,
    )


def run_preflight() -> None:
    """Exercise the real Ultralytics dataset builder without constructing a trainer or training."""
    import numpy as np
    import torch
    import ultralytics
    from ultralytics.cfg import DEFAULT_CFG, get_cfg
    from ultralytics.data.build import build_yolo_dataset
    from ultralytics.data.augment import Albumentations
    from ultralytics.utils.instance import Instances

    if ultralytics.__version__ != "8.4.174":
        raise RuntimeError(f"E004 protocol requires ultralytics==8.4.174; found {ultralytics.__version__}.")
    overrides = build_training_overrides()
    cfg = get_cfg(DEFAULT_CFG, overrides=overrides)
    _set_training_augmentation(cfg)
    data = load_training_and_validation_data()

    # This is the same build_yolo_dataset function invoked by DetectionTrainer.
    train_dataset = build_yolo_dataset(cfg, data["train"], batch=cfg.batch, data=data, mode="train", stride=32)
    train_albu = _find_albumentations_transform(train_dataset)
    if train_albu is None or train_albu.transform is None:
        raise RuntimeError("E004 CoarseDropout was not injected into the training pipeline.")
    transforms = train_albu.transform.transforms
    if len(transforms) != 1 or transforms[0].__class__.__name__ != "CoarseDropout":
        raise RuntimeError("Training Albumentations pipeline differs from the frozen E004 transform list.")
    # Directly exercise Ultralytics' Albumentations wrapper to prove its spatial
    # pathway preserves E004 labels exactly while altering only image pixels.
    boxes = np.array([[0.50, 0.50, 0.20, 0.20], [0.25, 0.25, 0.10, 0.10]], dtype=np.float32)
    labels = {
        "img": np.full((128, 128, 3), 200, dtype=np.uint8),
        "cls": np.array([[0], [4]], dtype=np.float32),
        "instances": Instances(boxes.copy(), bbox_format="xywh", normalized=True),
    }
    wrapper = Albumentations(p=1.0, transforms=[build_coarse_dropout()])
    augmented = wrapper(labels)
    if not np.allclose(augmented["instances"].bboxes, boxes) or len(augmented["cls"]) != len(boxes):
        raise RuntimeError("CoarseDropout changed E004 bounding boxes or labels.")
    val_dataset = build_yolo_dataset(cfg, data["val"], batch=cfg.batch, data=data, mode="val", rect=True, stride=32)
    if _find_albumentations_transform(val_dataset) is not None:
        raise RuntimeError("Validation pipeline unexpectedly contains Albumentations training augmentation.")
    sample = train_dataset[0]
    sample_boxes = sample["bboxes"]
    if len(sample_boxes) != len(sample["cls"]) or not torch.all((sample_boxes >= 0) & (sample_boxes <= 1)):
        raise RuntimeError("Training-pipeline smoke sample contains invalid normalized boxes or labels.")

    print(f"{EXPERIMENT_ID} preflight passed")
    print("- E002 controls loaded from frozen args.yaml")
    print("- CoarseDropout injected into training only")
    print("- Validation pipeline has no Albumentations training transform")
    print("- Bounding boxes and class labels preserved by the actual Ultralytics wrapper")
    print("- Only training and validation paths were resolved; protected benchmarks were not accessed")


def execute_training() -> None:
    """Start E004 only after explicit caller authorization through the CLI flag."""
    from ultralytics import YOLO

    model = YOLO(MODEL_PATH)
    model.train(trainer=create_e004_trainer(), **build_training_overrides())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SafaiOS E004 CoarseDropout controlled experiment")
    parser.add_argument(
        "--execute-training",
        action="store_true",
        help="Explicitly start the 100-epoch E004 training run. Omit for safe preflight only.",
    )
    args = parser.parse_args(argv)
    if args.execute_training:
        execute_training()
    else:
        run_preflight()
        print("Training was not started. Re-run with --execute-training only after authorization.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
