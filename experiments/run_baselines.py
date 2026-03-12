#!/usr/bin/env python3
"""Run lightweight forecasting baselines on the aggregate cluster series."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from models.baselines import linear_regression, mlp_regression, moving_average, persistence, random_forest
from models.ua_mstcn import UAMSTCN


def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.abs(y_true - y_pred)))


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    denom = np.where(np.abs(y_true) < 1e-6, 1.0, np.abs(y_true))
    return float(np.mean(np.abs((y_true - y_pred) / denom)))


def pinball(y_true: np.ndarray, y_pred: np.ndarray, quantile: float = 0.5) -> float:
    delta = y_true - y_pred
    return float(np.mean(np.maximum(quantile * delta, (quantile - 1.0) * delta)))


def split_series(series: np.ndarray, train_ratio: float, valid_ratio: float) -> tuple[np.ndarray, np.ndarray]:
    valid_end = int(len(series) * (train_ratio + valid_ratio))
    train = series[:valid_end]
    test = series[valid_end:]
    return train, test


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()

    with args.config.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    csv_path = Path(config["dataset"]["output_series_csv"])
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing prepared series file: {csv_path}")

    df = pd.read_csv(csv_path)
    series = df["cluster_cpu_utilization_mean"].to_numpy(dtype=float)
    context_window = int(config["forecast"]["context_window"])
    train_series, test_series = split_series(
        series,
        float(config["forecast"]["train_ratio"]),
        float(config["forecast"]["valid_ratio"]),
    )

    rows = []
    for horizon in config["forecast"]["horizons"]:
        t0 = time.perf_counter()
        p = persistence(test_series, context_window, horizon)
        rows.append(
            {
                "experiment_id": f"baseline-persistence-h{horizon}",
                "dataset_split": "test",
                "model_name": p.name,
                "policy_name": "",
                "horizon": horizon,
                "mae": mae(p.y_true, p.y_pred),
                "rmse": rmse(p.y_true, p.y_pred),
                "mape": mape(p.y_true, p.y_pred),
                "pinball_loss": pinball(p.y_true, p.y_pred),
                "sla_violation": "",
                "over_provisioning": "",
                "under_provisioning": "",
                "scaling_actions": "",
                "latency_ms": (time.perf_counter() - t0) * 1000.0,
            }
        )

        t0 = time.perf_counter()
        mv = moving_average(test_series, context_window, horizon)
        rows.append(
            {
                "experiment_id": f"baseline-moving-average-h{horizon}",
                "dataset_split": "test",
                "model_name": mv.name,
                "policy_name": "",
                "horizon": horizon,
                "mae": mae(mv.y_true, mv.y_pred),
                "rmse": rmse(mv.y_true, mv.y_pred),
                "mape": mape(mv.y_true, mv.y_pred),
                "pinball_loss": pinball(mv.y_true, mv.y_pred),
                "sla_violation": "",
                "over_provisioning": "",
                "under_provisioning": "",
                "scaling_actions": "",
                "latency_ms": (time.perf_counter() - t0) * 1000.0,
            }
        )

        t0 = time.perf_counter()
        lr = linear_regression(train_series, test_series, context_window, horizon)
        rows.append(
            {
                "experiment_id": f"baseline-linear-regression-h{horizon}",
                "dataset_split": "test",
                "model_name": lr.name,
                "policy_name": "",
                "horizon": horizon,
                "mae": mae(lr.y_true, lr.y_pred),
                "rmse": rmse(lr.y_true, lr.y_pred),
                "mape": mape(lr.y_true, lr.y_pred),
                "pinball_loss": pinball(lr.y_true, lr.y_pred),
                "sla_violation": "",
                "over_provisioning": "",
                "under_provisioning": "",
                "scaling_actions": "",
                "latency_ms": (time.perf_counter() - t0) * 1000.0,
            }
        )

        t0 = time.perf_counter()
        rf = random_forest(train_series, test_series, context_window, horizon)
        rows.append(
            {
                "experiment_id": f"baseline-random-forest-h{horizon}",
                "dataset_split": "test",
                "model_name": rf.name,
                "policy_name": "",
                "horizon": horizon,
                "mae": mae(rf.y_true, rf.y_pred),
                "rmse": rmse(rf.y_true, rf.y_pred),
                "mape": mape(rf.y_true, rf.y_pred),
                "pinball_loss": pinball(rf.y_true, rf.y_pred),
                "sla_violation": "",
                "over_provisioning": "",
                "under_provisioning": "",
                "scaling_actions": "",
                "latency_ms": (time.perf_counter() - t0) * 1000.0,
            }
        )

        t0 = time.perf_counter()
        mlp = mlp_regression(train_series, test_series, context_window, horizon)
        rows.append(
            {
                "experiment_id": f"baseline-mlp-regressor-h{horizon}",
                "dataset_split": "test",
                "model_name": mlp.name,
                "policy_name": "",
                "horizon": horizon,
                "mae": mae(mlp.y_true, mlp.y_pred),
                "rmse": rmse(mlp.y_true, mlp.y_pred),
                "mape": mape(mlp.y_true, mlp.y_pred),
                "pinball_loss": pinball(mlp.y_true, mlp.y_pred),
                "sla_violation": "",
                "over_provisioning": "",
                "under_provisioning": "",
                "scaling_actions": "",
                "latency_ms": (time.perf_counter() - t0) * 1000.0,
            }
        )

    ua_horizons = list(config["forecast"]["horizons"])
    t0 = time.perf_counter()
    ua_model = UAMSTCN(context_window=context_window, horizons=ua_horizons)
    ua_model.fit(train_series)
    fit_ms = (time.perf_counter() - t0) * 1000.0

    for horizon in ua_horizons:
        horizon_index = ua_horizons.index(horizon)
        t0 = time.perf_counter()
        histories, y_true_arr = ua_model.history_matrix(test_series, horizon)
        p50_matrix, p90_matrix = ua_model.predict_batch(histories)
        p50_arr = p50_matrix[:, horizon_index]
        p90_arr = p90_matrix[:, horizon_index]
        eval_ms = (time.perf_counter() - t0) * 1000.0
        pinball_avg = 0.5 * (
            pinball(y_true_arr, p50_arr, quantile=0.5) + pinball(y_true_arr, p90_arr, quantile=0.9)
        )
        rows.append(
            {
                "experiment_id": f"baseline-ua-mstcn-lite-h{horizon}",
                "dataset_split": "test",
                "model_name": ua_model.name,
                "policy_name": "",
                "horizon": horizon,
                "mae": mae(y_true_arr, p50_arr),
                "rmse": rmse(y_true_arr, p50_arr),
                "mape": mape(y_true_arr, p50_arr),
                "pinball_loss": pinball_avg,
                "sla_violation": "",
                "over_provisioning": "",
                "under_provisioning": "",
                "scaling_actions": "",
                "latency_ms": fit_ms / len(ua_horizons) + eval_ms,
            }
        )

    result_df = pd.DataFrame(rows)
    metrics_path = Path(config["output"]["metrics_csv"])
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    result_df.to_csv(metrics_path, index=False)


if __name__ == "__main__":
    main()
