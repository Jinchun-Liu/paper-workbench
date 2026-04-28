#!/usr/bin/env python3
"""Run the aggregate QLR smoke gate before larger uncertainty-aware experiments."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from models.baselines import quantile_linear_regression


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


def finite_or_false(values: list[float]) -> bool:
    return bool(np.all(np.isfinite(np.asarray(values, dtype=float))))


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

    output_dir = args.output_dir or (repo_root / "experiments" / "results" / "qlr_smoke")
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(csv_path)
    series = df["cluster_cpu_utilization_mean"].to_numpy(dtype=float)
    context_window = int(config["forecast"]["context_window"])
    horizons = list(config["forecast"]["horizons"])
    train_ratio = float(config["forecast"]["train_ratio"])
    valid_ratio = float(config["forecast"]["valid_ratio"])
    train_series, test_series = split_series(series, train_ratio, valid_ratio)

    rows: list[dict] = []
    gate_failures: list[str] = []
    for horizon in horizons:
        t0 = time.perf_counter()
        result = quantile_linear_regression(
            train_series,
            test_series,
            context_window,
            horizon,
            alpha=args.alpha,
            solver=args.solver,
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        y_true = result.y_true
        p50 = result.p50
        p90 = result.p90
        non_crossing_violations = int(np.sum(p90 < p50))
        metrics = {
            "horizon": horizon,
            "n_predictions": int(len(y_true)),
            "mae": mae(y_true, p50),
            "rmse": rmse(y_true, p50),
            "mape": mape(y_true, p50),
            "p50_pinball": pinball(y_true, p50, 0.5),
            "p90_pinball": pinball(y_true, p90, 0.9),
            "p50_coverage": float(np.mean(y_true <= p50)),
            "p90_coverage": float(np.mean(y_true <= p90)),
            "interval_width": float(np.mean(p90 - p50)),
            "non_crossing_violations": non_crossing_violations,
            "fit_eval_ms": elapsed_ms,
        }
        row_pass = (
            len(y_true) > 0
            and len(y_true) == len(p50) == len(p90)
            and non_crossing_violations == 0
            and finite_or_false(
                [
                    metrics["mae"],
                    metrics["rmse"],
                    metrics["mape"],
                    metrics["p50_pinball"],
                    metrics["p90_pinball"],
                    metrics["p50_coverage"],
                    metrics["p90_coverage"],
                    metrics["interval_width"],
                ]
            )
        )
        metrics["status"] = "pass" if row_pass else "fail"
        rows.append(metrics)
        if not row_pass:
            gate_failures.append(f"horizon {horizon} failed smoke gate")

    metrics_df = pd.DataFrame(rows)
    metrics_path = output_dir / "aggregate_qlr_smoke_metrics.csv"
    metrics_df.to_csv(metrics_path, index=False)

    split_report = [
        "# Aggregate QLR Smoke Report",
        "",
        "- run_id: `qlr_aggregate_smoke_20260427`",
        f"- series_path: `{csv_path}`",
        f"- train_plus_validation_rows_used_for_fit: `{len(train_series)}`",
        f"- heldout_test_rows_used_for_evaluation: `{len(test_series)}`",
        f"- context_window: `{context_window}`",
        f"- horizons: `{', '.join(str(h) for h in horizons)}`",
        f"- alpha: `{args.alpha}`",
        f"- solver: `{args.solver}`",
        f"- metrics_csv: `{metrics_path}`",
        f"- status: `{'pass' if not gate_failures else 'fail'}`",
        "",
        "## Gate Checks",
        "",
        "- P50/P90 predictions are nonempty.",
        "- Prediction lengths align with `y_true`.",
        "- P90 is guarded to be no lower than P50.",
        "- MAE, pinball, coverage, and interval-width metrics are finite.",
        "- Test rows are passed only to the evaluation side of the baseline API.",
        "",
        "## Results",
        "",
        "```csv",
        metrics_df.to_csv(index=False, lineterminator="\n").strip(),
        "```",
    ]
    report_path = output_dir / "aggregate_qlr_smoke_report.md"
    report_path.write_text("\n".join(split_report) + "\n", encoding="utf-8")

    if gate_failures:
        raise SystemExit("; ".join(gate_failures))


if __name__ == "__main__":
    main()
