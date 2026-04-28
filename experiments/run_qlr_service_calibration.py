#!/usr/bin/env python3
"""Run a 10-service QLR calibration before any broad service experiment."""

from __future__ import annotations

import argparse
import hashlib
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from contextlib import nullcontext
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

try:
    from threadpoolctl import threadpool_limits
except ImportError:  # pragma: no cover - optional runtime dependency
    threadpool_limits = None

from models.baselines import quantile_linear_regression
from policies.autoscaling_simulator import run_lagged_target_tracking, run_predictive, run_reactive


RUN_ID = "qlr_service_calibration_10_20260427"
MODEL_NAME = "quantile_linear_regression"
CALIBRATION_SERVICE_ROLES = {
    "pilot_low_load_low_burst": "app_2557",
    "pilot_low_load_high_burst": "app_7264",
    "pilot_high_load_low_burst": "app_1675",
    "pilot_high_load_high_burst": "app_3665",
    "pilot_median_anchor": "app_521",
    "cal_lowest_load_guard": "app_3422",
    "cal_highest_load_guard": "app_141",
    "cal_lowest_burst_guard": "app_2128",
    "cal_highest_burst_guard": "app_8205",
    "cal_peak_to_mean_guard": "app_7227",
}


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


def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.abs(y_true - y_pred)))


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    denom = np.where(np.abs(y_true) < 1e-6, 1.0, np.abs(y_true))
    return float(np.mean(np.abs((y_true - y_pred) / denom)))


def pinball(y_true: np.ndarray, y_pred: np.ndarray, quantile: float) -> float:
    delta = y_true - y_pred
    return float(np.mean(np.maximum(quantile * delta, (quantile - 1.0) * delta)))


def split_series(series: np.ndarray, train_ratio: float, valid_ratio: float) -> tuple[np.ndarray, np.ndarray, int]:
    split_idx = int(len(series) * (train_ratio + valid_ratio))
    return series[:split_idx], series[split_idx:], split_idx


def finite_values(values: list[float]) -> bool:
    return bool(np.all(np.isfinite(np.asarray(values, dtype=float))))


def frame_size_bytes(rows: list[dict]) -> int:
    if not rows:
        return 0
    return len(pd.DataFrame(rows).to_csv(index=False).encode("utf-8"))


def build_selection_profile(
    service_df: pd.DataFrame,
    summary_df: pd.DataFrame,
    train_ratio: float,
    valid_ratio: float,
) -> tuple[pd.DataFrame, list[str]]:
    summary_lookup = summary_df.set_index("app_du")
    fixed_app_to_role = {app_du: role for role, app_du in CALIBRATION_SERVICE_ROLES.items()}
    selection_rule = (
        "fixed 10-service calibration selected from train+validation prefix descriptors; "
        "test outcomes and full-span summary descriptors are not used for selection"
    )
    rows: list[dict] = []
    all_prefix_rows: list[dict] = []

    for app_du, group in service_df.groupby("app_du"):
        values = group.sort_values("minute_index")["service_cpu_used_cores_proxy"].to_numpy(dtype=float)
        prefix, _, split_idx = split_series(values, train_ratio, valid_ratio)
        load_mean = float(np.mean(prefix))
        burst_std = float(np.std(prefix, ddof=1)) if len(prefix) > 1 else 0.0
        burst_cv = burst_std / max(load_mean, 1e-9)
        peak_to_mean = float(np.max(prefix) / max(load_mean, 1e-9)) if len(prefix) else 0.0
        all_prefix_rows.append(
            {
                "app_du": app_du,
                "load_mean_prefix": load_mean,
                "burst_cv_prefix": burst_cv,
                "peak_to_mean_prefix": peak_to_mean,
            }
        )
        if app_du not in fixed_app_to_role:
            continue
        if app_du not in summary_lookup.index:
            raise KeyError(f"Missing service summary row for selected service {app_du}")
        summary_row = summary_lookup.loc[app_du]
        rows.append(
            {
                "selection_role": fixed_app_to_role[app_du],
                "app_du": app_du,
                "prefix_rows": int(len(prefix)),
                "train_valid_split_end": int(split_idx),
                "load_mean_prefix": load_mean,
                "burst_cv_prefix": burst_cv,
                "peak_to_mean_prefix": peak_to_mean,
                "selection_rule": selection_rule,
                "coverage_ratio_metadata_only": float(summary_row["coverage_ratio"]),
                "median_container_request_cores": float(summary_row["median_container_request_cores"]),
                "mean_container_request_cores": float(summary_row["mean_container_request_cores"]),
            }
        )

    profile_df = pd.DataFrame(rows)
    all_prefix_df = pd.DataFrame(all_prefix_rows)
    if not all_prefix_df.empty:
        profile_df["all_service_load_median_prefix"] = float(all_prefix_df["load_mean_prefix"].median())
        profile_df["all_service_burst_cv_median_prefix"] = float(all_prefix_df["burst_cv_prefix"].median())
        profile_df["all_service_peak_to_mean_median_prefix"] = float(
            all_prefix_df["peak_to_mean_prefix"].median()
        )
        profile_df["eligible_service_count_prefix_only"] = int(len(all_prefix_df))

    role_order = list(CALIBRATION_SERVICE_ROLES)
    profile_df["selection_role"] = pd.Categorical(profile_df["selection_role"], categories=role_order, ordered=True)
    profile_df = profile_df.sort_values("selection_role").reset_index(drop=True)
    profile_df["selection_role"] = profile_df["selection_role"].astype(str)

    gate_failures = []
    if len(profile_df) != len(CALIBRATION_SERVICE_ROLES):
        gate_failures.append(f"selection trace has {len(profile_df)} services, expected 10")
    missing_roles = sorted(set(CALIBRATION_SERVICE_ROLES) - set(profile_df["selection_role"]))
    if missing_roles:
        gate_failures.append(f"selection trace missing roles: {', '.join(missing_roles)}")
    return profile_df, gate_failures


def service_request_cores(service_meta: dict) -> tuple[float, str, bool]:
    median_request = float(service_meta["median_container_request_cores"])
    if median_request > 0.0:
        return max(median_request, 0.1), "median_container_request_cores", False
    mean_request = float(service_meta["mean_container_request_cores"])
    return max(mean_request, 0.1), "mean_container_request_cores", True


def evaluate_service_task(task: dict) -> dict:
    app_du = task["app_du"]
    selection_role = task["selection_role"]
    series = np.asarray(task["series"], dtype=float)
    service_meta = task["service_meta"]
    context_window = int(task["context_window"])
    horizons = list(task["horizons"])
    train_ratio = float(task["train_ratio"])
    valid_ratio = float(task["valid_ratio"])
    policy_config = task["policy_config"]
    alpha = float(task["alpha"])
    solver = str(task["solver"])
    planned_worker = int(task["planned_worker"])
    process_id = os.getpid()
    wall_start = time.perf_counter()

    thread_context = threadpool_limits(limits=1) if threadpool_limits is not None else nullcontext()
    with thread_context:
        train_series, test_series, split_idx = split_series(series, train_ratio, valid_ratio)
        forecast_rows: list[dict] = []
        prediction_rows: list[dict] = []
        policy_rows: list[dict] = []
        policy_series_rows: list[dict] = []
        gate_failures: list[str] = []
        result_by_horizon = {}

        for horizon in horizons:
            fit_start = time.perf_counter()
            result = quantile_linear_regression(
                train_series,
                test_series,
                context_window,
                horizon,
                alpha=alpha,
                solver=solver,
            )
            fit_eval_ms = (time.perf_counter() - fit_start) * 1000.0
            result_by_horizon[horizon] = result

            y_true = result.y_true
            p50 = result.p50
            raw_p90 = result.raw_p90 if result.raw_p90 is not None else result.p90
            guarded_p90 = result.p90_guarded
            raw_crossing_count = int(np.sum(raw_p90 < p50))
            guarded_crossing_count = int(np.sum(guarded_p90 < p50))
            raw_crossing_rate = float(raw_crossing_count / max(len(y_true), 1))
            guarded_crossing_rate = float(guarded_crossing_count / max(len(y_true), 1))
            p50_pinball = pinball(y_true, p50, 0.5)
            p90_raw_pinball = pinball(y_true, raw_p90, 0.9)
            p90_guarded_pinball = pinball(y_true, guarded_p90, 0.9)

            forecast_row = {
                "app_du": app_du,
                "selection_role": selection_role,
                "model_name": MODEL_NAME,
                "horizon": horizon,
                "train_valid_split_end": split_idx,
                "n_predictions": int(len(y_true)),
                "mae": mae(y_true, p50),
                "rmse": rmse(y_true, p50),
                "mape": mape(y_true, p50),
                "p50_pinball": p50_pinball,
                "p90_raw_pinball": p90_raw_pinball,
                "p90_guarded_pinball": p90_guarded_pinball,
                "mean_guarded_pinball": 0.5 * (p50_pinball + p90_guarded_pinball),
                "p50_coverage": float(np.mean(y_true <= p50)),
                "p90_raw_coverage": float(np.mean(y_true <= raw_p90)),
                "p90_guarded_coverage": float(np.mean(y_true <= guarded_p90)),
                "raw_interval_width": float(np.mean(raw_p90 - p50)),
                "guarded_interval_width": float(np.mean(guarded_p90 - p50)),
                "raw_crossing_count": raw_crossing_count,
                "raw_crossing_rate": raw_crossing_rate,
                "guarded_crossing_count": guarded_crossing_count,
                "guarded_crossing_rate": guarded_crossing_rate,
                "fit_eval_ms": fit_eval_ms,
            }
            row_pass = (
                len(y_true) > 0
                and len(y_true) == len(p50) == len(raw_p90) == len(guarded_p90)
                and guarded_crossing_count == 0
                and finite_values(
                    [
                        forecast_row["mae"],
                        forecast_row["rmse"],
                        forecast_row["mape"],
                        forecast_row["p50_pinball"],
                        forecast_row["p90_raw_pinball"],
                        forecast_row["p90_guarded_pinball"],
                        forecast_row["p50_coverage"],
                        forecast_row["p90_raw_coverage"],
                        forecast_row["p90_guarded_coverage"],
                        forecast_row["raw_interval_width"],
                        forecast_row["guarded_interval_width"],
                        forecast_row["raw_crossing_rate"],
                        forecast_row["guarded_crossing_rate"],
                    ]
                )
            )
            forecast_row["status"] = "pass" if row_pass else "fail"
            forecast_rows.append(forecast_row)
            if not row_pass:
                gate_failures.append(f"{app_du} horizon {horizon} failed forecasting gate")

            source_test_row_index = np.arange(len(y_true)) + context_window + horizon - 1
            prediction_rows.extend(
                {
                    "app_du": app_du,
                    "selection_role": selection_role,
                    "horizon": horizon,
                    "aligned_test_index": int(idx),
                    "source_test_row_index": int(source_idx),
                    "y_true": float(actual),
                    "p50_raw": float(median_pred),
                    "p90_raw": float(raw_upper),
                    "p90_guarded": float(guarded_upper),
                    "raw_crossing": bool(raw_upper < median_pred),
                    "guarded_crossing": bool(guarded_upper < median_pred),
                }
                for idx, source_idx, actual, median_pred, raw_upper, guarded_upper in zip(
                    range(len(y_true)),
                    source_test_row_index,
                    y_true,
                    p50,
                    raw_p90,
                    guarded_p90,
                )
            )

        policy_horizon = 5 if 5 in horizons else horizons[min(1, len(horizons) - 1)]
        result = result_by_horizon[policy_horizon]
        actual_series = result.y_true
        p50 = result.p50
        guarded_p90 = result.p90_guarded
        request_cores, request_source, request_fallback_used = service_request_cores(service_meta)
        headroom_ratio = float(policy_config["headroom_ratio"])
        actual_equivalent_replicas = actual_series / request_cores
        forecast_p50_replicas = p50 / request_cores
        forecast_p90_replicas = guarded_p90 / request_cores

        reactive_capacity, reactive_metrics = run_reactive(
            actual_load=actual_equivalent_replicas,
            upper_threshold=float(policy_config["reactive_upper_threshold"]),
            lower_threshold=float(policy_config["reactive_lower_threshold"]),
            min_capacity=1.0,
            max_step_change=1.0,
        )
        lagged_capacity, lagged_metrics = run_lagged_target_tracking(
            actual_load=actual_equivalent_replicas * (1.0 + headroom_ratio),
            min_capacity=1.0,
            max_step_change=1.0,
        )
        predictive_capacity, predictive_metrics = run_predictive(
            actual_load=actual_equivalent_replicas * (1.0 + headroom_ratio),
            forecast_p50=forecast_p50_replicas * (1.0 + headroom_ratio),
            forecast_p90=forecast_p90_replicas
            * (1.0 + headroom_ratio)
            * (1.0 + float(policy_config["scale_out_quantile_margin"])),
            min_capacity=1.0,
            cooldown_steps=int(policy_config["cooldown_steps"]),
            max_step_change=1.0,
            scale_in_safety_margin=float(policy_config["scale_in_safety_margin"]),
        )

        for policy_name, metrics in [
            ("reactive_service", reactive_metrics),
            ("lagged_tracking_service", lagged_metrics),
            ("qlr_predictive_service", predictive_metrics),
        ]:
            policy_rows.append(
                {
                    "app_du": app_du,
                    "selection_role": selection_role,
                    "policy_name": policy_name,
                    "model_name": MODEL_NAME if policy_name == "qlr_predictive_service" else "n/a",
                    "horizon": policy_horizon,
                    "request_cores_source": request_source,
                    "request_cores_used": request_cores,
                    "request_fallback_used": request_fallback_used,
                    "sla_violation": metrics.sla_violation,
                    "over_provisioning": metrics.over_provisioning,
                    "under_provisioning": metrics.under_provisioning,
                    "scaling_actions": metrics.scaling_actions,
                    "average_capacity": metrics.average_capacity,
                }
            )
            if not finite_values(
                [
                    metrics.sla_violation,
                    metrics.over_provisioning,
                    metrics.under_provisioning,
                    metrics.scaling_actions,
                    metrics.average_capacity,
                ]
            ):
                gate_failures.append(f"{app_du} {policy_name} has non-finite policy metrics")
            if not 0.0 <= float(metrics.sla_violation) <= 1.0:
                gate_failures.append(f"{app_du} {policy_name} has out-of-range SLA violation")

        for idx in range(len(actual_series)):
            policy_series_rows.append(
                {
                    "app_du": app_du,
                    "selection_role": selection_role,
                    "policy_horizon": policy_horizon,
                    "aligned_test_index": idx,
                    "request_cores_source": request_source,
                    "request_cores_used": request_cores,
                    "actual_equivalent_replicas": float(actual_equivalent_replicas[idx]),
                    "actual_headroom_replicas": float(actual_equivalent_replicas[idx] * (1.0 + headroom_ratio)),
                    "reactive_capacity": float(reactive_capacity[idx]),
                    "lagged_capacity": float(lagged_capacity[idx]),
                    "qlr_predictive_capacity": float(predictive_capacity[idx]),
                    "qlr_forecast_p50_replicas": float(forecast_p50_replicas[idx]),
                    "qlr_forecast_p90_replicas": float(forecast_p90_replicas[idx]),
                }
            )

        capacity_values = np.column_stack([reactive_capacity, lagged_capacity, predictive_capacity])
        if not np.all(np.isfinite(capacity_values)):
            gate_failures.append(f"{app_du} policy capacity series contains non-finite values")
        if np.any(capacity_values < 0.0):
            gate_failures.append(f"{app_du} policy capacity series contains negative values")

    runtime_wall_ms = (time.perf_counter() - wall_start) * 1000.0
    resource_trace = {
        "app_du": app_du,
        "selection_role": selection_role,
        "planned_worker": planned_worker,
        "process_id": process_id,
        "runtime_wall_ms": runtime_wall_ms,
        "fit_eval_ms_sum": float(sum(row["fit_eval_ms"] for row in forecast_rows)),
        "forecast_rows": len(forecast_rows),
        "prediction_rows": len(prediction_rows),
        "policy_rows": len(policy_rows),
        "policy_series_rows": len(policy_series_rows),
        "estimated_service_artifact_bytes": (
            frame_size_bytes(forecast_rows)
            + frame_size_bytes(prediction_rows)
            + frame_size_bytes(policy_rows)
            + frame_size_bytes(policy_series_rows)
        ),
        "gate_failure_count": len(gate_failures),
    }
    return {
        "forecast_rows": forecast_rows,
        "prediction_rows": prediction_rows,
        "policy_rows": policy_rows,
        "policy_series_rows": policy_series_rows,
        "resource_trace": resource_trace,
        "gate_failures": gate_failures,
        "request_fallback_used": request_fallback_used,
    }


def summarize_outputs(
    forecast_df: pd.DataFrame,
    policy_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    forecast_summary = (
        forecast_df.groupby(["model_name", "horizon"])
        .agg(
            service_count=("app_du", "nunique"),
            mae_mean=("mae", "mean"),
            mae_std=("mae", "std"),
            rmse_mean=("rmse", "mean"),
            mape_mean=("mape", "mean"),
            p50_coverage_mean=("p50_coverage", "mean"),
            p90_raw_coverage_mean=("p90_raw_coverage", "mean"),
            p90_guarded_coverage_mean=("p90_guarded_coverage", "mean"),
            raw_crossing_count_sum=("raw_crossing_count", "sum"),
            guarded_crossing_count_sum=("guarded_crossing_count", "sum"),
            fit_eval_ms_mean=("fit_eval_ms", "mean"),
        )
        .reset_index()
        .sort_values(["horizon", "model_name"])
    )
    policy_summary = (
        policy_df.groupby("policy_name")
        .agg(
            service_count=("app_du", "nunique"),
            sla_violation_mean=("sla_violation", "mean"),
            over_provisioning_mean=("over_provisioning", "mean"),
            under_provisioning_mean=("under_provisioning", "mean"),
            scaling_actions_mean=("scaling_actions", "mean"),
            average_capacity_mean=("average_capacity", "mean"),
        )
        .reset_index()
    )
    pivot = policy_df.pivot(index="app_du", columns="policy_name")
    delta_rows = []
    for app_du in sorted(policy_df["app_du"].unique()):
        delta_rows.append(
            {
                "app_du": app_du,
                "sla_violation_predictive_minus_reactive": float(
                    pivot.loc[app_du, ("sla_violation", "qlr_predictive_service")]
                    - pivot.loc[app_du, ("sla_violation", "reactive_service")]
                ),
                "over_provisioning_predictive_minus_reactive": float(
                    pivot.loc[app_du, ("over_provisioning", "qlr_predictive_service")]
                    - pivot.loc[app_du, ("over_provisioning", "reactive_service")]
                ),
                "scaling_actions_predictive_minus_reactive": float(
                    pivot.loc[app_du, ("scaling_actions", "qlr_predictive_service")]
                    - pivot.loc[app_du, ("scaling_actions", "reactive_service")]
                ),
            }
        )
    return forecast_summary, policy_summary, pd.DataFrame(delta_rows)


def write_report(
    output_dir: Path,
    selection_df: pd.DataFrame,
    forecast_summary_df: pd.DataFrame,
    policy_summary_df: pd.DataFrame,
    resource_trace_df: pd.DataFrame,
    gate_failures: list[str],
    metrics_hash_before: str | None,
    metrics_hash_after: str | None,
    full_result_dir: Path,
    num_workers: int,
    fallback_services: list[str],
) -> Path:
    status = "pass" if not gate_failures else "fail"
    report_lines = [
        "# QLR 10-Service Calibration Report",
        "",
        f"- run_id: `{RUN_ID}`",
        f"- status: `{status}`",
        f"- num_workers: `{num_workers}`",
        f"- selected_services: `{', '.join(selection_df['app_du'].tolist())}`",
        f"- metrics_csv_hash_before: `{metrics_hash_before}`",
        f"- metrics_csv_hash_after: `{metrics_hash_after}`",
        f"- full_result_dir_exists: `{full_result_dir.exists()}`",
        "",
        "## Scope Boundary",
        "",
        "This is a 10-service calibration only. It does not run the full 139-service experiment, does not invoke Full UA-MSTCN, and does not change the manuscript headline conclusion. Calibration pass does not automatically start full 139-service.",
        "",
        "## Selection Discipline",
        "",
        "The ten services are fixed from train+validation-prefix load, burst, and peak-to-mean descriptors. Test outcomes and full-span summary descriptors are not used for selection.",
        "The test split is used only for evaluation; QLR fitting uses the train+validation prefix only, and test data are not used for parameter, model, service, or policy selection.",
        "",
        "## Policy Parameter Reuse",
        "",
        "The calibration reuses the existing service-policy semantics: service `min_capacity=1.0`, service `max_step_change=1.0`, config-driven headroom, quantile margin, scale-in safety, cooldown, and reactive thresholds.",
        "",
        "## Replica Conversion Source",
        "",
        "`median_container_request_cores` is read from the service summary only for replica conversion, not for service selection.",
    ]
    if fallback_services:
        report_lines.append(f"Fallback to `mean_container_request_cores` was used for: `{', '.join(fallback_services)}`.")
    else:
        report_lines.append("No selected service required fallback from `median_container_request_cores`.")
    report_lines.extend(
        [
            "",
            "## Gate Checks",
            "",
            "- Exactly 10 services and all required selection roles are present.",
            "- Raw P90 and guarded P90 fields are written to artifacts.",
            "- Raw crossing count/rate are recorded; guarded crossing must be zero.",
            "- Forecasting and policy metrics must be finite.",
            "- Policy SLA violation must be in [0, 1] and capacities must be non-negative.",
            "- Resource trace records runtime, worker id, output row counts, and estimated artifact size.",
            "- `metrics.csv` must remain unchanged.",
            "- `experiments/results/qlr_service_broad/` must not be created.",
            "- Calibration pass does not automatically start full 139-service.",
            "",
        ]
    )
    if gate_failures:
        report_lines.extend(["## Gate Failures", ""])
        report_lines.extend(f"- {failure}" for failure in gate_failures)
        report_lines.append("")
    report_lines.extend(
        [
            "## Selection Profile",
            "",
            "```csv",
            selection_df.to_csv(index=False, lineterminator="\n").strip(),
            "```",
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
    report_path = output_dir / "qlr_service_calibration_report.md"
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    return report_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--service-csv", type=Path, default=None)
    parser.add_argument("--service-summary-csv", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--num-workers", type=int, default=2)
    parser.add_argument("--alpha", type=float, default=1e-4)
    parser.add_argument("--solver", type=str, default="highs")
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
        args.output_dir or (repo_root / "experiments" / "results" / "qlr_service_calibration_10"),
        repo_root,
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    metrics_path = resolve_workbench_path(config["output"]["metrics_csv"], repo_root)
    metrics_hash_before = sha256_file(metrics_path)
    full_result_dir = repo_root / "experiments" / "results" / "qlr_service_broad"

    selected_apps = set(CALIBRATION_SERVICE_ROLES.values())
    service_df = pd.read_csv(
        service_csv,
        usecols=["app_du", "minute_index", "service_cpu_used_cores_proxy"],
    )
    selected_service_df = service_df[service_df["app_du"].isin(selected_apps)].copy()
    summary_df = pd.read_csv(summary_csv)
    selection_df, gate_failures = build_selection_profile(
        service_df,
        summary_df,
        float(config["forecast"]["train_ratio"]),
        float(config["forecast"]["valid_ratio"]),
    )
    selection_df.to_csv(output_dir / "calibration_selection_profile.csv", index=False)

    if int(args.num_workers) != 2:
        gate_failures.append("10-service calibration gate requires --num-workers 2")

    summary_lookup = summary_df.set_index("app_du")
    tasks = []
    for idx, (role, app_du) in enumerate(CALIBRATION_SERVICE_ROLES.items()):
        group = selected_service_df[selected_service_df["app_du"] == app_du].sort_values("minute_index")
        if group.empty:
            gate_failures.append(f"selected service {app_du} has no rows in service CSV")
            continue
        tasks.append(
            {
                "app_du": app_du,
                "selection_role": role,
                "series": group["service_cpu_used_cores_proxy"].to_numpy(dtype=float),
                "service_meta": summary_lookup.loc[app_du].to_dict(),
                "context_window": int(config["forecast"]["context_window"]),
                "horizons": list(config["forecast"]["horizons"]),
                "train_ratio": float(config["forecast"]["train_ratio"]),
                "valid_ratio": float(config["forecast"]["valid_ratio"]),
                "policy_config": config["policy"],
                "alpha": float(args.alpha),
                "solver": str(args.solver),
                "planned_worker": idx % max(1, int(args.num_workers)),
            }
        )

    forecast_rows: list[dict] = []
    prediction_rows: list[dict] = []
    policy_rows: list[dict] = []
    policy_series_rows: list[dict] = []
    resource_rows: list[dict] = []
    fallback_services: list[str] = []

    max_workers = max(1, int(args.num_workers))
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(evaluate_service_task, task): task["app_du"] for task in tasks}
        for future in as_completed(futures):
            result = future.result()
            forecast_rows.extend(result["forecast_rows"])
            prediction_rows.extend(result["prediction_rows"])
            policy_rows.extend(result["policy_rows"])
            policy_series_rows.extend(result["policy_series_rows"])
            resource_rows.append(result["resource_trace"])
            gate_failures.extend(result["gate_failures"])
            if result["request_fallback_used"]:
                fallback_services.append(futures[future])

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
    resource_trace_df.to_csv(output_dir / "calibration_resource_trace.csv", index=False)

    if len(set(forecast_df["app_du"])) != 10:
        gate_failures.append("forecast artifacts do not contain exactly 10 services")
    if set(selection_df["selection_role"]) != set(CALIBRATION_SERVICE_ROLES):
        gate_failures.append("selection roles do not match the calibration role set")
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
    if len(resource_trace_df) != 10:
        gate_failures.append("resource trace does not contain exactly 10 services")
    for column in [
        "runtime_wall_ms",
        "planned_worker",
        "forecast_rows",
        "prediction_rows",
        "policy_rows",
        "policy_series_rows",
        "estimated_service_artifact_bytes",
    ]:
        if column not in resource_trace_df.columns:
            gate_failures.append(f"resource trace missing column {column}")

    metrics_hash_after = sha256_file(metrics_path)
    if metrics_hash_before != metrics_hash_after:
        gate_failures.append("metrics.csv changed during calibration")
    if full_result_dir.exists():
        gate_failures.append(f"full 139-service result directory exists: {full_result_dir}")

    report_path = write_report(
        output_dir,
        selection_df,
        forecast_summary_df,
        policy_summary_df,
        resource_trace_df,
        gate_failures,
        metrics_hash_before,
        metrics_hash_after,
        full_result_dir,
        max_workers,
        fallback_services,
    )
    if gate_failures:
        raise SystemExit(f"QLR service calibration gate failed; see {report_path}")


if __name__ == "__main__":
    main()
