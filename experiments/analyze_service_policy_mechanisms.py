#!/usr/bin/env python3
"""Summarize broad service-level policy mechanisms and heterogeneity."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


MAIN_METRICS = ["sla_violation", "over_provisioning", "scaling_actions"]
SPLIT_COLUMNS = [
    ("mean_load", "Mean load"),
    ("burstiness", "Burstiness"),
    ("lag1_autocorrelation", "Lag-1 autocorr."),
    ("imputed_ratio", "Imputation ratio"),
]
TAXONOMY_ORDER = [
    "SLA improved, Over improved",
    "SLA improved, Actions worsened",
    "Over improved, SLA worsened",
    "All worsened",
    "Near-neutral",
    "Other mixed",
]


def save_figure(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def safe_lag1_autocorrelation(series: np.ndarray) -> float:
    if len(series) < 2:
        return float("nan")
    left = series[:-1]
    right = series[1:]
    if np.std(left) <= 1e-9 or np.std(right) <= 1e-9:
        return float("nan")
    return float(np.corrcoef(left, right)[0, 1])


def compute_descriptors(service_df: pd.DataFrame, summary_df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, float | int | str]] = []
    for app_du, group in service_df.groupby("app_du"):
        series = group.sort_values("minute_index")["service_cpu_used_cores_proxy"].to_numpy(dtype=float)
        mean_load = float(series.mean())
        std_load = float(series.std(ddof=0))
        rows.append(
            {
                "app_du": app_du,
                "mean_load": mean_load,
                "coefficient_of_variation": std_load / max(mean_load, 1e-9),
                "burstiness": float(np.quantile(series, 0.95)) / max(mean_load, 1e-9),
                "lag1_autocorrelation": safe_lag1_autocorrelation(series),
                "usable_minutes": int((group["imputed"] == 0).sum()),
            }
        )

    descriptor_df = pd.DataFrame(rows)
    return descriptor_df.merge(
        summary_df[
            [
                "app_du",
                "coverage_ratio",
                "imputed_ratio",
                "mean_service_cpu_used_cores_proxy",
                "observed_minutes",
            ]
        ],
        on="app_du",
        how="left",
    )


def build_delta_wide(delta_df: pd.DataFrame) -> pd.DataFrame:
    broad_delta_df = delta_df[delta_df["cohort_label"] == "broad"].copy()
    wide = (
        broad_delta_df.pivot(index="app_du", columns="metric", values="predictive_minus_reactive")
        .rename(
            columns={
                "sla_violation": "sla_violation_delta",
                "over_provisioning": "over_provisioning_delta",
                "scaling_actions": "scaling_actions_delta",
                "average_capacity": "average_capacity_delta",
            }
        )
        .reset_index()
    )
    weights = (
        broad_delta_df[broad_delta_df["metric"] == "sla_violation"][["app_du", "load_weight"]]
        .drop_duplicates(subset=["app_du"])
        .rename(columns={"load_weight": "load_weight"})
    )
    return wide.merge(weights, on="app_du", how="left")


def assign_rank_halves(df: pd.DataFrame, column: str) -> pd.Series:
    ordered = df[["app_du", column]].sort_values([column, "app_du"]).reset_index(drop=True)
    ordered["rank_half"] = np.where(ordered.index < len(ordered) / 2, "low", "high")
    return df[["app_du"]].merge(ordered[["app_du", "rank_half"]], on="app_du", how="left")["rank_half"]


def build_subgroup_summary(analysis_df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    split_order = {column: idx for idx, (column, _) in enumerate(SPLIT_COLUMNS)}
    for column, display_name in SPLIT_COLUMNS:
        threshold = float(analysis_df[column].median())
        groups = analysis_df.copy()
        groups["group_label"] = assign_rank_halves(groups, column)
        for group_label, group_df in groups.groupby("group_label"):
            rows.append(
                {
                    "split_column": column,
                    "split_label": display_name,
                    "split_threshold": threshold,
                    "group_label": group_label,
                    "services": int(group_df["app_du"].nunique()),
                    "sla_delta_mean": float(group_df["sla_violation_delta"].mean()),
                    "over_delta_mean": float(group_df["over_provisioning_delta"].mean()),
                    "actions_delta_mean": float(group_df["scaling_actions_delta"].mean()),
                }
            )
    subgroup_df = pd.DataFrame(rows)
    subgroup_df["split_order"] = subgroup_df["split_column"].map(split_order)
    subgroup_df["group_sort"] = subgroup_df["group_label"].map({"high": 0, "low": 1})
    subgroup_df = subgroup_df.sort_values(["split_order", "group_sort"]).drop(
        columns=["split_order", "group_sort"]
    )
    return subgroup_df


def assign_taxonomy(analysis_df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, float]]:
    thresholds = {
        metric: float(analysis_df[f"{metric}_delta"].abs().quantile(0.25))
        for metric in MAIN_METRICS
    }

    def row_category(row: pd.Series) -> str:
        near_neutral = all(
            abs(float(row[f"{metric}_delta"])) <= thresholds[metric]
            for metric in MAIN_METRICS
        )
        sla_improved = float(row["sla_violation_delta"]) < 0
        over_improved = float(row["over_provisioning_delta"]) < 0
        actions_improved = float(row["scaling_actions_delta"]) < 0
        if near_neutral:
            return "Near-neutral"
        if sla_improved and over_improved:
            return "SLA improved, Over improved"
        if sla_improved and not actions_improved:
            return "SLA improved, Actions worsened"
        if over_improved and not sla_improved:
            return "Over improved, SLA worsened"
        if (not sla_improved) and (not over_improved) and (not actions_improved):
            return "All worsened"
        return "Other mixed"

    taxonomy_df = analysis_df.copy()
    taxonomy_df["outcome_taxonomy"] = taxonomy_df.apply(row_category, axis=1)
    return taxonomy_df, thresholds


def build_taxonomy_summary(taxonomy_df: pd.DataFrame) -> pd.DataFrame:
    total_services = int(taxonomy_df["app_du"].nunique())
    total_load = float(taxonomy_df["mean_load"].sum())
    summary_df = (
        taxonomy_df.groupby("outcome_taxonomy")
        .agg(
            services=("app_du", "nunique"),
            mean_sla_delta=("sla_violation_delta", "mean"),
            mean_over_delta=("over_provisioning_delta", "mean"),
            mean_actions_delta=("scaling_actions_delta", "mean"),
            load_sum=("mean_load", "sum"),
        )
        .reset_index()
    )
    summary_df["service_share_pct"] = 100.0 * summary_df["services"] / max(total_services, 1)
    summary_df["load_share_pct"] = 100.0 * summary_df["load_sum"] / max(total_load, 1e-9)
    summary_df["taxonomy_order"] = summary_df["outcome_taxonomy"].map(
        {label: idx for idx, label in enumerate(TAXONOMY_ORDER)}
    )
    return summary_df.sort_values("taxonomy_order").drop(columns=["taxonomy_order", "load_sum"])


def build_delta_summary(analysis_df: pd.DataFrame, stability_summary_df: pd.DataFrame) -> pd.DataFrame:
    broad_row = stability_summary_df[stability_summary_df["cohort_label"] == "broad"]
    if broad_row.empty:
        raise ValueError("Broad cohort row missing from stability summary.")
    broad_row = broad_row.iloc[0]

    rows: list[dict[str, object]] = []
    prefix_map = {
        "sla_violation": "pred_vs_reactive_sla",
        "over_provisioning": "pred_vs_reactive_over",
        "scaling_actions": "pred_vs_reactive_actions",
    }
    for metric, prefix in prefix_map.items():
        rows.append(
            {
                "metric": metric,
                "equal_weighted_mean_delta": float(broad_row[f"{prefix}_equal_delta"]),
                "equal_weighted_ci_low": float(broad_row[f"{prefix}_equal_ci_low"]),
                "equal_weighted_ci_high": float(broad_row[f"{prefix}_equal_ci_high"]),
                "equal_weighted_stability": broad_row[f"{prefix}_equal_stability"],
                "equal_weighted_median_delta": float(broad_row[f"{prefix}_equal_median_delta"]),
                "equal_weighted_q25_delta": float(broad_row[f"{prefix}_equal_q25_delta"]),
                "equal_weighted_q75_delta": float(broad_row[f"{prefix}_equal_q75_delta"]),
                "equal_weighted_iqr_delta": float(broad_row[f"{prefix}_equal_iqr_delta"]),
                "services_improved": int(broad_row[f"{prefix}_services_improved"]),
                "services_worsened": int(broad_row[f"{prefix}_services_worsened"]),
                "services_unchanged": int(broad_row[f"{prefix}_services_unchanged"]),
                "load_weighted_mean_delta": float(broad_row[f"{prefix}_load_delta"]),
                "load_weighted_ci_low": float(broad_row[f"{prefix}_load_ci_low"]),
                "load_weighted_ci_high": float(broad_row[f"{prefix}_load_ci_high"]),
                "load_weighted_stability": broad_row[f"{prefix}_load_stability"],
            }
        )
    return pd.DataFrame(rows)


def render_delta_distribution(analysis_df: pd.DataFrame, path: Path) -> None:
    metric_specs = [
        ("sla_violation_delta", "SLA delta", "#0f7b6c", "#8b1e3f"),
        ("over_provisioning_delta", "Over-provisioning delta", "#0f7b6c", "#c97c00"),
        ("scaling_actions_delta", "Scaling-actions delta", "#0f7b6c", "#8b1e3f"),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(12.0, 4.0), sharex=True)
    for ax, (column, title, improve_color, degrade_color) in zip(axes, metric_specs):
        values = np.sort(analysis_df[column].to_numpy(dtype=float))
        ranks = np.arange(1, len(values) + 1)
        colors = np.where(values < 0, improve_color, degrade_color)
        ax.plot(ranks, values, color="#4c4c4c", linewidth=0.9, alpha=0.55)
        ax.scatter(ranks, values, c=colors, s=14, alpha=0.9, edgecolors="none")
        ax.axhline(0.0, color="#444444", linewidth=0.9, alpha=0.85)
        ax.set_title(title)
        ax.grid(axis="y", alpha=0.18, linewidth=0.5)
        ax.set_xlabel("Service rank")
    axes[0].set_ylabel("Predictive - reactive")
    fig.suptitle("Service-level predictive-minus-reactive delta distributions", y=1.02)
    save_figure(fig, path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--service-csv", type=Path, required=True)
    parser.add_argument("--service-summary-csv", type=Path, required=True)
    parser.add_argument("--policy-delta-csv", type=Path, required=True)
    parser.add_argument("--stability-summary-csv", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    service_df = pd.read_csv(args.service_csv)
    summary_df = pd.read_csv(args.service_summary_csv)
    delta_df = pd.read_csv(args.policy_delta_csv)
    stability_summary_df = pd.read_csv(args.stability_summary_csv)

    output_tables_dir = args.output_dir / "tables"
    output_figures_dir = args.output_dir / "figures"
    output_tables_dir.mkdir(parents=True, exist_ok=True)
    output_figures_dir.mkdir(parents=True, exist_ok=True)

    descriptor_df = compute_descriptors(service_df, summary_df)
    delta_wide_df = build_delta_wide(delta_df)
    analysis_df = descriptor_df.merge(delta_wide_df, on="app_du", how="inner")

    taxonomy_df, taxonomy_thresholds = assign_taxonomy(analysis_df)
    subgroup_summary_df = build_subgroup_summary(taxonomy_df)
    taxonomy_summary_df = build_taxonomy_summary(taxonomy_df)
    delta_summary_df = build_delta_summary(taxonomy_df, stability_summary_df)

    taxonomy_df.to_csv(output_tables_dir / "service_policy_mechanism_by_service.csv", index=False)
    subgroup_summary_df.to_csv(output_tables_dir / "service_policy_subgroup_summary.csv", index=False)
    taxonomy_summary_df.to_csv(output_tables_dir / "service_policy_outcome_taxonomy.csv", index=False)
    delta_summary_df.to_csv(output_tables_dir / "service_policy_delta_summary.csv", index=False)
    pd.DataFrame([taxonomy_thresholds]).to_csv(
        output_tables_dir / "service_policy_taxonomy_thresholds.csv", index=False
    )

    render_delta_distribution(
        taxonomy_df,
        output_figures_dir / "service_policy_delta_distribution.png",
    )


if __name__ == "__main__":
    main()
