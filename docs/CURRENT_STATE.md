# Current State

Дата состояния: 2026-09-16.

## Live repository state

- default branch: `main`;
- `main` HEAD at Stage 1A start: `15df096e5f8aacca56ed78c04f7b470d6a61fea6`;
- Stage 0 accepted and merged via PR #1;
- Stage 1P accepted and merged via PR #2 on 2026-09-14;
- active work: draft PR #3, branch `stage1a/document-extraction-baseline`;
- current roadmap stage: **Stage 1A — Document extraction**.

Live GitHub state is authoritative for the current PR HEAD, CI and review status. This file intentionally does not claim that the current HEAD has passed CI; exact-head acceptance state must be resolved live before review/merge.

## Accepted Stage 1P baseline

Stage 1P established the public/private data boundary required before extraction:

- neutral public case/document ids;
- allowlist XLSX reconstruction;
- PDF/image inert derivative paths;
- format-aware leak checks;
- checksum-aware INN/OGRN detection;
- public manifest validation;
- Linux/Windows CPU-first CI;
- first public anonymized-real fixture `CASE_0001 / REQUEST_0001`.

Accepted merge commit:

`15df096e5f8aacca56ed78c04f7b470d6a61fea6`

Raw procurement documents remain outside the public repository.

## Stage 1A research decision

Research brief:

`docs/research/STAGE1A_DOCUMENT_EXTRACTION_RESEARCH.md`

Decision: **NARROW**.

Authorized first experiment:

- deterministic native XLSX parsing with openpyxl;
- canonical line fields:
  - `document_id`;
  - `document_role`;
  - `item_name_raw`;
  - `unit_raw`;
  - `quantity`;
  - `source_locator`;
- synthetic regression tests;
- public anonymized-real XLSX benchmark;
- CPU-first Linux/Windows execution.

Docling and PaddleOCR/PP-StructureV3 remain Stage 1A candidates for a separate PDF/image experiment. They are not production dependencies.

## Active PR #3 scope

PR #3: `Stage 1A: establish native XLSX extraction baseline`.

Implemented on the candidate branch:

1. Stage 1A research brief;
2. experimental `stroy_snab.experiments.stage1a_xlsx` extractor;
3. fail-closed unsupported/ambiguous-layout behavior;
4. cell-based source locators;
5. synthetic XLSX regression tests;
6. `scripts/benchmark_stage1a.py` against accepted public anonymized-real fixtures;
7. optional `stage1a` dependency group;
8. Linux/Windows hosted CI benchmark step.

No supplier discovery, item equivalence, OCR/VLM adoption, ERP/CAP mutation or raw Drive publication is part of this PR.

## Private source corpus

The private source corpus includes real procurement requests, invoices/commercial documents, UPD/delivery documents, specifications and incoming-control/material-accounting records.

The expanded Google Drive `Stroy-Snab` corpus is the preferred read-only raw source for later private control evaluation. It remains outside GitHub.

Private evaluation may publish only aggregate metrics and opaque dataset ids. No raw filenames, identities, requisites, cell values or reverse mappings may enter repository evidence.

## Prior provisional XLSX evidence

Implementation head `96f9690eb37196ad414f002d90f98dab534415a4` passed hosted workflow run `35101156575` / run #74:

- Ubuntu Python 3.11: 49 tests PASS; public XLSX benchmark 1 document -> 1 line, ~3.273 ms;
- Ubuntu Python 3.13: tests and benchmark PASS;
- Windows Python 3.13.15: 49 tests PASS; public XLSX benchmark 1 document -> 1 line, ~4.942 ms;
- benchmark logs contained aggregate counts/runtime only and reported `content_logged=false`.

This is historical provisional experiment evidence only. It does not certify the current PR HEAD.

## Independent review #1 — FAIL and remediation

Fresh independent review of exact head

`370be6763465b608dc032a97580905e31ea8d545`

returned `FAIL` with 5 surviving findings:

- P1: permissive quantity parsing could convert ambiguous values such as dates/dimensions/punctuated numbers into a successful quantity + garbage unit;
- P1: first-match header selection could choose `Количество мест` instead of the true line quantity;
- P2: a whitespace-only explicit unit cell could erase a unit recovered from the quantity cell;
- P2: formula quantities with no cached value could silently drop rows and produce a partial successful extraction;
- P3: canonical evidence text was stale relative to the exact final CI state.

Remediation in the current branch:

- quantity strings now use a strict numeric grammar and optional unit suffix only after a whitespace boundary; ambiguous forms fail closed;
- quantity header recognition uses a bounded exact allowlist, so `Количество мест` is not a line-quantity header;
- multiple supported candidates for the same header role fail closed as ambiguous;
- an explicit unit overrides the quantity suffix only when non-empty;
- quantity/unit formulas fail closed;
- any candidate item row with a missing or unparseable quantity fails closed instead of being silently skipped;
- regression tests cover the reviewed failure mechanisms;
- canonical docs no longer make a time-sensitive claim that the current HEAD has already passed exact-head CI.

## Independent review #2 — FAIL and remediation

Fresh independent review of exact head

`13dfee3f5b15a98b985f90d422d651e75f27fed5`

returned `FAIL` with 4 surviving findings:

- P1: a merged/multi-row header could still use parent `Количество` as the final quantity column and extract package/place count instead of the actual item quantity;
- P2: any `Итого/Всего` row unconditionally ended worksheet parsing, allowing silent truncation after a subtotal or first table;
- P2: formula item cells were returned as literal Excel expressions because formula guards existed only for quantity/unit;
- P2: broad item-header matching accepted unrelated tables such as `Наименование поставщика | Количество`.

Remediation in the current branch:

- item headers now use a bounded exact allowlist rather than substring matching;
- unit headers are also bounded to explicit supported labels;
- a non-empty row with an empty item cell inside a detected procurement table fails closed, which rejects merged/multi-row header continuations instead of guessing a data column;
- a total marker is treated as terminal only if no later non-empty content appears; later content fails closed rather than producing a partial successful extraction;
- formula item cells fail closed before item-name conversion;
- regression tests cover the merged multi-row header, subtotal followed by more content, formula item and supplier-name-table cases.

## Immediate next action

1. resolve the live PR #3 HEAD after remediation;
2. obtain SUCCESS hosted CI on that exact HEAD across the required Linux/Windows matrix;
3. freeze exact `BASE_SHA / HEAD_SHA`;
4. do not move HEAD after freeze;
5. run a fresh independent read-only semantic review of the new exact HEAD using accepted `.agents/skills/code-review/SKILL.md` v1.0;
6. only a PASS on the exact frozen HEAD permits merge;
7. any material fix requires new CI and another review.

## Stage 1A work still not completed by PR #3

Even if PR #3 is accepted, Stage 1A remains open.

Still required:

- human gold labels for extraction accuracy;
- line detection precision/recall;
- item/unit/quantity exact/normalized accuracy;
- document-level perfect extraction rate;
- PDF/JPG benchmark;
- measured comparison of native parsing vs Docling/PaddleOCR where appropriate;
- bounded private-corpus control evaluation;
- error taxonomy from real extraction failures.

Supplier/offer discovery remains Stage 4 and is not promoted early merely because a supplier database is a useful product goal.
