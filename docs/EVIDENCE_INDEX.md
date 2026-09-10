# Evidence Index

Канонический индекс только принятых/релевантных доказательств. Не использовать как журнал чатов.

## Stage 0 — accepted

Foundation acceptance identity:

- bootstrap BASE: `2397b487a3e7b4a0c8b7599f69c72e600ee9f6c2`;
- reviewed HEAD: `a0f400409a37190e8621a2e59e2e1d02ed000a2b`;
- independent semantic review: `PASS`, surviving findings `0`, review skill v1.0;
- merge commit on `main`: `44610bd33eff346f21414fc5b4513195682cbb76`;
- hosted CI/status checks: none existed for the documentation-only bootstrap head.

The exact-head PASS was recorded in PR #1 conversation before merge without moving HEAD.

## Stage 1P — research

Research brief: `docs/research/STAGE1P_ANONYMIZATION_RESEARCH.md`.

Decision: `NARROW`.

Accepted research direction for experiment:

- allowlist reconstruction instead of generic in-place sanitization as default;
- dual derivative model (safe semantic/native derivative plus visual derivative only where needed);
- format-aware independent leak checking;
- `openpyxl` as XLSX read/inspection candidate;
- `XlsxWriter` as clean XLSX reconstruction candidate;
- `pikepdf` as PDF inspection/defense-in-depth candidate, not proof of complete redaction;
- `pypdfium2` as permissive PDF-rendering candidate;
- CPU-first local target: Windows 11 x64, 16 GB RAM, no mandatory CUDA/NVIDIA.

These component choices are authorized for Stage 1P experiment only; production adoption remains subject to Stage 1P acceptance.

## Stage 1P — provisional experiment evidence

PR #2 BASE is accepted `main` commit `44610bd33eff346f21414fc5b4513195682cbb76`.

### Executable prototype

Implemented in PR #2:

- allocator-owned fixed-width neutral public identifiers with no caller-supplied ordinal, dense document numbering per prefix, and Stage 1P real-derived case limited to `CASE_0001`;
- strict manifest validation with no reverse/private identity fields and exact format/path binding;
- clean XLSX reconstruction from allowlisted values rather than source-container copying;
- fail-closed handling of writer truncation/drop/merge conditions;
- strict public-XLSX internal-member allowlist, case-ambiguous duplicate rejection and bounded ZIP/XML resource checks;
- inert PDF-page and image derivatives using pixel rendering/re-encoding;
- format-aware XLSX/JSON/image leak checks;
- fail-closed visual-review state;
- generic and checksum-aware identifier detection, including unlabeled valid INN/OGRN values;
- one-shot/generator denylist inputs frozen before multi-part scanning;
- leak reports that do not echo private matched values;
- hosted CI on Linux Python 3.11/3.13 and Windows Python 3.13;
- reproducible synthetic resource benchmark.

Pre-freeze synchronized head `69a63f91d89d5efb14b539496567c0ffe1f545ff` passed hosted workflow run `34495176448` across all three jobs. Windows Python 3.13 reported **38 tests passed** before this evidence-only synchronization commit. The next candidate HEAD must pass hosted CI again because changing this file moves HEAD.

### Bounded private smoke test

Opaque private sample id: `PRIVATE_SMOKE_2026-09-10_B`.

No raw source names, identifiers, cell values or reverse mapping are recorded here.

Sample shape and result:

- XLSX: **4/4 PASS**;
- PDF with text layer: **4/4 PASS**, 7 rendered pages;
- JPG/image: **4/4 PASS**;
- represented lifecycle roles include `REQUEST`, `OFFER_OR_INVOICE`, `UPD_OR_DELIVERY`, `INCOMING_CONTROL`;
- all candidate derivatives remained private and were discarded after the bounded run;
- no GPU/CUDA required.

Observed in the isolated private Linux environment:

- runtime: approximately **2.7 s**;
- process peak RSS: approximately **258 MB**;
- temporary tree: approximately **17.5 MB**.

These are aggregate engineering metrics only; no confidential content is represented by them.

### Hosted resource benchmark

CI benchmark shape:

- rebuilt XLSX with 5001 rows;
- 3-page PDF render path;
- JPG -> fresh PNG path;
- no GPU/CUDA.

On synchronized head `69a63f91d89d5efb14b539496567c0ffe1f545ff`, hosted Windows / Python 3.13 run `34495176448` measured:

- elapsed: **0.749 s**;
- peak working set: **109.9 MB**;
- temporary tree: **0.6 MB**;
- tests: **38 passed**.

Earlier exact implementation head `0749848e35d0bd76d836e43091a176a3cb402a2e` produced the same resource envelope on Windows and Linux, confirming that the measurement is stable across the subsequent safety/documentation hardening.

This provides cross-platform resource-envelope evidence and a large margin relative to the 16 GB CPU-first product target. It does not claim to reproduce the user's exact Windows 11 hardware/software load.

### First public anonymized-real fixture

Public case: `CASE_0001` / `REQUEST_0001`.

The fixture is a newly reconstructed minimal XLSX derivative, not a modified copy of the private source container.

- repository path: `data/fixtures/documents/anonymized-real/CASE_0001/REQUEST_0001/document.xlsx`;
- Git blob: `14a12b8cf6b1f9f5595c281804bcf281e4e5a0a5`;
- byte size: `5666`;
- SHA-256: `6530afe58465fce23e77ba1f023331dd49aa54bca95fc2da5663f8bc8132096a`;
- automated format-aware leak check: **PASS**;
- structured private-side spot-check of retained public content and excluded source identity fields: **PASS**;
- CI validates the manifest, exact declared derivative set and XLSX internals.

The fixture intentionally retains only a minimal technically useful procurement-line fragment and neutral structure. It contains no reverse mapping to its private source.

### Real visual derivative publication decision

Real PDF/JPG visual derivatives remain **private-only in Stage 1P**.

Rationale:

- real visual layout preserves more potentially identifying structure than the minimal rebuilt XLSX fixture;
- the visual pipeline is already exercised on private real documents and public synthetic regressions;
- Stage 1A has not yet demonstrated that publishing real visual layout is required for an extraction benchmark.

If Stage 1A demonstrates a measured need, public real visual fixtures require a new explicit data-safety review and completed manual visual review before commit.

## Stage 1P — independent review remediation

A fresh review of former head `ff3c252f2423af76abd647528debc57e87a848e8` returned `FAIL` with two surviving findings:

- P2: the former `neutral_id(prefix, ordinal)` API and syntactic validator could accept source-derived numeric payloads such as a date/document number;
- P3: benign upload-probe placeholder files had been deleted from the final tree but remained in reachable PR history.

Remediation completed on the development branch:

- P2: public generation now uses `NeutralIdAllocator`, which accepts no caller-supplied ordinal; IDs are fixed-width 4-digit sequences, document IDs must be dense per prefix, real-derived Stage 1P manifests are limited to `CASE_0001`, and low-level syntax parsing is not exported as a public neutrality guarantee. Regression tests cover `CASE_2026`, `CASE_20260910`, `INVOICE_5606`, and skipped dense ordinals.
- P3: the Stage 1P branch was rewritten so its reachable PR history contains one commit whose parent is accepted BASE `44610bd33eff346f21414fc5b4513195682cbb76`; the former benign placeholder commits are no longer in the PR commit chain.

The first clean-history remediation head `06ec361133d3499f93fc74bdb63dbaccab6e7f74` passed hosted workflow `34510372197` across Linux 3.11, Linux 3.13 and Windows 3.13. Each matrix reported **40 tests passed**. Windows benchmark: approximately **0.534 s / 110.2 MB / 0.6 MB**; Linux 3.13: approximately **0.538 s / 110.6 MB / 0.6 MB**. Subsequent API/document hardening moves HEAD and therefore still requires final exact-head CI and a fresh independent review.

## Stage 1P — evidence still required before acceptance

- obtain **SUCCESS** hosted CI on the final candidate HEAD after this final canonical synchronization;
- freeze exact BASE/HEAD without further repository changes;
- obtain fresh independent exact-head semantic review using accepted BASE code-review skill v1.0;
- if review causes any material code/doc fix, repeat exact-head CI and review on the new HEAD.

A future smoke-run on the user's exact Windows 11 machine is useful confirmation of the product target but is not represented as already completed evidence and is not required to establish that the current mandatory stack has a large 16 GB resource margin.

## Future research inputs

The following must be independently rechecked before adoption in their stages:

- CAP as existing external execution/verification project;
- ETIM as candidate technical product classification;
- ERPNext/Frappe/frappectl as procurement/data-plane candidates;
- OpenConstructionERP as construction-specific candidate;
- Pint/RapidFuzz/Sentence Transformers/Splink as candidate primitives;
- Docling/PaddleOCR and other document-understanding systems for Stage 1A;
- official Russian classification/standards/counterparty/supplier sources for later stages.

## Evidence record format

For accepted stage/experiment evidence record:

- stage / experiment id;
- immutable code/ref identity;
- dataset identity (`public`, private opaque corpus id, holdout id);
- configuration/model/component versions;
- metric artifact/report locator;
- review/CI identity where applicable;
- decision (`PROCEED | NARROW | DEFER` or adoption result).

Private documents and confidential values never appear in this file.
