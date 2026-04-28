# Major Revision Plan for Cluster Computing

Manuscript: `Trace-Driven Proactive Autoscaling for Cluster Workloads via Multi-Horizon Forecasting`

Decision: Major revision.

Core revision principle: do not try to defend the paper as a new-model paper. Reframe it as a reproducible public-trace evaluation and boundary-mapping paper, while adding enough method detail and a simple uncertainty-aware baseline to make the current surrogate and control results auditable.

## Current Baseline From The Workbench

- Current mainline: broad audited service-level version.
- Current manuscript sources: `manuscript/main.tex` and `manuscript/sections/*.tex`.
- Current service cohort: 139 audited `app_du` groups, 19,419 selected containers, 19,269 matched containers, 11,520 common minutes.
- Current aggregate forecasting headline: linear regression has the best average MAE on the aggregate series, 3.514.
- Current aggregate UA-MSTCN-Lite coverage: P90 coverage is 0.920, 0.867, and 0.868 at 1, 5, and 10 minutes.
- Current machine-level headline: linear regression remains strongest across the 12-machine cohort and under zero-shot transfer.
- Current broad service-level headline: linear regression is strongest on average, MAE 32.571; predictive control worsens SLA and scaling actions and does not have stable over-provisioning gain under service bootstrap.
- Current biggest risk: Reviewer 2 is correct that the current evidence does not support a strong method-superiority claim.

## Local Resource Census For QLR And Full UA-MSTCN

Resource probe date: 2026-04-27 local time.

Local hardware:

- CPU: AMD Ryzen 7 9700X, 8 physical cores and 16 logical threads.
- RAM: 32 GB physical memory; about 14.8 GB free at probe time.
- GPU: NVIDIA GeForce RTX 4070 Ti SUPER.
- GPU VRAM: 16 GB by `nvidia-smi` (`16376 MiB` total); about 3.2 GB already used by desktop/GUI processes at probe time, leaving roughly 13 GB usable without closing other applications.
- NVIDIA driver/CUDA runtime shown by `nvidia-smi`: driver 591.86, CUDA 13.1 driver capability.
- Disk free space:
  - `C:` 82.0 GB free.
  - `D:` 51.9 GB free; this is the current paper-workbench drive and is the limiting disk.
  - `E:` 168.6 GB free.
  - `F:` 113.9 GB free.
- Current data footprint: `paper-workbench/data` is about 29.6 GB, dominated by `container_usage.tar.gz` at about 27.2 GB. Current generated experiment results are small, about 0.02 GB.

Local Python/deep-learning environment:

- Default `python` is Python 3.13.11 and currently lacks `numpy`, `pandas`, `scikit-learn`, `matplotlib`, and `torch`.
- Bundled Codex runtime Python is 3.12.13 and has `numpy` and `pandas`, but lacks `torch`, `scikit-learn`, `matplotlib`, and `yaml`.
- Conda environment `lora-cheongsam` has Python 3.10.19, `torch 2.5.1+cu121`, CUDA available, and sees the RTX 4070 Ti SUPER with 15.99 GB VRAM; it lacks `pandas`, `scikit-learn`, and `matplotlib`.
- No ready-made environment currently contains both the existing paper dependencies and GPU PyTorch. A new dedicated environment is therefore required before full UA-MSTCN runs.

Local dataset scale:

- Aggregate series: 11,208 rows.
- Machine cohort: 138,240 rows across 12 machines.
- Broad service cohort: 1,601,280 rows across 139 `app_du` services.
- For a 60-minute context, the broad service global model has roughly 1.59 million supervised windows before train/validation/test splitting. This is well within local RAM/GPU capacity if windows are streamed or stored as float32 arrays/memmaps.

Synthetic TCN GPU probe:

- Environment: `lora-cheongsam`, PyTorch 2.5.1+cu121.
- Probe model: small causal multi-scale Conv1D network, 60-step input, 6 outputs.
- Observed throughput:
  - batch 256: about 448 steps/s, 1.07 GB peak allocated VRAM.
  - batch 512: about 531 steps/s, 2.12 GB peak allocated VRAM.
  - batch 1024: about 318 steps/s, 4.22 GB peak allocated VRAM.
  - batch 2048: about 134 steps/s, 8.41 GB peak allocated VRAM.

Local suitability decision:

- The local machine is sufficient for manuscript-facing full UA-MSTCN experiments if the main model is a shared/global multi-entity model, trained with mixed precision, early stopping, controlled seeds, and bounded checkpoint retention.
- The local machine is also sufficient for aggregate, 12-machine, cross-machine transfer, and 139-service broad-cohort experiments at 1 to 3 seeds.
- The local machine is not the best choice for exhaustive hyperparameter search, 139 separate per-service deep models, large ensembling, or many-seed robustness sweeps. Those should use a higher-performance server if needed.
- Because `D:` has only about 52 GB free, deep-learning artifacts should either:
  - be written to `E:\paper-ua-mstcn-runs\`, or
  - keep only best and last checkpoints and delete per-epoch checkpoints automatically.

Dedicated local environment plan:

```powershell
conda create -n paper-tcn python=3.11 -y
conda activate paper-tcn
pip install numpy pandas scikit-learn matplotlib pyyaml tqdm
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

If `cu121` wheels are replaced during implementation, use the newest CUDA wheel compatible with the installed NVIDIA driver, but record the exact package versions in `experiments/02-run-registry.md`.

Structural note:

- This resource census appears before the QLR gate only because it records the machine-wide experiment capacity once. It does not change execution priority.
- Execution priority is fixed by the next section: QLR first, Full UA-MSTCN second.

## Mandatory QLR First-Pass Gate

Quantile linear regression is not optional in this revision. Reviewer 2 explicitly requested a simpler uncertainty-aware baseline, so QLR must be implemented, run, reported, and answered in the response letter before the full UA-MSTCN novelty extension is used as the main scientific upgrade.

Reason for priority:

- QLR directly answers a named reviewer request.
- Full UA-MSTCN is an author-initiated novelty-strengthening action.
- If full UA-MSTCN is added without QLR, Reviewer 2 can still fairly say the paper avoided the simpler uncertainty-aware comparison.
- If QLR is implemented first, the full UA-MSTCN result can be interpreted against both a strong point baseline and a simple uncertainty-aware baseline.

QLR completion gate:

- Add `quantile_linear_regression` to the codebase.
- Run aggregate QLR forecasting and calibration.
- Run QLR-driven aggregate predictive policy.
- Run broad service-level QLR forecasting and QLR-driven predictive policy, because service-level policy is the main practical-benefit concern.
- Add machine-cohort and transfer QLR results if runtime permits, but do not submit without at least aggregate and broad service-level QLR evidence.
- Update manuscript tables and response letter even if QLR weakens the UA-MSTCN narrative.

Only after this gate passes should the revision rely on full UA-MSTCN as the primary novelty repair.

## Novelty Repair Strategy: QLR-First, Then Full UA-MSTCN

Reviewer 2's novelty concern should be treated as a real contribution gap, not only a wording problem. The revised paper should add a full UA-MSTCN implementation and make the existing `UA-MSTCN-Lite` an explicitly named surrogate or ablation.

Revised contribution hierarchy:

1. Quantile linear regression becomes the mandatory reviewer-requested uncertainty-aware baseline.
2. Full UA-MSTCN becomes the primary author-added model contribution for repairing weak novelty.
3. UA-MSTCN-Lite becomes a lightweight surrogate and ablation showing how much is lost by replacing the deep temporal backbone with quantile forests.
4. Linear regression remains the strongest simple point baseline wherever it wins.
5. The evaluation pipeline and service-level boundary analysis remain the paper's systems contribution.

Minimum manuscript-facing claim if full UA-MSTCN succeeds:

- "The full UA-MSTCN improves uncertainty-aware forecasting or control trade-offs relative to its lightweight surrogate and simpler uncertainty-aware baselines on at least one important evaluation surface, while broad service-level results still delimit where predictive control does not transfer unchanged."

Minimum manuscript-facing claim if full UA-MSTCN is mixed:

- "Implementing the full temporal backbone narrows some forecasting or calibration gaps but does not overturn the main boundary result: strong simple baselines and service heterogeneity remain difficult to beat."

Unsupported claim even after full UA-MSTCN:

- Do not claim universal superiority unless the full model beats all baselines across aggregate, machine, transfer, and service policy metrics with stable intervals. That outcome is unlikely and should not be prewritten into the paper.

## Full UA-MSTCN Architecture Design

Purpose:

- Replace the current tree-based `UA-MSTCN-Lite` surrogate with a genuine trainable multi-scale temporal convolutional network that outputs calibrated multi-horizon quantiles.

Input:

- Default history length: 60 one-minute steps.
- Primary signal: entity demand series used by the corresponding benchmark.
- Optional auxiliary channels:
  - imputation mask for machine and service cohorts;
  - time-of-day sine/cosine;
  - entity type flag for aggregate/machine/service if a joint model is used;
  - service descriptor channels only if computed from training data and fixed before test evaluation.
- For the main paper, keep the default input minimal: demand plus imputation mask and time-of-day features. Avoid service descriptors in the first full model unless ablation shows they are necessary, because descriptor leakage and overfitting would be harder to defend.

Backbone:

- Causal Conv1D stem projecting input channels to a hidden width.
- Multi-scale temporal convolution blocks with parallel causal kernels, for example kernel sizes 3, 5, and 7.
- Dilations across blocks: 1, 2, 4, 8, and 16 for a 60-minute receptive field.
- Residual and skip connections in every block.
- Layer normalization or weight normalization after convolution blocks.
- Dropout in the range 0.05 to 0.20, selected on validation only.
- Optional gated activation such as GLU or SiLU-gated residual branch.

Entity conditioning:

- For the broad service and machine cohorts, use a learned entity embedding only in the global model.
- Embedding dimension: 8 or 16.
- Concatenate or FiLM-condition the pooled temporal representation before the output head.
- Hold-out transfer experiments must not use embeddings for unseen entities unless an "unknown entity" embedding protocol is fixed in advance. For zero-shot transfer, train a separate no-entity-embedding variant to avoid leakage.

Output heads:

- Multi-horizon outputs for horizons 1, 5, and 10 minutes.
- Quantiles: P50 and P90 at minimum.
- Optional P10 can be added for interval diagnostics but should not become a core claim unless used in results.
- Enforce non-crossing quantiles by parameterization:
  - output `p50` directly;
  - output positive spread with `softplus`;
  - define `p90 = p50 + softplus(delta90)`.

Loss:

- Weighted pinball loss for P50 and P90 across all horizons.
- Default horizon weights equal across 1, 5, and 10 minutes.
- Add a small monotonicity or spread regularizer only if non-crossing parameterization is insufficient.
- Track validation MAE, P50/P90 pinball, and P90 coverage.
- Early stopping criterion: validation mean pinball across horizons, with MAE as a tie-breaker.

Calibration:

- Primary calibration should be validation-only conformal or residual calibration, not test-set tuning.
- Calibration options:
  - keep raw P90 if validation coverage is acceptable;
  - otherwise add a validation residual margin per horizon to P90, analogous to but cleaner than the current Lite calibration.
- Report both pre-calibration and post-calibration coverage in an appendix-style result if space permits.

Training defaults:

- Optimizer: AdamW.
- Initial learning rate: `1e-3`, with cosine decay or ReduceLROnPlateau.
- Weight decay: `1e-4`.
- Batch size: start with 512; increase to 1024 if VRAM remains below 10 GB and validation behavior is stable.
- Max epochs: 50.
- Early-stopping patience: 8 epochs.
- Gradient clipping: 1.0.
- Mixed precision: enabled on local RTX 4070 Ti SUPER.
- Seeds: 42, 43, 44 for manuscript-facing main runs. Use one seed for smoke/pilot only.

Model-size ladder:

- Small pilot: hidden width 32, 3 dilation blocks, no entity embedding.
- Main local model: hidden width 64, 5 dilation blocks, dropout 0.10, embedding dimension 8 for service/machine global models.
- Larger stress model: hidden width 128, 5 to 6 blocks, embedding dimension 16. Run this only if local calibration shows comfortable runtime or if using the server.

## Full UA-MSTCN Experiment Design

Reviewer concern answered:

- "Novelty claim is weak because the current paper uses only a lightweight surrogate." The experiment introduces the full temporal architecture, compares it against the Lite surrogate and simpler uncertainty-aware baselines, and uses ablations to show which model components matter.

Hypotheses:

- H1: Full UA-MSTCN improves average pinball loss and P90 calibration over UA-MSTCN-Lite on at least the aggregate and broad service-level cohorts.
- H2: Full UA-MSTCN narrows the point-forecast gap to linear regression but may not beat it everywhere.
- H3: Full UA-MSTCN improves at least one policy trade-off surface compared with the Lite predictive controller, but service-level heterogeneity may still prevent stable universal improvement.

Datasets and scales:

1. Aggregate cluster series:
   - one series, 11,208 points.
   - purpose: quick full-model sanity check and direct continuity with Table 4.

2. 12-machine cohort:
   - 12 entities, 138,240 rows.
   - purpose: test entity-level generality and compare with existing machine-cohort result.

3. Cross-machine transfer:
   - 3 deterministic folds, 8 train machines and 4 held-out machines.
   - full UA-MSTCN variant must not rely on held-out entity embeddings.
   - purpose: answer whether the full model transfers better than the Lite surrogate.

4. Broad service cohort:
   - 139 `app_du` services, 1,601,280 rows.
   - purpose: strongest construct-validity surface and main response to Reviewer 2.

Baselines:

- Persistence.
- Linear regression.
- Random forest.
- MLP regressor.
- Quantile linear regression.
- UA-MSTCN-Lite.
- Full UA-MSTCN.

Ablations:

- Full UA-MSTCN without multi-scale parallel kernels.
- Full UA-MSTCN without entity embedding for service/machine global runs.
- Full UA-MSTCN median-only controller, to test whether quantiles drive control.
- Full UA-MSTCN without validation calibration.

Metrics:

- Forecasting:
  - MAE, RMSE, MAPE from P50.
  - P50/P90 pinball loss.
  - P50/P90 empirical coverage.
  - mean interval width.
  - runtime per benchmark call or training/inference time separately.

- Policy:
  - SLA violation.
  - over-provisioning.
  - under-provisioning.
  - scaling actions.
  - mean capacity.
  - predictive-minus-reactive deltas.
  - paired service bootstrap for broad service cohort.

Statistical reporting:

- For full UA-MSTCN, report mean and standard deviation over 3 seeds for main aggregate and broad service results.
- For service policy deltas, keep paired bootstrap over services as the primary stability test.
- If runtime prevents 3 seeds on every surface, prioritize:
  1. broad service forecasting and policy,
  2. aggregate forecasting and policy,
  3. cross-machine transfer,
  4. machine cohort.

Manuscript tables/figures to add or revise:

- Add a compact model-specification table for Full UA-MSTCN versus Lite.
- Update aggregate forecasting table with Full UA-MSTCN and QLR.
- Add a calibration table with QLR, Lite, and Full UA-MSTCN.
- Update service-level forecasting table with Full UA-MSTCN.
- Update service-level policy comparison with Full-UA predictive controller and QLR predictive controller.
- Add one ablation table if space permits; otherwise include in a supplementary/reproducibility table and summarize in text.

## Local-Vs-Server Execution Decision

Local machine should be used for:

- Full model implementation.
- Smoke runs.
- Aggregate full runs.
- Machine cohort full runs.
- Broad service global model at 1 to 3 seeds.
- QLR baseline unless runtime becomes unexpectedly high.
- Figure regeneration and manuscript compilation.

Use the higher-performance server if any of these gates trigger:

- Local full service model with main settings exceeds 6 hours per seed.
- GPU OOM occurs at batch size 256 after mixed precision and reasonable model-size reduction.
- Broad service 3-seed run cannot finish within an overnight window of about 12 hours.
- You decide to train separate per-service deep models for many services.
- You decide to run a hyperparameter grid larger than 6 configurations.
- Disk free space on the selected run drive falls below 30 GB during experiments.

Minimum server specification if needed:

- GPU: 1 NVIDIA GPU with at least 24 GB VRAM, such as RTX 3090, RTX 4090, RTX 6000 Ada, A5000/A6000, L40/L40S, or A10/A10G.
- CPU: 16 physical cores or 32 vCPU.
- RAM: 64 GB.
- Storage: 300 GB free SSD/NVMe.
- Runtime stack: Linux preferred, CUDA-compatible NVIDIA driver, Python 3.10 or 3.11, PyTorch CUDA build, persistent SSH session or job scheduler.

Recommended server specification for stress or per-service models:

- GPU: 1 GPU with 48 GB VRAM or 2 GPUs with at least 24 GB VRAM each.
- CPU: 32 physical cores or 64 vCPU.
- RAM: 128 GB.
- Storage: 500 GB to 1 TB NVMe.
- This tier is recommended if running 139 per-service models, 5+ seeds, or large hyperparameter search.

Server artifact requirements:

- Use the same git commit as local.
- Copy only required processed datasets unless raw preprocessing is being tested.
- Write all outputs under a run id, for example `ua_full_2026_04_r1`.
- Synchronize back only tables, logs, configs, checkpoints for best seeds, and figure-ready outputs.

## QLR Execution Ladder

QLR must be completed before Full UA-MSTCN is allowed to carry the novelty response.

Stage Q0: implementation.

- Add `quantile_linear_regression` to `experiments/models/baselines.py`.
- Use the same leakage-free supervised windows as ordinary linear regression.
- Train separate quantile models for P50 and P90 at each horizon.
- Preferred implementation: `sklearn.linear_model.QuantileRegressor` with a fixed `alpha` selected on validation only.
- If exact QLR is slow on the broad service cohort, use a documented fallback based on `SGDRegressor(loss="quantile")` or a pre-fixed feature-reduced QLR. The fallback must still be a linear quantile model and must be reported clearly.

Stage Q1: aggregate smoke.

- Dataset: aggregate cluster series.
- Horizons: 1, 5, 10 minutes.
- Outputs: P50 MAE/RMSE/MAPE, P50/P90 pinball loss, P50/P90 coverage, interval width.
- Gate: metrics are generated and no test data is used for fitting or calibration.

Stage Q2: aggregate policy.

- Feed QLR P50/P90 into the same predictive controller used by UA-MSTCN-Lite.
- Use the same headroom, cooldown, scale-out margin, scale-in guard, and capacity mapping.
- Gate: QLR predictive policy appears beside reactive, lagged, Lite predictive, and later Full-UA predictive policies.

Stage Q3: broad service-level QLR.

- Dataset: audited 139-service broad cohort.
- Train either:
  - one pooled global QLR with entity-agnostic lag features, or
  - per-service QLR models if runtime is acceptable.
- Preferred first mainline: pooled/global QLR, because it is simpler, more reproducible, and directly comparable to the shared predictive-policy concern.
- Outputs: service-level forecasting table, QLR P90 coverage, QLR-driven service policy table, paired bootstrap deltas.
- Gate: broad service-level QLR result is included in the manuscript even if it performs poorly.

Stage Q4: machine and transfer add-on.

- Add QLR to the 12-machine cohort.
- Add pooled QLR to cross-machine transfer if runtime permits.
- Gate: these add-ons strengthen the response but are not allowed to delay aggregate and broad service-level QLR reporting.

Stage Q5: claim decision.

- If QLR matches or beats UA-MSTCN-Lite, the manuscript must say that a simple uncertainty-aware linear model is competitive and that deep novelty must be judged against this baseline.
- If QLR is worse, the manuscript can say the requested simple uncertainty-aware baseline was tested and does not remove the need for richer temporal uncertainty modeling.
- In both cases, QLR remains in the paper and response letter.

## Full UA-MSTCN Scale Ladder

Start this ladder only after QLR Stage Q1 and Q3 have passed. Full UA-MSTCN strengthens novelty, but it does not substitute for the QLR response.

Stage 0: environment setup.

- Create `paper-tcn` environment.
- Verify `torch.cuda.is_available()`.
- Add `requirements-tcn.txt` or `environment-paper-tcn.yml`.
- Record versions in run registry.

Stage 1: smoke.

- Dataset: aggregate series, first 2,000 points.
- Model: hidden width 32, 3 blocks, one seed.
- Epochs: 3.
- Gate: loss decreases, outputs have shape `[batch, horizons, quantiles]`, no quantile crossing, metrics CSV created.

Stage 2: pilot.

- Dataset: aggregate full + 5 representative services.
- Model: hidden width 64, 5 blocks.
- Epochs: up to 15 with early stopping.
- Gate: runtime/epoch, peak VRAM, RAM, and disk written to status JSON; no data leakage; validation calibration works.

Stage 3: calibration.

- Dataset: broad service cohort.
- Run 1 seed with batch sizes 512 and 1024.
- Choose batch size by measured throughput and VRAM, not by guess.
- Gate: peak VRAM below 12 GB on local machine and no CPU data-loading bottleneck severe enough to cut GPU utilization below about 40% for the main run.

Stage 4: main manuscript run.

- Aggregate, machine cohort, cross-machine transfer, and broad service global model.
- Seeds: 42, 43, 44 where feasible.
- Outputs:
  - `experiments/results/full_ua_mstcn/...`
  - metrics tables;
  - calibration tables;
  - policy comparisons;
  - run logs;
  - best checkpoints only.

Stage 5: ablation.

- Run no-multiscale, no-embedding, median-only, and no-calibration variants.
- Use one seed for ablations unless a variant is close enough to affect main claims.

Stage 6: stress/server optional.

- Larger model or additional seeds.
- Per-service fine-tuning only if the global full model still fails badly and novelty remains weak.
- Treat this as robustness evidence, not a blocker for resubmission if main full model is already sufficient.

## Revision Deliverables

1. Revised manuscript PDF and LaTeX source.
2. Point-by-point response letter in `revisions/response-letter.md`.
3. Public or review-accessible reproducibility package with a real repository URL, not a placeholder.
4. Mandatory QLR baseline implementation, forecasting results, calibration results, QLR-driven policy results, and regenerated tables/figures.
5. Full UA-MSTCN implementation, logs, metrics, calibration outputs, and policy results after the QLR gate passes.
6. Visual QA note showing that enlarged figures remain readable after compilation.
7. Updated `review/reviewer_feedback.md` or equivalent revision log recording what changed and where.

## Priority Order

1. Fix direct editorial and Reviewer 1 formatting requests first. These are low-risk and remove avoidable irritants.
2. Implement QLR immediately, because it is the explicit Reviewer 2 request and a hard response-letter gate.
3. Run aggregate and broad service-level QLR forecasting, calibration, and QLR-driven policy comparisons.
4. Implement the full UA-MSTCN environment and smoke run after QLR is working.
5. Run calibrated full-model experiments and regenerate affected results.
6. Reframe method novelty and claims after the QLR and full-model numbers are known.
7. Expand related work and add preamble paragraphs requested by Reviewer 3.
8. Enlarge and visually recheck figures.
9. Update reproducibility statements and repository package.
10. Compile, compare numbers, and write response letter.

## Editor-Level Plan

The editor asks for accurate results, less overstated conclusions, and fuller limitations. Apply a manuscript-wide claim calibration pass:

- Abstract: keep the explicit negative service-level result. Avoid language implying that predictive control is generally better.
- Introduction: state that the contribution is an evaluation pipeline and boundary map, not a validated production controller.
- Method: call UA-MSTCN-Lite a paper-specific lightweight surrogate, not the final UA-MSTCN architecture.
- Results: report when linear regression wins. Do not bury the result behind uncertainty benefits.
- Discussion and Conclusion: explicitly say the broad service-level cohort does not validate the shared global predictive policy as a service-level improvement route.
- Threats: keep three limitations visible: public trace rather than live cluster, service cohort is not a full census, surrogate is not the final deep architecture.

Acceptance criterion: a reviewer can read only the abstract, contribution paragraph, and conclusion and still understand that the paper is honest about mixed or negative control outcomes.

## Reviewer 1 Plan

### R1.1 Abstract horizon mapping

Current location: `manuscript/sections/abstract.tex`, sentence beginning "Leakage-free forecasting shows...".

Action:

- Replace the current sentence with the reviewer-requested wording, preserving the current service-level 139-service sentence after it:

```tex
Leakage-free forecasting shows that linear regression is the strongest average point baseline on the aggregate series (MAE 3.514), while \texttt{UA-MSTCN-Lite} still supplies usable $P90$ coverage of 0.920, 0.867, and 0.868 for the 1-, 5-, and 10-minute horizons, respectively.
```

Response letter:

- State that the abstract now maps each coverage value to its horizon.

### R1.2 Public artifact link in Introduction

Current location: `manuscript/sections/introduction.tex`, after the contribution/evidence paragraph.

Action:

- Do not submit `https://github.com/[repository-placeholder]`.
- Make the repository public or create a stable review release first.
- Candidate existing remote: `https://github.com/Jinchun-Liu/paper-workbench`.
- Insert the required sentence with the real repository URL:

```tex
All preprocessing scripts, model training code, and the predictive-control simulator are publicly released at \url{https://github.com/Jinchun-Liu/paper-workbench} to guarantee exact reproduction of every reported number.
```

- If the repository cannot be public before resubmission, the paper cannot honestly claim this. In that case, the revision should instead say "available to reviewers in a frozen repository" and explain the conflict in the response letter, but this is riskier because Reviewer 1 calls the public link mandatory.

Repository/package actions:

- Remove raw Alibaba archives from the public repository.
- Include scripts, manifests, result tables, figures, checksums, and a README explaining how to regenerate from Alibaba raw traces.
- Create a tagged release, for example `cluster-computing-major-revision-2026-04`.
- Prefer adding a Zenodo DOI after the GitHub release if time permits.

### R1.3 Related Work Table 1 line-break artifact

Current location: `manuscript/sections/related_work.tex`, Table `tab:related-positioning`.

Action:

- Current source already has the unbroken sentence:

```tex
Couples forecasting, transfer, and trace-driven control under one reproducible public-trace pipeline.
```

- Still verify in compiled PDF that it does not hyphenate awkwardly. If the two-column table forces a visual line break, widen the final column or slightly reduce table font rather than changing the sentence.

### R1.4 Required-capacity mapping equation

Current location: `manuscript/sections/method.tex`, required-capacity mapping paragraph.

Action:

- Rewrite the service-level equation so the definition of `r_e` appears immediately after the displayed equation:

```tex
\[
c^\star_{e,t} = \max\left( \frac{(1+\rho)x_{e,t}}{r_e}, c_{\min} \right).
\]
where \(r_e\) is the median per-container requested CPU cores for service \(e\).
```

- Keep `c^\star_{e,t}` rather than malformed `c^_{e,t}` unless the journal proof specifically asks for another symbol. The response letter can say the displayed equation and definition were corrected.

### R1.5 Predictive policy scale-in formula

Current location: `manuscript/sections/method.tex`, predictive policy block.

Action:

- Replace the scale-in line with a syntactically complete line:

```tex
c_{e,t+1} = \max(c_{e,t}-\Delta, (1+\gamma)\hat{c}^{(0.5)}_{e,t+h}), \quad \text{if scale-in},
```

- If retaining the aligned three-line block, keep this exact expression in the scale-in row and avoid splitting the conditional clause.

### R1.6 Section 4.3 service-route sentence placement

Current location: `manuscript/sections/experiments.tex`, container service cohort paragraph.

Action:

- Move this sentence to the immediate beginning of the paragraph beginning "The service route now follows a simpler fixed rule."
- Append `(see Table~\ref{tab:service-cohort-stats})`.
- Recommended revised paragraph opening:

```tex
This is therefore a much broader official-data extension, although it still should not be read as a full population census because the metadata prefilter intentionally excludes smaller and shorter-lived services (see Table~\ref{tab:service-cohort-stats}). The service route now follows a simpler fixed rule.
```

### R1.7 Table 2 caption

Current location: `manuscript/sections/experiments.tex`, service cohort table.

Action:

- Caption already exists in the current source. Verify compiled PDF shows it as Table 2 and uses:

```tex
Summary statistics of the broad Alibaba service-level cohort extracted from the official container tables.
```

- If the compiled numbering no longer maps this table to Table 2 after revisions, reference it by label in the response letter rather than by number.

### R1.8 Figure 1 caption subplot assignments

Current location: `manuscript/sections/experiments.tex`, `fig:workload-overview`.

Action:

- Replace caption with:

```tex
Aggregate workload overview across the processed Alibaba \texttt{v2018} series, including (top-left) CPU utilization, (top-right) memory utilization, (bottom-left) active-machine counts, and (bottom-right) first-day zoom.
```

### R1.9 Table 4 title and smoke-test terminology

Current location: `manuscript/sections/results.tex`, Table `tab:forecast-smoke-test`.

Action:

- Change caption to:

```tex
Leakage-free forecasting performance on the aggregate cluster series (MAE, RMSE, MAPE).
```

- Search manuscript only for "smoke-test" and "smoke test"; replace with "leakage-free" where referring to final reported results.
- Consider renaming the table label to `tab:forecast-leakage-free` and update references.
- Do not rename internal file `experiments/results/smoke-test-summary.md` unless doing a broader artifact cleanup; reviewer only asked manuscript terminology.

### R1.10 Figure 5 caption model names

Current location: `manuscript/sections/results.tex`, `fig:forecast-case-study`.

Action:

- Append the requested model list:

```tex
with persistence, linear regression, random forest, MLP regressor, and \texttt{UA-MSTCN-Lite} predictions overlaid on aligned test-set slices.
```

- If quantile linear regression is added to the plotted figure, either update the caption to include it or keep the figure unchanged and report QLR in a separate table/figure.

### R1.11 Context-window repeated fragment

Current location: `manuscript/sections/results.tex`, context sensitivity paragraph.

Action:

- Current source already contains the corrected single occurrence:

```tex
A 60-minute window gives the best average MAE (3.548), compared with 3.615 for 30 minutes and 3.585 for 120 minutes.
```

- Still run a search over manuscript source and compiled PDF text to confirm there are no repeated fragments.

### R1.12 Figure 7 dashed-line caption

Current location: `manuscript/sections/results.tex`, `fig:quantile-coverage`.

Action:

- Replace the final caption sentence with:

```tex
Dashed line indicates the nominal target level of 0.5 (P50) and 0.9 (P90).
```

- If both dashed lines are visible, use plural grammar:

```tex
Dashed lines indicate the nominal target levels of 0.5 (P50) and 0.9 (P90).
```

Response letter should mention the exact target levels are now named.

## Reviewer 2 Plan

Reviewer 2 is the main scientific risk. The response must not be cosmetic.

### R2.1 UA-MSTCN-Lite is under-specified

Current locations:

- `manuscript/sections/method.tex`, forecasting backbone paragraph.
- `experiments/models/ua_mstcn.py`.
- `experiments/sections/experiments.tex`, forecasting and policy configuration.

Actions:

1. Rename the method framing in prose:
   - Use "paper-specific lightweight uncertainty-aware surrogate" or "UA-MSTCN-Lite surrogate".
   - Avoid "proposed UA-MSTCN architecture" unless referring to future work.
   - State explicitly: "UA-MSTCN-Lite is not the full deep UA-MSTCN architecture."

2. Add a compact architecture/training paragraph or table in Section 3:
   - Input: 60-minute history window.
   - Horizons: 1, 5, 10 minutes.
   - Feature set:
     - lag values at 1, 2, 3, 5, 10, 15, 20, 30, 45, and 60 minutes;
     - multiscale windows 3, 5, 10, 20, 30, 60 minutes;
     - per-window mean, standard deviation, minimum, maximum, median, 0.1 quantile, 0.9 quantile, endpoint difference, last-minus-mean, and slope;
     - additional short/long moving-average and volatility differences.
   - Learner: one `RandomForestRegressor` per horizon.
   - Hyperparameters from code: 200 estimators, `min_samples_leaf=3`, `max_features="sqrt"`, random seed `42 + horizon`, `n_jobs=-1`.
   - Quantiles: per-tree prediction distribution yields P50 and P90.
   - Calibration: P90 is widened by the 0.99 quantile of positive training residuals relative to P50.
   - Clipping: P50 and P90 are clipped to training target support, with P90 allowed up to 1.10 times the training maximum before the calibration floor.
   - Multi-entity training: `fit_multi_series` pools windows from training entities for transfer experiments.

3. Add a "why not full UA-MSTCN" sentence:
   - The current revision prioritizes a fully reproducible trace-driven evaluation with a lightweight dependency stack.
   - A deeper temporal convolutional backbone is future work and is not claimed as implemented.

4. Add a reproducibility cross-reference:
   - Cite the implementation file path or public repository location in prose or declarations.

Response letter:

- Say the method is now explicitly identified as paper-specific and the concrete feature extractor, learner, quantile construction, calibration, and training split are described.

### R2.2 Results do not support main method claim

Action: accept the criticism and revise the paper's claim hierarchy.

Claim hierarchy after revision:

1. Strongest supported claim:
   - Public traces can support a reproducible forecasting-to-control evaluation across aggregate, machine, transfer, and service levels.
2. Secondary supported claim:
   - Simple linear models are very strong point baselines and often beat the current surrogate.
3. Conditional supported claim:
   - UA-MSTCN-Lite supplies usable quantile coverage that can be consumed by a controller.
4. Negative/boundary claim:
   - The current shared predictive policy is not validated as a stable service-level improvement route.
5. Unsupported claim to remove:
   - The current surrogate is a superior forecasting model or a validated new architecture.

Concrete manuscript edits:

- Abstract: keep "not a blanket superiority claim".
- Introduction contribution 4: explicitly say "not validated as a service-level improvement route".
- Results Section 5.1: keep linear regression wins in the first sentence after Table 4.
- Results service-level section: avoid saying the quantile model "helps" service policy unless the QLR comparison supports it.
- Conclusion: close with "boundary mapping" and "future service-aware tuning", not "predictive autoscaling improves cluster workloads".

### R2.3 Add simpler uncertainty-aware baseline

Mandatory experiment: add a simpler uncertainty-aware linear baseline. This is not optional and must be completed before relying on Full UA-MSTCN as the novelty repair, because Reviewer 2 explicitly named this comparison.

Recommended baseline name:

- `quantile_linear_regression`

Implementation target:

- Add to `experiments/models/baselines.py`.
- Use lag-history features matching the linear regression baseline for fairness.
- Train one model per horizon and quantile.
- Quantiles: P50 and P90.
- Candidate implementation:
  - `sklearn.linear_model.QuantileRegressor(quantile=0.5, alpha=1e-4, solver="highs")`
  - `sklearn.linear_model.QuantileRegressor(quantile=0.9, alpha=1e-4, solver="highs")`
  - Standardize features if solver stability requires it.
- If exact quantile regression is too slow for the full 139-service route, use a staged fallback:
  - first run aggregate and 12-machine routes exactly;
  - then run broad service route with a fixed feature-reduced linear quantile baseline using lags plus summary features capped in advance;
  - document the resource guard in experiments, not as an after-the-fact excuse.

Required result surfaces to regenerate:

1. Aggregate forecasting:
   - MAE/RMSE/MAPE from P50.
   - P50/P90 coverage.
   - Pinball loss for P50 and P90.
2. Aggregate policy:
   - Add `Predictive QLR` beside `Predictive UA-MSTCN-Lite`.
   - Same headroom, cooldown, and step constraints.
3. Broad service cohort:
   - Add QLR forecasting summary and service-level policy comparison.
   - Report whether QLR changes the current conclusion that service-level predictive control worsens SLA/actions.
   - Run the paired service bootstrap for QLR predictive-minus-reactive deltas.
4. Machine cohort:
   - Add QLR point MAE and coverage, at least in a compact table or appendix-style paragraph.
5. Cross-machine transfer:
   - Add pooled/global QLR if computationally feasible.
   - If not feasible, clearly state that QLR was added to aggregate and service control, while transfer remains point-baseline focused.

Promotion rule:

- If QLR outperforms UA-MSTCN-Lite on control, the revised paper must say so directly and demote UA-MSTCN-Lite to one uncertainty-aware baseline.
- If QLR is similar or worse, the revised paper can say the simpler uncertainty-aware linear baseline was tested and did not remove the service-level control boundary.
- In both cases, the contribution remains the evaluation pipeline, not model superiority.

Expected manuscript changes:

- Add QLR to Section 4.4 model list.
- Add QLR row(s) to Table 4 or a new compact calibration table.
- Add QLR to service-level forecasting and control tables.
- Update Figure 5 only if it remains legible. Otherwise, keep Figure 5 unchanged and add QLR to tables.
- Add one paragraph in Results explaining whether uncertainty itself or model complexity is driving control behavior.

### R2.4 Practical benefit is unconvincing

Action:

- Do not try to turn the service-level result into a positive performance story.
- Add one "policy implication" paragraph:
  - Aggregate trace: predictive policy can reduce over-provisioning if SLA penalty is acceptable.
  - Broad service cohort: the same shared policy worsens SLA and actions, so service-aware tuning or regime-aware control is required before operational use.
  - The value is diagnostic: the pipeline identifies where predictive control fails.

Possible wording:

```tex
The broad service-level result changes the practical interpretation. It does not validate the current shared predictive policy as a service-level replacement for reactive control. Instead, it shows that a controller that looks reasonable on the aggregate series can systematically trade lower over-provisioning for worse SLA and more scaling actions once service heterogeneity is exposed.
```

### R2.5 Novelty claim is weak

Action:

- Modify title only if necessary. Current title can remain because it does not claim a new architecture.
- In the introduction, replace any model-novelty emphasis with:
  - public trace evaluation;
  - leakage-free protocol;
  - multi-granularity evidence;
  - cross-machine transfer;
  - broad service-level audit;
  - honest mixed/negative policy results.
- In response letter, say the manuscript has been reframed accordingly.

## Reviewer 3 Plan

### R3.1 Add preamble after Section 2 heading

Current location: `manuscript/sections/related_work.tex` starts directly with `\subsection{Representative precedent studies}`.

Action:

- Insert a short preamble paragraph before the first subsection:

```tex
This section organizes prior work around the three layers needed for a trace-driven predictive-autoscaling study: workload characterization, forecasting, and control. The goal is not to claim that forecasting or autoscaling are new topics, but to identify where existing studies leave a reproducible public-trace gap between prediction quality and capacity-control behavior.
```

- Then keep the representative-table paragraph.

### R3.2 Add preamble after Section 4 heading

Current location: `manuscript/sections/experiments.tex` starts directly with `\subsection{Dataset and preprocessing}`.

Action:

- Insert a paragraph before `\subsection{Dataset and preprocessing}`:

```tex
This section describes the trace-processing and evaluation protocol used for all reported results. The protocol is organized from broader but more abstract signals to narrower but more service-relevant signals: aggregate cluster usage, high-coverage machine entities, cross-machine transfer, and the audited service-level cohort.
```

- Mention leakage-free chronological splits in this preamble or the first dataset paragraph.

### R3.3 Extend recent related work and add Gul 2022

Current locations:

- `manuscript/sections/related_work.tex`
- `manuscript/refs.bib`

Required addition:

- Add Gul OM, "Heuristic Resource Reservation Policies for Public Clouds in the IoT Era", Sensors, 2022, 22(23), 9034, DOI `10.3390/s22239034`.

Placement:

- Add Gul 2022 in the predictive autoscaling/resource reservation paragraph, not as a token citation in a generic list.
- Use it to strengthen the resource-reservation/control-policy context:

```tex
Resource-reservation studies also show that lightweight heuristic policies remain operationally relevant in public-cloud settings, especially when IoT-era demand variability makes over-reservation and SLA risk difficult to balance \citep{Gul2022HeuristicResourceReservation}.
```

Recent-work handling:

- Current refs already include several recent works: Rossi 2025, Zanussi 2026, Puebla 2024, Zargar Azad 2023, and Canizares 2023.
- Make those works more visible in Related Work, especially in the first preamble/table and predictive-autoscaling paragraph.
- Add at most 2 to 4 additional recent papers only if they directly match uncertainty-aware autoscaling, Kubernetes/microservice autoscaling, or public-trace evaluation. Do not inflate the bibliography with weakly related papers.

Response letter:

- State that the Related Work section now has a preamble, incorporates Gul 2022, and more clearly positions recent 2023-2026 work.

### R3.4 Enlarge Figures 1, 2, 3, 5, and 6

Current likely mapping after source order:

- Figure 1: `fig:workload-overview`, `cluster_workload_overview.png`
- Figure 2: `fig:distribution-views`, `resource_distribution_views.png`
- Figure 3: `fig:service-workload-overview`, `service_workload_overview.png`
- Figure 5: likely `fig:forecast-case-study`, `forecast_case_study.png`
- Figure 6: likely `fig:latency-tradeoff`, `forecast_latency_tradeoff.png`

Action:

- Confirm final numbering from compiled PDF after all table/figure changes.
- For the five reviewer-mentioned figures, enlarge at both source-render and LaTeX levels:
  - regenerate PNGs with larger `figsize`, larger font sizes, and `dpi >= 300`;
  - use `width=\linewidth` for single-column figures;
  - where multi-panel figures remain cramped, use `figure*` and `width=\textwidth`;
  - avoid simply stretching low-resolution images.
- Specific candidates:
  - `fig:service-workload-overview` currently uses `0.78\linewidth`; change to `\linewidth` or `figure*`.
  - `fig:latency-tradeoff` currently uses `0.82\linewidth`; change to `\linewidth`.
  - If Figure 1 and Figure 5 remain hard to read in two-column layout, promote them to `figure*`.
- After compiling, visually inspect PDF pages, not only source dimensions.

Response letter:

- Say the requested figures were enlarged and re-rendered, and captions were updated where requested by Reviewer 1.

## Reproducibility And Public Release Plan

Current status:

- Reviewer 1 explicitly asks for a public repository link.
- The manuscript, declarations, response letter, cover letter, and upload notes now use `https://github.com/Jinchun-Liu/paper-workbench` as the public reproducibility route.
- Anonymous web/API/git access to the repository was verified on 2026-04-28.

Completed actions:

1. Made the GitHub repository public with:
   - `manuscript/`;
   - `experiments/`;
   - `scripts/`;
   - `submission/reproducibility-package-manifest.yaml`;
   - result tables and figure-generation artifacts;
   - README with exact commands;
   - checksum manifest.
2. Do not include third-party raw Alibaba trace archives if redistribution is restricted or impractical.
3. Include download instructions and expected checksums or row counts for regenerated raw-derived artifacts.
4. Update `declarations.tex`:
   - Data availability: public Alibaba raw traces plus public processed/reproducibility artifacts.
   - Code availability: public GitHub URL and release tag.
5. Update `submission/reproducibility-package.md` to remove "confidential" as the primary route now that the repository is public.

Acceptance criterion:

- A reviewer can click the URL, see scripts and result artifacts, and trace how every table/figure number was produced. Current gate status: pass for anonymous public repository visibility.

## Concrete File-Level Edit Checklist

### Manuscript files

- `manuscript/sections/abstract.tex`
  - Add horizon mapping in aggregate P90 sentence.
  - Recheck abstract word count after edits.

- `manuscript/sections/introduction.tex`
  - Add public artifact sentence.
  - Calibrate contribution wording toward evaluation and boundary mapping.

- `manuscript/sections/related_work.tex`
  - Add Section 2 preamble.
  - Add Gul 2022 and strengthen recent-work discussion.
  - Verify Table 1 row text and formatting.

- `manuscript/sections/method.tex`
  - Fix service required-capacity equation and `r_e` definition placement.
  - Fix predictive scale-in formula.
  - Add concrete UA-MSTCN-Lite architecture/training description.
  - Add quantile linear regression baseline definition once implemented.

- `manuscript/sections/experiments.tex`
  - Add Section 4 preamble.
  - Move service cohort limitation sentence to paragraph beginning and append Table 2 reference.
  - Update model list and protocol for QLR.
  - Enlarge or promote requested figures.
  - Update Figure 1 caption.

- `manuscript/sections/results.tex`
  - Replace smoke-test terminology.
  - Add QLR results.
  - Update Figure 5 caption.
  - Update Figure 7 caption.
  - Add policy implication paragraph.
  - Recheck context-window duplicate fragment.

- `manuscript/sections/threats.tex`
  - Add limitation that QLR and UA-MSTCN-Lite are both trace-level baselines, not production validation.
  - Keep service cohort non-census limitation.

- `manuscript/sections/conclusion.tex`
  - Reframe final paragraph around reproducible evaluation, strong simple baselines, and service-level boundary mapping.

- `manuscript/refs.bib`
  - Add Gul 2022 BibTeX.
  - Add any selected recent works.
  - Remove unused entries after final compile if safe.

- `manuscript/main.tex`
  - Ensure `\url` support remains loaded.
  - Keep declarations after bibliography unless journal build requires otherwise.

### Experiment/code files

- `experiments/models/baselines.py`
  - Add QLR model class/function returning P50 and P90.

- `experiments/run_baselines.py`
  - Emit QLR MAE/RMSE/MAPE, coverage, and pinball metrics.

- `experiments/run_machine_cohort_experiments.py`
  - Add QLR if runtime permits.

- `experiments/run_machine_transfer_experiments.py`
  - Add pooled QLR or document scope if too slow.

- `experiments/run_broad_service_cohort_pipeline.py` or service runner
  - Add QLR forecasting and QLR-driven predictive policy.

- `experiments/render_manuscript_figures.py`
  - Enlarge figure dimensions and font sizes for Figures 1, 2, 3, 5, 6.
  - Avoid manual edits to generated PNGs.

### Revision and submission files

- `revisions/response-letter.md`
  - New point-by-point response.

- `submission/reproducibility-package.md`
  - Public release wording.

- `submission/checklist.md`
  - Add major revision completion checklist.

- `review/reviewer_feedback.md`
  - Append a new round documenting this external major-revision decision and the planned actions.

## Experiment Execution Ladder

Run new uncertainty-aware linear baseline in stages:

1. Smoke run:
   - aggregate series only;
   - horizons 1, 5, 10;
   - validate QLR output shape and coverage.

2. Aggregate full run:
   - regenerate `metrics.csv`;
   - regenerate aggregate tables and figures;
   - run aggregate policy with UA and QLR.

3. Machine pilot:
   - 2 machines, all horizons;
   - estimate runtime.

4. Machine full:
   - 12-machine cohort;
   - add summary table.

5. Service pilot:
   - 5 services spanning low/high load and burstiness;
   - confirm runtime and memory.

6. Broad service full:
   - 139 services;
   - QLR forecasting plus QLR-driven policy;
   - paired bootstrap if policy comparison is added.

7. Render and compile:
   - regenerate figures;
   - compile manuscript;
   - inspect PDF.

Recommended commands after implementation:

```bash
python experiments/run_baselines.py --config experiments/configs/default_v2018.yaml
python experiments/run_extended_experiments.py --config experiments/configs/default_v2018.yaml
python experiments/run_machine_cohort_experiments.py
python experiments/run_machine_transfer_experiments.py
python experiments/run_broad_service_cohort_pipeline.py
python experiments/render_manuscript_figures.py
cd manuscript
latexmk -pdf -interaction=nonstopmode main.tex
```

Adjust commands to the repository's existing path convention if scripts expect `paper-workbench/...` from the parent directory.

## Response Letter Structure

Open with:

- Thank the editor and reviewers.
- State that the manuscript was substantially revised.
- List the three major scientific changes:
  1. explicit reframing as evaluation and boundary mapping;
  2. addition of the reviewer-requested quantile linear regression baseline and updated control interpretation;
  3. implementation of the full UA-MSTCN model as a novelty-strengthening extension, with UA-MSTCN-Lite demoted to surrogate/ablation status.

Then answer by reviewer:

- Reviewer 1: mostly direct wording, formula, caption, and terminology fixes.
- Reviewer 2: scientific response, not defensive:
  - agree that UA-MSTCN-Lite needed specification;
  - agree that results do not support model-superiority claims;
  - explain the QLR baseline first, because it was explicitly requested;
  - then explain what the full UA-MSTCN adds beyond QLR and UA-MSTCN-Lite;
  - explain revised novelty framing.
- Reviewer 3:
  - preambles inserted;
  - Gul 2022 and recent works added;
  - figures enlarged and visually checked.

For each item include:

- Reviewer comment summary.
- Action taken.
- Location in revised manuscript.
- If no direct action, explain why with evidence.

## Final Quality Gates Before Resubmission

0. Portal upload compliance:
   - original submitting author account confirmed before upload;
   - submission ID recorded for upload and extension requests;
   - point-by-point response exported as a PDF;
   - response PDF describes all additional experiments carried out;
   - response PDF includes detailed rebuttal for any reviewer criticism or requested revision not adopted;
   - all changed files are identified and uploaded again;
   - clean revised manuscript contains no tracked changes or visible markup;
   - any highlighted or marked-up manuscript is uploaded only as a related file.

1. Manuscript source search:
   - no "smoke-test" in manuscript;
   - no "universally superior";
   - no "full UA-MSTCN" claim for current implementation;
   - public repo URL appears in Introduction and Code Availability.

2. Number consistency:
   - abstract numbers match result tables;
   - Table 4 caption matches reviewer wording;
   - QLR numbers are included wherever discussed;
   - service-level 139-service numbers match CSV artifacts.

3. Figure QA:
   - Figures 1, 2, 3, 5, 6 are visibly larger;
   - Figure 1 caption maps subplots;
   - Figure 5 names all plotted models;
   - Figure 7 names dashed target levels.

4. Formula QA:
   - service required-capacity equation renders correctly;
   - scale-in equation is syntactically complete;
   - notation `c^\star`, `r_e`, `\Delta`, `\gamma`, P50, and P90 are defined.

5. Claim QA:
   - abstract, introduction, results, threats, and conclusion tell the same story.
   - service-level policy degradation is not hidden.
   - QLR result is reported even if it weakens the UA-MSTCN-Lite narrative.

6. Reproducibility QA:
   - repository URL works;
   - release tag exists;
   - README has commands;
   - raw Alibaba data redistribution boundary is clear;
   - checksums or manifest are present.

7. Compile QA:
   - `latexmk` completes;
   - no missing references or citations;
   - major overfull boxes in revised figures/tables are fixed or documented.

## Suggested Schedule

Day 1:

- Make public artifact decision.
- Implement direct R1 edits.
- Implement QLR baseline and run aggregate QLR smoke.
- Add R3 preambles and Gul 2022 if time remains.

Day 2:

- Run aggregate QLR policy and broad service-level QLR forecasting/policy pilot.
- Freeze QLR protocol and update the response-letter outline for Reviewer 2.
- Start Full UA-MSTCN environment setup only after QLR aggregate and service pilots are producing valid artifacts.

Day 3:

- Run full broad service-level QLR and paired bootstrap.
- Implement Full UA-MSTCN smoke/pilot.
- Regenerate QLR result tables and identify which claims must change.

Day 4:

- Run Full UA-MSTCN main experiments if QLR gate has passed.
- Regenerate figures, including enlarged requested figures.
- Update manuscript results and claims.

Day 5:

- Compile PDF.
- Visual QA for enlarged figures.
- Update declarations, reproducibility package, and repository release.
- Write response letter.
- Final consistency pass.
- Prepare resubmission package.

## Strategic Position To Defend

The revised paper should defend this position:

> This paper is not claiming that UA-MSTCN-Lite is a new state-of-the-art autoscaling model. It provides a reproducible public-trace evaluation that links forecasting, uncertainty, transfer, and trace-driven control across aggregate, machine, and service levels. The strongest empirical message is that simple linear baselines remain very strong and that predictive control has clear service-level boundaries under heterogeneity. That negative/mixed result is the contribution, because it makes future service-aware predictive autoscaling work more honest and measurable.

After this update, the strategic position becomes:

> The revision first answers the reviewer-requested QLR comparison, then uses Full UA-MSTCN to strengthen novelty. If Full UA-MSTCN outperforms QLR and Lite, the paper can claim a real temporal uncertainty-modeling contribution. If it does not, the paper still has a defensible contribution because it will have shown, under a reproducible public-trace protocol, that even stronger temporal models must be judged against simple uncertainty-aware linear baselines and broad service-level policy boundaries.
