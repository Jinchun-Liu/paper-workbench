# 投稿后返修交接文档 / Revision Skill

最后更新：2026-03-13

## 1. 文档定位

这不是早期“继续把稿子做成可投稿稿”的 handoff。

当前稿件已经进入：

- `主投 Cluster Computing`
- `后备 Journal of Grid Computing`
- `双入口均可编译`
- `Cluster source package 已完成 clean-dir 校验`
- `private review repository + frozen review package 已准备`
- `处于提交后续返修 / 再投维护的合适状态，但本文件不假定“已经正式送审成功录入系统”`

因此，本文件现在的定位是：

- 供**投稿后续返修**使用的交接文档
- 供新线程快速接手的**背景叙述文档**
- 供 Codex 在收到“请读取 reviewer_feedback 并返修”“请修格式/题名页/投稿包”“请针对审稿意见补强 service-level 解释”时，直接当作**返修 skill**使用的执行手册

默认假设：

- 文章主线已经冻结为当前 broad 139-service 版本
- 后续工作应以**最小必要返修**为原则
- 不再为了“更完整”而重新设计整篇论文或扩张大量新实验

## 2. Skill-Style 使用方式

### 2.1 何时触发

当用户提出以下类型请求时，应优先把本文件当成返修 skill 使用：

- “读取 `reviewer_feedback.md` 并根据最新建议修改论文”
- “根据编辑/审稿意见修改 title page / abstract / declarations / cover letter”
- “修正某页表格、图片、caption、溢出、重叠、投稿包”
- “同步 Cluster / JGC 版本差异”
- “校正 service-level claim”
- “补一层最小机制分析 / 统计说明，而不是重做论文”

### 2.2 默认工作流

1. 读取本文件。
2. 读取 [00-status.md](/Users/liujinchun/Downloads/skills_codex/paper-workbench/00-status.md)。
3. 读取 [reviewer_feedback.md](/Users/liujinchun/Downloads/skills_codex/paper-workbench/review/reviewer_feedback.md) 最新一轮或最新几轮。
4. 只打开与该评论直接相关的稿件文件、结果表和投稿包文件。
5. 修改后必须：
   - 重编译 [main.tex](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.tex)
   - 如改到共享 section，也重编译 [main_jgc.tex](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main_jgc.tex)
   - 对受影响页面做视觉检查
   - 如改到提交相关内容，重建 [cluster-computing.zip](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/source-package/cluster-computing.zip)

### 2.3 成功标准

一轮返修默认只有在以下条件都满足时才算完成：

- claim 与当前证据一致
- 受影响页面无新的重叠、溢出、截断
- 相关 journal variant 编译通过
- 如果动了投稿源包，clean-dir 校验通过
- 若本轮属于正式审稿应对，已将评审结论追加到 [reviewer_feedback.md](/Users/liujinchun/Downloads/skills_codex/paper-workbench/review/reviewer_feedback.md)

## 3. 当前规范性快照

### 3.1 稿件身份

- 题目：
  `Trace-Driven Proactive Autoscaling for Cluster Workloads via Multi-Horizon Forecasting`
- 主投：
  `Cluster Computing`
- 后备：
  `Journal of Grid Computing`
- 当前页数：
  - [main.pdf](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.pdf) `20` 页
  - [main_jgc.pdf](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main_jgc.pdf) `20` 页

### 3.2 当前题名页

当前 title page 已按 Springer `sn-jnl` 模板下的最稳妥写法收口：

- 作者：
  - `Jinchun Liu^1*`
  - `Haoxun Li^1`
- 单位：
  - `Hainan International College, Communication University of China, No. 1 Dingfuzhuang East Street, Chaoyang District, Beijing 100024, China`
- 通讯作者信息：
  - `*Corresponding author: Jinchun Liu`
  - `E-mail: ljc20041122@qq.com`
  - `Tel.: +86 18010695863`
  - `Fax: N/A`

题名页源码入口：

- [main.tex](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.tex)
- [main_jgc.tex](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main_jgc.tex)

### 3.3 投稿与复现工件

当前已就绪的提交/审稿工件：

- Cluster 源包：
  - [cluster-computing.zip](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/source-package/cluster-computing.zip)
- Cluster 源包构建脚本：
  - [build_submission_package.py](/Users/liujinchun/Downloads/skills_codex/paper-workbench/scripts/build_submission_package.py)
- Cluster manifest：
  - [cluster-source-package-manifest.yaml](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/cluster-source-package-manifest.yaml)
- frozen review package：
  - [review-freeze-2026-03-12.tar.gz](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/frozen-package/review-freeze-2026-03-12.tar.gz)
- 审稿期复现说明：
  - [reproducibility-package.md](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/reproducibility-package.md)

当前声明口径是：

- 审稿期间提供 `private review repository + frozen review package`
- 录用后发布公开仓库与持久标识符

## 4. 当前论文应坚持的主定位

全文主定位已经冻结为：

`reproducible public-trace evaluation + multi-granularity evidence + service-level boundary mapping`

这篇文章现在应被包装成：

- `evaluation / benchmark / evidence` 论文

而不是：

- `universally superior new controller`
- `state-of-the-art forecasting backbone paper`
- `full-population service autoscaling proof`

一句话安全口径：

> 公共 Alibaba trace 支持可复核的 predictive-autoscaling 评估；aggregate、machine、transfer 与 broad service-level 证据共同说明 predictive route 的价值主要在 calibration-aware evaluation 与 trade-off mapping，而不是 blanket superiority。

## 5. 不可越界的 claim 约束

### 5.1 可以说

- 论文已经不再只依赖 aggregate proxy。
- 论文包含 aggregate、machine、transfer、broad service 四层证据。
- `UA-MSTCN-Lite` 的核心价值在 uncertainty-aware quantile / calibration 和 control coupling。
- broad service-level 结果揭示了 shared global predictive policy 的失效边界。
- mixed / negative finding 在 public trace 上仍有科学价值，因为它明确了 heterogeneity 下何时不该声称 predictive autoscaling 有稳定收益。

### 5.2 不可以说

- 不要说 `UA-MSTCN-Lite` 是全层级最强点预测器。
- 不要说 predictive control 在 service-level 上被证明整体更优。
- 不要说 over-provisioning 改善在 broad service cohort 上“稳定成立”。
- 不要说 scaling actions 在 service-level 上“稳定下降”。
- 不要把当前 service cohort 写成 full-population claim。
- 不要把稿件包装成强算法突破；它的 novelty 类型不是 framework/algorithm-first。

## 6. 当前证据主线

这一节是返修时最重要的事实底座。所有 claim 都应以这里为准。

### 6.1 Aggregate forecasting

关键工件：

- [metrics.csv](/Users/liujinchun/Downloads/skills_codex/paper-workbench/experiments/results/metrics.csv)
- [quantile_coverage.csv](/Users/liujinchun/Downloads/skills_codex/paper-workbench/experiments/results/tables/quantile_coverage.csv)
- [smoke-test-summary.md](/Users/liujinchun/Downloads/skills_codex/paper-workbench/experiments/results/smoke-test-summary.md)

当前 aggregate headline：

- 平均 MAE 排名：
  - `linear_regression = 3.514`
  - `random_forest = 3.529`
  - `UA-MSTCN-Lite = 3.548`
  - `MLP = 3.708`

解释：

- `UA-MSTCN-Lite` 在 aggregate 上不是最强平均点预测 baseline。
- 线性模型与随机森林都必须被诚实保留为强 baseline。

### 6.2 Aggregate quantile / calibration

当前 aggregate `P90` 覆盖率：

- `1 min = 0.920`
- `5 min = 0.867`
- `10 min = 0.868`

解释：

- calibration 仍是当前 uncertainty-aware surrogate 的主要正向价值。
- 这也是 aggregate predictive policy 可写性的主要来源。

### 6.3 Aggregate control

当前 aggregate 三策略结果来自 [results.tex](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/results.tex) 的 Table 11：

- reactive threshold:
  - `SLA = 0.001`
  - `Over = 0.351`
  - `Actions = 43`
  - `Capacity = 0.821`
- lagged target tracking:
  - `SLA = 0.471`
  - `Over = 0.013`
  - `Actions = 1616`
  - `Capacity = 0.469`
- predictive:
  - `SLA = 0.035`
  - `Over = 0.141`
  - `Actions = 589`
  - `Capacity = 0.610`

解释：

- aggregate 上 predictive policy 有明确 trade-off story：
  - 比 reactive 更冒险
  - 但明显减少 over-provisioning 与 capacity
  - 同时远优于 naive lagged target chasing

### 6.4 Machine cohort

关键工件：

- [machine_cohort_summary.csv](/Users/liujinchun/Downloads/skills_codex/paper-workbench/experiments/results/machine_cohort/tables/machine_cohort_summary.csv)
- [machine_cohort](/Users/liujinchun/Downloads/skills_codex/paper-workbench/experiments/results/machine_cohort)

当前 machine headline：

- `12` 台高覆盖机器
- 线性回归在点预测上仍是最稳 baseline
- `UA-MSTCN-Lite` 保持可用 quantile coverage，但不主导点预测

### 6.5 Cross-machine transfer

关键工件：

- [machine_transfer_summary.csv](/Users/liujinchun/Downloads/skills_codex/paper-workbench/experiments/results/machine_transfer/tables/machine_transfer_summary.csv)

当前 transfer headline：

- pooled global linear regression 与 entity-specific linear upper bound 差距极小：
  - `1 min = -0.004`
  - `5 min = -0.017`
  - `10 min = -0.013`
- global MLP 是第二梯队
- global `UA-MSTCN-Lite` 不占点预测优势

解释：

- 这部分不能被写成“复杂模型 transfer 获胜”。
- 它支持的是：
  - 当前 trace 的线性结构比预期更强
  - calibration-aware surrogate 的价值不在最优 point forecast

### 6.6 Broad service cohort

这是当前稿件最核心的主结果。

关键工件：

- [service_cohort_broad_summary_v2018.csv](/Users/liujinchun/Downloads/skills_codex/paper-workbench/data/processed/service_cohort_broad_summary_v2018.csv)
- [service_cohort_top10_overlap_audit.csv](/Users/liujinchun/Downloads/skills_codex/paper-workbench/data/processed/service_cohort_top10_overlap_audit.csv)
- [service_cohort_promotion_decision.csv](/Users/liujinchun/Downloads/skills_codex/paper-workbench/experiments/results/service_cohort_broad/tables/service_cohort_promotion_decision.csv)
- [service_cohort_stability_summary.csv](/Users/liujinchun/Downloads/skills_codex/paper-workbench/experiments/results/service_cohort_broad/tables/service_cohort_stability_summary.csv)

当前 broad cohort 事实：

- `139` 个 `app_du`
- `19,419` selected containers
- `19,269` matched containers
- 统一 `11,520` 分钟共享窗口
- mean coverage ratio `0.9727`
- mean container hit ratio `0.9932`
- top10 overlap audit 中原 `top10` 全部 retained

promotion decision 已固定：

- `forecast_headline_flip`
- `scaling_actions_sign_flip`
- `over_provisioning_mean_negative_but_not_stable`

因此 broad 被**升格为主结果**，top10 只保留为历史/对照背景。

### 6.7 Broad service forecasting

关键工件：

- [service_forecasting_summary.csv](/Users/liujinchun/Downloads/skills_codex/paper-workbench/experiments/results/service_cohort_broad/tables/service_forecasting_summary.csv)

当前 broad service forecasting headline：

- `linear_regression` 为最强平均点预测 baseline
- broad cohort 平均 MAE：
  - `linear_regression = 32.571`
  - `persistence = 33.381`
  - `MLP = 37.066`
  - `UA-MSTCN-Lite = 37.787`

解释：

- 这与早期 top10 路线相反。
- 返修时若 reviewer 质疑“为何不强调 UA 模型优势”，必须直接回到 broad audited result。

### 6.8 Broad service quantile

关键工件：

- [service_quantile_coverage_summary.csv](/Users/liujinchun/Downloads/skills_codex/paper-workbench/experiments/results/service_cohort_broad/tables/service_quantile_coverage_summary.csv)

当前 broad service `P90` 覆盖率：

- `1 min = 0.921`
- `5 min = 0.896`
- `10 min = 0.877`

解释：

- 即使 broad cohort 上 point forecast 不占优，upper quantile 仍然“足够可用”，因此 predictive controller 的存在仍有方法论上的合理性。

### 6.9 Broad service policy

关键工件：

- [service_policy_delta_summary.csv](/Users/liujinchun/Downloads/skills_codex/paper-workbench/experiments/results/service_cohort_broad/tables/service_policy_delta_summary.csv)
- [service_policy_summary.csv](/Users/liujinchun/Downloads/skills_codex/paper-workbench/experiments/results/service_cohort_broad/tables/service_policy_summary.csv)

当前 predictive-minus-reactive 主统计量是：

- `resampling unit = service`
- `paired bootstrap`
- `n = 10000`
- `fixed seed = 20260311`
- `primary = equal-weighted mean delta`
- `auxiliary = load-weighted mean delta`

当前 broad service headline：

- SLA:
  - mean delta `+0.0138`
  - 95% CI `[0.0035, 0.0271]`
  - median `+0.0036`
  - IQR `[0.0000, 0.0087]`
  - `stable degradation`
- Over-provisioning:
  - mean delta `-2.633`
  - 95% CI `[-6.953, 2.328]`
  - median `-8.176`
  - IQR `[-17.667, 2.216]`
  - `not stable`
- Scaling actions:
  - mean delta `+150.4`
  - 95% CI `[114.0, 185.0]`
  - median `+193.0`
  - IQR `[22.5, 295.0]`
  - `stable degradation`

解释：

- broad route **不支持**“service-level action reduction”
- broad route **不支持**“service-level over-provisioning stable improvement”
- broad route **明确支持**：
  - SLA 恶化稳定存在
  - action penalty 稳定存在
  - over-provisioning 改善只在均值/中位数层面部分存在，但不稳定

### 6.10 Broad service mechanism layer

关键工件：

- [service_policy_subgroup_summary.csv](/Users/liujinchun/Downloads/skills_codex/paper-workbench/experiments/results/service_cohort_broad/tables/service_policy_subgroup_summary.csv)
- [service_policy_outcome_taxonomy.csv](/Users/liujinchun/Downloads/skills_codex/paper-workbench/experiments/results/service_cohort_broad/tables/service_policy_outcome_taxonomy.csv)
- [service_policy_delta_distribution.png](/Users/liujinchun/Downloads/skills_codex/paper-workbench/experiments/results/service_cohort_broad/figures/service_policy_delta_distribution.png)

当前 mechanism headline：

- SLA penalty 在：
  - high burstiness
  - high lag-1 autocorrelation
 组更强
- 平均 over-provisioning gain 主要出现在：
  - low burstiness
  - low mean load
 组
- taxonomy 最大类是：
  - `Over improved, SLA worsened = 87 / 139`
- 同时改善 SLA 和 Over 的服务仅：
  - `6 / 139`

解释：

- broad 结果不是“predictive 对所有服务都失败”
- 正确写法是：
  - shared global predictive policy 主要用更差的 SLA 和更多的 actions 去交换一部分服务的 over-provisioning 改善
  - 且最严重的 SLA 惩罚集中在更 bursty、更 persistent 的服务上

## 7. 当前稿件与投稿包的已知状态

### 7.1 当前编译状态

已确认通过：

- [main.tex](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.tex)
- [main_jgc.tex](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main_jgc.tex)

### 7.2 当前仍存在的日志级噪声

这些目前是**非阻塞**，因为在 PDF 里没有形成可见错误：

- [main.log#L649](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.log#L649)
  related-work 表头约 `2.3pt` overfull
- [main.log#L942](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.log#L942)
  `service_workload_overview` 的 float-too-large warning
- [main.log#L1258](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.log#L1258)
  约 `0.6pt` overfull

如果 reviewer 没有专门指出这些页，不必为了清零 warning 而引入新的页面漂移。

### 7.3 当前已完成的提交包装

当前 Cluster 提交包已经满足：

- dependency-driven copy
- local figures
- no external workspace dependency
- clean-dir LaTeX compile verified

不要再把 repo 内的多文件结构误认为“提交源包不可用”。
当前 repo 仍是多文件工作树；提交包已经单独 staged 并验证。

## 8. 最可能出现的返修主题

后续返修大概率集中在以下几类，而不是重做整篇：

### 8.1 Claim consistency

高概率 reviewer comment：

- “正文仍有局部句子暗示 method superiority”
- “abstract / introduction / conclusion 与 results 的 broad evidence 不完全一致”

处理原则：

- 优先改 wording，不优先加实验
- 先对照 [service_cohort_stability_summary.csv](/Users/liujinchun/Downloads/skills_codex/paper-workbench/experiments/results/service_cohort_broad/tables/service_cohort_stability_summary.csv)
- 一律以 broad result 为准，不再回退到 top10 headline

### 8.2 Service-level mechanism explanation

高概率 reviewer comment：

- “为什么 predictive 在 broad cohort 上失败？”
- “哪些服务更容易受益或受害？”

处理原则：

- 先用现成的 descriptor split、taxonomy、distribution figure
- 不要第一反应就新增大模型实验
- 这类评论优先使用：
  - [service_policy_subgroup_summary.csv](/Users/liujinchun/Downloads/skills_codex/paper-workbench/experiments/results/service_cohort_broad/tables/service_policy_subgroup_summary.csv)
  - [service_policy_outcome_taxonomy.csv](/Users/liujinchun/Downloads/skills_codex/paper-workbench/experiments/results/service_cohort_broad/tables/service_policy_outcome_taxonomy.csv)
  - [service_policy_delta_distribution.png](/Users/liujinchun/Downloads/skills_codex/paper-workbench/experiments/results/service_cohort_broad/figures/service_policy_delta_distribution.png)

### 8.3 External validity / selection bias

高概率 reviewer comment：

- “service cohort 是否 convenience sample？”
- “为何不是全量服务？”

处理原则：

- 强调 audited broad selection rule 与 top10 overlap audit
- 强调这是高质量 broad subset，不是 full population
- 不能装作已经完成全量服务研究

### 8.4 Reproducibility / availability

高概率 reviewer comment：

- “代码和工件能否访问？”
- “为何不是公开仓库/DOI？”

处理原则：

- 当前回答应基于：
  - private review repository
  - frozen review package
  - acceptance 后 public archive / DOI plan
- 若无真实 DOI，不要在正文或声明里虚构 public archive

### 8.5 Format / title page / source package

高概率 editor comment：

- title page 联系方式
- declarations placement
- source package 自包含性
- figure/table layout

处理原则：

- 优先走最小排版修补
- 保持当前 title-page contact block 风格
- 若动到提交包，必须重建 cluster zip

## 9. 返修时不要做的事

- 不要把 broad 主结果改回 top10 主线。
- 不要为了 reviewer 的“能不能更强一点”临时堆一个大模型主实验。
- 不要做按服务逐个手调参数后直接拿来替代主结果。
- 不要把 mixed result 改写成正向性能故事。
- 不要重构整篇文章结构，除非 editor 明确要求。
- 不要覆盖 [reviewer_feedback.md](/Users/liujinchun/Downloads/skills_codex/paper-workbench/review/reviewer_feedback.md) 历史轮次；只能追加。

## 10. 文件地图

### 10.1 稿件主入口

- [main.tex](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.tex)
- [main_jgc.tex](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main_jgc.tex)

### 10.2 最常改的正文 section

- [abstract.tex](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/abstract.tex)
- [abstract_jgc.tex](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/abstract_jgc.tex)
- [introduction.tex](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/introduction.tex)
- [experiments.tex](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/experiments.tex)
- [results.tex](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/results.tex)
- [threats.tex](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/threats.tex)
- [conclusion.tex](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/conclusion.tex)
- [declarations.tex](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/declarations.tex)

### 10.3 审稿与交付文档

- [reviewer_feedback.md](/Users/liujinchun/Downloads/skills_codex/paper-workbench/review/reviewer_feedback.md)
- [00-status.md](/Users/liujinchun/Downloads/skills_codex/paper-workbench/00-status.md)
- [checklist.md](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/checklist.md)
- [cover-letter.md](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/cover-letter.md)
- [cover-letter_jgc.md](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/cover-letter_jgc.md)
- [highlights.md](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/highlights.md)

### 10.4 broad service 核心结果目录

- [service_cohort_broad](/Users/liujinchun/Downloads/skills_codex/paper-workbench/experiments/results/service_cohort_broad)

最常用的表：

- [service_cohort_promotion_decision.csv](/Users/liujinchun/Downloads/skills_codex/paper-workbench/experiments/results/service_cohort_broad/tables/service_cohort_promotion_decision.csv)
- [service_cohort_stability_summary.csv](/Users/liujinchun/Downloads/skills_codex/paper-workbench/experiments/results/service_cohort_broad/tables/service_cohort_stability_summary.csv)
- [service_forecasting_summary.csv](/Users/liujinchun/Downloads/skills_codex/paper-workbench/experiments/results/service_cohort_broad/tables/service_forecasting_summary.csv)
- [service_policy_delta_summary.csv](/Users/liujinchun/Downloads/skills_codex/paper-workbench/experiments/results/service_cohort_broad/tables/service_policy_delta_summary.csv)
- [service_policy_subgroup_summary.csv](/Users/liujinchun/Downloads/skills_codex/paper-workbench/experiments/results/service_cohort_broad/tables/service_policy_subgroup_summary.csv)
- [service_policy_outcome_taxonomy.csv](/Users/liujinchun/Downloads/skills_codex/paper-workbench/experiments/results/service_cohort_broad/tables/service_policy_outcome_taxonomy.csv)

### 10.5 提交打包脚本

- [build_submission_package.py](/Users/liujinchun/Downloads/skills_codex/paper-workbench/scripts/build_submission_package.py)
- [build_repro_package.py](/Users/liujinchun/Downloads/skills_codex/paper-workbench/scripts/build_repro_package.py)

## 11. 返修的标准操作命令

### 11.1 编译主稿

```bash
cd /Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript
latexmk -pdf main.tex
```

### 11.2 编译 JGC 备稿

```bash
cd /Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript
latexmk -pdf main_jgc.tex
```

### 11.3 重建 Cluster 提交源包

```bash
python3 /Users/liujinchun/Downloads/skills_codex/paper-workbench/scripts/build_submission_package.py \
  --manifest /Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/cluster-source-package-manifest.yaml \
  --output /Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/source-package/cluster-computing \
  --archive \
  --verify
```

### 11.4 重建 frozen reproducibility package

```bash
python3 /Users/liujinchun/Downloads/skills_codex/paper-workbench/scripts/build_repro_package.py \
  --manifest /Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/reproducibility-package-manifest.yaml \
  --output /Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/frozen-package/review-freeze-2026-03-12 \
  --archive
```

### 11.5 做视觉检查

当前本机可用的稳定路线是用 `gs` 将 PDF 渲染为 PNG 后检查。

示例：

```bash
gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -r200 \
  -dFirstPage=14 -dLastPage=16 \
  -sOutputFile=/tmp/check_%02d.png \
  /Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.pdf
```

## 12. 处理新审稿意见时的建议顺序

1. 先读 [reviewer_feedback.md](/Users/liujinchun/Downloads/skills_codex/paper-workbench/review/reviewer_feedback.md) 最新一轮。
2. 判断它属于哪一类：
   - format / title page / source package
   - claim wording
   - service-level mechanism
   - external validity
   - availability / reproducibility
   - layout / figure / table
3. 只动最小必要文件。
4. 如果评论涉及数字或 claim，先核对 CSV，再改正文。
5. 如果评论涉及 service-level 解释，优先用现有 subgroup / taxonomy / delta figure。
6. 若本轮确实新增稳定实验结果，再同步：
   - [00-status.md](/Users/liujinchun/Downloads/skills_codex/paper-workbench/00-status.md)
   - [dataset_manifest.yaml](/Users/liujinchun/Downloads/skills_codex/paper-workbench/experiments/dataset_manifest.yaml)
   - [evidence-ledger.csv](/Users/liujinchun/Downloads/skills_codex/paper-workbench/literature/evidence-ledger.csv)
7. 完成后追加新一轮 reviewer log，不覆盖旧轮次。

## 13. 如果上下文非常少，最短恢复路径

如果新线程时间很紧，只按下面顺序恢复上下文：

1. 读本文件
2. 读 [00-status.md](/Users/liujinchun/Downloads/skills_codex/paper-workbench/00-status.md)
3. 读 [reviewer_feedback.md](/Users/liujinchun/Downloads/skills_codex/paper-workbench/review/reviewer_feedback.md) 末尾
4. 读 [main.tex](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.tex)
5. 读 [results.tex](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/results.tex)
6. 读 [experiments.tex](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/experiments.tex)
7. 读 broad service 结果表

## 14. 一句话停机条件

只要：

- broad 139-service 主结果不被破坏
- claim 与证据一致
- 格式与提交包可用
- 新评论得到最小但充分的响应

就停止返修，不要再为了“也许还能更完整”而扩张任务。
