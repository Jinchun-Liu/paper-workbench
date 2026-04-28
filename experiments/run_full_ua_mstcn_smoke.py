#!/usr/bin/env python3
"""Stage-1 smoke run for the full PyTorch UA-MSTCN backbone.

This entrypoint is intentionally independent from ``models.ua_mstcn`` so the
existing UA-MSTCN-Lite surrogate remains auditable as a separate baseline.
The smoke run uses only the aggregate prefix, writes isolated artifacts, and
does not update central ``metrics.csv``.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import sys
import time
from pathlib import Path

import torch
from torch.utils.data import DataLoader, TensorDataset

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from models.full_ua_mstcn import FullUAMSTCN, pinball_loss


RUN_ID = "full_ua_mstcn_smoke_20260428"


def resolve_path(path: Path, repo_root: Path) -> Path:
    if path.is_absolute():
        return path
    if path.parts and path.parts[0] == repo_root.name:
        return repo_root.parent.joinpath(path)
    return repo_root.joinpath(path)


def read_series(series_csv: Path, column: str) -> list[float]:
    values: list[float] = []
    with series_csv.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if column not in (reader.fieldnames or []):
            raise KeyError(f"Column {column!r} not found in {series_csv}")
        for row in reader:
            values.append(float(row[column]))
    if not values:
        raise ValueError(f"No rows read from {series_csv}")
    return values


def split_bounds(length: int, train_ratio: float, valid_ratio: float) -> tuple[int, int]:
    train_end = int(length * train_ratio)
    valid_end = int(length * (train_ratio + valid_ratio))
    if not (0 < train_end < valid_end < length):
        raise ValueError("Invalid split ratios for smoke series length")
    return train_end, valid_end


def build_windows(
    normalized_values: list[float],
    raw_values: list[float],
    *,
    context_window: int,
    horizons: tuple[int, ...],
    origin_start: int,
    origin_end: int,
) -> tuple[torch.Tensor, torch.Tensor, list[dict]]:
    max_horizon = max(horizons)
    features: list[list[list[float]]] = []
    targets: list[list[float]] = []
    row_meta: list[dict] = []
    last_origin = origin_end - max_horizon + 1
    for origin in range(max(context_window, origin_start), max(context_window, last_origin)):
        history = normalized_values[origin - context_window : origin]
        if len(history) != context_window:
            continue
        feature_rows: list[list[float]] = []
        for minute_index, demand_value in enumerate(history, start=origin - context_window):
            angle = 2.0 * math.pi * (minute_index % 1440) / 1440.0
            feature_rows.append([demand_value, 1.0, math.sin(angle), math.cos(angle)])
        target_values = [normalized_values[origin + horizon - 1] for horizon in horizons]
        raw_targets = [raw_values[origin + horizon - 1] for horizon in horizons]
        features.append(feature_rows)
        targets.append(target_values)
        row_meta.append(
            {
                "origin_index": origin,
                "target_indices": ";".join(str(origin + horizon - 1) for horizon in horizons),
                "raw_targets": raw_targets,
            }
        )
    if not features:
        raise ValueError("No supervised windows were created")
    return (
        torch.tensor(features, dtype=torch.float32),
        torch.tensor(targets, dtype=torch.float32),
        row_meta,
    )


def pinball_scalar(actual: float, predicted: float, quantile: float) -> float:
    error = actual - predicted
    return max((quantile - 1.0) * error, quantile * error)


def evaluate(
    model: FullUAMSTCN,
    features: torch.Tensor,
    targets: torch.Tensor,
    row_meta: list[dict],
    *,
    mean: float,
    std: float,
    device: torch.device,
    split_name: str,
    horizons: tuple[int, ...],
) -> tuple[list[dict], list[dict], tuple[int, ...]]:
    model.eval()
    with torch.no_grad():
        predictions = model(features.to(device)).cpu()
    output_shape = tuple(int(value) for value in predictions.shape)
    target_raw = targets * std + mean
    prediction_raw = predictions * std + mean

    metrics_rows: list[dict] = []
    prediction_rows: list[dict] = []
    for horizon_index, horizon in enumerate(horizons):
        y_true = target_raw[:, horizon_index]
        p50 = prediction_raw[:, horizon_index, 0]
        p90 = prediction_raw[:, horizon_index, 1]
        errors = y_true - p50
        crossing = p90 < p50
        interval_width = p90 - p50
        mae = torch.mean(torch.abs(errors)).item()
        rmse = torch.sqrt(torch.mean(errors**2)).item()
        mape = torch.mean(torch.abs(errors) / torch.clamp(torch.abs(y_true), min=1e-6)).item()
        p50_pinball = sum(
            pinball_scalar(float(actual), float(pred), 0.5) for actual, pred in zip(y_true, p50)
        ) / len(y_true)
        p90_pinball = sum(
            pinball_scalar(float(actual), float(pred), 0.9) for actual, pred in zip(y_true, p90)
        ) / len(y_true)
        metrics_rows.append(
            {
                "run_id": RUN_ID,
                "split": split_name,
                "model_name": "full_ua_mstcn_smoke",
                "horizon": horizon,
                "n_predictions": len(y_true),
                "mae": mae,
                "rmse": rmse,
                "mape": mape,
                "p50_pinball": p50_pinball,
                "p90_pinball": p90_pinball,
                "p50_coverage": torch.mean((y_true <= p50).float()).item(),
                "p90_coverage": torch.mean((y_true <= p90).float()).item(),
                "interval_width": torch.mean(interval_width).item(),
                "crossing_count": int(torch.sum(crossing).item()),
                "crossing_rate": float(torch.mean(crossing.float()).item()),
            }
        )
        for row_index, meta in enumerate(row_meta):
            prediction_rows.append(
                {
                    "run_id": RUN_ID,
                    "split": split_name,
                    "horizon": horizon,
                    "origin_index": meta["origin_index"],
                    "target_index": int(meta["target_indices"].split(";")[horizon_index]),
                    "y_true": float(y_true[row_index]),
                    "p50": float(p50[row_index]),
                    "p90": float(p90[row_index]),
                    "crossing": bool(crossing[row_index]),
                }
            )
    return metrics_rows, prediction_rows, output_shape


def finite_metrics(rows: list[dict]) -> bool:
    for row in rows:
        for value in row.values():
            if isinstance(value, float) and not math.isfinite(value):
                return False
    return True


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"No rows to write for {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--series-csv", type=Path, default=Path("data/processed/cluster_series_v2018.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("experiments/results/full_ua_mstcn_smoke"))
    parser.add_argument("--column", default="cluster_cpu_utilization_mean")
    parser.add_argument("--limit-rows", type=int, default=2000)
    parser.add_argument("--context-window", type=int, default=60)
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    series_csv = resolve_path(args.series_csv, repo_root)
    output_dir = resolve_path(args.output_dir, repo_root)
    if output_dir.exists():
        raise SystemExit(f"Refusing to overwrite existing output directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=False)

    random.seed(args.seed)
    torch.manual_seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(args.seed)
        torch.cuda.reset_peak_memory_stats()

    raw_values = read_series(series_csv, args.column)[: int(args.limit_rows)]
    horizons = (1, 5, 10)
    train_end, valid_end = split_bounds(len(raw_values), 0.70, 0.15)
    train_prefix = raw_values[:train_end]
    mean = sum(train_prefix) / len(train_prefix)
    variance = sum((value - mean) ** 2 for value in train_prefix) / max(len(train_prefix) - 1, 1)
    std = max(math.sqrt(variance), 1e-6)
    normalized = [(value - mean) / std for value in raw_values]

    train_x, train_y, _ = build_windows(
        normalized,
        raw_values,
        context_window=args.context_window,
        horizons=horizons,
        origin_start=args.context_window,
        origin_end=train_end,
    )
    valid_x, valid_y, valid_meta = build_windows(
        normalized,
        raw_values,
        context_window=args.context_window,
        horizons=horizons,
        origin_start=train_end,
        origin_end=valid_end,
    )
    test_x, test_y, test_meta = build_windows(
        normalized,
        raw_values,
        context_window=args.context_window,
        horizons=horizons,
        origin_start=valid_end,
        origin_end=len(raw_values),
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = FullUAMSTCN(input_channels=train_x.shape[-1], horizons=horizons).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    train_loader = DataLoader(
        TensorDataset(train_x, train_y),
        batch_size=int(args.batch_size),
        shuffle=True,
        drop_last=False,
    )

    train_losses: list[float] = []
    valid_losses: list[float] = []
    started_at = time.perf_counter()
    for _epoch in range(int(args.epochs)):
        model.train()
        batch_losses: list[float] = []
        for batch_x, batch_y in train_loader:
            optimizer.zero_grad(set_to_none=True)
            predictions = model(batch_x.to(device))
            loss = pinball_loss(predictions, batch_y.to(device))
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            batch_losses.append(float(loss.detach().cpu()))
        train_losses.append(sum(batch_losses) / max(len(batch_losses), 1))
        model.eval()
        with torch.no_grad():
            valid_loss = pinball_loss(model(valid_x.to(device)), valid_y.to(device))
        valid_losses.append(float(valid_loss.cpu()))

    runtime_seconds = time.perf_counter() - started_at
    valid_metrics, valid_predictions, valid_shape = evaluate(
        model,
        valid_x,
        valid_y,
        valid_meta,
        mean=mean,
        std=std,
        device=device,
        split_name="validation",
        horizons=horizons,
    )
    test_metrics, test_predictions, test_shape = evaluate(
        model,
        test_x,
        test_y,
        test_meta,
        mean=mean,
        std=std,
        device=device,
        split_name="test",
        horizons=horizons,
    )
    all_metrics = valid_metrics + test_metrics
    all_predictions = valid_predictions + test_predictions
    write_csv(output_dir / "full_ua_mstcn_smoke_metrics.csv", all_metrics)
    write_csv(output_dir / "full_ua_mstcn_smoke_predictions.csv", all_predictions)

    crossing_total = sum(int(row["crossing_count"]) for row in all_metrics)
    expected_shape = (len(test_x), len(horizons), 2)
    loss_decreased = train_losses[-1] <= train_losses[0] or valid_losses[-1] <= valid_losses[0]
    shape_ok = test_shape == expected_shape and valid_shape[-2:] == (len(horizons), 2)
    gate_failures = []
    if not loss_decreased:
        gate_failures.append("training or validation loss did not decrease over the smoke epochs")
    if not shape_ok:
        gate_failures.append(f"unexpected output shape: test={test_shape}, expected={expected_shape}")
    if crossing_total != 0:
        gate_failures.append(f"non-crossing gate failed with {crossing_total} crossings")
    if not finite_metrics(all_metrics):
        gate_failures.append("metrics contain non-finite values")

    status = {
        "run_id": RUN_ID,
        "status": "pass" if not gate_failures else "fail",
        "series_csv": str(series_csv),
        "output_dir": str(output_dir),
        "limit_rows": int(args.limit_rows),
        "context_window": int(args.context_window),
        "horizons": list(horizons),
        "train_end": train_end,
        "valid_end": valid_end,
        "test_start": valid_end,
        "test_split_use": "evaluation only; no fitting, parameter selection, or policy selection",
        "model": {
            "input_channels": int(train_x.shape[-1]),
            "hidden_width": 32,
            "dilations": [1, 2, 4],
            "quantiles": ["p50", "p90"],
            "non_crossing": "p90 = p50 + softplus(delta90)",
        },
        "environment": {
            "python": sys.version,
            "torch": torch.__version__,
            "cuda_available": bool(torch.cuda.is_available()),
            "device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
            "peak_cuda_memory_bytes": int(torch.cuda.max_memory_allocated()) if torch.cuda.is_available() else 0,
        },
        "runtime_seconds": runtime_seconds,
        "train_losses": train_losses,
        "valid_losses": valid_losses,
        "test_output_shape": list(test_shape),
        "gate_failures": gate_failures,
        "metrics_csv_updated": False,
    }
    (output_dir / "full_ua_mstcn_smoke_status.json").write_text(
        json.dumps(status, indent=2), encoding="utf-8"
    )

    report_lines = [
        "# Full UA-MSTCN Smoke Report",
        "",
        f"- run_id: `{RUN_ID}`",
        f"- status: `{status['status']}`",
        f"- output_dir: `{output_dir}`",
        f"- device: `{status['environment']['device']}`",
        f"- torch: `{torch.__version__}`",
        f"- runtime_seconds: `{runtime_seconds:.3f}`",
        "- scope: Stage 1 smoke only; no manuscript conclusion is changed.",
        "- test split use: evaluation only; model fitting uses the training prefix and validation is only monitored.",
        "- central metrics.csv updated: `False`",
        "",
        "## Gate Result",
        "",
    ]
    if gate_failures:
        report_lines.extend(f"- FAIL: {failure}" for failure in gate_failures)
    else:
        report_lines.append("- PASS: smoke gate passed.")
    report_lines.extend(
        [
            "",
            "## Loss Trace",
            "",
            f"- train_losses: `{', '.join(f'{loss:.6f}' for loss in train_losses)}`",
            f"- valid_losses: `{', '.join(f'{loss:.6f}' for loss in valid_losses)}`",
            "",
            "## Metrics",
            "",
            "```csv",
        ]
    )
    with (output_dir / "full_ua_mstcn_smoke_metrics.csv").open("r", encoding="utf-8") as handle:
        report_lines.extend(handle.read().strip().splitlines())
    report_lines.extend(["```", ""])
    (output_dir / "full_ua_mstcn_smoke_report.md").write_text(
        "\n".join(report_lines), encoding="utf-8"
    )

    if gate_failures:
        raise SystemExit(f"Full UA-MSTCN smoke gate failed; see {output_dir / 'full_ua_mstcn_smoke_report.md'}")


if __name__ == "__main__":
    main()
