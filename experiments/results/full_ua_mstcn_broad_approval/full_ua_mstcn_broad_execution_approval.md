# Full UA-MSTCN Broad Full-Run Approval Package

- run_id: `full_ua_mstcn_broad_approval_20260428`
- status: `approval_plan_only`
- approval planning only; no broad Full UA-MSTCN run executed
- service_count: `139`
- calibration_dir: `D:\Desktop\Cluster Computing\paper-workbench-full\Users\liujinchun\Downloads\skills_codex\paper-workbench\experiments\results\full_ua_mstcn_broad_calibration`
- pilot_dir: `D:\Desktop\Cluster Computing\paper-workbench-full\Users\liujinchun\Downloads\skills_codex\paper-workbench\experiments\results\full_ua_mstcn_pilot`
- planned_full_result_dir: `D:\Desktop\Cluster Computing\paper-workbench-full\Users\liujinchun\Downloads\skills_codex\paper-workbench\experiments\results\full_ua_mstcn_broad`
- planned_full_result_dir_exists: `False`
- metrics_csv_hash_before: `0fa3fdb810ca0a0f74592d3adc92102c7a0ca67ea02c2b8c8f22435537f873ab`
- metrics_csv_hash_after: `0fa3fdb810ca0a0f74592d3adc92102c7a0ca67ea02c2b8c8f22435537f873ab`

## Approval Boundary

Calibration pass is not automatic approval. This package is an execution review artifact only.
No broad Full UA-MSTCN forecasting, policy, or superiority claim is supported by this artifact.
The manuscript headline conclusion remains unchanged, and mixed or negative future results must be preserved.

## Batch And Runtime Recommendation

- recommended_batch_size_from_calibration: `1024`
- conservative_validation_loss_batch_size: `512`
- planned_max_epochs: `20`
- planned_patience: `4`
- calibration_train_throughput_windows_per_second: `33606.7`
- calibration_peak_cuda_memory_bytes: `2555480064`
- planned_train_windows_total: `1111166`
- planned_validation_windows_total: `239080`
- planned_prediction_rows_total: `718769`
- safety_adjusted_wall_minutes_estimate: `23.3`
- safety_adjusted_artifact_mb_estimate: `295.3`
- safety_factor: `2.0`

## Current Resource Census

- os: `Windows-10-10.0.26200-SP0`
- python: `3.10.19 | packaged by Anaconda, Inc. | (main, Oct 21 2025, 16:41:31) [MSC v.1929 64 bit (AMD64)]`
- logical_cpu_count: `16`
- total_memory_bytes: `33409392640`
- free_memory_bytes: `11504234496`
- workspace_drive: `D:\`
- drive_total_bytes: `500098396160`
- drive_used_bytes: `443644526592`
- drive_free_bytes: `56453869568`

## Required Execution Rules

- Require explicit approval immediately before the broad full-model run.
- Re-check CPU, RAM, disk, CUDA availability, metrics hash, and output directory absence before execution.
- Use train prefix for fitting and validation prefix for early stopping/calibration.
- Use the held-out test split only for evaluation.
- Preserve raw P50/P90, calibrated or guarded P90, crossing diagnostics, calibration margins, and policy series.
- Reuse the existing service policy semantics, including service min_capacity=1.0 and max_step_change=1.0.
- Use median_container_request_cores only for replica conversion, with mean fallback only when median is non-positive.
- Do not update central `metrics.csv` from the broad service Full UA-MSTCN run.
- Do not change manuscript conclusions until a separate evidence-to-claim pass is approved.
