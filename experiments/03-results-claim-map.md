# Results Claim Map

This file maps revision-time artifacts to claims. Keep new results provisional until the matching gate and review checks pass.

## qlr_aggregate_full_20260427

- status: `aggregate-only provisional evidence`
- run_registry_entry: `experiments/02-run-registry.md#qlr_aggregate_full_20260427`
- artifacts:
  - `experiments/results/qlr_aggregate_full/aggregate_qlr_forecasting_metrics.csv`
  - `experiments/results/qlr_aggregate_full/aggregate_qlr_predictions.csv`
  - `experiments/results/qlr_aggregate_full/aggregate_qlr_policy_metrics.csv`
  - `experiments/results/qlr_aggregate_full/aggregate_qlr_policy_series.csv`
  - `experiments/results/qlr_aggregate_full/aggregate_qlr_full_report.md`
- supported_claim:
  - QLR is now an auditable aggregate uncertainty baseline under the existing train/validation/test split.
  - QLR predictive policy can be compared against reactive and lagged tracking under the same aggregate simulator parameters used by the existing UA-MSTCN-Lite policy path.
- boundaries:
  - The result is aggregate-only and does not support service-level or 139-service claims.
  - The result does not change the manuscript's main conclusion.
  - Raw crossing metrics are recorded, and guarded P90 is used only after documenting raw P90/P50 crossing behavior.
  - The held-out test split is used only for evaluation, not for fitting, model selection, parameter selection, or policy tuning.
- next_gate:
  - Run a five-service QLR pilot before any full 139-service expansion.
  - Do not start Full UA-MSTCN until QLR aggregate and service evidence are stable.

## qlr_service_pilot_20260427

- status: `service-level pilot evidence`
- run_registry_entry: `experiments/02-run-registry.md#qlr_service_pilot_20260427`
- artifacts:
  - `experiments/results/qlr_service_pilot/service_selection_profile.csv`
  - `experiments/results/qlr_service_pilot/service_qlr_forecasting_raw.csv`
  - `experiments/results/qlr_service_pilot/service_qlr_forecasting_summary.csv`
  - `experiments/results/qlr_service_pilot/service_qlr_predictions.csv`
  - `experiments/results/qlr_service_pilot/service_qlr_policy_raw.csv`
  - `experiments/results/qlr_service_pilot/service_qlr_policy_summary.csv`
  - `experiments/results/qlr_service_pilot/service_qlr_policy_delta_by_service.csv`
  - `experiments/results/qlr_service_pilot/service_qlr_policy_series.csv`
  - `experiments/results/qlr_service_pilot/qlr_service_pilot_report.md`
- supported_claim:
  - QLR service pilot artifacts are auditable on five fixed representative services.
  - Service selection trace uses train+validation-prefix load and burst descriptors; full-span summary descriptors are not used for selection.
  - Raw and guarded P90 behavior is recorded separately for service-level forecasts.
- boundaries:
  - The result is a pilot, not full 139-service evidence.
  - QLR predictive policy is mixed in the pilot: it improves strongly over lagged tracking but is slightly weaker than reactive on average SLA and over-provisioning.
  - The result does not change the manuscript's main conclusion.
  - `median_container_request_cores` is used only for replica conversion in policy simulation, not for service selection.
  - Pilot pass does not authorize an automatic full 139-service run.
- next_gate:
  - Prepare a full 139-service QLR resource and execution plan before running any broader service experiment.
  - Keep Full UA-MSTCN on hold.

## qlr_service_broad_plan_20260427

- status: `planning artifact only`
- run_registry_entry: `experiments/02-run-registry.md#qlr_service_broad_plan_20260427`
- artifacts:
  - `experiments/results/qlr_service_broad_plan/qlr_broad_resource_plan.md`
  - `experiments/results/qlr_service_broad_plan/qlr_broad_run_manifest.csv`
  - `experiments/results/qlr_service_broad_plan/qlr_broad_gate_checklist.md`
  - `experiments/results/qlr_service_broad_plan/qlr_broad_dry_run_report.md`
- supported_claim:
  - A future broad QLR run has a concrete 139-service manifest, resource estimate, and gate checklist.
  - Planning confirms that the next execution step should be 10-service calibration, not immediate full 139-service execution.
- boundaries:
  - This artifact contains no new model training or policy result.
  - It does not support a new manuscript claim.
  - It does not authorize automatic full 139-service execution.
  - It keeps the manuscript's current mixed service-pilot interpretation unchanged.
- next_gate:
  - Run a 10-service calibration only after explicit approval.
  - Keep full 139-service and the held deep-model path frozen until calibration evidence is reviewed.

## qlr_service_calibration_10_20260427

- status: `calibration evidence only`
- run_registry_entry: `experiments/02-run-registry.md#qlr_service_calibration_10_20260427`
- artifacts:
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
- supported_claim:
  - The QLR service calibration gate ran successfully on ten fixed services at `--num-workers 2`.
  - The calibration artifacts preserve prefix-only service descriptors, raw and guarded P90 fields, crossing diagnostics, policy metrics, and per-service resource traces.
  - The calibration supports resource and schema readiness review for a possible future full 139-service run.
- boundaries:
  - This is calibration evidence only, not full 139-service evidence.
  - QLR predictive policy remains mixed: it strongly improves over lagged tracking but is weaker than reactive on mean SLA violation, over-provisioning, and action count in this 10-service calibration.
  - The result does not change the manuscript's main conclusion.
  - `median_container_request_cores` is used only for replica conversion in policy simulation, not for service selection.
  - Calibration pass does not authorize an automatic full 139-service run.
- next_gate:
  - Prepare an explicit full 139-service execution approval plan before any broad run.
  - Keep Full UA-MSTCN frozen until QLR broad evidence is reviewed and explicitly approved.

## qlr_service_broad_approval_20260427

- status: `execution approval artifact only`
- run_registry_entry: `experiments/02-run-registry.md#qlr_service_broad_approval_20260427`
- artifacts:
  - `experiments/results/qlr_service_broad_approval/qlr_broad_execution_approval.md`
  - `experiments/results/qlr_service_broad_approval/qlr_broad_execution_manifest.csv`
  - `experiments/results/qlr_service_broad_approval/qlr_broad_preflight_checks.md`
  - `experiments/results/qlr_service_broad_approval/qlr_broad_resource_update_from_calibration.md`
- supported_claim:
  - A future full 139-service QLR run now has an auditable approval package and execution manifest.
  - The resource estimate is updated from 10-service calibration evidence: about 55.8 seconds/service, 129.2 serial minutes, and 64.6 minutes at two workers.
  - The approval package documents preflight checks, unchanged `metrics.csv`, and explicit-approval requirements.
- boundaries:
  - This artifact contains no new model fitting, policy simulation, or full 139-service result.
  - It does not support a new manuscript claim.
  - It does not authorize automatic full 139-service execution.
  - Full UA-MSTCN remains frozen.
  - Manuscript headline conclusions remain unchanged.
- next_gate:
  - Obtain explicit approval before running any full 139-service experiment.
  - Immediately before any future full run, re-check resources, `metrics.csv` hash, and absence of `experiments/results/qlr_service_broad/`.

## qlr_service_broad_preflight_20260427

- status: `protected-entrypoint preflight only`
- run_registry_entry: `experiments/02-run-registry.md#qlr_service_broad_preflight_20260427`
- artifacts:
  - `experiments/results/qlr_service_broad_preflight/qlr_service_broad_preflight_profile.csv`
  - `experiments/results/qlr_service_broad_preflight/qlr_service_broad_preflight_report.md`
- supported_claim:
  - A guarded full 139-service QLR entrypoint exists and can be checked without executing the full run.
  - The preflight profile covers 139 broad services and records prefix-only service descriptors.
  - The execution guard requires explicit confirmation before full 139-service execution.
- boundaries:
  - This artifact contains no model fitting, policy simulation, or full 139-service result.
  - It does not support a new manuscript claim.
  - It does not authorize automatic full 139-service execution.
  - Full UA-MSTCN remains frozen.
  - Manuscript headline conclusions remain unchanged.
- next_gate:
  - Run the full 139-service QLR experiment only after explicit approval with the required confirmation token.
  - Keep central `metrics.csv` unchanged and preserve mixed or negative outcomes if the full run is later executed.

## qlr_evidence_sync_20260427

- status: `writing support only`
- run_registry_entry: `experiments/02-run-registry.md#qlr_evidence_sync_20260427`
- artifacts:
  - `revisions/qlr-evidence-sync-2026-04-27.md`
- supported_claim:
  - The completed QLR lane has a conservative writing map separating aggregate evidence, bounded service evidence, and non-result approval/preflight artifacts.
  - Response-letter language can now answer the QLR baseline request without implying service-level or broad-run superiority.
- boundaries:
  - This artifact does not contain a new run.
  - It does not support a new manuscript result.
  - It does not authorize automatic full 139-service execution.
  - It keeps the main conclusion unchanged and records mixed service-level QLR behavior.
- next_gate:
  - Use this sync for response-letter drafting and manuscript boundary wording.
  - Require explicit confirmation before any full 139-service execution.

## qlr_response_and_boundary_edits_20260427

- status: `draft response and conservative manuscript edits`
- run_registry_entry: `experiments/02-run-registry.md#qlr_response_and_boundary_edits_20260427`
- artifacts:
  - `revisions/response-letter.md`
  - `manuscript/sections/experiments.tex`
  - `manuscript/sections/results.tex`
- supported_claim:
  - The manuscript can now state that aggregate QLR was added as a simpler uncertainty-aware baseline under the same held-out evaluation discipline.
  - The response letter can state that service QLR pilot/calibration results are mixed and bounded, not broad 139-service evidence.
- boundaries:
  - No new experiment was run.
  - No full 139-service QLR performance claim is supported.
  - Abstract and conclusion remain unchanged.
  - These edits require LaTeX compile and consistency QA before resubmission; the current local MiKTeX path is missing Perl for `latexmk` and `cuted.sty` for direct `pdflatex`.
- next_gate:
  - Compile the manuscript and check that response-letter language matches the manuscript wording and artifact numbers.

## revision_portal_upload_requirements_20260427

- status: `submission logistics only`
- run_registry_entry: `experiments/02-run-registry.md#revision_portal_upload_requirements_20260427`
- artifacts:
  - `submission/revision-upload-checklist.md`
  - `submission/checklist.md`
  - `revisions/response-letter.md`
  - `revisions/revision-plan.md`
- supported_claim:
  - The workbench now records the journal revision portal requirements for response PDF, clean manuscript upload, changed-file re-upload, original submitting author responsibility, and extension handling.
- boundaries:
  - This is not experimental evidence.
  - It does not change manuscript scientific claims.
  - It does not replace final portal checks on submission day.
- next_gate:
  - Export the point-by-point response as PDF and package the clean revised manuscript after local compile dependencies are restored.

## latex_environment_revision_pdf_export_20260427

- status: `submission build artifact only`
- run_registry_entry: `experiments/02-run-registry.md#latex_environment_revision_pdf_export_20260427`
- artifacts:
  - `manuscript/main.pdf`
  - `revisions/response-letter.pdf`
  - `revisions/response-letter.tex`
  - `submission/revision-upload-checklist.md`
  - `submission/checklist.md`
  - `.gitattributes`
- supported_claim:
  - The current revised manuscript and QLR-focused response letter can be built locally after restoring the MiKTeX/latexmk path.
  - The response PDF records the additional QLR experiments, the evaluation-only test split discipline, and the boundary between completed evidence and broad-run preflight/approval artifacts.
- boundaries:
  - This is not experimental evidence.
  - It does not support a new manuscript result.
  - It does not authorize automatic full 139-service execution.
  - It does not change the manuscript headline conclusion.
  - The exported response PDF is QLR-focused and still must be expanded to cover every reviewer comment before final upload.
- next_gate:
  - Complete the final all-reviewer point-by-point response and changed-file upload manifest.

## full_point_by_point_response_20260428

- status: `submission response artifact only`
- run_registry_entry: `experiments/02-run-registry.md#full_point_by_point_response_20260428`
- artifacts:
  - `revisions/response-letter.md`
  - `revisions/response-letter.tex`
  - `revisions/response-letter.pdf`
  - `manuscript/main.pdf`
  - `submission/checklist.md`
  - `submission/revision-upload-checklist.md`
- supported_claim:
  - The revision package now has a compiled point-by-point response covering the mapped R1/R2/R3 comments.
  - The response describes the additional QLR experiments, distinguishes completed aggregate evidence from service pilot/calibration and broad preflight/approval artifacts, and records conservative handling of the public-URL request.
- boundaries:
  - This is not new experimental evidence.
  - It does not support a full 139-service QLR result.
  - It does not authorize automatic full 139-service execution.
  - It does not change the manuscript headline conclusion.
- next_gate:
  - Prepare a changed-file upload manifest and refresh any source package required by the portal.

## revision_changed_files_and_source_package_20260428

- status: `submission packaging artifact only`
- run_registry_entry: `experiments/02-run-registry.md#revision_changed_files_and_source_package_20260428`
- artifacts:
  - `submission/revision-changed-files-manifest.md`
  - `submission/source-package/cluster-computing/`
  - `submission/source-package/cluster-computing.zip`
  - `submission/checklist.md`
  - `submission/revision-upload-checklist.md`
- supported_claim:
  - The revision package has an upload-facing changed-file manifest and a clean-dir verified source package.
- boundaries:
  - This is not experimental evidence.
  - It does not support a new manuscript result.
  - It does not authorize full 139-service QLR execution.
- next_gate:
  - Final portal-field and PDF visual QA before upload.

## qlr_service_broad_full_20260428

- status: `full broad QLR evidence available`
- run_registry_entry: `experiments/02-run-registry.md#qlr_service_broad_full_20260428`
- artifacts:
  - `experiments/results/qlr_service_broad/qlr_service_broad_report.md`
  - `experiments/results/qlr_service_broad/service_qlr_forecasting_summary.csv`
  - `experiments/results/qlr_service_broad/service_qlr_policy_summary.csv`
  - `experiments/results/qlr_service_broad/service_qlr_predictions.csv`
  - `experiments/results/qlr_service_broad/broad_resource_trace.csv`
- supported_claim:
  - The 139-service QLR broad run was executed after explicit approval and passed its gate.
  - QLR broad forecasting preserves raw P90 crossings and guarded P90 outputs; guarded crossings are zero.
  - The broad service policy comparison is mixed rather than uniformly favorable: QLR predictive lowers mean over-provisioning relative to reactive, but has slightly higher mean SLA violation and more scaling actions.
  - The report explicitly maintains evaluation-only test-split discipline and leaves central `metrics.csv` unchanged.
- boundaries:
  - This evidence does not automatically change the manuscript headline conclusion.
  - It must not be described as QLR policy superiority.
  - Earlier response/upload files required refresh after this run; later refresh entries now record that update.
  - Full UA-MSTCN claims remain unsupported beyond the separate smoke gate.
- next_gate:
  - Decide whether and how to incorporate broad QLR as conservative, mixed service-level evidence in the response letter and manuscript.

## full_ua_mstcn_smoke_20260428

- status: `stage 1 smoke evidence only`
- run_registry_entry: `experiments/02-run-registry.md#full_ua_mstcn_smoke_20260428`
- artifacts:
  - `experiments/models/full_ua_mstcn.py`
  - `experiments/run_full_ua_mstcn_smoke.py`
  - `experiments/environment-full-ua-mstcn.yml`
  - `experiments/results/full_ua_mstcn_smoke/full_ua_mstcn_smoke_report.md`
  - `experiments/results/full_ua_mstcn_smoke/full_ua_mstcn_smoke_status.json`
  - `experiments/results/full_ua_mstcn_smoke/full_ua_mstcn_smoke_metrics.csv`
- supported_claim:
  - Full UA-MSTCN has been started as a real PyTorch causal multi-scale TCN, separate from `UA-MSTCN-Lite`.
  - Stage 1 aggregate-prefix smoke passed on CUDA with non-crossing P50/P90 output shape `[291, 3, 2]`.
- boundaries:
  - This is not manuscript-facing performance evidence.
  - It does not support claims that Full UA-MSTCN improves over QLR, baselines, or UA-MSTCN-Lite.
  - It does not authorize a broad full-model run.
- next_gate:
  - Prepare a Full UA-MSTCN aggregate-full plus 5-service pilot plan with runtime, leakage, calibration, and policy gates.

## full_ua_mstcn_pilot_20260428

- status: `stage 2 pilot evidence only`
- run_registry_entry: `experiments/02-run-registry.md#full_ua_mstcn_pilot_20260428`
- artifacts:
  - `experiments/run_full_ua_mstcn_pilot.py`
  - `experiments/results/full_ua_mstcn_pilot/full_ua_mstcn_pilot_report.md`
  - `experiments/results/full_ua_mstcn_pilot/full_ua_mstcn_pilot_status.json`
  - `experiments/results/full_ua_mstcn_pilot/full_ua_mstcn_pilot_forecasting_metrics.csv`
  - `experiments/results/full_ua_mstcn_pilot/full_ua_mstcn_pilot_policy_metrics.csv`
  - `experiments/results/full_ua_mstcn_pilot/full_ua_mstcn_pilot_resource_trace.csv`
- supported_claim:
  - Full UA-MSTCN Stage 2 pilot can train and evaluate an aggregate full-series model and a fixed five-service global service model with validation-only P90 calibration.
  - The pilot preserves the held-out test split as evaluation-only and leaves central `metrics.csv` unchanged.
  - Aggregate Full-UA predictive policy is viable but not dominant: it improves over lagged tracking on SLA, while reactive remains lower-SLA in this pilot.
  - The five-service policy surface is mixed; the pilot supports continued calibration, not a superiority claim.
- boundaries:
  - This is not broad Full UA-MSTCN evidence.
  - It does not support a manuscript conclusion that Full UA-MSTCN beats QLR, UA-MSTCN-Lite, or reactive policy.
  - It does not authorize `experiments/results/full_ua_mstcn_broad/` or a broad full-model run.
- next_gate:
  - Run a calibration/batch-size resource plan or calibration slice before any broad Full UA-MSTCN execution.

## full_ua_mstcn_broad_calibration_20260428

- status: `broad calibration slice only`
- run_registry_entry: `experiments/02-run-registry.md#full_ua_mstcn_broad_calibration_20260428`
- artifacts:
  - `experiments/run_full_ua_mstcn_broad_calibration.py`
  - `experiments/results/full_ua_mstcn_broad_calibration/full_ua_mstcn_broad_calibration_report.md`
  - `experiments/results/full_ua_mstcn_broad_calibration/full_ua_mstcn_broad_calibration_status.json`
  - `experiments/results/full_ua_mstcn_broad_calibration/full_ua_mstcn_broad_calibration_results.csv`
  - `experiments/results/full_ua_mstcn_broad_calibration/full_ua_mstcn_broad_calibration_manifest.csv`
- supported_claim:
  - The local GPU can train the broad service Full UA-MSTCN architecture on a 139-service train/validation calibration slice with batch sizes 512 and 1024 under the 12GB VRAM gate.
  - Batch 1024 is faster in the calibration slice, while batch 512 has slightly lower validation loss.
  - The broad calibration path keeps the held-out test split untouched and central `metrics.csv` unchanged.
- boundaries:
  - This is not broad Full UA-MSTCN forecasting evidence.
  - It is not policy evidence.
  - It does not support manuscript performance claims.
  - It does not authorize broad full-model execution without a separate approval/run gate.
- next_gate:
  - Prepare an explicit Full UA-MSTCN broad full-run approval package, including batch-size choice and expected runtime/artifact growth.

## full_ua_mstcn_broad_approval_20260428

- status: `execution approval artifact only`
- run_registry_entry: `experiments/02-run-registry.md#full_ua_mstcn_broad_approval_20260428`
- artifacts:
  - `experiments/plan_full_ua_mstcn_broad_approval.py`
  - `experiments/results/full_ua_mstcn_broad_approval/full_ua_mstcn_broad_execution_approval.md`
  - `experiments/results/full_ua_mstcn_broad_approval/full_ua_mstcn_broad_execution_manifest.csv`
  - `experiments/results/full_ua_mstcn_broad_approval/full_ua_mstcn_broad_preflight_checks.md`
  - `experiments/results/full_ua_mstcn_broad_approval/full_ua_mstcn_broad_resource_update_from_calibration.md`
  - `experiments/results/full_ua_mstcn_broad_approval/full_ua_mstcn_broad_approval_status.json`
- supported_claim:
  - The project has an explicit, auditable approval package for a possible broad Full UA-MSTCN run.
  - The approval package uses the completed 139-service batch-size calibration to recommend batch `1024`, while preserving batch `512` as the conservative validation-loss option.
  - The package confirms that central `metrics.csv` remains unchanged and that `experiments/results/full_ua_mstcn_broad/` was not created.
- boundaries:
  - This is not broad Full UA-MSTCN forecasting evidence.
  - This is not policy evidence.
  - It does not support manuscript performance claims or a superiority conclusion.
  - It does not authorize automatic broad execution; a guarded entrypoint and explicit launch approval are still required.
- next_gate:
  - Implement a guarded broad full-run entrypoint with preflight checks, but do not launch broad execution without explicit approval.

## full_ua_mstcn_broad_preflight_20260428

- status: `guarded preflight artifact only`
- run_registry_entry: `experiments/02-run-registry.md#full_ua_mstcn_broad_preflight_20260428`
- artifacts:
  - `experiments/run_full_ua_mstcn_broad.py`
  - `experiments/results/full_ua_mstcn_broad_preflight/full_ua_mstcn_broad_preflight_report.md`
  - `experiments/results/full_ua_mstcn_broad_preflight/full_ua_mstcn_broad_preflight_status.json`
  - `experiments/results/full_ua_mstcn_broad_preflight/full_ua_mstcn_broad_preflight_manifest.csv`
- supported_claim:
  - The broad Full UA-MSTCN run now has a guarded entrypoint with approval, hash, resource, service-count, and output-directory checks.
  - The preflight confirms that the planned run covers the same `139` broad services and preserves test split evaluation-only discipline.
  - The entrypoint is configured to reuse the existing service-level policy semantics through the shared pilot implementation.
- boundaries:
  - This is not broad Full UA-MSTCN forecasting evidence.
  - This is not policy evidence.
  - It does not support manuscript performance claims or a superiority conclusion.
  - It does not mean the broad run has started; `experiments/results/full_ua_mstcn_broad/` remains absent.
- next_gate:
  - Launch the guarded broad Full UA-MSTCN run only with explicit approval and the command recorded in the preflight report.

## full_ua_mstcn_broad_20260428

- status: `broad Full UA-MSTCN evidence available`
- run_registry_entry: `experiments/02-run-registry.md#full_ua_mstcn_broad_20260428`
- artifacts:
  - `experiments/run_full_ua_mstcn_broad.py`
  - `experiments/run_full_ua_mstcn_pilot.py`
  - `experiments/results/full_ua_mstcn_broad/full_ua_mstcn_broad_report.md`
  - `experiments/results/full_ua_mstcn_broad/full_ua_mstcn_broad_status.json`
  - `experiments/results/full_ua_mstcn_broad/full_ua_mstcn_broad_forecasting_metrics.csv`
  - `experiments/results/full_ua_mstcn_broad/full_ua_mstcn_broad_policy_metrics.csv`
  - `experiments/results/full_ua_mstcn_broad/full_ua_mstcn_broad_predictions.csv`
  - `experiments/results/full_ua_mstcn_broad/full_ua_mstcn_broad_resource_trace.csv`
- supported_claim:
  - The 139-service broad Full UA-MSTCN run was executed through the guarded entrypoint and passed its gate.
  - The run preserves train/validation/test discipline: fitting uses the train prefix, calibration/early stopping uses validation, and the held-out test split is evaluation-only.
  - Forecasting metrics are finite, raw and calibrated P90 crossings are zero, and central `metrics.csv` remains unchanged.
  - Full UA-MSTCN broad predictive policy provides mixed service-level evidence: it lowers mean over-provisioning relative to reactive but has higher mean SLA violation and more scaling actions.
- boundaries:
  - This evidence does not support a universal Full UA-MSTCN superiority claim.
  - It must not be used to overwrite the manuscript headline conclusion without a separate claim-calibration pass.
  - The first failed OOM launch should be recorded as an implementation diagnostic, not hidden.
  - Earlier response/upload files required refresh after this run; later refresh entries now record that update.
- next_gate:
  - Prepare a conservative Full UA-MSTCN evidence sync and response-letter/manuscript-boundary refresh.

## response_letter_full_ua_broad_refresh_20260428

- status: `response upload artifact refreshed`
- run_registry_entry: `experiments/02-run-registry.md#response_letter_full_ua_broad_refresh_20260428`
- artifacts:
  - `revisions/full-ua-evidence-sync-2026-04-28.md`
  - `revisions/response-letter.md`
  - `revisions/response-letter.tex`
  - `revisions/response-letter.pdf`
  - `submission/revision-upload-checklist.md`
  - `submission/revision-changed-files-manifest.md`
- supported_claim:
  - The point-by-point response now accurately states that the broad Full UA-MSTCN run was executed and passed its gate.
  - The response records the broad Full UA-MSTCN result as mixed evidence, not a superiority result.
  - The response states that the manuscript headline conclusion remains unchanged.
- boundaries:
  - This is not a new experiment beyond `full_ua_mstcn_broad_20260428`.
  - It does not promote Full UA-MSTCN to a main manuscript superiority claim.
  - It does not refresh the source package by itself.
- next_gate:
  - Conservative manuscript/source-package refresh decision, if the authors want the late-stage artifacts included in the upload source package.

## source_package_refresh_full_ua_broad_20260428

- status: `submission packaging artifact only`
- run_registry_entry: `experiments/02-run-registry.md#source_package_refresh_full_ua_broad_20260428`
- artifacts:
  - `submission/source-package/cluster-computing/`
  - `submission/source-package/cluster-computing.zip`
  - `submission/cluster-source-package-manifest.yaml`
  - `scripts/build_submission_package.py`
- supported_claim:
  - The manuscript source package has been refreshed after the late-stage QLR and Full UA-MSTCN update cycle.
  - The package is self-contained for LaTeX compilation: both staged clean-dir verification and independent zip-extraction compilation passed.
  - The package contains only manuscript dependencies and excludes PDFs, LaTeX intermediate files, and experiment result directories.
  - A final submission-consistency pass removed the dedicated AI-use disclosure paragraph while retaining the check that no generative-AI-created images are included in the source package.
- boundaries:
  - This is not experimental evidence.
  - This does not update central `metrics.csv`.
  - This does not change the manuscript headline conclusion or the mixed-evidence interpretation.
- next_gate:
  - Final portal QA by the original submitting author: response PDF upload, clean revised manuscript/source upload, changed-file upload, submission ID check, and optional highlighted manuscript decision.
