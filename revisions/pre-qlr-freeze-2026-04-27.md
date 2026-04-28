# Pre-QLR Freeze Record

- freeze_id: `pre_qlr_freeze_20260427_180450`
- recorded_at: `2026-04-27 18:04:50 +08:00`
- purpose: Freeze the current major-revision workbench state before low-risk manuscript edits and QLR aggregate smoke work.
- scope: This record is additive. It does not replace or overwrite the older `review-freeze-2026-03-12` package.

## Dirty Worktree Snapshot

```text
 M HANDOFF.md
 M experiments/analyze_service_cohort_stability.py
 M experiments/models/baselines.py
 M experiments/policies/autoscaling_simulator.py
 M experiments/preprocessing/download_v2018.sh
 M experiments/preprocessing/prepare_v2018_machine_usage.py
 M experiments/results/service_cohort_broad/tables/service_cohort_stability_summary.csv
 M experiments/run_baselines.py
 M experiments/run_broad_service_cohort_pipeline.py
 M experiments/run_policy_eval.py
 M manuscript/main.pdf
 M manuscript/main.tex
 M manuscript/main_jgc.pdf
 M manuscript/main_jgc.tex
 M manuscript/sections/abstract.tex
 M manuscript/sections/abstract_jgc.tex
 M manuscript/sections/conclusion.tex
 M manuscript/sections/declarations.tex
 M manuscript/sections/experiments.tex
 M manuscript/sections/results.tex
 M manuscript/sections/threats.tex
 M review/reviewer_feedback.md
 M scripts/fetch_springer_template.sh
 M submission/checklist.md
 M submission/cover-letter.md
 M submission/cover-letter_jgc.md
?? experiments/analyze_service_policy_mechanisms.py
?? experiments/results/service_cohort_broad/figures/service_policy_delta_distribution.png
?? experiments/results/service_cohort_broad/tables/service_policy_delta_summary.csv
?? experiments/results/service_cohort_broad/tables/service_policy_mechanism_by_service.csv
?? experiments/results/service_cohort_broad/tables/service_policy_outcome_taxonomy.csv
?? experiments/results/service_cohort_broad/tables/service_policy_subgroup_summary.csv
?? experiments/results/service_cohort_broad/tables/service_policy_taxonomy_thresholds.csv
?? revisions/
?? scripts/build_submission_package.py
?? submission/cluster-source-package-manifest.yaml
?? submission/source-package/
```

## Key Artifact Hashes

| Path | Bytes | Last write time | SHA256 |
| --- | ---: | --- | --- |
| `manuscript/main.pdf` | 4587643 | 2026-03-13 00:27:19 | `DA4BBA0363D92FC9F93C742D33B548EB080789583CFFFAEB5D2A9ACD9C0CD930` |
| `manuscript/main_jgc.pdf` | 4589619 | 2026-03-13 00:27:19 | `48F97F4DBEE5EC40EDBF073A8BC5A6325A5A3C26E1F171F721EEC433FDFECA22` |
| `experiments/results/metrics.csv` | 3245 | 2026-03-11 18:41:41 | `A9A894BE51F76D6A74261978DB51F2F0A755138CD4FA2D57AF0D868F525AEB71` |
| `experiments/results/tables/quantile_coverage.csv` | 282 | 2026-03-12 16:33:21 | `82F131C3C351B89DE5F37A0609004F43D6DEE74EB222199940C93CF2292BF84E` |
| `experiments/results/service_cohort_broad/tables/service_forecasting_summary.csv` | 1765 | 2026-03-12 12:40:30 | `158FED08276989951CCF66C06A46406EDC5E8F2A5B4910FCD5E0E98D2767D2A7` |
| `experiments/results/service_cohort_broad/tables/service_policy_summary.csv` | 465 | 2026-03-12 12:40:30 | `BDD42FCF62F9F1D87C746DA904E0EFEC76D2CBB2340C48C170C651495329F0F3` |
| `experiments/results/service_cohort_broad/tables/service_policy_delta_summary.csv` | 1006 | 2026-03-12 21:14:13 | `0E733B30E1D9AEA7A5ECC41AFD589F4F1C92FABB6C253DABD657172B531BB05B` |
| `revisions/revision-plan.md` | 55516 | 2026-04-27 17:47:55 | `7D2A2927FE52F59170C9BE723BFDA29564EDA6DB6AC1CD6FCD1E6D013AF815A8` |
| `HANDOFF.md` | 26148 | 2026-03-13 00:54:11 | `F6F683A0330B6B28CCFD78FCE84E488F3362D71A1FD797CF718F365E191A4DAF` |

## Execution Boundary

- Start with low-risk manuscript and script preparation only.
- Run QLR aggregate smoke before any aggregate full policy extension.
- Do not run Full UA-MSTCN in this phase.
- Do not run full 139-service QLR in this phase.
- Do not fabricate a public repository URL; keep review-access and public-upon-acceptance wording until a real URL exists.
