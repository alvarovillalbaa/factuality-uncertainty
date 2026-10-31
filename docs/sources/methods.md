# Inspected methodological sources

Last updated: 2026-10-31

The supplied ZIP is preserved byte-for-byte for the selected spec and shared
method documents; docs/specs/provenance.json records member and archive hashes.
Live publication pages inspected on 2026-10-31:

- [FActScore](https://aclanthology.org/2023.emnlp-main.741/): claim-level source
  support motivates separate atomic judgments. Its model, biography data and
  empirical findings are not reproduced here.
- [TruthfulQA](https://aclanthology.org/2022.acl-long.229/): a distinct task of
  avoiding common false beliefs. No dataset is downloaded or repackaged.
- [Guo et al., calibration](https://proceedings.mlr.press/v70/guo17a.html):
  classification confidence calibration motivates held-out scoring. This release
  uses a fixed histogram map for a defined binary question event, not temperature
  scaling of prose or an assertion of a distribution-free guarantee.

Synthetic source documents are newly invented fixture text. CC0-1.0 applies to
those fixture documents only, and grants no rights over the cited papers or
third-party benchmarks. Source support never implies the source is correct.
