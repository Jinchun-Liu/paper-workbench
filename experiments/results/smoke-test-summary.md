# Smoke-Test Summary

Dataset artifact: `paper-workbench/data/processed/cluster_series_v2018.csv`

- Samples: `11208` observed one-minute points
- Signal: aggregate cluster CPU utilization mean
- Context window: `60`
- Horizons: `1`, `5`, `10`

## Forecasting baselines

| Horizon | Best model | MAE | RMSE | MAPE |
| --- | --- | ---: | ---: | ---: |
| 1 min | Linear regression | 2.2682 | 3.1229 | 0.0564 |
| 5 min | Random forest | 3.9283 | 5.2374 | 0.0972 |
| 10 min | Linear regression | 4.3066 | 5.7655 | 0.1067 |

Average MAE by model:

- `linear_regression`: `3.5140`
- `random_forest`: `3.5286`
- `ua_mstcn_lite_quantile_forest`: `3.5476`
- `persistence`: `4.0276`
- `moving_average`: `4.1490`

## Quantile calibration

| Horizon | P50 coverage | P90 coverage | Mean interval width |
| --- | ---: | ---: | ---: |
| 1 min | 0.5055 | 0.9199 | 4.6234 |
| 5 min | 0.5161 | 0.8665 | 6.7089 |
| 10 min | 0.5003 | 0.8679 | 7.4054 |

## Machine-cohort benchmark

Dataset artifacts:

- `paper-workbench/data/processed/machine_cohort_top12_v2018.csv`
- `paper-workbench/data/processed/machine_cohort_top12_summary_v2018.csv`

Selection summary:

- `12` machines
- coverage ratio range: `0.9372` to `0.9472`
- average imputed ratio after reindexing: `0.0581`

Average MAE across machines:

| Horizon | Best model | MAE |
| --- | --- | ---: |
| 1 min | Linear regression | 3.6335 |
| 5 min | Linear regression | 5.5203 |
| 10 min | Linear regression | 5.9659 |

Average quantile coverage of `UA-MSTCN-Lite` across the 12-machine cohort:

| Horizon | P50 coverage | P90 coverage |
| --- | ---: | ---: |
| 1 min | 0.5098 | 0.8909 |
| 5 min | 0.5235 | 0.8527 |
| 10 min | 0.5175 | 0.8469 |

## Cross-machine transfer

Artifact directory:

- `paper-workbench/experiments/results/machine_transfer/`

Protocol:

- `3` deterministic folds
- `8` train machines and `4` held-out machines per fold
- zero-shot global models are evaluated on completely unseen machines

Zero-shot MAE on held-out machines:

| Horizon | Global linear | Global UA-MSTCN-Lite | Global random forest | Persistence | Entity-specific linear |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 min | 3.6294 | 3.9342 | 4.4959 | 3.7163 | 3.6335 |
| 5 min | 5.5030 | 6.3275 | 6.2931 | 6.2682 | 5.5203 |
| 10 min | 5.9528 | 6.6481 | 6.6419 | 6.9318 | 5.9659 |

Transfer interpretation:

- pooled linear regression matches the entity-specific linear upper bound within `0.02` MAE at all horizons
- global `UA-MSTCN-Lite` remains calibrated on held-out machines with average `P90` coverage `0.9044 / 0.8586 / 0.8529`
- the current data therefore favors simple transferable linear structure for point prediction, while the uncertainty-aware surrogate still contributes usable quantile bands

## Service-level cohort

Dataset artifacts:

- `paper-workbench/data/processed/service_cohort_top10_v2018.csv`
- `paper-workbench/data/processed/service_cohort_top10_summary_v2018.csv`

Selection summary:

- `10` `app_du` services
- `2036` selected containers and `1970` matched containers
- common minute span: `11520`
- mean observed-minute coverage: `0.9713`
- coverage range: `0.9637` to `0.9727`
- mean container hit ratio: `0.9564`
- mean imputed ratio after reindexing: `0.0287`

Average MAE across the 10-service cohort:

| Horizon | Best model | MAE |
| --- | --- | ---: |
| 1 min | Linear regression | 5.6655 |
| 5 min | UA-MSTCN-Lite | 7.4069 |
| 10 min | Random forest | 8.1251 |

Average MAE across all service-horizon cells by model:

- `ua_mstcn_lite_quantile_forest`: `7.4216`
- `random_forest`: `7.4752`
- `linear_regression`: `7.7623`
- `persistence`: `8.1760`

Average quantile coverage of `UA-MSTCN-Lite` across the 10 services:

| Horizon | P50 coverage | P90 coverage |
| --- | ---: | ---: |
| 1 min | 0.4736 | 0.8917 |
| 5 min | 0.4765 | 0.8826 |
| 10 min | 0.4671 | 0.8660 |

Service-level policy comparison:

| Policy | SLA violation | Over-provisioning | Under-provisioning | Actions | Mean capacity |
| --- | ---: | ---: | ---: | ---: | ---: |
| Reactive service policy | 0.0103 | 5.1767 | 0.2063 | 481.2 | 13.5541 |
| Predictive service policy | 0.0434 | 4.4567 | 0.2751 | 428.8 | 14.0529 |

Service-level interpretation:

- the expanded 10-service cohort materially narrows the earlier construct-validity gap
- `UA-MSTCN-Lite` remains the strongest model on average after expanding from `2` to `10` services
- predictive control reduces over-provisioning for `4/10` services and scaling actions for `7/10`, but improves SLA violation for only `1/10`

## Policy comparison

| Policy | SLA violation | Over-provisioning | Under-provisioning | Mean capacity |
| --- | ---: | ---: | ---: | ---: |
| Reactive threshold | 0.0006 | 0.3506 | 0.0000 | 0.8207 |
| Predictive uncertainty-aware | 0.0346 | 0.1410 | 0.0013 | 0.6098 |

## Added manuscript views

- `cluster_workload_overview.png`: full-trace CPU, memory, active-machine counts, and first-day zoom
- `resource_distribution_views.png`: distribution and hour-of-day views
- `baseline_mae_by_horizon.png`: model comparison across horizons
- `forecast_case_study.png`: aligned test-slice comparison across horizons
- `forecast_latency_tradeoff.png`: average accuracy versus benchmark runtime
- `ua_context_sensitivity.png`: forecast sensitivity to 30/60/120-minute context windows
- `forecast_regime_comparison.png`: 5-minute forecast error across stable, moderate, and bursty regimes
- `quantile_coverage.png`: empirical P50/P90 coverage of the uncertainty-aware surrogate
- `policy_pareto_sensitivity.png`: SLA versus over-provisioning under scale-out margin and cooldown sweeps
- `machine_cohort_mae_by_horizon.png`: average MAE across the 12-machine high-coverage cohort
- `machine_cohort_entity_mae.png`: per-machine average MAE variation across models
- `machine_cohort_quantile_coverage.png`: average P50/P90 coverage across the machine cohort
- `machine_transfer_zero_shot_mae.png`: held-out-machine zero-shot transfer comparison
- `machine_transfer_quantile_coverage.png`: held-out-machine P50/P90 coverage for the global UA model
- `machine_transfer_gap_to_entity_linear.png`: gap from zero-shot global UA to entity-specific linear regression
- `service_workload_overview.png`: representative service-level demand views
- `service_forecasting_mae.png`: service-level forecast comparison across horizons on the expanded 10-service cohort
- `service_quantile_coverage.png`: service-level P50/P90 coverage of `UA-MSTCN-Lite` on the expanded cohort
- `service_policy_summary.png`: mean service-level policy comparison across the selected services
- `service_policy_by_app.png`: per-service policy heterogeneity across the expanded 10-service cohort

## Interpretation

- The trace processing and baseline harness are working end to end.
- The leakage-free rerun removed the earlier optimistic forecasting result; linear regression and random forest are the strongest point baselines on the aggregate workload series.
- The trainable `UA-MSTCN-Lite` surrogate remains competitive in MAE and now has direct empirical calibration evidence.
- The new machine-cohort benchmark shows that the aggregate conclusions are not just artifacts of one global series; linear regression remains the strongest point baseline across entities, while `UA-MSTCN-Lite` retains usable quantile calibration.
- The new cross-machine transfer benchmark shows that pooled linear regression generalizes almost perfectly to held-out machines, setting a stronger transfer baseline than the current surrogate can beat.
- The new expanded service-level cohort shows that the manuscript no longer depends only on aggregate or machine abstractions; it now includes official container-derived evidence at a more natural autoscaling unit across 10 services.
- Service-level control results remain intentionally mixed rather than overclaimed: average over-provisioning and action count improve, but SLA generally worsens and the gains do not transfer uniformly across services.
- The predictive policy is now evaluated with a trained uncertainty-aware forecaster in the same normalized capacity space as the reactive baseline.
- The manuscript now has enough real figures and quantitative results to move beyond a thin pilot-study presentation.
