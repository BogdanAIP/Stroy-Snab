## Goal

<!-- One bounded product/engineering outcome. -->

## Stage / authority

- Stage:
- Applicable research brief / decision:
- BASE_SHA:
- HEAD_SHA:

## Scope

<!-- Changed capabilities/data/components. -->

## Explicitly out of scope

<!-- Prevent scope creep. -->

## Reuse / dependencies

<!-- New external components? REUSE/ADAPT decision and license evidence. -->

## Data safety

- [ ] No raw private procurement documents, raw archive members or secrets committed.
- [ ] Every fixture is labelled `anonymized-real | synthetic | minimal-redacted | public-source`.
- [ ] Any `anonymized-real` fixture passed the full Anonymization Gate from `docs/DATA_POLICY.md`, including hidden metadata/internal-file checks; visual masking alone is not accepted redaction.

## Tests / evals

<!-- Commands, dataset identities, metrics and baseline comparison. -->

## Critical procurement safety

- [ ] No change can silently promote `CANDIDATE` to `EQUIVALENT` without accepted evidence/rules.
- [ ] Unit/quantity/provenance behavior is tested if touched.
- [ ] Consequence-bearing actions reconcile `UNKNOWN` before retry if touched.

## Evidence / acceptance

<!-- CI, eval report, physical/integration/anonymization evidence when applicable. -->

## Independent review

Terminal exact-head review required according to `AGENTS.md` and `.agents/skills/code-review/SKILL.md`.
