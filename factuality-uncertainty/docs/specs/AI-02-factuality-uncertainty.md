# AI-02 — Factuality and uncertainty

**Proposed repository:** `factuality-uncertainty`  
**Status:** research specification; no verifier, calibration results, or experiments are claimed complete.  
**Source intent:** “Factuality and uncertainty” in [eng-research](https://app.notion.com/p/402a1ee8bd068049accae3dcf68095ae).  
**Specification date:** 2026-10-28. Numerical targets and experimental settings below are proposed, not measured results.

## 1. Purpose and standalone value

Develop a verifier and decision policy that can answer three separate questions: **what claims were made, what evidence supports them, and when should the system abstain or request review?** The deliverable is a local library/CLI that accepts claims or answer documents plus an authorized evidence corpus and returns claim-level support, uncertainty, and a review recommendation. It is independently useful for technical reports, retrieval systems, evaluation pipelines, and research assistants.

Factual support is not the same as truth. A claim may match a mistaken source, lack evidence despite being true, or become outdated. Accordingly, the product must expose source reliability, time, contradictions, and missing information rather than emit one opaque “truth score.” The proposed initial scope is text and structured numeric claims in engineering documents; images, medical diagnosis, legal judgment, and direct physical control are outside the first release.

FActScore provides a reference for decomposing long-form text into atomic factual units and checking source support. TruthfulQA provides a different benchmark of answers to questions designed around common false beliefs. Neither alone measures numerical correctness, causal validity, or engineering safety. [AI-S03](https://aclanthology.org/2023.emnlp-main.741/), [AI-S04](https://aclanthology.org/2022.acl-long.229/).

## 2. Research questions and hypotheses

**RQ1:** Does evidence-linked claim verification reduce unsupported assertions at an acceptable answer coverage and cost? **H1:** Retrieval plus explicit claim verification lowers the unsupported-claim rate relative to the same reader with retrieval alone, at matched answered-question coverage.

**RQ2:** Can confidence estimates predict correctness on held-out domains? **H2:** A calibration method fitted only on a calibration split improves proper scoring loss and selective risk over raw elicited confidence; improvements may disappear under domain shift.

**RQ3:** What errors remain after a text claim is supported? **H3:** Explicit unit, numerical tolerance, timestamp, and evidence-scope checks catch additional engineering errors that a text-only support judge misses.

Each hypothesis is falsifiable. A verifier that reduces errors only by refusing nearly all questions has not demonstrated H1. A method that improves calibration while worsening all useful risk–coverage tradeoffs is not automatically preferable. A null result can identify when verification overhead adds no practical value.

## 3. Functional requirements and interfaces

| ID | Requirement | Acceptance behavior |
|---|---|---|
| AI-02-R01 | Preserve claim identity and scope | Each claim maps to source answer spans; conjunctions and numerical qualifiers remain traceable |
| AI-02-R02 | Distinguish evidence states | Supported, contradicted, insufficient evidence, and not fact-checkable are separate outputs |
| AI-02-R03 | Record evidence provenance | Source ID/version/hash, quote locator, publication/as-of time, retrieval time, and access scope accompany each judgment |
| AI-02-R04 | Support structured numeric validation | Units, bounds, arithmetic, tolerance, and the underlying assumptions are evaluated independently of prose support |
| AI-02-R05 | Separate confidence types | Model-elicited, verifier, empirical calibrated, and unavailable confidence are not conflated |
| AI-02-R06 | Permit abstention and escalation | Return explicit reason codes and unresolved evidence requirements |
| AI-02-R07 | Preserve conflicting evidence | Contradictions cannot be silently merged into one confident response |

Proposed input `ClaimBundle` includes `claim_id`, `text`, `answer_span`, `claim_type`, `as_of`, `domain`, and optional structured `quantity`, `unit`, `tolerance`, and `assumption_refs`. `EvidenceBundle` includes immutable version references, authorized content locators, and declared source quality metadata. Proposed output `VerificationResult` includes evidence state, support citations, contradictions, check failures, confidence method, calibrated probability when valid, and suggested action.

`verify(claims, evidence, policy)` and `select(results, risk_policy)` are proposed library contracts. All outputs use the FND-01 artifact/result envelope. Verification must work on supplied local evidence without a model-provider account; deterministic and fixture-based adapters provide the minimum standalone path. Live retrieval and FND-02 execution are optional adapters. No output from this project can authorize an external action by itself.

## 4. Data and ground truth

Build three explicitly separate tracks: short factual questions, long-form technical answers, and structured numerical statements. Start with rights-cleared public engineering references and synthetic numerical problems with exact solutions. Use TruthfulQA and FActScore-compatible tasks only after documenting dataset version, license, allowed redistribution, and any modifications. A paper being public does not establish that every associated dataset can be repackaged.

For technical documents, annotate claims against a frozen evidence snapshot. Include true-but-unavailable claims, stale-but-once-correct claims, misleading source snippets, incompatible units, uncertain ranges, and assumptions presented as facts. Preserve “not determinable from available evidence” as a valid label. Reviewers see source material and the agreed rubric, not model identity or method labels.

Split by source document, entity, and scenario family before generating paraphrases. Keep all paraphrases and derived questions from one source family in the same split. Use development, calibration, and final test partitions, plus a distinct shifted-domain test. Calibration data cannot train the answerer or tune the final test rubric. AI-03 can provide lineage and contamination checks as an optional preprocessing step.

Use independent annotators for a pilot and for a stratified final audit. Record disagreements and adjudication rather than discarding difficult claims. Disagreement may indicate source ambiguity, not annotator failure. Review of energy and aerospace numerical claims requires suitable domain expertise; until obtained, label that track synthetic or provisional.

## 5. Experimental matrix and baselines

Hold the answer model and evidence budget fixed while comparing: direct answering; retrieval only; retrieval plus evidence citations; claim decomposition plus verification; and structured verification with abstention. Include a deterministic source lookup or exact numerical solver wherever a task permits it. Compare at least two independently implemented verification approaches to reveal evaluator-specific artifacts.

For uncertainty, compare raw elicited confidence, a held-out calibration map, and abstention based on evidence sufficiency. When class logits are available, temperature scaling is an eligible baseline. The classic calibration paper studied classification models; applying its method to open-ended answer correctness requires defining a valid probability event and independently testing transfer. [AI-S05](https://proceedings.mlr.press/v70/guo17a.html). Do not apply a temperature to arbitrary prose confidence and call it calibrated model probability.

Run ablations removing retrieval, decomposition, time filtering, numerical checking, and contradiction handling one at a time. Record whether retrieval failed to find evidence or the verifier misread evidence that was present. Use an oracle-evidence diagnostic to separate these errors; oracle results are diagnostic upper bounds, not deployment performance.

Stress tests include evidence updates, authoritative-looking but irrelevant citations, omitted qualifiers, mismatched denominators, decimal/unit errors, mutually inconsistent sources, poisoned retrieved instructions, and domain shift. All inputs remain bounded research fixtures. A citation's presence alone never counts as support.

## 6. Metrics and statistical plan

Primary outcomes are unsupported/contradicted factual assertions among asserted claims and **question-level task correctness at matched coverage**. Report both: a model that emits fewer claims can raise claim precision while failing to answer. Show claim recall/completeness where reference claim sets are meaningful, citation precision, evidence retrieval recall, and numerical-check sensitivity/specificity on labeled fixtures.

For uncertainty, use Brier score or log loss for a clearly defined correctness event; clip probabilities only with a documented numerical rule. Show reliability plots and expected calibration error with declared bins as diagnostics, not the only conclusion. Report risk–coverage curves, abstention rate, escalation rate, and errors among accepted answers. Separate each domain and distribution-shift condition.

Cluster confidence intervals by question/document, because claims within an answer share evidence and generation. Use paired comparisons on identical questions. A proposed planning threshold is an absolute five-percentage-point reduction in unsupported-claim rate at no more than a two-percentage-point loss in question coverage; both values must be revised or accepted prospectively after pilot economics and reviewer needs are understood. Estimate required independent documents from pilot variance. Do not pretend that thousands of correlated claims from a few documents constitute a well-powered study.

A confidence interval or empirical risk estimate does not establish a deployment guarantee under arbitrary shift. If conformal or other coverage-control methods are added, document their assumptions and test whether the calibration/test construction fits those assumptions. This initial specification makes no distribution-free guarantee.

## 7. Reuse and dependency boundaries

FND-01 schemas are the only required portfolio dependency. FND-02 optionally supplies retrieval/model execution; AI-01 consumes this project's scorers without importing its live execution stack. AI-03 can export reviewed claims as a distinct labeled dataset; AI-04 can consume abstention and contradiction signals; AI-05 can attach temporal source versions to memory retrieval.

EN-01/EN-02 use structured checks for literature extraction, not as substitutes for physical validation. EN-03 may flag an explanation inconsistent with its actual dispatch result. AE-07 can separate image-derived inspection findings from unsupported maintenance narratives. Every such integration must preserve the difference between a measured physical quantity and a textual claim about that quantity.

## 8. Delivery plan and gates

| Stage | Concrete backlog | Deliverable |
|---|---|---|
| M1 | AI-02-T01 define claim/evidence schema; AI-02-T02 write annotation rubric and source policy | Hand-reviewed fixtures spanning all evidence states |
| M2 | AI-02-T03 implement deterministic numeric/time checks; AI-02-T04 implement source-linked verification adapters | Offline verifier with explicit unsupported cases |
| M3 | AI-02-T05 construct leakage-resistant splits; AI-02-T06 run pilot and fit calibration only on its allowed split | Preregistered final design and resource estimate |
| M4 | AI-02-T07 run controlled baselines/ablations; AI-02-T08 audit errors and distribution shift | Factuality, completeness, calibration, and cost results |
| M5 | AI-02-T09 package CLI/library; AI-02-T10 publish evidence limitations and reproducible report | Standalone release and a complete thesis-style report |

**AI-02-G01:** Every factual verdict links to evidence or an explicit evidence absence. **AI-02-G02:** Deterministic known-answer quantity/time fixtures pass, including deliberate failures. **AI-02-G03:** No calibration or test family crosses an unauthorized split. **AI-02-G04:** Results include abstention, completeness, contradictory evidence, and shifted-domain behavior. **AI-02-G05:** Research completion requires a reproducible conclusion, including failure to improve; product promotion requires meeting the separately preregistered risk/coverage/cost policy.

Proposed layout: `src/factuality_uncertainty/{claims,evidence,numeric,calibration,selection}/`, `rubrics/`, `adapters/`, `fixtures/`, `protocols/`, `tests/`, and `reports/`. Open decisions are the initial domain, qualified reviewers, acceptable evidence classes, required coverage, and handling of licensed source text. All remain visible in the experiment manifest rather than becoming undocumented defaults.
