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

The library exports `verify(claims, evidence, policy, calibrator=None)` and
`select(results, risk_policy)`. The CLI reads JSON only and emits FND-01
artifact envelopes with hashed local payloads. See [input contracts](docs/references/contracts.md).

Use Python 3.11+ with FND-01 0.1.0 and its validator dependencies available.
For a source checkout with research-contracts alongside it:

```sh
PYTHONPATH=src:../research-contracts/src python -m factuality_uncertainty \
  examples/claims.json examples/evidence.json /tmp/ai02-example-output \
  --revision ai02-source-v1
```

Choose a new output directory: existing evidence is never overwritten. The
example emits `artifact.json` and `verification.json`; the answer is supported
within its invented source. No credentials or network are needed. JSON Schemas
can be printed with `python -m factuality_uncertainty.schema` on the same path.

Verification commands:

```sh
PYTHONPATH=src:../research-contracts/src python -m unittest discover -s tests/unit
PYTHONPATH=src:../research-contracts/src python experiments/study.py replay
PYTHONPATH=src:../research-contracts/src python scripts/verify_release.py \
  --contracts-repo ../research-contracts --receipt /tmp/ai02-source-export.json
git diff --check
```

The [provisional report](reports/research.md) covers 6,480 final rows and
720 corrected pilot rows. [Release evidence](docs/release.md) maps requirements
to artifacts and open gates. Independent pilot/final annotations are pending;
the full research specification is **not complete**. The [45-case blinded
packet](audit/packet.json), rubric and blank annotation template are ready.

No fresh installation, hosted CI, real-model, empirical engineering, human audit
or production proof is claimed. Storage Guard prevented environment installation;
source replay uses existing dependencies read-only. Publication status is recorded
in [docs/publication.md](docs/publication.md).
