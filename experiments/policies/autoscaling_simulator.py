#!/usr/bin/env python3
"""Trace-driven autoscaling simulator for aggregate cluster capacity."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class PolicyMetrics:
    sla_violation: float
    over_provisioning: float
    under_provisioning: float
    scaling_actions: int
    average_capacity: float


def required_capacity(actual_load: np.ndarray, headroom_ratio: float, min_capacity: float) -> np.ndarray:
    return np.maximum(actual_load * (1.0 + headroom_ratio), min_capacity)


def run_reactive(
    actual_load: np.ndarray,
    upper_threshold: float,
    lower_threshold: float,
    min_capacity: float,
    max_step_change: float,
) -> tuple[np.ndarray, PolicyMetrics]:
    capacity = np.zeros_like(actual_load, dtype=float)
    capacity[0] = max(min_capacity, actual_load[0])
    actions = 0
    for idx in range(1, len(actual_load)):
        prev = capacity[idx - 1]
        util = actual_load[idx] / max(prev, 1e-6)
        new_cap = prev
        if util > upper_threshold:
            new_cap = prev + max_step_change
        elif util < lower_threshold:
            new_cap = max(min_capacity, prev - max_step_change)
        actions += int(abs(new_cap - prev) > 1e-9)
        capacity[idx] = new_cap
    return capacity, summarize_policy(actual_load, capacity, actions)


def run_predictive(
    actual_load: np.ndarray,
    forecast_p50: np.ndarray,
    forecast_p90: np.ndarray,
    min_capacity: float,
    cooldown_steps: int,
    max_step_change: float,
    scale_in_safety_margin: float,
) -> tuple[np.ndarray, PolicyMetrics]:
    capacity = np.zeros_like(actual_load, dtype=float)
    capacity[0] = max(min_capacity, forecast_p90[0])
    actions = 0
    cooldown = 0
    for idx in range(1, len(actual_load)):
        prev = capacity[idx - 1]
        target_up = forecast_p90[idx]
        target_down = max(min_capacity, forecast_p50[idx] * (1.0 + scale_in_safety_margin))
        new_cap = prev
        # Scale-out must remain responsive; cooldown is only used to suppress
        # oscillatory scale-in after recent decisions.
        if target_up > prev:
            new_cap = min(prev + max_step_change, target_up)
        elif cooldown == 0 and target_down < prev:
            new_cap = max(prev - max_step_change, target_down)
            cooldown = cooldown_steps
        else:
            cooldown = max(0, cooldown - 1)
        actions += int(abs(new_cap - prev) > 1e-9)
        capacity[idx] = new_cap
    return capacity, summarize_policy(actual_load, capacity, actions)


def run_lagged_target_tracking(
    actual_load: np.ndarray,
    min_capacity: float,
    max_step_change: float,
) -> tuple[np.ndarray, PolicyMetrics]:
    capacity = np.zeros_like(actual_load, dtype=float)
    capacity[0] = max(min_capacity, actual_load[0])
    actions = 0
    for idx in range(1, len(actual_load)):
        prev = capacity[idx - 1]
        target = max(min_capacity, actual_load[idx - 1])
        if target > prev:
            new_cap = min(prev + max_step_change, target)
        elif target < prev:
            new_cap = max(prev - max_step_change, target)
        else:
            new_cap = prev
        actions += int(abs(new_cap - prev) > 1e-9)
        capacity[idx] = new_cap
    return capacity, summarize_policy(actual_load, capacity, actions)


def summarize_policy(actual_load: np.ndarray, capacity: np.ndarray, actions: int) -> PolicyMetrics:
    slack = capacity - actual_load
    under = np.clip(-slack, 0.0, None)
    over = np.clip(slack, 0.0, None)
    return PolicyMetrics(
        sla_violation=float(np.mean(actual_load > capacity)),
        over_provisioning=float(np.mean(over)),
        under_provisioning=float(np.mean(under)),
        scaling_actions=int(actions),
        average_capacity=float(np.mean(capacity)),
    )
