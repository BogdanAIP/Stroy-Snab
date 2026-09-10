---
name: code-review
description: Fresh independent semantic review of an exact Stroy-Snab PR head before merge, including correctness, data leakage, dependency justification, evaluation integrity, procurement matching safety and action authority.
metadata:
  version: "1.0"
  project: "Stroy-Snab"
---

# Independent Code Review

Run in a fresh ordinary-ChatGPT context when `AGENTS.md` requires terminal review.

## Input identity

Require:

```text
REVIEW_REQUEST_V1
repository=BogdanAIP/Stroy-Snab
pr_number=<n>
base_sha=<40 hex>
head_sha=<40 hex>
review_policy_ref=<immutable accepted ref>
```

If identity is missing or live PR refs differ, return `ABSTAIN` or `STALE`; never silently review another head.

## Boundaries

Reviewer is read-only. It independently fetches live PR metadata, complete diff, governing BASE policy, applicable target docs/skills, tests/evals and relevant evidence. Developer prose and PR claims are leads, not acceptance proof.

## Review priorities

1. concrete wrong extraction/normalization/matching result;
2. false `EQUIVALENT` or unsafe downgrade of required evidence;
3. private/commercial data leakage into public repository/logs/fixtures, including hidden file metadata, hidden sheets/cells, comments/formulas/links, revision data, embedded objects, PDF OCR/text layers, attachments, filenames and ineffective overlay-only redaction;
4. re-identification risk from combinations of otherwise permitted fields;
5. wrong lifecycle links, units, quantities, identity or provenance;
6. stale supplier/offer facts presented as current;
7. consequence-bearing duplicate/retry/authorization failures;
8. dependency added without accepted research/evidence or with incompatible license;
9. eval leakage, contaminated holdout, misleading aggregate metric or baseline omission;
10. architecture duplication of CAP/external-system responsibility;
11. concrete test/eval gaps that permit an introduced defect.

Do not report style/taste/speculative future work as findings.

## Finding discipline

Every candidate finding must survive an attempt to disprove it by reading callers, schemas, guards, tests/evals and governing contracts.

Reported finding:

```text
severity=P0|P1|P2|P3
location=<file/symbol/range>
introduced_by=<exact changed behavior>
failure_mechanism=<concrete case>
consequence=<observable procurement/data/safety failure>
evidence=<code/test/policy/runtime>
falsification_attempt=<what could have disproved it>
why_it_survives=<reason>
```

Weak suspicions are dropped.

## Terminal result

Return one of:

- `PASS` — zero surviving findings;
- `FAIL` — one or more concrete findings;
- `STALE` — reviewed identity no longer matches;
- `ABSTAIN` — governing identity/evidence cannot be resolved.

Bind result to exact `repository, PR, BASE_SHA, HEAD_SHA, review_policy_ref, skill_version`.

A material fix moving HEAD invalidates the prior terminal review.
