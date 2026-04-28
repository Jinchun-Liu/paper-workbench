# Argument Logic Chain

Version: 2026-04-28 final concision pass

1. Target problem and scope
   - Predictive autoscaling may reduce reactive-delay waste, but trace-level evidence must connect forecasting, uncertainty, and control decisions.
   - Scope is public Alibaba trace evaluation, not live deployment proof.

2. Research gap
   - Prior work often separates forecasting metrics from policy behavior or depends on private/platform-specific evidence.
   - The revision therefore emphasizes reproducibility, leakage-free splits, and service-level boundary mapping.

3. Research question
   - Can public cluster traces support a reproducible predictive capacity-control evaluation that shows when predictive control improves or fails relative to reactive rules?

4. Evaluation move
   - Build one pipeline across aggregate series, 12-machine cohort, zero-shot machine transfer, and audited 139-service cohort.
   - Use point baselines, QLR, and the paper-specific `UA-MSTCN-Lite` uncertainty-aware surrogate.

5. Fair protocol
   - Use chronological splits.
   - Fit QLR and other models without test leakage.
   - Keep test split only for evaluation.
   - Preserve raw and guarded quantile outputs where QLR is used.

6. Result pattern
   - Linear regression is the strongest point-forecast baseline across the main benchmarks.
   - `UA-MSTCN-Lite` is not a point-forecast winner, but provides usable upper quantiles for control.
   - Aggregate predictive control reduces over-provisioning relative to reactive control.
   - Broad service-level control worsens SLA and scaling actions under equal-weighted service averaging, and the over-provisioning gain is not stable.

7. Licensed interpretation
   - The paper supports a reproducible benchmark and boundary map.
   - It does not support a universal predictive-control improvement claim or a full UA-MSTCN architectural superiority claim.

8. Boundary conditions
   - Service cohort is broad and audited but not a full service census.
   - `UA-MSTCN-Lite` is a lightweight surrogate, not the final deep UA-MSTCN.
   - Service-descriptor splits are descriptive, not causal identification.

9. Safe contribution statement
   - The strongest safe claim is an evaluation contribution: public-trace, leakage-free, multi-granularity evidence showing where predictive autoscaling helps, where linear baselines remain strong, and where a shared predictive policy breaks down under service heterogeneity.

10. Concision pass note
   - The 2026-04-28 pass compressed repeated explanation in the introduction, experimental setup, results, threats, and conclusion.
   - It preserved reviewer-required local edits, QLR reporting boundaries, and the manuscript's mixed-evidence main conclusion.
