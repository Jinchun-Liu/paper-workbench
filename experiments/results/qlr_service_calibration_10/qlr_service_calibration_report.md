# QLR 10-Service Calibration Report

- run_id: `qlr_service_calibration_10_20260427`
- status: `pass`
- num_workers: `2`
- selected_services: `app_2557, app_7264, app_1675, app_3665, app_521, app_3422, app_141, app_2128, app_8205, app_7227`
- metrics_csv_hash_before: `0fa3fdb810ca0a0f74592d3adc92102c7a0ca67ea02c2b8c8f22435537f873ab`
- metrics_csv_hash_after: `0fa3fdb810ca0a0f74592d3adc92102c7a0ca67ea02c2b8c8f22435537f873ab`
- full_result_dir_exists: `False`

## Scope Boundary

This is a 10-service calibration only. It does not run the full 139-service experiment, does not invoke Full UA-MSTCN, and does not change the manuscript headline conclusion. Calibration pass does not automatically start full 139-service.

## Selection Discipline

The ten services are fixed from train+validation-prefix load, burst, and peak-to-mean descriptors. Test outcomes and full-span summary descriptors are not used for selection.
The test split is used only for evaluation; QLR fitting uses the train+validation prefix only, and test data are not used for parameter, model, service, or policy selection.

## Policy Parameter Reuse

The calibration reuses the existing service-policy semantics: service `min_capacity=1.0`, service `max_step_change=1.0`, config-driven headroom, quantile margin, scale-in safety, cooldown, and reactive thresholds.

## Replica Conversion Source

`median_container_request_cores` is read from the service summary only for replica conversion, not for service selection.
No selected service required fallback from `median_container_request_cores`.

## Gate Checks

- Exactly 10 services and all required selection roles are present.
- Raw P90 and guarded P90 fields are written to artifacts.
- Raw crossing count/rate are recorded; guarded crossing must be zero.
- Forecasting and policy metrics must be finite.
- Policy SLA violation must be in [0, 1] and capacities must be non-negative.
- Resource trace records runtime, worker id, output row counts, and estimated artifact size.
- `metrics.csv` must remain unchanged.
- `experiments/results/qlr_service_broad/` must not be created.
- Calibration pass does not automatically start full 139-service.

## Selection Profile

```csv
selection_role,app_du,prefix_rows,train_valid_split_end,load_mean_prefix,burst_cv_prefix,peak_to_mean_prefix,selection_rule,coverage_ratio_metadata_only,median_container_request_cores,mean_container_request_cores,all_service_load_median_prefix,all_service_burst_cv_median_prefix,all_service_peak_to_mean_median_prefix,eligible_service_count_prefix_only
pilot_low_load_low_burst,app_2557,9792,9792,175.8797715822444,0.297129228739197,2.930979471729321,fixed 10-service calibration selected from train+validation prefix descriptors; test outcomes and full-span summary descriptors are not used for selection,0.97265625,4.0,4.0,325.170386710239,0.37948061875536104,2.212661887808129,139
pilot_low_load_high_burst,app_7264,9792,9792,175.70736955337668,0.49605665788873293,3.1584332598605864,fixed 10-service calibration selected from train+validation prefix descriptors; test outcomes and full-span summary descriptors are not used for selection,0.97265625,8.0,8.0,325.170386710239,0.37948061875536104,2.212661887808129,139
pilot_high_load_low_burst,app_1675,9792,9792,445.9742888071901,0.3615890799652505,4.009707984398576,fixed 10-service calibration selected from train+validation prefix descriptors; test outcomes and full-span summary descriptors are not used for selection,0.9727430555555556,8.0,8.0,325.170386710239,0.37948061875536104,2.212661887808129,139
pilot_high_load_high_burst,app_3665,9792,9792,583.2465788398688,0.42360567284783407,2.987815782476762,fixed 10-service calibration selected from train+validation prefix descriptors; test outcomes and full-span summary descriptors are not used for selection,0.9728298611111112,4.0,4.0,325.170386710239,0.37948061875536104,2.212661887808129,139
pilot_median_anchor,app_521,9792,9792,329.15802389705874,0.3905142135413251,1.8084322932566952,fixed 10-service calibration selected from train+validation prefix descriptors; test outcomes and full-span summary descriptors are not used for selection,0.9725694444444444,4.0,4.0,325.170386710239,0.37948061875536104,2.212661887808129,139
cal_lowest_load_guard,app_3422,9792,9792,19.987471745642523,0.23169117023491892,2.769734997227388,fixed 10-service calibration selected from train+validation prefix descriptors; test outcomes and full-span summary descriptors are not used for selection,0.97265625,4.0,4.0,325.170386710239,0.37948061875536104,2.212661887808129,139
cal_highest_load_guard,app_141,9792,9792,4395.189755446612,0.35103301542962895,1.8482448127751498,fixed 10-service calibration selected from train+validation prefix descriptors; test outcomes and full-span summary descriptors are not used for selection,0.9728298611111112,8.0,8.0,325.170386710239,0.37948061875536104,2.212661887808129,139
cal_lowest_burst_guard,app_2128,9792,9792,114.58851239106731,0.19174671042362426,1.5806121941951254,fixed 10-service calibration selected from train+validation prefix descriptors; test outcomes and full-span summary descriptors are not used for selection,0.9724826388888888,4.0,4.0,325.170386710239,0.37948061875536104,2.212661887808129,139
cal_highest_burst_guard,app_8205,9792,9792,172.0446078431372,0.9053907246199697,3.552102025523481,fixed 10-service calibration selected from train+validation prefix descriptors; test outcomes and full-span summary descriptors are not used for selection,0.97265625,4.0,4.0,325.170386710239,0.37948061875536104,2.212661887808129,139
cal_peak_to_mean_guard,app_7227,9792,9792,93.25579452614376,0.7981172023658499,11.878940130518538,fixed 10-service calibration selected from train+validation prefix descriptors; test outcomes and full-span summary descriptors are not used for selection,0.97265625,4.0,4.0,325.170386710239,0.37948061875536104,2.212661887808129,139
```

## Forecasting Summary

```csv
model_name,horizon,service_count,mae_mean,mae_std,rmse_mean,mape_mean,p50_coverage_mean,p90_raw_coverage_mean,p90_guarded_coverage_mean,raw_crossing_count_sum,guarded_crossing_count_sum,fit_eval_ms_mean
quantile_linear_regression,1,10,21.19235988660665,28.09765054561182,37.32301077933904,0.05054760884091745,0.49232613908872896,0.909652278177458,0.9106115107913668,84,0,18855.93503000009
quantile_linear_regression,5,10,34.08258769463886,45.27229254955956,63.917003372632465,0.07065564147707908,0.48173076923076924,0.8970552884615385,0.8978966346153847,68,0,18841.241779999928
quantile_linear_regression,10,10,41.94879355572976,57.28139665342313,76.67002243388923,0.07981605821716531,0.47474382157926465,0.8871609403254974,0.8880650994575046,54,0,18055.60813000002
```

## Policy Summary

```csv
policy_name,service_count,sla_violation_mean,over_provisioning_mean,under_provisioning_mean,scaling_actions_mean,average_capacity_mean
lagged_tracking_service,10,0.48461538461538456,6.594395895933431,7.063171829927808,1659.3,138.51075171274016
qlr_predictive_service,10,0.022776442307692307,59.61285733891983,0.7099979325013172,403.8,197.88238705315305
reactive_service,10,0.015324519230769232,56.09007446915039,0.4629041466346179,300.6,176.47893349358927
```

## Resource Trace Summary

```csv
app_du,selection_role,planned_worker,process_id,runtime_wall_ms,fit_eval_ms_sum,forecast_rows,prediction_rows,policy_rows,policy_series_rows,estimated_service_artifact_bytes,gate_failure_count
app_141,cal_highest_load_guard,0,23360,49576.213800000005,49553.55570000029,3,4991,3,1664,969040,0
app_1675,pilot_high_load_low_burst,0,23360,53716.64609999971,53694.019999999,3,4991,3,1664,995775,0
app_2128,cal_lowest_burst_guard,1,3380,53271.55589999984,53252.080499999465,3,4991,3,1664,989025,0
app_2557,pilot_low_load_low_burst,0,23360,58681.57289999999,58639.60390000102,3,4991,3,1664,996427,0
app_3422,cal_lowest_load_guard,1,3380,61199.40290000068,61179.1390999997,3,4991,3,1664,979359,0
app_3665,pilot_high_load_high_burst,1,3380,51576.66739999968,51558.809299999666,3,4991,3,1664,1015190,0
app_521,pilot_median_anchor,0,23360,57192.79370000004,57170.95149999932,3,4991,3,1664,954583,0
app_7227,cal_peak_to_mean_guard,1,3380,58028.164299999844,58007.212000001346,3,4991,3,1664,974204,0
app_7264,pilot_low_load_high_burst,1,3380,64924.89290000049,64886.84210000065,3,4991,3,1664,1004739,0
app_8205,cal_highest_burst_guard,0,23360,49608.11839999951,49585.63529999992,3,4991,3,1664,986567,0
```
