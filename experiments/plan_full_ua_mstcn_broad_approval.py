#!/usr/bin/env python3
"""Create an approval-only package for a possible Full UA-MSTCN broad run.

This script is deliberately plan-only. It reads the completed broad calibration
slice and pilot artifacts, estimates a future 139-service run, and writes
approval/preflight documents. It never imports model code and never trains.
"""

from __future__ import annotations

import argparse
import csv
import ctypes
import hashlib
import json
import math
import os
import platform
import shutil
import sys
from pathlib import Path

import yaml


RUN_ID = "full_ua_mstcn_broad_approval_20260428"
METRICS_HASH_EXPECTED = "0fa3fdb810ca0a0f74592d3adc92102c7a0ca67ea02c2b8c8f22435537f873ab"
FULL_RESULT_DIR_NAME = "full_ua_mstcn_broad"


def resolve_path(path: Path, repo_root: Path) -> Path:
    if path.is_absolute():
        return path
    if path.parts and path.parts[0] == repo_root.name:
        return repo_root.parent.joinpath(path)
    return repo_root.joinpath(path)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def windows_memory_status() -> tuple[int | None, int | None]:
    if os.name != "nt":
        return None, None

    class MemoryStatusEx(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    status = MemoryStatusEx()
    status.dwLength = ctypes.sizeof(MemoryStatusEx)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):  # type: ignore[attr-defined]
        return None, None
    return int(status.ullTotalPhys), int(status.ullAvailPhys)


def resource_census(repo_root: Path) -> dict:
    total_disk, used_disk, free_disk = shutil.disk_usage(repo_root.anchor or repo_root)
    total_mem, free_mem = windows_memory_status()
    return {
        "os": platform.platform(),
        "python": sys.version.replace("\n", " "),
        "logical_cpu_count": os.cpu_count() or "",
        "total_memory_bytes": total_mem or "",
        "free_memory_bytes": free_mem or "",
        "workspace_drive": repo_root.anchor,
        "drive_total_bytes": total_disk,
        "drive_used_bytes": used_disk,
        "drive_free_bytes": free_disk,
    }


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"No rows to write for {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def count_csv_data_rows(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8", newline="") as handle:
        return max(0, sum(1 for _line in handle) - 1)


def directory_size(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(item.stat().st_size for item in path.rglob("*") if item.is_file())


def parse_horizons(config: dict) -> tuple[int, ...]:
    return tuple(int(value) for value in config["forecast"]["horizons"])


def finite_float(value: object) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def pick_calibration_row(rows: list[dict[str, str]], target_batch_size: int) -> dict[str, str]:
    for row in rows:
        if int(row["batch_size"]) == int(target_batch_size):
            return row
    raise ValueError(f"Calibration results do not contain batch_size={target_batch_size}")


def build_manifest(
    calibration_manifest: list[dict[str, str]],
    *,
    config: dict,
    full_result_dir: Path,
    target_batch_size: int,
    max_epochs: int,
    patience: int,
    hidden_width: int,
) -> list[dict]:
    context_window = int(config["forecast"]["context_window"])
    horizons = parse_horizons(config)
    max_horizon = max(horizons)
    rows = []
    for row in calibration_manifest:
        row_count = int(row["row_count"])
        train_end = int(row["train_end"])
        valid_end = int(row["valid_end"])
        train_windows = max(0, train_end - context_window - max_horizon + 1)
        validation_windows = max(0, valid_end - train_end - max_horizon + 1)
        test_windows_by_horizon = {
            f"test_windows_h{horizon}": max(0, row_count - valid_end - horizon + 1)
            for horizon in horizons
        }
        prediction_rows = sum(test_windows_by_horizon.values())
        rows.append(
            {
                "run_id": RUN_ID,
                "app_du": row["app_du"],
                "entity_id": int(row["entity_id"]),
                "row_count": row_count,
                "train_end": train_end,
                "valid_end": valid_end,
                "context_window": context_window,
                "horizons": ";".join(str(horizon) for horizon in horizons),
                "planned_train_windows": train_windows,
                "planned_validation_windows": validation_windows,
                **test_windows_by_horizon,
                "planned_prediction_rows": prediction_rows,
                "planned_batch_size": target_batch_size,
                "planned_hidden_width": hidden_width,
                "planned_max_epochs": max_epochs,
                "planned_patience": patience,
                "normalization_source": "train prefix only",
                "validation_use": "early stopping and calibration only",
                "test_use": "held-out evaluation only",
                "planned_predictions_output": str(full_result_dir / "full_ua_mstcn_broad_predictions.csv"),
                "planned_forecasting_metrics_output": str(
                    full_result_dir / "full_ua_mstcn_broad_forecasting_metrics.csv"
                ),
                "planned_calibration_output": str(full_result_dir / "full_ua_mstcn_broad_calibration.csv"),
                "planned_policy_metrics_output": str(full_result_dir / "full_ua_mstcn_broad_policy_metrics.csv"),
                "planned_policy_series_output": str(full_result_dir / "full_ua_mstcn_broad_policy_series.csv"),
                "planned_resource_trace_output": str(full_result_dir / "full_ua_mstcn_broad_resource_trace.csv"),
                "planned_report_output": str(full_result_dir / "full_ua_mstcn_broad_report.md"),
            }
        )
    return sorted(rows, key=lambda item: item["app_du"])


def estimate_resources(
    *,
    manifest_rows: list[dict],
    calibration_status: dict,
    calibration_row: dict[str, str],
    pilot_dir: Path,
    calibration_dir: Path,
    max_epochs: int,
    safety_factor: float,
) -> dict:
    train_windows_total = sum(int(row["planned_train_windows"]) for row in manifest_rows)
    validation_windows_total = sum(int(row["planned_validation_windows"]) for row in manifest_rows)
    prediction_rows_total = sum(int(row["planned_prediction_rows"]) for row in manifest_rows)

    train_throughput = float(calibration_row["train_windows_per_second"])
    sampled_validation_windows = int(calibration_status["validation_windows"])
    validation_runtime = max(float(calibration_row["validation_runtime_seconds"]), 1e-9)
    validation_throughput = sampled_validation_windows / validation_runtime

    train_seconds_per_epoch = train_windows_total / max(train_throughput, 1e-9)
    validation_seconds_per_epoch = validation_windows_total / max(validation_throughput, 1e-9)
    test_eval_seconds = prediction_rows_total / max(validation_throughput, 1e-9)
    lower_bound_seconds = (
        train_seconds_per_epoch * max_epochs
        + validation_seconds_per_epoch * max_epochs
        + test_eval_seconds
    )

    pilot_bytes = directory_size(pilot_dir)
    pilot_prediction_rows = count_csv_data_rows(pilot_dir / "full_ua_mstcn_pilot_predictions.csv")
    if pilot_prediction_rows:
        artifact_bytes_from_pilot = int((pilot_bytes / pilot_prediction_rows) * prediction_rows_total)
    else:
        artifact_bytes_from_pilot = 0
    calibration_bytes = directory_size(calibration_dir)
    artifact_bytes_floor = max(artifact_bytes_from_pilot, calibration_bytes * 4, 50 * 1024 * 1024)

    return {
        "train_windows_total": train_windows_total,
        "validation_windows_total": validation_windows_total,
        "prediction_rows_total": prediction_rows_total,
        "train_throughput_windows_per_second": train_throughput,
        "validation_throughput_windows_per_second": validation_throughput,
        "train_seconds_per_epoch_estimate": train_seconds_per_epoch,
        "validation_seconds_per_epoch_estimate": validation_seconds_per_epoch,
        "test_eval_seconds_estimate": test_eval_seconds,
        "lower_bound_wall_seconds": lower_bound_seconds,
        "safety_adjusted_wall_seconds": lower_bound_seconds * safety_factor,
        "pilot_artifact_bytes": pilot_bytes,
        "pilot_prediction_rows": pilot_prediction_rows,
        "artifact_bytes_from_pilot_density": artifact_bytes_from_pilot,
        "artifact_bytes_floor": artifact_bytes_floor,
        "safety_adjusted_artifact_bytes": int(artifact_bytes_floor * safety_factor),
    }


def write_approval(
    output_dir: Path,
    *,
    manifest_rows: list[dict],
    calibration_status: dict,
    calibration_row: dict[str, str],
    calibration_dir: Path,
    pilot_dir: Path,
    full_result_dir: Path,
    metrics_hash_before: str,
    metrics_hash_after: str,
    census: dict,
    estimates: dict,
    target_batch_size: int,
    max_epochs: int,
    patience: int,
    safety_factor: float,
) -> None:
    service_count = len(manifest_rows)
    minutes = estimates["safety_adjusted_wall_seconds"] / 60.0
    artifact_mb = estimates["safety_adjusted_artifact_bytes"] / (1024 * 1024)
    conservative_batch = min(int(row["batch_size"]) for row in read_csv_rows(calibration_dir / "full_ua_mstcn_broad_calibration_results.csv"))
    lines = [
        "# Full UA-MSTCN Broad Full-Run Approval Package",
        "",
        f"- run_id: `{RUN_ID}`",
        "- status: `approval_plan_only`",
        "- approval planning only; no broad Full UA-MSTCN run executed",
        f"- service_count: `{service_count}`",
        f"- calibration_dir: `{calibration_dir}`",
        f"- pilot_dir: `{pilot_dir}`",
        f"- planned_full_result_dir: `{full_result_dir}`",
        f"- planned_full_result_dir_exists: `{full_result_dir.exists()}`",
        f"- metrics_csv_hash_before: `{metrics_hash_before}`",
        f"- metrics_csv_hash_after: `{metrics_hash_after}`",
        "",
        "## Approval Boundary",
        "",
        "Calibration pass is not automatic approval. This package is an execution review artifact only.",
        "No broad Full UA-MSTCN forecasting, policy, or superiority claim is supported by this artifact.",
        "The manuscript headline conclusion remains unchanged, and mixed or negative future results must be preserved.",
        "",
        "## Batch And Runtime Recommendation",
        "",
        f"- recommended_batch_size_from_calibration: `{target_batch_size}`",
        f"- conservative_validation_loss_batch_size: `{conservative_batch}`",
        f"- planned_max_epochs: `{max_epochs}`",
        f"- planned_patience: `{patience}`",
        f"- calibration_train_throughput_windows_per_second: `{float(calibration_row['train_windows_per_second']):.1f}`",
        f"- calibration_peak_cuda_memory_bytes: `{int(float(calibration_row['peak_cuda_memory_bytes']))}`",
        f"- planned_train_windows_total: `{estimates['train_windows_total']}`",
        f"- planned_validation_windows_total: `{estimates['validation_windows_total']}`",
        f"- planned_prediction_rows_total: `{estimates['prediction_rows_total']}`",
        f"- safety_adjusted_wall_minutes_estimate: `{minutes:.1f}`",
        f"- safety_adjusted_artifact_mb_estimate: `{artifact_mb:.1f}`",
        f"- safety_factor: `{safety_factor}`",
        "",
        "## Current Resource Census",
        "",
    ]
    for key, value in census.items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## Required Execution Rules",
            "",
            "- Require explicit approval immediately before the broad full-model run.",
            "- Re-check CPU, RAM, disk, CUDA availability, metrics hash, and output directory absence before execution.",
            "- Use train prefix for fitting and validation prefix for early stopping/calibration.",
            "- Use the held-out test split only for evaluation.",
            "- Preserve raw P50/P90, calibrated or guarded P90, crossing diagnostics, calibration margins, and policy series.",
            "- Reuse the existing service policy semantics, including service min_capacity=1.0 and max_step_change=1.0.",
            "- Use median_container_request_cores only for replica conversion, with mean fallback only when median is non-positive.",
            "- Do not update central `metrics.csv` from the broad service Full UA-MSTCN run.",
            "- Do not change manuscript conclusions until a separate evidence-to-claim pass is approved.",
        ]
    )
    (output_dir / "full_ua_mstcn_broad_execution_approval.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def write_resource_update(output_dir: Path, *, estimates: dict, calibration_row: dict[str, str], safety_factor: float) -> None:
    lines = [
        "# Full UA-MSTCN Broad Resource Update From Calibration",
        "",
        f"- run_id: `{RUN_ID}`",
        "- estimate_source: `full_ua_mstcn_broad_calibration_results.csv` plus pilot artifact density",
        f"- selected_batch_size: `{calibration_row['batch_size']}`",
        f"- selected_validation_loss: `{float(calibration_row['validation_loss']):.6f}`",
        f"- selected_peak_cuda_memory_bytes: `{int(float(calibration_row['peak_cuda_memory_bytes']))}`",
        f"- train_windows_total: `{estimates['train_windows_total']}`",
        f"- validation_windows_total: `{estimates['validation_windows_total']}`",
        f"- prediction_rows_total: `{estimates['prediction_rows_total']}`",
        f"- train_seconds_per_epoch_estimate: `{estimates['train_seconds_per_epoch_estimate']:.2f}`",
        f"- validation_seconds_per_epoch_estimate: `{estimates['validation_seconds_per_epoch_estimate']:.2f}`",
        f"- test_eval_seconds_estimate: `{estimates['test_eval_seconds_estimate']:.2f}`",
        f"- lower_bound_wall_minutes: `{estimates['lower_bound_wall_seconds'] / 60.0:.1f}`",
        f"- safety_adjusted_wall_minutes: `{estimates['safety_adjusted_wall_seconds'] / 60.0:.1f}`",
        f"- pilot_artifact_bytes: `{estimates['pilot_artifact_bytes']}`",
        f"- pilot_prediction_rows: `{estimates['pilot_prediction_rows']}`",
        f"- artifact_bytes_from_pilot_density: `{estimates['artifact_bytes_from_pilot_density']}`",
        f"- safety_adjusted_artifact_bytes: `{estimates['safety_adjusted_artifact_bytes']}`",
        f"- safety_factor: `{safety_factor}`",
        "",
        "This estimate is for execution approval only. It is not a performance result.",
    ]
    (output_dir / "full_ua_mstcn_broad_resource_update_from_calibration.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def write_preflight(
    output_dir: Path,
    *,
    manifest_rows: list[dict],
    calibration_status: dict,
    calibration_row: dict[str, str],
    full_result_dir: Path,
    metrics_hash_before: str,
    metrics_hash_after: str,
    census: dict,
    estimates: dict,
) -> list[str]:
    failures: list[str] = []
    if len(manifest_rows) != 139:
        failures.append(f"manifest has {len(manifest_rows)} services, expected 139")
    if calibration_status.get("status") != "pass":
        failures.append("broad calibration status is not pass")
    if "no test windows are generated" not in str(calibration_status.get("test_split_use", "")):
        failures.append("calibration status does not prove the test split stayed untouched")
    if full_result_dir.exists():
        failures.append(f"full result directory already exists: {full_result_dir}")
    if metrics_hash_before != metrics_hash_after:
        failures.append("metrics.csv changed during approval planning")
    if metrics_hash_after.lower() != METRICS_HASH_EXPECTED:
        failures.append("metrics.csv hash no longer matches the frozen reference")
    if not finite_float(calibration_row.get("validation_loss")):
        failures.append("selected calibration validation loss is not finite")
    if int(float(calibration_row.get("peak_cuda_memory_bytes", "0"))) >= 12 * 1024**3:
        failures.append("selected calibration batch exceeds the 12GB CUDA gate")
    free_disk = int(census["drive_free_bytes"]) if str(census.get("drive_free_bytes", "")).isdigit() else 0
    if free_disk and int(estimates["safety_adjusted_artifact_bytes"]) > free_disk:
        failures.append("estimated artifacts exceed free disk")

    status = "pass" if not failures else "fail"
    lines = [
        "# Full UA-MSTCN Broad Preflight Checks",
        "",
        f"- run_id: `{RUN_ID}`",
        f"- status: `{status}`",
        "- approval planning only; no broad Full UA-MSTCN run executed",
        f"- manifest_service_count: `{len(manifest_rows)}`",
        f"- calibration_status: `{calibration_status.get('status')}`",
        f"- full_result_dir_exists: `{full_result_dir.exists()}`",
        f"- metrics_csv_hash_before: `{metrics_hash_before}`",
        f"- metrics_csv_hash_after: `{metrics_hash_after}`",
        "",
        "## Completed Checks",
        "",
        "- [x] Broad batch-size calibration completed before approval planning.",
        "- [x] Manifest covers the 139 broad services from the calibration slice.",
        "- [x] Approval script did not import model code or start training.",
        "- [x] Approval script did not generate held-out test windows.",
        "- [x] Central `metrics.csv` hash is unchanged.",
        "- [x] Full broad result directory was not created.",
        "",
        "## Required Before Any Future Full Run",
        "",
        "- [ ] Explicit approval for broad Full UA-MSTCN execution.",
        "- [ ] Guarded broad-run entrypoint implemented and syntax-checked.",
        "- [ ] Output directory absence, metrics hash, memory, disk, and CUDA rechecked immediately before launch.",
        "- [ ] Manuscript conclusions remain frozen until broad results pass a separate evidence-to-claim review.",
        "",
        "## Gate Result",
        "",
    ]
    if failures:
        lines.extend(f"- FAIL: {failure}" for failure in failures)
    else:
        lines.append("- PASS: approval package is complete and no broad full-model run was executed.")
    (output_dir / "full_ua_mstcn_broad_preflight_checks.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    return failures


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a Full UA-MSTCN broad full-run approval package. This script never trains models."
    )
    parser.add_argument("--config", type=Path, default=Path("experiments/configs/default_v2018.yaml"))
    parser.add_argument(
        "--calibration-dir",
        type=Path,
        default=Path("experiments/results/full_ua_mstcn_broad_calibration"),
    )
    parser.add_argument("--pilot-dir", type=Path, default=Path("experiments/results/full_ua_mstcn_pilot"))
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("experiments/results/full_ua_mstcn_broad_approval"),
    )
    parser.add_argument("--target-batch-size", type=int, default=None)
    parser.add_argument("--max-epochs", type=int, default=20)
    parser.add_argument("--patience", type=int, default=4)
    parser.add_argument("--safety-factor", type=float, default=2.0)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    config_path = resolve_path(args.config, repo_root)
    calibration_dir = resolve_path(args.calibration_dir, repo_root)
    pilot_dir = resolve_path(args.pilot_dir, repo_root)
    output_dir = resolve_path(args.output_dir, repo_root)
    full_result_dir = repo_root / "experiments" / "results" / FULL_RESULT_DIR_NAME
    if output_dir.resolve() == full_result_dir.resolve():
        raise SystemExit("Refusing to write approval artifacts into the full result directory")
    output_dir.mkdir(parents=True, exist_ok=True)

    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    metrics_path = resolve_path(Path(config["output"]["metrics_csv"]), repo_root)
    metrics_hash_before = sha256_file(metrics_path)

    status_path = calibration_dir / "full_ua_mstcn_broad_calibration_status.json"
    results_path = calibration_dir / "full_ua_mstcn_broad_calibration_results.csv"
    manifest_path = calibration_dir / "full_ua_mstcn_broad_calibration_manifest.csv"
    calibration_status = json.loads(status_path.read_text(encoding="utf-8"))
    calibration_results = read_csv_rows(results_path)
    calibration_manifest = read_csv_rows(manifest_path)
    target_batch_size = int(args.target_batch_size or calibration_status["recommended_batch_size"])
    calibration_row = pick_calibration_row(calibration_results, target_batch_size)
    hidden_width = int(float(calibration_row["hidden_width"]))
    manifest_rows = build_manifest(
        calibration_manifest,
        config=config,
        full_result_dir=full_result_dir,
        target_batch_size=target_batch_size,
        max_epochs=int(args.max_epochs),
        patience=int(args.patience),
        hidden_width=hidden_width,
    )
    write_csv(output_dir / "full_ua_mstcn_broad_execution_manifest.csv", manifest_rows)

    estimates = estimate_resources(
        manifest_rows=manifest_rows,
        calibration_status=calibration_status,
        calibration_row=calibration_row,
        pilot_dir=pilot_dir,
        calibration_dir=calibration_dir,
        max_epochs=int(args.max_epochs),
        safety_factor=float(args.safety_factor),
    )
    census = resource_census(repo_root)
    metrics_hash_after = sha256_file(metrics_path)

    write_approval(
        output_dir,
        manifest_rows=manifest_rows,
        calibration_status=calibration_status,
        calibration_row=calibration_row,
        calibration_dir=calibration_dir,
        pilot_dir=pilot_dir,
        full_result_dir=full_result_dir,
        metrics_hash_before=metrics_hash_before,
        metrics_hash_after=metrics_hash_after,
        census=census,
        estimates=estimates,
        target_batch_size=target_batch_size,
        max_epochs=int(args.max_epochs),
        patience=int(args.patience),
        safety_factor=float(args.safety_factor),
    )
    write_resource_update(
        output_dir,
        estimates=estimates,
        calibration_row=calibration_row,
        safety_factor=float(args.safety_factor),
    )
    failures = write_preflight(
        output_dir,
        manifest_rows=manifest_rows,
        calibration_status=calibration_status,
        calibration_row=calibration_row,
        full_result_dir=full_result_dir,
        metrics_hash_before=metrics_hash_before,
        metrics_hash_after=metrics_hash_after,
        census=census,
        estimates=estimates,
    )
    status = {
        "run_id": RUN_ID,
        "status": "pass" if not failures else "fail",
        "scope": "approval planning only; no broad Full UA-MSTCN run executed",
        "output_dir": str(output_dir),
        "service_count": len(manifest_rows),
        "target_batch_size": target_batch_size,
        "max_epochs": int(args.max_epochs),
        "patience": int(args.patience),
        "metrics_csv_hash_before": metrics_hash_before,
        "metrics_csv_hash_after": metrics_hash_after,
        "full_broad_run_executed": False,
        "full_result_dir_exists": full_result_dir.exists(),
        "resource_census": census,
        "estimates": estimates,
        "gate_failures": failures,
    }
    (output_dir / "full_ua_mstcn_broad_approval_status.json").write_text(
        json.dumps(status, indent=2), encoding="utf-8"
    )
    if failures:
        raise SystemExit("; ".join(failures))


if __name__ == "__main__":
    main()
