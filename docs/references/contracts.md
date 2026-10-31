# Local contracts and source policy

Last updated: 2026-10-31

Version 0.1.0 accepts JSON ClaimBundle and EvidenceBundle records. The runnable
input validator is `validate_input` in verification.py; examples are generated
in fixtures/tasks.json. Unknown evidence versions and malformed bindings fail
before any verdict. The CLI never resolves network or file locators in corpus
content. JSON files are supplied explicitly, limited to 16 MiB each and checked
for duplicate keys, non-finite numbers and invalid UTF-8 encodings.

ClaimBundle has `version`, `bundle_id`, `answer` and a nonempty `claims` array.
Each claim has a unique `claim_id`, exact Unicode character `answer_span`
(`[start,end)`), `text`, `claim_type` (`text`, `numeric`, `opinion`), `as_of`,
`domain`, `subject`, `predicate`, `value`, `qualifiers`, `assumption_refs` and
optional `model_confidence`. Non-opinion text must equal the canonical typed
sentence. Explicit spans handle conjunctions without losing qualifiers; arbitrary
prose decomposition is unavailable. Unannotated answer text is outside the
asserted-claim set and is not certified. Claim completeness must therefore be
measured separately against a reference inventory.

Numeric claims also carry `unit`, optional `tolerance` in canonical base units,
and optional `arithmetic` with an allowlisted `op` and two typed operands.
Supported dimensions are energy, power, time, mass and ratio. Unknown units,
dimension errors, zero division, inconsistent bounds, missing assumptions and
claim tolerances exceeding the source tolerance fail explicitly. Source bounds
are in canonical base units. This is no general symbolic algebra or physics check.

EvidenceBundle has `version` and `sources`. Each source has unique `source_id`,
immutable `version`, raw UTF-8 text SHA-256, `text`, `domain`, `access_scope`,
`quality`, `license`, `published_at`, `as_of`, `retrieved_at`, and typed `facts`.
Each fact has a canonical sentence bound to its exact `quote_span`, typed
subject/predicate/value/qualifiers, assumptions and `[valid_from,valid_until)`.
Typed assertions are trusted annotations. Matching an annotation to its quote
prevents byte substitution; it does not independently validate source reliability
or the annotation's semantic interpretation.

Policy 0.1.0 has adapter (`literal` or `structured`), allowed scopes, source count
budget, retrieval/decomposition/time/numeric/contradiction flags. The caller owns
the authorization boundary; source text never grants access. Excluded sources
yield reason codes without quotes or source IDs. Retrieval time records when the
snapshot was acquired; publication/as-of and fact validity determine whether the
information existed at claim time. Historical snapshots may be acquired later.

Literal verification compares full quoted sentences after whitespace normalization.
Structured verification independently compares typed subject/predicate/value
and qualifiers, then performs numeric validation. They share corpus filtering
and differ in matching logic; this does not constitute independent external
replication. Conflicting sources survive in the output even in ablation runs.
No recognized support yields explicit evidence absence. Outputs keep source
quality metadata rather than converting assumed authority into a truth score.

VerificationResult includes all four evidence states, citations, contradictions,
numeric failures, reason codes, required evidence and suggested action. It hashes
the complete input and effective policy. Model-elicited confidence, deterministic
verifier indicators and unavailable claim probabilities remain distinct.

Optional question calibration uses five fixed bins with Laplace smoothing fitted
only on calibration families. The event is `all_required_factual_claims_correct`.
Bundle `family`, `domain` and `raw_probability` are required to apply it. The map
is unavailable for reused families, new domains, policy mismatch or empty bins.
It is never presented as an individual claim's calibrated probability. Selection
checks every supplied factual claim; a requested probability threshold fails
closed when the question probability is unavailable. No external action follows.

CLI exports contain a FND-01 0.1.0 artifact envelope and hashed payload. Study
summaries additionally use FND-01 result records. FND-01 is the sole mandatory
portfolio dependency; no runtime import of AI-01/FND-02/AI-03/AI-05 is added.
