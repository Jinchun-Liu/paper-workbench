# Working Literature Map

This file tracks the references that should shape the final `Related Work` section.
It is organized around the argument we want reviewers and editors to see.

## A. Target-journal precedent

- `Dinda2000HostLoad`: early `Cluster Computing` paper on host-load prediction using linear models.
- `Casalicchio2019ContainerAutoscaling`: `Cluster Computing` paper on container autoscaling metrics and performance evaluation.
- `Rossi2025UncertaintyAwareForecasting`: `Cluster Computing` paper on uncertainty-aware workload forecasting and transfer learning.

Use in manuscript:

- prove that `Cluster Computing` already publishes papers on load prediction, autoscaling, and uncertainty-aware workload management;
- show that our topic fits the journal's conversation rather than being a forced submission target.

## B. Trace datasets and workload characterization

- `reiss2012google`: Google cluster trace reference point.
- `alibabaclusterdata2026`: official Alibaba Cluster Trace Program entry point.
- `alibabav2018trace`: official v2018 dataset document.
- `Jiang2022Characterizing`: co-located workload characterization for Alibaba cloud datacenters.
- `guo2019limits`: Alibaba datacenter resource-efficiency bottleneck analysis.
- `luo2021characterizing`: Alibaba microservice dependency and performance characterization.
- `weng2022melaas`: GPU-cluster workload analysis in the wild.

Use in manuscript:

- justify public-trace realism,
- motivate workload diversity and burstiness,
- explain why trace-driven evaluation is meaningful even without a live deployment.

## C. Forecasting for cluster or cloud workloads

- `islam2012empirical`: early empirical cloud resource prediction.
- `Dinda2000HostLoad`: classical linear host-load prediction.
- `Calheiros2015ARIMAWorkload`: ARIMA forecasting and QoS impact.
- `Herbst2014ProactiveProvisioning`: proactive resource provisioning through classification and forecasting.
- `Baldan2018WorkloadForecasting`: workload forecasting methodology for cloud systems.
- `Song2017LSTMHostLoad`: LSTM-based host-load prediction.
- `Banerjee2021MultiStepPrediction`: multi-step workload prediction for cloud resource utilization.
- `Bi2021IntegratedDeepLearning`: joint workload and resource prediction.
- `Rossi2025UncertaintyAwareForecasting`: uncertainty-aware univariate and bivariate forecasting on Google and Alibaba traces.
- `salinas2020deepar`: probabilistic forecasting reference.
- `lim2021temporal`: multi-horizon forecasting reference.

Use in manuscript:

- show progression from statistical to deep and probabilistic forecasting,
- motivate multi-horizon prediction and uncertainty outputs,
- position the final UA-MSTCN design as a systems-oriented forecasting layer rather than a generic black-box benchmark.

## D. Autoscaling and elasticity control

- `lorido2014review`: autoscaling survey.
- `Mao2010DeadlineBudgetAutoscaling`: predictive scaling under explicit constraints.
- `Kim2017ProactiveAutoscaling`: proactive scaling using predicted network traffic in container environments.
- `AlDhuraibi2017ElasticDocker`: vertical elasticity for Docker containers.
- `Casalicchio2019ContainerAutoscaling`: metric-sensitive container autoscaling evaluation.
- `Burns2016BorgKubernetes`: operational background for large-scale container management.
- `Bernstein2014ContainersCloud`: containers-to-Kubernetes context.

Use in manuscript:

- distinguish reactive threshold policies from predictive control,
- show that container and cloud autoscaling has multiple design axes beyond forecasting accuracy alone,
- motivate the need for interpretable control logic and explicit safety margins.

## E. Uncertainty and transfer learning

- `Minarolli2017UncertaintyPrediction`: uncertainty in host overload and underload detection.
- `Weiss2016TransferLearning`: transfer-learning survey.
- `Ye2018TransferForecasting`: transfer learning for time-series forecasting.
- `Liu2022TRPredictior`: small-sample cloud workload prediction with transfer learning.
- `Hao2021TransferQoS`: transfer learning for QoS modeling.
- `Rossi2025UncertaintyAwareForecasting`: direct precedent that combines uncertainty and transfer learning in the target journal.

Use in manuscript:

- justify forecasting uncertainty as a control input,
- reserve room for later cross-workload or cross-dataset extensions,
- explain why the current draft keeps transfer learning in the discussion rather than over-claiming it as a completed contribution.

## F. Gap used by this manuscript

The final argument remains narrow and defensible:

1. Public-trace studies often stop at workload characterization.
2. Forecasting papers often do not show how predictive quality changes scaling decisions.
3. Autoscaling papers often depend on private infrastructure or platform-specific deployments.
4. The tractable gap is a reproducible, trace-driven, uncertainty-aware forecasting-to-control loop that stays close to the editorial scope of `Cluster Computing`.

## G. Immediate writing goals

- keep the current draft above `25` verified references now, then push toward the `35-45` target;
- cite target-journal precedent in both `Introduction` and `Related Work`;
- add a comparison table that makes the manuscript's positioning legible at a glance;
- connect every figure to one of the gaps above rather than adding decorative visuals.
