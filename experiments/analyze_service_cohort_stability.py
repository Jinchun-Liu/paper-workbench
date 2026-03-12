#!/usr/bin/env python3
"""Analyze service-cohort stability and decide whether broad results should be promoted."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


FORECAST_HEADLINE_MODEL = "ua_mstcn_lite_quantile_forest"
POLICY_HEADLINE_METRICS = ["over_provisioning", "scaling_actions"]
SLA_METRIC = "sla_violation"
OPTIONAL_METRICS = [SLA_METRIC, "average_capacity"]


def sign_label(value: float) -> str:
    if value > 0:
        return "positive"
    if value < 0:
        return "negative"
    return "zero"


def stability_label(ci_low: float, ci_high: float) -> str:
    if ci_high < 0:
        return "stable improvement"
    if ci_low > 0:
        return "stable degradation"
    return "not stable"


def forecasting_summary(forecast_raw: pd.DataFrame, cohort_label: str) -> tuple[pd.DataFrame, dict[str, object]]:
    overall = (
        forecast_raw.groupby("model_name")["mae"].mean().sort_values().reset_index(name="mean_mae")
    )
    overall["rank"] = np.arange(1, len(overall) + 1)
    horizon_winners = (
        forecast_raw.groupby(["horizon", "model_name"])["mae"]
        .mean()
        .reset_index()
        .sort_values(["horizon", "mae"])
        .groupby("horizon", as_index=False)
        .first()
        .rename(columns={"model_name": "model_name", "mae": "mean_mae"})
    )
    overall_records = overall.assign(cohort_label=cohort_label, scope="overall_ranking", horizon="all")[
        ["cohort_label", "scope", "horizon", "rank", "model_name", "mean_mae"]
    ]
    horizon_records = horizon_winners.assign(cohort_label=cohort_label, scope="horizon_winner", rank=1)[
        ["cohort_label", "scope", "horizon", "rank", "model_name", "mean_mae"]
    ]
    records = pd.concat(
        [overall_records, horizon_records],
        ignore_index=True,
    )
    return records, {
        "forecast_winner": overall.iloc[0]["model_name"],
        "forecast_winner_mae": float(overall.iloc[0]["mean_mae"]),
        "forecast_runner_up": overall.iloc[1]["model_name"] if len(overall) > 1 else overall.iloc[0]["model_name"],
        "forecast_runner_up_mae": float(overall.iloc[1]["mean_mae"]) if len(overall) > 1 else float(overall.iloc[0]["mean_mae"]),
    }


def build_policy_delta_frame(
    policy_raw: pd.DataFrame,
    summary_df: pd.DataFrame,
    cohort_label: str,
) -> pd.DataFrame:
    pivot = policy_raw.pivot(index="app_du", columns="policy_name")
    required_columns = {"predictive_service", "reactive_service"}
    missing = required_columns.difference(policy_raw["policy_name"].unique())
    if missing:
        raise ValueError(f"Missing policies in policy raw table: {sorted(missing)}")

    weights = summary_df.set_index("app_du")["mean_service_cpu_used_cores_proxy"]
    rows: list[dict] = []
    for app_du in sorted(policy_raw["app_du"].unique()):
        if app_du not in pivot.index or app_du not in weights.index:
            continue
        for metric in POLICY_HEADLINE_METRICS + OPTIONAL_METRICS:
            rows.append(
                {
                    "cohort_label": cohort_label,
                    "app_du": app_du,
                    "metric": metric,
                    "predictive_minus_reactive": float(
                        pivot.loc[app_du, (metric, "predictive_service")]
                        - pivot.loc[app_du, (metric, "reactive_service")]
                    ),
                    "load_weight": float(weights.loc[app_du]),
                }
            )
    return pd.DataFrame(rows)


def bootstrap_deltas(
    delta_df: pd.DataFrame,
    cohort_label: str,
    seed: int,
    n_resamples: int,
) -> tuple[pd.DataFrame, dict[str, dict[str, float | str]]]:
    rng = np.random.default_rng(seed)
    rows: list[dict] = []
    summary: dict[str, dict[str, float | str]] = {}

    for metric, metric_df in delta_df.groupby("metric"):
        deltas = metric_df["predictive_minus_reactive"].to_numpy(dtype=float)
        weights = metric_df["load_weight"].to_numpy(dtype=float)
        sample_indices = rng.integers(0, len(deltas), size=(n_resamples, len(deltas)))
        sampled_deltas = deltas[sample_indices]
        sampled_weights = weights[sample_indices]
        eq_samples = sampled_deltas.mean(axis=1)
        load_samples = (sampled_deltas * sampled_weights).sum(axis=1) / np.maximum(
            sampled_weights.sum(axis=1), 1e-9
        )

        eq_mean = float(deltas.mean())
        load_mean = float(np.average(deltas, weights=weights))
        eq_ci_low, eq_ci_high = np.quantile(eq_samples, [0.025, 0.975])
        load_ci_low, load_ci_high = np.quantile(load_samples, [0.025, 0.975])
        eq_label = stability_label(float(eq_ci_low), float(eq_ci_high))
        load_label = stability_label(float(load_ci_low), float(load_ci_high))
        eq_sign = sign_label(eq_mean)

        summary[metric] = {
            "equal_weighted_mean_delta": eq_mean,
            "equal_weighted_ci_low": float(eq_ci_low),
            "equal_weighted_ci_high": float(eq_ci_high),
            "equal_weighted_stability": eq_label,
            "equal_weighted_sign": eq_sign,
            "load_weighted_mean_delta": load_mean,
            "load_weighted_ci_low": float(load_ci_low),
            "load_weighted_ci_high": float(load_ci_high),
            "load_weighted_stability": load_label,
        }

        rows.extend(
            {
                "cohort_label": cohort_label,
                "metric": metric,
                "statistic_type": "equal_weighted_mean_delta",
                "resample_index": index,
                "value": float(value),
            }
            for index, value in enumerate(eq_samples)
        )
        rows.extend(
            {
                "cohort_label": cohort_label,
                "metric": metric,
                "statistic_type": "load_weighted_mean_delta",
                "resample_index": index,
                "value": float(value),
            }
            for index, value in enumerate(load_samples)
        )

    return pd.DataFrame(rows), summary


def build_summary_row(
    cohort_label: str,
    cohort_summary_df: pd.DataFrame,
    forecast_meta: dict[str, object],
    policy_meta: dict[str, dict[str, float | str]],
) -> dict[str, object]:
    row: dict[str, object] = {
        "cohort_label": cohort_label,
        "services": int(cohort_summary_df["app_du"].nunique()),
        "mean_coverage_ratio": float(cohort_summary_df["coverage_ratio"].mean()),
        "mean_container_hit_ratio": float(cohort_summary_df["container_hit_ratio"].mean()),
        "forecast_winner": forecast_meta["forecast_winner"],
        "forecast_winner_mae": forecast_meta["forecast_winner_mae"],
        "forecast_runner_up": forecast_meta["forecast_runner_up"],
        "forecast_runner_up_mae": forecast_meta["forecast_runner_up_mae"],
    }
    for metric, prefix in [
        ("sla_violation", "pred_vs_reactive_sla"),
        ("over_provisioning", "pred_vs_reactive_over"),
        ("scaling_actions", "pred_vs_reactive_actions"),
        ("average_capacity", "pred_vs_reactive_capacity"),
    ]:
        info = policy_meta[metric]
        row[f"{prefix}_equal_delta"] = info["equal_weighted_mean_delta"]
        row[f"{prefix}_equal_ci_low"] = info["equal_weighted_ci_low"]
        row[f"{prefix}_equal_ci_high"] = info["equal_weighted_ci_high"]
        row[f"{prefix}_equal_stability"] = info["equal_weighted_stability"]
        row[f"{prefix}_equal_sign"] = info["equal_weighted_sign"]
        row[f"{prefix}_load_delta"] = info["load_weighted_mean_delta"]
        row[f"{prefix}_load_ci_low"] = info["load_weighted_ci_low"]
        row[f"{prefix}_load_ci_high"] = info["load_weighted_ci_high"]
        row[f"{prefix}_load_stability"] = info["load_weighted_stability"]
    return row


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--top10-forecast-raw", type=Path, required=True)
    parser.add_argument("--top10-policy-raw", type=Path, required=True)
    parser.add_argument("--top10-summary-csv", type=Path, required=True)
    parser.add_argument("--broad-forecast-raw", type=Path, required=True)
    parser.add_argument("--broad-policy-raw", type=Path, required=True)
    parser.add_argument("--broad-summary-csv", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--bootstrap-seed", type=int, default=20260311)
    parser.add_argument("--bootstrap-resamples", type=int, default=10_000)
    args = parser.parse_args()

    top10_forecast_raw = pd.read_csv(args.top10_forecast_raw)
    top10_policy_raw = pd.read_csv(args.top10_policy_raw)
    top10_summary_df = pd.read_csv(args.top10_summary_csv)
    broad_forecast_raw = pd.read_csv(args.broad_forecast_raw)
    broad_policy_raw = pd.read_csv(args.broad_policy_raw)
    broad_summary_df = pd.read_csv(args.broad_summary_csv)

    output_tables_dir = args.output_dir / "tables"
    output_tables_dir.mkdir(parents=True, exist_ok=True)

    forecast_winners_frames = []
    compact_rows = []
    policy_delta_frames = []
    bootstrap_frames = []
    policy_meta_by_cohort: dict[str, dict[str, dict[str, float | str]]] = {}
    forecast_meta_by_cohort: dict[str, dict[str, object]] = {}

    for cohort_label, forecast_raw, policy_raw, summary_df, seed_offset in [
        ("top10", top10_forecast_raw, top10_policy_raw, top10_summary_df, 0),
        ("broad", broad_forecast_raw, broad_policy_raw, broad_summary_df, 1),
    ]:
        winners_df, forecast_meta = forecasting_summary(forecast_raw, cohort_label)
        forecast_winners_frames.append(winners_df)
        forecast_meta_by_cohort[cohort_label] = forecast_meta

        delta_df = build_policy_delta_frame(policy_raw, summary_df, cohort_label)
        policy_delta_frames.append(delta_df)
        bootstrap_df, policy_meta = bootstrap_deltas(
            delta_df=delta_df,
            cohort_label=cohort_label,
            seed=args.bootstrap_seed + seed_offset,
            n_resamples=args.bootstrap_resamples,
        )
        bootstrap_frames.append(bootstrap_df)
        policy_meta_by_cohort[cohort_label] = policy_meta
        compact_rows.append(build_summary_row(cohort_label, summary_df, forecast_meta, policy_meta))

    forecast_winners_df = pd.concat(forecast_winners_frames, ignore_index=True)
    forecast_winners_df.to_csv(output_tables_dir / "service_forecasting_winners.csv", index=False)

    policy_delta_df = pd.concat(policy_delta_frames, ignore_index=True)
    policy_delta_df.to_csv(output_tables_dir / "service_policy_delta_by_service.csv", index=False)

    bootstrap_df = pd.concat(bootstrap_frames, ignore_index=True)
    bootstrap_df.to_csv(output_tables_dir / "service_policy_bootstrap.csv", index=False)

    stability_summary_df = pd.DataFrame(compact_rows)

    top10_row = stability_summary_df[stability_summary_df["cohort_label"] == "top10"].iloc[0]
    broad_row = stability_summary_df[stability_summary_df["cohort_label"] == "broad"].iloc[0]

    forecast_flip = broad_row["forecast_winner"] != FORECAST_HEADLINE_MODEL
    over_sign_flip = broad_row["pred_vs_reactive_over_equal_sign"] != top10_row["pred_vs_reactive_over_equal_sign"]
    actions_sign_flip = (
        broad_row["pred_vs_reactive_actions_equal_sign"] != top10_row["pred_vs_reactive_actions_equal_sign"]
    )
    sla_sign_flip = broad_row["pred_vs_reactive_sla_equal_sign"] != top10_row["pred_vs_reactive_sla_equal_sign"]
    over_not_stable = (
        broad_row["pred_vs_reactive_over_equal_delta"] < 0
        and broad_row["pred_vs_reactive_over_equal_stability"] == "not stable"
    )
    actions_not_stable = (
        broad_row["pred_vs_reactive_actions_equal_delta"] < 0
        and broad_row["pred_vs_reactive_actions_equal_stability"] == "not stable"
    )

    reasons = []
    if forecast_flip:
        reasons.append("forecast_headline_flip")
    if over_sign_flip:
        reasons.append("over_provisioning_sign_flip")
    if actions_sign_flip:
        reasons.append("scaling_actions_sign_flip")
    if sla_sign_flip:
        reasons.append("sla_sign_flip")
    if over_not_stable:
        reasons.append("over_provisioning_mean_negative_but_not_stable")
    if actions_not_stable:
        reasons.append("scaling_actions_mean_negative_but_not_stable")

    promotion_required = bool(reasons)
    broad_role = "promote_to_main_result" if promotion_required else "robustness_section"
    decision_df = pd.DataFrame(
        [
            {
                "forecast_headline_model": FORECAST_HEADLINE_MODEL,
                "promotion_required": promotion_required,
                "broad_role": broad_role,
                "promotion_reasons": ";".join(reasons),
            }
        ]
    )
    decision_df.to_csv(output_tables_dir / "service_cohort_promotion_decision.csv", index=False)

    stability_summary_df["promotion_required"] = stability_summary_df["cohort_label"].eq("broad") & promotion_required
    stability_summary_df["broad_role"] = np.where(
        stability_summary_df["cohort_label"].eq("broad"),
        broad_role,
        "mainline_reference",
    )
    stability_summary_df.to_csv(output_tables_dir / "service_cohort_stability_summary.csv", index=False)


if __name__ == "__main__":
    main()
