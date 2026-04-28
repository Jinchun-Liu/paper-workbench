#!/usr/bin/env python3
"""Full UA-MSTCN broad-cohort batch-size calibration.

This is a calibration slice, not a broad full-model run. It samples
train/validation-prefix windows from all broad services, compares small batch
sizes, records runtime/VRAM, and leaves the held-out test split untouched.
"""

from __future__ import annotations

import argparse
import csv
import ctypes
import hashlib
import json
import math
import os
import platform
import random
import shutil
import sys
import time
from pathlib import Path

import numpy as np
import psutil
import torch
import yaml
from torch.utils.data import DataLoader, TensorDataset

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from models.full_ua_mstcn import FullUAMSTCN, pinball_loss


RUN_ID = "full_ua_mstcn_broad_calibration_20260428"


def resolve_path(path: Path, repo_root: Path) -> Path:
    if path.is_absolute():
        return path
    if path.parts and path.parts[0] == repo_root.name:
        return repo_root.parent.joinpath(path)
    return repo_root.joinpath(path)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def windows_memory_status() -> tuple[int | None, int | None]:
    if os.name != "nt":
        return None, None

    class MemoryStatusEx(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    status = MemoryStatusEx()
    status.dwLength = ctypes.sizeof(MemoryStatusEx)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):  # type: ignore[attr-defined]
        return None, None
    return int(status.ullTotalPhys), int(status.ullAvailPhys)


def resource_snapshot(repo_root: Path) -> dict:
    total_disk, used_disk, free_disk = shutil.disk_usage(repo_root.anchor or repo_root)
    total_mem, free_mem = windows_memory_status()
    return {
        "os": platform.platform(),
        "python": sys.version,
        "torch": torch.__version__,
        "cuda_available": bool(torch.cuda.is_available()),
        "cuda_device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
        "logical_cpu_count": os.cpu_count() or "",
        "process_memory_rss_bytes": int(psutil.Process(os.getpid()).memory_info().rss),
        "total_memory_bytes": total_mem or "",
        "free_memory_bytes": free_mem or "",
        "workspace_drive": repo_root.anchor,
        "drive_total_bytes": total_disk,
        "drive_used_bytes": used_disk,
        "drive_free_bytes": free_disk,
    }


def read_service_series(service_csv: Path) -> dict[str, np.ndarray]:
    rows: dict[str, list[tuple[int, float]]] = {}
    with service_csv.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            app_du = row["app_du"]
            rows.setdefault(app_du, []).append((int(row["minute_index"]), float(row["service_cpu_used_cores_proxy"])))
    series = {}
    for app_du, values in rows.items():
        values.sort(key=lambda item: item[0])
        series[app_du] = np.asarray([value for _, value in values], dtype=np.float32)
    return dict(sorted(series.items()))


def split_bounds(length: int, train_ratio: float, valid_ratio: float) -> tuple[int, int]:
    train_end = int(length * train_ratio)
    valid_end = int(length * (train_ratio + valid_ratio))
    if not (0 < train_end < valid_end < length):
        raise ValueError(f"Invalid split bounds for length={length}")
    return train_end, valid_end


def sample_origins(segment_start: int, segment_end: int, context_window: int, max_horizon: int, limit: int) -> np.ndarray:
    start = segment_start + context_window
    stop = segment_end - max_horizon
    if stop < start:
        return np.asarray([], dtype=np.int64)
    count = stop - start + 1
    if count <= limit:
        return np.arange(start, stop + 1, dtype=np.int64)
    return np.linspace(start, stop, num=limit, dtype=np.int64)


def build_sample_windows(
    values: np.ndarray,
    *,
    entity_id: int,
    context_window: int,
    horizons: tuple[int, ...],
    train_end: int,
    valid_end: int,
    train_limit: int,
    valid_limit: int,
) -> tuple[tuple[np.ndarray, np.ndarray, np.ndarray], tuple[np.ndarray, np.ndarray, np.ndarray], dict]:
    train_values = values[:train_end].astype(np.float64)
    mean = float(np.mean(train_values))
    std = max(float(np.std(train_values, ddof=1)), 1e-6)
    normalized = ((values - mean) / std).astype(np.float32)
    max_horizon = max(horizons)

    def make_parts(origins: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        features = np.zeros((len(origins), context_window, 4), dtype=np.float32)
        targets = np.zeros((len(origins), len(horizons)), dtype=np.float32)
        entity_ids = np.full((len(origins),), entity_id, dtype=np.int64)
        for row_idx, origin in enumerate(origins):
            history = normalized[origin - context_window : origin]
            for offset, demand_value in enumerate(history):
                minute_index = origin - context_window + offset
                angle = 2.0 * math.pi * (minute_index % 1440) / 1440.0
                features[row_idx, offset, :] = [demand_value, 1.0, math.sin(angle), math.cos(angle)]
            targets[row_idx, :] = [normalized[origin + horizon - 1] for horizon in horizons]
        return features, targets, entity_ids

    train_origins = sample_origins(0, train_end, context_window, max_horizon, train_limit)
    valid_origins = sample_origins(train_end, valid_end, context_window, max_horizon, valid_limit)
    profile = {
        "entity_id": entity_id,
        "row_count": int(len(values)),
        "train_end": int(train_end),
        "valid_end": int(valid_end),
        "train_sample_windows": int(len(train_origins)),
        "valid_sample_windows": int(len(valid_origins)),
        "normalization_source": "train prefix only",
        "selection_rule": "all 139 broad services; train/validation prefix sampling only; test split untouched",
    }
    return make_parts(train_origins), make_parts(valid_origins), profile


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"No rows to write for {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def train_probe(
    *,
    train_x: torch.Tensor,
    train_y: torch.Tensor,
    train_eids: torch.Tensor,
    valid_x: torch.Tensor,
    valid_y: torch.Tensor,
    valid_eids: torch.Tensor,
    batch_size: int,
    hidden_width: int,
    horizons: tuple[int, ...],
    num_entities: int,
    epochs: int,
    max_train_batches: int,
    device: torch.device,
) -> dict:
    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()
    model = FullUAMSTCN(
        input_channels=train_x.shape[-1],
        horizons=horizons,
        hidden_width=hidden_width,
        dilations=(1, 2, 4, 8, 16),
        dropout=0.10,
        num_entities=num_entities,
        entity_embedding_dim=8,
    ).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    loader = DataLoader(
        TensorDataset(train_x, train_y, train_eids),
        batch_size=batch_size,
        shuffle=True,
        drop_last=False,
    )
    started = time.perf_counter()
    train_losses: list[float] = []
    seen_windows = 0
    seen_batches = 0
    for _epoch in range(epochs):
        model.train()
        batch_losses: list[float] = []
        for batch_index, (batch_x, batch_y, batch_eids) in enumerate(loader):
            if batch_index >= max_train_batches:
                break
            optimizer.zero_grad(set_to_none=True)
            predictions = model(batch_x.to(device), batch_eids.to(device))
            loss = pinball_loss(predictions, batch_y.to(device))
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            batch_losses.append(float(loss.detach().cpu()))
            seen_windows += int(len(batch_x))
            seen_batches += 1
        train_losses.append(float(np.mean(batch_losses)))
    train_runtime = time.perf_counter() - started
    model.eval()
    valid_started = time.perf_counter()
    with torch.no_grad():
        valid_predictions = model(valid_x.to(device), valid_eids.to(device))
        valid_loss = pinball_loss(valid_predictions, valid_y.to(device))
    valid_runtime = time.perf_counter() - valid_started
    throughput = seen_windows / max(train_runtime, 1e-9)
    return {
        "run_id": RUN_ID,
        "batch_size": batch_size,
        "hidden_width": hidden_width,
        "epochs": epochs,
        "max_train_batches_per_epoch": max_train_batches,
        "seen_train_batches": seen_batches,
        "seen_train_windows": seen_windows,
        "train_runtime_seconds": train_runtime,
        "validation_runtime_seconds": valid_runtime,
        "train_windows_per_second": throughput,
        "first_train_loss": train_losses[0],
        "last_train_loss": train_losses[-1],
        "validation_loss": float(valid_loss.detach().cpu()),
        "peak_cuda_memory_bytes": int(torch.cuda.max_memory_allocated()) if torch.cuda.is_available() else 0,
        "process_memory_rss_bytes": int(psutil.Process(os.getpid()).memory_info().rss),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("experiments/configs/default_v2018.yaml"))
    parser.add_argument("--service-csv", type=Path, default=Path("data/processed/service_cohort_broad_v2018.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("experiments/results/full_ua_mstcn_broad_calibration"))
    parser.add_argument("--batch-sizes", nargs="+", type=int, default=[512, 1024])
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--max-train-batches", type=int, default=120)
    parser.add_argument("--train-windows-per-service", type=int, default=512)
    parser.add_argument("--valid-windows-per-service", type=int, default=128)
    parser.add_argument("--hidden-width", type=int, default=64)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    output_dir = resolve_path(args.output_dir, repo_root)
    if output_dir.exists():
        raise SystemExit(f"Refusing to overwrite existing output directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=False)
    config_path = resolve_path(args.config, repo_root)
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    service_csv = resolve_path(args.service_csv, repo_root)
    metrics_path = resolve_path(Path(config["output"]["metrics_csv"]), repo_root)
    metrics_hash_before = sha256_file(metrics_path)

    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(args.seed)

    horizons = tuple(int(value) for value in config["forecast"]["horizons"])
    context_window = int(config["forecast"]["context_window"])
    train_ratio = float(config["forecast"]["train_ratio"])
    valid_ratio = float(config["forecast"]["valid_ratio"])
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    census_before = resource_snapshot(repo_root)

    service_series = read_service_series(service_csv)
    profile_rows: list[dict] = []
    train_parts = []
    valid_parts = []
    for entity_id, (app_du, values) in enumerate(service_series.items()):
        train_end, valid_end = split_bounds(len(values), train_ratio, valid_ratio)
        train_part, valid_part, profile = build_sample_windows(
            values,
            entity_id=entity_id,
            context_window=context_window,
            horizons=horizons,
            train_end=train_end,
            valid_end=valid_end,
            train_limit=int(args.train_windows_per_service),
            valid_limit=int(args.valid_windows_per_service),
        )
        profile["app_du"] = app_du
        profile_rows.append(profile)
        train_parts.append(train_part)
        valid_parts.append(valid_part)
    train_x = torch.tensor(np.concatenate([part[0] for part in train_parts], axis=0), dtype=torch.float32)
    train_y = torch.tensor(np.concatenate([part[1] for part in train_parts], axis=0), dtype=torch.float32)
    train_eids = torch.tensor(np.concatenate([part[2] for part in train_parts], axis=0), dtype=torch.long)
    valid_x = torch.tensor(np.concatenate([part[0] for part in valid_parts], axis=0), dtype=torch.float32)
    valid_y = torch.tensor(np.concatenate([part[1] for part in valid_parts], axis=0), dtype=torch.float32)
    valid_eids = torch.tensor(np.concatenate([part[2] for part in valid_parts], axis=0), dtype=torch.long)

    calibration_rows = []
    for batch_size in args.batch_sizes:
        calibration_rows.append(
            train_probe(
                train_x=train_x,
                train_y=train_y,
                train_eids=train_eids,
                valid_x=valid_x,
                valid_y=valid_y,
                valid_eids=valid_eids,
                batch_size=int(batch_size),
                hidden_width=int(args.hidden_width),
                horizons=horizons,
                num_entities=len(service_series),
                epochs=int(args.epochs),
                max_train_batches=int(args.max_train_batches),
                device=device,
            )
        )
    write_csv(output_dir / "full_ua_mstcn_broad_calibration_manifest.csv", profile_rows)
    write_csv(output_dir / "full_ua_mstcn_broad_calibration_results.csv", calibration_rows)

    viable = [row for row in calibration_rows if int(row["peak_cuda_memory_bytes"]) < 12 * 1024**3]
    recommended = max(viable, key=lambda row: float(row["train_windows_per_second"])) if viable else calibration_rows[0]
    metrics_hash_after = sha256_file(metrics_path)
    gate_failures = []
    if len(profile_rows) != 139:
        gate_failures.append(f"manifest has {len(profile_rows)} services, expected 139")
    if metrics_hash_before != metrics_hash_after:
        gate_failures.append("central metrics.csv changed")
    if (repo_root / "experiments" / "results" / "full_ua_mstcn_broad").exists():
        gate_failures.append("unexpected full_ua_mstcn_broad directory exists")
    if not all(math.isfinite(float(row["validation_loss"])) for row in calibration_rows):
        gate_failures.append("non-finite validation loss")
    if not viable:
        gate_failures.append("no batch size stayed below 12GB peak CUDA memory")

    status = {
        "run_id": RUN_ID,
        "status": "pass" if not gate_failures else "fail",
        "scope": "broad calibration slice only; no held-out test evaluation and no full broad run",
        "output_dir": str(output_dir),
        "service_count": len(profile_rows),
        "train_windows": int(len(train_x)),
        "validation_windows": int(len(valid_x)),
        "test_split_use": "untouched; no test windows are generated in this calibration",
        "recommended_batch_size": int(recommended["batch_size"]),
        "metrics_csv_hash_before": metrics_hash_before,
        "metrics_csv_hash_after": metrics_hash_after,
        "resource_before": census_before,
        "resource_after": resource_snapshot(repo_root),
        "gate_failures": gate_failures,
        "metrics_csv_updated": False,
        "full_broad_run_executed": False,
    }
    (output_dir / "full_ua_mstcn_broad_calibration_status.json").write_text(
        json.dumps(status, indent=2), encoding="utf-8"
    )

    report_lines = [
        "# Full UA-MSTCN Broad Calibration Report",
        "",
        f"- run_id: `{RUN_ID}`",
        f"- status: `{status['status']}`",
        "- scope: broad calibration slice only; no held-out test evaluation and no full broad run.",
        f"- service_count: `{len(profile_rows)}`",
        f"- train_windows: `{len(train_x)}`",
        f"- validation_windows: `{len(valid_x)}`",
        f"- recommended_batch_size: `{status['recommended_batch_size']}`",
        f"- metrics_csv_hash_before: `{metrics_hash_before}`",
        f"- metrics_csv_hash_after: `{metrics_hash_after}`",
        "",
        "## Gate Result",
        "",
    ]
    if gate_failures:
        report_lines.extend(f"- FAIL: {failure}" for failure in gate_failures)
    else:
        report_lines.append("- PASS: broad calibration gate passed.")
    report_lines.extend(["", "## Batch Results", "", "```csv", ",".join(calibration_rows[0].keys())])
    for row in calibration_rows:
        report_lines.append(",".join(str(row[key]) for key in calibration_rows[0].keys()))
    report_lines.extend(["```", ""])
    (output_dir / "full_ua_mstcn_broad_calibration_report.md").write_text(
        "\n".join(report_lines), encoding="utf-8"
    )
    if gate_failures:
        raise SystemExit(
            f"Full UA-MSTCN broad calibration gate failed; see {output_dir / 'full_ua_mstcn_broad_calibration_report.md'}"
        )


if __name__ == "__main__":
    main()
