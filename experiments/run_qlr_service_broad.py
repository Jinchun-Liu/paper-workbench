#!/usr/bin/env python3
"""Guarded full 139-service QLR runner.

The default safe path is --preflight-only. Full execution requires an explicit
confirmation token so the broad run cannot start by accident.
"""

from __future__ import annotations

import argparse
import ctypes
import os
import platform
import shutil
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from run_qlr_service_calibration import (
    evaluate_service_task,
    resolve_workbench_path,
    sha256_file,
    summarize_outputs,
)


RUN_ID = "qlr_service_broad_20260427"
PREFLIGHT_RUN_ID = "qlr_service_broad_preflight_20260427"
CONFIRM_TOKEN = "I_APPROVE_QLR_139_SERVICE_FULL_RUN"


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


def service_request_source(summary_row: pd.Series) -> str:
    median_value = float(summary_row["median_container_request_cores"])
    return "median_container_request_cores" if median_value > 0.0 else "mean_container_request_cores"


def service_request_value(summary_row: pd.Series) -> float:
    source = service_request_source(summary_row)
    return max(float(summary_row[source]), 0.1)


def build_broad_profile(
    service_df: pd.DataFrame,
    summary_df: pd.DataFrame,
    train_ratio: float,
    valid_ratio: float,
) -> pd.DataFrame:
    summary_lookup = summary_df.set_index("app_du")
    rows: list[dict] = []
    for app_du, group in service_df.groupby("app_du", sort=True):
        if app_du not in summary_lookup.index:
            raise KeyError(f"Missing service summary row for service {app_du}")
        values = group.sort_values("minute_index")["service_cpu_used_cores_proxy"].to_numpy(dtype=float)
        split_idx = int(len(values) * (train_ratio + valid_ratio))
        prefix = values[:split_idx]
        load_mean = float(np.mean(prefix))
        burst_std = float(np.std(prefix, ddof=1)) if len(prefix) > 1 else 0.0
        burst_cv = burst_std / max(load_mean, 1e-9)
        peak_to_mean = float(np.max(prefix) / max(load_mean, 1e-9)) if len(prefix) else 0.0
        summary_row = summary_lookup.loc[app_du]
        rows.append(
            {
                "selection_role": "broad_full_service",
                "app_du": app_du,
                "prefix_rows": int(len(prefix)),
                "train_valid_split_end": int(split_idx),
                "row_count": int(len(values)),
                "test_rows": int(len(values) - split_idx),
                "load_mean_prefix": load_mean,
                "burst_cv_prefix": burst_cv,
                "peak_to_mean_prefix": peak_to_mean,
                "selection_rule": (
                    "139-service broad run profile computed from train+validation prefix descriptors; "
                    "test outcomes and full-span summary descriptors are not used for service selection"
                ),
                "coverage_ratio_metadata_only": float(summary_row["coverage_ratio"]),
                "request_cores_source": service_request_source(summary_row),
                "request_cores_value": service_request_value(summary_row),
                "median_container_request_cores": float(summary_row["median_container_request_cores"]),
                "mean_container_request_cores": float(summary_row["mean_container_request_cores"]),
            }
        )
    return pd.DataFrame(rows)


def build_tasks(
    service_df: pd.DataFrame,
    summary_df: pd.DataFrame,
    config: dict,
    alpha: float,
    solver: str,
    num_workers: int,
) -> list[dict]:
    summary_lookup = summary_df.set_index("app_du")
    tasks = []
    for idx, (app_du, group) in enumerate(service_df.groupby("app_du", sort=True)):
        tasks.append(
            {
                "app_du": app_du,
                "selection_role": "broad_full_service",
                "series": group.sort_values("minute_index")["service_cpu_used_cores_proxy"].to_numpy(dtype=float),
                "service_meta": summary_lookup.loc[app_du].to_dict(),
                "context_window": int(config["forecast"]["context_window"]),
                "horizons": list(config["forecast"]["horizons"]),
                "train_ratio": float(config["forecast"]["train_ratio"]),
                "valid_ratio": float(config["forecast"]["valid_ratio"]),
                "policy_config": config["policy"],
                "alpha": float(alpha),
                "solver": str(solver),
                "planned_worker": idx % max(1, int(num_workers)),
            }
        )
    return tasks


def write_preflight_report(
    preflight_dir: Path,
    profile_df: pd.DataFrame,
    census: dict,
    metrics_hash: str | None,
    output_dir: Path,
    num_workers: int,
    full_result_dir_exists: bool,
) -> list[str]:
    gate_failures = []
    if len(profile_df) != 139:
        gate_failures.append(f"profile has {len(profile_df)} services, expected 139")
    if full_result_dir_exists:
        gate_failures.append(f"full output directory already exists: {output_dir}")
    status = "pass" if not gate_failures else "fail"
    lines = [
        "# QLR 139-Service Full Preflight",
        "",
        f"- run_id: `{PREFLIGHT_RUN_ID}`",
        f"- status: `{status}`",
        "- preflight only; no full 139-service run executed",
        f"- service_count: `{len(profile_df)}`",
        f"- planned_output_dir: `{output_dir}`",
        f"- planned_num_workers: `{num_workers}`",
        f"- metrics_csv_hash: `{metrics_hash}`",
        f"- full_result_dir_exists: `{full_result_dir_exists}`",
        "",
        "## Resource Census",
        "",
    ]
    for key, value in census.items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## Execution Guard",
            "",
            f"Full execution requires `--confirm-full-run {CONFIRM_TOKEN}`.",
            "The test split must remain evaluation-only; model fitting uses train+validation prefixes.",
            "Central `metrics.csv` must remain unchanged by the broad service run.",
            "Mixed or negative full-run outcomes must be preserved in the report.",
            "",
            "## Gate Result",
            "",
        ]
    )
    if gate_failures:
        lines.extend(f"- FAIL: {failure}" for failure in gate_failures)
    else:
        lines.append("- PASS: guarded full-run entrypoint is ready, but the full run has not started.")
    preflight_dir.mkdir(parents=True, exist_ok=True)
    profile_df.to_csv(preflight_dir / "qlr_service_broad_preflight_profile.csv", index=False)
    (preflight_dir / "qlr_service_broad_preflight_report.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    return gate_failures


def write_broad_report(
    output_dir: Path,
    profile_df: pd.DataFrame,
    forecast_summary_df: pd.DataFrame,
    policy_summary_df: pd.DataFrame,
    resource_trace_df: pd.DataFrame,
    gate_failures: list[str],
    metrics_hash_before: str | None,
    metrics_hash_after: str | None,
    num_workers: int,
    fallback_services: list[str],
) -> Path:
    status = "pass" if not gate_failures else "fail"
    lines = [
        "# QLR 139-Service Broad Report",
        "",
        f"- run_id: `{RUN_ID}`",
        f"- status: `{status}`",
        f"- num_workers: `{num_workers}`",
        f"- service_count: `{profile_df['app_du'].nunique()}`",
        f"- metrics_csv_hash_before: `{metrics_hash_before}`",
        f"- metrics_csv_hash_after: `{metrics_hash_after}`",
        "",
        "## Scope Boundary",
        "",
        "This is the guarded 139-service QLR broad run. It does not update central `metrics.csv` and does not change the manuscript headline conclusion by itself.",
        "The test split is used only for evaluation; QLR fitting uses the train+validation prefix only, and test data are not used for parameter, model, service, or policy selection.",
        "",
        "## Policy Parameter Reuse",
        "",
        "The run reuses the existing service-policy semantics: service `min_capacity=1.0`, service `max_step_change=1.0`, config-driven headroom, quantile margin, scale-in safety, cooldown, and reactive thresholds.",
        "`median_container_request_cores` is read from the service summary only for replica conversion, not for service selection.",
    ]
    if fallback_services:
        lines.append(f"Services falling back to `mean_container_request_cores`: `{', '.join(sorted(fallback_services))}`.")
    else:
        lines.append("No selected service required fallback from `median_container_request_cores`.")
    lines.extend(
        [
            "",
            "## Gate Result",
            "",
        ]
    )
    if gate_failures:
        lines.extend(f"- FAIL: {failure}" for failure in gate_failures)
    else:
        lines.append("- PASS: all broad-run gates passed.")
    lines.extend(
        [
            "",
            "## Forecasting Summary",
            "",
            "```csv",
            forecast_summary_df.to_csv(index=False, lineterminator="\n").strip(),
            "```",
            "",
            "## Policy Summary",
            "",
            "```csv",
            policy_summary_df.to_csv(index=False, lineterminator="\n").strip(),
            "```",
            "",
            "## Resource Trace Summary",
            "",
            "```csv",
            resource_trace_df.to_csv(index=False, lineterminator="\n").strip(),
            "```",
        ]
    )
    report_path = output_dir / "qlr_service_broad_report.md"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


def run_full_broad(
    output_dir: Path,
    service_df: pd.DataFrame,
    summary_df: pd.DataFrame,
    profile_df: pd.DataFrame,
    config: dict,
    metrics_path: Path,
    num_workers: int,
    alpha: float,
    solver: str,
) -> None:
    if output_dir.exists():
        raise SystemExit(f"Refusing to overwrite existing output directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=False)
    profile_df.to_csv(output_dir / "broad_service_profile.csv", index=False)
    progress_path = output_dir / "broad_progress.csv"
    progress_rows: list[dict] = []
    run_start = time.perf_counter()
    metrics_hash_before = sha256_file(metrics_path)

    tasks = build_tasks(service_df, summary_df, config, alpha, solver, num_workers)
    forecast_rows: list[dict] = []
    prediction_rows: list[dict] = []
    policy_rows: list[dict] = []
    policy_series_rows: list[dict] = []
    resource_rows: list[dict] = []
    gate_failures: list[str] = []
    fallback_services: list[str] = []

    with ProcessPoolExecutor(max_workers=max(1, int(num_workers))) as executor:
        futures = {executor.submit(evaluate_service_task, task): task["app_du"] for task in tasks}
        for future in as_completed(futures):
            result = future.result()
            app_du = futures[future]
            forecast_rows.extend(result["forecast_rows"])
            prediction_rows.extend(result["prediction_rows"])
            policy_rows.extend(result["policy_rows"])
            policy_series_rows.extend(result["policy_series_rows"])
            resource_rows.append(result["resource_trace"])
            gate_failures.extend(result["gate_failures"])
            if result["request_fallback_used"]:
                fallback_services.append(app_du)
            progress_rows.append(
                {
                    "completed_services": len(resource_rows),
                    "total_services": len(tasks),
                    "app_du": app_du,
                    "elapsed_seconds": round(time.perf_counter() - run_start, 3),
                    "worker_id": result["resource_trace"].get("worker_id", ""),
                    "runtime_seconds": result["resource_trace"].get("runtime_seconds", ""),
                    "forecast_rows": result["resource_trace"].get("forecast_rows", ""),
                    "prediction_rows": result["resource_trace"].get("prediction_rows", ""),
                    "policy_rows": result["resource_trace"].get("policy_rows", ""),
                    "policy_series_rows": result["resource_trace"].get("policy_series_rows", ""),
                    "gate_failure_count": len(result["gate_failures"]),
                }
            )
            pd.DataFrame(progress_rows).to_csv(progress_path, index=False)
            print(
                f"[progress] {len(resource_rows)}/{len(tasks)} services complete; "
                f"latest={app_du}; elapsed={progress_rows[-1]['elapsed_seconds']}s",
                flush=True,
            )

    forecast_df = pd.DataFrame(forecast_rows)
    predictions_df = pd.DataFrame(prediction_rows)
    policy_df = pd.DataFrame(policy_rows)
    policy_series_df = pd.DataFrame(policy_series_rows)
    resource_trace_df = pd.DataFrame(resource_rows).sort_values("app_du").reset_index(drop=True)
    forecast_summary_df, policy_summary_df, policy_delta_df = summarize_outputs(forecast_df, policy_df)

    forecast_df.to_csv(output_dir / "service_qlr_forecasting_raw.csv", index=False)
    forecast_summary_df.to_csv(output_dir / "service_qlr_forecasting_summary.csv", index=False)
    predictions_df.to_csv(output_dir / "service_qlr_predictions.csv", index=False)
    policy_df.to_csv(output_dir / "service_qlr_policy_raw.csv", index=False)
    policy_summary_df.to_csv(output_dir / "service_qlr_policy_summary.csv", index=False)
    policy_delta_df.to_csv(output_dir / "service_qlr_policy_delta_by_service.csv", index=False)
    policy_series_df.to_csv(output_dir / "service_qlr_policy_series.csv", index=False)
    resource_trace_df.to_csv(output_dir / "broad_resource_trace.csv", index=False)

    if len(set(forecast_df["app_du"])) != 139:
        gate_failures.append("forecast artifacts do not contain exactly 139 services")
    if not {"p50_raw", "p90_raw", "p90_guarded"}.issubset(predictions_df.columns):
        gate_failures.append("prediction artifact is missing raw or guarded P90 fields")
    if int(forecast_df["guarded_crossing_count"].sum()) != 0:
        gate_failures.append("guarded P90 crossing count is nonzero")
    if not np.all(np.isfinite(forecast_df.select_dtypes(include=[np.number]).to_numpy(dtype=float))):
        gate_failures.append("forecast artifacts contain non-finite numeric values")
    if not np.all(np.isfinite(policy_df.select_dtypes(include=[np.number]).to_numpy(dtype=float))):
        gate_failures.append("policy artifacts contain non-finite numeric values")
    if not policy_df["sla_violation"].between(0.0, 1.0).all():
        gate_failures.append("policy SLA violation outside [0, 1]")
    capacity_columns = ["reactive_capacity", "lagged_capacity", "qlr_predictive_capacity"]
    if np.any(policy_series_df[capacity_columns].to_numpy(dtype=float) < 0.0):
        gate_failures.append("policy capacity artifacts contain negative values")
    if len(resource_trace_df) != 139:
        gate_failures.append("resource trace does not contain exactly 139 services")

    metrics_hash_after = sha256_file(metrics_path)
    if metrics_hash_before != metrics_hash_after:
        gate_failures.append("metrics.csv changed during broad service run")

    report_path = write_broad_report(
        output_dir,
        profile_df,
        forecast_summary_df,
        policy_summary_df,
        resource_trace_df,
        gate_failures,
        metrics_hash_before,
        metrics_hash_after,
        max(1, int(num_workers)),
        fallback_services,
    )
    if gate_failures:
        raise SystemExit(f"QLR broad service gate failed; see {report_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--service-csv", type=Path, default=None)
    parser.add_argument("--service-summary-csv", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--preflight-dir", type=Path, default=None)
    parser.add_argument("--num-workers", type=int, default=2)
    parser.add_argument("--alpha", type=float, default=1e-4)
    parser.add_argument("--solver", type=str, default="highs")
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--confirm-full-run", type=str, default="")
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
    output_dir = resolve_workbench_path(
        args.output_dir or (repo_root / "experiments" / "results" / "qlr_service_broad"),
        repo_root,
    )
    preflight_dir = resolve_workbench_path(
        args.preflight_dir or (repo_root / "experiments" / "results" / "qlr_service_broad_preflight"),
        repo_root,
    )
    metrics_path = resolve_workbench_path(config["output"]["metrics_csv"], repo_root)

    service_df = pd.read_csv(service_csv, usecols=["app_du", "minute_index", "service_cpu_used_cores_proxy"])
    summary_df = pd.read_csv(summary_csv)
    profile_df = build_broad_profile(
        service_df,
        summary_df,
        float(config["forecast"]["train_ratio"]),
        float(config["forecast"]["valid_ratio"]),
    )

    if args.preflight_only:
        failures = write_preflight_report(
            preflight_dir,
            profile_df,
            resource_census(repo_root),
            sha256_file(metrics_path),
            output_dir,
            max(1, int(args.num_workers)),
            output_dir.exists(),
        )
        if failures:
            raise SystemExit("; ".join(failures))
        return

    if args.confirm_full_run != CONFIRM_TOKEN:
        raise SystemExit(
            "Refusing to run full 139-service QLR without explicit confirmation. "
            f"Pass --confirm-full-run {CONFIRM_TOKEN} after approval."
        )

    run_full_broad(
        output_dir,
        service_df,
        summary_df,
        profile_df,
        config,
        metrics_path,
        max(1, int(args.num_workers)),
        float(args.alpha),
        str(args.solver),
    )


if __name__ == "__main__":
    main()
