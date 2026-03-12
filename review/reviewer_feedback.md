# Reviewer Feedback Log

本文件为累计审稿日志。后续每次收到“审稿 / 复审 / 更新反馈”请求时，在文件末尾追加新一轮记录，不覆盖既有内容。

> 注：当前项目树下 `review/` 目录在本轮前不存在，因此 Round 001-003 采用重建摘要，Round 004 为基于本轮最新稿件的完整评阅。

## 固定审稿基线

- 主投：`Cluster Computing`
- 后备：`Journal of Grid Computing`
- 评分维度：`journal fit`、`novelty and contribution`、`problem formulation`、`method soundness`、`experimental rigor`、`reproducibility and transparency`、`writing and organization`、`format and submission compliance`
- 严重级别：`Blocker`、`Major`、`Minor`、`Editorial`

## Round 001 (reconstructed)

- `review_round`: `001`
- `review_date`: `2026-03-11`
- `overall_verdict_cluster`: `Major Revision`
- `overall_verdict_jgc`: `Major Revision`
- 核心结论：早期稿件仍是 `workbench draft`，模板、摘要长度、声明项、元叙述和方法-实现一致性均明显不足。

## Round 002 (reconstructed)

- `review_round`: `002`
- `review_date`: `2026-03-11`
- `overall_verdict_cluster`: `Major Revision`
- `overall_verdict_jgc`: `Major Revision`
- 核心结论：新增 cross-machine transfer 是有效加分项，但同时证明 machine-level proxy 上 simple linear baseline 已经很强，单纯继续卷深模的边际价值受限。

## Round 003 (reconstructed)

- `review_round`: `003`
- `review_date`: `2026-03-11`
- `overall_verdict_cluster`: `Major Revision`
- `overall_verdict_jgc`: `Major Revision`
- 核心结论：10 个 `app_du` 的 service-level cohort 已进入正文，construct-validity gap 明显缩小；但 service-level policy 结果异质且普遍牺牲 SLA，仍需更严格的控制叙事与 tuning 策略。

## Round 004

- `review_round`: `004`
- `review_date`: `2026-03-11`
- `input_snapshot`:
  - [`main.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.tex)
  - [`abstract.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/abstract.tex)
  - [`introduction.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/introduction.tex)
  - [`method.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/method.tex)
  - [`experiments.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/experiments.tex)
  - [`results.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/results.tex)
  - [`threats.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/threats.tex)
  - [`conclusion.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/conclusion.tex)
  - [`declarations.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/declarations.tex)
  - [`refs.bib`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/refs.bib)
  - [`highlights.md`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/highlights.md)
  - [`cover-letter.md`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/cover-letter.md)
- `overall_verdict_cluster`: `Major Revision`
- `overall_verdict_jgc`: `Major Revision`
- `higher_tier_ceiling`: `Below threshold in current form`

### Review Summary

这轮稿件相比前几轮已经明显更像正式投稿稿，而不是内部 workbench：

1. 已切换到 Springer `sn-jnl` 模板。
2. 已显式加入 `Statements and Declarations`。
3. 摘要被大幅压缩，`Journal of Grid Computing` 的摘要长度门槛已满足，`Cluster Computing` 也只差很小一步。
4. 引言中的过程性口吻显著减少，service-level 容器证据已经被整合进摘要、引言、实验与结果主线。

因此，这一轮最重要的变化是：**过去那些 editor-level 的硬伤有一部分已经被实质修复**。但稿件仍未从 `Major Revision` 升级，原因是剩下的问题更集中在“最终投稿成熟度”和“policy 说服力”：

- affiliation 仍是占位；
- `Cluster Computing` 摘要仍略超上限；
- 结论与个别位置仍保留 `workbench`/路线图口吻；
- service-level 结果虽然 valuable，但目前更像“揭示异质 trade-off”而不是“证明 predictive policy 有稳定优势”；
- `highlights.md` 与 `cover-letter.md` 仍明显落后于当前 broad service-level 版本。

### Official Gate Snapshot

- `Cluster Computing` 当前作者指南：摘要 `100-150` 词，关键词 `4-6` 个，并要求 `Statements and Declarations` 与 `Data Availability Statement`。
- `Journal of Grid Computing` 当前作者指南：摘要 `150-250` 词，关键词 `4-6` 个，并要求同类声明。
- 当前稿件机械检查：
  - 摘要词数：约 `156`
  - 关键词数：`5`
  - 模板：已切换到 `sn-jnl`
  - 声明项：已加入 `Funding`、`Competing interests`、`Data availability`、`Code availability`、`Author contribution`
  - 参考文献总数：`33`
  - 未使用文献：`springerlatex2026`、`bai2018empirical`、`weng2022melaas`
  - 版式：`main.log` 仍有较多 underfull / overfull box warnings

### Scorecard

| Dimension | Score (1-5) | Delta | Reviewer note |
| --- | --- | --- | --- |
| `journal fit` | `4` | `0` | 主题与目标刊持续匹配，service-level 证据使贴合度更自然。 |
| `novelty and contribution` | `3` | `0` | service-level extension 是有效贡献，但 surrogate/最终模型叙事仍不够统一。 |
| `problem formulation` | `3` | `0` | 问题定义清楚，但“improves decision quality”仍需更谨慎表述。 |
| `method soundness` | `2` | `0` | aggregate/service-level formalization 仍不完全一致。 |
| `experimental rigor` | `4` | `0` | aggregate、machine、transfer、service 四层证据已经比较完整。 |
| `reproducibility and transparency` | `4` | `0` | 公共数据与声明项明显改善，但 data/code 仍是 `reasonable request`。 |
| `writing and organization` | `3` | `+1` | 引言明显更像正式论文，但结论和投稿包仍滞后。 |
| `format and submission compliance` | `3` | `+2` | 模板和声明项已就位；当前主要卡点变成摘要略长、affiliation 占位、投稿包未同步。 |

### Prioritized Findings

#### Blocker

1. **投稿包装还未完全过线，尤其是 `Cluster Computing` 版本**
   - 证据位置：
     - [`main.tex:17`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.tex#L17) affiliation 仍写 `Affiliation to be confirmed before submission`。
     - [`abstract.tex:1`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/abstract.tex#L1) 摘要约 `156` 词，略高于 `Cluster Computing` 当前 `100-150` 词要求。
   - 问题原因：对主投刊来说，这已经从“大量硬伤”收敛为“最后一批提交门槛”，但仍然是 editor-first impression 层面的硬问题。
   - 修改要求：
     - 将主投版摘要再压缩约 `6-10` 词；
     - 把 affiliation 补成正式信息；
     - 保留当前摘要作为可转投 `Journal of Grid Computing` 的较长版本基础。

2. **`cover-letter.md` 仍是明显过时的 bootstrap 草稿**
   - 证据位置：
     - [`cover-letter.md:7`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/cover-letter.md#L7) 只概述 public trace + reproducibility，没有反映 machine/transfer/service-level 扩展。
     - [`cover-letter.md:9`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/cover-letter.md#L9) 到 [`cover-letter.md:14`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/cover-letter.md#L14) 仍写着 `bootstrap draft` 和“submission 前再更新”。
   - 问题原因：如果正文已经显著更新，而附信仍停留在旧版本，会让整个投稿包看起来不一致。
   - 修改要求：在决定投稿候选版本后，必须重写 cover letter，直接反映当前 four-layer evidence 和 service-level 贡献。

#### Major

1. **当前最强的新内容是 service-level evidence，但它支持的是“异质性结论”，不是“policy 已被证明更优”**
   - 证据位置：
     - [`results.tex:214`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/results.tex#L214) 到 [`results.tex:246`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/results.tex#L246)
   - 问题原因：service-level 结果表明 `UA-MSTCN-Lite` 在 10-service cohort 上平均 MAE 最优，这是好消息；但 service-level control 上 predictive policy 仍将 SLA 从 `0.010` 拉高到 `0.043`，且只对 `1/10` 个服务改善 SLA。当前最合理的 reviewer 解读是“该框架揭示了 service heterogeneity and policy limits”，而不是“它已经证明 predictive control 在 service level 更好”。
   - 修改要求：摘要、引言和结论都应把 claim 进一步收紧到 heterogeneity-aware evidence，而不要暗示稳定 superiority。

2. **方法 formalization 仍然主要是 aggregate-capacity 版本，落后于现在的 service-level 实验范围**
   - 证据位置：
     - [`method.tex:14`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/method.tex#L14) 到 [`method.tex:34`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/method.tex#L34)
   - 问题原因：现在 results 已经有 service-level policy evidence，但 method 还没有把 service-level capacity proxy、shared global untuned policy、以及 service-level SLA proxy 正式化。
   - 修改要求：补充一小段 service-level formalization，而不是只靠 results 节解释。

3. **结论仍然保留内部路线图口吻**
   - 证据位置：
     - [`conclusion.tex:1`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/conclusion.tex#L1) 到 [`conclusion.tex:3`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/conclusion.tex#L3)
   - 问题原因：现在引言已经明显改善，但 conclusion 仍写成“工作台下一阶段要做什么”，这与正文成熟度不一致。
   - 修改要求：结论改为 standard journal style：重申问题、总结最强证据、界定限制、给出简洁 future work。

4. **`highlights.md` 已经落后于当前 broad service-level 版本**
   - 证据位置：
     - [`highlights.md:3`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/highlights.md#L3) 到 [`highlights.md:7`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/highlights.md#L7)
   - 问题原因：当前 highlights 仍是早期 generic 版本，只讲 public trace / forecasting / uncertainty / low transfer cost，没有提到现在最值钱的 service-level container evidence、10-service cohort、以及 heterogeneity finding。
   - 修改要求：如果 broad32 是候选投稿版本，highlights 必须同步，否则会显得稿件卖点还停留在旧层级。

5. **submission package 与正文的成熟度不一致**
   - 证据位置：
     - [`main.tex:1`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.tex#L1) 到 [`main.tex:47`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.tex#L47)
     - [`highlights.md:1`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/highlights.md#L1) 到 [`highlights.md:7`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/highlights.md#L7)
     - [`cover-letter.md:1`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/cover-letter.md#L1) 到 [`cover-letter.md:18`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/cover-letter.md#L18)
   - 问题原因：正文已经进入“可认真审”的阶段，投稿包却还是 bootstrap 占位稿。外部评审看不到你的开发过程，只会看到 package inconsistency。
   - 修改要求：在 broad32 或任何下一候选版本冻结后，同步更新 submission 材料。

#### Minor

1. **`Data availability` 与 `Code availability` 仍偏保守**
   - 证据位置：
     - [`declarations.tex:13`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/declarations.tex#L13) 到 [`declarations.tex:20`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/declarations.tex#L20)
   - 问题原因：`available on reasonable request` 比直接公开仓库/归档链接的说服力弱。
   - 修改要求：若可能，投稿前改成可公开访问链接或至少给出 planned repository statement。

2. **参考文献清洁度仍未收尾**
   - 证据位置：[`refs.bib`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/refs.bib)
   - 问题原因：仍有未使用条目，且大量 DOI URL 仍是旧式 `http://dx.doi.org`。
   - 修改要求：删除未用条目，统一 DOI 写法为现代格式。

3. **版式 warning 仍然很多**
   - 证据位置：[`main.log`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.log)
   - 问题原因：Springer 模板引入后，underfull/overfull 警告反而更多，说明表格/长句/图注需要重新整理。
   - 修改要求：重点处理 service-level 表格、图注和长句断行。

### Strategic Recommendation

- **对于“是否继续把 `highlights.md` 和 `cover-letter.md` 同步到 broad32 版本”**
  - `如果 broad32 是你准备继续拿去外部评审或投稿包预演的候选版本，推荐同步，而且是必要的。`
  - 原因不是形式主义，而是当前这两个文件已经明显落后于正文：
    - `highlights.md` 没有体现 10-service service-level evidence；
    - `cover-letter.md` 还写着 bootstrap draft。
  - `如果 broad32 还只是内部实验版本，结论和 wording 还会继续变动，则不必立刻同步；等 broad32 作为候选定稿版本冻结后再统一更新最合理。`

- **对 broad32 后续研发本身的建议**
  - 扩 cohort 是正向动作，但要强调 selection rule 和 stability；
  - service-aware tuning 可以做，但更推荐 `regime-aware` 或 `held-out-service validated` tuning，而不是逐服务手工调参；
  - 先把 submission blockers 清掉，再同步 submission package，避免 package 跟不上正文。

### Delta From Previous Round

- `已解决`
  - 已切换 Springer 模板；
  - 已加入声明项；
  - 摘要大幅压缩；
  - 引言过程性口吻明显减少。

- `未解决`
  - 主投摘要仍略长；
  - affiliation 仍占位；
  - service-level policy 仍以 SLA 换其他指标；
  - method 与 service-level evidence 的 formalization 仍不一致。

- `新增`
  - submission package stale 问题现在变得更突出；
  - `highlights.md` / `cover-letter.md` 已不能代表当前 broad service-level 正文。

### Sources Used For This Round

- [Cluster Computing journal page](https://link.springer.com/journal/10586)
- [Cluster Computing submission guidelines](https://www.springer.com/journal/10586/submission-guidelines)
- [Journal of Grid Computing journal page](https://link.springer.com/journal/10723)
- [Journal of Grid Computing submission guidelines](https://www.springer.com/journal/10723/submission-guidelines)
- [Alibaba Cluster Trace Program](https://github.com/alibaba/clusterdata)

## Round 012

- `review_round`: `012`
- `review_date`: `2026-03-12`
- `input_snapshot`:
  - [`main.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.tex)
  - [`main_jgc.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main_jgc.tex)
  - [`abstract.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/abstract.tex)
  - [`abstract_jgc.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/abstract_jgc.tex)
  - [`related_work.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/related_work.tex)
  - [`declarations.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/declarations.tex)
  - [`introduction.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/introduction.tex)
  - [`experiments.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/experiments.tex)
  - [`results.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/results.tex)
  - [`conclusion.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/conclusion.tex)
  - [`cover-letter.md`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/cover-letter.md)
  - [`cover-letter_jgc.md`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/cover-letter_jgc.md)
  - [`refs.bib`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/refs.bib)
- `target_journals`:
  - `Primary`: `Cluster Computing`
  - `Backup`: `Journal of Grid Computing`
- `overall_verdict_cluster`: `Ready to Submit`
- `overall_verdict_jgc`: `Ready to Submit`
- `higher_tier_ceiling`: `Still below threshold because the paper's strongest contribution is a reproducible benchmark and boundary-mapping result rather than a stronger method or positive service-level policy gain`

### Review Summary

这轮修改把上一轮剩余的两个可疑点都基本补齐了，而且补得是对审稿最有价值的部分，而不是纯措辞修饰。

1. [`related_work.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/related_work.tex) 现在已经补入 `2023--2026` 的 service-level / microservice resource-management、cloud evaluation 与最新 predictive-autoscaling 相关工作，references density 已达到当前目标刊常见见刊稿的可接受水平。
2. [`declarations.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/declarations.tex) 已从“reasonable request”推进到“frozen reproducibility package 可供 editor/reviewer 审阅，录用后以 persistent identifier 公开存档”的口径。这与本文“public-trace reproducible benchmark”定位更一致，也明显 stronger。

机械检查结果如下：

- [`abstract.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/abstract.tex) 当前 `147` 词，满足 `Cluster Computing` 当前摘要要求。
- [`abstract_jgc.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/abstract_jgc.tex) 当前 `209` 词，满足 `Journal of Grid Computing` 当前摘要要求。
- [`main.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.tex) 与 [`main_jgc.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main_jgc.tex) 均再次通过 `latexmk -pdf`。
- [`refs.bib`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/refs.bib) 当前包含 `31` 条参考文献，未见 BibTeX `unused entry` 警告；其中已经覆盖 `2023`、`2024`、`2025`、`2026` 文献。

从编辑视角看，当前稿件已经不再缺“投稿包完整性”；从 reviewer 视角看，当前稿件的主要结论、限制、复现承诺和期刊适配性也已经一致。剩余问题只属于可选的 polish，不再构成继续拖延投稿的理由。

### Prioritized Findings

#### Editorial

1. **本轮未发现新的 substantive blocker；稿件已达到可提交状态**
   - 证据位置：
     - [`related_work.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/related_work.tex)
     - [`declarations.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/declarations.tex)
     - [`main.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.tex)
     - [`main_jgc.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main_jgc.tex)
   - 问题原因：上一轮尚可考虑的“近年文献密度”和“availability 公开口径”已经被补到足以过 editor/reviewer 常规检查。
   - 修改要求：无必须继续修改项，可直接按目标刊路线投稿。

#### Minor

1. **如果还想再做最后一轮 polish，最值钱的是把 reproducibility package 进一步具体化**
   - 证据位置：
     - [`declarations.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/declarations.tex#L13)
     - [`declarations.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/declarations.tex#L19)
   - 问题原因：当前声明已经足够投稿，但如果你在投稿时就能提供匿名仓库、private review link 或预留 archive DOI，会进一步降低 reviewer 对“录用后才公开”的顾虑。
   - 修改要求：可选，不是提交前 blocker。

2. **模板级版式 warning 仍存在，但属于 Springer 双栏常见噪音**
   - 证据位置：
     - [`main.log`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.log)
     - [`main_jgc.log`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main_jgc.log)
   - 问题原因：当前日志仍有较多 `Underfull \hbox`，但未见 undefined reference/citation，也未发现新的可见版式损坏。
   - 修改要求：可在提交前顺手清理，但没有必要为此推迟投稿。

### Required Actions Before Submission

1. 无必须新增的正文或投稿包修改项。
2. 若你手上已经有匿名仓库或待发布归档地址，可把 availability 再从“可提供”推进到“submission-time access available”；否则当前版本已足够。
3. 其余工作若继续进行，应视为投稿后的下一阶段研究，而不是本轮投稿前提。

### Delta From Previous Round

- `已解决`
  - `2023--2026` 近年相关工作已补入并进入正文论述；
  - data/code availability 已升级到 frozen reproducibility package + persistent identifier 公开存档口径；
  - 双期刊 cover letter 与双主文件现在都和正文主结论一致。

- `仍保留`
  - 稿件的最高价值仍是 reproducible benchmark + boundary mapping，而不是更高层级期刊偏好的方法突破；
  - 模板级断行 warning 仍在，但不形成投稿阻塞。

- `新增`
  - 无新的高优先级问题。

### Sources Used For This Round

- [Cluster Computing journal page](https://link.springer.com/journal/10586)
- [Cluster Computing submission guidelines](https://www.springer.com/journal/10586/submission-guidelines)
- [Journal of Grid Computing journal page](https://link.springer.com/journal/10723)
- [Journal of Grid Computing submission guidelines](https://www.springer.com/journal/10723/submission-guidelines)
- [Springer Nature data availability statements guidance](https://www.springernature.com/gp/authors/research-data-policy/data-availability-statements)
- [Springer Nature software and code sharing policy](https://support.springernature.com/en/support/solutions/articles/6000237619-software-and-code-sharing)
- [Alibaba Cluster Trace Program](https://github.com/alibaba/clusterdata)

## Round 013

### Overall Assessment

这轮 reviewer 建议的优先级判断基本合理，而且已经按更值钱的方向处理：先加强 `data/code availability`，再少量补强近年相关工作，而不是继续堆 references 数量。当前稿件在“可复现 benchmark”这条主卖点上的说服力，比上一轮更接近期刊审稿人会期待的口径。

### What Was Changed

1. **Availability statement 已从 `reasonable request` 推进到 frozen-package during review / public release upon acceptance**
   - 已修改：
     - [`declarations.tex:13`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/declarations.tex#L13) 到 [`declarations.tex:20`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/declarations.tex#L20)
     - [`cover-letter.md`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/cover-letter.md)
     - [`cover-letter_jgc.md`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/cover-letter_jgc.md)
     - [`reproducibility-package.md`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/reproducibility-package.md)
   - 当前口径：
     - 原始 Alibaba trace 仍指向公开来源；
     - 本稿对应的 frozen reproducibility package 可在 peer review 期间提供给 editor / reviewers；
     - 录用后将连同代码与处理后工件一起存入带 persistent identifier 的公开仓库。
   - 评价：
     - 这比“upon reasonable request”明显更强，也更符合当前稿件的 reproducibility positioning。

2. **近年 related work 已做有限但有效的 densification**
   - 已修改：
     - [`related_work.tex:3`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/related_work.tex#L3)
     - [`related_work.tex:24`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/related_work.tex#L24)
     - [`related_work.tex:32`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/related_work.tex#L32)
     - [`refs.bib`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/refs.bib)
   - 新补条目覆盖了三类里最需要的空档：
     - service-level / microservice resource management
     - recent microservice autoscaling
     - reproducible cloud workload evaluation / simulation
   - 评价：
     - 这轮没有为了“看起来厚”而硬堆大串文献，方向是对的；当前 related work 的近年覆盖已比上一轮自然得多。

### Verification

- [`main.pdf`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.pdf) 与 [`main_jgc.pdf`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main_jgc.pdf) 已重新编译通过。
- 新增近年文献未再触发 undefined citation。
- 已对受影响页面做渲染级视觉检查：
  - 主稿第 `3/18/19` 页
  - JGC 版第 `3/16/17/18` 页
- 当前未见由新 availability 段或 related-work 增补导致的重叠、越界或截断。

### Residual Risks

1. **Availability 仍不是最强版本**
   - 现在已经达到“review access + upon-acceptance release”的可接受水平，但仍未给出实际 public repository / DOI。
   - 如果后续能在投稿前准备好稳定仓库或 archive identifier，这一项还可以再升一级。

2. **References 清洁度仍可继续做一次 submission cleanup**
   - 这轮重点是加分项而不是 bib hygiene，因此未系统清理未用条目与 DOI / URL 样式噪音。

### Verdict For This Round

这一轮不需要再改主结果或主叙事。按 reviewer 的最新建议看，最值得做的收尾项已经落地，而且价值排序是正确的：availability strengthening 的收益高于继续机械堆文献。若还继续动稿，优先级应是“准备真实 public archive / DOI”，而不是再扩 related-work 篇幅。

## Round 014

### Overall Assessment

这轮没有再改论文主结论，而是把上一轮提到的“availability 还可以再向前推进一步”真正落成了可执行工件。和只在声明里写 future plan 相比，当前状态已经更接近一个可以交给 editor / reviewer 审计的 frozen review package。

### What Was Changed

1. **新增 archive-ready 元数据与 package-staging 路线**
   - 已新增：
     - [`README.md`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/README.md)
     - [`CITATION.cff`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/CITATION.cff)
     - [`reproducibility-package-manifest.yaml`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/reproducibility-package-manifest.yaml)
     - [`build_repro_package.py`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/scripts/build_repro_package.py)
   - 评价：
     - 这一步把“将来会公开发布”的抽象承诺推进成了一个可重复执行的 staging route，明显提高了 availability 表述的可信度。

2. **已实际 stage 当前 review freeze**
   - 已生成：
     - [`review-freeze-2026-03-12`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/frozen-package/review-freeze-2026-03-12)
     - [`review-freeze-2026-03-12.tar.gz`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/frozen-package/review-freeze-2026-03-12.tar.gz)
     - [`BUILD-METADATA.json`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/frozen-package/review-freeze-2026-03-12/BUILD-METADATA.json)
     - [`SHA256SUMS`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/frozen-package/review-freeze-2026-03-12/SHA256SUMS)
   - 当前冻结快照摘要：
     - `185` 个文件
     - `834,376,871` bytes 未压缩内容
     - 排除了原始 Alibaba 第三方归档和 transient LaTeX build 噪音

3. **submission/status 文档已同步**
   - 已修改：
     - [`checklist.md`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/checklist.md)
     - [`00-status.md`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/00-status.md)
     - [`reproducibility-package.md`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/reproducibility-package.md)

### Verification

- package-staging 脚本已实际跑通，没有停留在“未执行模板”状态。
- staged snapshot 内已包含 manuscript sources、compiled PDFs、processed datasets、experiment scripts、results、evidence ledger、review log、submission materials。
- checksum manifest 与 build metadata 已写出，可直接用于 review-time audit。

### Residual Risks

1. **仍未形成真实 public DOI**
   - 当前已经具备 frozen-package 和 archive-ready metadata，但还没有上传到 Zenodo、Figshare 或 institution repository，因此 persistent identifier 仍是下一步任务。

2. **package 仍偏 workbench-style**
   - 冻结包已经足够做审计，但若面向最终公开发布，还可以继续收紧内容边界，例如进一步区分 manuscript-facing artifacts 与 exploratory legacy artifacts。

### Verdict For This Round

availability 这一项现在已经从“较保守的声明文字”推进到“可实际交付的 review freeze”。如果还要继续提高 reviewer 信任，下一步不该再停留在本地整理，而应直接完成稳定公开仓库或 archive DOI 的落地。

## Round 012

- `review_round`: `012`
- `review_date`: `2026-03-12`
- `input_snapshot`:
  - [`abstract.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/abstract.tex)
  - [`abstract_jgc.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/abstract_jgc.tex)
  - [`introduction.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/introduction.tex)
  - [`related_work.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/related_work.tex)
  - [`experiments.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/experiments.tex)
  - [`results.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/results.tex)
  - [`conclusion.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/conclusion.tex)
  - [`main.pdf`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.pdf)
  - [`main_jgc.pdf`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main_jgc.pdf)
- `overall_verdict_cluster`: `Minor Revision (text package aligned)`
- `overall_verdict_jgc`: `Minor Revision`

### Review Summary

最新一轮 published-paper benchmarking 提出的核心问题已经基本处理完了。正文里原本残留的写稿过程语言，例如 `promoted broad cohort`、`revised manuscript`、`earlier version of the study`、`must be promoted from a robustness check to the main result`，都已经从主文叙述中移除或改写为标准 scholarly prose。贡献段也已更明确地按 `benchmark / evaluation / evidence contribution` 重写，而不是继续保留 algorithm-first 的口吻。

本轮完成后的主要变化如下：

1. [`introduction.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/introduction.tex) 现在明确把论文定位为 `public-trace benchmark and boundary-mapping study`，并将 contributions 改成 evaluation-oriented wording。
2. [`related_work.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/related_work.tex) 的 framing 更接近正式文献比较，不再使用带有投稿过程色彩的表述。
3. [`results.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/results.tex) 已把 broad service cohort 段落和表图 caption 改成标准结果叙述，保留 `top-10` 对照的实质信息，但去掉 `promotion`/`main result` 这类过程性措辞。
4. [`conclusion.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/conclusion.tex) 现在更直接地把论文收束为 `benchmark and boundary-mapping result`。
5. [`abstract.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/abstract.tex) 和 [`abstract_jgc.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/abstract_jgc.tex) 也同步去掉了 `promoted broad` 这类内部过程语言。

### Validation

- [`main.pdf`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.pdf) 与 [`main_jgc.pdf`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main_jgc.pdf) 已重新编译通过，当前页数均为 `19`。
- 视觉检查已覆盖主稿第 `1/2/3/13/14/15` 页和 JGC 版第 `1/13/14` 页，未见新的重叠、超栏、截断或 service-level 表图回流问题。
- 剩余 warning 仍以 underfull box 为主，并保留既有的 `2.3pt` related-work 表头 overfull、`0.6pt` 轻微 overfull，以及 service workload figure 的 `Float too large` 提示；这些在当前 PDF 中未形成可见排版错误。

### Delta From Previous Round

- `已解决`
  - 正文中的 meta-narrative 已进一步清理；
  - contributions 已更明确地转为 evaluation / benchmark / evidence wording；
  - broad 主结果相关 caption 和段落已改成更像正式见刊稿的写法；
  - 双版本 PDF 已重新验证。

- `仍保留`
  - 论文的 strongest claim 仍是 reproducible benchmark and boundary finding，而不是强性能突破；
  - references density 可以在未来继续增厚，但当前不再是必须改动项；
  - code/data openness 仍偏保守。

### Sources Used For This Round

- [Cluster Computing journal page](https://link.springer.com/journal/10586)
- [Cluster Computing submission guidelines](https://www.springer.com/journal/10586/submission-guidelines)
- [Journal of Grid Computing journal page](https://link.springer.com/journal/10723)
- [Journal of Grid Computing submission guidelines](https://www.springer.com/journal/10723/submission-guidelines)
- [Rossi et al., Cluster Computing (2025)](https://link.springer.com/article/10.1007/s10586-024-04933-2)
- [Casalicchio et al., Cluster Computing (2019)](https://link.springer.com/article/10.1007/s10586-017-1610-y)
- [OnlineElastMan, Cluster Computing (2017)](https://link.springer.com/article/10.1007/s10586-017-1170-1)
- [Kovács, Journal of Grid Computing (2019)](https://link.springer.com/article/10.1007/s10723-019-09497-0)
- [Zanussi et al., Cluster Computing (2026)](https://link.springer.com/article/10.1007/s10586-026-04761-w)

## Round 011

- `review_round`: `011`
- `review_date`: `2026-03-12`
- `input_snapshot`:
  - [`main.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.tex)
  - [`main_jgc.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main_jgc.tex)
  - [`abstract.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/abstract.tex)
  - [`abstract_jgc.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/abstract_jgc.tex)
  - [`introduction.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/introduction.tex)
  - [`experiments.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/experiments.tex)
  - [`results.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/results.tex)
  - [`threats.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/threats.tex)
  - [`conclusion.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/conclusion.tex)
  - [`declarations.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/declarations.tex)
  - [`00-status.md`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/00-status.md)
  - [`dataset_manifest.yaml`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/experiments/dataset_manifest.yaml)
  - [`highlights.md`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/highlights.md)
  - [`cover-letter.md`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/cover-letter.md)
  - broad artifacts in [`service_cohort_broad/`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/experiments/results/service_cohort_broad)
- `target_journals`:
  - `Primary`: `Cluster Computing`
  - `Backup`: `Journal of Grid Computing`
- `overall_verdict_cluster`: `Minor Revision (submission-ready after one final consistency pass)`
- `overall_verdict_jgc`: `Minor Revision`
- `higher_tier_ceiling`: `Still below stronger-venue threshold because the broad cohort is stronger but the temporal backbone remains lightweight and the broad service-level policy result is negative`

### Review Summary

这轮稿件已经进入“最后一轮 reviewer-proofing”阶段。最关键的正面变化不是新增了某个局部实验，而是 broad promotion 已经真正贯穿全稿：

1. [`main.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.tex) 与 [`main_jgc.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main_jgc.tex) 双版本入口都已建立并可编译。
2. [`abstract.tex:1`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/abstract.tex#L1)、[`abstract_jgc.tex:1`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/abstract_jgc.tex#L1)、[`conclusion.tex:1`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/conclusion.tex#L1) 到 [`conclusion.tex:5`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/conclusion.tex#L5)、[`highlights.md:3`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/highlights.md#L3) 到 [`highlights.md:8`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/highlights.md#L8)、[`cover-letter.md:7`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/cover-letter.md#L7) 到 [`cover-letter.md:11`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/cover-letter.md#L11) 都已同步 broad 主结果。
3. [`00-status.md:3`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/00-status.md#L3) 到 [`00-status.md:11`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/00-status.md#L11) 与 [`dataset_manifest.yaml:37`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/experiments/dataset_manifest.yaml#L37) 到 [`dataset_manifest.yaml:45`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/experiments/dataset_manifest.yaml#L45) 已把 broad promotion、full mirror 和 stability analysis 记录为项目当前状态，而不再停留在 earlier top-10 阶段。
4. broad 工件本身是闭环的：[`service_cohort_promotion_decision.csv`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/experiments/results/service_cohort_broad/tables/service_cohort_promotion_decision.csv) 与 [`service_cohort_stability_summary.csv`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/experiments/results/service_cohort_broad/tables/service_cohort_stability_summary.csv) 的结论和正文一致。

当前机械检查：

- `Cluster Computing` 摘要约 `147` 词，满足 `100-150` 词要求。
- `Journal of Grid Computing` 摘要约 `209` 词，满足 `150-250` 词要求。
- 关键词数：`5`
- `main.pdf` / `main_jgc.pdf` 均为 `18` 页。
- 两个主文件均可通过 `latexmk -pdf` 编译。
- 未发现未定义引用错误。

### Scorecard

| Dimension | Score (1-5) | Delta | Reviewer note |
| --- | --- | --- | --- |
| `journal fit` | `4` | `0` | 主题与两本目标刊持续匹配。 |
| `novelty and contribution` | `4` | `0` | broad 主结果使 evaluation/evidence contribution 更可信。 |
| `problem formulation` | `4` | `0` | 问题、结果与结论已基本闭环。 |
| `method soundness` | `4` | `0` | broad 构建规则与 overlap/promotion 审计合理。 |
| `experimental rigor` | `4` | `0` | 四层证据面完整，broad artifacts 可追溯。 |
| `reproducibility and transparency` | `5` | `0` | 双 build、status/manifest 同步、artifact-driven decisions 都加分。 |
| `writing and organization` | `4` | `0` | 全稿已经统一，但仍有一处 contribution wording 偏软。 |
| `format and submission compliance` | `4` | `0` | 双期刊版本都已接近合规，剩余主要是 package 收尾。 |

### Prioritized Findings

#### Major

1. **broad promotion 的主判据仍应前移到 Experimental Setup，而不是主要留在 Results 里解释**
   - 证据位置：
     - [`experiments.tex:101`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/experiments.tex#L101) 到 [`experiments.tex:109`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/experiments.tex#L109)
     - [`results.tex:230`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/results.tex#L230) 到 [`results.tex:245`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/results.tex#L245)
     - [`results.tex:282`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/results.tex#L282)
   - 问题原因：现在 broad 升格依据已经是全稿核心逻辑，但 `equal-weighted mean delta`、`paired service bootstrap`、`load-weighted auxiliary check` 和 promotion rule 还主要靠 Results 段落来补解释。审稿人可能会问，这些判据是不是在看到结果后才被强调。
   - 修改要求：在 Experimental Setup 补一个很短的 protocol paragraph，明确：
     - 重采样单位为 `service`
     - 主统计量为 `equal-weighted predictive-minus-reactive mean delta`
     - `load-weighted mean delta` 仅为辅助解释
     - broad promotion 依据预先固定的 headline/stability rule

2. **引言 contribution 第 4 条仍弱于当前 broad 主结果**
   - 证据位置：
     - [`introduction.tex:19`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/introduction.tex#L19) 到 [`introduction.tex:20`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/introduction.tex#L20)
   - 问题原因：现在引言仍写“service-level policy gains do not transfer uniformly across heterogeneous services”。这更像 top-10 阶段的 softer conclusion。当前 broad 结果更强：forecast winner flip、stable SLA degradation、stable actions degradation、over-provisioning gain not stable。
   - 修改要求：把 contribution wording 收紧到当前 broad 结果层级，例如明确 earlier targeted service headline is not robust under broader audited service coverage。

#### Minor

1. **`Journal of Grid Computing` 的 article build 已经准备好，但 fallback 投稿包仍缺定向 cover letter**
   - 证据位置：
     - [`main_jgc.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main_jgc.tex)
     - [`cover-letter.md`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/cover-letter.md)
   - 问题原因：当前 `cover-letter.md` 仍然明确投向 `Cluster Computing`。如果真切到后备刊，论文本体已接近 ready，但投稿包还差一份匹配版本。
   - 修改要求：不一定现在立刻写，但在“最终可投”定义里应把 `cover-letter_jgc.md` 算进去。

2. **仍有 `3` 个未使用参考文献**
   - 证据位置：
     - [`refs.bib`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/refs.bib)
   - 问题原因：`springerlatex2026`、`bai2018empirical`、`weng2022melaas` 仍未使用。
   - 修改要求：提交前删除未用条目并统一条目样式。

3. **双栏版式 warning 仍然较多，但已不再构成结构性阻塞**
   - 证据位置：
     - [`main.log`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.log)
     - [`main_jgc.log`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main_jgc.log)
   - 问题原因：当前主要是 underfull box 与极轻微 overfull box，说明 broad promotion 引入的表格/长段落在版面上还有压缩空间。
   - 修改要求：最后一轮优先清理 promotion audit table、broad service tables 和长 caption。

### Required Actions Before Submission

1. 在 Experimental Setup 中前置 broad promotion 的统计判据与 stability protocol。
2. 收紧引言 contribution 第 4 条，使其与 broad 主结果同级。
3. 删除 `3` 个未使用参考文献。
4. 若保留 `JGC` 后备路线，补一份定向 cover letter。
5. 做最后一轮 broad-related 表格与段落的版式清洁。

### Delta From Previous Round

- `已解决`
  - broad 结果已贯穿摘要、正文、结论、status、manifest 与 submission package；
  - `main_jgc.tex` 已建立并成功编译；
  - 双版本摘要、MSC 与声明顺序分叉已实际落地；
  - broad 工件与正文 headline 目前一致。

- `未解决`
  - broad promotion 判据尚未足够 protocolized；
  - `UA-MSTCN-Lite` 仍是 surrogate instantiation；
  - broad cohort 仍非 full service census；
  - bib 清洁度与版式 warning 仍需收尾。

- `新增`
  - 当前稿件已从“可认真审”进入“接近提交，只差 final consistency pass”阶段。

### Sources Used For This Round

- [Cluster Computing journal page](https://link.springer.com/journal/10586)
- [Cluster Computing submission guidelines](https://www.springer.com/journal/10586/submission-guidelines)
- [Journal of Grid Computing journal page](https://link.springer.com/journal/10723)
- [Journal of Grid Computing submission guidelines](https://www.springer.com/journal/10723/submission-guidelines)
- [Alibaba Cluster Trace Program](https://github.com/alibaba/clusterdata)

## Round 011

- `review_round`: `011`
- `review_date`: `2026-03-12`
- `input_snapshot`:
  - [`main.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.tex)
  - [`main_jgc.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main_jgc.tex)
  - [`abstract.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/abstract.tex)
  - [`abstract_jgc.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/abstract_jgc.tex)
  - [`introduction.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/introduction.tex)
  - [`experiments.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/experiments.tex)
  - [`results.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/results.tex)
  - [`cover-letter.md`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/cover-letter.md)
  - [`cover-letter_jgc.md`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/cover-letter_jgc.md)
  - [`refs.bib`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/refs.bib)
- `target_journals`:
  - `Primary`: `Cluster Computing`
  - `Backup`: `Journal of Grid Computing`
- `overall_verdict_cluster`: `Minor Revision (submission-ready package)`
- `overall_verdict_jgc`: `Minor Revision (backup package ready)`
- `higher_tier_ceiling`: `Still below threshold because the implemented backbone remains lightweight and the promoted broad service-level policy result is negative`

### Review Summary

Round 010 提出的几项具体收尾建议已经基本完成，而且这次不是只改文字没有验收。Experimental Setup 现在已经把 broad promotion 所依赖的统计量、重采样单位、稳定性解释规则和 promotion rule 前置写死；引言 contribution 也已改成与 broad 主结果一致的 stronger wording；`Journal of Grid Computing` 的定向 cover letter 已补齐；主稿和 JGC 备份稿都重新编译并做了 broad-related 页面视觉检查。

同时，上一轮关于“仍有 3 个未使用参考文献”的判断在当前构建状态下不再成立。基于 `main.aux` 和 `main_jgc.aux` 的再次核对，当前 [`refs.bib`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/refs.bib) 为 `31` 条、`31` 条均被引用，未发现未使用条目。因此这项不需要再做删除动作。

机械检查结果如下：

- [`abstract.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/abstract.tex) 约 `147` 词，满足 `Cluster Computing` 当前摘要长度要求。
- [`abstract_jgc.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/abstract_jgc.tex) 约 `209` 词，满足 `Journal of Grid Computing` 当前摘要长度要求。
- [`main.pdf`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.pdf) 与 [`main_jgc.pdf`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main_jgc.pdf) 均重新编译通过，当前页数均为 `19`。
- 视觉检查覆盖主稿第 `7/13/14/15` 页与 JGC 版第 `8/13/14/15` 页，未见新的重叠、超栏、页底截断或 broad 主结果表图堆叠问题。

### Prioritized Findings

#### Editorial

1. **Round 010 的核心收尾项已完成，当前剩余的主要是模板噪音而非真实阻塞**
   - 已解决项：
     - [`experiments.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/experiments.tex) 已前置定义 `service` bootstrap、`equal-weighted mean delta` 主统计量、`load-weighted mean delta` 辅助统计量和 promotion rule。
     - [`introduction.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/introduction.tex) 的 contribution 第 4 条已改成 broad 主结果口径。
     - [`cover-letter_jgc.md`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/cover-letter_jgc.md) 已补齐。
     - [`refs.bib`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/refs.bib) 当前未见 unused entries。
   - 剩余情况：
     - [`main.log`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.log) 和 [`main_jgc.log`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main_jgc.log) 仍有 underfull box，以及少量既有浮动/断行 warning。
   - 结论：这些更接近 Springer 双栏模板的常见清洁度问题，不再构成“根据最新审稿建议必须继续改正文”的 blocker。

#### Minor

1. **当前 broad service workload 图仍触发模板级 float/wrapping warning，但实页已可接受**
   - 证据位置：
     - [`experiments.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/experiments.tex#L57)
     - [`main.pdf`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.pdf)
   - 问题原因：这类 warning 主要来自双栏下较高的 figure 和密集图注，不代表实际 PDF 已坏。
   - 修改要求：若投稿前还要再做一轮纯版式优化，可优先从 broad workload overview 图和若干长段落断行入手；否则可保持当前版本。

### Required Actions Before Submission

1. 当前已无必须因 Round 010 新建议而继续修改的正文 blocker。
2. 若还做最终 polish，只需要把它当成 `layout/noise cleanup`，而不是再改 broad 结论口径。

### Delta From Previous Round

- `已解决`
  - broad promotion 判据已前置到 protocol；
  - 引言已切到更贴近 broad 主结果的 stronger wording；
  - JGC 定向 cover letter 已补；
  - “3 个未使用参考文献”在当前构建下被复核为旧结论，不再成立；
  - 主稿与 JGC 备份稿均已重新编译并通过 broad-related 视觉检查。

- `仍保留`
  - broad service-level 主结果仍然是否定性 boundary result，而非 superiority claim；
  - `UA-MSTCN-Lite` 仍是 lightweight surrogate，而非更强时序骨干的最终实现；
  - 模板级 underfull/overfull 噪音仍存在，但未形成可见版式错误。

### Sources Used For This Round

- [Cluster Computing journal page](https://link.springer.com/journal/10586)
- [Cluster Computing submission guidelines](https://www.springer.com/journal/10586/submission-guidelines)
- [Journal of Grid Computing journal page](https://link.springer.com/journal/10723)
- [Journal of Grid Computing submission guidelines](https://www.springer.com/journal/10723/submission-guidelines)
- [Alibaba Cluster Trace Program](https://github.com/alibaba/clusterdata)

## Round 010

- `review_round`: `010`
- `review_date`: `2026-03-12`
- `input_snapshot`:
  - [`main.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.tex)
  - [`main_jgc.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main_jgc.tex)
  - [`abstract.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/abstract.tex)
  - [`abstract_jgc.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/abstract_jgc.tex)
  - [`introduction.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/introduction.tex)
  - [`experiments.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/experiments.tex)
  - [`results.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/results.tex)
  - [`threats.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/threats.tex)
  - [`conclusion.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/conclusion.tex)
  - [`declarations.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/declarations.tex)
  - [`00-status.md`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/00-status.md)
  - [`dataset_manifest.yaml`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/experiments/dataset_manifest.yaml)
  - [`highlights.md`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/highlights.md)
  - [`cover-letter.md`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/cover-letter.md)
  - broad service artifacts under [`service_cohort_broad/`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/experiments/results/service_cohort_broad)
- `target_journals`:
  - `Primary`: `Cluster Computing`
  - `Backup`: `Journal of Grid Computing`
- `overall_verdict_cluster`: `Minor Revision (close to submit)`
- `overall_verdict_jgc`: `Minor Revision`
- `higher_tier_ceiling`: `Still below threshold because broad cohort is strong but the implemented temporal backbone remains lightweight and service-level policy remains negative under broad coverage`

### Review Summary

这轮更新是一次实质性的主线升级，而不是普通修稿。broad service cohort 已经真正取代 earlier top-10，且这种 promotion 已被摘要、正文、结论、状态文件、manifest、highlights、cover letter 和双 LaTeX 入口同步吸收。最重要的是：你没有试图回避 broad 带来的不利结论，而是把它完整提升为主结果。这一点从 reviewer 视角是加分的。

本轮机械检查结果：

- [`abstract.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/abstract.tex) 约 `147` 词，满足 `Cluster Computing` 当前 `100-150` 词要求。
- [`abstract_jgc.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/abstract_jgc.tex) 约 `209` 词，满足 `Journal of Grid Computing` 当前 `150-250` 词要求。
- 关键词数：`5`
- [`main.pdf`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.pdf) / [`main_jgc.pdf`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main_jgc.pdf) 均为 `18` 页。
- `latexmk -pdf main.tex` 与 `latexmk -pdf main_jgc.tex` 均通过。
- 未见未定义引用错误；参考文献仍有 `3` 个未用条目。

因此，当前稿件已经不再主要卡在“有没有正式稿形态”，而是卡在最后几处方法口径和提交清洁度问题。

### Scorecard

| Dimension | Score (1-5) | Delta | Reviewer note |
| --- | --- | --- | --- |
| `journal fit` | `4` | `0` | 主题与两个目标刊持续匹配。 |
| `novelty and contribution` | `4` | `+1` | broad promotion 让 evaluation/evidence contribution 更有分量。 |
| `problem formulation` | `4` | `0` | broad negative result 已进入问题-结论闭环。 |
| `method soundness` | `4` | `0` | broad 规则筛选、overlap audit 和 dual-build 设计都合理。 |
| `experimental rigor` | `4` | `0` | aggregate、machine、transfer、broad service 四层证据完整。 |
| `reproducibility and transparency` | `5` | `+1` | 本地完整镜像、manifest/status 同步、artifact-based promotion 决策都明显加分。 |
| `writing and organization` | `4` | `0` | broad promotion 后的叙事大体一致。 |
| `format and submission compliance` | `4` | `0` | 双版本主文件已建立，剩余问题主要是清洁度与 package 细节。 |

### Prioritized Findings

#### Major

1. **broad promotion 依赖的主统计量与稳定性判据还没有被足够前置到 protocol 层**
   - 证据位置：
     - [`experiments.tex:101`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/experiments.tex#L101) 到 [`experiments.tex:109`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/experiments.tex#L109)
     - [`results.tex:230`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/results.tex#L230) 到 [`results.tex:245`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/results.tex#L245)
     - [`results.tex:282`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/results.tex#L282)
   - 问题原因：现在 broad promotion 的结论是建立在 `equal-weighted predictive-minus-reactive mean deltas + paired service bootstrap` 上的，这完全合理；但这套主判据目前主要是在 Results 节被解释，而不是在 Experimental Setup 中预先定义。由于它已经直接决定了“broad 是否升格为主结果”，reviewer 可能会质疑这是结果出来后才强化的判据。
   - 修改要求：在 [`experiments.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/experiments.tex) 增加 3-5 句 protocol-level 说明，明确：
     - 重采样单位是 `service`
     - 主统计量是 `equal-weighted mean delta`
     - `load-weighted mean delta` 只是辅助检查
     - promotion/stability 的解释规则在实验设计中预先固定

2. **引言对 broad 结果的口径仍略偏保守，弱于当前最强证据**
   - 证据位置：
     - [`introduction.tex:19`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/introduction.tex#L19) 到 [`introduction.tex:20`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/introduction.tex#L20)
   - 问题原因：当前 contribution 仍写成“service-level policy gains do not transfer uniformly across heterogeneous services”。这在 earlier top-10 阶段是合适的，但 broad 主结果现在更强：对 reactive baseline，SLA 与 actions 都是稳定退化，over-provisioning gain 也不稳定。继续只写“do not transfer uniformly”会让引言的 claim 明显弱于结果和结论。
   - 修改要求：把这句改得更贴近当前 broad 主结果，例如强调“the earlier top-10 service headline does not survive broader audited service coverage”或“the current shared global predictive policy is not validated as a broad service-level improvement route”。

#### Minor

1. **`Journal of Grid Computing` 主文件已经建立，但 fallback package 仍缺期刊定向的 cover letter**
   - 证据位置：
     - [`main_jgc.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main_jgc.tex)
     - [`cover-letter.md`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/cover-letter.md)
   - 问题原因：`main_jgc.tex`、MSC 和摘要长度都已就位，这很好；但当前 cover letter 仍是 `Cluster Computing` 导向。对主投无碍，但若真切换后备刊，package 还需要一份对应版本。
   - 修改要求：不必现在就写，但在“可提交”定义里应包含 `cover-letter_jgc.md` 或同等替代。

2. **参考文献清洁度仍未收尾**
   - 证据位置：
     - [`refs.bib`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/refs.bib)
   - 问题原因：仍有 `3` 个未使用条目：`springerlatex2026`、`bai2018empirical`、`weng2022melaas`。
   - 修改要求：投稿前删除未用条目并统一条目格式。

3. **双栏版式 warning 仍多，但现在已降级为清洁度问题**
   - 证据位置：
     - [`main.log`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.log)
     - [`main_jgc.log`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main_jgc.log)
   - 问题原因：当前无未定义引用，只有大量 underfull box 和极少数轻微 overfull box。它们不会阻止投稿，但会影响最后的版面精致度。
   - 修改要求：最后一轮只需要集中处理 broad service promotion 相关的新表格和长段落。

### Required Actions Before Submission

1. 把 `equal-weighted / load-weighted / paired service bootstrap / promotion rule` 的 protocol 说明前移到 Experimental Setup。
2. 将引言 contribution 第 4 条收紧到当前 broad 主结果，而不是保留 earlier top-10 阶段的 softer wording。
3. 删除 `3` 个未使用参考文献。
4. 如准备真正保留 `JGC` 后备路线，再补一份期刊定向的 cover letter。
5. 做最后一轮 broad-related 表格和段落的版式清洁。

### Delta From Previous Round

- `已解决`
  - broad service cohort 已被正式提升为主结果；
  - `main_jgc.tex` 已建立并可编译；
  - `main.tex` / `main_jgc.tex` 双摘要、声明顺序和 MSC 分叉已落地；
  - status、manifest、highlights、cover letter 已与 broad 结论同步；
  - 当前两份 PDF 均可成功构建。

- `未解决`
  - broad promotion 所依赖的主统计量与稳定性判据还未足够前置；
  - `UA-MSTCN-Lite` 仍然是 surrogate instantiation 而非真正 deep backbone；
  - broad cohort 仍不是 full population census；
  - bib 清洁度与版式 warning 仍需收尾。

- `新增`
  - broad 结果已经实质改写了 service-level 结论：forecasting winner flip、scaling-actions sign flip、over-provisioning gain not stable；
  - 当前稿件已从“service-level mixed supplement”升级为“broad negative boundary result”版本。

### Sources Used For This Round

- [Cluster Computing journal page](https://link.springer.com/journal/10586)
- [Cluster Computing submission guidelines](https://www.springer.com/journal/10586/submission-guidelines)
- [Journal of Grid Computing journal page](https://link.springer.com/journal/10723)
- [Journal of Grid Computing submission guidelines](https://www.springer.com/journal/10723/submission-guidelines)
- [Alibaba Cluster Trace Program](https://github.com/alibaba/clusterdata)

## Round 009

- `review_round`: `009`
- `review_date`: `2026-03-11`
- `input_snapshot`:
  - broad service cohort robustness plan (user-provided)
  - [`00-status.md`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/00-status.md)
  - [`dataset_manifest.yaml`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/experiments/dataset_manifest.yaml)
  - [`profile_v2018_container_usage_prefix.py`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/experiments/preprocessing/profile_v2018_container_usage_prefix.py)
  - [`abstract_jgc.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/abstract_jgc.tex)
  - [`main.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.tex)
- `target_journals`:
  - `Primary`: `Cluster Computing`
  - `Backup`: `Journal of Grid Computing`
- `overall_verdict_cluster`: `Plan is sound with two rule refinements`
- `overall_verdict_jgc`: `Plan is sound but backup packaging still needs a real entrypoint`
- `higher_tier_ceiling`: `Plan improves robustness substantially, but does not by itself remove service-level breadth limits`

### Review Summary

这份 broad robustness 计划总体方向是对的，而且比前一版更像一个可以被审稿人接受的证据计划：

1. 明确从 streamed prefix 切到本地完整镜像；
2. 用 `规则筛后全纳` 代替固定 `top20/top32`；
3. 用 `top10 overlap audit` 代替“必须保留 top10”；
4. 明确 broad 的角色是 `robustness section` 或 `promotion to main result` 二选一；
5. 为 `Journal of Grid Computing` 增加独立 `main_jgc.tex` 入口，而不是在 `main.tex` 里塞条件分支。

这几条都符合当前稿件最需要修复的 reviewer 风险：selection bias、fallback 包装不成体系、以及 broad 结果出现后没有预先写死升级规则。

### Prioritized Findings

#### Major

1. **promotion rule 还应覆盖“headline claim 的稳定性失效”，不能只看 mean sign flip**
   - 证据位置：user-provided broad plan
   - 问题原因：当前计划把 policy headline 定义为 `predictive - reactive` 在三项主指标上的 mean sign pattern 是否保持不变。这比之前已经好很多，但仍然不够严。因为如果 broad 上均值符号没翻，但 bootstrap 95% CI 跨过 `0`，那摘要和结论里用 “reduces ...” 这种陈述句就已经不再稳妥。
   - 修改要求：把 promotion condition 收紧为：
     - `headline flip`，或
     - `headline no longer supportable as a declarative claim because stability label degrades to not stable`
     至少对 `over_provisioning` 和 `scaling_actions` 这两个当前摘要里已用陈述句写出的 service-level gain 做此检查。

2. **`Journal of Grid Computing` 变体方案方向正确，但需要承认它与主投版存在真实的 front-matter 分叉**
   - 证据位置：
     - [`main.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.tex)
     - [`abstract_jgc.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/abstract_jgc.tex)
   - 问题原因：当前计划已加入 `main_jgc.tex`、`MSC` 和 `Declarations before References`，这是正确方向。之所以要单独指出，是因为这不是 cosmetic switch，而是 journal-specific manuscript front matter 真分叉。继续共享 section files 没问题，但不能假设 `main.tex` 的现有结构天然兼容后备刊。
   - 修改要求：保留 `main_jgc.tex` 方案，并把它视为独立 entrypoint，而不是临时投稿前手动改一处摘要这么简单。

#### Minor

1. **archive integrity check 最好明确为 SHA-256 校验，而不只是“能打开 tar”**
   - 证据位置：
     - [`alibaba-cluster-trace-v2018.md:33`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/sources/alibaba-cluster-trace-v2018.md#L33)
   - 问题原因：当前计划已提出 integrity check，这是对的；但工作台里已经有官方列出的 `container_usage.tar.gz` 校验值，直接做 SHA-256 比仅做 tar open 更硬。
   - 修改要求：把 `container_usage.tar.gz` 的校验值 `b4bd3b1b82f5407c1b0dd47fe736ff5152c4b016a9c30cb26f988e2d1c5e5031` 写进数据准备流程。

2. **计划中同步 `00-status.md` 和 `dataset_manifest.yaml` 是必要项，不应降级为顺手更新**
   - 证据位置：
     - [`00-status.md:10`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/00-status.md#L10)
     - [`dataset_manifest.yaml:8`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/experiments/dataset_manifest.yaml#L8)
     - [`dataset_manifest.yaml:40`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/experiments/dataset_manifest.yaml#L40)
   - 问题原因：当前两个文件仍然写的是 filtered stream / no full mirror 状态。如果 broad 成功落地而这两处不更新，artifact story 会和正文脱节。
   - 修改要求：把这两处同步视为 broad 完成定义的一部分。

3. **本地模板层面上，`main_jgc.tex + \\pacs[MSC Classification]{...}` 是可行的**
   - 证据位置：
     - [`sn-jnl.cls`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sn-jnl.cls)
   - 问题原因：本地 `sn-jnl` 类文件已包含 `\pacs` 宏，因此计划里的 `MSC` 入口不是拍脑袋设计。
   - 修改要求：实现时直接走独立 entrypoint，不必把 JGC fallback 做成复杂条件编译系统。

### Recommended Refinement

- 将 broad promotion 判定规则改成两层：
  - 第一层：任一 headline mean direction flip，立即 promotion。
  - 第二层：即使 mean direction 不翻，但对应主 headline 的稳定性标签从可陈述结论退化为 `not stable`，也 promotion，至少同步 abstract/conclusion wording。

### Delta From Previous Round

- `已解决`
  - broad 计划已从“固定 topN 扩容”升级为“规则筛后全纳 + overlap audit”；
  - JGC fallback 已从抽象想法升级为 `main_jgc.tex` 独立入口设想。

- `未解决`
  - broad promotion 规则还差最后一步：把 stability failure 纳入触发条件；
  - service-level 证据即使扩大，也仍不等于 full population claim。

- `新增`
  - 本地工作台已足以支持 broad 落地：脚本、`abstract_jgc.tex`、manifest/status 文件都在；
  - `sn-jnl` 模板本地支持 `\pacs`，JGC fallback 的模板障碍比预想小。

### Sources Used For This Round

- [Cluster Computing journal page](https://link.springer.com/journal/10586)
- [Cluster Computing submission guidelines](https://www.springer.com/journal/10586/submission-guidelines)
- [Journal of Grid Computing journal page](https://link.springer.com/journal/10723)
- [Journal of Grid Computing submission guidelines](https://www.springer.com/journal/10723/submission-guidelines)
- [Alibaba Cluster Trace Program](https://github.com/alibaba/clusterdata)

## Round 008

- `review_round`: `008`
- `review_date`: `2026-03-11`
- `input_snapshot`:
  - [`main.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.tex)
  - [`abstract.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/abstract.tex)
  - [`abstract_jgc.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/abstract_jgc.tex)
  - [`introduction.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/introduction.tex)
  - [`related_work.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/related_work.tex)
  - [`method.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/method.tex)
  - [`experiments.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/experiments.tex)
  - [`results.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/results.tex)
  - [`threats.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/threats.tex)
  - [`conclusion.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/conclusion.tex)
  - [`declarations.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/declarations.tex)
  - [`highlights.md`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/highlights.md)
  - [`cover-letter.md`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/cover-letter.md)
- `target_journals`:
  - `Primary`: `Cluster Computing`
  - `Backup`: `Journal of Grid Computing`
- `overall_verdict_cluster`: `Minor Revision`
- `overall_verdict_jgc`: `Minor Revision`
- `higher_tier_ceiling`: `Still below threshold without broader service coverage or a stronger implemented temporal backbone`

### Review Summary

这轮修改是实质加分，不是简单润色。和上一轮相比，最关键的改善有四点：

1. [`experiments.tex:87`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/experiments.tex#L87) 已补入标准 neural `MLP` baseline，baseline suite 不再只有 classical models。
2. [`experiments.tex:91`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/experiments.tex#L91) 到 [`experiments.tex:97`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/experiments.tex#L97) 已把 policy baseline 扩展为 reactive、lagged target-tracking、predictive 三者对比，而不再只是 reactive vs predictive 两条线。
3. [`results.tex:118`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/results.tex#L118) 到 [`results.tex:150`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/results.tex#L150) 与 [`results.tex:232`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/results.tex#L232) 到 [`results.tex:265`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/results.tex#L232) 更诚实地呈现了 `MLP` 和 lagged baseline 的位置，没有回避 surrogate 在 machine cohort 上落后于简单 neural baseline 的事实。
4. [`abstract_jgc.tex:1`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/abstract_jgc.tex#L1) 已单独准备 `Journal of Grid Computing` 的长摘要，说明主投/后备双版本已经开始被显式管理。

因此，上一轮“baseline suite 偏轻”这个问题已经被明显削弱。当前稿件比上一轮更接近 `Cluster Computing` 的可投状态。

### Official Gate Snapshot

- `Cluster Computing` 当前作者指南：摘要 `100-150` 词，关键词 `4-6` 个，`Statements and Declarations` 置于参考文献之后。
- `Journal of Grid Computing` 当前作者指南：摘要 `150-250` 词，关键词 `4-6` 个，要求 `MSC` 分类号，并将 `Declarations` 置于参考文献之前。
- 当前稿件机械检查：
  - `Cluster Computing` 摘要：约 `141` 词
  - `Journal of Grid Computing` 摘要：约 `174` 词
  - 关键词数：`5`
  - PDF 页数：`17`
  - 参考文献总数：`31`
  - 未使用文献：`springerlatex2026`、`bai2018empirical`、`weng2022melaas`
  - 当前主稿构建更接近 `Cluster Computing` 版，因为 [`main.tex:46`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.tex#L46) 到 [`main.tex:49`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.tex#L49) 采用 `References -> Declarations` 顺序，且 [`main.tex:19`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.tex#L19) 当前仍接入 `abstract.tex`

### Scorecard

| Dimension | Score (1-5) | Delta | Reviewer note |
| --- | --- | --- | --- |
| `journal fit` | `4` | `0` | 主题与主投/后备期刊继续匹配。 |
| `novelty and contribution` | `3` | `0` | 贡献仍以 evaluation/evidence 为主，而非算法突破。 |
| `problem formulation` | `4` | `0` | 问题、贡献、结论的口径现在更统一。 |
| `method soundness` | `4` | `0` | forecasting-to-control formalization 已较完整。 |
| `experimental rigor` | `4` | `+1` | `MLP` baseline 与 lagged policy baseline 明显增强了比较面。 |
| `reproducibility and transparency` | `4` | `0` | artifact route 与公开计划都比前几轮更稳。 |
| `writing and organization` | `4` | `0` | evaluation-paper 的定位比之前清楚。 |
| `format and submission compliance` | `4` | `0` | `Cluster` 版接近过线，但 `JGC` 版仍需单独包装。 |

### Prioritized Findings

#### Major

1. **`Journal of Grid Computing` 备用版本仍未真正成型，只是摘要已分流**
   - 证据位置：
     - [`abstract_jgc.tex:1`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/abstract_jgc.tex#L1)
     - [`main.tex:19`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.tex#L19) 到 [`main.tex:21`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.tex#L21)
     - [`main.tex:46`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.tex#L46) 到 [`main.tex:49`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.tex#L49)
   - 问题原因：你已经准备了 `JGC` 长摘要，这是对的；但当前主构建仍接入 `Cluster` 短摘要，没有 `MSC` 分类号，而且声明区顺序还是 `Cluster` 版顺序。也就是说，当前项目已经有 fallback 素材，但还没有 fallback 成稿入口。
   - 修改要求：如果要把 `JGC` 真正当后备路线，需要补一个最小化的 `JGC` build variant：`abstract_jgc + MSC codes + declarations-before-references`。

2. **service-level 证据依然是当前最主要的研究边界**
   - 证据位置：
     - [`experiments.tex:21`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/experiments.tex#L21) 到 [`experiments.tex:23`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/experiments.tex#L23)
     - [`threats.tex:6`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/threats.tex#L6) 到 [`threats.tex:13`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/threats.tex#L13)
   - 问题原因：现在 selection rule 已经写得更 defensible，service-level control 也被三路 policy 比较压得更扎实，但 cohort 仍然只有 `10` 个 `app_du`。这对目标刊仍可 defend，但继续限制了 generalization story。
   - 修改要求：如果后续还要继续增强录用概率，优先级仍然是扩大 service cohort 或补 selection-stability evidence。

3. **`UA-MSTCN-Lite` 的命名与当前 surrogate 实现之间仍有轻微张力**
   - 证据位置：
     - [`method.tex:65`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/method.tex#L65)
     - [`threats.tex:9`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/threats.tex#L9) 到 [`threats.tex:10`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/threats.tex#L10)
   - 问题原因：稿件已经承认它是 surrogate，但名字依然容易让 reviewer 先预期真实 TCN backbone。现在这个风险比之前小，但还没有完全消失。
   - 修改要求：在方法首段或引言贡献段再提前一句明确“interface instantiated by a lightweight surrogate”，以压低误读风险。

#### Minor

1. **baseline 风险已明显下降，但还没有完全达到“method-heavy paper”那种厚度**
   - 证据位置：
     - [`experiments.tex:87`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/experiments.tex#L87)
     - [`results.tex:118`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/results.tex#L118)
   - 问题原因：`MLP` baseline 和 lagged target baseline 的加入是明确加分，但如果 reviewer 站在更强 forecasting-method 角度，仍可能追问为什么没有更标准的 sequence baseline，如 `LSTM`/plain `TCN`。
   - 修改要求：对目标刊可以先不补；但若还有时间，补一个最基础的 sequence baseline 会继续抬高说服力。

2. **submission package 还没有完全反映这轮 baseline 扩展**
   - 证据位置：
     - [`highlights.md:3`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/highlights.md#L3) 到 [`highlights.md:7`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/highlights.md#L7)
     - [`cover-letter.md:7`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/cover-letter.md#L7) 到 [`cover-letter.md:11`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/cover-letter.md#L11)
   - 问题原因：正文现在已经有 `MLP` baseline 和 lagged target-tracking baseline，但投稿包仍只概括为 linear baseline / predictive vs reactive。它不算错误，但略微落后于当前稿件的实验设计成熟度。
   - 修改要求：投稿前可以顺手把 cover letter 的 systems trade-off 描述更新成“三路 policy comparison”。

3. **参考文献与版式清洁度仍可再收尾**
   - 证据位置：
     - [`refs.bib`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/refs.bib)
     - [`main.log`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.log)
   - 问题原因：仍有 `3` 个未用条目，双栏 warning 仍然较多。
   - 修改要求：提交前做一次最后的 bib 清理和版式清洁即可。

### Required Actions Before Submission

1. 保持当前 `Cluster Computing` 主稿路线不变。
2. 若真把 `Journal of Grid Computing` 作为后备，补一个最小的 `JGC` 主文件或切换机制：`abstract_jgc + MSC + declarations-before-references`。
3. 在更前的位置再明确一句 `UA-MSTCN-Lite` 当前是 lightweight surrogate instantiation。
4. 若还有一轮增强空间，优先继续扩 service cohort；次优先是再补一个 sequence baseline。
5. 清理 `3` 个未使用参考文献，并做最后一轮双栏版式修整。

### Delta From Previous Round

- `已解决`
  - 已加入标准 neural `MLP` baseline；
  - 已加入 lagged target-tracking policy baseline；
  - 结果节已更完整地呈现三路 policy surface；
  - `JGC` 长摘要已单独准备。

- `未解决`
  - targeted 10-service cohort 仍是最大外部效度限制；
  - `UA-MSTCN-Lite` 的命名与 surrogate 实现仍有轻微张力；
  - `Cluster`/`JGC` 双版本还未形成完整 build 流程；
  - bib 清洁度与版式 warning 仍未完全收尾。

- `新增`
  - `JGC` 当前新增的明确要求是 `MSC` 分类号与 declarations-before-references，这使后备刊版本的包装分叉更具体；
  - baseline 风险已从“明显偏轻”下降为“仍可再增强但不再是核心短板”。

### Sources Used For This Round

- [Cluster Computing journal page](https://link.springer.com/journal/10586)
- [Cluster Computing submission guidelines](https://www.springer.com/journal/10586/submission-guidelines)
- [Journal of Grid Computing journal page](https://link.springer.com/journal/10723)
- [Journal of Grid Computing submission guidelines](https://www.springer.com/journal/10723/submission-guidelines)
- [Alibaba Cluster Trace Program](https://github.com/alibaba/clusterdata)

## Round 007

- `review_round`: `007`
- `review_date`: `2026-03-11`
- `input_snapshot`:
  - [`main.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.tex)
  - [`abstract.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/abstract.tex)
  - [`abstract_jgc.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/abstract_jgc.tex)
  - [`introduction.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/introduction.tex)
  - [`related_work.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/related_work.tex)
  - [`method.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/method.tex)
  - [`experiments.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/experiments.tex)
  - [`results.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/results.tex)
  - [`threats.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/threats.tex)
  - [`conclusion.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/conclusion.tex)
  - [`declarations.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/declarations.tex)
  - [`highlights.md`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/highlights.md)
  - [`cover-letter.md`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/cover-letter.md)
  - [`PLAN.md`](/Users/liujinchun/Downloads/PLAN.md)
- `target_journals`:
  - `Primary`: `Cluster Computing`
  - `Backup`: `Journal of Grid Computing`
- `overall_verdict_cluster`: `Minor Revision`
- `overall_verdict_jgc`: `Minor Revision`
- `higher_tier_ceiling`: `Below threshold unless baseline rigor and service-level breadth are strengthened`

### Review Summary

这轮修改是有效的，而且不是表面修辞层面的微调。和上一轮相比，稿件在“正式投稿成熟度”和“evaluation paper 定位一致性”上都前进了一步：

1. [`main.tex:46`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.tex#L46) 到 [`main.tex:49`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.tex#L49) 已把 `References` 放到 `Statements and Declarations` 之前，主投 `Cluster Computing` 的一个格式性风险已解决。
2. [`introduction.tex:3`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/introduction.tex#L3) 到 [`introduction.tex:20`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/introduction.tex#L20) 与 [`related_work.tex:1`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/related_work.tex#L1) 到 [`related_work.tex:40`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/related_work.tex#L40) 已明显去掉“target journal / EI-oriented / aligned with precedent”这类元叙述，正文更像正式 paper。
3. [`declarations.tex:13`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/declarations.tex#L13) 到 [`declarations.tex:20`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/declarations.tex#L20) 已把数据与代码声明升级为“acceptance 后公开仓库”，reproducibility 说服力强于上一轮。
4. [`experiments.tex:23`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/experiments.tex#L23) 和 [`threats.tex:7`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/threats.tex#L7) 已把 service cohort 选择规则写得更程序化，selection bias 仍在，但表述比上一轮更 defensible。
5. [`abstract_jgc.tex:1`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/abstract_jgc.tex#L1) 已单独准备 `Journal of Grid Computing` 版本摘要，主投/后备的包装分叉开始被显式管理。

因此，本轮最大变化不是再一次“把稿件修得更像正式稿”，而是：**原来那些明显的 submission/package 问题大多已被消化，剩余风险开始集中到研究设计本身。**

### Official Gate Snapshot

- `Cluster Computing` 当前作者指南：摘要 `100-150` 词，关键词 `4-6` 个，并要求 `Statements and Declarations` 与 `Data Availability Statement`。
- `Journal of Grid Computing` 当前作者指南：摘要 `150-250` 词，关键词 `4-6` 个，并要求同类声明。
- 当前稿件机械检查：
  - `Cluster Computing` 摘要：[`abstract.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/abstract.tex) 约 `141` 词
  - `Journal of Grid Computing` 摘要：[`abstract_jgc.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/abstract_jgc.tex) 约 `174` 词
  - 关键词数：`5`
  - 模板：`sn-jnl`
  - PDF 页数：`17`
  - 参考文献总数：`31`
  - 未使用文献：`springerlatex2026`、`bai2018empirical`、`weng2022melaas`
  - 版式：`main.log` 仍有大量 underfull / 少量 overfull warnings，但未见本轮新的未定义引用错误

### PLAN Alignment

- `与 PLAN 一致`
  - 仍以公开 Alibaba traces 为唯一强制数据源；
  - 仍围绕 forecasting-to-policy 的 proactive autoscaling 主线；
  - 仍保留 `1/5/10` 分钟 horizon、`30/60/120` 分钟 context sensitivity、bursty/stable regime analysis、transfer benchmark、policy ablation；
  - 仍把论文定位在 `Cluster Computing` 主投、`Journal of Grid Computing` 后备。

- `与 PLAN 偏离`
  - [`PLAN.md:97`](/Users/liujinchun/Downloads/PLAN.md#L97) 到 [`PLAN.md:110`](/Users/liujinchun/Downloads/PLAN.md#L110) 原计划的预测基线包括 `ARIMA`、`LightGBM/XGBoost`、`LSTM`、`Plain TCN`，而当前正文只有 persistence / moving average / linear regression / random forest / `UA-MSTCN-Lite`。
  - [`PLAN.md:106`](/Users/liujinchun/Downloads/PLAN.md#L106) 到 [`PLAN.md:110`](/Users/liujinchun/Downloads/PLAN.md#L110) 原计划的策略基线包括 `HPA-style reactive policy` 与 `predictive policy without uncertainty margin`；当前正文主要是 reactive threshold、full predictive 以及 ablation 变体。
  - `UA-MSTCN` 在原计划中更偏向实际多尺度 TCN 主体；当前稿件已经诚实说明它是可训练 surrogate，但这也意味着算法 novelty 比原始计划更轻。

### Scorecard

| Dimension | Score (1-5) | Delta | Reviewer note |
| --- | --- | --- | --- |
| `journal fit` | `4` | `0` | 主题与主投/后备期刊仍然匹配。 |
| `novelty and contribution` | `3` | `0` | evaluation contribution 已更清楚，但 algorithm novelty 仍偏轻。 |
| `problem formulation` | `4` | `0` | 问题定义已与 mixed-result evidence 更一致。 |
| `method soundness` | `4` | `0` | forecasting-to-control 映射清楚，service-level formalization 充分。 |
| `experimental rigor` | `3` | `-1` | 多层证据完整，但 baseline suite 比计划和常见 method paper 更轻，这一点现在更显眼。 |
| `reproducibility and transparency` | `4` | `+1` | code/data availability wording 明显改善。 |
| `writing and organization` | `4` | `0` | 元叙述显著减少，正文和投稿材料更统一。 |
| `format and submission compliance` | `5` | `+1` | 主投版格式风险显著下降，后备摘要也已独立准备。 |

### Prioritized Findings

#### Major

1. **当前最主要的 remaining risk 已不再是模板或口径，而是 baseline suite 偏轻**
   - 证据位置：
     - [`experiments.tex:87`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/experiments.tex#L87) 到 [`experiments.tex:96`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/experiments.tex#L96)
     - [`PLAN.md:97`](/Users/liujinchun/Downloads/PLAN.md#L97) 到 [`PLAN.md:110`](/Users/liujinchun/Downloads/PLAN.md#L110)
   - 问题原因：现在稿件已经明确按 evaluation paper 叙事来写，这是进步；但 reviewer 仍可能追问，为什么 related work 明确讨论了 `ARIMA`、`LSTM`、`TCN`、framework-style predictive autoscaling，而实验只保留了更轻的一组 baselines。对 `Cluster Computing` 这不一定致命，但它会降低“方法层有多强”的说服力。
   - 修改要求：
     - 最优解：至少补一个标准 neural forecasting baseline（`LSTM` 或 plain `TCN` 二选一）和一个更显式的 policy baseline（如 predictive without uncertainty margin 的独立主表行）。
     - 次优解：如果不准备扩实验，就必须在正文里主动解释 baseline 筛选原则，避免 reviewer 觉得是 selective comparison。

2. **`UA-MSTCN-Lite` 的命名仍然略强于当前实现本体**
   - 证据位置：
     - [`method.tex:54`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/method.tex#L54) 到 [`method.tex:55`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/method.tex#L55)
     - [`experiments.tex:87`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/experiments.tex#L87)
     - [`threats.tex:9`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/threats.tex#L9) 到 [`threats.tex:10`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/threats.tex#L10)
   - 问题原因：你已经诚实写明它是 surrogate，这很好；但 `MSTCN` 这个名字仍然天然让 reviewer 先联想到真实 convolutional backbone。若读者读到实验才发现它本质是 quantile-forest surrogate，仍可能产生“命名先行”的观感。
   - 修改要求：二选一更稳：
     - 继续保留名称，但在 introduction/contribution 中更早一句明确说明它是 `UA-MSTCN interface instantiated by a lightweight surrogate`;
     - 或直接把名称改得更贴近实现，降低 architectural overclaim 风险。

3. **service-level 证据已经更稳，但仍然只是 targeted extension，不足以支撑更高层级期刊的 generalization 期待**
   - 证据位置：
     - [`experiments.tex:21`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/experiments.tex#L21) 到 [`experiments.tex:23`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/experiments.tex#L23)
     - [`threats.tex:6`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/threats.tex#L6) 到 [`threats.tex:13`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/threats.tex#L13)
   - 问题原因：你现在已经把这件事写得足够诚实，所以对 `Cluster Computing` / `Journal of Grid Computing` 是可 defend 的；但 reviewer 仍会把它视为最主要的外部效度限制。尤其在 service-level control 结果是 mixed 的情况下，cohort breadth 仍直接影响论证力度。
   - 修改要求：如果继续改稿，优先做 cohort widening 或 selection-stability appendix，而不是先重写 narrative。

#### Minor

1. **主投/后备双版本已经存在，但 journal-specific 切换尚未进入主 build 习惯**
   - 证据位置：
     - [`main.tex:19`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.tex#L19)
     - [`abstract_jgc.tex:1`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/abstract_jgc.tex#L1)
   - 问题原因：你已经准备好了 `JGC` 摘要，这是好事；但当前主稿仍只直接接入 `abstract.tex`。如果后续频繁切刊，最好把切换方式固定下来，减少人为遗漏。
   - 修改要求：保持两个摘要文件并在提交前显式切换即可；不必复杂化，只要流程固定。

2. **参考文献清洁度还可以再收尾**
   - 证据位置：
     - [`refs.bib`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/refs.bib)
   - 问题原因：现在总数已降到 `31`，但仍有 `3` 个未使用条目。
   - 修改要求：删除未用条目，统一 DOI / URL 样式。

3. **版式 warning 仍然很多，但已经从“阻塞”退化为“清洁度问题”**
   - 证据位置：
     - [`main.log`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.log)
   - 问题原因：underfull warnings 仍多，说明双栏模板下还有表格/长句断行可以优化。
   - 修改要求：投稿前集中处理 service 表格和几处长 caption 即可。

### Required Actions Before Submission

1. 决定是否愿意再补一个标准 neural forecasting baseline 和一个更清晰的 policy baseline。
2. 如果不补实验，就在实验设计里主动解释 baseline 选择原则，减少 reviewer 对 selective comparison 的怀疑。
3. 在更前的位置再明确一句：`UA-MSTCN-Lite` 当前是由 lightweight surrogate 实例化的接口，而不是完整 deep TCN 主体。
4. 保留当前 `Cluster Computing` 主摘要与 `Journal of Grid Computing` 备用摘要的双文件结构。
5. 清掉 `3` 个未使用参考文献并做最后一轮版式清理。

### Delta From Previous Round

- `已解决`
  - `Cluster Computing` 的声明区位置问题已解决；
  - 引言与 related work 中的 target-journal 元叙述已显著减少；
  - `code/data availability` 已从单纯 `reasonable request` 升级为 `upon acceptance public release`；
  - `Journal of Grid Computing` 的独立摘要已准备完成；
  - service cohort 的 selection rule 叙述已更程序化。

- `未解决`
  - service-level policy 仍然是 mixed trade-off，而不是稳定 superiority；
  - targeted 10-service cohort 仍然是最主要的外部效度限制；
  - `UA-MSTCN-Lite` 的命名与实现之间仍有轻微张力；
  - 版式 warning 与少量参考文献清洁度问题仍在。

- `新增`
  - baseline suite 偏轻现在成为最核心的 reviewer risk；
  - 主投/后备摘要分叉已经从“问题”转成“已管理的双版本流程”。

### Sources Used For This Round

- [Cluster Computing journal page](https://link.springer.com/journal/10586)
- [Cluster Computing submission guidelines](https://www.springer.com/journal/10586/submission-guidelines)
- [Journal of Grid Computing journal page](https://link.springer.com/journal/10723)
- [Journal of Grid Computing submission guidelines](https://www.springer.com/journal/10723/submission-guidelines)
- [Alibaba Cluster Trace Program](https://github.com/alibaba/clusterdata)

## Round 006

- `review_round`: `006`
- `review_date`: `2026-03-11`
- `input_snapshot`:
  - [`main.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.tex)
  - [`introduction.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/introduction.tex)
  - [`related_work.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/related_work.tex)
  - [`method.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/method.tex)
  - [`results.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/results.tex)
  - [`conclusion.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/conclusion.tex)
  - [`refs.bib`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/refs.bib)
- `target_journals`:
  - `Primary`: `Cluster Computing`
  - `Backup`: `Journal of Grid Computing`
- `overall_verdict_cluster`: `Minor Revision`
- `overall_verdict_jgc`: `Minor Revision`
- `higher_tier_ceiling`: `Still below stronger venue threshold due novelty packaging and service-level breadth`

### Comparative Review Against Published Papers

这轮不是常规格式核对，而是把当前稿件直接放到已见刊同主题文章旁边比较。结论很明确：**你现在的短板已经不是体量，而是“贡献类型的包装方式”和“正式期刊话语风格”**。

- `体量`：当前稿件 PDF 为 `17` 页、参考文献 `33` 条，在目标刊里并不算短。对比已见刊文章：
  - Casalicchio 2019 的 `Cluster Computing` 容器 autoscaling 文章约 `12` 页；
  - Kovács 2019 的 `Journal of Grid Computing` Kubernetes autoscaler 文章约 `17` 页；
  - OnlineElastMan 2017 的 `Cluster Computing` 文章约 `18` 页。
  - 因此，**你的问题不是“稿子太短”**，而是同样页数下，published paper 往往把更多篇幅给“系统对象、方法细节、实验设计与结论压缩”，而你仍留了一部分篇幅给“解释这篇稿件为什么适合投稿”。

- `成果与开创性`：当前稿件最强的贡献不是“提出了一个显著更强的新 autoscaler”，而是“建立了一个公共 Alibaba traces 驱动的 forecasting-to-control、aggregate-to-service 的可复现实证框架，并用 service-level 结果揭示了 policy boundary”。这在 `Cluster Computing` / `Journal of Grid Computing` 是可以成立的，但和已见刊文章相比，它属于 **benchmark/evaluation contribution**，不是 **algorithm/system contribution**。
  - 相比 Rossi et al. 2025，你在“多层证据 + uncertainty-aware framing”上已经同方向，但对方的 experimental surface 更广，而且 novelty 更集中在 forecasting method 与 cross-dataset generalization。
  - 相比 Zanussi et al. 2026 或 Kovács 2019，这些文章更像“提出一个可执行的 autoscaling framework / rule system / hybrid model 并展示 operational benefit”；你的稿件目前更像“建立一个诚实的 public-trace testbed，并展示 predictive policy 并非处处占优”。
  - 这不是坏事，但要求你在 positioning 上更精准：**不要把自己包装成一个已被证明显著更优的 autoscaling method paper，而要包装成一个 reproducible evaluation and boundary-mapping paper**。

- `表达方式`：这是当前和已见刊稿差距最大的地方。正式文章通常直接写 problem, method, evidence, limitation；而你正文里仍保留了明显的投稿/工作台元叙述。

### Prioritized Findings

#### Major

1. **正文仍有明显的“面向编辑解释投稿定位”的元叙述，这不是已见刊论文的常见写法**
   - 证据位置：
     - [`introduction.tex:3`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/introduction.tex#L3)
     - [`introduction.tex:5`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/introduction.tex#L5)
     - [`introduction.tex:13`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/introduction.tex#L13)
     - [`introduction.tex:20`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/introduction.tex#L20)
     - [`related_work.tex:1`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/related_work.tex#L1)
     - [`related_work.tex:7`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/related_work.tex#L7)
     - [`results.tex:205`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/results.tex#L205)
   - 问题原因：像 `target journal`、`EI-oriented systems paper`、`useful manuscript evidence`、`aligned with published Cluster Computing precedent` 这类说法，更适合 cover letter，不适合出现在 paper body。已见刊文章通常不在正文里讨论“为什么这篇稿适合这个刊”，而是直接让问题、方法和证据自行成立。
   - 修改要求：把这些元叙述全部移出正文。相关定位可以保留在 [`cover-letter.md`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/cover-letter.md)，但正文应改成标准 scholarly prose。

2. **与已见刊文章相比，当前稿件的 novelty 类型是“evaluation contribution”，但贡献段还没有完全按这个类型重写**
   - 证据位置：
     - [`introduction.tex:15`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/introduction.tex#L15) 到 [`introduction.tex:20`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/introduction.tex#L20)
     - [`conclusion.tex:1`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/conclusion.tex#L1) 到 [`conclusion.tex:5`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/conclusion.tex#L5)
   - 问题原因：现在最可信的贡献其实是：
     - 公共 trace 驱动的 forecasting-to-control pipeline；
     - aggregate / machine / transfer / service 四层证据；
     - 对 predictive policy 的 honest boundary finding。
     这与已见刊的 “new autoscaling framework”, “programmable rule engine”, “hybrid load-aware model” 不是同一种贡献。若仍按 algorithm-first 方式写 contribution，会让 novelty 看起来偏弱。
   - 修改要求：把 contribution wording 明确改成 benchmark / evaluation / evidence contribution，而不是让读者误以为你主打的是一个已经证明强优的 controller 或深模型。

3. **与见刊稿相比，你的 experimental breadth 已经够投稿，但 research payoff 仍偏“边界揭示”而非“强性能突破”**
   - 证据位置：
     - [`results.tex:216`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/results.tex#L216) 到 [`results.tex:256`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/results.tex#L256)
   - 问题原因：已见刊的 systems/autoscaling 文章通常至少在某一主轴上给出比较干脆的 win story，例如更好 SLA、成本、弹性策略、框架能力或部署可编程性。你这篇的强项在于“service-level mixed result 也没有被掩盖”，这在审稿上是加分，但它天然比正向性能 story 更难卖。
   - 修改要求：投稿时要主动把 value proposition 写成“negative and mixed findings on public traces are still scientifically valuable because they identify when predictive autoscaling fails under service heterogeneity”，而不是被动地把 mixed result 当作一个不太好看的残余。

#### Minor

1. **篇幅本身不是主要不足，但 references 和 related-work density 仍可再厚一点**
   - 证据位置：
     - [`refs.bib`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/refs.bib)
     - [`related_work.tex:22`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/related_work.tex#L22)
   - 问题原因：`33` 条参考文献对于 EI/Springer 期刊是可接受的，但与较新的同主题文章相比，你的 references 更像“够用”，还不算“厚实”。这会让 paper 看起来更像一篇扎实的 focused study，而不是 literature-dominating article。
   - 修改要求：不必盲目堆文献，但可以再补少量近年 uncertainty-aware autoscaling / service-level scaling / public-trace evaluation 的代表文献，尤其是 2023–2026 的同主题工作。

2. **相关工作里那张“对 target journal 文章的定位表”思路是对的，但放法不够像正式见刊稿**
   - 证据位置：
     - [`related_work.tex:5`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/related_work.tex#L5) 到 [`related_work.tex:20`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/related_work.tex#L20)
   - 问题原因：published paper 会比较 prior work，但通常不会直接把表题写成“Positioning against selected published work most relevant to the target journal route”。
   - 修改要求：保留表的实质信息，但把 framing 改成 standard literature-comparison table，而不是投稿路线说明表。

### Delta From Previous Round

- `已解决`
  - 本轮无新的格式性修复项，重点转为 published-paper benchmarking。

- `未解决`
  - mixed result 仍需更主动地包装为 positive scientific value；
  - service cohort breadth 仍弱于更强文章的 generalization surface；
  - data/code openness 仍偏保守。

- `新增`
  - 已明确识别出当前与见刊稿的最大风格差距是正文中的元叙述；
  - 已明确识别出当前贡献应按 `evaluation/benchmark paper` 而不是 `algorithm/framework paper` 来包装。

### Sources Used For This Round

- [Cluster Computing journal page](https://link.springer.com/journal/10586)
- [Cluster Computing submission guidelines](https://www.springer.com/journal/10586/submission-guidelines)
- [Journal of Grid Computing journal page](https://link.springer.com/journal/10723)
- [Journal of Grid Computing submission guidelines](https://www.springer.com/journal/10723/submission-guidelines)
- [Rossi et al., Cluster Computing (2025)](https://link.springer.com/article/10.1007/s10586-024-04933-2)
- [Casalicchio et al., Cluster Computing (2019)](https://link.springer.com/article/10.1007/s10586-017-1610-y)
- [OnlineElastMan, Cluster Computing (2017)](https://link.springer.com/article/10.1007/s10586-017-1170-1)
- [Kovács, Journal of Grid Computing (2019)](https://link.springer.com/article/10.1007/s10723-019-09497-0)
- [Zanussi et al., Cluster Computing (2026)](https://link.springer.com/article/10.1007/s10586-026-04761-w)

## Round 005

- `review_round`: `005`
- `review_date`: `2026-03-11`
- `input_snapshot`:
  - [`main.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.tex)
  - [`abstract.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/abstract.tex)
  - [`introduction.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/introduction.tex)
  - [`method.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/method.tex)
  - [`experiments.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/experiments.tex)
  - [`results.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/results.tex)
  - [`threats.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/threats.tex)
  - [`conclusion.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/conclusion.tex)
  - [`declarations.tex`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/declarations.tex)
  - [`refs.bib`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/refs.bib)
  - [`highlights.md`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/highlights.md)
  - [`cover-letter.md`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/cover-letter.md)
- `target_journals`:
  - `Primary`: `Cluster Computing`
  - `Backup`: `Journal of Grid Computing`
- `overall_verdict_cluster`: `Minor Revision`
- `overall_verdict_jgc`: `Minor Revision`
- `higher_tier_ceiling`: `Below threshold without broader service coverage or stronger service-level control evidence`

### Review Summary

这轮稿件已经从“还在收拾正式稿基本面”进入“可以认真冲投稿，但要把最后几处 journal-specific 问题和 claim 口径再收紧”的阶段。最重要的正向变化有五点：

1. [`main.tex:15`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.tex#L15) 到 [`main.tex:17`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.tex#L17) 的作者与 affiliation 已补成正式信息。
2. [`abstract.tex:1`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/abstract.tex#L1) 已显著压缩，并且现在更准确地把结论收束为“mixed but reproducible evidence”。
3. [`method.tex:1`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/method.tex#L1) 到 [`method.tex:32`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/method.tex#L32) 已把 entity-level 与 service-level mapping 形式化，修掉了前几轮 methods 落后于 results 的问题。
4. [`conclusion.tex:1`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/conclusion.tex#L1) 到 [`conclusion.tex:5`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/conclusion.tex#L5) 已切回标准 journal 结论口吻，不再像内部 workbench 路线图。
5. [`highlights.md:3`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/highlights.md#L3) 到 [`highlights.md:7`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/highlights.md#L7) 与 [`cover-letter.md:7`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/cover-letter.md#L7) 到 [`cover-letter.md:11`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/submission/cover-letter.md#L11) 已和 broad service-level 正文同步。

因此，前几轮那些明显的 editor-level 旧伤大多已经被修掉。当前剩下的问题主要分成两类：一类是 `Cluster Computing` / `Journal of Grid Computing` 之间的包装分叉，另一类是 research question 与 service-level 结果之间仍有一小段口径张力。

### Official Gate Snapshot

- `Cluster Computing` 当前作者指南：摘要 `100-150` 词，关键词 `4-6` 个，并要求 `Statements and Declarations` 与 `Data Availability Statement`。
- `Journal of Grid Computing` 当前作者指南：摘要 `150-250` 词，关键词 `4-6` 个，并要求同类声明。
- 当前稿件机械检查：
  - 摘要词数：约 `141`
  - 关键词数：`5`
  - 模板：`sn-jnl`
  - PDF 页数：`17`
  - 声明项：已包含 `Funding`、`Competing interests`、`Ethics approval and consent to participate`、`Consent for publication`、`Data availability`、`Materials availability`、`Code availability`、`Author contribution`
  - 参考文献总数：`33`
  - 未使用文献：`springerlatex2026`、`bai2018empirical`、`weng2022melaas`
  - 版式：`main.log` 仍有较多 underfull / overfull box warnings

### Scorecard

| Dimension | Score (1-5) | Delta | Reviewer note |
| --- | --- | --- | --- |
| `journal fit` | `4` | `0` | 主题与目标刊持续匹配，且 service-level evidence 已经足以支撑 cluster-resource-management 叙事。 |
| `novelty and contribution` | `3` | `0` | 新意主要来自 reproducible multi-granularity evidence 与 honest negative/mixed control result，而不是模型本体。 |
| `problem formulation` | `4` | `+1` | formalization 已明显改善，但引言里仍残留一处略强的“improves decision quality”表述。 |
| `method soundness` | `4` | `+2` | entity/service mapping 现已和结果层级基本对齐。 |
| `experimental rigor` | `4` | `0` | aggregate、machine、transfer、service 四层证据已成体系。 |
| `reproducibility and transparency` | `4` | `0` | 公共数据路线、artifact contract、submission package 均更成熟，但 code/data 仍非直接公开。 |
| `writing and organization` | `4` | `+1` | 引言、方法、结论和投稿材料的一致性已明显提升。 |
| `format and submission compliance` | `4` | `+1` | 当前主要问题不再是模板缺失，而是目标刊之间的 abstract/declaration placement 分叉。 |

### Prioritized Findings

#### Blocker

1. **当前版本对主投与后备期刊的摘要门槛已经出现分叉**
   - 证据位置：
     - [`abstract.tex:1`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/abstract.tex#L1)
   - 问题原因：当前摘要约 `141` 词，已经满足 `Cluster Computing` 的 `100-150` 词要求，但低于 `Journal of Grid Computing` 的 `150-250` 词要求。也就是说，你现在的正文更接近主投版，但已经不再是一个可以直接一稿两投包打天下的 fallback 版本。
   - 修改要求：保留当前 `Cluster Computing` 短摘要，同时单独准备一个 `Journal of Grid Computing` 版本的较长摘要，避免到转投时再临时改写。

#### Major

1. **`Cluster Computing` 版声明区位置仍建议调整到参考文献之后**
   - 证据位置：
     - [`main.tex:46`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.tex#L46) 到 [`main.tex:49`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.tex#L49)
   - 问题原因：当前 `Statements and Declarations` 被放在 bibliography 之前，而本轮核对的 `Cluster Computing` 提交说明明确要求把该部分置于 `References` 之后。这不是科研质量问题，但属于投稿格式层面的 journal-specific risk。
   - 修改要求：为主投版把 `\bibliography{refs}` 移到声明区前面，或在项目里维护两个很轻量的 journal-specific front/back matter 变体。

2. **研究问题在引言里仍略强于当前最稳妥的证据边界**
   - 证据位置：
     - [`introduction.tex:7`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/introduction.tex#L7)
     - [`results.tex:216`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/results.tex#L216) 到 [`results.tex:256`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/results.tex#L256)
   - 问题原因：引言当前仍把核心问题写成“是否 improves decision quality over reactive rules”。而 service-level 结果更准确的解读是：predictive route 在 aggregate 上改善资源效率，在 service level 上暴露异质 trade-off 与 policy boundary。摘要和结论已经基本处理好了这一点，但引言的问题句还没完全跟上。
   - 修改要求：把研究问题改成“whether public traces can support a reproducible predictive capacity-control evaluation that clarifies when decision trade-offs improve relative to reactive rules”之类的 evaluative wording，而不是直接预设 improvement。

3. **service cohort 的选择规则仍是当前最主要的外部效度风险**
   - 证据位置：
     - [`experiments.tex:23`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/experiments.tex#L23)
     - [`threats.tex:6`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/threats.tex#L6) 到 [`threats.tex:13`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/threats.tex#L13)
   - 问题原因：你已经诚实写明这是 targeted high-coverage subset，这很好；但当前 10-service 扩展仍部分依赖 low-`container_id` prefix 的务实选择规则。严格 reviewer 会接受它作为 limitation，但也会把它视为最主要的 residual bias source。
   - 修改要求：至少补一句更 procedure-like 的选择算法说明，强调它是 coverage-driven filtering 而非 result-driven picking；如果后续还改稿，优先补一个 selection-stability/robustness 附表，而不是先堆更多模型。

#### Minor

1. **`Data availability` 与 `Code availability` 仍然偏保守**
   - 证据位置：
     - [`declarations.tex:13`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/declarations.tex#L13) 到 [`declarations.tex:20`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/declarations.tex#L20)
   - 问题原因：`available on reasonable request` 的 reproducibility 说服力明显弱于直接给 public repository / archive link。
   - 修改要求：如果代码还不方便完全公开，至少在声明里给出“will be released upon acceptance”或 planned repository wording。

2. **参考文献清洁度仍可再收尾**
   - 证据位置：
     - [`refs.bib`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/refs.bib)
   - 问题原因：仍有 `3` 个未使用条目，且可进一步统一 DOI / URL 样式。
   - 修改要求：删除未用条目，统一条目格式，减少提交前的模板噪音。

3. **版式警告仍然偏多**
   - 证据位置：
     - [`main.log`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/main.log)
   - 问题原因：当前 PDF 已可读，但 `main.log` 仍有大量 overfull / underfull box warnings，说明表格、图注和长句断行仍有优化空间。
   - 修改要求：优先检查 service-level 表格和长 caption，因为这部分最容易在 Springer 双栏下挤出大 warning。

### Required Actions Before Submission

1. 为 `Cluster Computing` 调整 `Statements and Declarations` 到参考文献之后。
2. 保留当前 `141` 词短摘要作为主投版，同时准备 `Journal of Grid Computing` 的 `150-250` 词 fallback 摘要。
3. 把 [`introduction.tex:7`](/Users/liujinchun/Downloads/skills_codex/paper-workbench/manuscript/sections/introduction.tex#L7) 的研究问题改成 trade-off/evaluation wording。
4. 在 service cohort 描述里把 selection rule 再程序化一点，减少 convenience-sampling 观感。
5. 如果时间允许，至少把 code/data 的公开计划写得更前瞻，而不是只写 `reasonable request`。

### Delta From Previous Round

- `已解决`
  - affiliation 已补正式信息；
  - 结论已改成标准 journal 风格；
  - `highlights.md` 与 `cover-letter.md` 已同步到 broad service-level 版本；
  - method 与 service-level evidence 的 formalization 已基本对齐；
  - 主投 `Cluster Computing` 的摘要长度问题已解决。

- `未解决`
  - service-level policy 仍然呈现 mixed trade-off，而非稳定 superiority；
  - code/data availability 仍偏保守；
  - targeted service cohort 仍是最主要的 residual validity risk；
  - 版式 warning 仍较多。

- `新增`
  - 当前摘要已经转为 `Cluster Computing` 友好版，但对 `Journal of Grid Computing` 反而偏短；
  - `Cluster Computing` 版声明区位置现在成为更显性的格式问题；
  - 引言核心问题句相对摘要/结论仍略强。

### Sources Used For This Round

- [Cluster Computing journal page](https://link.springer.com/journal/10586)
- [Cluster Computing submission guidelines](https://www.springer.com/journal/10586/submission-guidelines)
- [Journal of Grid Computing journal page](https://link.springer.com/journal/10723)
- [Journal of Grid Computing submission guidelines](https://www.springer.com/journal/10723/submission-guidelines)
- [Alibaba Cluster Trace Program](https://github.com/alibaba/clusterdata)
