# Shared interface contracts

**Status:** draft contract set v0.1.0. The schemas in `contracts/schemas/` are concrete specification artifacts. They do not imply that any proposed repository or service has been implemented.

## 1. Interchange model

Start with files. A producer emits an immutable payload and a JSON envelope. A consumer validates the envelope, checks its payload hash, applies domain semantic checks, and records both the artifact ID and digest in the experiment manifest. No central server is required. Local files, object storage, and a later API may all carry the same representation.

The proposed schema dialect is [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12). The package pins this dialect deliberately. Schema validation checks structure; units, chronology, authorization, physical feasibility, and experimental independence require additional semantic checks.

## 2. Contract catalog

| File in `contracts/schemas/` | Purpose | Key fields |
|---|---|---|
| `artifact.schema.json` | Portable payload envelope | artifact/project/type/version, payload path/digest, provenance, evidence class, units, limitations |
| `dataset.schema.json` | Dataset rights, lineage, and split declaration | source, license status, permitted use, sensitivity, split manifest, group/time policy |
| `experiment.schema.json` | Frozen run/study configuration | protocol digest, code/dependency revisions, arms, scenario IDs, seed policy, metrics, split policy, budgets |
| `result.schema.json` | Reported measurements and analysis | experiment/arm/metric IDs, independent-unit count, attempted/valid/failed counts, estimates, intervals, limitations |
| `decision-request.schema.json` | A bounded policy decision | request ID, observation/reference time, allowed actions/tools, constraints, budget, deadline, policy versions |
| `decision-response.schema.json` | A proposed action or fallback decision | request ID, status, action, uncertainty/evidence, constraint verdict, usage, reason |
| `trace-event.schema.json` | Ordered execution record | run/request/event IDs, monotonic sequence, wall time, stage, input/output artifact references, redaction |

The first version intentionally omits a universal domain-payload schema. A PV time series, aircraft mass model, inspection image dataset, and memory ledger cannot share one meaningful set of physical fields. Domain projects define payload schemas and register them through the artifact's `payload_schema` value.

## 3. IDs, paths, hashes, versions

Project IDs are stable (`EN-03`, `AE-06`, `AI-01`, `FND-02`). Artifact IDs identify records, not filesystem locations. `schema_version` identifies an interchange contract. `producer_version` identifies a producing release. `payload_sha256` is computed over the exact payload bytes and changes whenever the bytes change. Never use a hash of the manifest as though it were the hash of the data.

Example fixture paths are relative to `contracts/examples/`. Production payload paths must resolve inside an explicitly allowed workspace or authorized object namespace. Reject traversal, absolute paths outside the allowed root, unexpected schemes, symlinks leaving the root, and untrusted schema-network resolution. Schema identifiers are stable identifiers; validating them must not require fetching arbitrary URLs.

Use UTC ISO-8601 timestamps for records and a monotonic sequence for event ordering. Scenario payloads must also retain the source timezone and daylight-saving policy when local electricity tariffs, weather, or occupancy depend on civil time. A wall-clock timestamp cannot establish event ordering across machines by itself.

The fields in `contracts/examples/` are fabricated fixture values. Identifiers with `fixture` in them, miniature datasets, zero costs, and mock version strings are intentionally synthetic. They test interchange only.

## 4. Numeric conventions

Every physical variable has a declared unit and reference convention. Prefer SI for interchange; use domain units such as Wh or kWh only when stated and converted explicitly. Energy is not power. Absolute and gauge pressure, Celsius and Kelvin, mass and weight, state-of-charge and state-of-health, and electrical and thermal energy must be distinct fields or have explicit metadata.

For time series, declare sampling interval, interpolation, timezone, missing-value representation, alignment, observation cut-off, and any resampling or aggregation. A forecast contains issue time, valid time, horizon, and uncertainty representation. Consumers may use only forecast vintages available at their simulated decision time.

For aircraft state, declare coordinate frame, handedness, axis convention, angle convention, and reference altitude. For AI confidence, declare whether a number is a calibrated probability, empirical score, interval, or uncalibrated model statement. A generic `confidence: 0.9` without semantics is not accepted as a decision-risk estimate.

A dataset manifest may have unresolved rights and an empty rights.allowed_uses array. Empty allowed_uses grants no use; it permits recording quarantine metadata without fabricating permission. The executor must enforce the rights decision separately from structural validation.

## 5. Experiment semantics

An experiment manifest includes a protocol identifier/digest, study stage (`fixture`, `pilot`, or `confirmatory`), scenario split, input artifacts, hashed semantic-input manifests, arm definitions with configuration digests, primary metric, secondary metrics, and failure policy. An arm is a complete intervention: model, effective version, harness, tool policy, memory policy, baseline solver, and budget settings where applicable. Inapplicable fields are absent, not guessed.

Every run is associated with one immutable experiment manifest. The decision request carries its experiment manifest reference/digest and arm ID; response and trace records inherit that association through the same run/request identity, which consumers must check. Raw-payload hashes do not freeze split assignments, units, or provenance: input_manifests binds those semantic envelopes separately. Each arm also records a configuration_sha256 alongside its configuration reference. An adapter that cannot expose an exact model revision records that limitation. A mutable provider alias cannot be described as a pinned model version. Set a task-defined wall-clock limit, input/output allowance, retries, and external-call ceiling. Budgets belong to the study protocol; no monetary spend is authorized by these example files.

The final analysis includes all eligible attempts. `attempted_count = valid_count + failed_count` in the simple result schema. Abstention can be a valid response with its own task outcome; invalid output, timeout, and simulator crash are failures. Also report scheduled and unattempted task counts with reasons: scheduled_count = attempted_count + unattempted_count. A successful-completion rate over scheduled tasks retains unattempted scheduled cases in its denominator; an attempted-task diagnostic uses its explicitly different denominator. Additional domain accounting must preserve these distinctions.

## 6. Decision runtime semantics

The runtime receives an observation, action-space identifier, constraints, permitted tools, deadline, and budget. It returns `proposed`, `abstain`, `fallback`, or `error`. A model never changes the action space, grants itself a tool, raises its budget, or weakens a constraint. The `action` is a proposal and cannot represent a trusted physical actuation command without a separately defined domain execution gate.

The domain validator computes feasibility independently. An LLM's assertion that an action is feasible is not a validator. Requests specify the validator/policy version. A failed feasibility check produces a documented rejection and a deterministic fallback or explicit failure as specified by the domain. Runtime retries are bounded and included in cost and latency. Every repaired or fallback action must be revalidated against the current observation, authorization scope, constraints, and remaining budget. If no feasible fallback exists before the deadline, return abstain or error with the reason and the domain-defined no-action or controlled-stop outcome; a fallback label cannot imply feasibility.

Idempotency is keyed by request/run identity plus intended operation. Duplicate retries must not repeat side effects. In the initial research implementation, tools are read-only, local simulation, or sandboxed synthetic operations. Actual external writes or physical experiments require an explicitly selected study execution mode and its concrete operating procedures.

## 7. Trace and privacy semantics

Trace events capture observation receipt, retrieval, model call, tool call, validation, fallback, and completion. Persist parameters and permitted I/O sufficient to reproduce the experiment. Do not request hidden model reasoning. Observable responses, tool actions, evidence references, and a short public decision rationale are sufficient trace content.

Sensitive inputs should use restricted artifact references, redacted views, access scopes, retention policy, and deletion lineage. Revoking access must also invalidate derived retrieval indexes and caches where required by the study's policy. Cross-tenant retrieval is a failing test, not an experimental feature.

## 8. Integration contract matrix

| Producer → consumer | Payload | Essential semantic checks |
|---|---|---|
| EN-01 → EN-03 | generation/forecast series | same power/energy units, site/timezone, issue-time causality, curtailment convention |
| EN-02 → EN-03/AE-01/AE-02 | capacity/power/degradation envelope | cell versus pack boundary, temperature, mass/volume overhead, valid load range |
| EN-04 → EN-05 → EN-03 | thermal state and flexibility offers | comfort/process limits, availability, rebound, baseline, dispatch duration |
| AE-01/AE-03 → AE-04/AE-06 | vehicle capability and mission envelopes | coordinate frames, payload/endurance, thrust/power limits, model fidelity |
| AE-05 → AE-07 | degradation/RUL evidence | technology applicability, censoring, uncertainty, serial-number split |
| AI-03 → all studies | dataset and split manifests | permissions, duplicate clusters, held-out lineage, evidence class |
| FND-02 → AI-01 | traces and task outcomes | complete failures, budget accounting, arm identity, redaction consistency |
| AI-05 → FND-02/AI-02 | retrieved context/evidence | access scope, source time, as-of semantics, deleted/revoked items |
| AI-02 → AI-04 | support/calibration assessments | independent evidence, matched coverage, evaluator version and bias audit |

## 9. Compatibility and acceptance

The schema package needs valid and deliberately invalid fixtures for every contract. A consumer must reject missing units, bad hashes, unknown schema versions, invalid status/action combinations, invalid result denominators, and references outside allowed roots. Unknown enum values cannot silently become successful results.

The draft JSON Schemas enforce structural conditions. The package validator also checks local file integrity, result arithmetic, and example references. Domain semantic validators remain implementation work and are listed in the project specs. Do not interpret a passing schema fixture as physics validation or a completed integration.

Changes to a field's meaning or unit require a migration even if its JSON type stays the same. Maintain old fixtures and document compatible ranges. Consumers may pin an older release until migration passes; one project's research schedule should not force every repository to upgrade simultaneously.
