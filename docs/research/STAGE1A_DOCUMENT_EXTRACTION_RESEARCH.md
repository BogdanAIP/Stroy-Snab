# Stage 1A — Document Extraction Research

Date: 2026-09-16

## Stage goal

Build the smallest reproducible document-extraction path that turns safe procurement documents into canonical procurement lines while preserving source provenance.

Initial canonical line:

```text
document_id
document_role
item_name_raw
unit_raw
quantity
source_locator
```

Commercial fields such as article, brand, price, VAT and line total are deliberately deferred until the minimum line-extraction baseline is measured. They may be added by a bounded follow-up experiment without re-reading raw documents from scratch.

## Current baseline / gap

Accepted Stage 1P provides a safe anonymization boundary and the first public anonymized-real XLSX fixture, but Stroy-Snab has no extraction implementation yet.

Private corpus evidence already shows a mixed procurement corpus with XLSX, PDF and image documents. Google Drive is the raw private source; raw Drive/Library/ZIP files remain outside GitHub.

The immediate gap is therefore not “find the strongest OCR model”. It is:

1. reliably extract rows from native XLSX without OCR;
2. define a source-locator contract;
3. establish a simple baseline that later PDF/image extractors must beat;
4. keep the mandatory local path CPU-first and bounded.

## Reuse lineage decisions

| Role | Existing/candidate | Decision | Reason |
|---|---|---|---|
| XLSX read baseline | openpyxl 3.1.5 | ADAPT | Already present in Stage 1P test tooling; native workbook access; no OCR/model cost. |
| Complex PDF/document parser | Docling | DEFER to PDF/image experiment | Strong unified document model and table/layout support, but unnecessary for the first XLSX baseline. |
| OCR/layout pipeline | PaddleOCR / PP-StructureV3 | DEFER to PDF/image experiment | Strong OCR/layout path with CPU support, but model stack is not justified for native XLSX. |
| Custom OCR/parser framework | new Stroy-Snab implementation | REJECT now | No measured gap justifies duplicating mature parsers. |
| Do nothing / manual extraction | spreadsheet/manual handling | KEEP only as gold/reference | Useful for adjudication, not scalable as product behavior. |

## Candidate approaches

### A. Native format parsing first

Use openpyxl in read-only/data-only mode for XLSX and deterministic header/row extraction.

Pros:
- smallest dependency and resource footprint;
- preserves exact cell values and worksheet locators;
- avoids OCR errors on native spreadsheets;
- easy to test on Windows/CPU.

Limits:
- workbook layout can be irregular;
- merged/multi-row headers need explicit handling;
- cannot solve scanned PDF/JPG.

License/version reference:
- openpyxl 3.1.5, MIT/Expat family; current PyPI release remains 3.1.5.
- https://pypi.org/project/openpyxl/

### B. Docling unified parsing

Docling supports PDF, DOCX, PPTX, XLSX, images and a unified document representation. Current project metadata in September 2026 reports Docling/Docling-slim 2.12x and MIT licensing; Windows and CPU execution are supported.

Pros:
- unified representation;
- strong PDF layout/table support;
- useful later for mixed-format normalization.

Limits:
- larger dependency/model surface than native XLSX;
- using it for XLSX before measuring a native baseline would hide whether the extra complexity is needed.

Sources:
- https://github.com/docling-project/docling
- https://docling-project.github.io/docling/

### C. PaddleOCR / PP-StructureV3

PaddleOCR 3.7.0 (2026-06-11) includes PP-OCRv6 and PP-StructureV3; the project is Apache-2.0 and supports CPU inference.

Pros:
- strong OCR and document-layout capability;
- suitable for scans, photographs and difficult PDFs;
- explicit CPU path.

Limits:
- model/runtime cost is unnecessary for native XLSX;
- model accuracy on Russian construction procurement layouts must be measured on our corpus rather than inferred from public benchmarks.

Sources:
- https://github.com/PaddlePaddle/PaddleOCR
- https://github.com/PaddlePaddle/PaddleOCR/blob/main/docs/version3.x/pipeline_usage/PP-StructureV3.en.md

## Problem evidence vs solution evidence

Problem evidence:
- accepted repository state has anonymization but no extraction path;
- the corpus contains many XLSX requests and mixed PDF/JPG commercial documents;
- Stage 1A must run on a Windows/16 GB/CPU-first baseline;
- exact row provenance is required for later lifecycle linkage.

Solution evidence:
- native XLSX can be parsed without OCR;
- Docling and PaddleOCR are mature active alternatives for the later mixed-format experiment;
- no evidence yet shows that either heavy parser improves XLSX extraction enough to justify becoming mandatory.

## Failure lessons / expected failure modes

Native XLSX baseline can fail on:
- multi-row headers;
- merged headers where labels are split across cells;
- units embedded inside item text;
- multiple procurement tables on one sheet;
- formulas whose cached values are absent;
- hidden semantic structure not represented as rows.

The baseline must fail closed when it cannot identify a line table; it must not hallucinate procurement rows.

OCR/layout approaches can additionally fail on:
- decimal/comma confusion;
- column drift;
- Cyrillic/Latin token confusion;
- page/table fragmentation;
- false row merges.

## Smallest reproducible experiment

Public dataset:
- `CASE_0001 / REQUEST_0001` anonymized-real XLSX accepted by Stage 1P;
- synthetic regression workbooks covering header variants, formatted quantities, totals and unsupported layouts.

Private control dataset:
- a bounded opaque sample of raw private XLSX documents may be evaluated locally;
- only aggregate counts/accuracy/resource metrics may be recorded;
- no raw filenames, company identities, document numbers, cell values or reverse mappings enter GitHub.

Experiment:
1. detect a procurement table from header semantics;
2. extract `item_name_raw`, `unit_raw`, `quantity`;
3. attach `document_id`, `document_role`, and cell-based `source_locator`;
4. measure runtime and extracted line count on the public fixture;
5. add human gold labels before claiming extraction accuracy.

## Metrics and falsification criteria

Required Stage 1A metrics from `EVALUATION_POLICY.md`:
- line detection precision/recall;
- exact/normalized accuracy for item name, unit and quantity;
- document-level perfect extraction rate;
- runtime and peak-resource envelope for mandatory local paths.

This first PR establishes deterministic behavior and benchmark plumbing, not a final accuracy claim.

Falsify the native baseline as the default XLSX path if:
- it cannot represent the accepted public fixture without workbook-specific hardcoding;
- private control shows systematic layout failure that a mature alternative materially fixes;
- resource or compatibility behavior violates the CPU-first Windows target.

## Security / data boundary

- raw Google Drive, Library and ZIP documents are read-only private source corpus;
- no raw file is committed;
- public CI consumes only accepted repository-safe fixtures;
- extraction output must not weaken Stage 1P anonymization;
- benchmark logs for private runs contain only aggregate metrics and opaque dataset ids.

## Architecture decision

**NARROW**

Authorized scope:
- add a deterministic native-XLSX extraction experiment;
- use openpyxl only as an experiment/runtime-extra dependency, not a mandatory production dependency;
- add synthetic regression tests and a public-fixture benchmark;
- define the canonical Stage 1A line contract and source locator;
- research Docling/PaddleOCR in the next bounded PDF/image experiment.

Not authorized yet:
- production adoption of Docling/PaddleOCR;
- OCR/VLM as a mandatory dependency;
- supplier discovery;
- item equivalence/matching;
- Google Drive write operations;
- raw corpus publication;
- ERP/CAP consequence-bearing integration.

## Acceptance ladder

1. branch contains research brief + bounded XLSX baseline only;
2. deterministic tests pass on Linux/Windows CI;
3. public anonymized-real fixture processes without raw-data leakage;
4. benchmark output records count/runtime without printing procurement contents;
5. private XLSX control may be run separately with aggregate-only evidence;
6. exact-head independent review is required before merge;
7. Stage 1A remains open after this PR: PDF/JPG extraction and gold accuracy benchmark still require separate work.
