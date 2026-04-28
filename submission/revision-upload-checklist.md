# Revision Upload Checklist

Source instruction recorded from the journal revision page: the original submitting author must upload a point-by-point response as a PDF; all changed files must be uploaded again; the revised manuscript must not include tracked changes; a highlighted version, if needed, belongs in the related-file section; extension requests must include the submission ID.

Submission ID: `1fc2f3df-78af-4b4d-bf18-8c4d58531184`.

Original submitting author account: confirmed by the user on 2026-04-28. The current manuscript marks Jinchun Liu as corresponding author, so no original-submitter/corresponding-author mismatch is indicated in the local manuscript metadata.

## Required Uploads

- [x] Full point-by-point response PDF exported from `revisions/response-letter.md` and `revisions/response-letter.tex`.
- [x] Clean revised manuscript PDF without tracked changes or visible markup patterns.
- [x] Final full point-by-point response PDF covers every mapped reviewer comment before upload.
- [x] Revised manuscript source package refreshed at `submission/source-package/cluster-computing.zip`.
- [x] Changed figures, tables, supplementary files, and source-package files identified in `submission/revision-changed-files-manifest.md`.
- [ ] Optional highlighted/marked-up revised manuscript uploaded only as a related file, not as the clean manuscript.

## Response PDF Content Gate

- [x] Opens with a concise summary of major changes.
- [x] Answers each mapped reviewer comment point by point.
- [x] Refreshed after the approved full 139-service QLR run completed.
- [x] Describes all additional QLR experiments carried out, including the approved full broad run.
- [x] Describes the full 139-service QLR result conservatively as mixed broad service evidence.
- [x] Describes the completed broad Full UA-MSTCN result conservatively as mixed broad service evidence.
- [x] Includes the requested public repository URL response for Reviewer 1.
- [x] Separates completed evidence from planned, preflight-only, and smoke-only work.
- [x] Does not claim broad 139-service QLR superiority; the verified full run is mixed.
- [x] Uses current compiled manuscript table/page references for the QLR additions.

## Upload Responsibility

- [x] Confirm the original submitting author account before upload.
- [x] Confirm whether the original submitting author differs from the corresponding author.
- [x] Record the submission ID before upload.
- [ ] If more time is needed, contact the journal with the submission ID before the deadline.

## Manuscript File Hygiene

- [x] Main revised manuscript has no tracked changes.
- [x] Main revised manuscript has no obvious comments or visible markup commands in LaTeX source.
- [ ] Any marked-up version is clearly named and uploaded under related files only.
- [x] Response PDF describes the verified full 139-service QLR numbers; the manuscript headline conclusion remains intentionally unchanged pending a separate table/discussion refresh decision.
- [x] Local compile environment has been restored and rerun after the latest edits.

## Current Revision-Specific Notes

- QLR aggregate full is completed evidence.
- QLR service pilot and 10-service calibration are bounded evidence only.
- QLR broad approval and guarded preflight are execution-readiness artifacts only.
- QLR full 139-service completed after explicit approval on 2026-04-28 and passed the broad gate; it must be described conservatively as mixed evidence, not superiority.
- Full UA-MSTCN Stage 1 smoke completed after the QLR broad gate; it is smoke-only and not manuscript-facing performance evidence.
- Full UA-MSTCN Stage 2 aggregate-full plus five-service pilot completed on 2026-04-28; it is pilot evidence only and remains mixed, not superiority evidence.
- Full UA-MSTCN broad batch-size calibration completed on 2026-04-28; it is resource calibration only, with no held-out test evaluation and no broad full-model result.
- Full UA-MSTCN broad full-run approval package completed on 2026-04-28; it is execution-readiness planning only, not new forecasting or policy evidence.
- Full UA-MSTCN guarded broad-run entrypoint preflight completed on 2026-04-28; the preflight itself remains a preflight-only artifact.
- Full UA-MSTCN broad full-model run completed on 2026-04-28 and passed its gate; results are mixed and must not be described as superiority evidence.
- The response PDF has been rebuilt after the approved full broad QLR run and the completed broad Full UA-MSTCN full-model result.
- The manuscript and response letter state the public reproducibility URL as `https://github.com/Jinchun-Liu/paper-workbench`; anonymous web/API/git access was verified on 2026-04-28 before upload.
- The manuscript keeps the original-submission style without a dedicated AI-use disclosure paragraph; no generative-AI-created images are included in the manuscript or source package.
- The source package has been rebuilt after the late-stage QLR/Full UA-MSTCN updates and final declaration cleanup; the uploaded zip is manuscript-source only, clean-dir verified, and does not include experiment result directories or LaTeX intermediates.
- Local LaTeX path has been restored for the current revision build: `latexmk` runs through the `paper-tcn` environment, `cuted.sty` is available through `sttools`, and `natbib.sty` is available in the user MiKTeX tree.
- Current generated PDFs: `manuscript/main.pdf` and `revisions/response-letter.pdf`.
- Submission ID is recorded as `1fc2f3df-78af-4b4d-bf18-8c4d58531184`; original submitting author upload responsibility is confirmed.
