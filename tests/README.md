# Tests

Deterministic domain behavior receives ordinary unit/regression tests here.

Document/ML/LLM quality is additionally measured under `evals/`; tests must not substitute for corpus-level evaluation and evals must not substitute for deterministic correctness tests.

CI may use only repository-safe public fixtures: `anonymized-real`, `synthetic`, `minimal-redacted` and approved `public-source` cases that satisfy `docs/DATA_POLICY.md`. Raw Library/Drive/ZIP documents never become CI dependencies.

Any test that consumes `anonymized-real` data must assume the fixture has passed the full Anonymization Gate, including hidden metadata/internal-file checks; tests do not waive or replace that gate.
