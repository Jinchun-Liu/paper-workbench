# QLR 139-Service Full Execution Approval

- run_id: `qlr_service_broad_approval_20260427`
- status: `approval_plan_only`
- approval planning only; no full 139-service run executed
- service_count: `139`
- broad_plan_manifest: `D:\Desktop\Cluster Computing\paper-workbench-full\Users\liujinchun\Downloads\skills_codex\paper-workbench\experiments\results\qlr_service_broad_plan\qlr_broad_run_manifest.csv`
- calibration_dir: `D:\Desktop\Cluster Computing\paper-workbench-full\Users\liujinchun\Downloads\skills_codex\paper-workbench\experiments\results\qlr_service_calibration_10`
- service_summary_csv: `D:\Desktop\Cluster Computing\paper-workbench-full\Users\liujinchun\Downloads\skills_codex\paper-workbench\data\processed\service_cohort_broad_summary_v2018.csv`
- recommended_full_run_workers_after_explicit_approval: `2`
- safety_factor: `2.0`
- metrics_csv_hash_before: `0fa3fdb810ca0a0f74592d3adc92102c7a0ca67ea02c2b8c8f22435537f873ab`
- metrics_csv_hash_after: `0fa3fdb810ca0a0f74592d3adc92102c7a0ca67ea02c2b8c8f22435537f873ab`
- full_result_dir_exists: `False`

## Approval Boundary

Full run has not been executed. Calibration pass is not automatic approval.
`Full UA-MSTCN` remains frozen, and the manuscript headline conclusion remains unchanged.
This artifact supports execution review only; it does not support a new experimental claim.

## Updated Resource Estimate From 10-Service Calibration

- source: `D:\Desktop\Cluster Computing\paper-workbench-full\Users\liujinchun\Downloads\skills_codex\paper-workbench\experiments\results\qlr_service_calibration_10\calibration_resource_trace.csv`
- calibration_service_count: `10`
- observed_workers: `0|1`
- mean_runtime_seconds_per_service: `55.8`
- max_runtime_seconds_per_service: `64.9`
- serial_139_estimated_minutes: `129.2`
- two_worker_estimated_wall_minutes: `64.6`
- safety_adjusted_artifact_bytes: `274244470`

## Current Resource Census

- os: `Windows-10-10.0.26200-SP0`
- python: `3.11.15`
- logical_cpu_count: `16`
- total_memory_bytes: `33409392640`
- free_memory_bytes: `16982048768`
- workspace_drive: `D:\`
- drive_total_bytes: `500098396160`
- drive_used_bytes: `443715862528`
- drive_free_bytes: `56382533632`

## Execution Rules For Any Future Full Run

- Require explicit approval before running the full 139-service command.
- Start with `--num-workers 2`; do not raise concurrency inside the approval step.
- Reuse the existing service policy semantics exactly, including service min_capacity=1.0 and max_step_change=1.0.
- Keep `median_container_request_cores` only for replica conversion, with mean fallback only when median is non-positive.
- Do not update central `metrics.csv` from the broad service run.
- Preserve raw and guarded P90 fields, raw crossing diagnostics, and guarded crossing diagnostics.
- Preserve mixed or negative outcomes; do not retune for a better story.
- Re-check memory, disk, metrics hash, and absence of the full output directory immediately before execution.
