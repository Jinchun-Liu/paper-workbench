#!/usr/bin/env python3
"""Guarded Full UA-MSTCN broad-service entrypoint.

Default behavior is preflight-only. A broad full-model run requires both
``--execute`` and ``--confirm-run-id full_ua_mstcn_broad_20260428``. The
preflight path does not create ``experiments/results/full_ua_mstcn_broad`` and
does not touch central ``metrics.csv``.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

import numpy as np
import torch
import yaml

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

import run_full_ua_mstcn_pilot as pilot


RUN_ID = "full_ua_mstcn_broad_20260428"
PREFLIGHT_RUN_ID = "full_ua_mstcn_broad_preflight_20260428"
MODEL_NAME = "full_ua_mstcn_broad"
EXPECTED_METRICS_HASH = "0fa3fdb810ca0a0f74592d3adc92102c7a0ca67ea02c2b8c8f22435537f873ab"


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


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"No rows to write for {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def read_service_names(service_csv: Path) -> list[str]:
    names = set()
    with service_csv.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            names.add(row["app_du"])
    return sorted(names)


def directory_size(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(item.stat().st_size for item in path.rglob("*") if item.is_file())


def load_inputs(args: argparse.Namespace, repo_root: Path) -> dict:
    config_path = resolve_path(args.config, repo_root)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    return {
        "config": config,
        "config_path": config_path,
        "service_csv": resolve_path(args.service_csv, repo_root),
        "service_summary_csv": resolve_path(args.service_summary_csv, repo_root),
        "approval_dir": resolve_path(args.approval_dir, repo_root),
        "output_dir": resolve_path(args.output_dir, repo_root),
        "preflight_output_dir": resolve_path(args.preflight_output_dir, repo_root),
        "metrics_path": resolve_path(Path(config["output"]["metrics_csv"]), repo_root),
    }


def preflight_checks(args: argparse.Namespace, repo_root: Path, paths: dict) -> tuple[list[str], dict, list[dict]]:
    output_dir = paths["output_dir"]
    preflight_dir = paths["preflight_output_dir"]
    preflight_dir.mkdir(parents=True, exist_ok=True)
    approval_status_path = paths["approval_dir"] / "full_ua_mstcn_broad_approval_status.json"
    approval_manifest_path = paths["approval_dir"] / "full_ua_mstcn_broad_execution_manifest.csv"
    approval_status = json.loads(approval_status_path.read_text(encoding="utf-8"))
    approval_manifest = read_csv_rows(approval_manifest_path)
    service_names = read_service_names(paths["service_csv"])
    service_summary_rows = read_csv_rows(paths["service_summary_csv"])
    summary_names = {row["app_du"] for row in service_summary_rows}
    manifest_names = {row["app_du"] for row in approval_manifest}
    metrics_hash = sha256_file(paths["metrics_path"])
    resource = pilot.resource_snapshot(repo_root)
    estimates = approval_status.get("estimates", {})

    failures: list[str] = []
    if approval_status.get("status") != "pass":
        failures.append("approval package status is not pass")
    if approval_status.get("full_broad_run_executed") is not False:
        failures.append("approval status does not record full_broad_run_executed=false")
    if len(approval_manifest) != 139:
        failures.append(f"approval manifest has {len(approval_manifest)} rows, expected 139")
    if len(service_names) != 139:
        failures.append(f"service CSV has {len(service_names)} services, expected 139")
    if manifest_names != set(service_names):
        failures.append("approval manifest service set does not match service CSV")
    if not set(service_names).issubset(summary_names):
        failures.append("service summary is missing one or more broad services")
    if output_dir.exists():
        failures.append(f"full output directory already exists: {output_dir}")
    if metrics_hash.lower() != EXPECTED_METRICS_HASH:
        failures.append("metrics.csv hash does not match frozen reference")
    if not torch.cuda.is_available():
        failures.append("CUDA is not available for the planned broad Full UA-MSTCN run")
    if int(approval_status.get("target_batch_size", 0)) != int(args.batch_size):
        failures.append("requested batch size does not match approved target batch size")
    free_disk = int(resource["drive_free_bytes"]) if str(resource.get("drive_free_bytes", "")).isdigit() else 0
    estimated_artifact_bytes = int(estimates.get("safety_adjusted_artifact_bytes", 0))
    if free_disk and estimated_artifact_bytes and estimated_artifact_bytes > free_disk:
        failures.append("estimated artifacts exceed current free disk")

    manifest_rows = []
    for row in approval_manifest:
        manifest_rows.append(
            {
                "run_id": PREFLIGHT_RUN_ID,
                "app_du": row["app_du"],
                "row_count": row["row_count"],
                "train_end": row["train_end"],
                "valid_end": row["valid_end"],
                "planned_train_windows": row["planned_train_windows"],
                "planned_validation_windows": row["planned_validation_windows"],
                "planned_prediction_rows": row["planned_prediction_rows"],
                "batch_size": args.batch_size,
                "max_epochs": args.max_epochs,
                "patience": args.patience,
                "test_use": "held-out evaluation only",
                "selection_rule": "all 139 broad services; no service selection by test performance",
            }
        )
    write_csv(preflight_dir / "full_ua_mstcn_broad_preflight_manifest.csv", manifest_rows)

    status = {
        "run_id": PREFLIGHT_RUN_ID,
        "status": "pass" if not failures else "fail",
        "scope": "preflight only; no broad Full UA-MSTCN training executed",
        "approval_status_path": str(approval_status_path),
        "approval_manifest_path": str(approval_manifest_path),
        "service_count": len(service_names),
        "manifest_count": len(approval_manifest),
        "batch_size": int(args.batch_size),
        "max_epochs": int(args.max_epochs),
        "patience": int(args.patience),
        "metrics_csv_hash": metrics_hash,
        "full_output_dir": str(output_dir),
        "full_output_dir_exists": output_dir.exists(),
        "preflight_output_dir": str(preflight_dir),
        "test_split_use": "held-out evaluation only; fitting uses train prefix and calibration/early stopping uses validation prefix",
        "resource": resource,
        "approval_estimates": estimates,
        "gate_failures": failures,
        "full_broad_run_executed": False,
        "metrics_csv_updated": False,
    }
    (preflight_dir / "full_ua_mstcn_broad_preflight_status.json").write_text(
        json.dumps(status, indent=2), encoding="utf-8"
    )
    report_lines = [
        "# Full UA-MSTCN Broad Guarded Preflight",
        "",
        f"- run_id: `{PREFLIGHT_RUN_ID}`",
        f"- status: `{status['status']}`",
        "- scope: preflight only; no broad Full UA-MSTCN training executed",
        f"- service_count: `{len(service_names)}`",
        f"- approval_manifest_count: `{len(approval_manifest)}`",
        f"- batch_size: `{args.batch_size}`",
        f"- max_epochs: `{args.max_epochs}`",
        f"- patience: `{args.patience}`",
        f"- metrics_csv_hash: `{metrics_hash}`",
        f"- full_output_dir_exists: `{output_dir.exists()}`",
        f"- preflight_artifact_bytes: `{directory_size(preflight_dir)}`",
        "",
        "## Boundary",
        "",
        "This is a guarded entrypoint preflight. It does not train the broad model, does not create the full output directory, and does not update central `metrics.csv`.",
        "The held-out test split is reserved for evaluation only; fitting uses train prefix and calibration/early stopping uses validation prefix.",
        "",
        "## Future Execute Command",
        "",
        "```powershell",
        "& 'C:\\Users\\Liu Jinchun\\miniconda3\\envs\\lora-cheongsam\\python.exe' experiments\\run_full_ua_mstcn_broad.py --config experiments\\configs\\default_v2018.yaml --execute --confirm-run-id full_ua_mstcn_broad_20260428",
        "```",
        "",
        "## Gate Result",
        "",
    ]
    if failures:
        report_lines.extend(f"- FAIL: {failure}" for failure in failures)
    else:
        report_lines.append("- PASS: guarded broad-run entrypoint preflight passed; no full run was executed.")
    (preflight_dir / "full_ua_mstcn_broad_preflight_report.md").write_text(
        "\n".join(report_lines) + "\n", encoding="utf-8"
    )
    return failures, status, manifest_rows


def execute_broad_run(args: argparse.Namespace, repo_root: Path, paths: dict) -> None:
    if args.confirm_run_id != RUN_ID:
        raise SystemExit(f"Refusing execution without --confirm-run-id {RUN_ID}")
    failures, _status, _manifest = preflight_checks(args, repo_root, paths)
    if failures:
        raise SystemExit("; ".join(failures))

    output_dir = paths["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=False)
    config = paths["config"]
    metrics_path = paths["metrics_path"]
    metrics_hash_before = sha256_file(metrics_path)
    census_before = pilot.resource_snapshot(repo_root)
    service_names = read_service_names(paths["service_csv"])

    np.random.seed(int(args.seed))
    torch.manual_seed(int(args.seed))
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(int(args.seed))
        torch.cuda.reset_peak_memory_stats()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    horizons = tuple(int(value) for value in config["forecast"]["horizons"])
    policy_config = config["policy"]
    service_values = pilot.read_service_series(paths["service_csv"], service_names)
    service_summary = pilot.read_service_summary(paths["service_summary_csv"])
    selection_roles = {app_du: "broad_service" for app_du in service_names}
    pilot.RUN_ID = RUN_ID
    pilot.MODEL_NAME = MODEL_NAME
    profile, forecast, predictions, calibration, policy_rows, policy_series, resource = pilot.run_scope(
        scope="service_broad",
        series_by_entity={app_du: service_values[app_du] for app_du in service_names},
        selection_roles=selection_roles,
        context_window=int(config["forecast"]["context_window"]),
        horizons=horizons,
        train_ratio=float(config["forecast"]["train_ratio"]),
        valid_ratio=float(config["forecast"]["valid_ratio"]),
        policy_config=policy_config,
        service_summary=service_summary,
        hidden_width=int(args.hidden_width),
        dilations=(1, 2, 4, 8, 16),
        batch_size=int(args.batch_size),
        max_epochs=int(args.max_epochs),
        patience=int(args.patience),
        device=device,
    )
    write_csv(output_dir / "full_ua_mstcn_broad_selection_profile.csv", profile)
    write_csv(output_dir / "full_ua_mstcn_broad_forecasting_metrics.csv", forecast)
    write_csv(output_dir / "full_ua_mstcn_broad_predictions.csv", predictions)
    write_csv(output_dir / "full_ua_mstcn_broad_calibration.csv", calibration)
    write_csv(output_dir / "full_ua_mstcn_broad_policy_metrics.csv", policy_rows)
    write_csv(output_dir / "full_ua_mstcn_broad_policy_series.csv", policy_series)
    write_csv(output_dir / "full_ua_mstcn_broad_resource_trace.csv", [resource])

    metrics_hash_after = sha256_file(metrics_path)
    gate_failures = []
    if len(profile) != 139:
        gate_failures.append(f"profile has {len(profile)} services, expected 139")
    if any(row["status"] != "pass" for row in forecast):
        gate_failures.append("one or more forecasting rows failed")
    if sum(int(row["calibrated_crossing_count"]) for row in forecast) != 0:
        gate_failures.append("calibrated P90 crossing count is nonzero")
    if not pilot.rows_numeric_finite(forecast):
        gate_failures.append("forecast metrics contain non-finite values")
    if not pilot.rows_numeric_finite(policy_rows):
        gate_failures.append("policy metrics contain non-finite values")
    if any(not (0.0 <= float(row["sla_violation"]) <= 1.0) for row in policy_rows):
        gate_failures.append("policy SLA violation outside [0, 1]")
    for column in ["reactive_capacity", "lagged_capacity", "predictive_capacity"]:
        if any(float(row[column]) < 0.0 for row in policy_series):
            gate_failures.append(f"{column} contains negative values")
    if metrics_hash_before != metrics_hash_after:
        gate_failures.append("central metrics.csv changed")

    status = {
        "run_id": RUN_ID,
        "status": "pass" if not gate_failures else "fail",
        "scope": "broad Full UA-MSTCN service run",
        "service_count": len(profile),
        "output_dir": str(output_dir),
        "seed": int(args.seed),
        "batch_size": int(args.batch_size),
        "max_epochs": int(args.max_epochs),
        "patience": int(args.patience),
        "test_split_use": "held-out evaluation only; fitting uses train prefix and calibration/early stopping uses validation prefix",
        "metrics_csv_hash_before": metrics_hash_before,
        "metrics_csv_hash_after": metrics_hash_after,
        "resource_before": census_before,
        "resource_after": pilot.resource_snapshot(repo_root),
        "resource_trace": resource,
        "gate_failures": gate_failures,
        "metrics_csv_updated": False,
    }
    (output_dir / "full_ua_mstcn_broad_status.json").write_text(json.dumps(status, indent=2), encoding="utf-8")
    report_lines = [
        "# Full UA-MSTCN Broad Report",
        "",
        f"- run_id: `{RUN_ID}`",
        f"- status: `{status['status']}`",
        f"- service_count: `{len(profile)}`",
        "- test split use: held-out evaluation only; fitting uses train prefix and calibration/early stopping uses validation prefix.",
        f"- metrics_csv_hash_before: `{metrics_hash_before}`",
        f"- metrics_csv_hash_after: `{metrics_hash_after}`",
        "",
        "## Gate Result",
        "",
    ]
    if gate_failures:
        report_lines.extend(f"- FAIL: {failure}" for failure in gate_failures)
    else:
        report_lines.append("- PASS: broad Full UA-MSTCN gate passed.")
    report_lines.extend(["", "## Resource Trace", "", "```csv", ",".join(resource.keys())])
    report_lines.append(",".join(str(resource[key]) for key in resource.keys()))
    report_lines.extend(["```", ""])
    (output_dir / "full_ua_mstcn_broad_report.md").write_text("\n".join(report_lines), encoding="utf-8")
    if gate_failures:
        raise SystemExit(f"Broad Full UA-MSTCN gate failed; see {output_dir / 'full_ua_mstcn_broad_report.md'}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("experiments/configs/default_v2018.yaml"))
    parser.add_argument("--service-csv", type=Path, default=Path("data/processed/service_cohort_broad_v2018.csv"))
    parser.add_argument(
        "--service-summary-csv",
        type=Path,
        default=Path("data/processed/service_cohort_broad_summary_v2018.csv"),
    )
    parser.add_argument(
        "--approval-dir",
        type=Path,
        default=Path("experiments/results/full_ua_mstcn_broad_approval"),
    )
    parser.add_argument(
        "--preflight-output-dir",
        type=Path,
        default=Path("experiments/results/full_ua_mstcn_broad_preflight"),
    )
    parser.add_argument("--output-dir", type=Path, default=Path("experiments/results/full_ua_mstcn_broad"))
    parser.add_argument("--batch-size", type=int, default=1024)
    parser.add_argument("--max-epochs", type=int, default=20)
    parser.add_argument("--patience", type=int, default=4)
    parser.add_argument("--hidden-width", type=int, default=64)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--confirm-run-id", type=str, default="")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    paths = load_inputs(args, repo_root)
    if args.execute:
        execute_broad_run(args, repo_root, paths)
        return
    failures, _status, _manifest = preflight_checks(args, repo_root, paths)
    if failures:
        raise SystemExit("; ".join(failures))


if __name__ == "__main__":
    main()
