#!/usr/bin/env python3
"""Run sensitivity, regime, and policy-ablation experiments."""

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

from models.baselines import random_forest
from models.ua_mstcn import UAMSTCN
from policies.autoscaling_simulator import required_capacity, run_predictive


def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.abs(y_true - y_pred)))


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


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


def run_context_sensitivity(
    train_series: np.ndarray,
    test_series: np.ndarray,
    horizons: list[int],
    output_csv: Path,
    output_png: Path,
) -> pd.DataFrame:
    rows = []
    for context_window in [30, 60, 120]:
        model = UAMSTCN(
            context_window=context_window,
            horizons=horizons,
            variant_label=f"ua_mstcn_lite_c{context_window}",
        )
        model.fit(train_series)
        for horizon in horizons:
            horizon_index = horizons.index(horizon)
            histories, y_true = model.history_matrix(test_series, horizon)
            p50_matrix, _ = model.predict_batch(histories)
            y_pred = p50_matrix[:, horizon_index]
            rows.append(
                {
                    "context_window": context_window,
                    "horizon": horizon,
                    "mae": mae(y_true, y_pred),
                    "rmse": rmse(y_true, y_pred),
                }
            )

    df = pd.DataFrame(rows)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False)

    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    for horizon in horizons:
        subset = df[df["horizon"] == horizon].sort_values("context_window")
        ax.plot(
            subset["context_window"],
            subset["mae"],
            marker="o",
            linewidth=1.8,
            label=f"{horizon}-min horizon",
        )
    ax.set_xlabel("Context window (minutes)")
    ax.set_ylabel("MAE")
    ax.set_title("Context-window sensitivity of UA-MSTCN-Lite")
    ax.set_xticks([30, 60, 120])
    ax.legend(frameon=False)
    ax.grid(alpha=0.18, linewidth=0.5)
    save_figure(fig, output_png)
    return df


def run_regime_analysis(
    train_series: np.ndarray,
    test_series: np.ndarray,
    horizons: list[int],
    output_csv: Path,
    output_png: Path,
) -> pd.DataFrame:
    ua_model = UAMSTCN(context_window=60, horizons=horizons)
    ua_model.fit(train_series)

    rows = []
    target_horizon = 5
    histories, y_true = ua_model.history_matrix(test_series, target_horizon)
    local_std = histories[:, -30:].std(axis=1)
    low_cut = float(np.quantile(local_std, 1.0 / 3.0))
    high_cut = float(np.quantile(local_std, 2.0 / 3.0))
    labels = np.where(local_std <= low_cut, "stable", np.where(local_std >= high_cut, "bursty", "moderate"))

    rf_result = random_forest(train_series, test_series, 60, target_horizon)
    ua_pred = ua_model.predict_batch(histories)[0][:, horizons.index(target_horizon)]

    for model_name, y_pred in [
        ("Random forest", rf_result.y_pred),
        ("UA-MSTCN-Lite", ua_pred),
    ]:
        for regime in ["stable", "moderate", "bursty"]:
            mask = labels == regime
            rows.append(
                {
                    "regime": regime,
                    "model_name": model_name,
                    "sample_count": int(mask.sum()),
                    "mae": mae(y_true[mask], y_pred[mask]),
                    "rmse": rmse(y_true[mask], y_pred[mask]),
                }
            )

    df = pd.DataFrame(rows)
    df.to_csv(output_csv, index=False)

    pivot = df.pivot(index="regime", columns="model_name", values="mae").reindex(["stable", "moderate", "bursty"])
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    x = np.arange(len(pivot.index))
    width = 0.34
    ax.bar(x - width / 2, pivot["Random forest"], width=width, color="#0f7b6c", label="Random forest")
    ax.bar(x + width / 2, pivot["UA-MSTCN-Lite"], width=width, color="#8b1e3f", label="UA-MSTCN-Lite")
    ax.set_xticks(x)
    ax.set_xticklabels([label.title() for label in pivot.index])
    ax.set_ylabel("MAE at 5-minute horizon")
    ax.set_title("Forecast error by workload regime")
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.18, linewidth=0.5)
    save_figure(fig, output_png)
    return df


def run_quantile_calibration(
    train_series: np.ndarray,
    test_series: np.ndarray,
    horizons: list[int],
    output_csv: Path,
    output_png: Path,
) -> pd.DataFrame:
    ua_model = UAMSTCN(context_window=60, horizons=horizons)
    ua_model.fit(train_series)

    rows = []
    for horizon in horizons:
        horizon_index = horizons.index(horizon)
        histories, y_true = ua_model.history_matrix(test_series, horizon)
        p50_matrix, p90_matrix = ua_model.predict_batch(histories)
        p50 = p50_matrix[:, horizon_index]
        p90 = p90_matrix[:, horizon_index]
        rows.append(
            {
                "horizon": horizon,
                "p50_coverage": float(np.mean(y_true <= p50)),
                "p90_coverage": float(np.mean(y_true <= p90)),
                "interval_width": float(np.mean(p90 - p50)),
                "mae": mae(y_true, p50),
            }
        )

    df = pd.DataFrame(rows)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False)

    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    x = np.arange(len(df))
    width = 0.28
    ax.bar(x - width / 2, df["p50_coverage"], width=width, color="#1f4e79", label="Empirical P50 coverage")
    ax.bar(x + width / 2, df["p90_coverage"], width=width, color="#0f7b6c", label="Empirical P90 coverage")
    ax.axhline(0.50, color="#1f4e79", linestyle="--", linewidth=1.0, alpha=0.8)
    ax.axhline(0.90, color="#0f7b6c", linestyle="--", linewidth=1.0, alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{h} min" for h in df["horizon"]])
    ax.set_ylim(0.0, 1.02)
    ax.set_ylabel("Coverage")
    ax.set_title("Empirical quantile coverage of UA-MSTCN-Lite")
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.18, linewidth=0.5)
    save_figure(fig, output_png)
    return df


def run_policy_extensions(
    norm_train_series: np.ndarray,
    norm_test_series: np.ndarray,
    output_ablation_csv: Path,
    output_sensitivity_csv: Path,
    output_sensitivity_png: Path,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    horizons = [1, 5, 10]
    target_horizon = 5
    ua_model = UAMSTCN(context_window=60, horizons=horizons)
    ua_model.fit(norm_train_series)

    histories, aligned_actual = ua_model.history_matrix(norm_test_series, target_horizon)
    p50_matrix, p90_matrix = ua_model.predict_batch(histories)
    idx = horizons.index(target_horizon)
    p50 = p50_matrix[:, idx]
    p90 = p90_matrix[:, idx]

    actual_required = required_capacity(aligned_actual, headroom_ratio=0.15, min_capacity=0.20)
    base_p50_required = required_capacity(p50, headroom_ratio=0.15, min_capacity=0.20)
    base_p90_required = required_capacity(p90, headroom_ratio=0.15, min_capacity=0.20)

    ablations = [
        ("predictive_full", base_p50_required, base_p90_required * 1.10, 8, 0.05),
        ("no_scale_out_margin", base_p50_required, base_p90_required, 8, 0.05),
        ("no_cooldown", base_p50_required, base_p90_required * 1.10, 0, 0.05),
        ("median_only", base_p50_required, base_p50_required, 8, 0.05),
        ("no_scale_in_guard", base_p50_required, base_p90_required * 1.10, 8, 0.0),
    ]

    ablation_rows = []
    for variant_name, forecast_p50, forecast_p90, cooldown_steps, scale_in_margin in ablations:
        _, metrics = run_predictive(
            actual_load=actual_required,
            forecast_p50=forecast_p50,
            forecast_p90=forecast_p90,
            min_capacity=0.20,
            cooldown_steps=cooldown_steps,
            max_step_change=0.10,
            scale_in_safety_margin=scale_in_margin,
        )
        ablation_rows.append(
            {
                "variant_name": variant_name,
                "sla_violation": metrics.sla_violation,
                "over_provisioning": metrics.over_provisioning,
                "under_provisioning": metrics.under_provisioning,
                "scaling_actions": metrics.scaling_actions,
                "average_capacity": metrics.average_capacity,
            }
        )

    ablation_df = pd.DataFrame(ablation_rows)
    ablation_df.to_csv(output_ablation_csv, index=False)

    sensitivity_rows = []
    for margin in [0.00, 0.05, 0.10, 0.15]:
        for cooldown in [0, 3, 8, 12]:
            _, metrics = run_predictive(
                actual_load=actual_required,
                forecast_p50=base_p50_required,
                forecast_p90=base_p90_required * (1.0 + margin),
                min_capacity=0.20,
                cooldown_steps=cooldown,
                max_step_change=0.10,
                scale_in_safety_margin=0.05,
            )
            sensitivity_rows.append(
                {
                    "scale_out_margin": margin,
                    "cooldown_steps": cooldown,
                    "sla_violation": metrics.sla_violation,
                    "over_provisioning": metrics.over_provisioning,
                    "under_provisioning": metrics.under_provisioning,
                    "scaling_actions": metrics.scaling_actions,
                    "average_capacity": metrics.average_capacity,
                }
            )

    sensitivity_df = pd.DataFrame(sensitivity_rows)
    sensitivity_df.to_csv(output_sensitivity_csv, index=False)

    fig, ax = plt.subplots(figsize=(8.2, 5.1))
    scatter = ax.scatter(
        sensitivity_df["over_provisioning"],
        sensitivity_df["sla_violation"],
        c=sensitivity_df["scale_out_margin"],
        s=65,
        cmap="viridis",
    )
    annotation_offsets = {
        (0.00, 0): (6, 3, "left"),
        (0.00, 8): (-8, 10, "right"),
        (0.00, 12): (6, 3, "left"),
        (0.10, 0): (12, 8, "left"),
        (0.10, 8): (10, 4, "left"),
        (0.10, 12): (12, -6, "left"),
        (0.15, 0): (8, 4, "left"),
        (0.15, 8): (-12, 10, "right"),
        (0.15, 12): (-12, -4, "right"),
    }
    for _, row in sensitivity_df.iterrows():
        key = (round(float(row["scale_out_margin"]), 2), int(row["cooldown_steps"]))
        if key in annotation_offsets:
            offset_x, offset_y, ha = annotation_offsets[key]
            ax.annotate(
                f"m={row['scale_out_margin']:.2f}, c={int(row['cooldown_steps'])}",
                (row["over_provisioning"], row["sla_violation"]),
                textcoords="offset points",
                xytext=(offset_x, offset_y),
                ha=ha,
                fontsize=8,
                bbox={
                    "boxstyle": "round,pad=0.15",
                    "facecolor": "white",
                    "alpha": 0.75,
                    "edgecolor": "none",
                },
                arrowprops={"arrowstyle": "-", "color": "#666666", "lw": 0.5, "alpha": 0.6},
            )
    ax.set_xlabel("Over-provisioning")
    ax.set_ylabel("SLA violation")
    ax.set_title("Policy sensitivity under margin and cooldown changes")
    ax.grid(alpha=0.18, linewidth=0.5)
    x_min = float(sensitivity_df["over_provisioning"].min())
    x_max = float(sensitivity_df["over_provisioning"].max())
    y_min = float(sensitivity_df["sla_violation"].min())
    y_max = float(sensitivity_df["sla_violation"].max())
    ax.set_xlim(x_min - 0.006, x_max + 0.012)
    ax.set_ylim(max(0.0, y_min - 0.008), y_max + 0.008)
    cbar = fig.colorbar(scatter, ax=ax)
    cbar.set_label("Scale-out margin")
    save_figure(fig, output_sensitivity_png)
    return ablation_df, sensitivity_df


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()

    with args.config.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    series_path = Path(config["dataset"]["output_series_csv"])
    tables_dir = Path(config["output"]["tables_dir"])
    figures_dir = Path(config["output"]["forecast_dir"])
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(series_path)
    series_pct = df["cluster_cpu_utilization_mean"].to_numpy(dtype=float)
    series_norm = series_pct / 100.0
    horizons = list(config["forecast"]["horizons"])

    train_pct, test_pct = split_series(
        series_pct,
        float(config["forecast"]["train_ratio"]),
        float(config["forecast"]["valid_ratio"]),
    )
    train_norm, test_norm = split_series(
        series_norm,
        float(config["forecast"]["train_ratio"]),
        float(config["forecast"]["valid_ratio"]),
    )

    run_context_sensitivity(
        train_pct,
        test_pct,
        horizons,
        tables_dir / "ua_context_sensitivity.csv",
        figures_dir / "ua_context_sensitivity.png",
    )
    run_regime_analysis(
        train_pct,
        test_pct,
        horizons,
        tables_dir / "forecast_regime_analysis.csv",
        figures_dir / "forecast_regime_comparison.png",
    )
    run_quantile_calibration(
        train_pct,
        test_pct,
        horizons,
        tables_dir / "quantile_coverage.csv",
        figures_dir / "quantile_coverage.png",
    )
    run_policy_extensions(
        train_norm,
        test_norm,
        tables_dir / "policy_ablation.csv",
        tables_dir / "policy_sensitivity.csv",
        figures_dir / "policy_pareto_sensitivity.png",
    )


if __name__ == "__main__":
    main()
