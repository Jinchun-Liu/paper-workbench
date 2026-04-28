# QLR Evidence Sync for Manuscript and Response Letter

- sync_id: `qlr_evidence_sync_20260427`
- prepared_at: `2026-04-27 23:35:22 +08:00`
- status: `writing_support_only`
- scope: QLR lane evidence audit after aggregate full, service pilot, 10-service calibration, broad approval planning, and guarded preflight.
- boundary: This sync does not run full 139-service, does not invoke Full UA-MSTCN, and does not change manuscript headline conclusions.

## Artifact Chain

- Aggregate QLR full: `experiments/results/qlr_aggregate_full/aggregate_qlr_full_report.md`
- Service QLR pilot: `experiments/results/qlr_service_pilot/qlr_service_pilot_report.md`
- Service QLR 10-service calibration: `experiments/results/qlr_service_calibration_10/qlr_service_calibration_report.md`
- Broad 139-service approval package: `experiments/results/qlr_service_broad_approval/qlr_broad_execution_approval.md`
- Guarded broad preflight: `experiments/results/qlr_service_broad_preflight/qlr_service_broad_preflight_report.md`
- Claim map: `experiments/03-results-claim-map.md`
- Run registry: `experiments/02-run-registry.md`

## Evidence Ready For Conservative Writing

Aggregate QLR full has passed the full aggregate forecasting and policy gate.

- Forecasting MAE by horizon: `h=1` 2.265, `h=5` 3.967, `h=10` 4.315.
- Raw P90/P50 crossing count: 0 at all aggregate horizons.
- Predictive QLR policy: SLA violation 0.033993, over-provisioning 0.147416, scaling actions 587.
- Reactive aggregate policy: SLA violation 0.000618, over-provisioning 0.350565, scaling actions 43.
- Lagged aggregate policy: SLA violation 0.470952, over-provisioning 0.013448, scaling actions 1616.
- Test split discipline is explicit: test rows are evaluation-only; fitting uses the train+validation prefix.
- Central `metrics.csv` was updated only after aggregate gate pass and only for `qlr-*` experiment ids.

Service QLR pilot and calibration are valid bounded evidence, not full 139-service evidence.

- Five-service pilot forecasting MAE means: `h=1` 17.619, `h=5` 29.047, `h=10` 35.662.
- Five-service pilot raw crossing count: 131 total; guarded crossing count: 0.
- Five-service pilot policy means: QLR predictive SLA 0.019471, over-provisioning 52.958, actions 366.4.
- Five-service pilot policy means: reactive SLA 0.015385, over-provisioning 50.223, actions 331.6.
- Ten-service calibration forecasting MAE means: `h=1` 21.192, `h=5` 34.083, `h=10` 41.949.
- Ten-service calibration raw crossing count: 206 total; guarded crossing count: 0.
- Ten-service calibration policy means: QLR predictive SLA 0.022776, over-provisioning 59.613, actions 403.8.
- Ten-service calibration policy means: reactive SLA 0.015325, over-provisioning 56.090, actions 300.6.
- Service selection descriptors are train+validation-prefix only; full-span descriptors and test outcomes are not used for service selection.
- `median_container_request_cores` is service metadata used only for replica conversion; no pilot/calibration selected service required fallback.
- Service `metrics.csv` was not updated.

Broad 139-service full run is not complete.

- The approval package estimates the full run from 10-service calibration at 55.8 seconds/service, 129.2 serial minutes, and 64.6 minutes at two workers.
- Safety-adjusted artifact estimate is 274,244,470 bytes.
- Guarded preflight covers 139 services and passes.
- `experiments/results/qlr_service_broad/` has not been created.
- Full execution requires explicit token `I_APPROVE_QLR_139_SERVICE_FULL_RUN`.

## Response Letter Draft Text

For Reviewer 2, use language like:

> We agree that the original revision needed a simpler uncertainty-aware baseline before any stronger model claim could be defended. We therefore added a quantile linear regression (QLR) baseline with P50/P90 outputs, explicit raw crossing diagnostics, and a guarded P90 used only after reporting raw crossing behavior. The aggregate QLR gate passed for horizons 1, 5, and 10, and the held-out test split was used only for evaluation; fitting and all policy choices use the train+validation prefix.

> The QLR policy results are deliberately reported as mixed rather than as a new superiority claim. On the aggregate trace, QLR predictive control reduces SLA violation relative to lagged tracking but remains worse than the reactive policy on SLA and scaling actions. In service-level pilot and calibration runs, QLR again improves strongly over lagged tracking but is weaker than reactive on average SLA violation, over-provisioning, and action count. We treat this as evidence for the paper's boundary-mapping interpretation: uncertainty-aware predictive control is auditable, but service heterogeneity limits simple transfer of aggregate policy improvements.

> We have not reported a full 139-service QLR result yet. Instead, we prepared an approval package and a guarded preflight entrypoint for that scale. The preflight covers all 139 services and explicitly prevents accidental execution without a confirmation token. This keeps the response separated between completed evidence and planned execution.

## Manuscript-Safe Claim Edits

Allowed now:

- State that QLR aggregate forecasting and policy artifacts have passed the aggregate gate.
- State that service pilot/calibration results are mixed and preliminary, with QLR weaker than reactive on mean service policy metrics.
- State that raw and guarded P90 are both recorded, and that guarded P90 has zero crossing in pilot/calibration artifacts.
- State that test split is evaluation-only, and that service selection uses train+validation-prefix descriptors.
- State that full 139-service QLR execution is prepared but not yet run.

Blocked until full 139-service completes:

- Do not claim broad 139-service QLR performance.
- Do not imply QLR service-level superiority.
- Do not update manuscript headline conclusions based on pilot, calibration, approval, or preflight artifacts alone.
- Do not claim Full UA-MSTCN evidence from the QLR-only lane.

## Next Gate

The next experiment gate remains explicit full 139-service approval. Without the confirmation token, the safe writing task is to update response-letter wording and manuscript methods/results boundaries using only the completed aggregate and bounded service evidence above.
