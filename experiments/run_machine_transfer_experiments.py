#!/usr/bin/env python3
"""Evaluate cross-machine transfer on the high-coverage machine cohort."""

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
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from models.baselines import fit_mlp_regressor, make_supervised, persistence
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


def build_fold_assignments(summary_df: pd.DataFrame, num_folds: int) -> pd.DataFrame:
    ordered = summary_df.sort_values(["coverage_ratio", "std_cpu", "machine_id"], ascending=[False, False, True]).copy()
    ordered["fold_id"] = np.arange(len(ordered)) % num_folds
    return ordered[["machine_id", "fold_id", "coverage_ratio", "std_cpu", "mean_cpu", "imputed_ratio"]]


def pooled_supervised(series_list: list[np.ndarray], context_window: int, horizon: int) -> tuple[np.ndarray, np.ndarray]:
    xs = []
    ys = []
    for series in series_list:
        if len(series) < context_window + horizon:
            continue
        part_x, part_y = make_supervised(series, context_window, horizon)
        if len(part_x) == 0:
            continue
        xs.append(part_x)
        ys.append(part_y)
    if not xs:
        raise ValueError(f"No supervised windows for horizon {horizon}.")
    return np.vstack(xs), np.concatenate(ys)


def render_zero_shot_summary(summary_df: pd.DataFrame, path: Path) -> None:
    zero_shot = summary_df[summary_df["evaluation_mode"] == "zero_shot"].copy()
    model_order = [
        "persistence",
        "global_linear_regression",
        "global_random_forest",
        "global_mlp_regressor",
        "global_ua_mstcn_lite",
    ]
    display_names = {
        "persistence": "Persistence",
        "global_linear_regression": "Global linear reg.",
        "global_random_forest": "Global random forest",
        "global_mlp_regressor": "Global MLP",
        "global_ua_mstcn_lite": "Global UA-MSTCN-Lite",
    }
    color_map = {
        "persistence": "#7f7f7f",
        "global_linear_regression": "#1f4e79",
        "global_random_forest": "#0f7b6c",
        "global_mlp_regressor": "#c97c00",
        "global_ua_mstcn_lite": "#8b1e3f",
    }

    x = np.arange(zero_shot["horizon"].nunique())
    horizon_order = sorted(zero_shot["horizon"].unique())
    width = 0.15
    offsets = np.linspace(-2.0 * width, 2.0 * width, len(model_order))

    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    for offset, model_name in zip(offsets, model_order):
        subset = zero_shot[zero_shot["model_name"] == model_name].sort_values("horizon")
        ax.bar(
            x + offset,
            subset["mae_mean"],
            width=width,
            label=display_names[model_name],
            color=color_map[model_name],
        )
    ax.set_xticks(x)
    ax.set_xticklabels([f"{h} min" for h in horizon_order])
    ax.set_ylabel("MAE on held-out machines")
    ax.set_title("Cross-machine zero-shot transfer performance")
    ax.legend(frameon=False, ncols=2)
    ax.grid(axis="y", alpha=0.18, linewidth=0.5)
    save_figure(fig, path)


def render_gap_summary(gap_df: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    ax.bar(gap_df["horizon"].astype(str), gap_df["gap_to_entity_specific_linear_mean"], color="#c97c00")
    ax.set_xlabel("Horizon (minutes)")
    ax.set_ylabel("MAE gap")
    ax.set_title("Gap from zero-shot global UA to entity-specific linear regression")
    ax.grid(axis="y", alpha=0.18, linewidth=0.5)
    save_figure(fig, path)


def render_coverage_summary(coverage_df: pd.DataFrame, path: Path) -> None:
    x = np.arange(len(coverage_df))
    width = 0.28
    fig, ax = plt.subplots(figsize=(7.8, 4.6))
    ax.bar(x - width / 2, coverage_df["p50_coverage_mean"], width=width, color="#1f4e79", label="P50 coverage")
    ax.bar(x + width / 2, coverage_df["p90_coverage_mean"], width=width, color="#0f7b6c", label="P90 coverage")
    ax.axhline(0.50, color="#1f4e79", linestyle="--", linewidth=1.0, alpha=0.8)
    ax.axhline(0.90, color="#0f7b6c", linestyle="--", linewidth=1.0, alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{int(h)} min" for h in coverage_df["horizon"]])
    ax.set_ylim(0.0, 1.02)
    ax.set_ylabel("Coverage on held-out machines")
    ax.set_title("Cross-machine quantile coverage of global UA-MSTCN-Lite")
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.18, linewidth=0.5)
    save_figure(fig, path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--cohort-csv", type=Path, required=True)
    parser.add_argument("--cohort-summary-csv", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--num-folds", type=int, default=3)
    parser.add_argument("--forest-trees", type=int, default=80)
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

    series_map: dict[str, np.ndarray] = {}
    for machine_id, group in cohort_df.groupby("machine_id"):
        series_map[machine_id] = group.sort_values("minute_index")["cpu_utilization_mean"].to_numpy(dtype=float)

    fold_assignments = build_fold_assignments(cohort_summary_df, args.num_folds)
    fold_assignments.to_csv(output_tables_dir / "machine_transfer_fold_assignments.csv", index=False)

    rows: list[dict] = []
    coverage_rows: list[dict] = []
    machine_ids = set(series_map)

    for fold_id in range(args.num_folds):
        test_ids = fold_assignments.loc[fold_assignments["fold_id"] == fold_id, "machine_id"].tolist()
        train_ids = sorted(machine_ids - set(test_ids))

        train_series_list = []
        for machine_id in train_ids:
            train_series, _ = split_series(series_map[machine_id], train_ratio, valid_ratio)
            train_series_list.append(train_series)

        global_ua = UAMSTCN(
            context_window=context_window,
            horizons=horizons,
            n_estimators=args.forest_trees,
            variant_label="global_ua_mstcn_lite",
        )
        ua_fit_start = time.perf_counter()
        global_ua.fit_multi_series(train_series_list)
        ua_fit_ms = (time.perf_counter() - ua_fit_start) * 1000.0

        global_linear_models: dict[int, LinearRegression] = {}
        global_rf_models: dict[int, RandomForestRegressor] = {}
        global_mlp_models = {}
        for horizon in horizons:
            train_x, train_y = pooled_supervised(train_series_list, context_window, horizon)
            linear_model = LinearRegression()
            linear_model.fit(train_x, train_y)
            global_linear_models[horizon] = linear_model

            rf_model = RandomForestRegressor(
                n_estimators=args.forest_trees,
                min_samples_leaf=5,
                max_features="sqrt",
                random_state=100 + fold_id * 10 + horizon,
                n_jobs=-1,
            )
            rf_model.fit(train_x, train_y)
            global_rf_models[horizon] = rf_model
            global_mlp_models[horizon] = fit_mlp_regressor(
                train_x,
                train_y,
                random_state=200 + fold_id * 10 + horizon,
            )

        for machine_id in test_ids:
            train_series, test_series = split_series(series_map[machine_id], train_ratio, valid_ratio)
            for horizon in horizons:
                pers_start = time.perf_counter()
                pers = persistence(test_series, context_window, horizon)
                pers_ms = (time.perf_counter() - pers_start) * 1000.0
                rows.append(
                    {
                        "fold_id": fold_id,
                        "machine_id": machine_id,
                        "model_name": "persistence",
                        "evaluation_mode": "zero_shot",
                        "horizon": horizon,
                        "mae": mae(pers.y_true, pers.y_pred),
                        "rmse": rmse(pers.y_true, pers.y_pred),
                        "mape": mape(pers.y_true, pers.y_pred),
                        "latency_ms": pers_ms,
                    }
                )

                test_x, test_y = make_supervised(test_series, context_window, horizon)

                linear_start = time.perf_counter()
                linear_pred = global_linear_models[horizon].predict(test_x)
                linear_ms = (time.perf_counter() - linear_start) * 1000.0
                rows.append(
                    {
                        "fold_id": fold_id,
                        "machine_id": machine_id,
                        "model_name": "global_linear_regression",
                        "evaluation_mode": "zero_shot",
                        "horizon": horizon,
                        "mae": mae(test_y, linear_pred),
                        "rmse": rmse(test_y, linear_pred),
                        "mape": mape(test_y, linear_pred),
                        "latency_ms": linear_ms,
                    }
                )

                rf_start = time.perf_counter()
                rf_pred = global_rf_models[horizon].predict(test_x)
                rf_ms = (time.perf_counter() - rf_start) * 1000.0
                rows.append(
                    {
                        "fold_id": fold_id,
                        "machine_id": machine_id,
                        "model_name": "global_random_forest",
                        "evaluation_mode": "zero_shot",
                        "horizon": horizon,
                        "mae": mae(test_y, rf_pred),
                        "rmse": rmse(test_y, rf_pred),
                        "mape": mape(test_y, rf_pred),
                        "latency_ms": rf_ms,
                    }
                )

                mlp_start = time.perf_counter()
                mlp_pred = global_mlp_models[horizon].predict(test_x)
                mlp_ms = (time.perf_counter() - mlp_start) * 1000.0
                rows.append(
                    {
                        "fold_id": fold_id,
                        "machine_id": machine_id,
                        "model_name": "global_mlp_regressor",
                        "evaluation_mode": "zero_shot",
                        "horizon": horizon,
                        "mae": mae(test_y, mlp_pred),
                        "rmse": rmse(test_y, mlp_pred),
                        "mape": mape(test_y, mlp_pred),
                        "latency_ms": mlp_ms,
                    }
                )

                horizon_index = horizons.index(horizon)
                ua_start = time.perf_counter()
                histories, y_true = global_ua.history_matrix(test_series, horizon)
                p50_matrix, p90_matrix = global_ua.predict_batch(histories)
                ua_ms = (time.perf_counter() - ua_start) * 1000.0
                p50 = p50_matrix[:, horizon_index]
                p90 = p90_matrix[:, horizon_index]
                rows.append(
                    {
                        "fold_id": fold_id,
                        "machine_id": machine_id,
                        "model_name": "global_ua_mstcn_lite",
                        "evaluation_mode": "zero_shot",
                        "horizon": horizon,
                        "mae": mae(y_true, p50),
                        "rmse": rmse(y_true, p50),
                        "mape": mape(y_true, p50),
                        "latency_ms": ua_fit_ms / len(horizons) + ua_ms,
                    }
                )
                coverage_rows.append(
                    {
                        "fold_id": fold_id,
                        "machine_id": machine_id,
                        "horizon": horizon,
                        "p50_coverage": float(np.mean(y_true <= p50)),
                        "p90_coverage": float(np.mean(y_true <= p90)),
                        "interval_width": float(np.mean(p90 - p50)),
                    }
                )

                entity_linear_start = time.perf_counter()
                entity_train_x, entity_train_y = make_supervised(train_series, context_window, horizon)
                entity_linear = LinearRegression()
                entity_linear.fit(entity_train_x, entity_train_y)
                entity_linear_pred = entity_linear.predict(test_x)
                entity_linear_ms = (time.perf_counter() - entity_linear_start) * 1000.0
                rows.append(
                    {
                        "fold_id": fold_id,
                        "machine_id": machine_id,
                        "model_name": "entity_specific_linear_regression",
                        "evaluation_mode": "entity_specific_upper_bound",
                        "horizon": horizon,
                        "mae": mae(test_y, entity_linear_pred),
                        "rmse": rmse(test_y, entity_linear_pred),
                        "mape": mape(test_y, entity_linear_pred),
                        "latency_ms": entity_linear_ms,
                    }
                )

    raw_df = pd.DataFrame(rows)
    raw_df.to_csv(output_tables_dir / "machine_transfer_raw.csv", index=False)

    summary_df = (
        raw_df.groupby(["evaluation_mode", "model_name", "horizon"])
        .agg(
            mae_mean=("mae", "mean"),
            mae_std=("mae", "std"),
            rmse_mean=("rmse", "mean"),
            mape_mean=("mape", "mean"),
            latency_ms_mean=("latency_ms", "mean"),
        )
        .reset_index()
        .sort_values(["evaluation_mode", "horizon", "mae_mean"])
    )
    summary_df.to_csv(output_tables_dir / "machine_transfer_summary.csv", index=False)

    zero_shot_winners = (
        raw_df[raw_df["evaluation_mode"] == "zero_shot"]
        .sort_values("mae")
        .groupby(["fold_id", "machine_id", "horizon"], as_index=False)
        .first()[["fold_id", "machine_id", "horizon", "model_name", "mae"]]
    )
    zero_shot_winners.to_csv(output_tables_dir / "machine_transfer_zero_shot_winners.csv", index=False)

    coverage_df = pd.DataFrame(coverage_rows)
    coverage_df.to_csv(output_tables_dir / "machine_transfer_quantile_coverage_raw.csv", index=False)
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
    coverage_summary_df.to_csv(output_tables_dir / "machine_transfer_quantile_coverage.csv", index=False)

    ua_zero_shot = raw_df[
        (raw_df["evaluation_mode"] == "zero_shot") & (raw_df["model_name"] == "global_ua_mstcn_lite")
    ][["fold_id", "machine_id", "horizon", "mae"]].rename(columns={"mae": "ua_zero_shot_mae"})
    entity_specific = raw_df[
        raw_df["model_name"] == "entity_specific_linear_regression"
    ][["fold_id", "machine_id", "horizon", "mae"]].rename(columns={"mae": "entity_specific_linear_mae"})
    gap_df = ua_zero_shot.merge(entity_specific, on=["fold_id", "machine_id", "horizon"])
    gap_df["gap_to_entity_specific_linear"] = gap_df["ua_zero_shot_mae"] - gap_df["entity_specific_linear_mae"]
    gap_summary_df = (
        gap_df.groupby("horizon")
        .agg(
            gap_to_entity_specific_linear_mean=("gap_to_entity_specific_linear", "mean"),
            gap_to_entity_specific_linear_std=("gap_to_entity_specific_linear", "std"),
        )
        .reset_index()
        .sort_values("horizon")
    )
    gap_summary_df.to_csv(output_tables_dir / "machine_transfer_gap_summary.csv", index=False)

    render_zero_shot_summary(summary_df, output_figures_dir / "machine_transfer_zero_shot_mae.png")
    render_gap_summary(gap_summary_df, output_figures_dir / "machine_transfer_gap_to_entity_linear.png")
    render_coverage_summary(coverage_summary_df, output_figures_dir / "machine_transfer_quantile_coverage.png")


if __name__ == "__main__":
    main()
