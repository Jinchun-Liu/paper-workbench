#!/usr/bin/env python3
"""Render manuscript figures from the prepared Alibaba trace artifacts."""

from __future__ import annotations

import argparse
import sys
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


def split_series(series: np.ndarray, train_ratio: float, valid_ratio: float) -> tuple[np.ndarray, np.ndarray]:
    valid_end = int(len(series) * (train_ratio + valid_ratio))
    train = series[:valid_end]
    test = series[valid_end:]
    return train, test


def save_figure(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def render_workload_overview(df: pd.DataFrame, path: Path) -> None:
    minute_index = df["minute_index"].to_numpy()
    hours = minute_index / 60.0
    first_day = hours <= 24.0

    fig, axes = plt.subplots(2, 2, figsize=(11, 7))
    axes = axes.ravel()

    axes[0].plot(hours, df["cluster_cpu_utilization_mean"], color="#1f4e79", linewidth=1.2)
    axes[0].set_title("CPU utilization across the trace")
    axes[0].set_xlabel("Hour")
    axes[0].set_ylabel("CPU utilization (%)")

    axes[1].plot(hours, df["cluster_memory_utilization_mean"], color="#7a3e00", linewidth=1.2)
    axes[1].set_title("Memory utilization across the trace")
    axes[1].set_xlabel("Hour")
    axes[1].set_ylabel("Memory utilization (%)")

    axes[2].plot(hours, df["active_machine_count"], color="#0f7b6c", linewidth=1.2)
    axes[2].set_title("Active machine count")
    axes[2].set_xlabel("Hour")
    axes[2].set_ylabel("Machines")

    axes[3].plot(
        hours[first_day],
        df.loc[first_day, "cluster_cpu_utilization_mean"],
        color="#1f4e79",
        linewidth=1.2,
        label="CPU",
    )
    axes[3].plot(
        hours[first_day],
        df.loc[first_day, "cluster_memory_utilization_mean"],
        color="#c97c00",
        linewidth=1.2,
        label="Memory",
    )
    axes[3].set_title("First 24 hours")
    axes[3].set_xlabel("Hour")
    axes[3].set_ylabel("Utilization (%)")
    axes[3].legend(frameon=False)

    save_figure(fig, path)


def render_distribution_views(df: pd.DataFrame, path: Path) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(11, 7))
    axes = axes.ravel()

    axes[0].hist(df["cluster_cpu_utilization_mean"], bins=35, color="#1f4e79", alpha=0.9)
    axes[0].set_title("CPU utilization distribution")
    axes[0].set_xlabel("CPU utilization (%)")
    axes[0].set_ylabel("Minutes")

    axes[1].hist(df["cluster_memory_utilization_mean"], bins=35, color="#c97c00", alpha=0.9)
    axes[1].set_title("Memory utilization distribution")
    axes[1].set_xlabel("Memory utilization (%)")
    axes[1].set_ylabel("Minutes")

    axes[2].scatter(
        df["cluster_cpu_utilization_mean"],
        df["cluster_memory_utilization_mean"],
        s=8,
        alpha=0.18,
        color="#0f7b6c",
        edgecolors="none",
    )
    axes[2].set_title("CPU-memory relationship")
    axes[2].set_xlabel("CPU utilization (%)")
    axes[2].set_ylabel("Memory utilization (%)")

    hour_of_day = ((df["minute_index"] // 60) % 24).astype(int)
    hourly_profile = (
        df.assign(hour_of_day=hour_of_day)
        .groupby("hour_of_day")[["cluster_cpu_utilization_mean", "cluster_memory_utilization_mean"]]
        .mean()
        .reset_index()
    )
    axes[3].plot(
        hourly_profile["hour_of_day"],
        hourly_profile["cluster_cpu_utilization_mean"],
        color="#1f4e79",
        linewidth=1.6,
        label="CPU",
    )
    axes[3].plot(
        hourly_profile["hour_of_day"],
        hourly_profile["cluster_memory_utilization_mean"],
        color="#c97c00",
        linewidth=1.6,
        label="Memory",
    )
    axes[3].set_title("Average hour-of-day profile")
    axes[3].set_xlabel("Hour of day")
    axes[3].set_ylabel("Utilization (%)")
    axes[3].set_xticks(range(0, 24, 3))
    axes[3].legend(frameon=False)

    save_figure(fig, path)


def render_mae_figure(metrics_df: pd.DataFrame, path: Path) -> None:
    forecast_df = metrics_df[metrics_df["policy_name"].fillna("") == ""].copy()
    forecast_df["horizon"] = forecast_df["horizon"].astype(int)

    model_order = [
        "persistence",
        "moving_average",
        "linear_regression",
        "random_forest",
        "mlp_regressor",
        "ua_mstcn_lite_quantile_forest",
    ]
    horizon_order = [1, 5, 10]
    display_names = {
        "persistence": "Persistence",
        "moving_average": "Moving avg.",
        "linear_regression": "Linear reg.",
        "random_forest": "Random forest",
        "mlp_regressor": "MLP",
        "ua_mstcn_lite_quantile_forest": "UA-MSTCN-Lite",
    }
    color_map = {
        "persistence": "#7f7f7f",
        "moving_average": "#c97c00",
        "linear_regression": "#1f4e79",
        "random_forest": "#0f7b6c",
        "mlp_regressor": "#cc6f00",
        "ua_mstcn_lite_quantile_forest": "#8b1e3f",
    }

    x = np.arange(len(horizon_order))
    width = 0.13
    offsets = np.linspace(-2.5 * width, 2.5 * width, len(model_order))

    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    for offset, model_name in zip(offsets, model_order):
        subset = forecast_df[forecast_df["model_name"] == model_name].sort_values("horizon")
        ax.bar(
            x + offset,
            subset["mae"].to_numpy(dtype=float),
            width=width,
            label=display_names[model_name],
            color=color_map[model_name],
        )

    ax.set_xticks(x)
    ax.set_xticklabels([f"{h} min" for h in horizon_order])
    ax.set_ylabel("MAE")
    ax.set_title("Forecast error by model and horizon")
    ymax = float(forecast_df["mae"].max())
    ax.set_ylim(0.0, ymax * 1.18)
    ax.legend(frameon=False, ncols=2, loc="upper left")

    save_figure(fig, path)


def render_case_study(
    train_series: np.ndarray,
    test_series: np.ndarray,
    context_window: int,
    path: Path,
) -> None:
    horizons = [1, 5, 10]
    ua_model = UAMSTCN(context_window=context_window, horizons=horizons)
    ua_model.fit(train_series)
    model_builders = {
        "Persistence": lambda h: persistence(test_series, context_window, h),
        "Random forest": lambda h: random_forest(train_series, test_series, context_window, h),
        "MLP": lambda h: mlp_regression(train_series, test_series, context_window, h),
    }
    colors = {
        "Persistence": "#7f7f7f",
        "Random forest": "#0f7b6c",
        "MLP": "#cc6f00",
        "UA-MSTCN-Lite": "#8b1e3f",
    }

    fig, axes = plt.subplots(len(horizons), 1, figsize=(10.5, 8.5), sharex=False)
    start = 220
    window = 180
    for ax, horizon in zip(axes, horizons):
        model_outputs = {name: builder(horizon) for name, builder in model_builders.items()}
        actual = next(iter(model_outputs.values())).y_true
        horizon_index = horizons.index(horizon)
        histories, _ = ua_model.history_matrix(test_series, horizon)
        ua_predictions_arr = ua_model.predict_batch(histories)[0][:, horizon_index]
        end = min(start + window, len(actual))
        x_axis = np.arange(start, end)

        ax.plot(x_axis, actual[start:end], color="black", linewidth=1.6, label="Actual")
        for name, output in model_outputs.items():
            ax.plot(
                x_axis,
                output.y_pred[start:end],
                color=colors[name],
                linewidth=1.2,
                label=name,
            )
        ax.plot(
            x_axis,
            ua_predictions_arr[start:end],
            color=colors["UA-MSTCN-Lite"],
            linewidth=1.2,
            label="UA-MSTCN-Lite",
        )
        ax.set_title(f"Case study at {horizon}-minute horizon")
        ax.set_ylabel("CPU utilization (%)")
        ax.grid(alpha=0.15, linewidth=0.5)
        plotted = [actual[start:end], ua_predictions_arr[start:end]]
        plotted.extend(output.y_pred[start:end] for output in model_outputs.values())
        y_min = min(float(np.min(series_slice)) for series_slice in plotted)
        y_max = max(float(np.max(series_slice)) for series_slice in plotted)
        y_pad = max(2.0, 0.20 * (y_max - y_min))
        ax.set_ylim(y_min - y_pad * 0.35, y_max + y_pad)

    axes[-1].set_xlabel("Aligned test-step index")
    handles, labels = axes[0].get_legend_handles_labels()
    axes[0].legend(handles, labels, frameon=False, ncols=5, loc="upper center", bbox_to_anchor=(0.63, 1.02))

    save_figure(fig, path)


def render_latency_tradeoff(metrics_df: pd.DataFrame, path: Path) -> None:
    forecast_df = metrics_df[metrics_df["policy_name"].fillna("") == ""].copy()
    summary = (
        forecast_df.groupby("model_name")[["mae", "latency_ms"]]
        .mean()
        .reset_index()
        .sort_values("mae")
    )
    display_names = {
        "persistence": "Persistence",
        "moving_average": "Moving avg.",
        "linear_regression": "Linear reg.",
        "random_forest": "Random forest",
        "mlp_regressor": "MLP",
        "ua_mstcn_lite_quantile_forest": "UA-MSTCN-Lite",
    }

    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    ax.scatter(summary["latency_ms"], summary["mae"], s=90, color="#0f7b6c")
    x_max = float(summary["latency_ms"].max())
    x_offsets = {
        "moving_average": (6, 4, "left"),
        "persistence": (6, 4, "left"),
        "linear_regression": (6, 4, "left"),
        "mlp_regressor": (6, 4, "left"),
        "ua_mstcn_lite_quantile_forest": (6, 4, "left"),
        "random_forest": (-8, -2, "right"),
    }
    for _, row in summary.iterrows():
        offset_x, offset_y, ha = x_offsets.get(row["model_name"], (6, 4, "left"))
        if row["latency_ms"] >= 0.82 * x_max and ha == "left":
            offset_x, offset_y, ha = (-8, 4, "right")
        ax.annotate(
            display_names[row["model_name"]],
            (row["latency_ms"], row["mae"]),
            textcoords="offset points",
            xytext=(offset_x, offset_y),
            ha=ha,
            fontsize=9,
        )
    ax.set_xscale("log")
    ax.set_xlim(float(summary["latency_ms"].min()) * 0.75, x_max * 1.65)
    ax.set_ylim(float(summary["mae"].min()) - 0.03, float(summary["mae"].max()) + 0.05)
    ax.set_xlabel("Average runtime per benchmark call (ms, log scale)")
    ax.set_ylabel("Average MAE across horizons")
    ax.set_title("Accuracy-latency trade-off")
    ax.grid(alpha=0.15, linewidth=0.5)

    save_figure(fig, path)


def render_policy_view(policy_series_csv: Path, path: Path) -> None:
    if not policy_series_csv.exists():
        return

    df = pd.read_csv(policy_series_csv)
    sample = df.iloc[:260].copy()
    x_axis = np.arange(len(sample))

    fig, ax = plt.subplots(figsize=(10.5, 4.6))
    ax.plot(x_axis, sample["actual_required_capacity"], color="black", linewidth=1.6, label="Required capacity")
    ax.plot(x_axis, sample["reactive_capacity"], color="#1f4e79", linewidth=1.2, label="Reactive")
    if "lagged_capacity" in sample:
        ax.plot(x_axis, sample["lagged_capacity"], color="#c97c00", linewidth=1.2, label="Lagged target")
    ax.plot(x_axis, sample["predictive_capacity"], color="#0f7b6c", linewidth=1.2, label="Predictive")
    ax.fill_between(
        x_axis,
        sample["forecast_p50"],
        sample["forecast_p90"],
        color="#0f7b6c",
        alpha=0.12,
        label="Predictive P50-P90 band",
    )
    ax.set_xlabel("Aligned test-step index")
    ax.set_ylabel("Normalized capacity")
    ax.set_title("Policy trajectories on the evaluation horizon")
    ax.legend(frameon=False, ncols=2)
    ax.grid(alpha=0.15, linewidth=0.5)
    y_min = float(
        sample[
            [
                "actual_required_capacity",
                "reactive_capacity",
                "lagged_capacity",
                "predictive_capacity",
                "forecast_p50",
                "forecast_p90",
            ]
        ].min().min()
    )
    y_max = float(
        sample[
            [
                "actual_required_capacity",
                "reactive_capacity",
                "lagged_capacity",
                "predictive_capacity",
                "forecast_p50",
                "forecast_p90",
            ]
        ].max().max()
    )
    y_pad = max(0.03, 0.16 * (y_max - y_min))
    ax.set_ylim(y_min - y_pad * 0.3, y_max + y_pad)

    save_figure(fig, path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()

    with args.config.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    series_path = Path(config["dataset"]["output_series_csv"])
    metrics_path = Path(config["output"]["metrics_csv"])
    figures_dir = Path(config["output"]["forecast_dir"])

    df = pd.read_csv(series_path)
    metrics_df = pd.read_csv(metrics_path)
    series = df["cluster_cpu_utilization_mean"].to_numpy(dtype=float)
    context_window = int(config["forecast"]["context_window"])
    train_series, test_series = split_series(
        series,
        float(config["forecast"]["train_ratio"]),
        float(config["forecast"]["valid_ratio"]),
    )

    render_workload_overview(df, figures_dir / "cluster_workload_overview.png")
    render_distribution_views(df, figures_dir / "resource_distribution_views.png")
    render_mae_figure(metrics_df, figures_dir / "baseline_mae_by_horizon.png")
    render_case_study(train_series, test_series, context_window, figures_dir / "forecast_case_study.png")
    render_latency_tradeoff(metrics_df, figures_dir / "forecast_latency_tradeoff.png")
    render_policy_view(figures_dir / "policy_series.csv", figures_dir / "policy_capacity_comparison.png")


if __name__ == "__main__":
    main()
