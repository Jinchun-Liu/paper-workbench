#!/usr/bin/env python3
"""Run forecasting experiments on a high-coverage machine cohort dataset."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from models.baselines import linear_regression, mlp_regression, persistence, random_forest
from models.ua_mstcn import UAMSTCN


def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.abs(y_true - y_pred)))


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    denom = np.where(np.abs(y_true) < 1e-6, 1.0, np.abs(y_true))
    return float(np.mean(np.abs((y_true - y_pred) / denom)))


def split_series(series: np.ndarray, train_ratio: float, valid_ratio: float) -> tuple[np.ndarray, np.ndarray]:
    valid_end = int(len(series) * (train_ratio + valid_ratio))
    return series[:valid_end], series[valid_end:]


def save_figure(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def render_horizon_summary(summary_df: pd.DataFrame, path: Path) -> None:
    model_order = ["persistence", "linear_regression", "random_forest", "mlp_regressor", "ua_mstcn_lite_quantile_forest"]
    display_names = {
        "persistence": "Persistence",
        "linear_regression": "Linear reg.",
        "random_forest": "Random forest",
        "mlp_regressor": "MLP",
        "ua_mstcn_lite_quantile_forest": "UA-MSTCN-Lite",
    }
    color_map = {
        "persistence": "#7f7f7f",
        "linear_regression": "#1f4e79",
        "random_forest": "#0f7b6c",
        "mlp_regressor": "#c97c00",
        "ua_mstcn_lite_quantile_forest": "#8b1e3f",
    }

    x = np.arange(summary_df["horizon"].nunique())
    horizon_order = sorted(summary_df["horizon"].unique())
    width = 0.15
    offsets = np.linspace(-2.0 * width, 2.0 * width, len(model_order))

    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    for offset, model_name in zip(offsets, model_order):
        subset = summary_df[summary_df["model_name"] == model_name].sort_values("horizon")
        ax.bar(
            x + offset,
            subset["mae_mean"],
            width=width,
            label=display_names[model_name],
            color=color_map[model_name],
        )
    ax.set_xticks(x)
    ax.set_xticklabels([f"{h} min" for h in horizon_order])
    ax.set_ylabel("Average MAE across machines")
    ax.set_title("Machine-cohort forecasting performance")
    ax.legend(frameon=False, ncols=2)
    ax.grid(axis="y", alpha=0.18, linewidth=0.5)
    save_figure(fig, path)


def render_entity_scatter(entity_df: pd.DataFrame, path: Path) -> None:
    model_order = ["linear_regression", "random_forest", "mlp_regressor", "ua_mstcn_lite_quantile_forest"]
    display_names = {
        "linear_regression": "Linear reg.",
        "random_forest": "Random forest",
        "mlp_regressor": "MLP",
        "ua_mstcn_lite_quantile_forest": "UA-MSTCN-Lite",
    }
    color_map = {
        "linear_regression": "#1f4e79",
        "random_forest": "#0f7b6c",
        "mlp_regressor": "#c97c00",
        "ua_mstcn_lite_quantile_forest": "#8b1e3f",
    }

    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    positions = np.arange(len(model_order))
    for idx, model_name in enumerate(model_order):
        subset = entity_df[entity_df["model_name"] == model_name]
        jitter = np.linspace(-0.12, 0.12, len(subset))
        ax.scatter(
            np.full(len(subset), positions[idx]) + jitter,
            subset["average_mae"],
            color=color_map[model_name],
            s=46,
            alpha=0.9,
            label=display_names[model_name],
        )
        ax.hlines(
            subset["average_mae"].mean(),
            idx - 0.23,
            idx + 0.23,
            color="black",
            linewidth=1.2,
        )
    ax.set_xticks(positions)
    ax.set_xticklabels([display_names[name] for name in model_order])
    ax.set_ylabel("Average MAE per machine")
    ax.set_title("Cross-machine variability of forecasting error")
    ax.grid(axis="y", alpha=0.18, linewidth=0.5)
    save_figure(fig, path)


def render_quantile_coverage(coverage_df: pd.DataFrame, path: Path) -> None:
    horizon_order = sorted(coverage_df["horizon"].unique())
    subset = coverage_df.sort_values("horizon")
    x = np.arange(len(horizon_order))
    width = 0.28

    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    ax.bar(x - width / 2, subset["p50_coverage_mean"], width=width, color="#1f4e79", label="P50 coverage")
    ax.bar(x + width / 2, subset["p90_coverage_mean"], width=width, color="#0f7b6c", label="P90 coverage")
    ax.axhline(0.50, color="#1f4e79", linestyle="--", linewidth=1.0, alpha=0.8)
    ax.axhline(0.90, color="#0f7b6c", linestyle="--", linewidth=1.0, alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{h} min" for h in horizon_order])
    ax.set_ylim(0.0, 1.02)
    ax.set_ylabel("Average coverage across machines")
    ax.set_title("Machine-cohort quantile coverage of UA-MSTCN-Lite")
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.18, linewidth=0.5)
    save_figure(fig, path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--cohort-csv", type=Path, required=True)
    parser.add_argument("--cohort-summary-csv", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    with args.config.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    cohort_df = pd.read_csv(args.cohort_csv)
    cohort_summary_df = pd.read_csv(args.cohort_summary_csv)
    output_tables_dir = args.output_dir / "tables"
    output_figures_dir = args.output_dir / "figures"
    output_tables_dir.mkdir(parents=True, exist_ok=True)
    output_figures_dir.mkdir(parents=True, exist_ok=True)

    context_window = int(config["forecast"]["context_window"])
    horizons = list(config["forecast"]["horizons"])
    train_ratio = float(config["forecast"]["train_ratio"])
    valid_ratio = float(config["forecast"]["valid_ratio"])

    result_rows: list[dict] = []
    coverage_rows: list[dict] = []
    machine_ids = cohort_summary_df.sort_values("coverage_ratio", ascending=False)["machine_id"].tolist()

    for machine_id in machine_ids:
        entity_df = cohort_df[cohort_df["machine_id"] == machine_id].sort_values("minute_index")
        series = entity_df["cpu_utilization_mean"].to_numpy(dtype=float)
        train_series, test_series = split_series(series, train_ratio, valid_ratio)

        ua_model = UAMSTCN(context_window=context_window, horizons=horizons)
        fit_start = time.perf_counter()
        ua_model.fit(train_series)
        ua_fit_ms = (time.perf_counter() - fit_start) * 1000.0

        for horizon in horizons:
            pers_start = time.perf_counter()
            pers = persistence(test_series, context_window, horizon)
            pers_ms = (time.perf_counter() - pers_start) * 1000.0
            result_rows.append(
                {
                    "machine_id": machine_id,
                    "model_name": pers.name,
                    "horizon": horizon,
                    "mae": mae(pers.y_true, pers.y_pred),
                    "rmse": rmse(pers.y_true, pers.y_pred),
                    "mape": mape(pers.y_true, pers.y_pred),
                    "latency_ms": pers_ms,
                }
            )

            lr_start = time.perf_counter()
            lr = linear_regression(train_series, test_series, context_window, horizon)
            lr_ms = (time.perf_counter() - lr_start) * 1000.0
            result_rows.append(
                {
                    "machine_id": machine_id,
                    "model_name": lr.name,
                    "horizon": horizon,
                    "mae": mae(lr.y_true, lr.y_pred),
                    "rmse": rmse(lr.y_true, lr.y_pred),
                    "mape": mape(lr.y_true, lr.y_pred),
                    "latency_ms": lr_ms,
                }
            )

            rf_start = time.perf_counter()
            rf = random_forest(train_series, test_series, context_window, horizon)
            rf_ms = (time.perf_counter() - rf_start) * 1000.0
            result_rows.append(
                {
                    "machine_id": machine_id,
                    "model_name": rf.name,
                    "horizon": horizon,
                    "mae": mae(rf.y_true, rf.y_pred),
                    "rmse": rmse(rf.y_true, rf.y_pred),
                    "mape": mape(rf.y_true, rf.y_pred),
                    "latency_ms": rf_ms,
                }
            )

            mlp_start = time.perf_counter()
            mlp = mlp_regression(train_series, test_series, context_window, horizon)
            mlp_ms = (time.perf_counter() - mlp_start) * 1000.0
            result_rows.append(
                {
                    "machine_id": machine_id,
                    "model_name": mlp.name,
                    "horizon": horizon,
                    "mae": mae(mlp.y_true, mlp.y_pred),
                    "rmse": rmse(mlp.y_true, mlp.y_pred),
                    "mape": mape(mlp.y_true, mlp.y_pred),
                    "latency_ms": mlp_ms,
                }
            )

            horizon_index = horizons.index(horizon)
            ua_start = time.perf_counter()
            histories, y_true = ua_model.history_matrix(test_series, horizon)
            p50_matrix, p90_matrix = ua_model.predict_batch(histories)
            ua_ms = (time.perf_counter() - ua_start) * 1000.0
            p50 = p50_matrix[:, horizon_index]
            p90 = p90_matrix[:, horizon_index]
            result_rows.append(
                {
                    "machine_id": machine_id,
                    "model_name": ua_model.name,
                    "horizon": horizon,
                    "mae": mae(y_true, p50),
                    "rmse": rmse(y_true, p50),
                    "mape": mape(y_true, p50),
                    "latency_ms": ua_fit_ms / len(horizons) + ua_ms,
                }
            )
            coverage_rows.append(
                {
                    "machine_id": machine_id,
                    "horizon": horizon,
                    "p50_coverage": float(np.mean(y_true <= p50)),
                    "p90_coverage": float(np.mean(y_true <= p90)),
                    "interval_width": float(np.mean(p90 - p50)),
                }
            )

    results_df = pd.DataFrame(result_rows)
    results_df.to_csv(output_tables_dir / "machine_cohort_forecasting.csv", index=False)

    summary_df = (
        results_df.groupby(["model_name", "horizon"])
        .agg(
            mae_mean=("mae", "mean"),
            mae_std=("mae", "std"),
            rmse_mean=("rmse", "mean"),
            mape_mean=("mape", "mean"),
            latency_ms_mean=("latency_ms", "mean"),
        )
        .reset_index()
        .sort_values(["horizon", "mae_mean"])
    )
    summary_df.to_csv(output_tables_dir / "machine_cohort_summary.csv", index=False)

    entity_avg_df = (
        results_df.groupby(["machine_id", "model_name"])
        .agg(
            average_mae=("mae", "mean"),
            average_rmse=("rmse", "mean"),
        )
        .reset_index()
        .sort_values(["model_name", "average_mae"])
    )
    entity_avg_df.to_csv(output_tables_dir / "machine_cohort_entity_average.csv", index=False)

    best_per_machine_horizon = (
        results_df.sort_values("mae")
        .groupby(["machine_id", "horizon"], as_index=False)
        .first()[["machine_id", "horizon", "model_name", "mae"]]
    )
    win_counts_df = (
        best_per_machine_horizon.groupby(["horizon", "model_name"])
        .size()
        .reset_index(name="win_count")
        .sort_values(["horizon", "win_count"], ascending=[True, False])
    )
    win_counts_df.to_csv(output_tables_dir / "machine_cohort_win_counts.csv", index=False)

    coverage_df = pd.DataFrame(coverage_rows)
    coverage_df.to_csv(output_tables_dir / "machine_cohort_quantile_coverage_raw.csv", index=False)
    coverage_summary_df = (
        coverage_df.groupby("horizon")
        .agg(
            p50_coverage_mean=("p50_coverage", "mean"),
            p90_coverage_mean=("p90_coverage", "mean"),
            interval_width_mean=("interval_width", "mean"),
        )
        .reset_index()
        .sort_values("horizon")
    )
    coverage_summary_df.to_csv(output_tables_dir / "machine_cohort_quantile_coverage.csv", index=False)

    render_horizon_summary(summary_df, output_figures_dir / "machine_cohort_mae_by_horizon.png")
    render_entity_scatter(entity_avg_df, output_figures_dir / "machine_cohort_entity_mae.png")
    render_quantile_coverage(coverage_summary_df, output_figures_dir / "machine_cohort_quantile_coverage.png")


if __name__ == "__main__":
    main()
