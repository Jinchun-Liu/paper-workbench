#!/usr/bin/env python3
"""Evaluate reactive and predictive capacity-control policies on a prepared series."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from models.ua_mstcn import UAMSTCN
from policies.autoscaling_simulator import (
    required_capacity,
    run_lagged_target_tracking,
    run_predictive,
    run_reactive,
)


def append_metrics(metrics_csv: Path, rows: list[dict]) -> None:
    existing = pd.read_csv(metrics_csv) if metrics_csv.exists() and metrics_csv.stat().st_size else pd.DataFrame()
    incoming = pd.DataFrame(rows)
    if not existing.empty and "experiment_id" in existing.columns:
        existing = existing[~existing["experiment_id"].isin(incoming["experiment_id"])]
    updated = pd.concat([existing, incoming], ignore_index=True)
    updated.to_csv(metrics_csv, index=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()

    with args.config.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    series_path = Path(config["dataset"]["output_series_csv"])
    if not series_path.exists():
        raise FileNotFoundError(f"Missing prepared series file: {series_path}")

    df = pd.read_csv(series_path)
    # Policy evaluation operates on normalized utilization so threshold and step-size
    # parameters remain in the same unit system as the simulator configuration.
    actual = df["cluster_cpu_utilization_mean"].to_numpy(dtype=float) / 100.0
    context_window = int(config["forecast"]["context_window"])
    horizons = list(config["forecast"]["horizons"])

    split_idx = int(len(actual) * (config["forecast"]["train_ratio"] + config["forecast"]["valid_ratio"]))
    history = actual[:split_idx]
    test = actual[split_idx:]
    if len(test) <= max(horizons) + context_window:
        raise ValueError("Series too short for policy evaluation.")

    model = UAMSTCN(context_window=context_window, horizons=horizons)
    model.fit(history)

    chosen_horizon = horizons[min(1, len(horizons) - 1)]
    horizon_index = horizons.index(chosen_horizon)
    histories, aligned_actual_arr = model.history_matrix(test, chosen_horizon)
    p50_matrix, p90_matrix = model.predict_batch(histories)
    p50_arr = p50_matrix[:, horizon_index]
    p90_arr = p90_matrix[:, horizon_index]
    required = required_capacity(
        aligned_actual_arr,
        headroom_ratio=float(config["policy"]["headroom_ratio"]),
        min_capacity=float(config["policy"]["min_capacity"]),
    )
    forecast_p50_required = required_capacity(
        p50_arr,
        headroom_ratio=float(config["policy"]["headroom_ratio"]),
        min_capacity=float(config["policy"]["min_capacity"]),
    )
    forecast_p90_required = required_capacity(
        p90_arr,
        headroom_ratio=float(config["policy"]["headroom_ratio"]),
        min_capacity=float(config["policy"]["min_capacity"]),
    )
    forecast_p90_required = forecast_p90_required * (1.0 + float(config["policy"]["scale_out_quantile_margin"]))

    reactive_capacity, reactive_metrics = run_reactive(
        actual_load=required,
        upper_threshold=float(config["policy"]["reactive_upper_threshold"]),
        lower_threshold=float(config["policy"]["reactive_lower_threshold"]),
        min_capacity=float(config["policy"]["min_capacity"]),
        max_step_change=float(config["policy"]["max_step_change"]),
    )
    lagged_capacity, lagged_metrics = run_lagged_target_tracking(
        actual_load=required,
        min_capacity=float(config["policy"]["min_capacity"]),
        max_step_change=float(config["policy"]["max_step_change"]),
    )
    predictive_capacity, predictive_metrics = run_predictive(
        actual_load=required,
        forecast_p50=forecast_p50_required,
        forecast_p90=forecast_p90_required,
        min_capacity=float(config["policy"]["min_capacity"]),
        cooldown_steps=int(config["policy"]["cooldown_steps"]),
        max_step_change=float(config["policy"]["max_step_change"]),
        scale_in_safety_margin=float(config["policy"]["scale_in_safety_margin"]),
    )

    figures_dir = Path(config["output"]["forecast_dir"])
    figures_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        {
            "actual_required_capacity": required,
            "reactive_capacity": reactive_capacity,
            "lagged_capacity": lagged_capacity,
            "predictive_capacity": predictive_capacity,
            "forecast_p50": forecast_p50_required,
            "forecast_p90": forecast_p90_required,
        }
    ).to_csv(figures_dir / "policy_series.csv", index=False)

    rows = [
        {
            "experiment_id": "policy-reactive",
            "dataset_split": "test",
            "model_name": "n/a",
            "policy_name": "reactive_threshold",
            "horizon": chosen_horizon,
            "mae": "",
            "rmse": "",
            "mape": "",
            "pinball_loss": "",
            "sla_violation": reactive_metrics.sla_violation,
            "over_provisioning": reactive_metrics.over_provisioning,
            "under_provisioning": reactive_metrics.under_provisioning,
            "scaling_actions": reactive_metrics.scaling_actions,
            "latency_ms": "",
        },
        {
            "experiment_id": "policy-lagged-tracking",
            "dataset_split": "test",
            "model_name": "n/a",
            "policy_name": "lagged_target_tracking",
            "horizon": chosen_horizon,
            "mae": "",
            "rmse": "",
            "mape": "",
            "pinball_loss": "",
            "sla_violation": lagged_metrics.sla_violation,
            "over_provisioning": lagged_metrics.over_provisioning,
            "under_provisioning": lagged_metrics.under_provisioning,
            "scaling_actions": lagged_metrics.scaling_actions,
            "latency_ms": "",
        },
        {
            "experiment_id": "policy-predictive",
            "dataset_split": "test",
            "model_name": model.name,
            "policy_name": "predictive_uncertainty_aware",
            "horizon": chosen_horizon,
            "mae": "",
            "rmse": "",
            "mape": "",
            "pinball_loss": "",
            "sla_violation": predictive_metrics.sla_violation,
            "over_provisioning": predictive_metrics.over_provisioning,
            "under_provisioning": predictive_metrics.under_provisioning,
            "scaling_actions": predictive_metrics.scaling_actions,
            "latency_ms": "",
        },
    ]

    append_metrics(Path(config["output"]["metrics_csv"]), rows)


if __name__ == "__main__":
    main()
