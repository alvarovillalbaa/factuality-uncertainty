# AI-02 requirement and release audit

Last updated: 2026-10-31

The software and synthetic study are committed and published in draft PR #1.
Full research completion is not claimed: independent annotations and the real
engineering-reference extension remain pending. The user authorized branch/commit/PR operations; no approval for
new provider spend, physical control, dependencies, production or infrastructure
was inferred.

| Requirement / task | Current authoritative evidence | Assessment |
|---|---|---|
| R01, T01: claim identity/schema | schema.py; exact span/canonical-text checks; conjunction fixture | Implemented for supplied typed claims; arbitrary prose decomposition unavailable |
| R02: four evidence states | verification.py; all fifteen known-case unit assertions; complete row payloads | Implemented |
| R03: provenance | Raw source hash, version, quote, publication/as-of/retrieval, quality, license and scope on every citation | Implemented for local typed sources |
| R04, T03: units/bounds/arithmetic/time | numeric.py; conversion, dimensions, denominator, tolerance, assumption and date fixtures | Implemented within allowlisted dimensions |
| R05: distinct confidence | question calibration with explicit event/scope; claim probability unavailable; unit assertions | Implemented |
| R06: abstention/escalation | select; explicit reasons/evidence requirements; main test 120 abstentions and 144 reviews | Implemented |
| R07: conflicting evidence | Both sources retained; strict selection escalates; no-conflict ablation remains visibly unsafe | Implemented |
| T02: rubric/source policy | rubrics/source-support.md; docs/references/contracts.md; CC0 synthetic manifest | Synthetic fixtures only; real source rights/qualified annotation pending |
| T04: source-linked adapters | Full-sentence literal matcher and independently coded typed matcher, sharing filters | Implemented bounded approaches; no semantic model or independent external replication |
| T05, G03: leakage-resistant splits | Source/entity/document checks, sealed ordered hashes and disjoint allocation; negative leakage tests | Implemented; template mechanism intentionally shared and declared |
| T06: pilot/calibration | Corrected 720-row pilot; planning.json; twelve calibration families; committed freeze before outcomes | Computational evidence present; independent pilot labels pending |
| T07: baselines/ablations | Twelve arms, fixed answers and evidence; all 6,480 original rows; latency diagnostics corrected before final run | Synthetic controlled filtering comparison; real reader/retrieval effectiveness untested |
| T08: audit/shift | Twelve shifted families; 45 blinded cases; annotation import validation, disagreement retention and explicit adjudication requirement | Distribution shift run; independent final annotation/adjudication pending |
| T09: standalone library/CLI | Public API, project entry point, examples, isolated source CLI/checks, draft PR #1 | Source execution and publication proven; fresh installation not run |
| T10: report/limitations | reports/research.md, complete analysis and provenance, FND-01 exports | Provisional conclusion; full research release remains open |
| G01: support or evidence absence | Main verdict citations or explicit exclusion/absence reasons; scope leak negative fixture | Proven in bounded fixtures |
| G02: deliberate quantity/time failures | Unit tests and exact deterministic main replay | Proven in declared dimensions |
| G04: abstention/completeness/conflicts/shift | Full analysis, risk curves, both claim/question denominators and shifted-source false answers | Present, provisional design labels |
| G05: reproducible full conclusion | source-export-final.json, reports/research.md, immutable inputs and original outcomes | Provisional replay passes; independent evidence and remaining source tracks prevent full completion |

Focused checks: 29 T2 unit tests; 720 corrected pilot and 6,480 final row replays;
49 FND-01 artifact/result records; network-disabled gitless source export and CLI;
git diff --check. Original 720-row timing-contaminated pilot remains retained
as superseded evidence rather than being silently replaced.

No installs, builds, databases, large worktrees or hosted checks ran. Existing
Python 3.12.14 and validator dependencies were used read-only. Temporary export
and CLI directories were removed after verification. The 30 GiB storage reserve
was respected by avoiding gated installations; no unrelated files were deleted.

Next: obtain the two independent annotation files against audit/packet.json,
record disagreements and adjudication, choose rights-cleared real-reference
tasks and qualified reviewers before any empirical extension. Publication is
recorded in docs/publication.md. New evidence requires a new report/protocol version;
never alter original labels or claim that replay creates new samples.

Alvaro explicitly chose to leave independent annotation pending on 2026-10-31.
That permits handing off this provisional implementation and report; it does
not create annotation evidence or promote the research/product gate. The real
engineering-reference track remains a separately gated empirical extension.
Output schema and figure generation were added after the main run as validation
and reporting artifacts. Frozen computational inputs and original outcomes were
not changed.
