Add an offline AI-02 library and CLI that retain claim spans, authorized evidence
provenance, contradictions, numeric failures and explicit abstention. A frozen
synthetic comparison shows that strict verification reduces unsupported accepted
claims while losing substantial coverage, and still accepts false claims from
wrong sources under shift.

Validation: 28 unit tests; exact replay of 720 corrected pilot and 6,480 final
rows; 49 FND-01 envelopes; CLI and source replay from gitless exports with
networking disabled. The original pilot and its timing correction are retained.
No dependency installation or hosted CI was run.

Draft: independent pilot/final annotations and adjudication remain pending, as do
rights-cleared real engineering-reference tasks. Forty-five blinded cases and
strict annotation import are ready. The report is provisional and does not close
AI-02's full research-release gate or imply real-model/physical/product evidence.
