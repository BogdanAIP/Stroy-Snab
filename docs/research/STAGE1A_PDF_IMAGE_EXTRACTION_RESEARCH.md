# Stage 1A — PDF/Image Extraction Research

Date: 2026-09-17

## Stage goal

Extend accepted Stage 1A XLSX extraction to PDF and image documents without weakening the CPU-first, provenance-first and private-data boundaries.

Target canonical line remains:

```text
document_id
document_role
item_name_raw
unit_raw
quantity
source_locator
```

The immediate user/product outcome is a reproducible experiment that can extract procurement-line evidence from digital PDFs and scanned/image documents, distinguish text-layer vs OCR paths, preserve page-level provenance, and measure quality/resource cost before any OCR/layout stack becomes a default dependency.

Out of scope:

- supplier/offer discovery;
- item normalization or technical equivalence;
- lifecycle linkage implementation;
- ERP/CAP actions;
- mandatory VLM/GPU runtime;
- raw private corpus publication;
- production adoption of a heavy parser before measured evidence.

## Current baseline / measured gap

Accepted `main` at research start:

`98fa5258a66e141e3b643a736e0f14dc85982feb`

Accepted Stage 1A already provides:

- deterministic native XLSX extraction;
- evaluation harness for line precision/recall and exact/normalized field accuracy;
- aggregate-safe private controls;
- accepted private XLSX result of 28/28 lines, 28/28 unit exact, 4/4 document-perfect after PR #5.

The remaining Stage 1A gap is PDF/JPG extraction. The private source corpus contains mixed commercial/delivery documents in visual formats, while no public anonymized-real PDF/JPG extraction fixture is yet accepted. Stage 1P intentionally kept real visual derivatives private-only pending measured need and manual visual review.

Therefore the first PDF/image work must be an experiment, not a production-adoption claim.

## Problem evidence

Repository evidence:

- Stage 1 requires PDF/JPG benchmark, extraction gold, error taxonomy and a selected minimal extraction stack;
- mandatory local target remains Windows 11 x64, 16 GB RAM, CPU-first, no required NVIDIA/CUDA;
- architecture prefers native parsing for digital PDFs before OCR/model inference;
- pypdfium2 is already present for PDF rendering and can expose PDF text pages;
- public CI currently has no accepted real-derived PDF/JPG fixture;
- raw Google Drive/Library documents may be used only as private source/control data.

Expected PDF/image failure classes:

- `DOC_LAYOUT` — table/column reading order failure;
- `LINE_SPLIT` — row split/merge errors;
- `OCR_TEXT` — Cyrillic/Latin confusion and OCR substitutions;
- `UNIT` / `NUMBER` — unit and decimal/comma corruption;
- page/table fragmentation across multiple pages;
- image rotation/skew/low contrast;
- false text-layer trust where the embedded PDF text is incomplete or scrambled.

## Reuse lineage decisions

| Role | Candidate | Decision | Reason |
|---|---|---|---|
| digital PDF text baseline | pypdfium2 / PDFium | KEEP + ADAPT | Already accepted in Stage 1P, permissive licensing, Windows/CPU path, Unicode text extraction available; no layout analysis, so it is a deliberately weak baseline. |
| digital PDF layout/table comparator | Docling 2.128.0 | ADAPT for bounded experiment | MIT, current release 2026-09-16, Windows support, PDF/image parsing, reading order and table structure; larger dependency/model surface means it must prove value. |
| scanned PDF/JPG OCR/layout comparator | PaddleOCR 3.7.0 / PP-StructureV3 | ADAPT for bounded experiment | Apache-2.0, active project, strong OCR/layout path and CPU support. For Russian, use PP-OCRv5 `ru`/East-Slavic/Cyrillic recognition rather than PP-OCRv6, because current PP-OCRv6 language list does not include Russian. |
| classic OCR text-layer pipeline | OCRmyPDF 17.12.1 + Tesseract 5.5.3 | DEFER as primary path | Mature and permissively usable stack, but Windows setup requires external Tesseract and typically Ghostscript; it creates/searches text layers but does not solve procurement table structure by itself. Retain as fallback/reference if later evidence shows text-layer augmentation is useful. |
| custom Stroy-Snab OCR/layout engine | new implementation | REJECT | No measured gap justifies duplicating mature OCR/layout systems. |
| no new component | pypdfium2-only | KEEP as baseline, not assumed winner | Lowest cost and useful for digital PDFs, but expected to fail on scans and complex tables; the experiment must quantify where it stops being sufficient. |

## Current candidate evidence

### pypdfium2 / PDFium

Current documentation exposes `PdfTextPage.get_text_bounded()` for full-Unicode page/rectangle text extraction and `get_text_range()` for character ranges. The project explicitly states that it does not itself provide layout analysis such as word/line/paragraph detection.

License: pypdfium2 Apache-2.0 OR BSD-3-Clause; bundled PDFium and third-party notices remain applicable to binary redistribution.

Sources:

- https://pypdfium2.readthedocs.io/en/stable/python_api.html
- https://github.com/pypdfium2-team/pypdfium2

### Docling

Latest checked release: `v2.128.0`, published 2026-09-16.

Capabilities relevant to this experiment:

- PDF and image inputs;
- reading-order/layout understanding;
- table structure extraction;
- standard pipeline can run with OCR disabled for digital PDFs;
- selectable PDF backends and OCR engines;
- Windows is listed as a supported platform.

License: MIT for Docling code; model-specific licenses still require checking for any selected optional model.

Sources:

- https://github.com/docling-project/docling/releases/tag/v2.128.0
- https://github.com/docling-project/docling
- https://docling-project.github.io/docling/

### PaddleOCR / PP-StructureV3

Latest checked PaddleOCR release: `v3.7.0`, published 2026-06-11.

Relevant capability:

- PP-StructureV3 document parsing/layout pipeline;
- OCR and table/document structure extraction;
- CPU inference path;
- Russian is supported in PP-OCRv5 multilingual recognition (`ru`, East-Slavic/Cyrillic models), while the current PP-OCRv6 supported-language list does not include Russian.

License: Apache-2.0.

Sources:

- https://github.com/PaddlePaddle/PaddleOCR/releases/tag/v3.7.0
- https://github.com/PaddlePaddle/PaddleOCR/blob/main/docs/version3.x/pipeline_usage/PP-StructureV3.md
- https://github.com/PaddlePaddle/PaddleOCR/blob/main/docs/version3.x/pipeline_usage/OCR.en.md
- https://github.com/PaddlePaddle/PaddleOCR/blob/main/docs/version3.x/algorithm/PP-OCRv5/PP-OCRv5_multi_languages.en.md

### OCRmyPDF / Tesseract

Latest checked releases:

- OCRmyPDF `v17.12.1`, published 2026-09-16;
- Tesseract `5.5.3`, published 2026-07-24.

OCRmyPDF is useful for building/searching OCR text layers but Windows installation requires external native dependencies; current installation guidance requires 64-bit Tesseract and, for the full/recommended path, Ghostscript and additional components. This increases normal-user installation friction and still leaves table/row reconstruction to Stroy-Snab or another parser.

Licenses:

- OCRmyPDF: MPL-2.0;
- Tesseract: Apache-2.0; Leptonica is BSD-style.

Sources:

- https://github.com/ocrmypdf/OCRmyPDF/releases/tag/v17.12.1
- https://ocrmypdf.readthedocs.io/en/stable/installation.html
- https://github.com/tesseract-ocr/tesseract/releases/tag/5.5.3
- https://github.com/tesseract-ocr/tesseract

## Alternatives comparison

| Approach | Digital PDF | Scan/JPG | Table/layout | Windows CPU-first fit | Dependency blast radius | Experiment role |
|---|---:|---:|---:|---:|---:|---|
| pypdfium2 text layer only | strong text access | none | weak | strong | low/already present | mandatory baseline |
| Docling standard, no OCR for digital PDF | strong | limited without OCR | strong | plausible, must measure | medium/high | digital layout comparator |
| PaddleOCR PP-StructureV3 + PP-OCRv5 Russian | works via rendered pages | strong | strong | plausible, must measure | high/model downloads | scan/image comparator |
| OCRmyPDF + Tesseract | useful OCR text layer | strong text OCR | weak/none by itself | higher setup friction | external native tools | deferred fallback/reference |

No single candidate is accepted as default from source claims alone.

## Smallest reproducible experiment

### Experiment E1A-PDF-IMG-1

Compare three active paths behind one experiment-only adapter contract:

1. `native_pdf_text` — pypdfium2 text-layer extraction for digital PDFs;
2. `docling_layout` — Docling standard pipeline with OCR disabled for digital-PDF/layout comparison;
3. `paddle_structure_ru` — PP-StructureV3 with PP-OCRv5 Russian recognition for image-only PDF/JPG/scanned documents.

OCRmyPDF/Tesseract is not installed in the first experiment; it remains a documented fallback comparator if the active paths cannot provide a usable OCR text substrate on Windows.

### Public reproducible data

Use repository-generated `synthetic` fixtures only in the first experiment:

- digital PDF with a simple procurement table and real text layer;
- image-only/scanned PDF containing the same synthetic table;
- JPG/PNG equivalent;
- adversarial synthetic variants: rotated page, Cyrillic/Latin lookalikes, decimal comma, merged/multiline item text, page split.

Fixtures must contain no private names, filenames, numbers or reverse mappings.

### Private control

Use a bounded opaque dataset id, proposed:

`PRIVATE_VISUAL_CONTROL_0001`

Select a small cross-format sample from the existing raw Drive corpus, including at least:

- one digital PDF with usable embedded text;
- one image-only/scanned PDF;
- one JPG/PNG/photo-like document if available;
- at least two procurement roles among `OFFER_OR_INVOICE | UPD_OR_DELIVERY | INCOMING_CONTROL | REQUEST`.

Raw filenames, company identities, document numbers, paths, page text and reverse mappings remain outside GitHub. Repository evidence may record only opaque dataset id, document/page counts, role counts, metrics and resource aggregates.

## Experiment adapter/output contract

Experiment outputs must normalize candidates into a provider-neutral intermediate form before procurement-line parsing:

```text
DocumentPageEvidence
- document_id
- page_number
- provider
- text_blocks[]
  - text
  - bbox? / polygon?
  - confidence?
  - block_kind? (text/table/cell)
- tables[]?
- warnings[] (safe codes only)
```

The experiment must not make Docling/Paddle-specific objects part of core `ProcurementLine` schemas.

`source_locator` should remain provider-neutral, with page identity mandatory and geometry optional, e.g. `PDF!p=2` or `IMG!p=1;bbox=...`. Raw source filenames must never be embedded into locators/logs.

## Metrics

Primary E1A metrics, identical across providers:

- line detection precision/recall;
- item exact and normalized accuracy;
- unit exact and normalized accuracy;
- quantity exact accuracy;
- strict-line accuracy;
- document-perfect rate.

Additional visual-extraction metrics:

- text-block/row ordering error count;
- OCR character/token error notes for critical procurement tokens;
- page/table split error count;
- extraction failure rate;
- per-document runtime;
- peak RSS;
- temporary disk use;
- model/download footprint for optional providers.

Quality comparisons must use the same gold and same canonical line parser where possible. Provider output may not be manually corrected before scoring.

## Falsification criteria

### pypdfium2 baseline is insufficient for a class when

- a digital PDF contains correct visible procurement lines but text-layer ordering prevents reliable row reconstruction;
- the source is image-only and text extraction is empty;
- line recall or document-perfect materially trails a mature layout comparator on the same gold.

### Docling is not promoted when

- it does not materially improve line/document metrics over native digital PDF parsing;
- CPU/RAM/disk/model cost makes it unsuitable as a mandatory local path;
- its output loses source provenance needed for deterministic line locators;
- dependency/model licensing cannot be bounded cleanly.

### PaddleOCR/PP-StructureV3 is not promoted when

- Russian OCR produces critical item/unit/number errors at unacceptable rate;
- table/row ordering introduces false procurement lines;
- CPU resource cost exceeds the normal 16 GB local target without a clearly optional fallback architecture;
- model downloads/runtime cannot be made reproducible and version-pinned.

### All heavy paths are rejected as default when

native text extraction plus narrower deterministic parsing meets the measured digital-PDF need, and scanned/image cases are rare enough to remain an explicit optional/manual fallback.

## Security / data boundary

- no raw private PDF/JPG/image is committed;
- no provider debug dump may print document text in public CI;
- private experiment logging is aggregate-only and uses opaque dataset ids;
- provider errors/warnings must be sanitized before repository evidence;
- model/API candidates that require sending raw documents to third-party hosted services are out of scope for this experiment;
- local/offline execution is the default privacy boundary;
- any future public anonymized-real visual fixture must independently pass Stage 1P Anonymization Gate plus completed manual visual review before commit.

## Architecture decision

**NARROW**

Authorized next scope:

1. implement experiment-only provider-neutral `DocumentPageEvidence` boundary;
2. add a native pypdfium2 digital-PDF text baseline using the already accepted dependency;
3. add reproducible synthetic digital-PDF/image fixtures and E1A evaluation plumbing;
4. test Docling 2.128.x as an optional digital layout/table comparator behind the same boundary;
5. test PaddleOCR 3.7.x PP-StructureV3 with PP-OCRv5 Russian recognition as an optional scan/JPG comparator behind the same boundary;
6. perform a bounded raw-private control and publish only aggregate metrics;
7. keep every heavy provider optional until evidence supports promotion.

Not authorized:

- making Docling, PaddleOCR, OCRmyPDF, Tesseract or a VLM mandatory production dependencies;
- hosted/cloud OCR on raw private documents;
- general-purpose custom OCR/layout framework;
- supplier/matching/lifecycle work in this experiment;
- declaring Stage 1A complete without an accepted anonymized-real visual regression fixture or an explicit accepted reason to keep visual evaluation private-only.

## Acceptance ladder

1. this research brief is present and terminal decision remains `NARROW`;
2. experiment adapter is provider-neutral and heavy dependencies are optional extras;
3. synthetic digital PDF + scan/image regressions run reproducibly;
4. native baseline is measured before crediting heavy components;
5. provider/config/model versions are recorded exactly;
6. public logs contain no procurement contents/paths and remain aggregate-only;
7. private control produces only opaque aggregate evidence;
8. Windows/Linux CPU resource results are recorded for any candidate proposed as mandatory;
9. no unexplained regression in accepted XLSX Stage 1A behavior;
10. fresh exact-head independent semantic review is required before merge;
11. a separate promotion decision is required before any heavy provider becomes the default production path.
