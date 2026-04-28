# QLR 139-Service Full Preflight

- run_id: `qlr_service_broad_preflight_20260427`
- status: `pass`
- preflight only; no full 139-service run executed
- service_count: `139`
- planned_output_dir: `D:\Desktop\Cluster Computing\paper-workbench-full\Users\liujinchun\Downloads\skills_codex\paper-workbench\experiments\results\qlr_service_broad`
- planned_num_workers: `2`
- metrics_csv_hash: `0fa3fdb810ca0a0f74592d3adc92102c7a0ca67ea02c2b8c8f22435537f873ab`
- full_result_dir_exists: `False`

## Resource Census

- os: `Windows-10-10.0.26200-SP0`
- python: `3.11.15`
- logical_cpu_count: `16`
- total_memory_bytes: `33409392640`
- free_memory_bytes: `14188077056`
- workspace_drive: `D:\`
- drive_total_bytes: `500098396160`
- drive_used_bytes: `443712163840`
- drive_free_bytes: `56386232320`

## Execution Guard

Full execution requires `--confirm-full-run I_APPROVE_QLR_139_SERVICE_FULL_RUN`.
The test split must remain evaluation-only; model fitting uses train+validation prefixes.
Central `metrics.csv` must remain unchanged by the broad service run.
Mixed or negative full-run outcomes must be preserved in the report.

## Gate Result

- PASS: guarded full-run entrypoint is ready, but the full run has not started.
