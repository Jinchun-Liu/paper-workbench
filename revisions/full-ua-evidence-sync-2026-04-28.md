# Full UA-MSTCN Evidence Sync - 2026-04-28

## Scope

This sync records the evidence boundary after the guarded 139-service Full UA-MSTCN broad run. It is a response-letter and claim-boundary artifact. It does not change the manuscript headline conclusion by itself.

## Completed Run

- run_id: `full_ua_mstcn_broad_20260428`
- command: `experiments/run_full_ua_mstcn_broad.py --config experiments/configs/default_v2018.yaml --execute --confirm-run-id full_ua_mstcn_broad_20260428`
- output_dir: `experiments/results/full_ua_mstcn_broad/`
- status: `pass`
- service_count: `139`
- train_windows: `1111166`
- validation_windows: `230740`
- prediction_rows: `1384023`
- epochs_completed: `20`
- total_runtime_seconds: `1054.340`
- metrics_csv_hash_after: `0FA3FDB810CA0A0F74592D3ADC92102C2B8C8F22435537F873AB`

## Gate Evidence

- Test split use is recorded as held-out evaluation only.
- Fitting uses train prefix; early stopping and P90 calibration use validation prefix.
- Forecasting rows: `834`.
- Calibration rows: `417`.
- Policy metric rows: `417`.
- Policy series rows: `230601`.
- Raw crossing count: `0`.
- Calibrated crossing count: `0`.
- Forecasting and policy metrics are finite.
- Policy SLA violation values are within `[0, 1]`.
- Reactive, lagged, and predictive capacity series are nonnegative.

## Forecasting Summary

Mean test MAE over 139 services:

- h=1: `26.677`
- h=5: `36.834`
- h=10: `42.829`

Mean calibrated P90 coverage over 139 services:

- h=1: `0.918`
- h=5: `0.906`
- h=10: `0.901`

## Policy Summary

Mean 5-minute policy outcomes over 139 services:

- Full UA-MSTCN predictive: SLA `0.0219`, over-provisioning `52.07`, scaling actions `377.18`.
- Reactive: SLA `0.0173`, over-provisioning `56.20`, scaling actions `248.06`.
- Lagged tracking: SLA `0.4862`, over-provisioning `3.84`, scaling actions `1655.95`.

Interpretation: the Full UA-MSTCN predictive policy lowers mean over-provisioning relative to reactive, but has higher mean SLA violation and more scaling actions. This is mixed evidence, not superiority evidence.

## Execution Diagnostic

The first guarded launch reached training but failed in validation with CUDA OOM because the shared training function evaluated the full validation tensor at once. The empty failed output directory was verified and removed. The validation loss computation was then changed to batched evaluation, and the guarded command completed successfully. This diagnostic should remain recorded for reproducibility.

## Response-Letter Boundary

The response letter may now state that the broad Full UA-MSTCN run was executed and passed its gate. It must also state that:

- the result is mixed;
- no universal Full UA-MSTCN superiority claim is made;
- the manuscript headline conclusion remains unchanged unless a separate claim-calibration pass approves new wording;
- broad Full UA-MSTCN evidence does not erase the negative/mixed service-level boundary already emphasized in the manuscript.
