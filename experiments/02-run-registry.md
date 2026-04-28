# Experiment Run Registry

This registry records revision-time experiment execution. Add new entries instead of rewriting previous runs.

## pre_qlr_freeze_20260427_180450

- status: `completed`
- recorded_at: `2026-04-27 18:04:50 +08:00`
- purpose: Freeze current workbench state before QLR implementation and smoke testing.
- artifact: `revisions/pre-qlr-freeze-2026-04-27.md`
- notes:
  - Dirty worktree was intentionally preserved.
  - Existing `review-freeze-2026-03-12` package was not overwritten.
  - Full UA-MSTCN and full 139-service experiments remain out of scope for this phase.

## qlr_aggregate_smoke_20260427

- status: `completed`
- completed_at: `2026-04-27 18:13:56 +08:00`
- purpose: Validate the reviewer-requested quantile linear regression baseline on the aggregate Alibaba series before any larger experiment.
- command:

```powershell
conda run -n paper-tcn python experiments/run_qlr_smoke.py --config experiments/configs/default_v2018.yaml
```

- expected_outputs:
  - `experiments/results/qlr_smoke/aggregate_qlr_smoke_metrics.csv`
  - `experiments/results/qlr_smoke/aggregate_qlr_smoke_report.md`
- observed_outputs:
  - `experiments/results/qlr_smoke/aggregate_qlr_smoke_metrics.csv`
  - `experiments/results/qlr_smoke/aggregate_qlr_smoke_report.md`
- result_summary:
  - `h=1`: MAE 2.265, P50 coverage 0.496, P90 coverage 0.900, non-crossing violations 0.
  - `h=5`: MAE 3.967, P50 coverage 0.502, P90 coverage 0.883, non-crossing violations 0.
  - `h=10`: MAE 4.315, P50 coverage 0.484, P90 coverage 0.886, non-crossing violations 0.
- gate:
  - P50/P90 predictions are nonempty.
  - Prediction lengths align with `y_true`.
  - P90 is not below P50 after the non-crossing guard.
  - MAE, pinball, coverage, and interval-width metrics are finite.
  - The test split is used only for evaluation.
- gate_decision: `pass`
- next_allowed_step: `QLR aggregate full forecasting and policy; do not skip directly to service full or Full UA-MSTCN.`

## qlr_aggregate_full_20260427

- status: `completed`
- completed_at: `2026-04-27 18:35:20 +08:00`
- purpose: Run the reviewer-requested quantile linear regression baseline through aggregate full forecasting and the matched predictive policy gate after the smoke pass.
- command:

```powershell
conda run -n paper-tcn python experiments/run_qlr_aggregate_full.py --config experiments/configs/default_v2018.yaml
```

- expected_outputs:
  - `experiments/results/qlr_aggregate_full/aggregate_qlr_forecasting_metrics.csv`
  - `experiments/results/qlr_aggregate_full/aggregate_qlr_predictions.csv`
  - `experiments/results/qlr_aggregate_full/aggregate_qlr_policy_metrics.csv`
  - `experiments/results/qlr_aggregate_full/aggregate_qlr_policy_series.csv`
  - `experiments/results/qlr_aggregate_full/aggregate_qlr_full_report.md`
- observed_outputs:
  - `experiments/results/qlr_aggregate_full/aggregate_qlr_forecasting_metrics.csv`
  - `experiments/results/qlr_aggregate_full/aggregate_qlr_predictions.csv`
  - `experiments/results/qlr_aggregate_full/aggregate_qlr_policy_metrics.csv`
  - `experiments/results/qlr_aggregate_full/aggregate_qlr_policy_series.csv`
  - `experiments/results/qlr_aggregate_full/aggregate_qlr_full_report.md`
- result_summary:
  - `h=1`: MAE 2.265, P50 coverage 0.496, guarded P90 coverage 0.900, raw crossings 0.
  - `h=5`: MAE 3.967, P50 coverage 0.502, guarded P90 coverage 0.883, raw crossings 0.
  - `h=10`: MAE 4.315, P50 coverage 0.484, guarded P90 coverage 0.886, raw crossings 0.
  - `qlr-policy-reactive`: SLA violation 0.000618, over-provisioning 0.350565, scaling actions 43.
  - `qlr-policy-lagged-tracking`: SLA violation 0.470952, over-provisioning 0.013448, scaling actions 1616.
  - `qlr-policy-predictive`: SLA violation 0.033993, over-provisioning 0.147416, scaling actions 587.
- gate:
  - Raw P90/P50 crossing count and rate are recorded before the guard.
  - Guarded P90 is computed as `max(raw_p90, p50)` and has zero crossing violations.
  - Forecasting and policy metrics are finite.
  - Policy uses the same aggregate simulator parameters as the UA-MSTCN-Lite policy path.
  - The report states that the held-out test split is used only for evaluation.
  - `metrics.csv` was updated conservatively with `qlr-*` experiment ids only.
- gate_decision: `pass`
- claim_boundary: `aggregate-only provisional evidence; manuscript headline claims are unchanged in this step.`
- next_allowed_step: `QLR service pilot on five representative services; still do not run full 139-service or Full UA-MSTCN.`

## qlr_service_pilot_20260427

- status: `completed`
- completed_at: `2026-04-27 18:50:38 +08:00`
- purpose: Run a fixed five-service QLR pilot with prefix-only service-selection trace before considering any broader service experiment.
- command:

```powershell
conda run -n paper-tcn python experiments/run_qlr_service_pilot.py --config experiments/configs/default_v2018.yaml --num-workers 1
```

- selected_services:
  - `low_load_low_burst`: `app_2557`
  - `low_load_high_burst`: `app_7264`
  - `high_load_low_burst`: `app_1675`
  - `high_load_high_burst`: `app_3665`
  - `median_anchor`: `app_521`
- expected_outputs:
  - `experiments/results/qlr_service_pilot/service_selection_profile.csv`
  - `experiments/results/qlr_service_pilot/service_qlr_forecasting_raw.csv`
  - `experiments/results/qlr_service_pilot/service_qlr_forecasting_summary.csv`
  - `experiments/results/qlr_service_pilot/service_qlr_predictions.csv`
  - `experiments/results/qlr_service_pilot/service_qlr_policy_raw.csv`
  - `experiments/results/qlr_service_pilot/service_qlr_policy_summary.csv`
  - `experiments/results/qlr_service_pilot/service_qlr_policy_delta_by_service.csv`
  - `experiments/results/qlr_service_pilot/service_qlr_policy_series.csv`
  - `experiments/results/qlr_service_pilot/qlr_service_pilot_report.md`
- observed_outputs:
  - `experiments/results/qlr_service_pilot/service_selection_profile.csv`
  - `experiments/results/qlr_service_pilot/service_qlr_forecasting_raw.csv`
  - `experiments/results/qlr_service_pilot/service_qlr_forecasting_summary.csv`
  - `experiments/results/qlr_service_pilot/service_qlr_predictions.csv`
  - `experiments/results/qlr_service_pilot/service_qlr_policy_raw.csv`
  - `experiments/results/qlr_service_pilot/service_qlr_policy_summary.csv`
  - `experiments/results/qlr_service_pilot/service_qlr_policy_delta_by_service.csv`
  - `experiments/results/qlr_service_pilot/service_qlr_policy_series.csv`
  - `experiments/results/qlr_service_pilot/qlr_service_pilot_report.md`
- result_summary:
  - Forecasting MAE mean by horizon: `h=1` 17.619, `h=5` 29.047, `h=10` 35.662.
  - Raw crossing counts by horizon: `h=1` 22, `h=5` 62, `h=10` 47.
  - Guarded crossing counts by horizon: all 0.
  - Policy means: reactive SLA 0.015385 / over-provisioning 50.223 / actions 331.6.
  - Policy means: QLR predictive SLA 0.019471 / over-provisioning 52.958 / actions 366.4.
  - Policy means: lagged tracking SLA 0.487861 / over-provisioning 5.109 / actions 1661.2.
- gate:
  - Selection trace contains exactly five fixed services and all required roles.
  - Selection descriptors are computed from train+validation prefixes only; full-span summary descriptors are metadata-only.
  - Raw P90 and guarded P90 fields are both written to artifacts.
  - Raw crossing count/rate are recorded, and guarded crossing is zero.
  - Existing service policy semantics and parameters are reused.
  - `median_container_request_cores` is used only for replica conversion; no selected service required fallback.
  - The held-out test split is used only for evaluation.
  - `metrics.csv` hash remained unchanged during the pilot.
- gate_decision: `pass`
- claim_boundary: `service-level QLR pilot evidence only; mixed policy result; manuscript headline claims remain unchanged.`
- next_allowed_step: `Prepare a full 139-service QLR resource and execution plan only; do not automatically start the full run or Full UA-MSTCN.`

## qlr_service_broad_plan_20260427

- status: `planned_only`
- completed_at: `2026-04-27 18:57:31 +08:00`
- purpose: Prepare a resource estimate, run manifest, and gate checklist for a possible future 139-service QLR run without executing the full run.
- command:

```powershell
conda run -n paper-tcn python experiments/plan_qlr_service_broad.py --config experiments/configs/default_v2018.yaml
```

- expected_outputs:
  - `experiments/results/qlr_service_broad_plan/qlr_broad_resource_plan.md`
  - `experiments/results/qlr_service_broad_plan/qlr_broad_run_manifest.csv`
  - `experiments/results/qlr_service_broad_plan/qlr_broad_gate_checklist.md`
  - `experiments/results/qlr_service_broad_plan/qlr_broad_dry_run_report.md`
- observed_outputs:
  - `experiments/results/qlr_service_broad_plan/qlr_broad_resource_plan.md`
  - `experiments/results/qlr_service_broad_plan/qlr_broad_run_manifest.csv`
  - `experiments/results/qlr_service_broad_plan/qlr_broad_gate_checklist.md`
  - `experiments/results/qlr_service_broad_plan/qlr_broad_dry_run_report.md`
- resource_summary:
  - Machine snapshot: 16 logical CPUs, about 18.5 GB free memory, about 56.4 GB free on `D:\`.
  - Pilot-derived mean fit/eval time: 42.8 seconds/service.
  - Estimated serial 139-service fit/eval time: 99.2 minutes.
  - Estimated future wall time at 2 workers: 49.6 minutes.
  - Safety-adjusted CSV artifact estimate: 265,018,845 bytes.
- gate:
  - Manifest contains exactly 139 services.
  - The dry-run report states: `planning only; no full 139-service run executed`.
  - `experiments/results/qlr_service_broad/` was not created.
  - `metrics.csv` hash remained unchanged.
  - The plan script does not import the held deep-model path.
  - No manuscript conclusion was updated.
- gate_decision: `pass`
- claim_boundary: `planning artifact only; supports scheduling and resource review but no new experimental claim.`
- next_allowed_step: `Design and run a 10-service calibration only if explicitly requested; do not automatically start full 139-service or Full UA-MSTCN.`

## qlr_service_calibration_10_20260427

- status: `pass`
- completed_at: `2026-04-27 19:10:47 +08:00`
- purpose: Run a fixed 10-service QLR calibration to validate `--num-workers 2` runtime, artifact growth, schema stability, policy metrics, and gate checks before any broader service run.
- command:

```powershell
conda run -n paper-tcn python experiments/run_qlr_service_calibration.py --config experiments/configs/default_v2018.yaml --num-workers 2
```

- fixed_services:
  - `app_2557`
  - `app_7264`
  - `app_1675`
  - `app_3665`
  - `app_521`
  - `app_3422`
  - `app_141`
  - `app_2128`
  - `app_8205`
  - `app_7227`
- selection_roles:
  - `pilot_low_load_low_burst`: `app_2557`
  - `pilot_low_load_high_burst`: `app_7264`
  - `pilot_high_load_low_burst`: `app_1675`
  - `pilot_high_load_high_burst`: `app_3665`
  - `pilot_median_anchor`: `app_521`
  - `cal_lowest_load_guard`: `app_3422`
  - `cal_highest_load_guard`: `app_141`
  - `cal_lowest_burst_guard`: `app_2128`
  - `cal_highest_burst_guard`: `app_8205`
  - `cal_peak_to_mean_guard`: `app_7227`
- expected_outputs:
  - `experiments/results/qlr_service_calibration_10/calibration_selection_profile.csv`
  - `experiments/results/qlr_service_calibration_10/service_qlr_forecasting_raw.csv`
  - `experiments/results/qlr_service_calibration_10/service_qlr_forecasting_summary.csv`
  - `experiments/results/qlr_service_calibration_10/service_qlr_predictions.csv`
  - `experiments/results/qlr_service_calibration_10/service_qlr_policy_raw.csv`
  - `experiments/results/qlr_service_calibration_10/service_qlr_policy_summary.csv`
  - `experiments/results/qlr_service_calibration_10/service_qlr_policy_delta_by_service.csv`
  - `experiments/results/qlr_service_calibration_10/service_qlr_policy_series.csv`
  - `experiments/results/qlr_service_calibration_10/calibration_resource_trace.csv`
  - `experiments/results/qlr_service_calibration_10/qlr_service_calibration_report.md`
- observed_outputs:
  - `experiments/results/qlr_service_calibration_10/calibration_selection_profile.csv`
  - `experiments/results/qlr_service_calibration_10/service_qlr_forecasting_raw.csv`
  - `experiments/results/qlr_service_calibration_10/service_qlr_forecasting_summary.csv`
  - `experiments/results/qlr_service_calibration_10/service_qlr_predictions.csv`
  - `experiments/results/qlr_service_calibration_10/service_qlr_policy_raw.csv`
  - `experiments/results/qlr_service_calibration_10/service_qlr_policy_summary.csv`
  - `experiments/results/qlr_service_calibration_10/service_qlr_policy_delta_by_service.csv`
  - `experiments/results/qlr_service_calibration_10/service_qlr_policy_series.csv`
  - `experiments/results/qlr_service_calibration_10/calibration_resource_trace.csv`
  - `experiments/results/qlr_service_calibration_10/qlr_service_calibration_report.md`
- result_summary:
  - Forecasting MAE mean by horizon: `h=1` 21.192, `h=5` 34.083, `h=10` 41.949.
  - Raw crossing counts by horizon: `h=1` 84, `h=5` 68, `h=10` 54.
  - Guarded crossing counts by horizon: all 0.
  - Policy means: reactive SLA 0.015325 / over-provisioning 56.090 / actions 300.6.
  - Policy means: QLR predictive SLA 0.022776 / over-provisioning 59.613 / actions 403.8.
  - Policy means: lagged tracking SLA 0.484615 / over-provisioning 6.594 / actions 1659.3.
  - Resource trace covers 10 services with workers `0` and `1`; generated calibration artifacts total about 9.9 MB.
- gate:
  - Selection trace contains exactly ten fixed services and all required roles.
  - Selection descriptors are computed from train+validation prefixes only; full-span summary descriptors are not used for service selection.
  - Raw P90 and guarded P90 fields are both written to artifacts.
  - Raw crossing count/rate are recorded, and guarded crossing is zero.
  - Forecasting and policy metrics are finite.
  - Policy SLA violation remains in `[0, 1]`, and capacity is non-negative.
  - Service policy semantics and parameters match the existing service policy path.
  - `median_container_request_cores` is used only for replica conversion; no selected service required fallback.
  - The held-out test split is used only for evaluation.
  - `metrics.csv` hash remained unchanged during calibration.
  - `experiments/results/qlr_service_broad/` was not created.
  - Calibration pass does not authorize an automatic full 139-service run.
- gate_decision: `pass`
- claim_boundary: `calibration evidence only; mixed policy result; manuscript headline claims remain unchanged.`
- next_allowed_step: `Prepare an explicit approval plan for any future full 139-service run; do not automatically start full 139-service or Full UA-MSTCN.`

## qlr_service_broad_approval_20260427

- status: `approval_plan_only`
- completed_at: `2026-04-27 23:14:45 +08:00`
- purpose: Prepare an auditable approval package for a possible future full 139-service QLR run without executing the full run.
- command:

```powershell
conda run -n paper-tcn python experiments/plan_qlr_service_broad_approval.py --config experiments/configs/default_v2018.yaml
```

- expected_outputs:
  - `experiments/results/qlr_service_broad_approval/qlr_broad_execution_approval.md`
  - `experiments/results/qlr_service_broad_approval/qlr_broad_execution_manifest.csv`
  - `experiments/results/qlr_service_broad_approval/qlr_broad_preflight_checks.md`
  - `experiments/results/qlr_service_broad_approval/qlr_broad_resource_update_from_calibration.md`
- observed_outputs:
  - `experiments/results/qlr_service_broad_approval/qlr_broad_execution_approval.md`
  - `experiments/results/qlr_service_broad_approval/qlr_broad_execution_manifest.csv`
  - `experiments/results/qlr_service_broad_approval/qlr_broad_preflight_checks.md`
  - `experiments/results/qlr_service_broad_approval/qlr_broad_resource_update_from_calibration.md`
- resource_update:
  - Estimate source is the 10-service calibration resource trace, not the earlier 5-service pilot alone.
  - Calibration mean runtime: 55.8 seconds/service.
  - Estimated 139-service serial runtime: 129.2 minutes.
  - Estimated wall time at `--num-workers 2`: 64.6 minutes.
  - Safety-adjusted artifact estimate: 274,244,470 bytes.
  - Current resource census: 16 logical CPUs, about 16.98 GB free memory, about 56.38 GB free on `D:\`.
- gate:
  - Approval manifest contains exactly 139 services.
  - Approval report states: `approval planning only; no full 139-service run executed`.
  - `experiments/results/qlr_service_broad/` was not created.
  - `metrics.csv` hash remained unchanged.
  - The approval script does not import the held deep-model path.
  - The approval package records that calibration pass is not automatic full-run approval.
  - The approval package keeps central `metrics.csv` unchanged for any future broad service artifacts.
  - No manuscript conclusion was updated.
- gate_decision: `pass`
- claim_boundary: `execution approval artifact only; supports future run review but no new experimental claim.`
- next_allowed_step: `Request explicit approval before any full 139-service execution; keep Full UA-MSTCN frozen.`

## qlr_service_broad_preflight_20260427

- status: `pass`
- completed_at: `2026-04-27 23:30:42 +08:00`
- purpose: Add and verify a guarded full 139-service QLR entrypoint, using preflight-only mode to confirm scope, resources, and execution guard before any full run.
- command:

```powershell
conda run -n paper-tcn python experiments/run_qlr_service_broad.py --config experiments/configs/default_v2018.yaml --preflight-only --num-workers 2
```

- expected_outputs:
  - `experiments/results/qlr_service_broad_preflight/qlr_service_broad_preflight_profile.csv`
  - `experiments/results/qlr_service_broad_preflight/qlr_service_broad_preflight_report.md`
- observed_outputs:
  - `experiments/results/qlr_service_broad_preflight/qlr_service_broad_preflight_profile.csv`
  - `experiments/results/qlr_service_broad_preflight/qlr_service_broad_preflight_report.md`
- guard:
  - Full execution requires explicit token `I_APPROVE_QLR_139_SERVICE_FULL_RUN`.
  - Default safe path is `--preflight-only`.
  - Planned broad run uses `--num-workers 2` unless a later approved calibration changes concurrency.
  - Central `metrics.csv` must remain unchanged by the broad service run.
  - Mixed or negative outcomes must be preserved in the report.
- gate:
  - Preflight profile contains exactly 139 services.
  - Preflight report states: `preflight only; no full 139-service run executed`.
  - `experiments/results/qlr_service_broad/` was not created.
  - `metrics.csv` hash remained unchanged.
  - The guarded broad script does not import the held deep-model path.
  - The test split is explicitly evaluation-only in the preflight report.
  - A no-token full-run invocation refused execution before creating the full output directory.
- gate_decision: `pass`
- claim_boundary: `protected-entrypoint and preflight artifact only; no full 139-service evidence.`
- next_allowed_step: `Only run full 139-service after explicit approval with the required confirmation token; keep Full UA-MSTCN frozen.`

## qlr_evidence_sync_20260427

- status: `writing_support_only`
- completed_at: `2026-04-27 23:35:22 +08:00`
- purpose: Consolidate completed QLR aggregate, service pilot, service calibration, broad approval, and guarded preflight artifacts into a conservative manuscript/response-letter evidence map.
- command: manual artifact synthesis from verified CSV and Markdown reports; no model run.
- observed_outputs:
  - `revisions/qlr-evidence-sync-2026-04-27.md`
- evidence_summary:
  - Aggregate QLR full is passed evidence and can be discussed as aggregate QLR evidence.
  - Service pilot and 10-service calibration are bounded evidence only; they remain mixed and weaker than reactive on mean service policy metrics.
  - Broad 139-service approval and preflight are execution-readiness artifacts only, not broad service results.
  - Test split discipline and prefix-only service selection are restated for response-letter use.
- gate:
  - No full 139-service run was executed.
  - `experiments/results/qlr_service_broad/` remains absent.
  - No central metrics update was made by this writing sync.
  - Manuscript headline conclusions remain unchanged.
- gate_decision: `pass`
- claim_boundary: `writing support only; no new experimental claim.`
- next_allowed_step: `Use the sync pack for response-letter and conservative manuscript boundary edits, or explicitly approve full 139-service execution before running the broad experiment.`

## qlr_response_and_boundary_edits_20260427

- status: `drafted`
- completed_at: `2026-04-27 23:42:33 +08:00`
- purpose: Convert the QLR evidence sync into conservative response-letter text and low-risk manuscript boundary edits without changing the headline conclusion.
- observed_outputs:
  - `revisions/response-letter.md`
  - `manuscript/sections/experiments.tex`
  - `manuscript/sections/results.tex`
- edit_summary:
  - Added a response-letter draft for the QLR baseline request, service-level boundary interpretation, and broad-run execution boundary.
  - Added QLR protocol wording: train+validation-only fitting, test evaluation only, raw P90 retention, guarded P90, and service QLR as bounded audit evidence.
  - Added an aggregate QLR baseline table and conservative aggregate QLR policy interpretation.
- gate:
  - No full 139-service run was executed.
  - `experiments/results/qlr_service_broad/` remains absent.
  - Central `metrics.csv` hash remained unchanged.
  - Abstract and conclusion were not changed.
  - No broad 139-service QLR performance claim was inserted.
- compile_check:
  - `latexmk` was blocked by the local MiKTeX environment because Perl is unavailable.
  - Direct `pdflatex` was blocked before manuscript body processing because `cuted.sty` is unavailable.
  - Static text checks found no QLR edits in the abstract or conclusion and no broad 139-service QLR performance claim.
- gate_decision: `blocked_by_local_latex_environment`
- claim_boundary: `response-letter draft and conservative manuscript boundary edits only.`
- next_allowed_step: `Restore the local LaTeX template dependencies or use the previously verified clean compile environment, then rerun compile and QA before resubmission.`

## revision_portal_upload_requirements_20260427

- status: `captured`
- completed_at: `2026-04-27 23:52:45 +08:00`
- purpose: Align the workbench with the journal revision upload page requirements.
- source_instruction: user-provided submission portal text.
- observed_outputs:
  - `submission/revision-upload-checklist.md`
  - `submission/checklist.md`
  - `revisions/response-letter.md`
  - `revisions/revision-plan.md`
- captured_requirements:
  - The original submitting author must upload the revision.
  - The point-by-point response must be uploaded as a PDF.
  - The response PDF must describe additional experiments.
  - The response PDF must provide detailed rebuttal for criticisms or requested revisions not adopted.
  - Changed files, including the manuscript, must be uploaded again.
  - The clean revised manuscript must not include tracked changes.
  - A highlighted or marked-up manuscript, if needed, belongs in the related-file section.
  - Extension requests must include the submission ID.
- gate:
  - No experiment was run.
  - No central metrics file changed.
  - `experiments/results/qlr_service_broad/` remains absent.
- gate_decision: `pass`
- claim_boundary: `submission logistics and compliance only.`
- next_allowed_step: `Use the upload checklist during final packaging; export the point-by-point response to PDF after compile dependencies are restored.`

## latex_environment_revision_pdf_export_20260427

- status: `pass`
- completed_at: `2026-04-28 00:25:00 +08:00`
- purpose: Restore the local LaTeX build path and export the current revised manuscript PDF plus the QLR-focused response PDF required by the revision portal.
- environment_actions:
  - Installed Perl into the `paper-tcn` conda environment so `latexmk` can run locally.
  - Installed/restored MiKTeX `sttools` so `cuted.sty` is available.
  - Generated `natbib.sty` from the CTAN `natbib.ins`/`natbib.dtx` source after removing a temporary bad 404 stub, then refreshed the MiKTeX file database.
- commands:

```powershell
conda run -n paper-tcn latexmk -gg -pdf -interaction=nonstopmode -halt-on-error main.tex
conda run -n paper-tcn latexmk -gg -pdf -interaction=nonstopmode -halt-on-error response-letter.tex
```

- observed_outputs:
  - `manuscript/main.pdf`
  - `revisions/response-letter.pdf`
  - `revisions/response-letter.tex`
  - `.gitattributes`
- gate:
  - Revised manuscript PDF compiled successfully from current LaTeX source.
  - Response PDF compiled successfully from the QLR-focused response-letter source.
  - Response letter states that test split use is evaluation-only and separates completed QLR evidence from broad-run approval/preflight artifacts.
  - Static markup scan found no obvious tracked-change commands in manuscript `.tex` source.
  - `experiments/results/qlr_service_broad/` remains absent.
  - `metrics.csv` hash remained `0FA3FDB810CA0A0F74592D3ADC92102C7A0CA67EA02C2B8C8F22435537F873AB`.
  - `git diff --check` now reports only the pre-existing `HANDOFF.md:430` trailing whitespace after marking PDFs as binary.
- gate_decision: `pass_for_current_qlr_response_pack`
- claim_boundary: `compile and submission-logistics artifact only; no new experiment and no manuscript headline conclusion change.`
- next_allowed_step: `Expand the response PDF to cover every reviewer comment before upload, while keeping full 139-service QLR and Full UA-MSTCN frozen unless explicitly approved.`

## full_point_by_point_response_20260428

- status: `pass`
- completed_at: `2026-04-28 00:55:00 +08:00`
- purpose: Expand the response letter from the QLR-focused draft into a full point-by-point response covering the mapped R1/R2/R3 comments, then rebuild the manuscript and response PDF.
- observed_outputs:
  - `revisions/response-letter.md`
  - `revisions/response-letter.tex`
  - `revisions/response-letter.pdf`
  - `manuscript/main.pdf`
  - `submission/checklist.md`
  - `submission/revision-upload-checklist.md`
- manuscript_edits:
  - Abstract now maps P90 coverage values to 1-, 5-, and 10-minute horizons.
  - Method now states that `UA-MSTCN-Lite` is a paper-specific lightweight surrogate and documents its feature extractor, random-forest learner, quantile construction, calibration, clipping, and pooled transfer route.
  - Service-cohort limitation wording now appears with the selection rule and points to Table 2.
  - Table/Figure captions were updated for Table 4, Figure 1, Figure 5, and the quantile-coverage figure.
- response_scope:
  - Covers R1.1--R1.12, R2.1--R2.5, and R3.1--R3.4.
  - Describes additional QLR experiments and artifacts.
  - Provides conservative rationale for the partially adopted public-URL request.
  - States that full 139-service QLR has not been executed and remains approval-gated.
- compile_check:
  - `conda run -n paper-tcn latexmk -gg -pdf -interaction=nonstopmode -halt-on-error main.tex` passed.
  - `conda run -n paper-tcn latexmk -gg -pdf -interaction=nonstopmode -halt-on-error response-letter.tex` passed.
  - `manuscript/main.pdf`: 21 pages.
  - `revisions/response-letter.pdf`: 7 pages.
- gate:
  - Response PDF contains R1/R2/R3 point-by-point headings.
  - Response PDF states that the held-out test split is evaluation-only for QLR.
  - Response PDF separates completed aggregate QLR evidence from broad approval/preflight artifacts.
  - `experiments/results/qlr_service_broad/` remains absent.
  - `metrics.csv` hash remained `0FA3FDB810CA0A0F74592D3ADC92102C7A0CA67EA02C2B8C8F22435537F873AB`.
- gate_decision: `pass`
- claim_boundary: `response and low-risk manuscript clarification only; no new experiment and no broad QLR claim.`
- next_allowed_step: `Prepare changed-file upload manifest/source-package refresh; do not run full 139-service QLR or Full UA-MSTCN without explicit approval.`

## revision_changed_files_and_source_package_20260428

- status: `pass`
- completed_at: `2026-04-28 01:05:00 +08:00`
- purpose: Prepare the upload-facing changed-file manifest and refresh the self-contained Cluster Computing source package after the latest manuscript edits.
- command:

```powershell
conda run -n paper-tcn python scripts\build_submission_package.py --verify --archive
```

- observed_outputs:
  - `submission/revision-changed-files-manifest.md`
  - `submission/source-package/cluster-computing/`
  - `submission/source-package/cluster-computing.zip`
- source_package_result:
  - Staged 31 files.
  - Dependencies: 10 tex, 1 bib, 17 figures, 2 static extras.
  - Class: `sn-jnl`.
  - Clean-dir `latexmk` verification passed.
- gate:
  - Required main uploads are identified: clean manuscript PDF, point-by-point response PDF, and refreshed source package zip.
  - Changed manuscript source, response/revision records, QLR scripts, and QLR artifact directories are listed.
  - The manifest explicitly says `experiments/results/qlr_service_broad/` does not exist and must not be uploaded or described as a completed result.
  - `metrics.csv` hash remained `0FA3FDB810CA0A0F74592D3ADC92102C7A0CA67EA02C2B8C8F22435537F873AB`.
- gate_decision: `pass`
- claim_boundary: `submission packaging only; no new scientific claim.`
- next_allowed_step: `Final QA pass over compiled PDFs and portal fields; keep full 139-service QLR and Full UA-MSTCN frozen unless explicitly approved.`

## qlr_service_broad_full_20260428

- status: `pass`
- completed_at: `2026-04-28 11:55:31 +08:00`
- purpose: Execute the explicitly approved guarded full 139-service QLR broad run after preflight and calibration gates.
- command:

```powershell
conda run -n paper-tcn python experiments\run_qlr_service_broad.py --config experiments\configs\default_v2018.yaml --num-workers 2 --confirm-full-run I_APPROVE_QLR_139_SERVICE_FULL_RUN
```

- observed_outputs:
  - `experiments/results/qlr_service_broad/broad_service_profile.csv`
  - `experiments/results/qlr_service_broad/service_qlr_forecasting_raw.csv`
  - `experiments/results/qlr_service_broad/service_qlr_forecasting_summary.csv`
  - `experiments/results/qlr_service_broad/service_qlr_predictions.csv`
  - `experiments/results/qlr_service_broad/service_qlr_policy_raw.csv`
  - `experiments/results/qlr_service_broad/service_qlr_policy_summary.csv`
  - `experiments/results/qlr_service_broad/service_qlr_policy_delta_by_service.csv`
  - `experiments/results/qlr_service_broad/service_qlr_policy_series.csv`
  - `experiments/results/qlr_service_broad/broad_resource_trace.csv`
  - `experiments/results/qlr_service_broad/broad_progress.csv`
  - `experiments/results/qlr_service_broad/qlr_service_broad_report.md`
- runtime:
  - Broad progress heartbeat completed `139/139` services.
  - Last service completion elapsed time: `3959.261` seconds.
  - Total broad artifact size: `132565795` bytes.
- gate:
  - `qlr_service_broad_report.md` status is `pass`.
  - Profile, forecasting, prediction, policy, and resource trace artifacts each cover exactly `139` services.
  - Forecast rows: `417`; prediction rows: `693749`; policy rows: `417`; policy-series rows: `231296`.
  - Raw and guarded P90 fields are present in forecast and prediction artifacts.
  - Raw P90 crossing count is recorded: `8963` total raw crossings.
  - Guarded P90 crossing count is `0`.
  - Forecasting and policy numeric fields are finite.
  - Policy SLA violation values are within `[0, 1]`.
  - Reactive, lagged, and QLR-predictive capacity series are nonnegative.
  - Report explicitly states that the test split is evaluation-only.
  - `experiments/results/metrics.csv` hash remained `0FA3FDB810CA0A0F74592D3ADC92102C7A0CA67EA02C2B8C8F22435537F873AB`.
- headline_numbers:
  - Forecast MAE means by horizon: `19.207` at h=1, `32.959` at h=5, `42.095` at h=10.
  - P90 guarded coverage means by horizon: `0.9028`, `0.8963`, `0.8868`.
  - Policy means: reactive SLA `0.0173`, QLR predictive SLA `0.0206`; reactive over-provisioning `56.31`, QLR predictive over-provisioning `54.71`.
- gate_decision: `pass`
- claim_boundary: `full broad QLR evidence is now available, but it is mixed policy evidence and does not automatically change the manuscript headline conclusion. Response/upload artifacts that said the full broad run was not executed are now stale and must be refreshed before submission.`
- next_allowed_step: `Start Full UA-MSTCN Stage 1 smoke only; do not promote Full UA-MSTCN claims or rewrite the main conclusion until smoke/pilot/main evidence is reviewed.`

## full_ua_mstcn_smoke_20260428

- status: `pass`
- completed_at: `2026-04-28 12:02:27 +08:00`
- purpose: Start the Full UA-MSTCN scale ladder after the full QLR broad gate by running a Stage 1 PyTorch smoke test on the first 2,000 aggregate samples.
- command:

```powershell
& 'C:\Users\Liu Jinchun\miniconda3\envs\lora-cheongsam\python.exe' experiments\run_full_ua_mstcn_smoke.py --series-csv data\processed\cluster_series_v2018.csv --output-dir experiments\results\full_ua_mstcn_smoke --limit-rows 2000 --epochs 3 --batch-size 256
```

- implementation_outputs:
  - `experiments/models/full_ua_mstcn.py`
  - `experiments/run_full_ua_mstcn_smoke.py`
  - `experiments/environment-full-ua-mstcn.yml`
- observed_outputs:
  - `experiments/results/full_ua_mstcn_smoke/full_ua_mstcn_smoke_metrics.csv`
  - `experiments/results/full_ua_mstcn_smoke/full_ua_mstcn_smoke_predictions.csv`
  - `experiments/results/full_ua_mstcn_smoke/full_ua_mstcn_smoke_status.json`
  - `experiments/results/full_ua_mstcn_smoke/full_ua_mstcn_smoke_report.md`
- environment:
  - Python: `3.10.19`
  - PyTorch: `2.5.1+cu121`
  - CUDA available: `true`
  - Device: `NVIDIA GeForce RTX 4070 Ti SUPER`
  - Peak CUDA memory: `2219642880` bytes.
- gate:
  - Smoke report status is `pass`.
  - Model is a real PyTorch causal multi-scale TCN, separate from the existing `UA-MSTCN-Lite` surrogate.
  - Output shape is `[291, 3, 2]` for the test split.
  - Non-crossing is enforced by `p90 = p50 + softplus(delta90)`.
  - Crossing count is `0` for validation and test smoke metrics.
  - Training loss decreased from `0.261530` to `0.201443`.
  - Test split is recorded as evaluation-only.
  - Central `metrics.csv` was not updated.
- gate_decision: `pass_for_stage_1_smoke`
- claim_boundary: `Full UA-MSTCN has been started and smoke-tested only. These artifacts do not support manuscript performance claims, broad full-model conclusions, or response-letter superiority claims.`
- next_allowed_step: `Design a Full UA-MSTCN aggregate-full + 5-service pilot gate before any broad full-model run.`

## response_letter_full_qlr_refresh_20260428

- status: `pass`
- completed_at: `2026-04-28 12:08:00 +08:00`
- purpose: Refresh the point-by-point response after the approved full 139-service QLR run and Full UA-MSTCN smoke so the upload-facing PDF no longer says the broad QLR run was unexecuted.
- observed_outputs:
  - `revisions/response-letter.md`
  - `revisions/response-letter.tex`
  - `revisions/response-letter.pdf`
  - `submission/checklist.md`
  - `submission/revision-upload-checklist.md`
  - `submission/revision-changed-files-manifest.md`
- compile_check:
  - `conda run -n paper-tcn latexmk -gg -pdf -interaction=nonstopmode -halt-on-error response-letter.tex` passed.
  - `revisions/response-letter.pdf`: 8 pages, `163783` bytes.
- gate:
  - Response letter now states that the full 139-service QLR run was executed after explicit approval and passed its gate.
  - Response letter records the mixed service-policy outcome rather than claiming QLR superiority.
  - Response letter states that Full UA-MSTCN Stage 1 smoke is not manuscript-facing performance evidence.
  - Manuscript headline conclusion remains unchanged.
- gate_decision: `pass`
- claim_boundary: `response upload artifact refreshed only; manuscript tables and main conclusion were not promoted to full broad QLR or Full UA-MSTCN claims.`
- next_allowed_step: `If the authors want full broad QLR in the manuscript tables, make a separate conservative manuscript/table update and rebuild the source package.`

## full_ua_mstcn_pilot_20260428

- status: `pass`
- completed_at: `2026-04-28 12:33:23 +08:00`
- purpose: Run the Full UA-MSTCN Stage 2 pilot after Stage 1 smoke: aggregate full-series model plus a fixed five-service service-pilot model with validation-only P90 calibration.
- command:

```powershell
& 'C:\Users\Liu Jinchun\miniconda3\envs\lora-cheongsam\python.exe' experiments\run_full_ua_mstcn_pilot.py --config experiments\configs\default_v2018.yaml --max-epochs 15 --patience 4 --batch-size 512
```

- implementation_outputs:
  - `experiments/models/full_ua_mstcn.py`
  - `experiments/run_full_ua_mstcn_pilot.py`
- observed_outputs:
  - `experiments/results/full_ua_mstcn_pilot/full_ua_mstcn_pilot_selection_profile.csv`
  - `experiments/results/full_ua_mstcn_pilot/full_ua_mstcn_pilot_forecasting_metrics.csv`
  - `experiments/results/full_ua_mstcn_pilot/full_ua_mstcn_pilot_predictions.csv`
  - `experiments/results/full_ua_mstcn_pilot/full_ua_mstcn_pilot_calibration.csv`
  - `experiments/results/full_ua_mstcn_pilot/full_ua_mstcn_pilot_policy_metrics.csv`
  - `experiments/results/full_ua_mstcn_pilot/full_ua_mstcn_pilot_policy_series.csv`
  - `experiments/results/full_ua_mstcn_pilot/full_ua_mstcn_pilot_resource_trace.csv`
  - `experiments/results/full_ua_mstcn_pilot/full_ua_mstcn_pilot_status.json`
  - `experiments/results/full_ua_mstcn_pilot/full_ua_mstcn_pilot_report.md`
- environment:
  - Python: `3.10.19`
  - PyTorch: `2.5.1+cu121`
  - CUDA available: `true`
  - Device: `NVIDIA GeForce RTX 4070 Ti SUPER`
- resource_trace:
  - Aggregate model: `7776` train windows, `1612` validation windows, `10` epochs, `2.760s` train runtime, peak CUDA memory `451079168` bytes.
  - Service-pilot global model: `39970` train windows, `8300` validation windows, `11` epochs, `13.863s` train runtime, peak CUDA memory `1205614592` bytes.
- gate:
  - Status JSON and report status are `pass`.
  - Selection profile contains exactly one aggregate entity and the fixed services `app_2557`, `app_7264`, `app_1675`, `app_3665`, and `app_521`.
  - Validation-only calibration margins are written for all entities and horizons.
  - Forecasting metrics rows: `36`; prediction rows: `59460`; policy metric rows: `18`; policy series rows: `9908`; resource trace rows: `2`.
  - Raw and calibrated P90 fields are written.
  - Raw crossing count is `0`; calibrated crossing count is `0`.
  - Forecasting and policy metrics are finite.
  - Policy SLA violation values are within `[0, 1]`; capacity series are nonnegative.
  - Test split is recorded as evaluation-only.
  - `experiments/results/full_ua_mstcn_broad/` does not exist.
  - `experiments/results/metrics.csv` hash remained `0FA3FDB810CA0A0F74592D3ADC92102C7A0CA67EA02C2B8C8F22435537F873AB`.
- headline_numbers:
  - Aggregate test MAE: `2.528` at h=1, `4.122` at h=5, `4.551` at h=10.
  - Aggregate Full-UA predictive policy: SLA `0.0372`, over-provisioning `0.1359`, scaling actions `588`.
  - Five-service pilot policy remains mixed: Full-UA predictive reduces SLA relative to lagged tracking on all five services, but does not uniformly beat reactive SLA and often uses more capacity.
- gate_decision: `pass_for_stage_2_pilot`
- claim_boundary: `pilot evidence only; do not promote Full UA-MSTCN superiority or broad full-model claims.`
- next_allowed_step: `Prepare a Full UA-MSTCN calibration/batch-size plan before any broad full-model run; keep manuscript headline conclusion unchanged unless a separate conservative writing pass is requested.`

## response_letter_full_ua_pilot_refresh_20260428

- status: `pass`
- completed_at: `2026-04-28 12:36:00 +08:00`
- purpose: Refresh the point-by-point response after Full UA-MSTCN Stage 2 pilot so the response no longer says aggregate-full and service-pilot results remain future gates.
- observed_outputs:
  - `revisions/response-letter.md`
  - `revisions/response-letter.tex`
  - `revisions/response-letter.pdf`
- compile_check:
  - `conda run -n paper-tcn latexmk -gg -pdf -interaction=nonstopmode -halt-on-error response-letter.tex` passed.
  - `revisions/response-letter.pdf`: 8 pages, `164113` bytes.
- gate:
  - Response letter now states that Full UA-MSTCN Stage 1 smoke and Stage 2 aggregate/service-pilot runs are complete.
  - Response letter preserves the boundary that the Full UA-MSTCN pilot is mixed and not broad manuscript-facing performance evidence.
  - Manuscript headline conclusion remains unchanged.
- gate_decision: `pass`
- claim_boundary: `response upload artifact refreshed only; no broad Full UA-MSTCN or superiority claim was added.`
- next_allowed_step: `Prepare Full UA-MSTCN broad calibration/batch-size planning before any broad full-model run.`

## full_ua_mstcn_broad_calibration_20260428

- status: `pass`
- completed_at: `2026-04-28 12:47:17 +08:00`
- purpose: Run a broad-cohort Full UA-MSTCN calibration slice to compare batch sizes before any broad full-model execution.
- command:

```powershell
& 'C:\Users\Liu Jinchun\miniconda3\envs\lora-cheongsam\python.exe' experiments\run_full_ua_mstcn_broad_calibration.py --config experiments\configs\default_v2018.yaml --batch-sizes 512 1024 --epochs 2 --max-train-batches 120 --train-windows-per-service 512 --valid-windows-per-service 128
```

- implementation_outputs:
  - `experiments/run_full_ua_mstcn_broad_calibration.py`
- observed_outputs:
  - `experiments/results/full_ua_mstcn_broad_calibration/full_ua_mstcn_broad_calibration_manifest.csv`
  - `experiments/results/full_ua_mstcn_broad_calibration/full_ua_mstcn_broad_calibration_results.csv`
  - `experiments/results/full_ua_mstcn_broad_calibration/full_ua_mstcn_broad_calibration_status.json`
  - `experiments/results/full_ua_mstcn_broad_calibration/full_ua_mstcn_broad_calibration_report.md`
- scope_boundary:
  - Broad calibration slice only.
  - Held-out test split untouched; no test windows generated.
  - No `experiments/results/full_ua_mstcn_broad/` result directory created.
  - Central `metrics.csv` unchanged.
- resource_and_batch_results:
  - Service count: `139`.
  - Sampled train windows: `71168`; sampled validation windows: `17792`.
  - Batch 512: `31181` train windows/s, validation loss `0.137236`, peak CUDA memory `2555364864` bytes.
  - Batch 1024: `33607` train windows/s, validation loss `0.145796`, peak CUDA memory `2555480064` bytes.
  - Recommended batch size by throughput and VRAM gate: `1024`.
  - Conservative validation-loss option: `512`.
- gate:
  - Status JSON and report status are `pass`.
  - Manifest covers exactly `139` broad services.
  - Validation losses are finite.
  - Both tested batch sizes stayed below the 12GB local VRAM gate.
  - `experiments/results/full_ua_mstcn_broad/` does not exist.
  - `experiments/results/metrics.csv` hash remained `0FA3FDB810CA0A0F74592D3ADC92102C7A0CA67EA02C2B8C8F22435537F873AB`.
- gate_decision: `pass_for_broad_calibration_slice`
- claim_boundary: `resource calibration only; no broad Full UA-MSTCN forecasting or policy claim.`
- next_allowed_step: `Prepare an explicit Full UA-MSTCN broad full-run approval package or run plan; do not start broad full-model execution without a separate approval gate.`

## response_letter_full_ua_calibration_refresh_20260428

- status: `pass`
- completed_at: `2026-04-28 12:50:00 +08:00`
- purpose: Refresh the point-by-point response after the Full UA-MSTCN broad batch-size calibration slice.
- observed_outputs:
  - `revisions/response-letter.md`
  - `revisions/response-letter.tex`
  - `revisions/response-letter.pdf`
- compile_check:
  - `conda run -n paper-tcn latexmk -gg -pdf -interaction=nonstopmode -halt-on-error response-letter.tex` passed.
  - `revisions/response-letter.pdf`: 8 pages, `164360` bytes.
- gate:
  - Response letter now mentions Full UA-MSTCN smoke, Stage 2 pilot, and broad batch-size calibration.
  - Response letter states that broad calibration touched no held-out test split and produced no broad forecasting or policy result.
  - Manuscript headline conclusion remains unchanged.
- gate_decision: `pass`
- claim_boundary: `response upload artifact refreshed only; no broad Full UA-MSTCN result was added.`
- next_allowed_step: `Prepare Full UA-MSTCN broad full-run approval package before execution.`

## full_ua_mstcn_broad_approval_20260428

- status: `approval_plan_only`
- completed_at: `2026-04-28 14:07:55 +08:00`
- purpose: Prepare an explicit Full UA-MSTCN broad full-run approval package after the broad batch-size calibration slice, without starting the broad full-model run.
- command:

```powershell
& 'C:\Users\Liu Jinchun\miniconda3\envs\lora-cheongsam\python.exe' experiments\plan_full_ua_mstcn_broad_approval.py --config experiments\configs\default_v2018.yaml
```

- implementation_outputs:
  - `experiments/plan_full_ua_mstcn_broad_approval.py`
- observed_outputs:
  - `experiments/results/full_ua_mstcn_broad_approval/full_ua_mstcn_broad_execution_approval.md`
  - `experiments/results/full_ua_mstcn_broad_approval/full_ua_mstcn_broad_execution_manifest.csv`
  - `experiments/results/full_ua_mstcn_broad_approval/full_ua_mstcn_broad_preflight_checks.md`
  - `experiments/results/full_ua_mstcn_broad_approval/full_ua_mstcn_broad_resource_update_from_calibration.md`
  - `experiments/results/full_ua_mstcn_broad_approval/full_ua_mstcn_broad_approval_status.json`
- resource_and_batch_estimate:
  - Recommended batch size from calibration: `1024`.
  - Conservative validation-loss option: `512`.
  - Planned train windows: `1111166`; planned validation windows: `239080`; planned prediction rows: `718769`.
  - Safety-adjusted wall estimate: `23.3` minutes; safety-adjusted artifact estimate: `295.3` MB.
  - Current resource census: `16` logical CPUs, `11504234496` free RAM bytes, `56453869568` free D-drive bytes.
- gate:
  - Approval manifest covers exactly `139` broad services.
  - Approval script did not import model code or start training.
  - Approval script did not generate held-out test windows.
  - `experiments/results/full_ua_mstcn_broad/` does not exist.
  - `experiments/results/metrics.csv` hash remained `0FA3FDB810CA0A0F74592D3ADC92102C7A0CA67EA02C2B8C8F22435537F873AB`.
- gate_decision: `pass_for_approval_package_only`
- claim_boundary: `execution-readiness artifact only; no broad Full UA-MSTCN forecasting, policy, or superiority claim.`
- next_allowed_step: `Implement and preflight a guarded broad full-run entrypoint, then require explicit approval again before launching broad execution.`

## full_ua_mstcn_broad_preflight_20260428

- status: `pass`
- completed_at: `2026-04-28 14:22:48 +08:00`
- purpose: Implement and preflight the guarded Full UA-MSTCN broad-run entrypoint without launching broad training.
- command:

```powershell
& 'C:\Users\Liu Jinchun\miniconda3\envs\lora-cheongsam\python.exe' experiments\run_full_ua_mstcn_broad.py --config experiments\configs\default_v2018.yaml
```

- implementation_outputs:
  - `experiments/run_full_ua_mstcn_broad.py`
  - `experiments/run_full_ua_mstcn_pilot.py` updated so shared policy/evaluation code treats `service_broad` as service-level semantics.
- observed_outputs:
  - `experiments/results/full_ua_mstcn_broad_preflight/full_ua_mstcn_broad_preflight_manifest.csv`
  - `experiments/results/full_ua_mstcn_broad_preflight/full_ua_mstcn_broad_preflight_status.json`
  - `experiments/results/full_ua_mstcn_broad_preflight/full_ua_mstcn_broad_preflight_report.md`
- gate:
  - Guarded entrypoint requires `--execute --confirm-run-id full_ua_mstcn_broad_20260428` before broad training can start.
  - Preflight covered exactly `139` services and the `139`-row approval manifest.
  - CUDA was available on `NVIDIA GeForce RTX 4070 Ti SUPER`.
  - Test split is recorded as held-out evaluation only; fitting uses train prefix and calibration/early stopping uses validation prefix.
  - `experiments/results/full_ua_mstcn_broad/` does not exist.
  - `experiments/results/metrics.csv` hash remained `0FA3FDB810CA0A0F74592D3ADC92102C7A0CA67EA02C2B8C8F22435537F873AB`.
- gate_decision: `pass_for_guarded_preflight_only`
- claim_boundary: `preflight artifact only; no broad Full UA-MSTCN model was trained and no forecasting or policy result was produced.`
- next_allowed_step: `Only after explicit approval, launch the guarded broad Full UA-MSTCN command; otherwise keep manuscript claims frozen.`

## full_ua_mstcn_broad_20260428

- status: `pass`
- completed_at: `2026-04-28 15:01:56 +08:00`
- purpose: Execute the guarded broad Full UA-MSTCN run over the 139-service broad cohort after approval and preflight gates.
- command:

```powershell
& 'C:\Users\Liu Jinchun\miniconda3\envs\lora-cheongsam\python.exe' experiments\run_full_ua_mstcn_broad.py --config experiments\configs\default_v2018.yaml --execute --confirm-run-id full_ua_mstcn_broad_20260428
```

- implementation_outputs:
  - `experiments/run_full_ua_mstcn_broad.py`
  - `experiments/run_full_ua_mstcn_pilot.py` updated to compute validation loss in batches for broad-scale memory safety.
- execution_note:
  - The first launch attempt reached training but failed during validation with CUDA OOM because the shared training function evaluated the full validation tensor at once.
  - The failed attempt wrote no result artifacts; the empty failed output directory was verified and removed.
  - The training function was patched to evaluate validation loss in batches, then the same guarded command was rerun successfully.
- observed_outputs:
  - `experiments/results/full_ua_mstcn_broad/full_ua_mstcn_broad_selection_profile.csv`
  - `experiments/results/full_ua_mstcn_broad/full_ua_mstcn_broad_forecasting_metrics.csv`
  - `experiments/results/full_ua_mstcn_broad/full_ua_mstcn_broad_predictions.csv`
  - `experiments/results/full_ua_mstcn_broad/full_ua_mstcn_broad_calibration.csv`
  - `experiments/results/full_ua_mstcn_broad/full_ua_mstcn_broad_policy_metrics.csv`
  - `experiments/results/full_ua_mstcn_broad/full_ua_mstcn_broad_policy_series.csv`
  - `experiments/results/full_ua_mstcn_broad/full_ua_mstcn_broad_resource_trace.csv`
  - `experiments/results/full_ua_mstcn_broad/full_ua_mstcn_broad_status.json`
  - `experiments/results/full_ua_mstcn_broad/full_ua_mstcn_broad_report.md`
- resource_trace:
  - Service count: `139`.
  - Train windows: `1111166`; validation windows: `230740`; prediction rows: `1384023`.
  - Batch size: `1024`; max epochs: `20`; epochs completed: `20`.
  - Train runtime: `755.869s`; total runtime: `1054.340s`.
  - Peak CUDA memory: `891226624` bytes; process RSS in resource trace: `5566631936` bytes.
- gate:
  - Status JSON and report status are `pass`.
  - Forecasting rows: `834`; profile rows: `139`; calibration rows: `417`; policy metric rows: `417`; policy series rows: `230601`.
  - Forecast and policy metrics are finite.
  - Raw crossing count is `0`; calibrated crossing count is `0`.
  - Policy SLA violation values are within `[0, 1]`; capacity series are nonnegative.
  - Test split is recorded as held-out evaluation only.
  - `experiments/results/metrics.csv` hash remained `0FA3FDB810CA0A0F74592D3ADC92102C7A0CA67EA02C2B8C8F22435537F873AB`.
- headline_numbers:
  - Test mean MAE by horizon: h=1 `26.677`, h=5 `36.834`, h=10 `42.829`.
  - Test mean calibrated P90 coverage by horizon: h=1 `0.918`, h=5 `0.906`, h=10 `0.901`.
  - Policy means: Full-UA predictive SLA `0.0219`, over-provisioning `52.07`, scaling actions `377.18`.
  - Reactive policy means: SLA `0.0173`, over-provisioning `56.20`, scaling actions `248.06`.
- gate_decision: `pass_for_broad_full_ua_mstcn_evidence`
- claim_boundary: `broad evidence is mixed; Full UA-MSTCN predictive lowers mean over-provisioning relative to reactive but has higher mean SLA violation and more scaling actions. Do not claim superiority.`
- next_allowed_step: `Prepare a conservative evidence sync and response-letter/manuscript-boundary refresh; keep main conclusion unchanged unless a separate claim-calibration pass approves wording.`

## response_letter_full_ua_broad_refresh_20260428

- status: `pass`
- completed_at: `2026-04-28 15:44:16 +08:00`
- purpose: Refresh the point-by-point response after the guarded broad Full UA-MSTCN run and preserve the mixed-evidence boundary.
- observed_outputs:
  - `revisions/full-ua-evidence-sync-2026-04-28.md`
  - `revisions/response-letter.md`
  - `revisions/response-letter.tex`
  - `revisions/response-letter.pdf`
- compile_check:
  - `conda run -n paper-tcn latexmk -gg -pdf -interaction=nonstopmode -halt-on-error response-letter.tex` passed.
  - `revisions/response-letter.pdf`: 8 pages, `165428` bytes.
  - Compile log has one underfull hbox at lines 24--25 and no overfull or fatal errors.
- gate:
  - Response letter no longer says broad Full UA-MSTCN full-model results remain future gates.
  - Response letter states that the broad Full UA-MSTCN run completed all 139 services, passed its gate, and preserved evaluation-only test-split discipline.
  - Response letter records the mixed policy outcome: Full UA-MSTCN predictive lowers mean over-provisioning relative to reactive but has higher mean SLA violation and more scaling actions.
  - Manuscript headline conclusion remains unchanged.
- gate_decision: `pass`
- claim_boundary: `response upload artifact refreshed only; no broad Full UA-MSTCN superiority claim was added.`
- next_allowed_step: `Decide whether to refresh the manuscript/source package conservatively; otherwise keep current main conclusion and upload response PDF with changed-file manifest.`

## source_package_refresh_full_ua_broad_20260428

- status: `pass`
- completed_at: `2026-04-28 16:09:21 +08:00`
- purpose: Refresh the self-contained Cluster Computing LaTeX source package after the late-stage full broad QLR and broad Full UA-MSTCN updates and the AI-use disclosure check, without changing manuscript conclusions or experiment metrics.
- command:

```powershell
conda run -n paper-tcn python scripts\build_submission_package.py --manifest submission\cluster-source-package-manifest.yaml --output submission\source-package\cluster-computing --verify --archive
```

- observed_outputs:
  - `submission/source-package/cluster-computing/`
  - `submission/source-package/cluster-computing.zip`
- package_summary:
  - Staged files: `31`.
  - Dependency discovery: `10` LaTeX files, `1` BibTeX file, `17` figure assets, and `2` static template extras.
  - Source zip SHA256: `89762B030FADC40EC210A5374D192CB399E7AD0C7106BB9D1036B1743555C602`.
  - Source zip size: `4103752` bytes.
  - The zip contains no manuscript PDF, response PDF, LaTeX intermediate files, or experiment result directories.
- compliance_note:
  - The live Springer AI-policy path was checked during final submission QA.
  - At that package snapshot, `manuscript/sections/declarations.tex` included a conservative AI-use disclosure for Codex-assisted revision preparation; this was later superseded by `ai_disclosure_removal_20260428`.
  - No generative-AI-created images are included in the manuscript or source package.
- compile_check:
  - Build-script clean-dir `latexmk` verification passed.
  - Independent zip-extraction `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex` verification passed.
  - Extracted clean build produced `main.pdf`: `21` pages, `4667806` bytes.
- final_qa:
  - `experiments/results/metrics.csv` SHA256 remained `0FA3FDB810CA0A0F74592D3ADC92102C7A0CA67EA02C2B8C8F22435537F873AB`.
  - `git diff --check` reported only the known `HANDOFF.md:430` trailing whitespace plus existing CRLF warnings.
  - Temporary zip clean-verification directory was removed after verification.
  - After reviewer-compliance audit, the internal non-rendered Table 4 label was renamed from a smoke-test label to `tab:forecast-leakage-free`; manuscript compilation and source-package clean verification still passed.
- gate_decision: `pass_for_submission_source_package`
- claim_boundary: `packaging and compile QA only; no new experiment, result row, or manuscript headline conclusion was added.`
- next_allowed_step: `Run final portal-facing submission QA: confirm original submitting author, submission ID, upload roles, and whether a highlighted related-file manuscript is needed.`

## manuscript_concision_source_refresh_20260428

- status: `pass`
- completed_at: `2026-04-28 16:51:33 +08:00`
- purpose: Compress the revised manuscript to stay within the 20-page cap while preserving reviewer-required edits, the mixed-evidence boundary, and the current main conclusion.
- manuscript_edits:
  - Condensed repeated explanatory prose in `manuscript/sections/introduction.tex`, `experiments.tex`, `results.tex`, `threats.tex`, and `conclusion.tex`.
  - Preserved the reviewer-requested abstract horizon mapping, QLR raw/guarded reporting, service-cohort boundary, and no-superiority framing.
  - No experiment metrics, `metrics.csv`, or central results tables were regenerated for this pass.
- compile_check:
  - Initial `latexmk` attempt found `main.pdf` locked by WPS; a temporary `main_pagecheck` job compiled successfully and confirmed `17` pages.
  - After closing the locked PDF view, standard manuscript compile passed:

```powershell
conda run -n paper-tcn latexmk -gg -pdf -interaction=nonstopmode -halt-on-error main.tex
```

  - `manuscript/main.pdf`: `17` pages, `4640593` bytes.
- source_package_refresh:
  - command:

```powershell
conda run -n paper-tcn python scripts\build_submission_package.py --manifest submission\cluster-source-package-manifest.yaml --output submission\source-package\cluster-computing --verify --archive
```

  - Build-script clean-dir `latexmk` verification passed.
  - Staged files: `31`.
  - Dependency discovery: `10` LaTeX files, `1` BibTeX file, `17` figure assets, and `2` static template extras.
  - Source zip SHA256: `0A16BF41EFF49C9C3C4BA3E6102ED1BADBE35C5C43DE61D48C6AC754B97892D9`.
  - Source zip size: `4097298` bytes.
- final_qa:
  - `experiments/results/metrics.csv` SHA256 remained `0FA3FDB810CA0A0F74592D3ADC92102C7A0CA67EA02C2B8C8F22435537F873AB`.
  - Source zip check: `31` entries, `17` figure assets, and `0` PDF/LaTeX-intermediate files.
  - Current manuscript source scan found no `smoke-test`, `repository-placeholder`, public-release placeholder sentence, or LaTeX tracked-change markers.
  - `git diff --check` reported only the known `HANDOFF.md:430` trailing whitespace plus existing CRLF warnings.
  - `submission/revision-changed-files-manifest.md` and `submission/checklist.md` were updated to record the 17-page manuscript and refreshed source package.
- gate_decision: `pass_for_20_page_submission_cap`
- claim_boundary: `language and packaging QA only; no new experiment, result row, or manuscript headline conclusion was added.`

## figure_readability_fix_20260428

- status: `pass`
- completed_at: `2026-04-28 20:10:12 +08:00`
- purpose: Increase readability of Figures 3, 5, and 6, enlarge Figures 1 and 2 as double-column figures, and fix the observed Figure 3 page overflow risk.
- edits:
  - `manuscript/sections/experiments.tex`: changed Figures 1, 2, and 3 to `figure*` double-column floats with `0.95\textwidth` image width.
  - `experiments/render_manuscript_figures.py`: increased Figure 5 and Figure 6 in-plot title, axis, tick, annotation, and legend readability; kept Figure 6 to the original displayed model set despite additional QLR rows in `metrics.csv`.
  - `experiments/run_container_service_experiments.py`: regenerated Figure 3 as a compact 3-by-4 panel layout rather than a 12-row vertical stack.
- visual_qa:
  - Rendered Figure 3 page with `pdftoppm` before and after the fix.
  - Before: Figure 3 filled almost the full left column height and placed the caption at the bottom margin.
  - After: Figure 3 is a double-column 3-by-4 panel on page 9 with caption and following text fully inside the page; no visible overflow.
- compile_check:
  - Temporary `main_fig3check` compile passed and produced `18` pages.
  - Standard `main.pdf` compile passed after closing the WPS lock on `main.pdf`.
  - `manuscript/main.pdf`: `18` pages, `3468186` bytes.
- source_package_refresh:
  - Build-script clean-dir `latexmk` verification passed.
  - Source zip SHA256: `1048C53FAB97F92C358FDDE2E62833B620784BE83761C2BF18D3C9EF89B8F4F0`.
  - Source zip size: `2923714` bytes.
- final_qa:
  - `experiments/results/metrics.csv` SHA256 remained `0FA3FDB810CA0A0F74592D3ADC92102C7A0CA67EA02C2B8C8F22435537F873AB`.
  - `submission/revision-changed-files-manifest.md` and `submission/checklist.md` were updated to record the 18-page figure-adjusted manuscript and refreshed source package.
- gate_decision: `pass_for_figure_readability_and_no_overflow`
- claim_boundary: `figure rendering and packaging QA only; no experiment result or manuscript headline conclusion changed.`

## ai_disclosure_removal_20260428

- status: `pass`
- completed_at: `2026-04-28 20:33:29 +08:00`
- purpose: Remove the dedicated final `Use of artificial intelligence tools` declaration paragraph so the revised manuscript keeps the same declaration style as the original submission, without changing scientific claims or experiment metrics.
- edits:
  - `manuscript/sections/declarations.tex`: removed the dedicated AI-use paragraph and left the author-contribution paragraph immediately after code availability.
  - `submission/checklist.md`, `submission/field-answers.md`, `submission/revision-upload-checklist.md`, and `submission/revision-changed-files-manifest.md`: replaced statements saying the manuscript includes an AI-use disclosure with submission-consistency wording.
  - `experiments/03-results-claim-map.md`: recorded this as declaration/package QA only.
- compile_check:
  - Standard `main.pdf` compile passed after closing the WPS lock on `main.pdf`.
  - `manuscript/main.pdf`: `18` pages, `3466515` bytes.
- source_package_refresh:
  - `scripts/build_submission_package.py --verify --archive` passed clean-dir `latexmk` verification.
  - Independent zip-extraction `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex` verification passed.
  - Source zip SHA256: `B4444C9C2F54502A70D375E00321D368C720948E4A5EAA3C28CF1FD05F2ED83E`.
  - Source zip size: `2923507` bytes.
- final_qa:
  - Current manuscript and refreshed source-package LaTeX sources contain no `Use of artificial intelligence tools`, `OpenAI Codex was used`, or `Codex-assisted revision` text.
  - `experiments/results/metrics.csv` SHA256 remained `0FA3FDB810CA0A0F74592D3ADC92102C2B8C8F22435537F873AB`.
  - `git diff --check` reported only the known `HANDOFF.md:430` trailing whitespace plus existing CRLF warnings.
- gate_decision: `pass_for_submission_consistency`
- claim_boundary: `declaration and packaging QA only; no experiment result or manuscript headline conclusion changed.`

## figure5_legend_layout_fix_20260428

- status: `pass`
- completed_at: `2026-04-28 20:57:37 +08:00`
- purpose: Fix the visible Figure 5 overlap where the top legend collided with the `Case study at 1-minute horizon` title in the compiled manuscript.
- edits:
  - `experiments/render_manuscript_figures.py`: extended `save_figure` with an optional tight-layout rectangle and moved the Figure 5 legend from the first subplot axis to a figure-level top legend with reserved space.
  - `experiments/results/figures/forecast_case_study.png`: regenerated from the plotting script.
- visual_qa:
  - Direct PNG inspection confirmed the legend and all three case-study titles are separated.
  - Compiled page render saved to `submission/qa-pages/fig5_layout_final-10.png`; page 10 visual inspection found no visible Figure 5 title/legend overlap or clipping.
- compile_check:
  - `conda run -n paper-tcn python -m py_compile experiments\render_manuscript_figures.py` passed.
  - Standard `main.pdf` compile passed and produced `18` pages, `3444970` bytes.
- source_package_refresh:
  - Build-script clean-dir `latexmk` verification passed.
  - Independent zip-extraction `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex` verification passed.
  - Source zip SHA256: `2493300B43E03F37F0D9597978D5E69A6C9DC18A2168F8D147D02EB59216C53D`.
  - Source zip size: `2914945` bytes.
- final_qa:
  - `experiments/results/metrics.csv` SHA256 remained `0FA3FDB810CA0A0F74592D3ADC92102C2B8C8F22435537F873AB`.
- gate_decision: `pass_for_figure5_visual_readability`
- claim_boundary: `figure rendering and packaging QA only; no experiment result or manuscript headline conclusion changed.`

## reviewer1_public_repository_url_20260428

- status: `pass`
- completed_at: `2026-04-28 21:09:54 +08:00`
- purpose: Align the revision with Reviewer 1's mandatory request for a public reproducibility repository link in the Introduction and remove conflicting confidential-only availability language from current submission materials.
- repository_url: `https://github.com/Jinchun-Liu/paper-workbench`
- public_access_verified_at: `2026-04-28 21:48:11 +08:00`
- edits:
  - `manuscript/sections/introduction.tex`: added the public repository sentence after the contribution list.
  - `manuscript/sections/declarations.tex`: replaced confidential/private/upon-acceptance availability language with the public repository route.
  - `revisions/response-letter.md` and `revisions/response-letter.tex`: changed R1.2 from partial adoption to completed public-link adoption.
  - `submission/cover-letter.md`, `submission/cover-letter_jgc.md`, `submission/reproducibility-package.md`, `submission/field-answers.md`, `submission/revision-upload-checklist.md`, `submission/checklist.md`, and `submission/revision-changed-files-manifest.md`: synchronized the public repository URL and upload notes.
- compile_check:
  - Standard `main.pdf` compile passed and produced `18` pages, `3446081` bytes.
  - `response-letter.pdf` compile passed and produced `8` pages, `165756` bytes.
- source_package_refresh:
  - Build-script clean-dir `latexmk` verification passed.
  - Independent zip-extraction `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex` verification passed.
  - Source zip SHA256 after final service-capacity equation and QLR broad-service text polish: `50CCD5C4B63C4CF834F15A46D54D1252FC58381EA6EB9AED6A1E39AB59B71B10`.
  - Source zip size after final service-capacity equation and QLR broad-service text polish: `2915180` bytes.
- final_qa:
  - Current manuscript and response-letter sources contain `https://github.com/Jinchun-Liu/paper-workbench`.
  - Current manuscript and response-letter sources no longer contain the prior R1.2 partial-adoption wording.
  - Anonymous HTTP access to `https://github.com/Jinchun-Liu/paper-workbench` returned `200`.
  - GitHub API returned `private=false`, `visibility=public`, and default branch `main`.
  - Anonymous `git ls-remote --heads https://github.com/Jinchun-Liu/paper-workbench.git` returned `344c44f8bbfe5366cac184ce47d16d509bd7eab4 refs/heads/main`.
  - `experiments/results/metrics.csv` SHA256 remained `0FA3FDB810CA0A0F74592D3ADC92102C2B8C8F22435537F873AB`.
- gate_decision: `pass_for_text_package_and_public_repo_visibility`
- claim_boundary: `submission/reproducibility-route correction only; no experiment result or manuscript headline conclusion changed.`
