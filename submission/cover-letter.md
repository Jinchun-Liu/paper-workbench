# Cover Letter

Dear Editors,

Please consider our Original Article entitled "Trace-Driven Proactive Autoscaling for Cluster Workloads via Multi-Horizon Forecasting" for publication in *Cluster Computing*.

This work studies predictive autoscaling on public Alibaba traces and asks whether a reproducible forecasting-to-control pipeline can provide trustworthy evidence across aggregate, machine, transfer, and service-level settings. The manuscript addresses a practical systems question in cluster resource management: whether predictive control on public traces yields useful operating trade-offs relative to reactive rules once the evidence is widened beyond a single aggregate workload series.

The study contributes a reproducible multi-granularity evaluation pipeline spanning an aggregate workload series, a 12-machine high-coverage cohort, a 3-fold zero-shot cross-machine transfer benchmark, and an audited broad service-level cohort derived from the official container tables covering 139 `app_du` groups and 19,419 selected containers. The results support a calibrated rather than overclaimed conclusion. On the aggregate and machine routes, simple linear models remain the strongest average point baselines, while the uncertainty-aware `UA-MSTCN-Lite` surrogate contributes usable upper-quantile forecasts for predictive control. On the audited broad service-level cohort, linear regression becomes the strongest average point forecaster, predictive control increases mean SLA violation and mean scaling actions relative to reactive control, and the apparent mean over-provisioning reduction is not stable under paired service bootstrap. We believe this explicit boundary-mapping result is important because it shows how public traces can support honest predictive-autoscaling evaluation rather than only positive performance claims.

We believe the manuscript is appropriate for *Cluster Computing* because it focuses on forecasting and control for cluster resource management, uses public large-scale trace evidence, and speaks directly to the journal's readership in networks, software tools, and distributed systems applications. The manuscript source, preprocessing route, model training code, broad service-cohort construction scripts, figure-generation artifacts, and predictive-control simulator are released through the public reproducibility repository at `https://github.com/Jinchun-Liu/paper-workbench`.

We confirm that this manuscript has not been published elsewhere and is not under consideration by another journal. All authors have approved the manuscript and agree with its submission to *Cluster Computing*.

Corresponding author:
Jinchun Liu
E-mail: ljc20041122@qq.com
Tel.: +86 18010695863

Sincerely,

Jinchun Liu
Corresponding author, on behalf of all authors
