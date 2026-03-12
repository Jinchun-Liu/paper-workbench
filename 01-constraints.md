# Constraint Card

## must_include

- English manuscript.
- LaTeX project that compiles on local TeX Live 2023.
- Numeric citations with BibTeX.
- EI-aligned computer systems / cluster computing journal path.
- Public, reproducible Alibaba trace data only.
- No fabricated experiments, citations, or claimed gains.

## preferred

- Springer-compatible journal structure to reduce transfer cost between `Cluster Computing` and `Journal of Grid Computing`.
- A lightweight forecasting-plus-policy pipeline that can run on a workstation.
- Scripts that can resume large dataset downloads.
- A manuscript that is useful before all experiments are finished.

## must_avoid

- Closed-source APIs or private cluster data.
- Claims of novelty such as `first` or `state of the art` without verification.
- Heavy dependencies that are unnecessary for the first reproducible pass.
- Template or package choices that are fragile on TeX Live 2023.

## non_negotiables

- Only verified quantitative results may enter the paper.
- Dataset provenance must be recorded.
- Every high-risk statement must be traceable to a source or reproducible artifact.
- The project must remain transferable to the backup journal with limited rewrite effort.

## fallback_allowed_or_not

- yes: `Use a 2023-safe article fallback while keeping an official Springer template fetch script in the workspace.`
- yes: `Start with v2018 machine-level trace if container-level traces are too large for the first pass.`
- no: `No invented tables, figures, or metrics to make the draft look complete.`
