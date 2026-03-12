# Execution Plan Snapshot

## Current target

- Working title: `Trace-Driven Proactive Autoscaling for Cluster Workloads via Multi-Horizon Forecasting`
- Data route: Alibaba `cluster-trace-v2018`
- First reproducible task: aggregate machine-level utilization into a cluster demand series, then compare reactive capacity control against predictive control

## Immediate commands

```bash
. .venv-paper/bin/activate
bash paper-workbench/experiments/preprocessing/download_v2018.sh
python paper-workbench/experiments/preprocessing/prepare_v2018_machine_usage.py \
  --input-tar paper-workbench/data/raw/machine_usage.tar.gz \
  --output-csv paper-workbench/data/processed/cluster_series_v2018.csv
python paper-workbench/experiments/run_baselines.py \
  --config paper-workbench/experiments/configs/default_v2018.yaml
python paper-workbench/experiments/run_policy_eval.py \
  --config paper-workbench/experiments/configs/default_v2018.yaml
cd paper-workbench/manuscript
latexmk -pdf main.tex
```

## Milestones

1. [x] Fetch metadata and large trace files.
2. [x] Build a clean one-minute aggregate workload series.
3. [x] Generate forecasting baseline metrics and smoke-test autoscaling metrics.
4. [ ] Export manuscript-ready figures from the verified final model.
5. [ ] Replace placeholder control results with numbers from a real trainable predictive model.
