# QLR Service Pilot Report

- run_id: `qlr_service_pilot_20260427`
- status: `pass`
- service_csv: `D:\Desktop\Cluster Computing\paper-workbench-full\Users\liujinchun\Downloads\skills_codex\paper-workbench\data\processed\service_cohort_broad_v2018.csv`
- service_summary_csv: `D:\Desktop\Cluster Computing\paper-workbench-full\Users\liujinchun\Downloads\skills_codex\paper-workbench\data\processed\service_cohort_broad_summary_v2018.csv`
- selected_services: `app_2557, app_7264, app_1675, app_3665, app_521`
- metrics_csv_updated: `False`
- metrics_csv_hash_before: `0fa3fdb810ca0a0f74592d3adc92102c7a0ca67ea02c2b8c8f22435537f873ab`
- metrics_csv_hash_after: `0fa3fdb810ca0a0f74592d3adc92102c7a0ca67ea02c2b8c8f22435537f873ab`

## Scope Boundary

This run is a fixed five-service QLR pilot only. It does not run the full 139-service cohort, does not invoke Full UA-MSTCN, and does not change the manuscript headline conclusion. Passing this pilot permits only a separate full-run resource and execution plan; it does not automatically start full 139-service experiments.

## Selection Trace Discipline

The five services are fixed, and the trace records train+validation-prefix descriptors for audit. Service selection descriptors use only prefix load and burstiness computed from each time-sorted service series. Full-span summary descriptors are not used for selection. `coverage_ratio_metadata_only` is copied only for audit context.

## Replica Conversion Source

`median_container_request_cores` is read from `service_cohort_broad_summary_v2018.csv` only to convert CPU demand into equivalent replicas for policy simulation. It is not used for service selection.
No selected service required fallback from `median_container_request_cores` to `mean_container_request_cores`.

## Policy Parameter Reuse

The pilot reuses the existing service-policy semantics: `headroom_ratio`, `scale_out_quantile_margin`, `scale_in_safety_margin`, `cooldown_steps`, reactive thresholds, service `min_capacity=1.0`, and service `max_step_change=1.0`.

## Split Discipline

QLR fitting uses only the train+validation prefix. The held-out test split is used only for evaluation; no test rows are used for service selection, model selection, parameter selection, or policy tuning.

## Gate Checks

- Exactly five services and all five selection roles are present.
- Raw P90 and guarded P90 fields are both written to artifacts.
- Raw crossing count/rate are recorded; guarded crossing must be zero.
- Forecasting and policy metrics must be finite.
- Policy SLA violation must be in [0, 1] and capacities must be non-negative.
- `metrics.csv` must not be updated by the pilot.
- Pilot pass does not automatically start full 139-service experiments.

## Selection Profile

```csv
selection_role,app_du,prefix_rows,train_valid_split_end,load_mean_prefix,burst_cv_prefix,peak_to_mean_prefix,coverage_ratio_metadata_only,selection_rule,median_container_request_cores,mean_container_request_cores,all_service_load_median_prefix,all_service_burst_cv_median_prefix,eligible_service_count_prefix_only
low_load_low_burst,app_2557,9792,9792,175.8797715822444,0.297129228739197,2.930979471729321,0.97265625,fixed five-service pilot chosen from train+validation prefix load/burst quadrants; full-span summary descriptors are not used for selection,4.0,4.0,325.170386710239,0.37948061875536104,139
low_load_high_burst,app_7264,9792,9792,175.70736955337668,0.49605665788873293,3.1584332598605864,0.97265625,fixed five-service pilot chosen from train+validation prefix load/burst quadrants; full-span summary descriptors are not used for selection,8.0,8.0,325.170386710239,0.37948061875536104,139
high_load_low_burst,app_1675,9792,9792,445.9742888071901,0.3615890799652505,4.009707984398576,0.9727430555555556,fixed five-service pilot chosen from train+validation prefix load/burst quadrants; full-span summary descriptors are not used for selection,8.0,8.0,325.170386710239,0.37948061875536104,139
high_load_high_burst,app_3665,9792,9792,583.2465788398688,0.42360567284783407,2.987815782476762,0.9728298611111112,fixed five-service pilot chosen from train+validation prefix load/burst quadrants; full-span summary descriptors are not used for selection,4.0,4.0,325.170386710239,0.37948061875536104,139
median_anchor,app_521,9792,9792,329.15802389705874,0.3905142135413251,1.8084322932566952,0.9725694444444444,fixed five-service pilot chosen from train+validation prefix load/burst quadrants; full-span summary descriptors are not used for selection,4.0,4.0,325.170386710239,0.37948061875536104,139
```

## Forecasting Summary

```csv
horizon,service_count,mae_mean,p90_guarded_coverage_mean,raw_crossing_count_sum,guarded_crossing_count_sum
1,5,17.619147280834802,0.9127098321342926,22,0
5,5,29.046537715183707,0.8923076923076924,62,0
10,5,35.66150388274026,0.8758288125376733,47,0
```

## Policy Summary

```csv
policy_name,service_count,sla_violation_mean,over_provisioning_mean,under_provisioning_mean,scaling_actions_mean,average_capacity_mean
lagged_tracking_service,5,0.48786057692307694,5.1093795973557885,4.13530512319712,1661.2,120.5533295522836
qlr_predictive_service,5,0.019471153846153846,52.958111301980104,0.6078914863236292,366.4,171.9294748937814
reactive_service,5,0.015384615384615385,50.22279827724368,0.3070460737179469,331.6,153.89771314102566
```
