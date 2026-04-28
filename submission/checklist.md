# Submission Checklist

## Journal fit

- [x] Primary journal selected.
- [x] Backup journal selected.
- [ ] Final article type confirmed on submission day.
- [ ] Final author instructions re-checked on submission day.
- [x] Original submitting author account confirmed for revision upload.
- [x] Submission ID recorded for upload and possible extension request: `1fc2f3df-78af-4b4d-bf18-8c4d58531184`.

## Manuscript

- [x] LaTeX manuscript scaffold created.
- [x] Numeric BibTeX workflow selected.
- [ ] All figures exported from verified experiment artifacts.
- [ ] All tables populated from verified experiment artifacts.
- [x] Abstract updated with final numbers only.

## Data and experiments

- [x] Official dataset source recorded.
- [x] Resumable download script created.
- [x] Full machine_usage trace downloaded.
- [x] Aggregate cluster series generated.
- [x] Forecasting baselines run on the current split.
- [x] Smoke-test policy evaluation run.
- [ ] Final trainable predictive model evaluated.

## Major revision QLR lane

- [x] Pre-QLR freeze record created before new experiments.
- [x] Dedicated `paper-tcn` environment created without installing Full UA-MSTCN/PyTorch dependencies.
- [x] QLR aggregate smoke gate passed.
- [x] QLR aggregate full forecasting and policy completed.
- [x] QLR service pilot completed before any 139-service full run.
- [x] QLR 139-service broad resource plan prepared without running the full experiment.
- [x] QLR 10-service calibration completed before any 139-service full run.
- [x] QLR 139-service full execution approval package prepared without running the full experiment.
- [x] Guarded QLR 139-service full-run entrypoint preflight completed without running the full experiment.
- [x] QLR evidence sync prepared for conservative response-letter and manuscript boundary edits.
- [x] QLR response-letter draft and conservative manuscript boundary edits prepared.
- [x] QLR manuscript compile recheck completed after local LaTeX dependencies are restored.
- [x] Full point-by-point response PDF expanded to cover R1/R2/R3 and recompiled.
- [x] QLR full 139-service run completed after explicit approval.
- [x] Full UA-MSTCN Stage 1 smoke started after QLR broad gate.
- [x] Full UA-MSTCN aggregate-full plus 5-service pilot completed.
- [x] Full UA-MSTCN broad calibration/batch-size slice completed before any broad full-model run.
- [x] Full UA-MSTCN broad full-run approval package prepared before execution.
- [x] Full UA-MSTCN guarded broad full-run entrypoint preflight completed before execution.
- [x] Full UA-MSTCN broad full-model run explicitly approved and launched.
- [x] Full UA-MSTCN broad evidence sync and response-letter refresh completed.

## Revision upload package

- [x] Journal revision upload requirements captured in `submission/revision-upload-checklist.md`.
- [x] QLR-focused response letter exported as PDF.
- [x] Final full point-by-point response PDF covers every mapped reviewer comment.
- [x] Response PDF refreshed after the approved full 139-service QLR run.
- [x] Response PDF describes all QLR experiments carried out, including the full broad run.
- [x] Response PDF updated to describe the approved full 139-service QLR result and preserve the mixed-evidence boundary.
- [x] Response PDF includes the requested public repository URL response for Reviewer 1.
- [x] Public GitHub repository URL is anonymously accessible before upload: `https://github.com/Jinchun-Liu/paper-workbench`.
- [x] Clean revised manuscript PDF compiled without tracked changes or visible markup patterns.
- [x] Revised manuscript compressed and figure-adjusted to 18 pages, within the 20-page cap, without changing the main conclusion.
- [ ] Optional highlighted revised manuscript prepared only for related-file upload, if needed.
- [x] All changed files identified for re-upload in `submission/revision-changed-files-manifest.md`.

## Evidence and ethics

- [x] Evidence ledger initialized.
- [x] No unverified gain claims inserted into manuscript.
- [x] Manuscript retains no dedicated AI-use disclosure paragraph for consistency with the original submission; no generative-AI-created images are included.
- [x] Funding, author roles, conflict of interest, and data availability statements completed.
- [x] Frozen reproducibility-package manifest prepared.
- [x] Frozen reproducibility package staged for the final submission snapshot.
- [x] Cluster source package built.
- [x] Clean-dir LaTeX compile verified.
- [x] Cluster source package refreshed after latest manuscript edits and archived as `submission/source-package/cluster-computing.zip`.
- [x] Cluster source package refreshed after full broad QLR artifacts and Full UA-MSTCN smoke/pilot/calibration/approval/preflight/broad-run code were added; source package remains limited to manuscript dependencies and passed clean zip compile.
- [x] Cluster source package refreshed after the final 17-page concision pass; clean-dir LaTeX verification passed.
- [x] Cluster source package refreshed after final declaration cleanup; clean-dir and independent zip-extraction LaTeX verification passed.
- [x] Figure 5 legend/title overlap fixed, page-10 visual QA captured, and source package refreshed with clean-dir and independent zip-extraction LaTeX verification.
- [x] Reviewer 1 public repository URL inserted into Introduction, availability statements, response letter, cover letter, and upload notes; source package refreshed and zip-extraction compile verified.
