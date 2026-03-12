# Cover Letter Draft

Dear Editors,

Please consider our manuscript entitled **"Trace-Driven Proactive Autoscaling for Cluster Workloads via Multi-Horizon Forecasting"** for publication in *Cluster Computing*.

This manuscript studies trace-driven proactive autoscaling using only public Alibaba cluster data. Its main contribution is a reproducible evaluation pipeline that spans an aggregate workload series, a 12-machine high-coverage cohort, a 3-fold zero-shot cross-machine transfer benchmark, and an audited broad service-level benchmark derived from the official container tables covering 139 `app_du` groups and 19,419 selected containers.

The results support a systems-oriented and deliberately non-overclaimed conclusion. On the aggregate and machine-level routes, simple linear models remain the strongest average point baselines, while the uncertainty-aware `UA-MSTCN-Lite` surrogate contributes calibrated upper quantiles that can drive predictive control. The audited broad service-level benchmark sharpens the boundary further: linear regression becomes the strongest average point forecaster, predictive control worsens mean SLA violation and mean scaling actions relative to reactive control, and the apparent average over-provisioning reduction is not stable under paired service bootstrap. For confidential peer review, the submitted version is already staged in a private GitHub review repository together with a frozen `review-freeze-2026-03-12` package; access can be granted immediately to editors and reviewers. Upon acceptance, the same package will be deposited publicly with a persistent identifier.

We believe this combination of reproducibility, multi-granularity evaluation, and explicit service-level trade-off analysis fits *Cluster Computing* well because the paper addresses forecasting and control for cluster resource management rather than presenting only a forecasting benchmark.

This manuscript is original, has not been published previously, and is not under consideration for publication elsewhere.

Sincerely,

Jinchun Liu
