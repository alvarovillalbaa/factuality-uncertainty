# Factuality and uncertainty

Last updated: 2026-10-31

AI-02 provides local claim verification, separate numeric checks, evidence
provenance, calibration and abstention. It compares exact sentence lookup with
typed source assertions. Both are bounded deterministic approaches, and neither
establishes the truth of a source or understands arbitrary natural language.

The selected study uses invented engineering documents and exact numerical
problems. No hosted model, licensed benchmark, live retrieval or physical system
is connected. The supplied AI-02 specification remains authoritative in
docs/specs/. Scope decisions and release evidence live in docs/.

The library exports `verify(claims, evidence, policy)` and
`select(results, risk_policy)`. The CLI reads JSON only and emits FND-01
artifact envelopes with hashed local payloads. Commands and full input semantics
will be documented alongside the implementation before release.
