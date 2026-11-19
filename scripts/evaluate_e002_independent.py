"""One-time independent evaluation of the frozen E002 checkpoint.

This runner never imports or invokes the E003 evaluation main routine. It fixes
the E002 checkpoint and frozen inference thresholds, evaluates each protected
benchmark once, and refuses to overwrite an existing evaluation directory.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WEIGHTS = ROOT / "runs/detect/runs/detect/runs/safaios/safaios_yolo11s_v10k_img768/weights/best.pt"
EXPECTED_SHA256 = "8bd30b05a0b4a84d95c5e71f213b967d255144a8fe57791ef110b920fc86d073"
OUTPUT = ROOT / "reports/evaluations/SAFAIOS-E002-independent"
BENCHMARKS = {
    "test_locked_v2": ROOT / "data/safaios_dataset_v10k/test_locked_v2",
    "india_real_world": ROOT / "data/india_real_world",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_helpers():
    """Load only pure matching helpers; the E003 main routine is never called."""
    spec = importlib.util.spec_from_file_location("safaios_matching_helpers", ROOT / "scripts/evaluate_e003.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def evaluate(name: str, root: Path, model, helpers, cfg: dict) -> dict:
    images, labels = root / "images", root / "labels"
    if not images.is_dir() or not labels.is_dir():
        raise FileNotFoundError(f"{name} is missing images or labels")
    data_yaml = OUTPUT / f"{name}.yaml"
    data_yaml.write_text(yaml.safe_dump({"path": str(root), "train": "images", "val": "images", "nc": 5, "names": cfg["taxonomy"]}), encoding="utf-8")
    metrics = model.val(data=str(data_yaml), split="val", imgsz=cfg["model"]["imgsz"], batch=16, device=cfg["model"]["device"], plots=True, project=str(OUTPUT), name=f"official_{name}", exist_ok=False, verbose=False)
    helpers.VAL_IMAGES_DIR, helpers.VAL_LABELS_DIR = images, labels
    gt = helpers.load_ground_truth()
    predictions = helpers.run_model_inference(model, imgsz=cfg["model"]["imgsz"], conf_thresh=cfg["thresholds"]["confidence"], iou_thresh=cfg["thresholds"]["iou_nms"])
    operational = helpers.match_and_analyze(gt, predictions, iou_thresh=cfg["thresholds"]["greedy_matching_iou"])
    return {
        "benchmark": name, "images": len(gt), "ground_truth": operational["total_gt"],
        "official": {"precision": float(metrics.box.mp), "recall": float(metrics.box.mr), "map50": float(metrics.box.map50), "map50_95": float(metrics.box.map), "per_class": {helpers.TAXONOMY[i]: {"precision": float(metrics.box.p[i]), "recall": float(metrics.box.r[i]), "map50": float(metrics.box.ap50[i]), "map50_95": float(metrics.box.ap[i])} for i in range(5)}},
        "operational": operational,
        "representative_successes": [item for item in operational["failure_cases"]["false_negatives"][:0]],
        "representative_failures": {key: values[:5] for key, values in operational["failure_cases"].items()},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute-independent-evaluation", action="store_true")
    args = parser.parse_args()
    if not args.execute_independent_evaluation:
        raise SystemExit("Refusing protected-benchmark access without --execute-independent-evaluation.")
    if OUTPUT.exists():
        raise SystemExit(f"Refusing to overwrite existing evaluation output: {OUTPUT}")
    if sha256(WEIGHTS) != EXPECTED_SHA256:
        raise SystemExit("Frozen E002 checkpoint SHA-256 mismatch.")
    cfg = yaml.safe_load((ROOT / "configs/inference.yaml").read_text(encoding="utf-8"))
    if Path(cfg["model"]["weights"]).as_posix() != WEIGHTS.relative_to(ROOT).as_posix():
        raise SystemExit("Inference config does not select the frozen E002 checkpoint.")
    OUTPUT.mkdir(parents=True)
    helpers = load_helpers()
    from ultralytics import YOLO
    model = YOLO(str(WEIGHTS))
    report = {"checkpoint": str(WEIGHTS.relative_to(ROOT)), "checkpoint_sha256": EXPECTED_SHA256, "configuration": cfg, "benchmarks": {}}
    for name, root in BENCHMARKS.items():
        report["benchmarks"][name] = evaluate(name, root, model, helpers, cfg)
        (OUTPUT / f"{name}.json").write_text(json.dumps(report["benchmarks"][name], indent=2), encoding="utf-8")
    (OUTPUT / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT), "checkpoint_sha256": EXPECTED_SHA256, "benchmarks": list(report["benchmarks"])}, indent=2))

if __name__ == "__main__":
    main()
