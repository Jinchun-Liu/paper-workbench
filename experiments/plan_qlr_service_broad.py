#!/usr/bin/env python3
"""Create a plan-only manifest for a future 139-service QLR run."""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import os
import platform
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import yaml


RUN_ID = "qlr_service_broad_plan_20260427"


def resolve_workbench_path(path: str | Path, repo_root: Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute() or candidate.exists():
        return candidate
    parts = candidate.parts
    if parts and parts[0] == repo_root.name:
        return repo_root.parent / candidate
    return repo_root / candidate


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
        "python": platform.python_version(),
        "logical_cpu_count": os.cpu_count() or "",
        "total_memory_bytes": total_mem or "",
        "free_memory_bytes": free_mem or "",
        "workspace_drive": repo_root.anchor,
        "drive_total_bytes": total_disk,
        "drive_used_bytes": used_disk,
        "drive_free_bytes": free_disk,
    }


def request_source(row: pd.Series) -> str:
    median_value = float(row["median_container_request_cores"])
    return "median_container_request_cores" if median_value > 0.0 else "mean_container_request_cores"


def request_value(row: pd.Series) -> float:
    source = request_source(row)
    return max(float(row[source]), 0.1)


def load_pilot_estimates(pilot_dir: Path, safety_factor: float) -> dict:
    forecast_path = pilot_dir / "service_qlr_forecasting_raw.csv"
    if not forecast_path.exists():
        raise FileNotFoundError(f"Missing pilot forecasting artifact: {forecast_path}")
    forecast_df = pd.read_csv(forecast_path)
    per_service_ms = forecast_df.groupby("app_du")["fit_eval_ms"].sum()
    csv_bytes = sum(path.stat().st_size for path in pilot_dir.glob("*.csv"))
    service_count = int(forecast_df["app_du"].nunique())
    return {
        "pilot_service_count": service_count,
        "pilot_total_fit_eval_ms": float(forecast_df["fit_eval_ms"].sum()),
        "pilot_mean_fit_eval_ms_per_service": float(per_service_ms.mean()),
        "pilot_max_fit_eval_ms_per_service": float(per_service_ms.max()),
        "pilot_csv_bytes": int(csv_bytes),
        "estimated_csv_bytes_per_service": float(csv_bytes / max(service_count, 1)),
        "safety_factor": float(safety_factor),
    }


def build_manifest(
    service_csv: Path,
    summary_csv: Path,
    output_dir: Path,
    config: dict,
    pilot_estimates: dict,
    target_workers: int,
) -> pd.DataFrame:
    service_df = pd.read_csv(service_csv, usecols=["app_du", "minute_index"])
    summary_df = pd.read_csv(summary_csv).set_index("app_du")
    train_ratio = float(config["forecast"]["train_ratio"])
    valid_ratio = float(config["forecast"]["valid_ratio"])
    context_window = int(config["forecast"]["context_window"])
    horizons = list(config["forecast"]["horizons"])
    max_horizon = max(horizons)
    rows = []
    for idx, (app_du, group) in enumerate(service_df.groupby("app_du")):
        row_count = int(len(group))
        split_idx = int(row_count * (train_ratio + valid_ratio))
        test_rows = row_count - split_idx
        estimated_predictions_per_horizon = max(0, test_rows - context_window - max_horizon + 1)
        service_summary = summary_df.loc[app_du]
        shard_id = idx % max(1, target_workers)
        runtime_ms = float(pilot_estimates["pilot_mean_fit_eval_ms_per_service"])
        rows.append(
            {
                "app_du": app_du,
                "row_count": row_count,
                "train_valid_split_end": split_idx,
                "test_rows": test_rows,
                "context_window": context_window,
                "horizons": "|".join(str(horizon) for horizon in horizons),
                "estimated_predictions_per_horizon": estimated_predictions_per_horizon,
                "request_cores_source": request_source(service_summary),
                "request_cores_value": request_value(service_summary),
                "planned_shard": shard_id,
                "estimated_fit_eval_ms": runtime_ms,
                "planned_forecast_output": str(output_dir / "tables" / f"{app_du}_qlr_forecasting.csv"),
                "planned_policy_output": str(output_dir / "tables" / f"{app_du}_qlr_policy.csv"),
                "planned_status_output": str(output_dir / "status" / f"{app_du}_status.json"),
            }
        )
    return pd.DataFrame(rows).sort_values(["planned_shard", "app_du"]).reset_index(drop=True)


def write_resource_plan(
    output_dir: Path,
    manifest_df: pd.DataFrame,
    service_csv: Path,
    summary_csv: Path,
    pilot_dir: Path,
    config: dict,
    census: dict,
    pilot_estimates: dict,
    target_workers: int,
    safety_factor: float,
    metrics_hash_before: str | None,
    metrics_hash_after: str | None,
    full_result_dir: Path,
) -> None:
    total_estimated_minutes = float(manifest_df["estimated_fit_eval_ms"].sum() / 60000.0)
    parallel_estimated_minutes = total_estimated_minutes / max(1, target_workers)
    artifact_estimate_bytes = int(
        pilot_estimates["estimated_csv_bytes_per_service"] * len(manifest_df) * safety_factor
    )
    lines = [
        "# QLR 139-Service Broad Resource Plan",
        "",
        f"- run_id: `{RUN_ID}`",
        "- status: `planning_only`",
        "- planning only; no full 139-service run executed",
        f"- service_count: `{len(manifest_df)}`",
        f"- service_csv: `{service_csv}`",
        f"- service_summary_csv: `{summary_csv}`",
        f"- pilot_dir: `{pilot_dir}`",
        f"- target_workers_for_future_calibration: `{target_workers}`",
        f"- safety_factor: `{safety_factor}`",
        f"- metrics_csv_hash_before: `{metrics_hash_before}`",
        f"- metrics_csv_hash_after: `{metrics_hash_after}`",
        f"- full_result_dir_exists: `{full_result_dir.exists()}`",
        "",
        "## Resource Census",
        "",
    ]
    for key, value in census.items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## Estimates From Pilot",
            "",
            f"- pilot_service_count: `{pilot_estimates['pilot_service_count']}`",
            f"- pilot_total_fit_eval_seconds: `{pilot_estimates['pilot_total_fit_eval_ms'] / 1000.0:.1f}`",
            f"- mean_fit_eval_seconds_per_service: `{pilot_estimates['pilot_mean_fit_eval_ms_per_service'] / 1000.0:.1f}`",
            f"- max_fit_eval_seconds_per_service: `{pilot_estimates['pilot_max_fit_eval_ms_per_service'] / 1000.0:.1f}`",
            f"- serial_139_estimated_minutes: `{total_estimated_minutes:.1f}`",
            f"- target_worker_estimated_wall_minutes: `{parallel_estimated_minutes:.1f}`",
            f"- safety_adjusted_csv_artifact_bytes: `{artifact_estimate_bytes}`",
            "",
            "## Recommended Ladder",
            "",
            "1. Run a 10-service calibration with the same QLR-only service script family and `--num-workers 2`.",
            "2. Verify runtime, memory, raw/guarded P90 fields, policy metrics, and unchanged central `metrics.csv`.",
            "3. Prepare the full run only if calibration passes and resource use remains stable.",
            "4. Do not use this plan as authorization to start the full 139-service run automatically.",
            "",
            "## Claim Boundary",
            "",
            "This plan is a scheduling and resource artifact. It supports no new manuscript result and does not alter the current mixed service-pilot interpretation.",
        ]
    )
    (output_dir / "qlr_broad_resource_plan.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_gate_checklist(output_dir: Path) -> None:
    lines = [
        "# QLR Broad Gate Checklist",
        "",
        "- [ ] 10-service calibration completed before full 139-service execution.",
        "- [ ] Calibration confirms raw and guarded P90 fields for every service and horizon.",
        "- [ ] Calibration confirms `metrics.csv` remains unchanged.",
        "- [ ] Calibration report records runtime, memory, disk growth, and any service failures.",
        "- [ ] Full run command is explicitly reviewed after calibration; it is not launched by the planning script.",
        "- [ ] Full run keeps service policy parameters identical to the existing service policy semantics.",
        "- [ ] Full run report preserves mixed/negative outcomes instead of tuning for a better story.",
        "- [ ] Full run does not invoke the held deep-model path.",
    ]
    (output_dir / "qlr_broad_gate_checklist.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_dry_run_report(
    output_dir: Path,
    manifest_df: pd.DataFrame,
    full_result_dir: Path,
    metrics_hash_before: str | None,
    metrics_hash_after: str | None,
) -> list[str]:
    gate_failures = []
    if len(manifest_df) != 139:
        gate_failures.append(f"manifest has {len(manifest_df)} services, expected 139")
    if full_result_dir.exists():
        gate_failures.append(f"full result directory exists: {full_result_dir}")
    if metrics_hash_before != metrics_hash_after:
        gate_failures.append("metrics.csv changed during plan-only run")
    status = "pass" if not gate_failures else "fail"
    lines = [
        "# QLR Broad Dry-Run Report",
        "",
        f"- run_id: `{RUN_ID}`",
        f"- status: `{status}`",
        "- planning only; no full 139-service run executed",
        f"- manifest_service_count: `{len(manifest_df)}`",
        f"- full_result_dir_exists: `{full_result_dir.exists()}`",
        f"- metrics_csv_hash_before: `{metrics_hash_before}`",
        f"- metrics_csv_hash_after: `{metrics_hash_after}`",
        "",
        "## Gate Result",
        "",
    ]
    if gate_failures:
        lines.extend(f"- FAIL: {failure}" for failure in gate_failures)
    else:
        lines.append("- PASS: manifest covers 139 services and no full-result directory was created.")
    (output_dir / "qlr_broad_dry_run_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return gate_failures


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Plan a future broad QLR service run. This script never trains models or executes the run."
    )
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--service-csv", type=Path, default=None)
    parser.add_argument("--service-summary-csv", type=Path, default=None)
    parser.add_argument("--pilot-dir", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--target-workers", type=int, default=2)
    parser.add_argument("--safety-factor", type=float, default=2.0)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    with args.config.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    service_csv = resolve_workbench_path(
        args.service_csv or (repo_root / "data" / "processed" / "service_cohort_broad_v2018.csv"),
        repo_root,
    )
    summary_csv = resolve_workbench_path(
        args.service_summary_csv or (repo_root / "data" / "processed" / "service_cohort_broad_summary_v2018.csv"),
        repo_root,
    )
    pilot_dir = resolve_workbench_path(
        args.pilot_dir or (repo_root / "experiments" / "results" / "qlr_service_pilot"),
        repo_root,
    )
    output_dir = resolve_workbench_path(
        args.output_dir or (repo_root / "experiments" / "results" / "qlr_service_broad_plan"),
        repo_root,
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    metrics_path = resolve_workbench_path(config["output"]["metrics_csv"], repo_root)
    metrics_hash_before = sha256_file(metrics_path)
    full_result_dir = repo_root / "experiments" / "results" / "qlr_service_broad"

    census = resource_census(repo_root)
    pilot_estimates = load_pilot_estimates(pilot_dir, args.safety_factor)
    manifest_df = build_manifest(
        service_csv,
        summary_csv,
        output_dir,
        config,
        pilot_estimates,
        max(1, int(args.target_workers)),
    )
    manifest_df.to_csv(output_dir / "qlr_broad_run_manifest.csv", index=False)
    metrics_hash_after = sha256_file(metrics_path)

    write_resource_plan(
        output_dir,
        manifest_df,
        service_csv,
        summary_csv,
        pilot_dir,
        config,
        census,
        pilot_estimates,
        max(1, int(args.target_workers)),
        float(args.safety_factor),
        metrics_hash_before,
        metrics_hash_after,
        full_result_dir,
    )
    write_gate_checklist(output_dir)
    gate_failures = write_dry_run_report(
        output_dir,
        manifest_df,
        full_result_dir,
        metrics_hash_before,
        metrics_hash_after,
    )
    if gate_failures:
        raise SystemExit("; ".join(gate_failures))


if __name__ == "__main__":
    main()
