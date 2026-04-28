#!/usr/bin/env python3
"""Create an approval-only package for a possible 139-service QLR run."""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import os
import platform
import shutil
from pathlib import Path

import pandas as pd
import yaml


RUN_ID = "qlr_service_broad_approval_20260427"
HELD_DEEP_MODEL_LABEL = "Full UA-" + "MSTCN"


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


def load_calibration_estimates(calibration_dir: Path, safety_factor: float) -> dict:
    trace_path = calibration_dir / "calibration_resource_trace.csv"
    if not trace_path.exists():
        raise FileNotFoundError(f"Missing calibration trace: {trace_path}")
    trace_df = pd.read_csv(trace_path)
    service_count = int(trace_df["app_du"].nunique())
    artifact_bytes = int(trace_df["estimated_service_artifact_bytes"].sum())
    return {
        "calibration_trace_path": str(trace_path),
        "calibration_service_count": service_count,
        "runtime_wall_ms_sum": float(trace_df["runtime_wall_ms"].sum()),
        "runtime_wall_ms_mean": float(trace_df["runtime_wall_ms"].mean()),
        "runtime_wall_ms_max": float(trace_df["runtime_wall_ms"].max()),
        "fit_eval_ms_sum": float(trace_df["fit_eval_ms_sum"].sum()),
        "fit_eval_ms_mean": float(trace_df["fit_eval_ms_sum"].mean()),
        "fit_eval_ms_max": float(trace_df["fit_eval_ms_sum"].max()),
        "artifact_bytes_sum": artifact_bytes,
        "artifact_bytes_mean_per_service": float(artifact_bytes / max(service_count, 1)),
        "workers_observed": "|".join(str(worker) for worker in sorted(trace_df["planned_worker"].unique())),
        "safety_factor": float(safety_factor),
    }


def build_execution_manifest(
    broad_plan_manifest: Path,
    summary_csv: Path,
    output_full_dir: Path,
    calibration_estimates: dict,
    target_workers: int,
) -> pd.DataFrame:
    plan_df = pd.read_csv(broad_plan_manifest)
    summary_df = pd.read_csv(summary_csv).set_index("app_du")
    rows = []
    for idx, row in plan_df.sort_values("app_du").reset_index(drop=True).iterrows():
        app_du = row["app_du"]
        service_summary = summary_df.loc[app_du]
        planned_worker = idx % max(1, target_workers)
        rows.append(
            {
                "app_du": app_du,
                "row_count": int(row["row_count"]),
                "train_valid_split_end": int(row["train_valid_split_end"]),
                "test_rows": int(row["test_rows"]),
                "context_window": int(row["context_window"]),
                "horizons": row["horizons"],
                "estimated_predictions_per_horizon": int(row["estimated_predictions_per_horizon"]),
                "request_cores_source": request_source(service_summary),
                "request_cores_value": request_value(service_summary),
                "planned_worker": planned_worker,
                "estimated_runtime_wall_ms_from_calibration": calibration_estimates["runtime_wall_ms_mean"],
                "estimated_fit_eval_ms_from_calibration": calibration_estimates["fit_eval_ms_mean"],
                "planned_forecasting_raw_output": str(output_full_dir / "service_qlr_forecasting_raw.csv"),
                "planned_forecasting_summary_output": str(output_full_dir / "service_qlr_forecasting_summary.csv"),
                "planned_predictions_output": str(output_full_dir / "service_qlr_predictions.csv"),
                "planned_policy_raw_output": str(output_full_dir / "service_qlr_policy_raw.csv"),
                "planned_policy_summary_output": str(output_full_dir / "service_qlr_policy_summary.csv"),
                "planned_policy_delta_output": str(output_full_dir / "service_qlr_policy_delta_by_service.csv"),
                "planned_policy_series_output": str(output_full_dir / "service_qlr_policy_series.csv"),
                "planned_resource_trace_output": str(output_full_dir / "broad_resource_trace.csv"),
                "planned_report_output": str(output_full_dir / "qlr_service_broad_report.md"),
            }
        )
    return pd.DataFrame(rows)


def write_execution_approval(
    output_dir: Path,
    manifest_df: pd.DataFrame,
    broad_plan_manifest: Path,
    calibration_dir: Path,
    service_summary_csv: Path,
    census: dict,
    calibration_estimates: dict,
    target_workers: int,
    safety_factor: float,
    metrics_hash_before: str | None,
    metrics_hash_after: str | None,
    full_result_dir: Path,
) -> None:
    service_count = len(manifest_df)
    serial_minutes = calibration_estimates["runtime_wall_ms_mean"] * service_count / 60000.0
    two_worker_minutes = serial_minutes / max(1, target_workers)
    artifact_bytes = int(calibration_estimates["artifact_bytes_mean_per_service"] * service_count * safety_factor)
    lines = [
        "# QLR 139-Service Full Execution Approval",
        "",
        f"- run_id: `{RUN_ID}`",
        "- status: `approval_plan_only`",
        "- approval planning only; no full 139-service run executed",
        f"- service_count: `{service_count}`",
        f"- broad_plan_manifest: `{broad_plan_manifest}`",
        f"- calibration_dir: `{calibration_dir}`",
        f"- service_summary_csv: `{service_summary_csv}`",
        f"- recommended_full_run_workers_after_explicit_approval: `{target_workers}`",
        f"- safety_factor: `{safety_factor}`",
        f"- metrics_csv_hash_before: `{metrics_hash_before}`",
        f"- metrics_csv_hash_after: `{metrics_hash_after}`",
        f"- full_result_dir_exists: `{full_result_dir.exists()}`",
        "",
        "## Approval Boundary",
        "",
        "Full run has not been executed. Calibration pass is not automatic approval.",
        f"`{HELD_DEEP_MODEL_LABEL}` remains frozen, and the manuscript headline conclusion remains unchanged.",
        "This artifact supports execution review only; it does not support a new experimental claim.",
        "",
        "## Updated Resource Estimate From 10-Service Calibration",
        "",
        f"- source: `{calibration_estimates['calibration_trace_path']}`",
        f"- calibration_service_count: `{calibration_estimates['calibration_service_count']}`",
        f"- observed_workers: `{calibration_estimates['workers_observed']}`",
        f"- mean_runtime_seconds_per_service: `{calibration_estimates['runtime_wall_ms_mean'] / 1000.0:.1f}`",
        f"- max_runtime_seconds_per_service: `{calibration_estimates['runtime_wall_ms_max'] / 1000.0:.1f}`",
        f"- serial_139_estimated_minutes: `{serial_minutes:.1f}`",
        f"- two_worker_estimated_wall_minutes: `{two_worker_minutes:.1f}`",
        f"- safety_adjusted_artifact_bytes: `{artifact_bytes}`",
        "",
        "## Current Resource Census",
        "",
    ]
    for key, value in census.items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## Execution Rules For Any Future Full Run",
            "",
            "- Require explicit approval before running the full 139-service command.",
            f"- Start with `--num-workers {target_workers}`; do not raise concurrency inside the approval step.",
            "- Reuse the existing service policy semantics exactly, including service min_capacity=1.0 and max_step_change=1.0.",
            "- Keep `median_container_request_cores` only for replica conversion, with mean fallback only when median is non-positive.",
            "- Do not update central `metrics.csv` from the broad service run.",
            "- Preserve raw and guarded P90 fields, raw crossing diagnostics, and guarded crossing diagnostics.",
            "- Preserve mixed or negative outcomes; do not retune for a better story.",
            "- Re-check memory, disk, metrics hash, and absence of the full output directory immediately before execution.",
        ]
    )
    (output_dir / "qlr_broad_execution_approval.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_resource_update(
    output_dir: Path,
    calibration_estimates: dict,
    manifest_df: pd.DataFrame,
    target_workers: int,
    safety_factor: float,
) -> None:
    service_count = len(manifest_df)
    serial_minutes = calibration_estimates["runtime_wall_ms_mean"] * service_count / 60000.0
    parallel_minutes = serial_minutes / max(1, target_workers)
    artifact_bytes = int(calibration_estimates["artifact_bytes_mean_per_service"] * service_count * safety_factor)
    lines = [
        "# QLR Broad Resource Update From Calibration",
        "",
        f"- run_id: `{RUN_ID}`",
        "- estimate_source: `10-service calibration_resource_trace.csv`",
        f"- calibration_service_count: `{calibration_estimates['calibration_service_count']}`",
        f"- observed_workers: `{calibration_estimates['workers_observed']}`",
        f"- mean_runtime_seconds_per_service: `{calibration_estimates['runtime_wall_ms_mean'] / 1000.0:.1f}`",
        f"- max_runtime_seconds_per_service: `{calibration_estimates['runtime_wall_ms_max'] / 1000.0:.1f}`",
        f"- mean_fit_eval_seconds_per_service: `{calibration_estimates['fit_eval_ms_mean'] / 1000.0:.1f}`",
        f"- artifact_bytes_per_service: `{calibration_estimates['artifact_bytes_mean_per_service']:.1f}`",
        f"- broad_service_count: `{service_count}`",
        f"- serial_estimated_minutes: `{serial_minutes:.1f}`",
        f"- estimated_wall_minutes_at_workers_{target_workers}: `{parallel_minutes:.1f}`",
        f"- safety_factor: `{safety_factor}`",
        f"- safety_adjusted_artifact_bytes: `{artifact_bytes}`",
        "",
        "This estimate replaces the earlier pilot-only estimate for approval planning.",
    ]
    (output_dir / "qlr_broad_resource_update_from_calibration.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def write_preflight_checks(
    output_dir: Path,
    manifest_df: pd.DataFrame,
    metrics_hash_before: str | None,
    metrics_hash_after: str | None,
    full_result_dir: Path,
) -> list[str]:
    gate_failures = []
    if len(manifest_df) != 139:
        gate_failures.append(f"manifest has {len(manifest_df)} services, expected 139")
    if full_result_dir.exists():
        gate_failures.append(f"full result directory exists: {full_result_dir}")
    if metrics_hash_before != metrics_hash_after:
        gate_failures.append("metrics.csv changed during approval planning")

    status = "pass" if not gate_failures else "fail"
    lines = [
        "# QLR Broad Preflight Checks",
        "",
        f"- run_id: `{RUN_ID}`",
        f"- status: `{status}`",
        "- approval planning only; no full 139-service run executed",
        f"- manifest_service_count: `{len(manifest_df)}`",
        f"- full_result_dir_exists: `{full_result_dir.exists()}`",
        f"- metrics_csv_hash_before: `{metrics_hash_before}`",
        f"- metrics_csv_hash_after: `{metrics_hash_after}`",
        "",
        "## Completed Checks",
        "",
        "- [x] 10-service calibration completed before any full 139-service execution.",
        "- [x] Calibration estimates, not pilot-only estimates, drive this approval package.",
        "- [x] Approval manifest covers the intended broad services.",
        "- [x] `metrics.csv` hash is unchanged during approval planning.",
        "- [x] Full-result directory is not created by the approval script.",
        "- [x] Approval package states that calibration pass is not automatic full-run approval.",
        "",
        "## Required Before Any Future Full Run",
        "",
        "- [ ] Explicit human approval for full 139-service execution.",
        "- [ ] Re-check current CPU, memory, disk, metrics hash, and output directory absence.",
        "- [ ] Run with `--num-workers 2` unless a new calibration justifies changing concurrency.",
        "- [ ] Keep central `metrics.csv` unchanged for broad service artifacts.",
        "- [ ] Keep the held deep-model path frozen.",
        "- [ ] Preserve mixed or negative results in the report.",
        "",
        "## Gate Result",
        "",
    ]
    if gate_failures:
        lines.extend(f"- FAIL: {failure}" for failure in gate_failures)
    else:
        lines.append("- PASS: approval package is complete and no full run was executed.")
    (output_dir / "qlr_broad_preflight_checks.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return gate_failures


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a 139-service QLR full-run approval package. This script never trains models."
    )
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--broad-plan-manifest", type=Path, default=None)
    parser.add_argument("--service-summary-csv", type=Path, default=None)
    parser.add_argument("--calibration-dir", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--target-workers", type=int, default=2)
    parser.add_argument("--safety-factor", type=float, default=2.0)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    with args.config.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    broad_plan_manifest = resolve_workbench_path(
        args.broad_plan_manifest
        or (repo_root / "experiments" / "results" / "qlr_service_broad_plan" / "qlr_broad_run_manifest.csv"),
        repo_root,
    )
    service_summary_csv = resolve_workbench_path(
        args.service_summary_csv or (repo_root / "data" / "processed" / "service_cohort_broad_summary_v2018.csv"),
        repo_root,
    )
    calibration_dir = resolve_workbench_path(
        args.calibration_dir or (repo_root / "experiments" / "results" / "qlr_service_calibration_10"),
        repo_root,
    )
    output_dir = resolve_workbench_path(
        args.output_dir or (repo_root / "experiments" / "results" / "qlr_service_broad_approval"),
        repo_root,
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    metrics_path = resolve_workbench_path(config["output"]["metrics_csv"], repo_root)
    metrics_hash_before = sha256_file(metrics_path)
    full_result_dir = repo_root / "experiments" / "results" / "qlr_service_broad"
    target_workers = max(1, int(args.target_workers))
    safety_factor = float(args.safety_factor)

    census = resource_census(repo_root)
    calibration_estimates = load_calibration_estimates(calibration_dir, safety_factor)
    manifest_df = build_execution_manifest(
        broad_plan_manifest,
        service_summary_csv,
        full_result_dir,
        calibration_estimates,
        target_workers,
    )
    manifest_df.to_csv(output_dir / "qlr_broad_execution_manifest.csv", index=False)
    metrics_hash_after = sha256_file(metrics_path)

    write_execution_approval(
        output_dir,
        manifest_df,
        broad_plan_manifest,
        calibration_dir,
        service_summary_csv,
        census,
        calibration_estimates,
        target_workers,
        safety_factor,
        metrics_hash_before,
        metrics_hash_after,
        full_result_dir,
    )
    write_resource_update(output_dir, calibration_estimates, manifest_df, target_workers, safety_factor)
    gate_failures = write_preflight_checks(output_dir, manifest_df, metrics_hash_before, metrics_hash_after, full_result_dir)
    if gate_failures:
        raise SystemExit("; ".join(gate_failures))


if __name__ == "__main__":
    main()
