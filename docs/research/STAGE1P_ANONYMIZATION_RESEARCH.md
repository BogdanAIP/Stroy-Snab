# Stage 1P Research — Anonymization Pipeline

Date: 2026-09-10

BASE: `44610bd33eff346f21414fc5b4513195682cbb76`

Decision: **NARROW**

## Stage goal

Build the smallest reproducible, format-aware pipeline that can transform private real procurement documents into public `anonymized-real` derivatives without known visible or hidden identifying data, while preserving enough layout and commodity content for Stage 1A/1B evaluation.

The target local runtime is Windows 11 x64, **16 GB RAM, CPU-first, no mandatory discrete GPU or CUDA**. GPU acceleration and cloud/VLM fallbacks may be optional, never required for the core path.

## Current baseline / gap

Accepted Stage 0 already requires a full-file Anonymization Gate and prohibits raw private procurement documents in GitHub. The current gap is operational: there is no reproducible sanitizer, leak-checker or accepted derivative format yet.

Manual visual redaction is not an acceptable baseline because hidden metadata, formulas, links, comments, embedded objects, PDF text/OCR layers and filenames can retain private data.

## Reuse lineage decisions

| Role | Candidate | Decision | Reason |
|---|---|---|---|
| Read XLSX structure | `openpyxl` | `ADAPT` | Mature MIT library; can inspect workbook/sheet/cell structure, comments, names and links. Reading is useful, but mutating an original workbook is not the publication strategy. |
| Create sanitized XLSX derivative | `XlsxWriter` | `ADAPT` | BSD-2-Clause, write-only by design; creates a new workbook rather than preserving unknown internal parts. `constant_memory` supports bounded-memory generation. |
| Inspect/sanitize PDF internals | `pikepdf` | `ADAPT` for inspection/defense-in-depth only | MPL-2.0 and strong access to metadata/attachments/active content. Its own documentation states that programmatic structural redaction cannot guarantee removal of every hidden copy of visible content. |
| Render PDF pages into inert visual derivatives | `pypdfium2` / PDFium | `ADAPT` | Permissive Apache-2.0/BSD-3-Clause wrapper; suitable for page rendering on Windows without CUDA. |
| Heavy local VLM/OCR sanitizer | large VLM / MinerU-like path | `DEFER` | Not required to prove Stage 1P and conflicts with the CPU-first 16 GB target as a mandatory dependency. |
| In-place generic Office/PDF redactor | custom container-preserving sanitizer | `REJECT` as default | High risk of hidden-state leakage and large custom blast radius. |
| No public real-derived corpus | keep all real data private only | `REJECT` as default | Safest for privacy but blocks reproducible CI/independent evaluation on realistic cases. Remains fallback for documents that cannot be safely sanitized. |

## Candidate approaches

### A. In-place/container-preserving sanitization

Modify the original XLSX/PDF and attempt to remove private fields, metadata and hidden structures.

Advantages: highest visual/native fidelity.

Failure mode: the sanitizer must enumerate every relevant internal representation. For PDFs, text may exist in invisible OCR layers, XObjects, thumbnails, indexes or off-page content. For Office files, hidden sheets, defined names, external links, cached values and embedded objects create similar risk.

Result: **not accepted as the default publication path**.

### B. Allowlist reconstruction

Read the private source, extract only explicitly permitted values/layout primitives, then create a **new file** from those permitted values.

For XLSX, read with a native parser and generate a new workbook using a write-only library. Do not copy formulas, external links, comments, macros, embedded files, document properties or unknown OOXML parts unless a later explicit need and sanitizer proves them safe.

For PDF/image sources, redact at the rendered-pixel level and rebuild a new inert derivative rather than preserving the original PDF object graph.

Result: **preferred publication mechanism**.

### C. Dual derivative fixture bundle

For evaluation, represent one private source as a small public bundle rather than insisting on a byte-compatible sanitized original:

```text
CASE_0001/
  manifest.json
  REQUEST_0001/
    document.xlsx
  INVOICE_0001/
    visual/
      page-001.png
  DOC_0001/
    expected.json
```

The public manifest binds each document id to its exact derivative format/path. This separates visual/layout evidence from semantic gold and avoids carrying unknown source-container internals into Git.

Result: **preferred Stage 1P experiment shape**.

### D. Private-only evaluation

Keep the original document outside Git and publish only aggregate metrics.

Result: **allowed fallback**, but insufficient as the only Stage 1 strategy because independent regression/CI would not see realistic cases.

## Failure lessons

1. Visual masking is not deletion.
2. PDF sanitization cannot be defined as a single library call; even mature PDF tooling documents limits of structural redaction.
3. New-file reconstruction has a smaller disclosure surface than preserving unknown internals from Office/PDF containers.
4. Public case/document IDs must not encode source filenames, dates, supplier identity or original document numbers. Stage 1P enforces this mechanically: IDs are fixed-width four-digit ordinals allocated only by internal counters with no caller-supplied ordinal; document ordinals must be dense per prefix. The current real-derived public surface is intentionally limited to `CASE_0001`; expansion requires a separately reviewed repository-level case allocator.
5. A reverse lookup from public ID to raw source may exist only outside the repository if operationally needed; it must never be committed.
6. Leak-checking must inspect both rendered output and format internals of the derivative.
7. Sanitization fidelity and extraction fidelity are separate metrics: a safe derivative that destroys all useful layout is not an adequate benchmark fixture.

## Smallest reproducible experiment

Use a bounded private sample containing at least:

- 4 XLSX documents with merged cells/layout variation;
- 4 digital PDFs with a text layer;
- 4 scanned/image documents;
- representation from at least three lifecycle roles (request/specification, invoice/delivery, incoming control).

Raw files remain outside Git. Only sanitized candidate derivatives and safe aggregate reports may enter the branch after leak checks pass.

For each case test three outputs where applicable:

1. semantic-only safe JSON;
2. sanitized visual pages;
3. rebuilt native derivative (initially XLSX only).

## Metrics

### Privacy / safety — blocking

- known identifier leak count: **0**;
- metadata/property leak count: **0**;
- hidden/embedded/link/comment/formula leak count: **0** in inspected derivative formats;
- filename/archive-member leak count: **0**;
- failed manual spot-check count: **0** for the initial accepted batch.

Any confirmed `ANONYMIZATION_LEAK` blocks promotion.

### Utility

- retained required procurement-line fields;
- retained table/row/column structure where relevant;
- layout fidelity sufficient for Stage 1A benchmark;
- retained neutral lifecycle references needed by Stage 1B;
- derivative generation success rate by format.

### Runtime

On the target Windows CPU-first profile:

- peak RAM must remain compatible with **16 GB total system RAM** while ordinary desktop applications are running;
- processing must be bounded per document/small batch rather than loading the corpus into memory;
- no mandatory CUDA/NVIDIA dependency;
- temporary disk use and output size are measured and reported.

No hard performance threshold is accepted yet; the experiment measures the baseline first.

## Security/data boundary

- Raw corpus: private Drive/Library/local source only.
- No raw filename list, supplier identity, real document numbers, company/project identifiers or reversible mapping in Git.
- Candidate derivatives remain local until both format-aware automated checks and manual spot checks pass.
- Uncertain cases fail closed and remain private.
- Sanitization code must not log raw cell values or extracted private strings into public CI artifacts.

## Architecture decision

**NARROW**

Implement only a Stage 1P prototype around **allowlist reconstruction + dual derivative fixtures + independent leak-check**.

Initial local building blocks may use:

- `openpyxl` for XLSX inspection/read;
- `XlsxWriter` for clean XLSX reconstruction;
- `pikepdf` for PDF structure inspection and defense-in-depth checks, not as proof of complete redaction;
- `pypdfium2` for PDF rendering into inert visual derivatives.

Do not adopt Docling/PaddleOCR/MinerU as Stage 1P dependencies merely for anonymization. They belong to Stage 1A extraction experiments unless a measured Stage 1P gap requires them.

## Explicitly deferred/rejected work

- universal in-place PDF redactor;
- universal in-place Office sanitizer;
- local large VLM as mandatory component;
- OCR as the default route for digital XLSX/PDF;
- publishing raw or merely visually masked source containers;
- ERP/PIM/supplier integration;
- product equivalence/matching logic.

## Acceptance ladder

1. Implement safe manifest/case-id rules and format inventory.
2. Implement XLSX reconstruction prototype and internal leak checks.
3. Implement PDF/image visual derivative prototype and inert-output checks.
4. Run bounded private sample; publish only derivatives that pass all blocking checks.
5. Add deterministic tests with synthetic leak fixtures.
6. Record runtime/RAM/disk measurements on CPU-first target.
7. Freeze exact PR head and obtain fresh independent semantic review before merge.

## Sources checked

- openpyxl documentation: https://openpyxl.readthedocs.io/
- XlsxWriter documentation and license: https://xlsxwriter.readthedocs.io/
- pikepdf sanitization documentation: https://pikepdf.readthedocs.io/en/latest/topics/sanitize.html
- pypdfium2 documentation/licensing: https://pypdfium2-team.github.io/pypdfium2/readme.html
- Docling installation/license references (Stage 1A candidate context): https://docling-project.github.io/docling/getting_started/installation/
