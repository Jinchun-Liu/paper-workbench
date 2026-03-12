# Trace-Driven Proactive Autoscaling Paper Workbench

This repository contains the manuscript, experiment scripts, processed artifacts, and submission materials for the paper `Trace-Driven Proactive Autoscaling for Cluster Workloads via Multi-Horizon Forecasting`.

## Scope

The current verified manuscript mainline is the broad audited service-level version:

- primary journal build: `manuscript/main.tex`
- backup JGC build: `manuscript/main_jgc.tex`
- promoted service-level main result: `139` audited `app_du` groups

The repository is organized as a reproducibility workbench rather than as a production software package. Raw Alibaba trace archives remain third-party data and are not redistributed by the frozen review package.

For GitHub distribution, the repository excludes:

- `data/raw/` third-party Alibaba archives
- `submission/frozen-package/` local staged review-freeze copies
- three oversized processed CSV files that exceed GitHub's single-file upload limit

Those oversized artifacts are instead expected to be distributed through the review-freeze release archive.

## Reproduce the manuscript builds

From `manuscript/`:

```bash
latexmk -pdf -interaction=nonstopmode main.tex
latexmk -pdf -interaction=nonstopmode main_jgc.tex
```

## Reproduce the frozen review package

The review package manifest is stored at `submission/reproducibility-package-manifest.yaml`.

To stage a frozen package:

```bash
python3 scripts/build_repro_package.py \
  --manifest submission/reproducibility-package-manifest.yaml \
  --output submission/frozen-package/review-freeze-2026-03-12 \
  --archive
```

This command copies the declared package contents, excludes transient build files, and writes:

- `BUILD-METADATA.json`
- `SHA256SUMS`
- an optional `.tar.gz` archive

## Main directories

- `data/`: dataset notes and processed artifacts
- `experiments/`: preprocessing, modeling, evaluation, and generated result artifacts
- `literature/`: evidence ledger and related support material
- `manuscript/`: Springer manuscript sources and compiled PDFs
- `review/`: reviewer-response log
- `submission/`: highlights, cover letters, checklists, and reproducibility-package planning
