# Aggregate QLR Full Report

- run_id: `qlr_aggregate_full_20260427`
- series_path: `D:\Desktop\Cluster Computing\paper-workbench-full\Users\liujinchun\Downloads\skills_codex\paper-workbench\data\processed\cluster_series_v2018.csv`
- train_plus_validation_rows_used_for_fit: `9526`
- heldout_test_rows_used_for_evaluation: `1682`
- split_index: `9526`
- context_window: `60`
- horizons: `1, 5, 10`
- alpha: `0.0001`
- solver: `highs`
- status: `pass`
- central_metrics_updated: `True`
- central_metrics_csv: `D:\Desktop\Cluster Computing\paper-workbench-full\Users\liujinchun\Downloads\skills_codex\paper-workbench\experiments\results\metrics.csv`

## Split Discipline

The held-out test split is used only for evaluation. QLR fitting uses only the train+validation prefix. No test rows are used to select parameters, choose a model, or tune the policy.

## Gate Checks

- y_true, P50, raw P90, and guarded P90 predictions are nonempty and length-aligned.
- Raw crossing count and raw crossing rate are recorded before applying the non-crossing guard.
- Guarded P90 is computed as `max(raw_p90, p50)` and must have zero crossing violations.
- Forecasting metrics and policy metrics must be finite.
- Policy SLA violation must be within [0, 1].
- `metrics.csv` is updated only after all gates pass, and only `qlr-*` experiment ids are added or replaced.

## Forecasting Metrics

```csv
horizon,n_predictions,mae,rmse,mape,p50_pinball,p90_pinball,mean_pinball,p50_coverage,p90_raw_coverage,p90_guarded_coverage,raw_interval_width,guarded_interval_width,raw_crossing_count,raw_crossing_rate,guarded_crossing_count,guarded_crossing_rate,fit_eval_ms,status
1,1622,2.2648100420601085,3.1452119260289284,0.05596365301420313,1.1324050210300542,0.6266040349513774,0.8795045279907159,0.4956843403205919,0.8995067817509248,0.8995067817509248,3.9998529731406807,3.9998529731406807,0,0.0,0,0.0,14472.749300000032,pass
5,1618,3.9666545156881985,5.389813585293006,0.09624385776970228,1.9833272578440992,1.1445493928892465,1.563938325366673,0.5024721878862793,0.8825710754017305,0.8825710754017305,7.118057842165502,7.118057842165502,0,0.0,0,0.0,14840.901600000507,pass
10,1613,4.31549093849647,5.8607548549379,0.10518634375818382,2.157745469248235,1.1952409066577319,1.6764931879529836,0.48357098574085555,0.8859268443893367,0.8859268443893367,7.917864401205117,7.917864401205117,0,0.0,0,0.0,16365.287099999478,pass
```

## Policy Metrics

```csv
experiment_id,dataset_split,model_name,policy_name,horizon,sla_violation,over_provisioning,under_provisioning,scaling_actions,average_capacity
qlr-policy-reactive,test,n/a,reactive_threshold,5,0.0006180469715698393,0.3505654283028808,1.1669491992555367e-05,43,0.8206896554033274
qlr-policy-lagged-tracking,test,n/a,lagged_target_tracking,5,0.47095179233621753,0.013447960038719798,0.014215703304689877,1616,0.469368153326469
qlr-policy-predictive,test,quantile_linear_regression,predictive_uncertainty_aware_qlr,5,0.033992583436341164,0.14741551987556142,0.0014025248340861335,587,0.6161488916339143
```
