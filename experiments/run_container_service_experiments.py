#!/usr/bin/env python3
"""Run forecasting and service-level policy experiments on container app_du cohorts."""

from __future__ import annotations

import argparse
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from contextlib import nullcontext

try:
    from threadpoolctl import threadpool_limits
except ImportError:  # pragma: no cover - optional runtime dependency
    threadpool_limits = None

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from models.baselines import linear_regression, mlp_regression, persistence, random_forest
from models.ua_mstcn import UAMSTCN
from policies.autoscaling_simulator import run_lagged_target_tracking, run_predictive, run_reactive


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


def render_forecast_summary(summary_df: pd.DataFrame, path: Path) -> None:
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

    fig, ax = plt.subplots(figsize=(8.6, 4.8))
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
    ax.set_ylabel("MAE across selected services")
    ax.set_title("Service-level forecasting performance")
    ax.legend(frameon=False, ncols=2)
    ax.grid(axis="y", alpha=0.18, linewidth=0.5)
    save_figure(fig, path)


def render_service_overview(df: pd.DataFrame, path: Path) -> None:
    service_load = (
        df.groupby("app_du")["service_cpu_used_cores_proxy"].mean().sort_values(ascending=False)
    )
    services = service_load.index.tolist()
    title = "Service-level CPU demand for the selected app_du cohort"
    if len(services) > 12:
        services = services[:12]
        title = "Top-12 service CPU demand traces within the selected app_du cohort"
    fig, axes = plt.subplots(len(services), 1, figsize=(10.5, 3.0 * len(services)), sharex=True)
    if len(services) == 1:
        axes = [axes]
    for ax, app_du in zip(axes, services):
        group = df[df["app_du"] == app_du].sort_values("minute_index")
        ax.plot(
            group["minute_index"],
            group["service_cpu_used_cores_proxy"],
            color="#1f4e79",
            linewidth=1.0,
        )
        ax.set_ylabel("CPU cores")
        ax.set_title(
            f"{app_du}: mean={group['service_cpu_used_cores_proxy'].mean():.1f}, "
            f"peak={group['service_cpu_used_cores_proxy'].max():.1f}, "
            f"cv={group['service_cpu_used_cores_proxy'].std() / max(group['service_cpu_used_cores_proxy'].mean(), 1e-6):.2f}"
        )
        ax.grid(alpha=0.18, linewidth=0.5)
    axes[-1].set_xlabel("Minute index")
    fig.suptitle(title, y=1.02)
    save_figure(fig, path)


def render_policy_summary(policy_df: pd.DataFrame, path: Path) -> None:
    avg = (
        policy_df.groupby("policy_name")[["sla_violation", "over_provisioning", "under_provisioning"]]
        .mean()
        .reset_index()
    )
    labels = [label for label in ["reactive_service", "lagged_tracking_service", "predictive_service"] if label in avg["policy_name"].tolist()]
    display_names = {
        "reactive_service": "Reactive",
        "lagged_tracking_service": "Lagged target",
        "predictive_service": "Predictive",
    }
    color_map = {
        "reactive_service": "#1f4e79",
        "lagged_tracking_service": "#c97c00",
        "predictive_service": "#0f7b6c",
    }
    fig, axes = plt.subplots(1, 3, figsize=(10.8, 3.8))
    metrics = [
        ("sla_violation", "SLA violation"),
        ("over_provisioning", "Over-provisioning"),
        ("under_provisioning", "Under-provisioning"),
    ]
    for ax, (metric, title) in zip(axes, metrics):
        subset = avg.set_index("policy_name").loc[labels]
        ax.bar(
            [display_names[label] for label in labels],
            subset[metric],
            color=[color_map[label] for label in labels],
        )
        ax.set_title(title)
        ax.grid(axis="y", alpha=0.18, linewidth=0.5)
    save_figure(fig, path)


def render_policy_by_service(policy_df: pd.DataFrame, path: Path) -> None:
    services = sorted(policy_df["app_du"].unique())
    if len(services) > 16:
        render_policy_delta_ranked(policy_df, path)
        return
    fig, axes = plt.subplots(1, 3, figsize=(11.4, 3.8))
    metrics = [
        ("sla_violation", "SLA violation"),
        ("over_provisioning", "Over-provisioning"),
        ("scaling_actions", "Scaling actions"),
    ]
    colors = {
        "reactive_service": "#1f4e79",
        "lagged_tracking_service": "#c97c00",
        "predictive_service": "#0f7b6c",
    }
    display_names = {
        "reactive_service": "Reactive",
        "lagged_tracking_service": "Lagged target",
        "predictive_service": "Predictive",
    }
    policy_order = [name for name in ["reactive_service", "lagged_tracking_service", "predictive_service"] if name in policy_df["policy_name"].unique()]
    x = np.arange(len(services))
    width = 0.24
    for ax, (metric, title) in zip(axes, metrics):
        offsets = np.linspace(-(len(policy_order) - 1) / 2 * width, (len(policy_order) - 1) / 2 * width, len(policy_order))
        for offset, policy_name in zip(offsets, policy_order):
            metric_values = []
            for app_du in services:
                group = policy_df[policy_df["app_du"] == app_du].set_index("policy_name")
                metric_values.append(group.loc[policy_name, metric])
            ax.bar(
                x + offset,
                metric_values,
                width=width,
                color=colors[policy_name],
                label=display_names[policy_name],
            )
        ax.set_xticks(x)
        ax.set_xticklabels(services)
        ax.set_title(title)
        ax.grid(axis="y", alpha=0.18, linewidth=0.5)
    axes[0].legend(frameon=False)
    save_figure(fig, path)


def render_policy_delta_ranked(policy_df: pd.DataFrame, path: Path) -> None:
    pivot = policy_df.pivot(index="app_du", columns="policy_name")
    metric_specs = [
        ("sla_violation", "SLA delta", "#8b1e3f", "#1f4e79"),
        ("over_provisioning", "Over-provisioning delta", "#0f7b6c", "#c97c00"),
        ("scaling_actions", "Scaling-actions delta", "#0f7b6c", "#c97c00"),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(12.2, 4.8))
    for ax, (metric, title, improve_color, degrade_color) in zip(axes, metric_specs):
        delta = (
            pivot[(metric, "predictive_service")] - pivot[(metric, "reactive_service")]
        ).sort_values()
        if metric == "sla_violation":
            colors = [improve_color if value > 0 else degrade_color for value in delta]
        else:
            colors = [improve_color if value < 0 else degrade_color for value in delta]
        ax.barh(delta.index, delta.values, color=colors)
        ax.axvline(0.0, color="#444444", linewidth=0.9, alpha=0.8)
        ax.set_title(title)
        ax.grid(axis="x", alpha=0.18, linewidth=0.5)
    save_figure(fig, path)


def render_quantile_coverage(coverage_df: pd.DataFrame, path: Path) -> None:
    x = np.arange(len(coverage_df))
    width = 0.28
    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    ax.bar(x - width / 2, coverage_df["p50_coverage_mean"], width=width, color="#1f4e79", label="P50 coverage")
    ax.bar(x + width / 2, coverage_df["p90_coverage_mean"], width=width, color="#0f7b6c", label="P90 coverage")
    ax.axhline(0.50, color="#1f4e79", linestyle="--", linewidth=1.0, alpha=0.8)
    ax.axhline(0.90, color="#0f7b6c", linestyle="--", linewidth=1.0, alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{int(h)} min" for h in coverage_df["horizon"]])
    ax.set_ylim(0.0, 1.02)
    ax.set_ylabel("Coverage")
    ax.set_title("Service-level quantile coverage of UA-MSTCN-Lite")
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.18, linewidth=0.5)
    save_figure(fig, path)


def evaluate_service_task(task: dict) -> tuple[list[dict], list[dict], list[dict]]:
    app_du = task["app_du"]
    series = np.asarray(task["series"], dtype=float)
    service_meta = task["service_meta"]
    context_window = int(task["context_window"])
    horizons = list(task["horizons"])
    train_ratio = float(task["train_ratio"])
    valid_ratio = float(task["valid_ratio"])
    policy_config = task["policy_config"]

    thread_context = threadpool_limits(limits=1) if threadpool_limits is not None else nullcontext()
    with thread_context:
        train_series, test_series = split_series(series, train_ratio, valid_ratio)
        ua_model = UAMSTCN(context_window=context_window, horizons=horizons)
        fit_start = time.perf_counter()
        ua_model.fit(train_series)
        ua_fit_ms = (time.perf_counter() - fit_start) * 1000.0

        forecast_rows: list[dict] = []
        coverage_rows: list[dict] = []
        policy_rows: list[dict] = []

        for horizon in horizons:
            pers_start = time.perf_counter()
            pers = persistence(test_series, context_window, horizon)
            pers_ms = (time.perf_counter() - pers_start) * 1000.0
            forecast_rows.append(
                {
                    "app_du": app_du,
                    "model_name": "persistence",
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
            forecast_rows.append(
                {
                    "app_du": app_du,
                    "model_name": "linear_regression",
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
            forecast_rows.append(
                {
                    "app_du": app_du,
                    "model_name": "random_forest",
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
            forecast_rows.append(
                {
                    "app_du": app_du,
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
            forecast_rows.append(
                {
                    "app_du": app_du,
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
                    "app_du": app_du,
                    "horizon": horizon,
                    "p50_coverage": float(np.mean(y_true <= p50)),
                    "p90_coverage": float(np.mean(y_true <= p90)),
                    "interval_width": float(np.mean(p90 - p50)),
                }
            )

        policy_horizon = 5 if 5 in horizons else horizons[min(1, len(horizons) - 1)]
        horizon_index = horizons.index(policy_horizon)
        histories, actual_series = ua_model.history_matrix(test_series, policy_horizon)
        p50_matrix, p90_matrix = ua_model.predict_batch(histories)
        p50 = p50_matrix[:, horizon_index]
        p90 = p90_matrix[:, horizon_index]

        per_container_request = float(service_meta["median_container_request_cores"])
        if per_container_request <= 1e-9:
            per_container_request = float(service_meta["mean_container_request_cores"])
        per_container_request = max(per_container_request, 0.1)

        headroom_ratio = float(policy_config["headroom_ratio"])
        actual_equivalent_replicas = actual_series / per_container_request
        forecast_p50_replicas = p50 / per_container_request
        forecast_p90_replicas = p90 / per_container_request

        _, reactive_metrics = run_reactive(
            actual_load=actual_equivalent_replicas,
            upper_threshold=float(policy_config["reactive_upper_threshold"]),
            lower_threshold=float(policy_config["reactive_lower_threshold"]),
            min_capacity=1.0,
            max_step_change=1.0,
        )
        _, lagged_metrics = run_lagged_target_tracking(
            actual_load=actual_equivalent_replicas * (1.0 + headroom_ratio),
            min_capacity=1.0,
            max_step_change=1.0,
        )
        _, predictive_metrics = run_predictive(
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
            ("predictive_service", predictive_metrics),
        ]:
            policy_rows.append(
                {
                    "app_du": app_du,
                    "policy_name": policy_name,
                    "horizon": policy_horizon,
                    "sla_violation": metrics.sla_violation,
                    "over_provisioning": metrics.over_provisioning,
                    "under_provisioning": metrics.under_provisioning,
                    "scaling_actions": metrics.scaling_actions,
                    "average_capacity": metrics.average_capacity,
                }
            )

    return forecast_rows, coverage_rows, policy_rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--service-csv", type=Path, required=True)
    parser.add_argument("--service-summary-csv", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--num-workers", type=int, default=min(8, os.cpu_count() or 1))
    args = parser.parse_args()

    with args.config.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    df = pd.read_csv(args.service_csv)
    summary_df = pd.read_csv(args.service_summary_csv)
    output_tables_dir = args.output_dir / "tables"
    output_figures_dir = args.output_dir / "figures"
    output_tables_dir.mkdir(parents=True, exist_ok=True)
    output_figures_dir.mkdir(parents=True, exist_ok=True)

    context_window = int(config["forecast"]["context_window"])
    horizons = list(config["forecast"]["horizons"])
    train_ratio = float(config["forecast"]["train_ratio"])
    valid_ratio = float(config["forecast"]["valid_ratio"])

    forecast_rows: list[dict] = []
    coverage_rows: list[dict] = []
    policy_rows: list[dict] = []

    service_groups = {
        app_du: group.sort_values("minute_index")["service_cpu_used_cores_proxy"].to_numpy(dtype=float)
        for app_du, group in df.groupby("app_du")
    }
    tasks = []
    for _, service_meta in summary_df.iterrows():
        app_du = service_meta["app_du"]
        tasks.append(
            {
                "app_du": app_du,
                "series": service_groups[app_du],
                "service_meta": service_meta.to_dict(),
                "context_window": context_window,
                "horizons": horizons,
                "train_ratio": train_ratio,
                "valid_ratio": valid_ratio,
                "policy_config": config["policy"],
            }
        )

    total_services = len(tasks)
    max_workers = max(1, min(int(args.num_workers), total_services))
    print(f"service_experiment_workers {max_workers}", flush=True)
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(evaluate_service_task, task): task["app_du"]
            for task in tasks
        }
        completed = 0
        for future in as_completed(futures):
            completed += 1
            app_du = futures[future]
            print(f"service_experiment {completed}/{total_services} app_du={app_du}", flush=True)
            service_forecast_rows, service_coverage_rows, service_policy_rows = future.result()
            forecast_rows.extend(service_forecast_rows)
            coverage_rows.extend(service_coverage_rows)
            policy_rows.extend(service_policy_rows)

    forecast_df = pd.DataFrame(forecast_rows)
    forecast_df.to_csv(output_tables_dir / "service_forecasting_raw.csv", index=False)
    forecast_summary_df = (
        forecast_df.groupby(["model_name", "horizon"])
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
    forecast_summary_df.to_csv(output_tables_dir / "service_forecasting_summary.csv", index=False)

    coverage_df = pd.DataFrame(coverage_rows)
    coverage_df.to_csv(output_tables_dir / "service_quantile_coverage_raw.csv", index=False)
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
    coverage_summary_df.to_csv(output_tables_dir / "service_quantile_coverage_summary.csv", index=False)

    policy_df = pd.DataFrame(policy_rows)
    policy_df.to_csv(output_tables_dir / "service_policy_raw.csv", index=False)
    policy_summary_df = (
        policy_df.groupby("policy_name")
        .agg(
            sla_violation_mean=("sla_violation", "mean"),
            over_provisioning_mean=("over_provisioning", "mean"),
            under_provisioning_mean=("under_provisioning", "mean"),
            scaling_actions_mean=("scaling_actions", "mean"),
            average_capacity_mean=("average_capacity", "mean"),
        )
        .reset_index()
    )
    policy_summary_df.to_csv(output_tables_dir / "service_policy_summary.csv", index=False)

    render_forecast_summary(forecast_summary_df, output_figures_dir / "service_forecasting_mae.png")
    render_quantile_coverage(coverage_summary_df, output_figures_dir / "service_quantile_coverage.png")
    render_policy_summary(policy_df, output_figures_dir / "service_policy_summary.png")
    render_service_overview(df, output_figures_dir / "service_workload_overview.png")
    render_policy_by_service(policy_df, output_figures_dir / "service_policy_by_app.png")


if __name__ == "__main__":
    main()
