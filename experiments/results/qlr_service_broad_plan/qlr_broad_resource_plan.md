# QLR 139-Service Broad Resource Plan

- run_id: `qlr_service_broad_plan_20260427`
- status: `planning_only`
- planning only; no full 139-service run executed
- service_count: `139`
- service_csv: `D:\Desktop\Cluster Computing\paper-workbench-full\Users\liujinchun\Downloads\skills_codex\paper-workbench\data\processed\service_cohort_broad_v2018.csv`
- service_summary_csv: `D:\Desktop\Cluster Computing\paper-workbench-full\Users\liujinchun\Downloads\skills_codex\paper-workbench\data\processed\service_cohort_broad_summary_v2018.csv`
- pilot_dir: `D:\Desktop\Cluster Computing\paper-workbench-full\Users\liujinchun\Downloads\skills_codex\paper-workbench\experiments\results\qlr_service_pilot`
- target_workers_for_future_calibration: `2`
- safety_factor: `2.0`
- metrics_csv_hash_before: `0fa3fdb810ca0a0f74592d3adc92102c7a0ca67ea02c2b8c8f22435537f873ab`
- metrics_csv_hash_after: `0fa3fdb810ca0a0f74592d3adc92102c7a0ca67ea02c2b8c8f22435537f873ab`
- full_result_dir_exists: `False`

## Resource Census

- os: `Windows-10-10.0.26200-SP0`
- python: `3.11.15`
- logical_cpu_count: `16`
- total_memory_bytes: `33409392640`
- free_memory_bytes: `18516660224`
- workspace_drive: `D:\`
- drive_total_bytes: `500098396160`
- drive_used_bytes: `443691884544`
- drive_free_bytes: `56406511616`

## Estimates From Pilot

- pilot_service_count: `5`
- pilot_total_fit_eval_seconds: `214.0`
- mean_fit_eval_seconds_per_service: `42.8`
- max_fit_eval_seconds_per_service: `48.2`
- serial_139_estimated_minutes: `99.2`
- target_worker_estimated_wall_minutes: `49.6`
- safety_adjusted_csv_artifact_bytes: `265018845`

## Recommended Ladder

1. Run a 10-service calibration with the same QLR-only service script family and `--num-workers 2`.
2. Verify runtime, memory, raw/guarded P90 fields, policy metrics, and unchanged central `metrics.csv`.
3. Prepare the full run only if calibration passes and resource use remains stable.
4. Do not use this plan as authorization to start the full 139-service run automatically.

## Claim Boundary

This plan is a scheduling and resource artifact. It supports no new manuscript result and does not alter the current mixed service-pilot interpretation.
