#!/usr/bin/env python3
"""Trainable uncertainty-aware multi-horizon forecaster.

This implementation is a lightweight surrogate for the intended UA-MSTCN family.
It preserves the same multi-horizon and uncertainty-aware interface while using
multi-scale features and a quantile-aware tree ensemble that is reproducible in
the current local environment without extra deep-learning dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.ensemble import RandomForestRegressor


@dataclass
class UAMSTCNOutput:
    p50: np.ndarray
    p90: np.ndarray


def _window_slope(values: np.ndarray) -> float:
    if len(values) < 2:
        return 0.0
    return float((values[-1] - values[0]) / (len(values) - 1))


class UAMSTCN:
    """Lightweight trainable surrogate that matches the UA-MSTCN interface."""

    def __init__(
        self,
        context_window: int,
        horizons: list[int],
        *,
        use_multiscale_features: bool = True,
        calibration_quantile: float | None = 0.99,
        n_estimators: int = 200,
        variant_label: str | None = None,
    ) -> None:
        self.context_window = context_window
        self.horizons = horizons
        self.use_multiscale_features = use_multiscale_features
        self.calibration_quantile = calibration_quantile
        self.n_estimators = n_estimators
        if variant_label is not None:
            self.name = variant_label
        elif use_multiscale_features and calibration_quantile is not None:
            self.name = "ua_mstcn_lite_quantile_forest"
        elif not use_multiscale_features and calibration_quantile is not None:
            self.name = "ua_mstcn_lite_no_multiscale"
        elif use_multiscale_features and calibration_quantile is None:
            self.name = "ua_mstcn_lite_no_calibration"
        else:
            self.name = "ua_mstcn_lite_reduced"
        self.models: dict[int, RandomForestRegressor] = {}
        self.upper_calibration_margin: dict[int, float] = {}
        self.target_min: float | None = None
        self.target_max: float | None = None

    def _feature_vector(self, history_window: np.ndarray) -> np.ndarray:
        history = np.asarray(history_window, dtype=float)
        if len(history) != self.context_window:
            raise ValueError(f"Expected history length {self.context_window}, got {len(history)}")

        features: list[float] = []
        lag_steps = [lag for lag in [1, 2, 3, 5, 10, 15, 20, 30, 45, 60] if lag <= len(history)]
        for lag in lag_steps:
            features.append(float(history[-lag]))

        if self.use_multiscale_features:
            windows = [window for window in [3, 5, 10, 20, 30, 60] if window <= len(history)]
            for window in windows:
                tail = history[-window:]
                features.extend(
                    [
                        float(np.mean(tail)),
                        float(np.std(tail)),
                        float(np.min(tail)),
                        float(np.max(tail)),
                        float(np.median(tail)),
                        float(np.quantile(tail, 0.1)),
                        float(np.quantile(tail, 0.9)),
                        float(tail[-1] - tail[0]),
                        float(tail[-1] - np.mean(tail)),
                        _window_slope(tail),
                    ]
                )

        features.extend(
            [
                float(np.mean(history[-min(5, len(history)) :]) - np.mean(history[-min(20, len(history)) :])),
                float(np.mean(history[-min(10, len(history)) :]) - np.mean(history[-min(30, len(history)) :])),
                float(np.std(history[-min(10, len(history)) :]) - np.std(history[-min(30, len(history)) :])),
                float(history[-1] - history[-min(2, len(history))]),
                float(history[-1] - history[-min(5, len(history))]),
                float(history[-1] - history[-min(10, len(history))]),
                float(np.max(history[-min(10, len(history)) :]) - np.min(history[-min(10, len(history)) :])),
                float(np.max(history[-min(30, len(history)) :]) - np.min(history[-min(30, len(history)) :])),
            ]
        )
        return np.asarray(features, dtype=float)

    def _build_supervised(self, series: np.ndarray, horizon: int) -> tuple[np.ndarray, np.ndarray]:
        xs = []
        ys = []
        for idx in range(self.context_window, len(series) - horizon + 1):
            history = series[idx - self.context_window : idx]
            xs.append(self._feature_vector(history))
            ys.append(series[idx + horizon - 1])
        return np.asarray(xs, dtype=float), np.asarray(ys, dtype=float)

    def fit(self, series: np.ndarray) -> None:
        train_series = np.asarray(series, dtype=float)
        self.target_min = float(np.min(train_series))
        self.target_max = float(np.max(train_series))
        self.models = {}
        self.upper_calibration_margin = {}

        for horizon in self.horizons:
            train_x, train_y = self._build_supervised(train_series, horizon)
            model = RandomForestRegressor(
                n_estimators=self.n_estimators,
                min_samples_leaf=3,
                max_features="sqrt",
                random_state=42 + horizon,
                n_jobs=-1,
            )
            model.fit(train_x, train_y)
            self.models[horizon] = model
            tree_predictions = np.vstack([estimator.predict(train_x) for estimator in model.estimators_])
            train_p50 = np.quantile(tree_predictions, 0.50, axis=0)
            positive_residual = np.clip(train_y - train_p50, 0.0, None)
            if self.calibration_quantile is None:
                self.upper_calibration_margin[horizon] = 0.0
            else:
                self.upper_calibration_margin[horizon] = float(
                    np.quantile(positive_residual, self.calibration_quantile)
                )

    def fit_multi_series(self, series_list: list[np.ndarray]) -> None:
        prepared_series = [np.asarray(series, dtype=float) for series in series_list]
        if not prepared_series:
            raise ValueError("fit_multi_series() requires at least one training series.")

        self.target_min = float(min(np.min(series) for series in prepared_series))
        self.target_max = float(max(np.max(series) for series in prepared_series))
        self.models = {}
        self.upper_calibration_margin = {}

        for horizon in self.horizons:
            train_x_parts = []
            train_y_parts = []
            for series in prepared_series:
                if len(series) < self.context_window + horizon:
                    continue
                part_x, part_y = self._build_supervised(series, horizon)
                if len(part_x) == 0:
                    continue
                train_x_parts.append(part_x)
                train_y_parts.append(part_y)
            if not train_x_parts:
                raise ValueError(f"No usable windows were created for horizon {horizon}.")

            train_x = np.vstack(train_x_parts)
            train_y = np.concatenate(train_y_parts)
            model = RandomForestRegressor(
                n_estimators=self.n_estimators,
                min_samples_leaf=3,
                max_features="sqrt",
                random_state=42 + horizon,
                n_jobs=-1,
            )
            model.fit(train_x, train_y)
            self.models[horizon] = model
            tree_predictions = np.vstack([estimator.predict(train_x) for estimator in model.estimators_])
            train_p50 = np.quantile(tree_predictions, 0.50, axis=0)
            positive_residual = np.clip(train_y - train_p50, 0.0, None)
            if self.calibration_quantile is None:
                self.upper_calibration_margin[horizon] = 0.0
            else:
                self.upper_calibration_margin[horizon] = float(
                    np.quantile(positive_residual, self.calibration_quantile)
                )

    def history_matrix(self, series: np.ndarray, horizon: int) -> tuple[np.ndarray, np.ndarray]:
        histories = []
        targets = []
        for idx in range(self.context_window, len(series) - horizon + 1):
            histories.append(series[idx - self.context_window : idx])
            targets.append(series[idx + horizon - 1])
        return np.asarray(histories, dtype=float), np.asarray(targets, dtype=float)

    def predict_batch(self, history_windows: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        if not self.models:
            raise RuntimeError("Model must be fitted before calling predict_batch().")

        history_arr = np.asarray(history_windows, dtype=float)
        if history_arr.ndim == 1:
            history_arr = history_arr.reshape(1, -1)
        features = np.asarray([self._feature_vector(window) for window in history_arr], dtype=float)

        p50_matrix = np.zeros((len(history_arr), len(self.horizons)), dtype=float)
        p90_matrix = np.zeros((len(history_arr), len(self.horizons)), dtype=float)
        for horizon_index, horizon in enumerate(self.horizons):
            model = self.models[horizon]
            tree_predictions = np.vstack([estimator.predict(features) for estimator in model.estimators_])
            p50 = np.quantile(tree_predictions, 0.50, axis=0)
            p90 = np.quantile(tree_predictions, 0.90, axis=0)
            if self.target_min is not None and self.target_max is not None:
                p50 = np.clip(p50, self.target_min, self.target_max)
                p90 = np.clip(p90, self.target_min, self.target_max * 1.10)
            p90 = np.maximum(p90, p50 + self.upper_calibration_margin.get(horizon, 0.0))
            p90 = np.maximum(p90, p50 + 1e-6)
            p50_matrix[:, horizon_index] = p50
            p90_matrix[:, horizon_index] = p90
        return p50_matrix, p90_matrix

    def _predict_quantiles(
        self,
        horizon: int,
        model: RandomForestRegressor,
        features: np.ndarray,
    ) -> tuple[float, float]:
        tree_predictions = np.asarray(
            [estimator.predict(features.reshape(1, -1))[0] for estimator in model.estimators_],
            dtype=float,
        )
        p50 = float(np.quantile(tree_predictions, 0.50))
        p90 = float(np.quantile(tree_predictions, 0.90))
        if self.target_min is not None and self.target_max is not None:
            p50 = float(np.clip(p50, self.target_min, self.target_max))
            p90 = float(np.clip(p90, self.target_min, self.target_max * 1.10))
        p90 = max(p90, p50 + self.upper_calibration_margin.get(horizon, 0.0))
        p90 = max(p90, p50 + 1e-6)
        return p50, p90

    def predict(self, history_window: np.ndarray) -> UAMSTCNOutput:
        if not self.models:
            raise RuntimeError("Model must be fitted before calling predict().")

        features = self._feature_vector(np.asarray(history_window, dtype=float))
        p50_values = []
        p90_values = []
        for horizon in self.horizons:
            p50, p90 = self._predict_quantiles(horizon, self.models[horizon], features)
            p50_values.append(p50)
            p90_values.append(p90)
        return UAMSTCNOutput(
            p50=np.asarray(p50_values, dtype=float),
            p90=np.asarray(p90_values, dtype=float),
        )
