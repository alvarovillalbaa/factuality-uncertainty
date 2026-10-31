# Execution plan and research gates

## 1. Recommended first slice

**Start with energy-orchestration as a classical simulation benchmark, backed by a minimal research-contracts package and evaluation-lab.** This is a recommendation based on the portfolio's integration value, not a ranking inferred from the unlabeled source scores. It yields a measurable controller comparison and exercises energy, AI, and shared infrastructure without waiting for aircraft hardware or novel materials.

The first vertical slice is a small generation/load/storage fixture → rule-based controller → constrained optimization baseline → result ledger → reproducible report. Add a model/harness arm only after the physical accounting, baseline feasibility, and measurement pipeline work. Existing public/reference datasets or a clearly labeled synthetic system can start the pipeline; empirical claims require the relevant real evidence.

In parallel, AE-01 can begin mission definition and classical aircraft sizing with synthetic/component-reference inputs. AI-03 can define rights and split lineage. These are bounded workstreams with their own useful outputs. They should not block the energy baseline on completion of the entire portfolio.

## 2. Stages and evidence gates

| Gate | Work | Evidence required to pass |
|---|---|---|
| G0 — scope | Resolve study-specific ambiguity, users, constraints, and primary question | Versioned scope, source links, assumptions, standalone deliverable |
| G1 — evidence | Acquire permitted data; implement simplest valid baseline | Dataset manifest, rights check, split plan, physical/task sanity checks |
| G2 — pilot | Estimate variance, failure modes, tolerances, and resource cost | Pilot ledger, revised protocol, sample-size/budget proposal |
| G3 — protocol freeze | Freeze primary outcomes, comparisons, stopping/exclusion rules | Immutable protocol version/digest and timestamp; holdout protected |
| G4 — study | Execute frozen comparisons and robustness tests | Complete runs including failures; resource accounting; independent-unit counts |
| G5 — research release | Analyze, reproduce, review, write thesis and reusable artifact | Effect sizes/uncertainty, limitations, source/data/code lineage, replay evidence |
| G6 — product/physical extension | Qualify a concrete application, deployment, or physical test | Appropriate operating requirements, evidence gaps, and application-specific review |

G0–G5 define research completion. G6 is a distinct extension; it cannot be inferred from a simulation benchmark. A negative research result can pass G5. A stage may reveal that a project should stop, narrow, or change question; that is an evidence-based outcome rather than a reason to manufacture success.

## 3. Portfolio sequencing

| Track | Begin with | Add when useful evidence exists |
|---|---|---|
| Shared contracts | FND-01 envelopes, units, fixtures, result accounting | Migration tooling, richer domain extensions |
| Decision experiments | AI-01 offline evaluator; FND-02 mock/classical adapters | Real providers, AI-02 calibration, AI-04 audited oversight, AI-05 memory |
| Energy | EN-03 feasible dispatch on simple fixtures | EN-01/02 physical models; EN-04/05 flexibility and thermal coupling |
| Civil aircraft | AE-01 mission/sizing; AE-03 comparative accounting | AE-06 coupled validation, AE-04 fleet coordination, AE-05/07 reliability |
| Specialized aerospace | AE-02 architecture scope; AE-08 fluid-system applicability | Higher-fidelity or physical work after scope and evidence gates |

These tracks describe prerequisites, not calendar promises. Project-specific backlogs in each spec contain the technical work. `planning/backlog.csv` provides an import-friendly portfolio delivery spine with IDs, dependencies, outputs, and acceptance evidence. It is not a set of tasks already created in Linear, Notion, or GitHub.

## 4. Avoid simultaneous infrastructure build-out

Implement the minimum contract needed by the first two consumers. A simple local runner with one mock adapter and one deterministic optimizer is enough to test the interface. Adopt a workflow engine, vector database, cloud scheduler, or full agent framework only after a measured requirement justifies it. Compare harnesses as study interventions instead of embedding one unexamined framework as the portfolio's permanent architecture.

Within a domain, freeze an artifact release and hand it to the consumer. For example, EN-02 v0.1 may provide a limited storage model with known uncertainty while the thesis continues. EN-03 should state the limitations of that model rather than waiting for a perfect battery study.

## 5. Budget and capacity planning

No provider spend, physical test budget, staffing, or delivery date is approved in the source. Estimate resources after the pilot. A computational study budget can be decomposed as:

`scenario families × independent cases × model arms × harness arms × repetitions × mean cost per run`,

plus baseline solver time, dataset acquisition, labeling, evaluation, review, storage, and contingency. This product is a planning upper bound; not every study needs a full factorial. A fractional design or a staged screening study can reduce cost, but its interaction-identification limits must be declared before analysis.

Track monetary cost in the purchase currency and rate date, CPU/GPU hours, wall-clock elapsed time, energy where measurable, human labeling/review time, and simulator fidelity. Set a hard run/call ceiling and an interruption policy. Failed and retried calls count. Do not calculate a budget from undocumented current model prices.

## 6. Promotion decisions

Promote a project from pilot to confirmation when the comparator is valid, the metric is stable, required rights/data exist, numerical or task sanity checks pass, and the expected study can answer its primary question within the chosen budget. Promote from research to a product only when a real user can use the artifact independently and the evidence supports that use.

Pause or redirect if the hypothesis cannot be tested with available data, the selected system boundary makes comparisons unfair, observed effects are smaller than relevant uncertainty, an external model is unavailable, or a project depends on an unresolved interpretation such as airship versus eVTOL. Record why and what evidence would change the decision.

## 7. First repository contents

For any selected project, the first meaningful commit should include a source-linked spec, a small fixture with rights/evidence classification, a baseline that executes, a test for the most consequential invariant, and a result artifact. Add the frozen protocol and full experiment matrix after the pilot. A folder structure alone is not a research milestone.

The proposed repository naming and ownership should be decided when implementation is requested. This ZIP creates no remote repositories and assigns no people, dates, or statuses to external systems.
