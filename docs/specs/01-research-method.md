# Common research and evidence method

**Applicability:** every proposed project. Project-specific protocols refine these rules. They do not convert draft hypotheses or numerical targets into approved commitments.

## 1. Evidence vocabulary

| Label | Meaning | Permitted claim |
|---|---|---|
| Source intent | A statement on the supplied Notion page | The user proposed this research topic |
| External evidence | Retrieved primary publication, official dataset, specification, or documentation | The cited source supports the specific adjacent method/fact |
| Assumption | A chosen scenario, constraint, interpretation, target, or budget | The study is conditional on this choice |
| Proposed design | A recommended interface, experiment, or workflow | This is how the project could be implemented |
| Pilot result | An exploratory measurement after implementation | It may guide design; it is not held-out confirmation |
| Confirmatory result | A measurement under a frozen protocol and held-out analysis | It supports only the scope and uncertainty actually tested |

This package contains the first four categories. Its synthetic contract examples are not research results.

## 2. Start with a precise question

For each project, declare the population/scenario distribution, intervention or design variable, comparator, outcome, and constraints. Replace “best” with a Pareto trade-space or a constrained optimization problem. For example, reducing battery mass is meaningful only at fixed delivered energy, load profile, thermal limits, lifetime conditions, and an explicitly chosen system boundary.

State at least one falsifiable primary hypothesis and a null or non-inferiority alternative where appropriate. Define the smallest effect that would matter in practice before selecting the final sample size. A hypothesis can fail without the project failing: a defensible finding that a more complex method offers no useful improvement is valuable.

## 3. Freeze the study before confirmation

The protocol must specify study version, hypotheses, primary outcomes, baseline versions, allowed information, datasets/splits, exclusions, budgets, stopping rules, sample-size logic, statistical analyses, and criteria for handling unavailable models or failed simulators. Preregistration distinguishes planned analyses from subsequent exploration; the [Center for Open Science guidance](https://www.cos.io/initiatives/prereg) motivates that distinction. The protocol template is a draft, not a registration already performed.

Pilot studies may determine plausible effect size, variance, simulator tolerances, and computational cost. Keep their cases separate from confirmatory cases unless the reuse policy was specified and justified before outcomes were examined. An outcome-driven change creates a new protocol version and an exploratory analysis label.

## 4. Comparators and fair information

Every study needs the simplest valid comparator and a credible specialist baseline. Energy control should compare against feasible rules and appropriate optimization; navigation against classical planners/controllers; AI memory against no-memory and equal-budget retrieval; inspection against a documented manual or deterministic workflow.

An oracle with realized future information is an upper/lower performance bound, not a deployable comparator. Controllers see only information available at the decision time. Training, calibration, prompt tuning, tool selection, memory population, and evaluation may not use held-out answers. If a model has unknown pretraining exposure, report contamination risk instead of asserting a clean benchmark.

For model/harness experiments, distinguish provider/model/version, reasoning mode, harness policy, tools, evidence corpus, context allowance, retrieval settings, output limits, retries, wall-clock limit, and monetary budget. A shared token budget is not necessarily equal compute across providers. Report both fixed-budget and quality/cost-frontier comparisons where feasible. Record caching, provider errors, and unavailable arms rather than removing them after seeing outcomes.

## 5. Experimental unit, splits, and replication

The independent unit is the system instance or scenario family that can support a generalization claim: site/day block, aircraft/mission family, vehicle serial number, user/session family, document source, task family, or dataset lineage group. Repeated timestamps or repeated model seeds within one unit are not automatically independent samples.

Use group-aware, time-aware, or source-aware splits to prevent related examples crossing train/calibration/test boundaries. Hold out difficult regimes intentionally: unseen sites, weather periods, vehicle variants, fault types, objective conflicts, evidence changes, and permissions. Separate in-distribution accuracy from out-of-distribution resilience.

Pair methods on the same scenario draws, initial conditions, and disturbance realizations when the design allows it. Repeat stochastic model and simulator runs within a scenario, preserving the nesting structure in the analysis. Never enlarge the apparent sample size by counting every control timestep as a new independent trial.

## 6. Sample size and uncertainty

Choose the required uncertainty from the decision being supported. For paired continuous outcomes, a useful planning approximation is

`n ≈ ((z_(1-alpha/2) + z_(1-beta)) * sigma_difference / delta_min)^2`,

where `n` counts independent pairs, `sigma_difference` is estimated from pilot pairs, and `delta_min` is the smallest effect worth detecting. This approximation is conditional on its distributional assumptions; skewed costs, clustered data, rare failures, and sequential studies need a tailored simulation or analysis. Do not substitute an arbitrary seed count for power analysis.

For a zero-failure binomial study, an approximate one-sided 95% upper bound is `3/n` for sufficiently large `n`. The exact bound is `1 - 0.05^(1/n)`. This calculation requires independent trials and a relevant sampling distribution; correlated simulation episodes do not establish an operational reliability rate. These are mathematical planning relationships, not measured safety claims.

Report effect sizes and uncertainty intervals, not only p-values. Use clustered/blocked resampling or hierarchical models when the design is nested. Preserve paired differences. Predeclare how multiple primary hypotheses are handled; label secondary and exploratory comparisons. Report numerical tolerances, measurement error, parameter uncertainty, model discrepancy, and random variability separately where the model permits it.

## 7. Physical and computational credibility

Physical-model verification asks whether the equations and algorithms are solved as intended. Validation compares the model with independent observations appropriate to its intended use. Neither is established by a smooth chart or optimizer convergence.

Check units, conservation identities, time alignment, feasible bounds, sign conventions, missing values, sensor bias, numerical step-size/mesh convergence when applicable, and calibration limits. Uncertain or unavailable physical validation data constrains the conclusion to simulation. Aerospace-specific credibility and testing requirements are detailed in AE-06.

For AI tasks, fluent rationales, self-reported confidence, and model judges are measurements needing validation. Prefer task outcomes, verifiable references, independent labels, and blinded human audit where applicable. The [NIST Generative AI Profile](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence) is a supporting risk-management reference, not a certification or an experimental acceptance threshold.

## 8. Metrics and failure accounting

Define each metric's unit, direction, denominator, aggregation, eligible population, exclusions, missingness behavior, and primary/secondary status. A battery's Wh/kg, electrical round-trip efficiency, delivered kWh, and cycle life are different quantities. A model's task success, calibration, latency, and cost must not be collapsed into a single score without stated weights and sensitivity analysis.

Count infeasible actions, invalid outputs, timeout, abstention, escalation, solver failure, missing sensor data, exhausted budget, and fallback invocation separately. A denominator cannot silently drop a failed attempt. Report both end-to-end outcomes and diagnostic metrics so an apparently better controller cannot hide violations or extra human labor.

Report measurement cost using actual run-time rates, currencies, and timestamps when purchased resources are used. This package does not estimate current API prices or authorize spend. Comparisons should expose total and marginal costs, data-labeling time, setup time, and review time where relevant.

## 9. Reproducibility and provenance

Every run records source-code revision, uncommitted changes if allowed, dependency/container lock, dataset digests, parameters, seeds, model identifiers, prompt/harness hashes, evaluator versions, execution environment, start/end time, and all generated artifact digests. The [W3C PROV overview](https://www.w3.org/TR/prov-overview/) supplies a useful entity/activity/agent vocabulary; the package uses a compact JSON envelope rather than claiming full PROV conformance.

Distinguish exact deterministic replay, statistical replication under the same distribution, independent implementation replication, and external physical validation. Hosted-model responses may change even under identical inputs; persist permitted inputs/outputs and effective model metadata, and state the reproducibility limit. No secret keys or unrestricted private observations belong in trace exports.

## 10. Data rights and human evidence

For each dataset, record source, version, access date, license or other permission, intended uses, redistribution limits, consent/access basis where needed, sensitive attributes, retention, deletion lineage, split policy, and limitations. “Publicly accessible” is not a license. Synthetic data must be labeled and must not be described as measured reality. Real people, sites, or vehicles remain separated from synthetic fixtures.

Human rating or oversight studies require a defined task rubric, rater qualifications appropriate to the claim, disagreement handling, blinded assignment where feasible, sampling, compensation/burden planning, and handling of sensitive records. Required institutional or jurisdiction-specific review must be resolved when the actual study is defined; this is not a claim that a particular legal regime applies to every project.

## 11. Completion and release

A completed research release contains the frozen protocol and deviations; versioned data manifests and access instructions; reproducible baseline and candidate implementations; full run ledger; primary and secondary results including failures; uncertainty analysis; independently checked representative outputs; thesis-style report; artifact contracts; and an explicit applicability/limitations section.

Product readiness is a separate decision requiring user needs, supportability, deployment conditions, rights, and domain-specific assurance. A benchmark-winning configuration does not automatically become a production controller or an approved aircraft design.
