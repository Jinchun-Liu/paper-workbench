#!/usr/bin/env python3
"""Stage-2 pilot for the full PyTorch UA-MSTCN backbone.

This script runs the next scale-ladder step after the Stage-1 smoke:

* aggregate full-series forecasting and policy evaluation;
* a fixed five-service pilot with a small global entity-conditioned model.

The script is deliberately isolated from central ``metrics.csv`` and from the
existing ``UA-MSTCN-Lite`` surrogate. Validation is used for monitoring and P90
calibration only; the test split is evaluation-only.
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
from typing import Iterable

import numpy as np
import psutil
import torch
import yaml
from torch.utils.data import DataLoader, TensorDataset

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from models.full_ua_mstcn import FullUAMSTCN, pinball_loss
from policies.autoscaling_simulator import run_lagged_target_tracking, run_predictive, run_reactive


RUN_ID = "full_ua_mstcn_pilot_20260428"
MODEL_NAME = "full_ua_mstcn_pilot"
SERVICE_ROLES = {
    "app_2557": "pilot_low_load_low_burst",
    "app_7264": "pilot_high_load_low_burst",
    "app_1675": "pilot_low_load_high_burst",
    "app_3665": "pilot_high_load_high_burst",
    "app_521": "pilot_median_reference",
}


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


def read_aggregate_series(series_csv: Path, column: str) -> np.ndarray:
    values: list[float] = []
    with series_csv.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            values.append(float(row[column]))
    if not values:
        raise ValueError(f"No aggregate rows read from {series_csv}")
    return np.asarray(values, dtype=np.float32)


def read_service_series(service_csv: Path, app_dus: Iterable[str]) -> dict[str, np.ndarray]:
    selected = set(app_dus)
    rows: dict[str, list[tuple[int, float]]] = {app_du: [] for app_du in selected}
    with service_csv.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            app_du = row["app_du"]
            if app_du in selected:
                rows[app_du].append((int(row["minute_index"]), float(row["service_cpu_used_cores_proxy"])))
    series = {}
    for app_du, app_rows in rows.items():
        if not app_rows:
            raise ValueError(f"No service rows read for {app_du}")
        app_rows.sort(key=lambda item: item[0])
        series[app_du] = np.asarray([value for _, value in app_rows], dtype=np.float32)
    return series


def read_service_summary(summary_csv: Path) -> dict[str, dict[str, float]]:
    summary: dict[str, dict[str, float]] = {}
    with summary_csv.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            summary[row["app_du"]] = {
                key: float(value)
                for key, value in row.items()
                if key != "app_du" and value not in ("", None)
            }
    return summary


def split_bounds(length: int, train_ratio: float, valid_ratio: float) -> tuple[int, int]:
    train_end = int(length * train_ratio)
    valid_end = int(length * (train_ratio + valid_ratio))
    if not (0 < train_end < valid_end < length):
        raise ValueError(f"Invalid split bounds for length={length}")
    return train_end, valid_end


def prefix_descriptors(values: np.ndarray, train_end: int, valid_end: int) -> dict:
    prefix = values[:valid_end]
    load_mean = float(np.mean(prefix))
    burst_cv = float(np.std(prefix, ddof=1) / max(load_mean, 1e-9)) if len(prefix) > 1 else 0.0
    peak_to_mean = float(np.max(prefix) / max(load_mean, 1e-9)) if len(prefix) else 0.0
    return {
        "prefix_rows": int(len(prefix)),
        "train_split_end": int(train_end),
        "train_valid_split_end": int(valid_end),
        "load_mean_prefix": load_mean,
        "burst_cv_prefix": burst_cv,
        "peak_to_mean_prefix": peak_to_mean,
    }


def normalize_with_train(values: np.ndarray, train_end: int) -> tuple[np.ndarray, float, float]:
    train_values = values[:train_end].astype(np.float64)
    mean = float(np.mean(train_values))
    std = float(np.std(train_values, ddof=1))
    std = max(std, 1e-6)
    return ((values - mean) / std).astype(np.float32), mean, std


def build_segment_windows(
    normalized: np.ndarray,
    raw_values: np.ndarray,
    *,
    context_window: int,
    horizons: tuple[int, ...],
    segment_start: int,
    segment_end: int,
    entity_id: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[dict]]:
    max_horizon = max(horizons)
    features: list[list[list[float]]] = []
    targets: list[list[float]] = []
    entity_ids: list[int] = []
    meta_rows: list[dict] = []
    start_origin = segment_start + context_window
    stop_origin = segment_end - max_horizon + 1
    for origin in range(start_origin, stop_origin):
        history = normalized[origin - context_window : origin]
        if len(history) != context_window:
            continue
        feature_rows: list[list[float]] = []
        for minute_index, demand_value in enumerate(history, start=origin - context_window):
            angle = 2.0 * math.pi * (minute_index % 1440) / 1440.0
            feature_rows.append([float(demand_value), 1.0, math.sin(angle), math.cos(angle)])
        features.append(feature_rows)
        targets.append([float(normalized[origin + horizon - 1]) for horizon in horizons])
        entity_ids.append(entity_id)
        meta_rows.append(
            {
                "origin_index": origin,
                "target_indices": [origin + horizon - 1 for horizon in horizons],
                "raw_targets": [float(raw_values[origin + horizon - 1]) for horizon in horizons],
            }
        )
    if not features:
        raise ValueError("No windows were created for segment")
    return (
        np.asarray(features, dtype=np.float32),
        np.asarray(targets, dtype=np.float32),
        np.asarray(entity_ids, dtype=np.int64),
        meta_rows,
    )


def concatenate_parts(parts: list[tuple[np.ndarray, np.ndarray, np.ndarray]]) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    features = np.concatenate([part[0] for part in parts], axis=0)
    targets = np.concatenate([part[1] for part in parts], axis=0)
    entity_ids = np.concatenate([part[2] for part in parts], axis=0)
    return (
        torch.tensor(features, dtype=torch.float32),
        torch.tensor(targets, dtype=torch.float32),
        torch.tensor(entity_ids, dtype=torch.long),
    )


def train_model(
    *,
    model: FullUAMSTCN,
    train_x: torch.Tensor,
    train_y: torch.Tensor,
    train_entity_ids: torch.Tensor,
    valid_x: torch.Tensor,
    valid_y: torch.Tensor,
    valid_entity_ids: torch.Tensor,
    use_entity_ids: bool,
    batch_size: int,
    max_epochs: int,
    patience: int,
    device: torch.device,
) -> tuple[list[float], list[float], int, float]:
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    loader = DataLoader(
        TensorDataset(train_x, train_y, train_entity_ids),
        batch_size=batch_size,
        shuffle=True,
        drop_last=False,
    )
    best_valid = float("inf")
    best_state: dict[str, torch.Tensor] | None = None
    stale_epochs = 0
    train_losses: list[float] = []
    valid_losses: list[float] = []
    started = time.perf_counter()
    for _epoch in range(max_epochs):
        model.train()
        batch_losses: list[float] = []
        for batch_x, batch_y, batch_eids in loader:
            optimizer.zero_grad(set_to_none=True)
            if use_entity_ids:
                predictions = model(batch_x.to(device), batch_eids.to(device))
            else:
                predictions = model(batch_x.to(device))
            loss = pinball_loss(predictions, batch_y.to(device))
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            batch_losses.append(float(loss.detach().cpu()))
        train_losses.append(float(np.mean(batch_losses)))
        model.eval()
        valid_loader = DataLoader(
            TensorDataset(valid_x, valid_y, valid_entity_ids),
            batch_size=batch_size,
            shuffle=False,
            drop_last=False,
        )
        valid_loss_total = 0.0
        valid_count = 0
        with torch.no_grad():
            for valid_batch_x, valid_batch_y, valid_batch_eids in valid_loader:
                if use_entity_ids:
                    valid_predictions = model(valid_batch_x.to(device), valid_batch_eids.to(device))
                else:
                    valid_predictions = model(valid_batch_x.to(device))
                batch_loss = pinball_loss(valid_predictions, valid_batch_y.to(device))
                valid_loss_total += float(batch_loss.detach().cpu()) * int(len(valid_batch_x))
                valid_count += int(len(valid_batch_x))
        valid_value = valid_loss_total / max(valid_count, 1)
        valid_losses.append(valid_value)
        if valid_value < best_valid - 1e-4:
            best_valid = valid_value
            best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
            stale_epochs = 0
        else:
            stale_epochs += 1
            if stale_epochs >= patience:
                break
    if best_state is not None:
        model.load_state_dict(best_state)
    runtime = time.perf_counter() - started
    return train_losses, valid_losses, len(train_losses), runtime


def predict_numpy(
    model: FullUAMSTCN,
    features: torch.Tensor,
    entity_ids: torch.Tensor,
    *,
    use_entity_ids: bool,
    device: torch.device,
    batch_size: int,
) -> np.ndarray:
    model.eval()
    outputs: list[np.ndarray] = []
    loader = DataLoader(TensorDataset(features, entity_ids), batch_size=batch_size, shuffle=False)
    with torch.no_grad():
        for batch_x, batch_eids in loader:
            if use_entity_ids:
                predictions = model(batch_x.to(device), batch_eids.to(device))
            else:
                predictions = model(batch_x.to(device))
            outputs.append(predictions.detach().cpu().numpy())
    return np.concatenate(outputs, axis=0)


def pinball(actual: np.ndarray, predicted: np.ndarray, quantile: float) -> float:
    error = actual - predicted
    return float(np.mean(np.maximum((quantile - 1.0) * error, quantile * error)))


def finite_row_values(row: dict) -> bool:
    for value in row.values():
        if isinstance(value, float) and not math.isfinite(value):
            return False
    return True


def evaluate_entity_predictions(
    *,
    scope: str,
    entity_name: str,
    selection_role: str,
    split_name: str,
    horizons: tuple[int, ...],
    raw_targets: np.ndarray,
    predictions_norm: np.ndarray,
    mean: float,
    std: float,
    calibration_margins: dict[int, float],
    meta_rows: list[dict],
) -> tuple[list[dict], list[dict], dict[int, tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]]:
    prediction_rows: list[dict] = []
    metric_rows: list[dict] = []
    arrays_by_horizon: dict[int, tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]] = {}
    p50_raw_all = predictions_norm[:, :, 0] * std + mean
    p90_raw_all = predictions_norm[:, :, 1] * std + mean
    for horizon_index, horizon in enumerate(horizons):
        y_true = raw_targets[:, horizon_index]
        p50 = p50_raw_all[:, horizon_index]
        p90_raw = p90_raw_all[:, horizon_index]
        p90_calibrated = p90_raw + calibration_margins[horizon]
        raw_crossing = p90_raw < p50
        calibrated_crossing = p90_calibrated < p50
        metric = {
            "run_id": RUN_ID,
            "scope": scope,
            "entity": entity_name,
            "selection_role": selection_role,
            "split": split_name,
            "model_name": MODEL_NAME,
            "horizon": horizon,
            "n_predictions": int(len(y_true)),
            "mae": float(np.mean(np.abs(y_true - p50))),
            "rmse": float(np.sqrt(np.mean((y_true - p50) ** 2))),
            "mape": float(np.mean(np.abs(y_true - p50) / np.maximum(np.abs(y_true), 1e-6))),
            "p50_pinball": pinball(y_true, p50, 0.5),
            "p90_raw_pinball": pinball(y_true, p90_raw, 0.9),
            "p90_calibrated_pinball": pinball(y_true, p90_calibrated, 0.9),
            "p50_coverage": float(np.mean(y_true <= p50)),
            "p90_raw_coverage": float(np.mean(y_true <= p90_raw)),
            "p90_calibrated_coverage": float(np.mean(y_true <= p90_calibrated)),
            "raw_interval_width": float(np.mean(p90_raw - p50)),
            "calibrated_interval_width": float(np.mean(p90_calibrated - p50)),
            "raw_crossing_count": int(np.sum(raw_crossing)),
            "raw_crossing_rate": float(np.mean(raw_crossing)),
            "calibrated_crossing_count": int(np.sum(calibrated_crossing)),
            "calibrated_crossing_rate": float(np.mean(calibrated_crossing)),
            "calibration_margin": float(calibration_margins[horizon]),
        }
        metric["status"] = "pass" if finite_row_values(metric) and len(y_true) > 0 and int(np.sum(calibrated_crossing)) == 0 else "fail"
        metric_rows.append(metric)
        arrays_by_horizon[horizon] = (y_true, p50, p90_raw, p90_calibrated)
        for row_index, meta in enumerate(meta_rows):
            prediction_rows.append(
                {
                    "run_id": RUN_ID,
                    "scope": scope,
                    "entity": entity_name,
                    "selection_role": selection_role,
                    "split": split_name,
                    "horizon": horizon,
                    "origin_index": int(meta["origin_index"]),
                    "target_index": int(meta["target_indices"][horizon_index]),
                    "y_true": float(y_true[row_index]),
                    "p50": float(p50[row_index]),
                    "p90_raw": float(p90_raw[row_index]),
                    "p90_calibrated": float(p90_calibrated[row_index]),
                    "raw_crossing": bool(raw_crossing[row_index]),
                    "calibrated_crossing": bool(calibrated_crossing[row_index]),
                }
            )
    return metric_rows, prediction_rows, arrays_by_horizon


def service_request_cores(summary_row: dict[str, float]) -> tuple[float, str, bool]:
    median_value = float(summary_row["median_container_request_cores"])
    if median_value > 0.0:
        return max(median_value, 0.1), "median_container_request_cores", False
    mean_value = float(summary_row["mean_container_request_cores"])
    return max(mean_value, 0.1), "mean_container_request_cores", True


def summarize_policy(actual_load: np.ndarray, capacity: np.ndarray, actions: int) -> dict:
    slack = capacity - actual_load
    under = np.clip(-slack, 0.0, None)
    over = np.clip(slack, 0.0, None)
    return {
        "sla_violation": float(np.mean(actual_load > capacity)),
        "over_provisioning": float(np.mean(over)),
        "under_provisioning": float(np.mean(under)),
        "scaling_actions": int(actions),
        "average_capacity": float(np.mean(capacity)),
    }


def add_policy_rows(
    *,
    scope: str,
    entity: str,
    selection_role: str,
    policy_config: dict,
    arrays_by_horizon: dict[int, tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]],
    request_cores: float,
    request_source: str,
    request_fallback_used: bool,
    is_service: bool,
    policy_rows: list[dict],
    policy_series_rows: list[dict],
) -> None:
    policy_horizon = 5 if 5 in arrays_by_horizon else sorted(arrays_by_horizon)[0]
    y_true, p50, _p90_raw, p90_calibrated = arrays_by_horizon[policy_horizon]
    headroom = float(policy_config["headroom_ratio"])
    margin = float(policy_config["scale_out_quantile_margin"])
    if is_service:
        actual_load = y_true / request_cores * (1.0 + headroom)
        forecast_p50 = p50 / request_cores * (1.0 + headroom)
        forecast_p90 = p90_calibrated / request_cores * (1.0 + headroom) * (1.0 + margin)
        reactive_actual = y_true / request_cores
        min_capacity = 1.0
        max_step_change = 1.0
    else:
        actual_norm = y_true / 100.0
        p50_norm = p50 / 100.0
        p90_norm = p90_calibrated / 100.0
        min_capacity = float(policy_config["min_capacity"])
        max_step_change = float(policy_config["max_step_change"])
        actual_load = np.maximum(actual_norm * (1.0 + headroom), min_capacity)
        forecast_p50 = np.maximum(p50_norm * (1.0 + headroom), min_capacity)
        forecast_p90 = np.maximum(p90_norm * (1.0 + headroom), min_capacity) * (1.0 + margin)
        reactive_actual = actual_load

    reactive_capacity, reactive_metrics = run_reactive(
        actual_load=reactive_actual,
        upper_threshold=float(policy_config["reactive_upper_threshold"]),
        lower_threshold=float(policy_config["reactive_lower_threshold"]),
        min_capacity=min_capacity,
        max_step_change=max_step_change,
    )
    lagged_capacity, lagged_metrics = run_lagged_target_tracking(
        actual_load=actual_load,
        min_capacity=min_capacity,
        max_step_change=max_step_change,
    )
    predictive_capacity, predictive_metrics = run_predictive(
        actual_load=actual_load,
        forecast_p50=forecast_p50,
        forecast_p90=forecast_p90,
        min_capacity=min_capacity,
        cooldown_steps=int(policy_config["cooldown_steps"]),
        max_step_change=max_step_change,
        scale_in_safety_margin=float(policy_config["scale_in_safety_margin"]),
    )
    metric_objects = [
        ("reactive", reactive_metrics),
        ("lagged_tracking", lagged_metrics),
        ("full_ua_mstcn_predictive", predictive_metrics),
    ]
    for policy_name, metrics in metric_objects:
        policy_rows.append(
            {
                "run_id": RUN_ID,
                "scope": scope,
                "entity": entity,
                "selection_role": selection_role,
                "policy_name": policy_name,
                "model_name": MODEL_NAME if policy_name == "full_ua_mstcn_predictive" else "n/a",
                "horizon": policy_horizon,
                "request_cores_source": request_source,
                "request_cores_used": float(request_cores),
                "request_fallback_used": bool(request_fallback_used),
                "sla_violation": float(metrics.sla_violation),
                "over_provisioning": float(metrics.over_provisioning),
                "under_provisioning": float(metrics.under_provisioning),
                "scaling_actions": int(metrics.scaling_actions),
                "average_capacity": float(metrics.average_capacity),
            }
        )
    for idx in range(len(actual_load)):
        policy_series_rows.append(
            {
                "run_id": RUN_ID,
                "scope": scope,
                "entity": entity,
                "selection_role": selection_role,
                "policy_horizon": policy_horizon,
                "aligned_test_index": idx,
                "actual_load": float(actual_load[idx]),
                "forecast_p50": float(forecast_p50[idx]),
                "forecast_p90": float(forecast_p90[idx]),
                "reactive_capacity": float(reactive_capacity[idx]),
                "lagged_capacity": float(lagged_capacity[idx]),
                "predictive_capacity": float(predictive_capacity[idx]),
            }
        )


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"No rows to write for {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def rows_numeric_finite(rows: list[dict]) -> bool:
    return all(finite_row_values(row) for row in rows)


def run_scope(
    *,
    scope: str,
    series_by_entity: dict[str, np.ndarray],
    selection_roles: dict[str, str],
    context_window: int,
    horizons: tuple[int, ...],
    train_ratio: float,
    valid_ratio: float,
    policy_config: dict,
    service_summary: dict[str, dict[str, float]] | None,
    hidden_width: int,
    dilations: tuple[int, ...],
    batch_size: int,
    max_epochs: int,
    patience: int,
    device: torch.device,
) -> tuple[list[dict], list[dict], list[dict], list[dict], list[dict], list[dict], dict]:
    use_entity_ids = len(series_by_entity) > 1
    service_scope = scope in {"service_pilot", "service_broad"}
    entity_names = list(series_by_entity)
    entity_to_id = {entity: idx for idx, entity in enumerate(entity_names)}
    train_parts = []
    valid_parts = []
    meta_by_entity_split: dict[tuple[str, str], list[dict]] = {}
    raw_targets_by_entity_split: dict[tuple[str, str], np.ndarray] = {}
    norm_stats: dict[str, tuple[float, float]] = {}
    profile_rows: list[dict] = []
    calibration_rows: list[dict] = []
    forecast_rows: list[dict] = []
    prediction_rows: list[dict] = []
    policy_rows: list[dict] = []
    policy_series_rows: list[dict] = []
    resource_start = time.perf_counter()
    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()

    for entity, values in series_by_entity.items():
        train_end, valid_end = split_bounds(len(values), train_ratio, valid_ratio)
        normalized, mean, std = normalize_with_train(values, train_end)
        norm_stats[entity] = (mean, std)
        role = selection_roles.get(entity, "aggregate_full" if scope == "aggregate" else "service_pilot")
        selection_rule = (
            "all 139 broad services; descriptors use train+validation prefix only"
            if scope == "service_broad"
            else "fixed Stage-2 Full UA-MSTCN pilot entity; descriptors use train+validation prefix only"
        )
        profile = {
            "run_id": RUN_ID,
            "scope": scope,
            "entity": entity,
            "selection_role": role,
            "row_count": int(len(values)),
            "selection_rule": selection_rule,
            "normalization_source": "train prefix only",
        }
        profile.update(prefix_descriptors(values, train_end, valid_end))
        if service_summary is not None and entity in service_summary:
            request_cores, request_source, request_fallback = service_request_cores(service_summary[entity])
            profile.update(
                {
                    "request_cores_source": request_source,
                    "request_cores_used": request_cores,
                    "request_fallback_used": request_fallback,
                }
            )
        else:
            profile.update(
                {
                    "request_cores_source": "n/a",
                    "request_cores_used": 1.0,
                    "request_fallback_used": False,
                }
            )
        profile_rows.append(profile)
        entity_id = entity_to_id[entity]
        train_part = build_segment_windows(
            normalized,
            values,
            context_window=context_window,
            horizons=horizons,
            segment_start=0,
            segment_end=train_end,
            entity_id=entity_id,
        )
        valid_part = build_segment_windows(
            normalized,
            values,
            context_window=context_window,
            horizons=horizons,
            segment_start=train_end,
            segment_end=valid_end,
            entity_id=entity_id,
        )
        test_part = build_segment_windows(
            normalized,
            values,
            context_window=context_window,
            horizons=horizons,
            segment_start=valid_end,
            segment_end=len(values),
            entity_id=entity_id,
        )
        train_parts.append(train_part[:3])
        valid_parts.append(valid_part[:3])
        for split_name, part in [("validation", valid_part), ("test", test_part)]:
            raw_targets_by_entity_split[(entity, split_name)] = np.asarray(
                [meta["raw_targets"] for meta in part[3]], dtype=np.float32
            )
            meta_by_entity_split[(entity, split_name)] = part[3]

    train_x, train_y, train_eids = concatenate_parts(train_parts)
    valid_x, valid_y, valid_eids = concatenate_parts(valid_parts)
    model = FullUAMSTCN(
        input_channels=train_x.shape[-1],
        horizons=horizons,
        hidden_width=hidden_width,
        dilations=dilations,
        dropout=0.10,
        num_entities=len(entity_names) if use_entity_ids else None,
        entity_embedding_dim=8 if use_entity_ids else 0,
    ).to(device)
    train_losses, valid_losses, epochs_completed, train_runtime = train_model(
        model=model,
        train_x=train_x,
        train_y=train_y,
        train_entity_ids=train_eids,
        valid_x=valid_x,
        valid_y=valid_y,
        valid_entity_ids=valid_eids,
        use_entity_ids=use_entity_ids,
        batch_size=batch_size,
        max_epochs=max_epochs,
        patience=patience,
        device=device,
    )

    arrays_for_policy: dict[str, dict[int, tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]] = {}
    for entity in entity_names:
        role = selection_roles.get(entity, "aggregate_full" if scope == "aggregate" else "service_pilot")
        mean, std = norm_stats[entity]
        entity_id = entity_to_id[entity]
        values = series_by_entity[entity]
        train_end, valid_end = split_bounds(len(values), train_ratio, valid_ratio)
        split_parts = {}
        for split_name, start, end in [
            ("validation", train_end, valid_end),
            ("test", valid_end, len(values)),
        ]:
            x_arr, _y_arr, eids_arr, meta_rows = build_segment_windows(
                (values - mean) / std,
                values,
                context_window=context_window,
                horizons=horizons,
                segment_start=start,
                segment_end=end,
                entity_id=entity_id,
            )
            split_parts[split_name] = (
                torch.tensor(x_arr, dtype=torch.float32),
                torch.tensor(eids_arr, dtype=torch.long),
                np.asarray([meta["raw_targets"] for meta in meta_rows], dtype=np.float32),
                meta_rows,
            )
        valid_predictions = predict_numpy(
            model,
            split_parts["validation"][0],
            split_parts["validation"][1],
            use_entity_ids=use_entity_ids,
            device=device,
            batch_size=batch_size,
        )
        p90_valid_raw = valid_predictions[:, :, 1] * std + mean
        valid_targets = split_parts["validation"][2]
        calibration_margins: dict[int, float] = {}
        for horizon_index, horizon in enumerate(horizons):
            margin = float(np.quantile(np.maximum(valid_targets[:, horizon_index] - p90_valid_raw[:, horizon_index], 0.0), 0.90))
            calibration_margins[horizon] = margin
            calibration_rows.append(
                {
                    "run_id": RUN_ID,
                    "scope": scope,
                    "entity": entity,
                    "selection_role": role,
                    "horizon": horizon,
                    "calibration_split": "validation",
                    "calibration_quantile": 0.90,
                    "p90_additive_margin": margin,
                }
            )
        for split_name in ["validation", "test"]:
            features, eids, raw_targets, meta_rows = split_parts[split_name]
            predictions = valid_predictions if split_name == "validation" else predict_numpy(
                model,
                features,
                eids,
                use_entity_ids=use_entity_ids,
                device=device,
                batch_size=batch_size,
            )
            metric_part, prediction_part, arrays_by_horizon = evaluate_entity_predictions(
                scope=scope,
                entity_name=entity,
                selection_role=role,
                split_name=split_name,
                horizons=horizons,
                raw_targets=raw_targets,
                predictions_norm=predictions,
                mean=mean,
                std=std,
                calibration_margins=calibration_margins,
                meta_rows=meta_rows,
            )
            forecast_rows.extend(metric_part)
            prediction_rows.extend(prediction_part)
            if split_name == "test":
                arrays_for_policy[entity] = arrays_by_horizon

    is_service = service_scope
    for entity in entity_names:
        if service_summary is not None and entity in service_summary:
            request_cores, request_source, request_fallback = service_request_cores(service_summary[entity])
        else:
            request_cores, request_source, request_fallback = 1.0, "n/a", False
        add_policy_rows(
            scope=scope,
            entity=entity,
            selection_role=selection_roles.get(entity, "aggregate_full" if scope == "aggregate" else "service_pilot"),
            policy_config=policy_config,
            arrays_by_horizon=arrays_for_policy[entity],
            request_cores=request_cores,
            request_source=request_source,
            request_fallback_used=request_fallback,
            is_service=is_service,
            policy_rows=policy_rows,
            policy_series_rows=policy_series_rows,
        )

    resource_runtime = time.perf_counter() - resource_start
    resource_row = {
        "run_id": RUN_ID,
        "scope": scope,
        "model_name": MODEL_NAME,
        "entity_count": len(entity_names),
        "entities": ";".join(entity_names),
        "train_windows": int(len(train_x)),
        "validation_windows": int(len(valid_x)),
        "hidden_width": hidden_width,
        "dilations": ";".join(str(value) for value in dilations),
        "batch_size": batch_size,
        "max_epochs": max_epochs,
        "epochs_completed": epochs_completed,
        "train_runtime_seconds": train_runtime,
        "total_runtime_seconds": resource_runtime,
        "mean_epoch_seconds": train_runtime / max(epochs_completed, 1),
        "first_train_loss": train_losses[0],
        "last_train_loss": train_losses[-1],
        "first_valid_loss": valid_losses[0],
        "best_valid_loss": min(valid_losses),
        "last_valid_loss": valid_losses[-1],
        "peak_cuda_memory_bytes": int(torch.cuda.max_memory_allocated()) if torch.cuda.is_available() else 0,
        "process_memory_rss_bytes": int(psutil.Process(os.getpid()).memory_info().rss),
    }
    return (
        profile_rows,
        forecast_rows,
        prediction_rows,
        calibration_rows,
        policy_rows,
        policy_series_rows,
        resource_row,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("experiments/configs/default_v2018.yaml"))
    parser.add_argument("--aggregate-csv", type=Path, default=None)
    parser.add_argument("--service-csv", type=Path, default=Path("data/processed/service_cohort_broad_v2018.csv"))
    parser.add_argument("--service-summary-csv", type=Path, default=Path("data/processed/service_cohort_broad_summary_v2018.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("experiments/results/full_ua_mstcn_pilot"))
    parser.add_argument("--max-epochs", type=int, default=15)
    parser.add_argument("--patience", type=int, default=4)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--hidden-width", type=int, default=64)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    with resolve_path(args.config, repo_root).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    aggregate_csv = resolve_path(args.aggregate_csv or Path(config["dataset"]["output_series_csv"]), repo_root)
    service_csv = resolve_path(args.service_csv, repo_root)
    service_summary_csv = resolve_path(args.service_summary_csv, repo_root)
    output_dir = resolve_path(args.output_dir, repo_root)
    if output_dir.exists():
        raise SystemExit(f"Refusing to overwrite existing output directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=False)

    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(args.seed)
        torch.cuda.reset_peak_memory_stats()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    horizons = tuple(int(value) for value in config["forecast"]["horizons"])
    context_window = int(config["forecast"]["context_window"])
    train_ratio = float(config["forecast"]["train_ratio"])
    valid_ratio = float(config["forecast"]["valid_ratio"])
    policy_config = config["policy"]
    metrics_path = resolve_path(Path(config["output"]["metrics_csv"]), repo_root)
    metrics_hash_before = sha256_file(metrics_path)
    census_before = resource_snapshot(repo_root)

    aggregate_values = read_aggregate_series(aggregate_csv, "cluster_cpu_utilization_mean")
    service_values = read_service_series(service_csv, SERVICE_ROLES.keys())
    service_summary = read_service_summary(service_summary_csv)

    all_profile_rows: list[dict] = []
    all_forecast_rows: list[dict] = []
    all_prediction_rows: list[dict] = []
    all_calibration_rows: list[dict] = []
    all_policy_rows: list[dict] = []
    all_policy_series_rows: list[dict] = []
    resource_rows: list[dict] = []
    scope_results = []
    scope_results.append(
        run_scope(
            scope="aggregate",
            series_by_entity={"aggregate_cluster": aggregate_values},
            selection_roles={"aggregate_cluster": "aggregate_full"},
            context_window=context_window,
            horizons=horizons,
            train_ratio=train_ratio,
            valid_ratio=valid_ratio,
            policy_config=policy_config,
            service_summary=None,
            hidden_width=int(args.hidden_width),
            dilations=(1, 2, 4, 8, 16),
            batch_size=int(args.batch_size),
            max_epochs=int(args.max_epochs),
            patience=int(args.patience),
            device=device,
        )
    )
    scope_results.append(
        run_scope(
            scope="service_pilot",
            series_by_entity={app_du: service_values[app_du] for app_du in SERVICE_ROLES},
            selection_roles=SERVICE_ROLES,
            context_window=context_window,
            horizons=horizons,
            train_ratio=train_ratio,
            valid_ratio=valid_ratio,
            policy_config=policy_config,
            service_summary=service_summary,
            hidden_width=int(args.hidden_width),
            dilations=(1, 2, 4, 8, 16),
            batch_size=int(args.batch_size),
            max_epochs=int(args.max_epochs),
            patience=int(args.patience),
            device=device,
        )
    )
    for profile, forecast, predictions, calibration, policy, policy_series, resource in scope_results:
        all_profile_rows.extend(profile)
        all_forecast_rows.extend(forecast)
        all_prediction_rows.extend(predictions)
        all_calibration_rows.extend(calibration)
        all_policy_rows.extend(policy)
        all_policy_series_rows.extend(policy_series)
        resource_rows.append(resource)

    write_csv(output_dir / "full_ua_mstcn_pilot_selection_profile.csv", all_profile_rows)
    write_csv(output_dir / "full_ua_mstcn_pilot_forecasting_metrics.csv", all_forecast_rows)
    write_csv(output_dir / "full_ua_mstcn_pilot_predictions.csv", all_prediction_rows)
    write_csv(output_dir / "full_ua_mstcn_pilot_calibration.csv", all_calibration_rows)
    write_csv(output_dir / "full_ua_mstcn_pilot_policy_metrics.csv", all_policy_rows)
    write_csv(output_dir / "full_ua_mstcn_pilot_policy_series.csv", all_policy_series_rows)
    write_csv(output_dir / "full_ua_mstcn_pilot_resource_trace.csv", resource_rows)

    metrics_hash_after = sha256_file(metrics_path)
    census_after = resource_snapshot(repo_root)
    gate_failures: list[str] = []
    service_entities = {row["entity"] for row in all_profile_rows if row["scope"] == "service_pilot"}
    if service_entities != set(SERVICE_ROLES):
        gate_failures.append(f"service pilot entities mismatch: {sorted(service_entities)}")
    if {row["scope"] for row in resource_rows} != {"aggregate", "service_pilot"}:
        gate_failures.append("resource trace missing aggregate or service_pilot scope")
    if any(row["status"] != "pass" for row in all_forecast_rows):
        gate_failures.append("one or more forecasting metric rows failed")
    if sum(int(row["calibrated_crossing_count"]) for row in all_forecast_rows) != 0:
        gate_failures.append("calibrated P90 crossing count is nonzero")
    if not rows_numeric_finite(all_forecast_rows):
        gate_failures.append("forecasting metrics contain non-finite values")
    if not rows_numeric_finite(all_policy_rows):
        gate_failures.append("policy metrics contain non-finite values")
    if any(not (0.0 <= float(row["sla_violation"]) <= 1.0) for row in all_policy_rows):
        gate_failures.append("policy SLA violation outside [0, 1]")
    capacity_columns = ["reactive_capacity", "lagged_capacity", "predictive_capacity"]
    for column in capacity_columns:
        if any(float(row[column]) < 0.0 for row in all_policy_series_rows):
            gate_failures.append(f"{column} contains negative values")
    if metrics_hash_before != metrics_hash_after:
        gate_failures.append("central metrics.csv changed")
    if (repo_root / "experiments" / "results" / "full_ua_mstcn_broad").exists():
        gate_failures.append("unexpected full_ua_mstcn_broad directory exists")

    status = {
        "run_id": RUN_ID,
        "status": "pass" if not gate_failures else "fail",
        "output_dir": str(output_dir),
        "scope": "Stage 2 pilot only; no broad Full UA-MSTCN run executed",
        "test_split_use": "evaluation only; fitting uses train prefix and P90 calibration uses validation prefix",
        "seed": int(args.seed),
        "horizons": list(horizons),
        "context_window": context_window,
        "fixed_services": list(SERVICE_ROLES),
        "metrics_csv_hash_before": metrics_hash_before,
        "metrics_csv_hash_after": metrics_hash_after,
        "resource_before": census_before,
        "resource_after": census_after,
        "gate_failures": gate_failures,
        "metrics_csv_updated": False,
        "manuscript_conclusion_changed": False,
    }
    (output_dir / "full_ua_mstcn_pilot_status.json").write_text(json.dumps(status, indent=2), encoding="utf-8")

    report_lines = [
        "# Full UA-MSTCN Stage 2 Pilot Report",
        "",
        f"- run_id: `{RUN_ID}`",
        f"- status: `{status['status']}`",
        f"- output_dir: `{output_dir}`",
        f"- device: `{census_after['cuda_device']}`",
        f"- torch: `{torch.__version__}`",
        "- scope: Stage 2 pilot only; no broad Full UA-MSTCN run executed.",
        "- test split use: evaluation only; fitting uses train prefix and P90 calibration uses validation prefix.",
        f"- metrics_csv_hash_before: `{metrics_hash_before}`",
        f"- metrics_csv_hash_after: `{metrics_hash_after}`",
        "",
        "## Gate Result",
        "",
    ]
    if gate_failures:
        report_lines.extend(f"- FAIL: {failure}" for failure in gate_failures)
    else:
        report_lines.append("- PASS: aggregate full plus five-service pilot gate passed.")
    report_lines.extend(
        [
            "",
            "## Resource Trace",
            "",
            "```csv",
            ",".join(resource_rows[0].keys()),
        ]
    )
    for row in resource_rows:
        report_lines.append(",".join(str(row[key]) for key in resource_rows[0].keys()))
    report_lines.extend(
        [
            "```",
            "",
            "## Test Forecasting Metrics",
            "",
            "```csv",
        ]
    )
    test_rows = [row for row in all_forecast_rows if row["split"] == "test"]
    report_lines.append(",".join(test_rows[0].keys()))
    for row in test_rows:
        report_lines.append(",".join(str(row[key]) for key in test_rows[0].keys()))
    report_lines.extend(
        [
            "```",
            "",
            "## Policy Metrics",
            "",
            "```csv",
            ",".join(all_policy_rows[0].keys()),
        ]
    )
    for row in all_policy_rows:
        report_lines.append(",".join(str(row[key]) for key in all_policy_rows[0].keys()))
    report_lines.extend(["```", ""])
    (output_dir / "full_ua_mstcn_pilot_report.md").write_text("\n".join(report_lines), encoding="utf-8")

    if gate_failures:
        raise SystemExit(f"Full UA-MSTCN pilot gate failed; see {output_dir / 'full_ua_mstcn_pilot_report.md'}")


if __name__ == "__main__":
    main()
