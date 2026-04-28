# Revision Changed-Files Upload Manifest

Purpose: support the revision portal requirement that any file changed in response to reviewer comments is uploaded again. This manifest is conservative: when in doubt, upload the file or package again.

Submission ID: `1fc2f3df-78af-4b4d-bf18-8c4d58531184`. The user confirmed they are the original submitting author account holder for the revision upload.

## Required Main Uploads

- `manuscript/main.pdf` -- clean revised manuscript PDF, rebuilt after the response-letter and caption/method edits.
- `revisions/response-letter.pdf` -- point-by-point response PDF covering the mapped editor/R1/R2/R3 issues, rebuilt after the approved full 139-service QLR run and completed broad Full UA-MSTCN run.
- `submission/source-package/cluster-computing.zip` -- refreshed self-contained LaTeX source package after the full broad QLR and Full UA-MSTCN broad-run updates; clean-dir `latexmk` verification passed from the staged package and from an independent zip extraction.

## Revised Manuscript Source Files

- `manuscript/main.tex`
- `manuscript/refs.bib`
- `manuscript/sections/abstract.tex`
- `manuscript/sections/introduction.tex`
- `manuscript/sections/method.tex`
- `manuscript/sections/related_work.tex`
- `manuscript/sections/experiments.tex`
- `manuscript/sections/results.tex`
- `manuscript/sections/threats.tex`
- `manuscript/sections/conclusion.tex`
- `manuscript/sections/declarations.tex`

## Response And Revision Records

- `revisions/response-letter.md`
- `revisions/response-letter.tex`
- `revisions/revision-plan.md`
- `revisions/pre-qlr-freeze-2026-04-27.md`
- `revisions/qlr-evidence-sync-2026-04-27.md`
- `revisions/full-ua-evidence-sync-2026-04-28.md`
- `experiments/02-run-registry.md`
- `experiments/03-results-claim-map.md`
- `submission/checklist.md`
- `submission/revision-upload-checklist.md`

## Experiment And Artifact Files Changed By The Revision

Upload these as supplementary/reproducibility files if the portal requests experiment artifacts or a source/review package:

- QLR scripts: `experiments/run_qlr_smoke.py`, `experiments/run_qlr_aggregate_full.py`, `experiments/run_qlr_service_pilot.py`, `experiments/run_qlr_service_calibration.py`, `experiments/plan_qlr_service_broad.py`, `experiments/plan_qlr_service_broad_approval.py`, `experiments/run_qlr_service_broad.py`.
- Baseline/policy code touched by QLR: `experiments/models/baselines.py`, `experiments/policies/autoscaling_simulator.py`.
- QLR result directories: `experiments/results/qlr_smoke/`, `experiments/results/qlr_aggregate_full/`, `experiments/results/qlr_service_pilot/`, `experiments/results/qlr_service_calibration_10/`, `experiments/results/qlr_service_broad_plan/`, `experiments/results/qlr_service_broad_approval/`, `experiments/results/qlr_service_broad_preflight/`, `experiments/results/qlr_service_broad/`.
- Full UA-MSTCN smoke/pilot/calibration/approval/preflight/broad-run code and artifacts: `experiments/models/full_ua_mstcn.py`, `experiments/run_full_ua_mstcn_smoke.py`, `experiments/run_full_ua_mstcn_pilot.py`, `experiments/run_full_ua_mstcn_broad_calibration.py`, `experiments/plan_full_ua_mstcn_broad_approval.py`, `experiments/run_full_ua_mstcn_broad.py`, `experiments/environment-full-ua-mstcn.yml`, `experiments/results/full_ua_mstcn_smoke/`, `experiments/results/full_ua_mstcn_pilot/`, `experiments/results/full_ua_mstcn_broad_calibration/`, `experiments/results/full_ua_mstcn_broad_approval/`, `experiments/results/full_ua_mstcn_broad_preflight/`, `experiments/results/full_ua_mstcn_broad/`.
- Broad service diagnostic files under `experiments/results/service_cohort_broad/figures/` and `experiments/results/service_cohort_broad/tables/` that support the revised service-level mechanism discussion.

## Not Completed / Do Not Upload As Results

- Full UA-MSTCN Stage 1 smoke, Stage 2 aggregate/service pilot, broad batch-size calibration, approval, and preflight are execution-ladder artifacts; do not describe those intermediate artifacts alone as final Full UA-MSTCN results.
- Full UA-MSTCN broad full-model run is completed and mixed; ablation and stress-test runs are not completed.
- A highlighted/marked-up manuscript has not been prepared; upload one only in the related-file section if the portal explicitly asks for it.

## Latest Verification

- `manuscript/main.pdf`: 18 pages after the final concision and figure-readability pass, within the 20-page cap.
- `revisions/response-letter.pdf`: 8 pages.
- `submission/source-package/cluster-computing.zip`: rebuilt and clean-dir verified after the Reviewer 1 public-repository URL update; SHA256 `C60F83FB1E00D15A8340DED74C8E3C3CE083B2EE866476EADCD5A8682B2275D7`; size `2914975` bytes; `31` zip entries including `17` figure assets and no PDF/LaTeX intermediate files.
- `metrics.csv` SHA256 remains `0FA3FDB810CA0A0F74592D3ADC92102C7A0CA67EA02C2B8C8F22435537F873AB`.
- `experiments/results/qlr_service_broad/` now exists, passed gate, and contains the approved full 139-service QLR artifacts.
- `experiments/results/full_ua_mstcn_smoke/` now exists and contains Stage 1 smoke-only artifacts.
- `experiments/results/full_ua_mstcn_pilot/` now exists and contains Stage 2 pilot-only artifacts.
- `experiments/results/full_ua_mstcn_broad_calibration/` now exists and contains resource-calibration-only artifacts.
- `experiments/results/full_ua_mstcn_broad_approval/` now exists and contains approval-only artifacts produced before broad execution.
- `experiments/results/full_ua_mstcn_broad_preflight/` now exists and contains guarded-entrypoint preflight-only artifacts produced before broad execution.
- `experiments/results/full_ua_mstcn_broad/` now exists and contains the approved broad Full UA-MSTCN artifacts; evidence is mixed and should not be described as superiority.
- Current response PDF has been rebuilt after the full broad QLR and broad Full UA-MSTCN full-model results; the manuscript remains without a dedicated AI-use disclosure paragraph to match the original submission, has been compressed and figure-adjusted to fit the page limit, and the source package has been refreshed after these late-stage additions. The source package remains a manuscript-only source package rather than an experiment-artifact archive.
- Reviewer 1's mandatory public repository request is now reflected in the Introduction, Data availability, Code availability, response letter, cover letter, and upload notes with URL `https://github.com/Jinchun-Liu/paper-workbench`. Anonymous web/API/git access was verified on 2026-04-28 before upload.
- Final Figure 5 visual QA page render is saved as `submission/qa-pages/fig5_layout_final-10.png`; the legend is separated from the 1-minute title with no visible overlap in the compiled PDF.
- Revision portal responsibility is confirmed: the original submitting author account will upload the point-by-point response PDF and all changed manuscript/source files again.
