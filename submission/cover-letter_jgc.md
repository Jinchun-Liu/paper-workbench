# Cover Letter Draft (JGC)

Dear Editors,

Please consider our manuscript entitled **"Trace-Driven Proactive Autoscaling for Cluster Workloads via Multi-Horizon Forecasting"** for publication in *Journal of Grid Computing*.

This manuscript studies predictive autoscaling for distributed cluster workloads using only public Alibaba trace artifacts. Its main contribution is a reproducible evaluation pipeline that spans an aggregate workload series, a 12-machine high-coverage cohort, a 3-fold zero-shot cross-machine transfer benchmark, and an audited broad service-level benchmark derived from the official container tables covering 139 `app_du` groups and 19,419 selected containers.

The contribution is evaluative and systems-oriented rather than overclaimed as an algorithmic breakthrough. On the aggregate and machine-level routes, simple linear models remain the strongest average point baselines, while the uncertainty-aware `UA-MSTCN-Lite` surrogate contributes calibrated upper quantiles that can drive predictive control. On the audited broad service-level benchmark, linear regression becomes the strongest average point forecaster, predictive control worsens mean SLA violation and mean scaling actions relative to reactive control, and the apparent average over-provisioning reduction is not stable under paired service bootstrap. The manuscript source, preprocessing route, model training code, broad service-cohort construction scripts, figure-generation artifacts, and predictive-control simulator are released through the public reproducibility repository at `https://github.com/Jinchun-Liu/paper-workbench`. We believe this explicit boundary-mapping result fits *Journal of Grid Computing* because the paper addresses forecasting, control, and reproducible resource-management evidence for large-scale distributed systems.

This manuscript is original, has not been published previously, and is not under consideration for publication elsewhere.

Sincerely,

Jinchun Liu
Corresponding author, on behalf of all authors
