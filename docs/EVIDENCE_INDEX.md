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

## Stage 1P — accepted

Terminal acceptance:

- accepted BASE: `44610bd33eff346f21414fc5b4513195682cbb76`;
- reviewed Stage 1P HEAD: `a6360a18c15efb4db84b3bedf8b1bfae4cbc4ee2`;
- independent exact-head semantic review: `PASS`, surviving findings `0`, accepted code-review skill v1.0;
- final hosted workflow referenced by PR #2: run `34814297721`, Linux 3.11/3.13 and Windows 3.13 all SUCCESS with 43 tests per matrix;
- merge commit on `main`: `15df096e5f8aacca56ed78c04f7b470d6a61fea6` on 2026-09-14.

Stage 1P is no longer an open gate. Stage 1A may proceed under a new research decision.

## Stage 1A — research

Research brief: `docs/research/STAGE1A_DOCUMENT_EXTRACTION_RESEARCH.md`.

Decision: `NARROW`.

Authorized first experiment:

- deterministic native XLSX extraction using openpyxl;
- canonical fields: document id/role, raw item name, raw unit, quantity, source locator;
- synthetic regression tests plus accepted public anonymized-real fixture;
- Docling and PaddleOCR/PP-StructureV3 remain deferred candidates for a separate PDF/image experiment;
- no supplier discovery, matching/equivalence, raw-corpus publication or consequence-bearing integration.

## Stage 1A — provisional XLSX experiment evidence

PR #3 BASE: `15df096e5f8aacca56ed78c04f7b470d6a61fea6`.

Historical implementation head:

`96f9690eb37196ad414f002d90f98dab534415a4`.

Hosted workflow run `35101156575` / run #74: **SUCCESS**.

Matrix results on that historical implementation head:

- Ubuntu / Python 3.11: **49 tests passed**; public Stage 1A benchmark: 1 XLSX document, 1 extracted line, ~3.273 ms;
- Ubuntu / Python 3.13: tests + Stage 1A benchmark SUCCESS;
- Windows / Python 3.13.15: **49 tests passed**; public Stage 1A benchmark: 1 XLSX document, 1 extracted line, ~4.942 ms.

Benchmark safety:

- dataset: accepted public `anonymized-real` corpus;
- current public sample: `CASE_0001 / REQUEST_0001`;
- benchmark logs record only aggregate document/line counts and runtime;
- `content_logged=false`;
- no raw Drive/Library/ZIP document is a CI dependency.

Observed public-fixture lesson:

- the first baseline failed because quantity and unit may share one cell;
- the implementation added a generic combined quantity/unit path rather than fixture-specific constants.

This is provisional experiment evidence only. It is **not** an accuracy claim and does not certify the current PR HEAD.

## Stage 1A — independent review #1

Reviewed exact identity:

- repository: `BogdanAIP/Stroy-Snab`;
- PR: `#3`;
- BASE: `15df096e5f8aacca56ed78c04f7b470d6a61fea6`;
- reviewed HEAD: `370be6763465b608dc032a97580905e31ea8d545`;
- review policy ref: accepted BASE `15df096e5f8aacca56ed78c04f7b470d6a61fea6`;
- skill: `code-review` v1.0;
- terminal result: **FAIL**;
- surviving findings: **5**.

Accepted remediation targets from the review:

1. reject ambiguous quantity syntax instead of converting a numeric prefix plus arbitrary remainder into quantity/unit;
2. prevent `Количество мест` or multiple quantity-like columns from silently winning over the true line quantity;
3. preserve a unit recovered from a quantity cell when an explicit unit cell is blank/whitespace;
4. fail closed on formulas/partial extraction instead of silently dropping candidate rows;
5. keep canonical evidence text time-stable: current exact-head CI/review state must be resolved live rather than inferred from a stale statement in this file.

Current branch remediation implements these targets and adds deterministic regressions for the concrete reviewed cases.

No terminal acceptance is recorded here yet. The exact current PR HEAD, hosted CI state and repeated independent review must be resolved from live GitHub immediately before merge. A future `PASS` must be bound to that exact frozen HEAD.

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
