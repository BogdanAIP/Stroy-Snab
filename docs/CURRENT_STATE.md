# Current State

Дата состояния: 2026-09-16.

## Live repository state

- default branch: `main`;
- current `main` HEAD at PR #5 start: `1b0d6086d08855e84e859a715f1363bf529b3f11`;
- Stage 0 accepted and merged via PR #1;
- Stage 1P accepted and merged via PR #2 on 2026-09-14;
- Stage 1A native XLSX baseline accepted and merged via PR #3 on 2026-09-16;
- Stage 1A XLSX evaluation harness accepted and merged via PR #4 on 2026-09-16;
- active work: PR #5 branch `stage1a/unlabeled-adjacent-unit`;
- current roadmap stage: **Stage 1A — Document extraction/evaluation**.

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

## Accepted PR #3 baseline

PR #3 `Stage 1A: establish native XLSX extraction baseline` is merged in `main` as:

`ea67a647d31bf3e8238136f62d1c550aa1a26e76`

Accepted baseline includes:

1. Stage 1A research brief;
2. deterministic native XLSX extractor;
3. fail-closed unsupported/ambiguous-layout behavior;
4. cell-based provenance locators;
5. synthetic XLSX regression tests;
6. public anonymized-real benchmark;
7. optional `stage1a` openpyxl dependency;
8. Linux/Windows hosted CI path.

Final pre-merge candidate was `79724de933958ba6dde0f3e2b4ac1c01accfdf02`; hosted workflow #92 passed all required matrices and confirmed review findings were remediated before merge.

## Accepted PR #4 implemented scope

PR #4: `Stage 1A: add XLSX extraction evaluation harness` is accepted and merged.

Accepted scope:

- public anonymized-real gold labels for accepted `CASE_0001 / REQUEST_0001`;
- E1A line detection precision/recall;
- item/unit exact and normalized accuracy;
- quantity/role exact accuracy;
- strict-line accuracy;
- document-perfect rate;
- aggregate-safe runner suitable for bounded private XLSX control;
- CI execution and regression tests.

No PDF/JPG extraction, OCR/VLM adoption, supplier discovery, matching/equivalence, lifecycle linkage implementation or raw corpus publication is part of PR #4.

## Accepted PR #4 evaluation harness

PR #4 `Stage 1A: add XLSX extraction evaluation harness` is merged in `main` as:

`1b0d6086d08855e84e859a715f1363bf529b3f11`

Final reviewed candidate:

`2c54894fbb17e1904881c0c846eec86404b3601d`

Terminal independent review: `PASS`, surviving findings `0`.

Accepted harness provides reproducible E1A line/field/document metrics plus aggregate-safe private-control execution.

## Active PR #5 scope

Measured private-control gap from `PRIVATE_CONTROL_0001`:

- 4 documents / 28 gold lines;
- line detection, item and quantity accuracy: 1.00;
- unit exact accuracy: 24/28 = 0.8571;
- document-perfect: 3/4;
- one real XLSX layout stores valid unit values in the blank-header column immediately right of quantity.

PR #5 tests one explicit structural rule only:

- no explicit unit header may exist;
- candidate unit column must be immediately right of quantity;
- its header must be blank;
- at least two procurement rows must support the inference;
- every considered item row must have a non-empty unit token from the bounded allowlist `м | шт`;
- quantity cells carrying their own unit suffix block the structural inference;
- mixed/comment/non-adjacent/single-row cases remain uninferred.

This is deliberately narrower than general unit normalization and does not add supplier discovery, matching, lifecycle linkage, PDF/OCR or other Stage 1 capabilities.

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

## PR #4 evaluation result

Public anonymized-real evaluation on the accepted fixture is reproducible in hosted CI and reports perfect metrics on the single public document.

Bounded private control `PRIVATE_CONTROL_0001` used 4 raw XLSX request documents / 28 human-adjudicated gold lines outside GitHub.

Aggregate private result:

- line detection precision/recall: 1.00 / 1.00;
- item exact accuracy: 1.00;
- quantity exact accuracy: 1.00;
- unit exact accuracy: 0.8571 (24/28);
- strict line accuracy: 0.8571;
- document-perfect rate: 0.75 (3/4);
- extraction failures: 0.

The measured gap is structural rather than semantic: one real template contains unit values in an adjacent column whose header is blank. The current baseline intentionally does not guess that column, so item/quantity extraction remains correct while four units stay unknown.

This gap is **not fixed inside PR #4**. It is the next bounded Stage 1A extraction experiment after PR #4 acceptance.

## PR #4 independent review #1 — FAIL

Fresh independent review of exact head `8b241a9300af24f96badd1e427254e03d7b46b65` returned `FAIL` with one P2 finding: the aggregate-safe runner echoed any syntactically allowed free-form dataset label, so a private ASCII filename/company identifier could be logged verbatim.

Remediation:

- free-form `--dataset-label` is removed;
- CLI now accepts only reviewed internal `--dataset-key` values;
- output dataset ids come from a code-owned registry;
- current private control key `private-0001` maps to opaque `PRIVATE_CONTROL_0001`;
- unknown keys fail closed as `INVALID_DATASET_KEY` without echoing the supplied value;
- regressions cover space/slash input, filename-shaped ASCII and company-shaped ASCII.

## PR #4 independent review #2 — FAIL

Repeat independent review of exact head `cb02f96d37b7957bfd53ad1c106a57a06a134b75` returned `FAIL` with two P2 stderr-leakage findings:

- removed legacy `--dataset-label` still leaked its supplied value through default argparse error output before safe handling;
- `openpyxl` warnings could include workbook-controlled private text and reach stderr even when extraction exceptions were redacted.

Remediation:

- evaluation CLI now uses a custom parser whose error path raises internally and emits only `INVALID_ARGUMENTS`;
- removed/unknown CLI arguments are never echoed;
- the evaluation body runs inside `warnings.catch_warnings()` with warnings promoted to exceptions;
- workbook/parser warnings therefore become ordinary aggregate extraction failures and cannot write raw warning text to stderr;
- regressions reproduce both the stale `--dataset-label PRIVATE_SUPPLIER_SECRET.xlsx` invocation and a real openpyxl malformed Print_Area warning containing a private worksheet title.

## PR #5 provisional evaluation result

Hosted workflow on implementation/evidence pre-sync head `fae7b576378d7ae0b598b1081f91da4639692f60`:

- run `35140479068` / #108: SUCCESS;
- Ubuntu Python 3.11: 86 tests PASS;
- Ubuntu Python 3.13: 86 tests PASS;
- Windows Python 3.13: 86 tests PASS;
- public anonymized-real benchmark/evaluation unchanged and PASS.

Repeated private control `PRIVATE_CONTROL_0001` on the same 4 documents / 28 gold lines reproduced the accepted PR #4 baseline when the new inference was disabled:

- unit exact: 24/28 = 0.8571;
- strict line: 24/28 = 0.8571;
- document-perfect: 3/4 = 0.75;
- extraction failures: 0.

With the PR #5 rule enabled:

- predicted lines: 28/28;
- line detection precision/recall: 1.00 / 1.00;
- item exact: 1.00;
- quantity exact: 1.00;
- role exact: 1.00;
- unit exact: 28/28 = 1.00;
- strict line: 28/28 = 1.00;
- document-perfect: 4/4 = 1.00;
- extraction failures: 0.

No raw filenames, item values, worksheet titles, paths or reverse mapping are recorded in repository evidence.

## Immediate next action

1. obtain hosted CI for PR #5 across the required Linux/Windows matrix;
2. repeat `PRIVATE_CONTROL_0001` against the new extractor without publishing raw documents;
3. compare unit/strict/document-perfect metrics against the accepted PR #4 baseline;
4. reject or narrow the rule if any previously correct line/item/quantity behavior regresses;
5. if evidence is positive, freeze exact PR #5 BASE/HEAD and run fresh independent exact-head semantic review before merge.

## Stage 1A work still not completed

Stage 1A remains open after PR #4 and the current PR #5 experiment.

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
