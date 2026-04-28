# QLR Broad Preflight Checks

- run_id: `qlr_service_broad_approval_20260427`
- status: `pass`
- approval planning only; no full 139-service run executed
- manifest_service_count: `139`
- full_result_dir_exists: `False`
- metrics_csv_hash_before: `0fa3fdb810ca0a0f74592d3adc92102c7a0ca67ea02c2b8c8f22435537f873ab`
- metrics_csv_hash_after: `0fa3fdb810ca0a0f74592d3adc92102c7a0ca67ea02c2b8c8f22435537f873ab`

## Completed Checks

- [x] 10-service calibration completed before any full 139-service execution.
- [x] Calibration estimates, not pilot-only estimates, drive this approval package.
- [x] Approval manifest covers the intended broad services.
- [x] `metrics.csv` hash is unchanged during approval planning.
- [x] Full-result directory is not created by the approval script.
- [x] Approval package states that calibration pass is not automatic full-run approval.

## Required Before Any Future Full Run

- [ ] Explicit human approval for full 139-service execution.
- [ ] Re-check current CPU, memory, disk, metrics hash, and output directory absence.
- [ ] Run with `--num-workers 2` unless a new calibration justifies changing concurrency.
- [ ] Keep central `metrics.csv` unchanged for broad service artifacts.
- [ ] Keep the held deep-model path frozen.
- [ ] Preserve mixed or negative results in the report.

## Gate Result

- PASS: approval package is complete and no full run was executed.
