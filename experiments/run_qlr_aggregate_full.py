#!/usr/bin/env python3
"""Run aggregate QLR forecasting and policy evaluation after the smoke gate."""

from __future__ import annotations

import argparse
import csv
from io import StringIO
import time
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from models.baselines import quantile_linear_regression
from policies.autoscaling_simulator import (
    required_capacity,
    run_lagged_target_tracking,
    run_predictive,
    run_reactive,
)


RUN_ID = "qlr_aggregate_full_20260427"
MODEL_NAME = "quantile_linear_regression"


def resolve_workbench_path(path: str | Path, repo_root: Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute() or candidate.exists():
        return candidate
    parts = candidate.parts
    if parts and parts[0] == repo_root.name:
        return repo_root.parent / candidate
    return repo_root / candidate


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


def split_series(series: np.ndarray, train_ratio: float, valid_ratio: float) -> tuple[np.ndarray, np.ndarray]:
    valid_end = int(len(series) * (train_ratio + valid_ratio))
    return series[:valid_end], series[valid_end:]


def finite_values(values: list[float]) -> bool:
    return bool(np.all(np.isfinite(np.asarray(values, dtype=float))))


def append_metrics_conservatively(metrics_csv: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError("No QLR rows were provided for metrics.csv update.")
    incoming_ids = [str(row["experiment_id"]) for row in rows]
    bad_ids = [
        experiment_id
        for experiment_id in incoming_ids
        if not experiment_id.startswith("qlr-")
    ]
    if bad_ids:
        raise ValueError(f"Refusing conservative metrics update for non-QLR ids: {bad_ids}")

    metrics_csv.parent.mkdir(parents=True, exist_ok=True)
    if metrics_csv.exists() and metrics_csv.stat().st_size:
        existing_lines = metrics_csv.read_text(encoding="utf-8").splitlines()
        header_line = existing_lines[0]
        fieldnames = header_line.split(",")
        preserved_lines = [header_line]
        incoming_id_set = set(incoming_ids)
        for line in existing_lines[1:]:
            experiment_id = line.split(",", 1)[0]
            if experiment_id not in incoming_id_set:
                preserved_lines.append(line)
    else:
        fieldnames = list(rows[0].keys())
        preserved_lines = [",".join(fieldnames)]

    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n", extrasaction="ignore")
    for row in rows:
        writer.writerow({field: row.get(field, "") for field in fieldnames})
    incoming_lines = buffer.getvalue().splitlines()
    metrics_csv.write_text("\n".join(preserved_lines + incoming_lines) + "\n", encoding="utf-8")


def forecasting_rows(
    train_series: np.ndarray,
    test_series: np.ndarray,
    context_window: int,
    horizons: list[int],
    alpha: float,
    solver: str,
) -> tuple[pd.DataFrame, pd.DataFrame, list[dict], list[str]]:
    metrics_rows: list[dict] = []
    prediction_rows: list[dict] = []
    central_rows: list[dict] = []
    gate_failures: list[str] = []

    for horizon in horizons:
        t0 = time.perf_counter()
        result = quantile_linear_regression(
            train_series,
            test_series,
            context_window,
            horizon,
            alpha=alpha,
            solver=solver,
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        y_true = result.y_true
        p50 = result.p50
        raw_p90 = result.raw_p90 if result.raw_p90 is not None else result.p90
        guarded_p90 = result.p90_guarded
        raw_crossing_count = int(np.sum(raw_p90 < p50))
        guarded_crossing_count = int(np.sum(guarded_p90 < p50))
        raw_crossing_rate = float(raw_crossing_count / max(len(y_true), 1))
        guarded_crossing_rate = float(guarded_crossing_count / max(len(y_true), 1))
        p50_pinball = pinball(y_true, p50, 0.5)
        p90_pinball = pinball(y_true, guarded_p90, 0.9)

        row = {
            "horizon": horizon,
            "n_predictions": int(len(y_true)),
            "mae": mae(y_true, p50),
            "rmse": rmse(y_true, p50),
            "mape": mape(y_true, p50),
            "p50_pinball": p50_pinball,
            "p90_pinball": p90_pinball,
            "mean_pinball": 0.5 * (p50_pinball + p90_pinball),
            "p50_coverage": float(np.mean(y_true <= p50)),
            "p90_raw_coverage": float(np.mean(y_true <= raw_p90)),
            "p90_guarded_coverage": float(np.mean(y_true <= guarded_p90)),
            "raw_interval_width": float(np.mean(raw_p90 - p50)),
            "guarded_interval_width": float(np.mean(guarded_p90 - p50)),
            "raw_crossing_count": raw_crossing_count,
            "raw_crossing_rate": raw_crossing_rate,
            "guarded_crossing_count": guarded_crossing_count,
            "guarded_crossing_rate": guarded_crossing_rate,
            "fit_eval_ms": elapsed_ms,
        }
        row_pass = (
            len(y_true) > 0
            and len(y_true) == len(p50) == len(raw_p90) == len(guarded_p90)
            and guarded_crossing_count == 0
            and finite_values(
                [
                    row["mae"],
                    row["rmse"],
                    row["mape"],
                    row["p50_pinball"],
                    row["p90_pinball"],
                    row["p50_coverage"],
                    row["p90_raw_coverage"],
                    row["p90_guarded_coverage"],
                    row["raw_interval_width"],
                    row["guarded_interval_width"],
                    row["raw_crossing_rate"],
                    row["guarded_crossing_rate"],
                ]
            )
        )
        row["status"] = "pass" if row_pass else "fail"
        metrics_rows.append(row)
        if not row_pass:
            gate_failures.append(f"horizon {horizon} failed forecasting gate")

        source_test_row_index = np.arange(len(y_true)) + context_window + horizon - 1
        prediction_rows.extend(
            {
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
        central_rows.append(
            {
                "experiment_id": f"qlr-aggregate-forecast-h{horizon}",
                "dataset_split": "test",
                "model_name": MODEL_NAME,
                "policy_name": "",
                "horizon": horizon,
                "mae": row["mae"],
                "rmse": row["rmse"],
                "mape": row["mape"],
                "pinball_loss": row["mean_pinball"],
                "sla_violation": "",
                "over_provisioning": "",
                "under_provisioning": "",
                "scaling_actions": "",
                "latency_ms": elapsed_ms,
            }
        )

    return pd.DataFrame(metrics_rows), pd.DataFrame(prediction_rows), central_rows, gate_failures


def policy_rows(
    train_series: np.ndarray,
    test_series: np.ndarray,
    config: dict,
    context_window: int,
    horizons: list[int],
    alpha: float,
    solver: str,
) -> tuple[pd.DataFrame, pd.DataFrame, list[dict], list[str]]:
    policy_config = config["policy"]
    chosen_horizon = horizons[min(1, len(horizons) - 1)]
    result = quantile_linear_regression(
        train_series,
        test_series,
        context_window,
        chosen_horizon,
        alpha=alpha,
        solver=solver,
    )
    aligned_actual = result.y_true
    p50 = result.p50
    guarded_p90 = result.p90_guarded

    required = required_capacity(
        aligned_actual,
        headroom_ratio=float(policy_config["headroom_ratio"]),
        min_capacity=float(policy_config["min_capacity"]),
    )
    forecast_p50_required = required_capacity(
        p50,
        headroom_ratio=float(policy_config["headroom_ratio"]),
        min_capacity=float(policy_config["min_capacity"]),
    )
    forecast_p90_required = required_capacity(
        guarded_p90,
        headroom_ratio=float(policy_config["headroom_ratio"]),
        min_capacity=float(policy_config["min_capacity"]),
    )
    forecast_p90_required = forecast_p90_required * (
        1.0 + float(policy_config["scale_out_quantile_margin"])
    )

    reactive_capacity, reactive_metrics = run_reactive(
        actual_load=required,
        upper_threshold=float(policy_config["reactive_upper_threshold"]),
        lower_threshold=float(policy_config["reactive_lower_threshold"]),
        min_capacity=float(policy_config["min_capacity"]),
        max_step_change=float(policy_config["max_step_change"]),
    )
    lagged_capacity, lagged_metrics = run_lagged_target_tracking(
        actual_load=required,
        min_capacity=float(policy_config["min_capacity"]),
        max_step_change=float(policy_config["max_step_change"]),
    )
    predictive_capacity, predictive_metrics = run_predictive(
        actual_load=required,
        forecast_p50=forecast_p50_required,
        forecast_p90=forecast_p90_required,
        min_capacity=float(policy_config["min_capacity"]),
        cooldown_steps=int(policy_config["cooldown_steps"]),
        max_step_change=float(policy_config["max_step_change"]),
        scale_in_safety_margin=float(policy_config["scale_in_safety_margin"]),
    )

    policy_specs = [
        ("qlr-policy-reactive", "n/a", "reactive_threshold", reactive_metrics),
        ("qlr-policy-lagged-tracking", "n/a", "lagged_target_tracking", lagged_metrics),
        ("qlr-policy-predictive", MODEL_NAME, "predictive_uncertainty_aware_qlr", predictive_metrics),
    ]
    metric_rows = [
        {
            "experiment_id": experiment_id,
            "dataset_split": "test",
            "model_name": model_name,
            "policy_name": policy_name,
            "horizon": chosen_horizon,
            "sla_violation": metrics.sla_violation,
            "over_provisioning": metrics.over_provisioning,
            "under_provisioning": metrics.under_provisioning,
            "scaling_actions": metrics.scaling_actions,
            "average_capacity": metrics.average_capacity,
        }
        for experiment_id, model_name, policy_name, metrics in policy_specs
    ]
    central_rows = [
        {
            "experiment_id": row["experiment_id"],
            "dataset_split": row["dataset_split"],
            "model_name": row["model_name"],
            "policy_name": row["policy_name"],
            "horizon": row["horizon"],
            "mae": "",
            "rmse": "",
            "mape": "",
            "pinball_loss": "",
            "sla_violation": row["sla_violation"],
            "over_provisioning": row["over_provisioning"],
            "under_provisioning": row["under_provisioning"],
            "scaling_actions": row["scaling_actions"],
            "latency_ms": "",
        }
        for row in metric_rows
    ]
    series_df = pd.DataFrame(
        {
            "actual_required_capacity": required,
            "reactive_capacity": reactive_capacity,
            "lagged_capacity": lagged_capacity,
            "qlr_predictive_capacity": predictive_capacity,
            "qlr_forecast_p50_required": forecast_p50_required,
            "qlr_forecast_p90_required": forecast_p90_required,
        }
    )

    gate_failures = []
    for row in metric_rows:
        finite_metric_values = [
            row["sla_violation"],
            row["over_provisioning"],
            row["under_provisioning"],
            row["scaling_actions"],
            row["average_capacity"],
        ]
        if not finite_values(finite_metric_values):
            gate_failures.append(f"{row['experiment_id']} has non-finite policy metrics")
        if not 0.0 <= float(row["sla_violation"]) <= 1.0:
            gate_failures.append(f"{row['experiment_id']} has out-of-range SLA violation")
    if not np.all(np.isfinite(series_df.to_numpy(dtype=float))):
        gate_failures.append("policy series contains non-finite values")
    if np.any(series_df[["reactive_capacity", "lagged_capacity", "qlr_predictive_capacity"]].to_numpy() < 0.0):
        gate_failures.append("policy series contains negative capacity")

    return pd.DataFrame(metric_rows), series_df, central_rows, gate_failures


def write_report(
    output_dir: Path,
    csv_path: Path,
    metrics_path: Path,
    forecasting_df: pd.DataFrame,
    policy_df: pd.DataFrame,
    gate_failures: list[str],
    split_idx: int,
    train_rows: int,
    test_rows: int,
    context_window: int,
    horizons: list[int],
    alpha: float,
    solver: str,
    central_metrics_updated: bool,
) -> Path:
    status = "pass" if not gate_failures else "fail"
    report_lines = [
        "# Aggregate QLR Full Report",
        "",
        f"- run_id: `{RUN_ID}`",
        f"- series_path: `{csv_path}`",
        f"- train_plus_validation_rows_used_for_fit: `{train_rows}`",
        f"- heldout_test_rows_used_for_evaluation: `{test_rows}`",
        f"- split_index: `{split_idx}`",
        f"- context_window: `{context_window}`",
        f"- horizons: `{', '.join(str(horizon) for horizon in horizons)}`",
        f"- alpha: `{alpha}`",
        f"- solver: `{solver}`",
        f"- status: `{status}`",
        f"- central_metrics_updated: `{central_metrics_updated}`",
        f"- central_metrics_csv: `{metrics_path}`",
        "",
        "## Split Discipline",
        "",
        "The held-out test split is used only for evaluation. QLR fitting uses only the train+validation prefix. No test rows are used to select parameters, choose a model, or tune the policy.",
        "",
        "## Gate Checks",
        "",
        "- y_true, P50, raw P90, and guarded P90 predictions are nonempty and length-aligned.",
        "- Raw crossing count and raw crossing rate are recorded before applying the non-crossing guard.",
        "- Guarded P90 is computed as `max(raw_p90, p50)` and must have zero crossing violations.",
        "- Forecasting metrics and policy metrics must be finite.",
        "- Policy SLA violation must be within [0, 1].",
        "- `metrics.csv` is updated only after all gates pass, and only `qlr-*` experiment ids are added or replaced.",
        "",
    ]
    if gate_failures:
        report_lines.extend(["## Gate Failures", ""])
        report_lines.extend(f"- {failure}" for failure in gate_failures)
        report_lines.append("")
    report_lines.extend(
        [
            "## Forecasting Metrics",
            "",
            "```csv",
            forecasting_df.to_csv(index=False, lineterminator="\n").strip(),
            "```",
            "",
            "## Policy Metrics",
            "",
            "```csv",
            policy_df.to_csv(index=False, lineterminator="\n").strip(),
            "```",
        ]
    )
    report_path = output_dir / "aggregate_qlr_full_report.md"
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    return report_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--alpha", type=float, default=1e-4)
    parser.add_argument("--solver", type=str, default="highs")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    with args.config.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    csv_path = resolve_workbench_path(config["dataset"]["output_series_csv"], repo_root)
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing prepared aggregate series: {csv_path}")

    output_dir = args.output_dir or (repo_root / "experiments" / "results" / "qlr_aggregate_full")
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(csv_path)
    series_pct = df["cluster_cpu_utilization_mean"].to_numpy(dtype=float)
    series_norm = series_pct / 100.0
    context_window = int(config["forecast"]["context_window"])
    horizons = list(config["forecast"]["horizons"])
    train_ratio = float(config["forecast"]["train_ratio"])
    valid_ratio = float(config["forecast"]["valid_ratio"])
    split_idx = int(len(series_pct) * (train_ratio + valid_ratio))

    train_pct, test_pct = split_series(series_pct, train_ratio, valid_ratio)
    train_norm, test_norm = split_series(series_norm, train_ratio, valid_ratio)

    forecasting_df, predictions_df, central_forecast_rows, forecast_gate_failures = forecasting_rows(
        train_pct,
        test_pct,
        context_window,
        horizons,
        args.alpha,
        args.solver,
    )
    policy_df, policy_series_df, central_policy_rows, policy_gate_failures = policy_rows(
        train_norm,
        test_norm,
        config,
        context_window,
        horizons,
        args.alpha,
        args.solver,
    )
    gate_failures = forecast_gate_failures + policy_gate_failures

    forecasting_df.to_csv(output_dir / "aggregate_qlr_forecasting_metrics.csv", index=False)
    predictions_df.to_csv(output_dir / "aggregate_qlr_predictions.csv", index=False)
    policy_df.to_csv(output_dir / "aggregate_qlr_policy_metrics.csv", index=False)
    policy_series_df.to_csv(output_dir / "aggregate_qlr_policy_series.csv", index=False)

    metrics_path = resolve_workbench_path(config["output"]["metrics_csv"], repo_root)
    central_metrics_updated = False
    if not gate_failures:
        append_metrics_conservatively(metrics_path, central_forecast_rows + central_policy_rows)
        central_metrics_updated = True

    report_path = write_report(
        output_dir,
        csv_path,
        metrics_path,
        forecasting_df,
        policy_df,
        gate_failures,
        split_idx,
        len(train_pct),
        len(test_pct),
        context_window,
        horizons,
        args.alpha,
        args.solver,
        central_metrics_updated,
    )
    if gate_failures:
        raise SystemExit(f"QLR aggregate full gate failed; see {report_path}")


if __name__ == "__main__":
    main()
