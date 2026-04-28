# Full UA-MSTCN Broad Calibration Report

- run_id: `full_ua_mstcn_broad_calibration_20260428`
- status: `pass`
- scope: broad calibration slice only; no held-out test evaluation and no full broad run.
- service_count: `139`
- train_windows: `71168`
- validation_windows: `17792`
- recommended_batch_size: `1024`
- metrics_csv_hash_before: `0fa3fdb810ca0a0f74592d3adc92102c7a0ca67ea02c2b8c8f22435537f873ab`
- metrics_csv_hash_after: `0fa3fdb810ca0a0f74592d3adc92102c7a0ca67ea02c2b8c8f22435537f873ab`

## Gate Result

- PASS: broad calibration gate passed.

## Batch Results

```csv
run_id,batch_size,hidden_width,epochs,max_train_batches_per_epoch,seen_train_batches,seen_train_windows,train_runtime_seconds,validation_runtime_seconds,train_windows_per_second,first_train_loss,last_train_loss,validation_loss,peak_cuda_memory_bytes,process_memory_rss_bytes
full_ua_mstcn_broad_calibration_20260428,512,64,2,120,240,122880,3.940817300011986,0.16368709999369457,31181.349107360613,0.0863374792970717,0.06698772571980953,0.13723647594451904,2555364864,1508483072
full_ua_mstcn_broad_calibration_20260428,1024,64,2,120,140,142336,4.2353398999985075,0.12479589998838492,33606.747831514105,0.09436627200671605,0.06985079289547035,0.14579559862613678,2555480064,1516589056
```
