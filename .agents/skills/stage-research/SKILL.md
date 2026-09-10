---
name: stage-research
description: Research gate before a new Stroy-Snab stage, major domain capability, external component adoption, data model change, supplier/procurement integration, or consequence-bearing authority change.
metadata:
  version: "1.0"
  project: "Stroy-Snab"
---

# Stage Research

Use before production implementation of a new roadmap stage or material architecture/component decision.

## Hard rule

Finish with exactly one decision: `PROCEED | NARROW | DEFER`.

`DEFER` blocks implementation. `NARROW` permits only its explicit scope.

## Required sequence

1. Resolve live repository/PR state.
2. Read `PRODUCT`, `CURRENT_STATE`, `ROADMAP`, relevant `ARCHITECTURE`, `REUSE_BASELINE`, data/eval policy.
3. State the exact user/product outcome and what is out of scope.
4. Identify current baseline and measured failure/gap. Do not start from a preferred library.
5. Check `REUSE_BASELINE`: for every touched role choose `KEEP | REUSE_MORE | ADAPT | REPLACE | DEFER | REJECT`.
6. Research strong current candidates using official docs/source, licenses, maintenance/release history, tests/benchmarks and issue/failure evidence.
7. Compare at least three materially different approaches when credible alternatives exist, including doing less/no new component.
8. Separate `problem evidence` from `solution evidence`.
9. Define the smallest reproducible experiment and baseline comparison.
10. Define metrics from `EVALUATION_POLICY.md`, dataset identity and falsification criteria.
11. For private data, prove the experiment does not commit/leak raw corpus content.
12. For consequence-bearing actions, include ambiguity/retry/reconciliation failure matrix and CAP ownership boundary.

## Procurement-specific questions

When the stage touches item matching/substitution, explicitly answer:

- which attributes are critical vs optional?
- what evidence can establish `EXACT`?
- what additional authority establishes `EQUIVALENT`?
- what forces `CANDIDATE`, `REJECT`, or `UNKNOWN`?
- how is false-equivalent risk measured?

When the stage touches an ERP/PIM/provider, answer:

- what native state remains owned by the external system?
- can Stroy-Snab integrate through a narrow replaceable adapter?
- why is browser interaction needed if an official API exists?

## Brief output

A Stage Research Brief must contain:

- Stage goal
- Current baseline/gap
- Reuse lineage decisions
- Candidate approaches and licenses
- Failure lessons
- Alternatives comparison
- Experiment design + datasets + metrics
- Security/data boundary
- Architecture decision: `PROCEED | NARROW | DEFER`
- Explicit deferred/rejected work
- Acceptance ladder

A material architecture change discovered during implementation invalidates the brief and requires research re-entry.
