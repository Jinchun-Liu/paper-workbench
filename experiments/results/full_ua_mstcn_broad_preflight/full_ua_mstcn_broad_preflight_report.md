# Full UA-MSTCN Broad Guarded Preflight

- run_id: `full_ua_mstcn_broad_preflight_20260428`
- status: `pass`
- scope: preflight only; no broad Full UA-MSTCN training executed
- service_count: `139`
- approval_manifest_count: `139`
- batch_size: `1024`
- max_epochs: `20`
- patience: `4`
- metrics_csv_hash: `0fa3fdb810ca0a0f74592d3adc92102c7a0ca67ea02c2b8c8f22435537f873ab`
- full_output_dir_exists: `False`
- preflight_artifact_bytes: `29168`

## Boundary

This is a guarded entrypoint preflight. It does not train the broad model, does not create the full output directory, and does not update central `metrics.csv`.
The held-out test split is reserved for evaluation only; fitting uses train prefix and calibration/early stopping uses validation prefix.

## Future Execute Command

```powershell
& 'C:\Users\Liu Jinchun\miniconda3\envs\lora-cheongsam\python.exe' experiments\run_full_ua_mstcn_broad.py --config experiments\configs\default_v2018.yaml --execute --confirm-run-id full_ua_mstcn_broad_20260428
```

## Gate Result

- PASS: guarded broad-run entrypoint preflight passed; no full run was executed.
