# Full UA-MSTCN Broad Preflight Checks

- run_id: `full_ua_mstcn_broad_approval_20260428`
- status: `pass`
- approval planning only; no broad Full UA-MSTCN run executed
- manifest_service_count: `139`
- calibration_status: `pass`
- full_result_dir_exists: `False`
- metrics_csv_hash_before: `0fa3fdb810ca0a0f74592d3adc92102c7a0ca67ea02c2b8c8f22435537f873ab`
- metrics_csv_hash_after: `0fa3fdb810ca0a0f74592d3adc92102c7a0ca67ea02c2b8c8f22435537f873ab`

## Completed Checks

- [x] Broad batch-size calibration completed before approval planning.
- [x] Manifest covers the 139 broad services from the calibration slice.
- [x] Approval script did not import model code or start training.
- [x] Approval script did not generate held-out test windows.
- [x] Central `metrics.csv` hash is unchanged.
- [x] Full broad result directory was not created.

## Required Before Any Future Full Run

- [ ] Explicit approval for broad Full UA-MSTCN execution.
- [ ] Guarded broad-run entrypoint implemented and syntax-checked.
- [ ] Output directory absence, metrics hash, memory, disk, and CUDA rechecked immediately before launch.
- [ ] Manuscript conclusions remain frozen until broad results pass a separate evidence-to-claim review.

## Gate Result

- PASS: approval package is complete and no broad full-model run was executed.
