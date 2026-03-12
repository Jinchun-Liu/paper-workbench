#!/usr/bin/env python3
"""Lightweight baseline forecasters for the first reproducible pass."""

from __future__ import annotations

from dataclasses import dataclass
import warnings

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler


def make_supervised(series: np.ndarray, context_window: int, horizon: int) -> tuple[np.ndarray, np.ndarray]:
    xs = []
    ys = []
    for idx in range(context_window, len(series) - horizon + 1):
        xs.append(series[idx - context_window : idx])
        ys.append(series[idx + horizon - 1])
    return np.asarray(xs), np.asarray(ys)


@dataclass
class ForecastResult:
    name: str
    horizon: int
    y_true: np.ndarray
    y_pred: np.ndarray


@dataclass
class ScaledMLPModel:
    x_scaler: StandardScaler
    y_scaler: StandardScaler
    model: MLPRegressor

    def predict(self, x: np.ndarray) -> np.ndarray:
        x_scaled = self.x_scaler.transform(x)
        y_scaled = self.model.predict(x_scaled)
        return self.y_scaler.inverse_transform(y_scaled.reshape(-1, 1)).ravel()


def persistence(series: np.ndarray, context_window: int, horizon: int) -> ForecastResult:
    x, y = make_supervised(series, context_window, horizon)
    pred = x[:, -1]
    return ForecastResult("persistence", horizon, y, pred)


def moving_average(series: np.ndarray, context_window: int, horizon: int, window: int = 5) -> ForecastResult:
    x, y = make_supervised(series, context_window, horizon)
    pred = x[:, -window:].mean(axis=1)
    return ForecastResult("moving_average", horizon, y, pred)


def linear_regression(
    train_series: np.ndarray,
    test_series: np.ndarray,
    context_window: int,
    horizon: int,
) -> ForecastResult:
    train_x, train_y = make_supervised(train_series, context_window, horizon)
    test_x, test_y = make_supervised(test_series, context_window, horizon)
    model = LinearRegression()
    model.fit(train_x, train_y)
    pred = model.predict(test_x)
    return ForecastResult("linear_regression", horizon, test_y, pred)


def random_forest(
    train_series: np.ndarray,
    test_series: np.ndarray,
    context_window: int,
    horizon: int,
) -> ForecastResult:
    train_x, train_y = make_supervised(train_series, context_window, horizon)
    test_x, test_y = make_supervised(test_series, context_window, horizon)
    model = RandomForestRegressor(
        n_estimators=200,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=1,
    )
    model.fit(train_x, train_y)
    pred = model.predict(test_x)
    return ForecastResult("random_forest", horizon, test_y, pred)


def fit_mlp_regressor(
    train_x: np.ndarray,
    train_y: np.ndarray,
    *,
    random_state: int = 42,
    hidden_layer_sizes: tuple[int, ...] = (64, 32),
    max_iter: int = 250,
) -> ScaledMLPModel:
    x_scaler = StandardScaler()
    y_scaler = StandardScaler()
    train_x_scaled = x_scaler.fit_transform(train_x)
    train_y_scaled = y_scaler.fit_transform(train_y.reshape(-1, 1)).ravel()

    model = MLPRegressor(
        hidden_layer_sizes=hidden_layer_sizes,
        activation="relu",
        solver="adam",
        alpha=1e-4,
        batch_size=min(128, len(train_x_scaled)),
        learning_rate_init=1e-3,
        max_iter=max_iter,
        early_stopping=True,
        validation_fraction=0.15,
        n_iter_no_change=15,
        random_state=random_state,
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model.fit(train_x_scaled, train_y_scaled)
    return ScaledMLPModel(x_scaler=x_scaler, y_scaler=y_scaler, model=model)


def mlp_regression(
    train_series: np.ndarray,
    test_series: np.ndarray,
    context_window: int,
    horizon: int,
) -> ForecastResult:
    train_x, train_y = make_supervised(train_series, context_window, horizon)
    test_x, test_y = make_supervised(test_series, context_window, horizon)
    model = fit_mlp_regressor(train_x, train_y, random_state=42 + horizon)
    pred = model.predict(test_x)
    return ForecastResult("mlp_regressor", horizon, test_y, pred)
