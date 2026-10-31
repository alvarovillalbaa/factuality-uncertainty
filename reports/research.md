# AI-02: source support and abstention on invented technical documents

Last updated: 2026-10-31

**Status: provisional synthetic research; independent annotation and final
research release gates remain open.** All results below are conditional on
invented fixtures. No real model, physical system or human rating was measured.

## Question and methods

The study asks whether deterministic claim verification reduces unsupported
assertions while preserving useful question coverage. A fixed scripted answerer
supplies identical answers and raw confidence to direct, retrieval, citation,
literal verification, structured verification and strict abstention arms.
Five ablations remove retrieval, decomposition, time checks, numeric checks or
contradiction handling. An oracle-evidence diagnostic sees the same exhaustive
local corpus, so cannot improve retrieval or manufacture missing evidence.

Three tracks cover short questions, long technical answers and structured
numeric statements. Fifteen scenarios include correct, contrary, absent,
subjective, unit, conversion, arithmetic, qualifier, stale, conflicting,
poisoned-instruction, future, bounded and denied-source cases. Calibration
families are disjoint from development, pilot, test and shifted families by
entity, document and source group. Paraphrases and claims never inflate the
independent-family count.

The original four-family pilot is retained in reports/pilot-initial. A baseline
timing correction was made before final analysis and documented in
docs/pilot-notes.md. The corrected pilot contains 720 rows. Its paired variance
of 0.008889 implies about 28 families under the approximate five percentage
point planning calculation. The final allocation is 24 test and 12 shifted
families, with repeated invented templates; it is explicitly descriptive.

Twelve calibration families fit five fixed probability bins with Laplace
smoothing for the event that every required factual claim in an answer is
correct. Probabilities are unavailable outside the calibrated domain, for reused
calibration families, different policies or empty bins. Raw elicited confidence
and deterministic verifier indicators remain separate.

Source revision 12a31f8240e7457f249c6dbe1f76dc2dc0c12927 committed the source,
fixtures, rubric, calibration maps and protocol seal before main outcomes.
The final matrix has 6,480 scheduled and attempted rows, zero unattempted rows,
zero provider calls and zero purchased-provider spend. Main runtime was 2.42
seconds on the recorded local interpreter; no latency extrapolation is made.
All outputs, input seals, failures/reasons and denominator definitions are in
reports/main/ and protocols/.

## Results

| Method | Test question coverage | Unsupported asserted claims | Test accepted errors | Shift accepted errors |
|---|---:|---:|---:|---:|
| Retrieval, fixed answers | 100% | 65% | 168 / 360 | 96 / 180 |
| Literal verification | 40% | 50% | 72 / 144 | 48 / 72 |
| Structured / strict abstention | 26.67% | 0% | 0 / 96 | 12 / 48 |

Strict abstention on test answers also emits 120 abstentions and 144 review
recommendations; on shifted answers, 60 abstentions and 72 reviews. Suggested
review is a measurement, never an external action.

At exactly 26.67% question coverage, retrieval's raw-confidence ranking makes
46 errors among 96 test questions, versus zero under strict evidence ranking.
The paired increase in correct questions per scheduled question is 0.12778,
with a family-bootstrap interval [0.10000, 0.16389]. On shifted questions it is
0.07778 [0.04444, 0.11667]. These intervals describe the invented scenario
allocation, not a human/model/engineering population.

At matched coverage, unsupported asserted-claim rates are 65.12% versus 0% on
test and 65.63% versus 0% under shift. Selection IDs are retained. Whole-answer
correctness and claim correctness have different denominators; the full
risk–coverage curves, reference-claim recall and citation precision diagnostics
are in analysis.json. The strict test arm recovers only 19.05% of the reference
claim inventory when abstained answers count as missing. Opinion spans are
kept outside factual assertion denominators, while the reference inventory
conservatively retains supplied claim slots.

Numeric-check sensitivity and specificity are each 1.0 on the selected known
fixtures. Removing numerical checks accepts erroneous unit/arithmetic/bounds
cases and raises test accepted errors to 96. Removing time checks raises them
to 24. These fixtures test explicit failure mechanisms and establish no rate for
unseen engineering errors. The exhaustive-corpus oracle equals the structured
arm, as expected; actual retrieval-search error is unmeasured.

Raw test Brier loss is 0.32250; the calibration-split map yields 0.24889.
This is a descriptive synthetic improvement. Shifted-domain raw Brier loss is
0.35583, and all 180 shifted questions correctly receive unavailable calibrated
probability. Reliability bins, ECE, clipped log loss and resource measurements
remain visible rather than selecting only a favorable metric.

## Interpretation and limits

The five percentage point unsupported-claim threshold is exceeded at matched
coverage in this constructed matrix. Deployment coverage drops by 73.33
percentage points, far exceeding the proposed two point allowance. H1 therefore
does not establish the proposed useful operating tradeoff. H2 has a descriptive
in-domain proper-score improvement but no transfer evidence. H3's explicit
numeric/time fixtures pass, without proving general engineering validity.

Twelve shifted accepted answers are false despite supported citations: a wrong
invented source states a wrong fact. Verification measures support, not truth.
Poisoned text remains inert data. Source quality metadata is exposed, never
interpreted as guaranteed reliability. Typed annotations and manually supplied
claim inventories are trusted; arbitrary prose entailment/decomposition is not
implemented. Both adapters share source filtering, so common filtering errors
can affect them together.

Independent pilot/final annotators and suitable real-domain reviewers have not
supplied labels. The 45-case blinded packet removes method identity, design
scenario names and raw confidence. No human disagreement or adjudication rate
is fabricated. Numerical exact answers and the creator's rubric checks remain
provisional until the specified independent annotation evidence exists.

Rights-cleared public engineering-reference tasks and licensed benchmark tracks
remain unimplemented; all current task documents are synthetic and their fixture
rights are recorded. No real-generation, FActScore/TruthfulQA reproduction,
arbitrary-shift guarantee or product-promotion claim follows. Operational
risk/coverage/cost policy remains unapproved. This report is a reproducible
provisional conclusion, not a completed AI-02 research release.

## Reproduction

README.md gives replay, CLI, unit and isolated-export commands. The source export
receipt records 28 tests, both original corrected pilot and final score replay,
49 FND-01 envelopes, and CLI behavior with networking disabled. Existing
dependency versions and FND-01 revision are captured in that receipt; the
dependency snapshot was recorded after the study in the same session with no
dependency installation between run and snapshot. It was not a preregistered
external environment lock. Fresh wheel/venv installation and hosted CI have not
run. Exact replay is not a new independent sample.
