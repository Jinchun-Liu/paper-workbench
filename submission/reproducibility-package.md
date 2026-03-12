# Reproducibility Package Plan

This note summarizes the reproducibility package referenced by the manuscript declarations and cover letters.

## Scope

The frozen package for the current manuscript version is intended to include:

- manuscript sources and build entrypoints: `manuscript/main.tex`, `manuscript/main_jgc.tex`, and section files
- dataset documentation and manifests: `experiments/dataset_manifest.yaml`, `00-status.md`, and `literature/evidence-ledger.csv`
- preprocessing and experiment scripts under `experiments/`
- processed datasets and cohort summaries under `data/processed/`
- generated result tables and figures under `experiments/results/`

The concrete package manifest used to stage this bundle is stored at `submission/reproducibility-package-manifest.yaml`.

## Review Access

During peer review, the frozen package can be supplied to the editor and reviewers on request so that the manuscript numbers, figures, and service-cohort artifacts can be audited against the submitted version.

## Public Release Plan

Upon acceptance, the same frozen package will be deposited in a stable public repository with a persistent identifier and referenced from the final Data Availability and Code Availability statements.

## Staging Command

The current repository includes a package-staging script:

```bash
python3 scripts/build_repro_package.py \
  --manifest submission/reproducibility-package-manifest.yaml \
  --output submission/frozen-package/review-freeze-2026-03-12 \
  --archive
```

This route copies the declared files, excludes transient LaTeX build outputs and raw third-party archives, and writes a checksum manifest for audit.

## Current Staged Snapshot

The current staged review-freeze snapshot is:

- directory: `submission/frozen-package/review-freeze-2026-03-12`
- archive: `submission/frozen-package/review-freeze-2026-03-12.tar.gz`
- contents summary: `185` files, `834,376,871` bytes before compression
