# Target-Journal Style Analysis

This note benchmarks the draft against papers already published in `Cluster Computing`.
All counts below were checked on March 10, 2026 from official Springer article pages.

## Representative papers

| Paper | Link | Topical fit to our draft | Main section pattern | Approx. references | Approx. figures | Notes |
| --- | --- | --- | --- | ---: | ---: | --- |
| Rossi et al., 2025, `Forecasting workload in cloud computing: towards uncertainty-aware predictions and transfer learning` | https://link.springer.com/article/10.1007/s10586-024-04933-2 | Very high: workload forecasting, uncertainty, Google + Alibaba traces, cloud resource management | Introduction; Related work; Methodology; Experimental results; Conclusion and future work; Data availability; Code availability; Appendices | 70 | 11 | This is the strongest direct benchmark for our paper's expected body size. |
| Casalicchio, 2019, `A study on performance measures for auto-scaling CPU-intensive containerized applications` | https://link.springer.com/article/10.1007/s10586-018-02890-1 | High: container autoscaling, metric selection, performance evaluation | Introduction; Motivating example; Workload characterization; Correlation model; Auto-scaling performance evaluation; Related works; Conclusions | 37 | 7 | Even an older application-focused paper carries a substantial experimental narrative and a dedicated related-work section. |
| Dinda and O'Hallaron, 2000, `Host load prediction using linear models` | https://link.springer.com/article/10.1023/A:1019048724544 | Medium-high: cluster load prediction in the target journal | Classic load-prediction article structure | not re-counted in this pass | not re-counted in this pass | Useful as evidence that `Cluster Computing` has a long history of publishing workload-prediction papers. |

## What these papers imply for our manuscript

### 1. Introduction is not enough by itself

The target-journal papers do not stop at a generic introduction and one compact experiment section. They usually split the body into problem-motivated stages:

- workload context or motivating example,
- modeling method,
- experimental design,
- result analysis,
- and explicit conclusion or future work.

This means our draft should avoid a thin `Introduction -> Method -> Results` flow with minimal internal structure.

### 2. Related work is expected to be dense

The closest 2025 forecasting paper carries about `70` references, and the 2019 autoscaling paper carries about `37`.
Our draft therefore cannot stay near the low-teens citation range without looking under-researched.
The practical implication is not to chase citation count blindly, but to cover the full conversation:

- trace characterization,
- workload forecasting,
- predictive autoscaling,
- uncertainty-aware control,
- transfer learning or cross-workload generalization,
- and target-journal precedent.

### 3. Figures are part of the argument

The examined papers use figures not as decoration but as evidence:

- workload shape or motivating traces,
- method overviews,
- correlation plots,
- benchmark comparisons,
- sensitivity views,
- and case-study trajectories.

Our previous draft had too few views for this journal style. The manuscript should therefore include multiple complementary figures rather than one overview plot and one control plot only.

### 4. Experimental sections are usually layered

The target papers typically separate:

- dataset description,
- model or system configuration,
- evaluation metrics,
- main benchmark results,
- and additional analysis or sensitivity.

This is important for us because the current manuscript needs to make the smoke-test evidence legible even before the final UA-MSTCN implementation is available.

## Concrete actions applied to the draft

1. Increase the verified bibliography and cite target-journal precedent directly.
2. Split `Related Work`, `Experimental Setup`, and `Results and Discussion` into subsections.
3. Add richer views from the real Alibaba artifact:
   - full-trace workload overview,
   - distribution and daily-profile views,
   - forecast error comparison by horizon,
   - forecast case study,
   - and policy trajectory visualization.
4. Add at least one comparison table that positions the manuscript against closely related published work.
5. Remove or de-emphasize placeholder content that makes the manuscript look incomplete when a real alternative view can be shown instead.

## Acquisition gap

One adjacent `Cluster Computing` article remains difficult to inspect in full from the current anonymous session because Springer redirects the PDF through a cookie gate:

- https://link.springer.com/article/10.1007/s10586-024-04711-0
- https://link.springer.com/content/pdf/10.1007/s10586-024-04711-0.pdf

If you can fetch that PDF manually and place it in the workspace, I can extract its section hierarchy, figure strategy, and citation pattern as an additional benchmark.
