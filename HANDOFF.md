# 项目交接文件

最后更新：2026-03-11

## 1. 任务目标

当前项目目标是在 `paper-workbench/` 下完成一篇可投稿到 EI 检索期刊的英文论文，主题为：

`Trace-Driven Proactive Autoscaling for Cluster Workloads via Multi-Horizon Forecasting`

当前主投期刊是 `Cluster Computing`，后备期刊是 `Journal of Grid Computing`。

这篇稿件的主线已经从“只有 aggregate 级别 smoke test”推进到：

- aggregate cluster evidence
- machine-level cohort evidence
- cross-machine transfer evidence
- service-level evidence from `container_meta + filtered container_usage`

当前最重要的任务不是继续换更深的 forecasting backbone，而是继续增强 `service/container-level` 证据，降低 construct validity 和 selection bias 风险。

## 2. 用户已明确的偏好

这些决策不要轻易推翻：

- 优先级 1：继续扩大 Alibaba `container_usage` 路线的 `service-level` 证据。
- 优先级 2：在 service-level 上做受控 tuning 或更稳健的 policy 验证。
- 优先级 3：只有在 container/service 路线短期无法推进时，才考虑更深 forecasting 模型。
- 不要把论文主叙事写成“我们有最强点预测精度”。
- 可以写成“uncertainty-aware surrogate 在 calibration 和 predictive control 接入上有价值”。
- service-level policy 结果必须如实陈述 trade-off，不能回避 SLA 恶化。

用户已经明确指出：当前最大的拒稿风险是 construct validity，不是 forecasting backbone 不够深。

## 3. 当前总体状态

先看这几个文件：

- `paper-workbench/00-status.md`
- `paper-workbench/HANDOFF.md`
- `paper-workbench/experiments/results/smoke-test-summary.md`
- `paper-workbench/manuscript/main.tex`
- `paper-workbench/manuscript/sections/method.tex`
- `paper-workbench/manuscript/sections/experiments.tex`
- `paper-workbench/manuscript/sections/results.tex`

当前状态摘要：

- 稿件已经切到官方 Springer `sn-jnl` 模板。
- 摘要已压到 `150` 词，满足：
  - `Cluster Computing`: `100-150` 词
  - `Journal of Grid Computing`: `150-250` 词
- `Statements and Declarations` 已补上。
- 旧的 `Workbench draft`、`Data and artifact status`、`current draft`、`local workspace` 等研发口吻已经移除。
- `method.tex` 已从单一 aggregate 形式改成 entity-level 形式，能覆盖 aggregate、machine、service 三层。
- 稿件当前可以编译通过。

## 4. 当前稿件与投稿合规状态

### 已完成

- 模板：`paper-workbench/manuscript/main.tex` 使用 `\documentclass[pdflatex,iicol,sn-mathphys-num]{sn-jnl}`
- 模板依赖已在稿件目录中：
  - `paper-workbench/manuscript/sn-jnl.cls`
  - `paper-workbench/manuscript/sn-mathphys-num.bst`
- 声明部分：
  - `paper-workbench/manuscript/sections/declarations.tex`
- 最新 PDF：
  - `paper-workbench/manuscript/main.pdf`

### 尚未完全收尾

- `main.tex` 里作者单位仍是占位：
  - `Affiliation to be confirmed before submission`
- 当前稿件仍通过 `\input{sections/...}` 组织。
  - 这对本地写作没问题。
  - 但 Springer 模板注释倾向于最终提交时合成单个 `.tex` 文件。
  - 如果进入正式投稿打包阶段，建议最后做一次 flatten。

## 5. 当前最重要的研究结论

请不要丢掉这些已经验证过的口径。

### 5.1 Aggregate cluster series

文件：

- `paper-workbench/data/processed/cluster_series_v2018.csv`
- `paper-workbench/experiments/results/metrics.csv`
- `paper-workbench/experiments/results/smoke-test-summary.md`

当前 aggregate CPU 结果：

- 1 分钟 horizon：线性回归最好，MAE `2.2682`
- 5 分钟 horizon：随机森林最好，MAE `3.9283`
- 10 分钟 horizon：线性回归最好，MAE `4.3066`

平均 MAE：

- `linear_regression`: `3.5140`
- `random_forest`: `3.5286`
- `ua_mstcn_lite_quantile_forest`: `3.5476`

结论：

- 当前数据下，`UA-MSTCN-Lite` 不是 aggregate 上最强点预测器。
- 不能再写成它全面优于线性/随机森林。

### 5.2 Quantile calibration

文件：

- `paper-workbench/experiments/results/tables/quantile_coverage.csv`
- `paper-workbench/experiments/results/figures/quantile_coverage.png`

aggregate 上 `P90` 覆盖率：

- `0.9199 / 0.8665 / 0.8679` for `1 / 5 / 10` min

结论：

- calibration 是当前 `UA-MSTCN-Lite` 最可写进论文的优势之一。

### 5.3 Machine-level cohort

文件：

- `paper-workbench/data/processed/machine_cohort_top12_v2018.csv`
- `paper-workbench/data/processed/machine_cohort_top12_summary_v2018.csv`
- `paper-workbench/experiments/results/machine_cohort/`

当前 machine cohort：

- `12` 台高覆盖机器
- 覆盖率范围：`0.9372` 到 `0.9472`
- 平均插补比例：`0.0581`

结果口径：

- 点预测上，线性回归仍是最稳的 baseline。
- `UA-MSTCN-Lite` 在 machine cohort 上仍保持可用的 quantile coverage。

### 5.4 Cross-machine transfer

文件：

- `paper-workbench/experiments/results/machine_transfer/`

当前结论：

- `3` 折 zero-shot transfer 下，pooled linear regression 几乎追平 entity-specific linear upper bound。
- `global_ua_mstcn_lite` 点预测不占优。
- 但 `P90` 覆盖率在 held-out machines 上仍可用。

这部分的正确写法是：

- transfer baseline 很强，说明当前数据中的线性结构比预期更强。
- uncertainty-aware surrogate 的价值更多体现在 calibration，而不是最优点预测。

### 5.5 Service-level cohort

这是当前论文最值钱的新增证据。

文件：

- `paper-workbench/data/processed/service_cohort_top10_v2018.csv`
- `paper-workbench/data/processed/service_cohort_top10_summary_v2018.csv`
- `paper-workbench/data/processed/service_cohort_top10_apps_v2018.csv`
- `paper-workbench/experiments/results/service_cohort_top10/`

当前 top10 service cohort 概况：

- `10` 个 `app_du`
- `2036` 个 selected containers
- `1970` 个 matched containers
- 统一 `11520` 分钟跨度
- 平均 observed-minute coverage：`0.9713`
- 平均 container hit ratio：`0.9564`

当前 10 个 `app_du`：

- `app_1063`
- `app_141`
- `app_1826`
- `app_2241`
- `app_3073`
- `app_3641`
- `app_512`
- `app_565`
- `app_6658`
- `app_7876`

service-level forecasting 结果：

- 平均 MAE 最低模型：`ua_mstcn_lite_quantile_forest = 7.4216`
- 其后是：
  - `random_forest = 7.4752`
  - `linear_regression = 7.7623`
  - `persistence = 8.1760`

service-level quantile coverage：

- `P90 = 0.8917 / 0.8826 / 0.8660` for `1 / 5 / 10` min

service-level policy 结果：

- reactive:
  - SLA violation `0.0103`
  - over-provisioning `5.1767`
  - actions `481.2`
- predictive:
  - SLA violation `0.0434`
  - over-provisioning `4.4567`
  - actions `428.8`

正确口径：

- predictive service policy 平均减少了 over-provisioning 和 scaling actions。
- 但平均 SLA violation 明显变差。
- 结果存在显著 service heterogeneity。
- 这意味着“service-level predictive control 是否值得采用”目前仍是开放问题。

不要把这部分写成无条件正结果。

## 6. 当前最重要的图表与结果文件

优先复用这些现有输出，不要重复造轮子：

- aggregate figures:
  - `paper-workbench/experiments/results/figures/cluster_workload_overview.png`
  - `paper-workbench/experiments/results/figures/resource_distribution_views.png`
  - `paper-workbench/experiments/results/figures/baseline_mae_by_horizon.png`
  - `paper-workbench/experiments/results/figures/forecast_case_study.png`
  - `paper-workbench/experiments/results/figures/forecast_latency_tradeoff.png`
  - `paper-workbench/experiments/results/figures/quantile_coverage.png`
  - `paper-workbench/experiments/results/figures/policy_pareto_sensitivity.png`
- machine cohort:
  - `paper-workbench/experiments/results/machine_cohort/figures/`
- machine transfer:
  - `paper-workbench/experiments/results/machine_transfer/figures/`
- service top10:
  - `paper-workbench/experiments/results/service_cohort_top10/figures/service_workload_overview.png`
  - `paper-workbench/experiments/results/service_cohort_top10/figures/service_forecasting_mae.png`
  - `paper-workbench/experiments/results/service_cohort_top10/figures/service_quantile_coverage.png`
  - `paper-workbench/experiments/results/service_cohort_top10/figures/service_policy_summary.png`
  - `paper-workbench/experiments/results/service_cohort_top10/figures/service_policy_by_app.png`

## 7. 实验环境

### Python

不要直接用系统 `python3` 跑实验。

当前可用环境是：

- `./.venv-paper/bin/python`

这个环境里已经确认可导入：

- `numpy`
- `pandas`
- `matplotlib`
- `yaml`
- `sklearn`

系统 `python3` 当前缺少至少 `pandas`，直接跑会报错。

推荐开工方式：

```bash
. .venv-paper/bin/activate
```

### LaTeX

当前可用：

- `latexmk` at `/Library/TeX/texbin/latexmk`
- TeX Live 2023

编译命令：

```bash
cd paper-workbench/manuscript
latexmk -pdf main.tex
```

## 8. 原始数据状态

### 已在本地

目录：`paper-workbench/data/raw`

当前已有：

- `machine_meta.tar.gz`
- `machine_usage.tar.gz`
- `container_meta.tar.gz`

### 尚未完整镜像到本地

- `container_usage.tar.gz`

说明：

- 官方 `container_usage.tar.gz` 约 `28 GiB` 压缩体积。
- 当前 service-level 实验不是基于完整本地镜像，而是基于 streamed filtered extraction。
- 相关背景见：
  - `paper-workbench/sources/alibaba-cluster-trace-v2018.md`

## 9. 关键脚本入口

### Aggregate / machine / transfer

- `paper-workbench/experiments/preprocessing/prepare_v2018_machine_usage.py`
- `paper-workbench/experiments/preprocessing/prepare_v2018_machine_cohort.py`
- `paper-workbench/experiments/run_baselines.py`
- `paper-workbench/experiments/run_policy_eval.py`
- `paper-workbench/experiments/run_machine_cohort_experiments.py`
- `paper-workbench/experiments/run_machine_transfer_experiments.py`
- `paper-workbench/experiments/run_extended_experiments.py`
- `paper-workbench/experiments/render_manuscript_figures.py`

### Service-level

- `paper-workbench/experiments/preprocessing/profile_v2018_container_usage_prefix.py`
- `paper-workbench/experiments/preprocessing/prepare_v2018_container_service_cohort.py`
- `paper-workbench/experiments/run_container_service_experiments.py`

### Forecasting / policy internals

- `paper-workbench/experiments/models/ua_mstcn.py`
- `paper-workbench/experiments/models/baselines.py`
- `paper-workbench/experiments/policies/autoscaling_simulator.py`
- `paper-workbench/experiments/configs/default_v2018.yaml`

## 10. 如果新线程要继续做什么，推荐顺序如下

### 第一优先级：继续扩大 service cohort

当前 top10 cohort 已经有价值，但还不够强，原因是：

- 仍然是 targeted high-coverage app selection
- 仍然不是 full population
- 仍然可能被 reviewer 质疑 selection bias

推荐做法：

1. 用 `profile_v2018_container_usage_prefix.py` 在更大的 `container_id` prefix 上继续 profile。
2. 找出更多满足以下条件的 `app_du`：
   - 较长 span
   - 足够多的 containers
   - 较高 container hit ratio
   - 较高 minute coverage ratio
3. 将当前 `top10` 扩到更大 cohort，例如 `top20` 或“规则筛选后全纳入”。
4. 重新运行 service forecasting 和 service policy benchmark。
5. 把新的 cohort 规模、选择规则、结论是否稳定写入论文。

建议不要直接把 `container_usage` 全量下载作为第一步，除非确实需要。先用 streamed prefix 扩大 cohort，性价比更高。

### 第二优先级：service-aware tuning，但必须受控

可以做，但不能写成 test-set 事后调参。

更稳的路线：

- 先保留 `global untuned policy` 作为主结果
- 再补一个 `held-out-service validated tuning` 或 `service-regime-aware tuning`
- 明确 tuning 规则不是针对测试服务手工调出来的

不要做的事情：

- 不要对每个 service 手动各调一套参数再直接汇报主结果
- 不要让 reviewer 觉得 policy improvement 只是 overfitting

### 第三优先级：只有前两项推进受阻时，再换更深模型

当前更深 forecasting 模型不是最急的，因为：

- 用户已经明确把 construct validity 放在更高优先级
- machine-level transfer 已经表明线性结构很强
- 再花大量时间换 backbone，不一定比扩大 service evidence 更能提高录用概率

## 11. 推荐的下一步命令

### 11.1 激活环境

```bash
cd /Users/liujinchun/Desktop/skills_codex
. .venv-paper/bin/activate
```

### 11.2 先用更大 prefix 做 service coverage profiling

示例：

```bash
python paper-workbench/experiments/preprocessing/profile_v2018_container_usage_prefix.py \
  --meta-tar paper-workbench/data/raw/container_meta.tar.gz \
  --usage-source http://aliopentrace.oss-cn-beijing.aliyuncs.com/v2018Traces/container_usage.tar.gz \
  --output-csv paper-workbench/data/processed/service_profile_prefix100000.csv \
  --max-container-id 100000 \
  --min-span-seconds 650000 \
  --min-containers 60
```

然后人工查看输出 CSV，筛更多 `app_du`。

### 11.3 构建更大的 service cohort

如果已经整理出一个 `selected_apps_file`，可以这样跑：

```bash
python paper-workbench/experiments/preprocessing/prepare_v2018_container_service_cohort.py \
  --meta-tar paper-workbench/data/raw/container_meta.tar.gz \
  --usage-source http://aliopentrace.oss-cn-beijing.aliyuncs.com/v2018Traces/container_usage.tar.gz \
  --output-csv paper-workbench/data/processed/service_cohort_next_v2018.csv \
  --summary-csv paper-workbench/data/processed/service_cohort_next_summary_v2018.csv \
  --selected-apps-csv paper-workbench/data/processed/service_cohort_next_apps_v2018.csv \
  --temp-filtered-csv paper-workbench/data/processed/service_cohort_next_filtered_container_usage.csv \
  --selected-apps-file paper-workbench/data/processed/service_candidate_apps_70500.txt \
  --chunk-size 400000 \
  --max-container-id 100000
```

注意：

- 当前 `service_candidate_apps_70500.txt` 只是一个历史中间产物，不是最终答案。
- 更合理的做法是生成新的候选列表，而不是盲目复用旧列表。

### 11.4 跑 service-level benchmark

```bash
python paper-workbench/experiments/run_container_service_experiments.py \
  --config paper-workbench/experiments/configs/default_v2018.yaml \
  --service-csv paper-workbench/data/processed/service_cohort_next_v2018.csv \
  --service-summary-csv paper-workbench/data/processed/service_cohort_next_summary_v2018.csv \
  --output-dir paper-workbench/experiments/results/service_cohort_next
```

### 11.5 重新编译论文

```bash
cd paper-workbench/manuscript
latexmk -pdf main.tex
```

## 12. 新线程修改论文时应遵守的口径

### 可以强调

- 论文已经不再只依赖 aggregate proxy。
- 已有 official Alibaba container-derived service-level evidence。
- `UA-MSTCN-Lite` 的价值主要在 uncertainty-aware calibration 和 predictive control coupling。
- predictive control 在 resource efficiency 与 service risk 之间存在可量化 trade-off。
- service heterogeneity 是真实发现，不是坏事。

### 不要强调

- 不要说 `UA-MSTCN-Lite` 在所有层级上都是最强点预测器。
- 不要说 predictive control 在 service-level 上“整体更优”。
- 不要写成已经完成 full-service population study。
- 不要把当前 surrogate 当成最终 full deep TCN 的等价物。

## 13. 尚未解决的人类输入项

这些项最终需要用户确认：

- 投稿作者单位
- 是否只有单作者
- 最终投稿期刊是否仍优先 `Cluster Computing`
- 是否要在最终打包前把 `main.tex` flatten 成单文件

当前 `main.tex` 里的 visible metadata：

- 作者名：`Jinchun Liu`
- 邮箱：`liujinchun114514@gmail.com`
- 单位：占位，未确认

## 14. 建议新线程开工的最短路径

如果上下文很少，按这个顺序重新建立认知：

1. 读 `paper-workbench/HANDOFF.md`
2. 读 `paper-workbench/00-status.md`
3. 读 `paper-workbench/experiments/results/smoke-test-summary.md`
4. 读 `paper-workbench/manuscript/main.tex`
5. 读 `paper-workbench/manuscript/sections/method.tex`
6. 读 `paper-workbench/manuscript/sections/results.tex`
7. 读 `paper-workbench/experiments/preprocessing/prepare_v2018_container_service_cohort.py`
8. 读 `paper-workbench/experiments/run_container_service_experiments.py`

如果时间只够做一件事，就做：

- 扩大 `service cohort` 并验证结论是否稳定

如果时间够做两件事，再加：

- 做受控的 service-aware tuning，而不是逐服务手工调参
