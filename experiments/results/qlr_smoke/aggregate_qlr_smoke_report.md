# Aggregate QLR Smoke Report

- run_id: `qlr_aggregate_smoke_20260427`
- series_path: `D:\Desktop\Cluster Computing\paper-workbench-full\Users\liujinchun\Downloads\skills_codex\paper-workbench\data\processed\cluster_series_v2018.csv`
- train_plus_validation_rows_used_for_fit: `9526`
- heldout_test_rows_used_for_evaluation: `1682`
- context_window: `60`
- horizons: `1, 5, 10`
- alpha: `0.0001`
- solver: `highs`
- metrics_csv: `D:\Desktop\Cluster Computing\paper-workbench-full\Users\liujinchun\Downloads\skills_codex\paper-workbench\experiments\results\qlr_smoke\aggregate_qlr_smoke_metrics.csv`
- status: `pass`

## Gate Checks

- P50/P90 predictions are nonempty.
- Prediction lengths align with `y_true`.
- P90 is guarded to be no lower than P50.
- MAE, pinball, coverage, and interval-width metrics are finite.
- Test rows are passed only to the evaluation side of the baseline API.

## Results

```csv
horizon,n_predictions,mae,rmse,mape,p50_pinball,p90_pinball,p50_coverage,p90_coverage,interval_width,non_crossing_violations,fit_eval_ms,status
1,1622,2.2648100420601085,3.1452119260289284,0.05596365301420313,1.1324050210300542,0.6266040349513774,0.4956843403205919,0.8995067817509248,3.9998529731406807,0,14065.125399999943,pass
5,1618,3.9666545156881985,5.389813585293006,0.09624385776970228,1.9833272578440992,1.1445493928892465,0.5024721878862793,0.8825710754017305,7.118057842165502,0,15008.188599999812,pass
10,1613,4.31549093849647,5.8607548549379,0.10518634375818382,2.157745469248235,1.1952409066577319,0.48357098574085555,0.8859268443893367,7.917864401205117,0,14798.566499999652,pass
```
