from types import SimpleNamespace

import pytest

from scripts import train_e004_coarsedropout as e004


def test_e004_transform_matches_frozen_protocol():
    transform = e004.build_coarse_dropout()
    assert transform.num_holes_range == (1, 2)
    assert transform.hole_height_range == (0.08, 0.18)
    assert transform.hole_width_range == (0.08, 0.18)
    assert transform.fill == (114.0, 114.0, 114.0)
    assert transform.p == 0.5


def test_e004_controls_are_loaded_from_frozen_e002_args():
    controls = e004.load_e002_controls()
    overrides = e004.build_training_overrides()
    for key, value in controls.items():
        assert overrides[key] == value
    assert overrides["model"] == "yolo11s.pt"
    assert overrides["imgsz"] == 768
    assert overrides["batch"] == 16
    assert overrides["optimizer"] == "MuSGD"
    assert overrides["resume"] is False
    assert overrides["exist_ok"] is False


def test_trainer_injects_augmentation_only_for_train(monkeypatch):
    trainer_type = e004.create_e004_trainer()
    trainer = object.__new__(trainer_type)
    trainer.args = SimpleNamespace()

    from ultralytics.models.yolo.detect import DetectionTrainer

    calls = []

    def fake_build_dataset(self, img_path, mode="train", batch=None):
        calls.append((img_path, mode, batch))
        return mode

    monkeypatch.setattr(DetectionTrainer, "build_dataset", fake_build_dataset)
    assert trainer.build_dataset("train-images", mode="train", batch=16) == "train"
    assert trainer.args.augmentations[0].__class__.__name__ == "CoarseDropout"
    del trainer.args.augmentations
    assert trainer.build_dataset("validation-images", mode="val", batch=16) == "val"
    assert not hasattr(trainer.args, "augmentations")
    assert calls == [("train-images", "train", 16), ("validation-images", "val", 16)]


def test_training_requires_explicit_flag(monkeypatch):
    called = []
    monkeypatch.setattr(e004, "run_preflight", lambda: called.append("preflight"))
    monkeypatch.setattr(e004, "execute_training", lambda: called.append("training"))
    assert e004.main([]) == 0
    assert called == ["preflight"]
    assert e004.main(["--execute-training"]) == 0
    assert called == ["preflight", "training"]
