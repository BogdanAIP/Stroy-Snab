# Current State

Дата состояния: 2026-09-16.

## Live repository state

- default branch: `main`;
- `main` HEAD at Stage 1A start: `15df096e5f8aacca56ed78c04f7b470d6a61fea6`;
- Stage 0 accepted and merged via PR #1;
- Stage 1P accepted and merged via PR #2 on 2026-09-14;
- active work: draft PR #3, branch `stage1a/document-extraction-baseline`;
- current roadmap stage: **Stage 1A — Document extraction**.

The previous version of this file was stale after PR #2 merge and still described Stage 1P as unaccepted. Live GitHub state is authoritative.

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
3. fail-closed unsupported-layout behavior;
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

## Immediate acceptance ladder

For PR #3:

1. hosted CI must pass on the final exact HEAD on Linux 3.11/3.13 and Windows 3.13;
2. public `CASE_0001` benchmark must process at least one XLSX and extract at least one line without logging procurement contents;
3. deterministic tests must remain green;
4. provisional experiment evidence may then be recorded in `EVIDENCE_INDEX.md`;
5. a bounded private XLSX control may be run separately with aggregate-only reporting;
6. final candidate HEAD requires fresh independent exact-head semantic review using accepted `code-review` skill v1.0;
7. any material fix moving HEAD invalidates the review and requires new CI/review.

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
