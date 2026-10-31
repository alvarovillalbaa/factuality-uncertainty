# Decisions, assumptions, and unresolved choices

**Status:** proposed defaults for spec completeness. These are not approvals or established facts. Exact source language is preserved in `sources/00-notion-source-snapshot.md`.

| ID | Issue | Proposed default or treatment | Resolve before |
|---|---|---|---|
| DEC-01 | Who owns the portfolio? | Treat as personal research; source ancestor is the personal page. Do not infer Clous product scope from workspace URL. | Repository organization selection |
| DEC-02 | What does the present request authorize? | Produce a ZIP of specifications. Preserve the source's eventual repo/research intent as future scope. | Any repository creation or study execution |
| DEC-03 | How many projects? | Split solar capture and storage; retain all other named topics; add research-contracts and decision-runtime. | Initial repository setup |
| DEC-04 | What do the pasted table scores mean? | Preserve the numbers in the source snapshot; do not infer weights, rankings, column meanings, or priority. | Any score-based prioritization |
| DEC-05 | What is “Jev”? | Unknown provider/model/system identity. Reserve an adapter slot without inventing a provider, API, or capability. | Adding that experimental arm |
| DEC-06 | Which models and harnesses? | Select accessible versions at protocol freeze; record effective IDs, policies, costs, and limitations. Compare model and harness separately. | AI run budget and protocol freeze |
| DEC-07 | “Air-taxi airships” versus eVTOL | Treat eVTOL as a working comparative baseline because the page points to eVTOLs; retain lighter-than-air interpretation as a separate architecture fork. | AE-02 detailed mission and structural sizing |
| DEC-08 | Autonomous/electric versus alternative fuels | Apply autonomous/electric to the default civil-aircraft research branch. AE-03 compares full propulsion architectures; AE-08 is an explicit fluid/cryogenic branch. | AE-03/AE-08 system boundary freeze |
| DEC-09 | Civil aviation versus reusable launch context | Durability/reflight/feed/slosh language may refer to other vehicles. Keep the initial artifacts civilian and technology-specific; do not silently mix rocket and aircraft results. | AE-05/AE-07/AE-08 evidence selection |
| DEC-10 | Solar “absorption” | Separate optical absorption, conversion efficiency, temperature losses, and annual useful yield. Define the primary objective explicitly. | EN-01 experiment design |
| DEC-11 | Storage “efficiency” | Treat mass/volume-specific usable energy and round-trip efficiency as distinct metrics under fixed duty cycle/system boundary. | EN-02 comparator selection |
| DEC-12 | Physical experimentation | Begin with simulation and existing evidence; physical tests are separately scoped extensions with appropriate equipment and procedures. | Any new physical experiment |
| DEC-13 | Numeric targets | All numbers in proposed experiments are design assumptions, fixture values, or explicitly cited reference facts; tune justified thresholds after pilot and before holdout analysis. | Confirmation |
| DEC-14 | Data, rights, and representativeness | Sources are candidates until acquired and their license, quality, use rights, version, and applicability are checked. | Dataset release or training |
| DEC-15 | Repo ownership and licensing | Slugs are proposals; organization, visibility, code/data licenses, publication rights, and maintainers are unassigned. | Remote repo creation/publication |
| DEC-16 | Time, budget, and staffing | Use dependency gates, not invented delivery dates; estimate after pilot. | Paid runs or project commitments |
| DEC-17 | Independent usefulness versus commercial success | Each repo has a standalone deliverable and potential user. Sellability is a hypothesis requiring customer evidence. | Product investment |
| DEC-18 | Acceptance versus improvement | A reproducible, well-powered null result can finish research; deployment thresholds remain separate. | Research and product release decisions |
| DEC-19 | Protocol status | Specs and templates are proposed; no external preregistration has occurred. | Confirmatory study start |
| DEC-20 | Legal/assurance scope | Regulatory references orient later scoping; neither specs nor simulation imply certification, compliance, or flight authorization. | Concrete operational deployment |

## Decision-record format

For a resolved item, record the source or owner decision, date, rationale, considered alternatives, affected projects, downstream contract changes, and evidence that would cause reconsideration. Do not overwrite the original ambiguity: append the resolution and its provenance.

## Decisions that can wait

The unknown “Jev” identity does not block classical energy benchmarks. The airship/eVTOL fork does not block the sensing-aircraft project. Choosing a GitHub organization does not block writing a protocol. Choosing a paid model does not block runtime testing with mocks. This package is intentionally complete enough to begin those independent steps while keeping consequential choices visible.
