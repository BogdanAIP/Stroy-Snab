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
- https://github.com/PaddlePaddle/PaddleOCR/blob/main/docs/version3.x/pipeline_usage/PP-StructureV3.en.md
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

## Failure lessons / upstream tests, benchmarks and issue evidence

The sources below are not treated as proof that a historical bug still exists in the exact versions selected for E1A-PDF-IMG-1. They are failure evidence that defines what the experiment must pin, reproduce, falsify or measure. Provider marketing benchmarks are priors only; procurement accuracy is decided on the same Stroy-Snab gold.

### pypdfium2 / PDFium lessons

Existing Stroy-Snab Stage 1P CI already exercises the accepted pypdfium2/PDFium substrate on Linux and Windows through PDF rendering. The synthetic Stage 1P resource benchmark processes three PDF pages and has remained around a ~110 MB whole-benchmark peak RSS envelope in hosted CI. This proves basic cross-platform availability, not PDF text/table accuracy.

Upstream failure evidence:

- pypdfium2 documents PDFium thread incompatibility; project issue #206 discusses sequencing PDFium calls because simultaneous calls may crash, and issue #309 reports random `Data format error` failures from a threaded Celery pool;
- issue #234 demonstrates that rotated pages require explicit care when converting text bounding boxes between PDF/page/device coordinate systems;
- issue #306 reports a special-character extraction mismatch tied to PDF/font behavior;
- issue #298 was a severe `get_text_range()` buffer-size mismatch on a concrete PDF and reinforces fail-closed handling of native text extraction errors.

Experiment consequences:

- `native_pdf_text` is sequential within one process; no shared-process thread parallelism is credited in the first experiment;
- rotated-page fixtures must verify both extracted text and normalized geometry/source locators;
- synthetic text-layer fixtures include Cyrillic and visually/semantically critical special characters rather than ASCII-only smoke tests;
- native extraction exceptions or inconsistent text evidence are explicit extraction failures, never silent empty-success rows;
- the first baseline may use page-bounded text access and must not assume `get_text_range()` or native character order is always authoritative.

Sources:

- https://pypdfium2.readthedocs.io/en/stable/python_api.html#thread-incompatibility
- https://github.com/pypdfium2-team/pypdfium2/issues/206
- https://github.com/pypdfium2-team/pypdfium2/issues/309
- https://github.com/pypdfium2-team/pypdfium2/issues/234
- https://github.com/pypdfium2-team/pypdfium2/issues/306
- https://github.com/pypdfium2-team/pypdfium2/issues/298

### Docling lessons

Upstream benchmark evidence is useful but incomplete for procurement. A September 2026 Docling proposal (#4146) cites an internal comparison over OmniDocBench and DocLayNet structure slices with element pass rates around `0.71` and `0.77` on 50-item slices, plus remaining reading-order headroom. These figures motivate testing Docling but are not accepted as procurement-table accuracy claims.

Concrete issue/failure evidence:

- issue #3512 reproduced a backend-dependent table loss: the serial `DoclingParseDocumentBackend` detected one table while `ThreadedDoclingParseDocumentBackend` returned zero even with `parser_threads=1`. The issue was closed on 2026-09-16, so the experiment must verify the exact 2.128.0 behavior rather than assume the historical failure persists;
- open issue #4028 reports silent row-content corruption in dense multi-page ruled tables with wrapped cells: table shape can look correct while the tail of one row is attached to the next row; it was reproduced across Docling 2.95.0 and 2.120.3;
- open issue #3194 shows cases where predicted table column order disagrees with cell `bbox.l` geometry;
- open issue #3473 shows OCR `TextItem`s present in structured JSON but absent from `md_content` for TABLE regions;
- open issue #4083 reports row labels and numeric values shifting under hybrid native-PDF/OCR behavior on PDFs with a partial/unreliable text layer.

Experiment consequences:

- first Docling digital-PDF comparator pins the serial PDF backend and `do_ocr=False`; backend identity is part of the recorded provider configuration;
- Docling is scored from structured `DoclingDocument`/JSON evidence, not Markdown serialization alone;
- adversarial fixtures include a multi-page table with wrapped item text and a geometry/order check; scoring requires exact item/unit/quantity row association, not merely correct table/row counts;
- canonicalization may use geometry as evidence, but conflicting structural order vs geometry is surfaced as a warning/failure rather than silently selecting a column order;
- hybrid native+OCR Docling behavior is outside the first digital comparator; if later tested, it becomes a separate configuration and cannot inherit the digital-only result.

Sources:

- https://github.com/docling-project/docling/issues/4146
- https://github.com/docling-project/docling/issues/3512
- https://github.com/docling-project/docling/issues/4028
- https://github.com/docling-project/docling/issues/3194
- https://github.com/docling-project/docling/issues/3473
- https://github.com/docling-project/docling/issues/4083

### PaddleOCR / PP-StructureV3 lessons

Official PP-StructureV3 documentation publishes per-model accuracy, CPU inference time and model-size benchmarks, and explicitly notes that reported inference time excludes pre/post-processing. Examples from the checked documentation show a large spread in CPU cost: `PP-DocLayout-S` is listed at 70.9 mAP(0.5), 18.53/6.29 ms CPU and 4.834 MB, while `PP-DocLayout-L` is listed at 90.4 mAP(0.5), 503.01/251.08 ms CPU and 123.76 MB; the larger `PP-DocLayout_plus-L` is listed at 83.2 mAP(0.5), 634.62/378.32 ms CPU and 126.01 MB. These are component benchmarks, not end-to-end procurement results.

For Russian recognition, official PP-OCRv5 multilingual benchmarks report `eslav_PP-OCRv5_mobile_rec` at 81.6% on an East-Slavic dataset of 7,031 Russian/Belarusian/Ukrainian text images and `cyrillic_PP-OCRv5_mobile_rec` at 80.27% on a 7,600-image Cyrillic dataset. These results justify including the Russian/East-Slavic path, but do not establish accuracy on procurement SKUs, quantities or units.

Concrete issue/failure evidence:

- issue #16037 reports text recognized by standalone PP-OCRv5 being absent from PP-StructureV3 output even though recognition boxes were present;
- issue #17503 reproduced a PP-StructureV3 `ValueError("The list of bounding boxes is empty.")` with `use_doc_unwarping=True` on Windows and Linux, CPU and CUDA; disabling unwarping avoided the reported failure. The issue is closed, so this is a configuration lesson to verify on 3.7.0 rather than an assertion that the current release is broken;
- issues #16606/#16656 report offline/local-model configurations still attempting hosting/network resolution in older 3.x deployments, and #15589 reports repeat model download behavior;
- issue #18117 shows an alternate `transformers` engine table path failing in a newer configuration; that engine is not needed for the first Windows CPU comparison.

Experiment consequences:

- first `paddle_structure_ru` pins the ordinary Paddle inference path, exact model names/directories and PP-OCRv5 Russian/East-Slavic recognition; optional transformer-engine variants are excluded;
- `use_doc_unwarping=False` in the initial comparator so OCR/layout quality can be measured without adding a second preprocessing variable; warped/skewed input is a later bounded configuration if needed;
- model assets are pre-resolved and the experiment includes a network-disabled startup/inference check; unexpected model-host access fails reproducibility/privacy acceptance;
- structured PP-Structure output is compared with its underlying OCR text coverage so recognized-but-dropped text is observable;
- end-to-end runtime, peak RSS, temporary disk and total model/download footprint are measured because official component inference times exclude pre/post-processing and model startup.

Sources:

- https://github.com/PaddlePaddle/PaddleOCR/blob/main/docs/version3.x/pipeline_usage/PP-StructureV3.en.md
- https://github.com/PaddlePaddle/PaddleOCR/blob/main/docs/version3.x/algorithm/PP-OCRv5/PP-OCRv5_multi_languages.en.md
- https://github.com/PaddlePaddle/PaddleOCR/issues/16037
- https://github.com/PaddlePaddle/PaddleOCR/issues/17503
- https://github.com/PaddlePaddle/PaddleOCR/issues/16606
- https://github.com/PaddlePaddle/PaddleOCR/issues/16656
- https://github.com/PaddlePaddle/PaddleOCR/issues/15589
- https://github.com/PaddlePaddle/PaddleOCR/issues/18117

### OCRmyPDF / Tesseract lessons

OCRmyPDF remains a mature reference for producing searchable OCR text layers, but upstream Windows issue evidence supports keeping it outside the first primary path:

- issue #1629 shows a Windows/MSYS2 installation where Ghostscript existed as `gs.exe`/`gswin32c.exe` but OCRmyPDF expected `gswin64c`, preventing startup until the executable mapping was corrected;
- issue #1567 shows an OCRmyPDF/Tesseract configuration failing because selected tessdata lacked the `hocr` and `txt` config scripts required by the integration;
- issue #1216 reports an OCR text layer misaligned with the page image on a concrete Windows/macOS reproduction;
- issue #1636 documents a Windows case where CLI and Python API behavior diverged while Ghostscript was absent.

Experiment consequence: OCRmyPDF/Tesseract stays `DEFER` for E1A-PDF-IMG-1. If activated later, the configuration must pin external binary versions/paths, prove an offline Windows installation, and validate OCR text geometry against the same page gold. A searchable text layer alone earns no table/row reconstruction credit.

Sources:

- https://github.com/ocrmypdf/OCRmyPDF/issues/1629
- https://github.com/ocrmypdf/OCRmyPDF/issues/1567
- https://github.com/ocrmypdf/OCRmyPDF/issues/1216
- https://github.com/ocrmypdf/OCRmyPDF/issues/1636

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

1. `native_pdf_text` — pypdfium2 text-layer extraction for digital PDFs, sequential within one process;
2. `docling_layout` — Docling 2.128.0 standard pipeline with serial PDF backend and OCR disabled for digital-PDF/layout comparison;
3. `paddle_structure_ru` — PaddleOCR 3.7.x PP-StructureV3 using the standard Paddle engine, PP-OCRv5 Russian/East-Slavic recognition, explicit local model assets and document unwarping disabled for the first image-only PDF/JPG/scanned comparison.

Every result records an exact `provider_config_id` resolving provider version, backend/engine, model identities and relevant preprocessing switches. A configuration change that could affect extraction quality is a new experiment configuration, not the same provider result.

OCRmyPDF/Tesseract is not installed in the first experiment; it remains a documented fallback comparator if the active paths cannot provide a usable OCR text substrate on Windows.

### Public reproducible data

Use repository-generated `synthetic` fixtures only in the first experiment:

- digital PDF with a simple procurement table and real text layer;
- image-only/scanned PDF containing the same synthetic table;
- JPG/PNG equivalent;
- adversarial synthetic variants: rotated page, Cyrillic/Latin lookalikes and special characters, decimal comma, merged/multiline item text, multi-page wrapped rows/page split, and deliberately partial/empty native text where feasible.

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
- provider_config_id
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
- structured-output text coverage where a provider has both OCR/text blocks and parsed structure;
- extraction failure rate;
- per-document runtime including pre/post-processing;
- peak RSS;
- temporary disk use;
- model/download footprint and network-access count for optional providers.

Quality comparisons must use the same gold and same canonical line parser where possible. Provider output may not be manually corrected before scoring. Serializer output such as Markdown is not the sole scoring oracle when the provider exposes a richer structured representation.

## Falsification criteria

### pypdfium2 baseline is insufficient for a class when

- a digital PDF contains correct visible procurement lines but text-layer ordering prevents reliable row reconstruction;
- the source is image-only and text extraction is empty;
- line recall or document-perfect materially trails a mature layout comparator on the same gold.

### Docling is not promoted when

- it does not materially improve line/document metrics over native digital PDF parsing;
- CPU/RAM/disk/model cost makes it unsuitable as a mandatory local path;
- its output loses source provenance needed for deterministic line locators;
- structured output silently disagrees with row geometry or loses text needed for procurement-line reconstruction;
- dependency/model licensing cannot be bounded cleanly.

### PaddleOCR/PP-StructureV3 is not promoted when

- Russian OCR produces critical item/unit/number errors at unacceptable rate;
- PP-Structure drops text present in its OCR substrate or table/row ordering introduces false procurement lines;
- network-disabled execution cannot be made reproducible with pinned local model assets;
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
- optional model assets are pre-resolved before private-control execution and unexpected network access is a failed privacy/reproducibility check;
- any future public anonymized-real visual fixture must independently pass Stage 1P Anonymization Gate plus completed manual visual review before commit.

## Architecture decision

**NARROW**

Authorized next scope:

1. implement experiment-only provider-neutral `DocumentPageEvidence` boundary;
2. add a native pypdfium2 digital-PDF text baseline using the already accepted dependency, with sequential PDFium calls in the first experiment;
3. add reproducible synthetic digital-PDF/image fixtures and E1A evaluation plumbing, including rotation, special-character and multi-page wrapped-row cases;
4. test Docling 2.128.x as an optional digital layout/table comparator behind the same boundary, with a pinned serial backend and OCR disabled for this configuration;
5. test PaddleOCR 3.7.x PP-StructureV3 with PP-OCRv5 Russian/East-Slavic recognition as an optional scan/JPG comparator behind the same boundary, with pinned local model assets, standard Paddle engine and unwarping disabled in the first configuration;
6. verify optional OCR/layout provider startup/inference with network disabled before using raw private controls;
7. perform a bounded raw-private control and publish only aggregate metrics;
8. keep every heavy provider optional until evidence supports promotion.

Not authorized:

- making Docling, PaddleOCR, OCRmyPDF, Tesseract or a VLM mandatory production dependencies;
- hosted/cloud OCR on raw private documents;
- general-purpose custom OCR/layout framework;
- supplier/matching/lifecycle work in this experiment;
- treating upstream provider benchmarks as Stroy-Snab procurement accuracy evidence;
- declaring Stage 1A complete without an accepted anonymized-real visual regression fixture or an explicit accepted reason to keep visual evaluation private-only.

## Acceptance ladder

1. this research brief is present, contains candidate-specific failure lessons/test/benchmark evidence, and terminal decision remains `NARROW`;
2. experiment adapter is provider-neutral and heavy dependencies are optional extras;
3. synthetic digital PDF + scan/image regressions run reproducibly, including the failure classes derived from upstream lessons;
4. native baseline is measured before crediting heavy components;
5. provider/config/backend/engine/model versions and preprocessing switches are recorded exactly;
6. optional OCR/layout providers pass a network-disabled startup/inference check before private-control use;
7. public logs contain no procurement contents/paths and remain aggregate-only;
8. private control produces only opaque aggregate evidence;
9. Windows/Linux CPU end-to-end resource results are recorded for any candidate proposed as mandatory;
10. no unexplained regression in accepted XLSX Stage 1A behavior;
11. fresh exact-head independent semantic review is required before merge;
12. a separate promotion decision is required before any heavy provider becomes the default production path.
