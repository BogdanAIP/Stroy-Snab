# Current State

Дата состояния: 2026-09-18.

## Live repository state at native-PDF baseline start

- default branch: `main`;
- accepted `main` HEAD: `ee065e2bdb4c77c6304df773ecbf47d5303354b5`;
- Stage 0 accepted via PR #1;
- Stage 1P anonymization accepted via PR #2;
- Stage 1A native XLSX baseline/evaluation/remediation accepted via PRs #3-#5;
- Stage 1A PDF/image research gate accepted via PR #6;
- active branch: `stage1a/pdf-native-text-baseline`;
- current roadmap stage: **Stage 1A — Document extraction/evaluation**.

Live GitHub state remains authoritative for the current branch/PR HEAD, CI and review status.

## Accepted XLSX Stage 1A state

Accepted private XLSX control `PRIVATE_CONTROL_0001` remains:

- documents: 4;
- gold lines: 28;
- predicted lines: 28;
- extraction failures: 0;
- line precision/recall: 1.00 / 1.00;
- item exact: 1.00;
- quantity exact: 1.00;
- role exact: 1.00;
- unit exact: 28/28 = 1.00;
- strict line: 28/28 = 1.00;
- document-perfect: 4/4 = 1.00.

Raw private filenames, paths, worksheet titles, item values and reverse mappings remain outside GitHub.

## Accepted PDF/image research authority

Research brief:

`docs/research/STAGE1A_PDF_IMAGE_EXTRACTION_RESEARCH.md`

Terminal decision:

**NARROW**

PR #6 was merged into `main` as:

`ee065e2bdb4c77c6304df773ecbf47d5303354b5`

Final reviewed PR #6 head:

`b49ce3bc79355e37f00bf0151e979f6ac443df7b`

The exact-head hosted workflow #118 / `35237203755` passed. A fresh independent exact-head semantic review under BASE `code-review` v1.0 returned `PASS` with zero surviving findings.

The accepted research decision authorizes a provider-neutral visual-extraction experiment, requires the native pypdfium2 digital-PDF baseline first, and keeps Docling/PaddleOCR/OCRmyPDF/Tesseract/VLM paths optional or deferred until measured evidence supports promotion.

## Active bounded experiment — native digital PDF baseline

Objective:

- implement experiment-only provider-neutral `DocumentPageEvidence`;
- extract native digital-PDF text with the already accepted pypdfium2/PDFium dependency;
- keep PDFium calls sequential in the first experiment;
- preserve page-level provenance without raw source filenames;
- expose only reviewed safe warning codes;
- record exact pypdfium2/PDFium runtime identity;
- reproduce Unicode/Cyrillic text-layer, multi-page, rotated-page and image-only failure classes with synthetic data;
- measure runtime and peak RSS in hosted CI without logging procurement contents or paths.

Current implementation branch adds:

- `src/stroy_snab/experiments/stage1a_pdf.py`;
- `src/stroy_snab/experiments/stage1a_pdf_synthetic.py`;
- `tests/test_stage1a_pdf_native.py`;
- `scripts/benchmark_stage1a_pdf.py`;
- the PDF benchmark as an additional existing CI matrix step.

The native baseline deliberately does **not** perform OCR or claim procurement-line accuracy yet. Image-only PDFs are expected to surface `NO_NATIVE_TEXT`, which is baseline failure evidence rather than a hidden fallback.

Explicitly out of scope for this bounded PR:

- Docling implementation;
- PaddleOCR/PP-StructureV3 implementation;
- OCRmyPDF/Tesseract adoption;
- VLM/cloud OCR;
- raw private visual fixtures in GitHub;
- supplier discovery, matching, lifecycle linkage or later-stage work;
- promotion of any heavy provider.

## Local preflight evidence

Development-side isolated preflight for the new native-PDF files:

- 9/9 focused tests passed;
- synthetic benchmark: 1 document / 3 pages / 153 extracted characters;
- one rotated page was surfaced explicitly;
- local elapsed time was about 31.8 ms on the latest preflight run;
- local whole-process peak RSS was about 94.5 MB;
- local pypdfium2: 5.8.0;
- local PDFium: 149.0.7825.0;
- temporary synthetic tree: about 0.002 MB;
- model footprint: 0;
- benchmark output contains aggregate metadata only and declares `content_logged=false`, `paths_logged=false`.

These are development-environment measurements only. They are not hosted CI evidence and are not measurements of the user's exact PC.

PR #7 `Stage 1A: establish native PDF text baseline` is open against the accepted BASE `ee065e2bdb4c77c6304df773ecbf47d5303354b5`.

## Acceptance gate for the active experiment

Before merge:

1. exact branch/PR BASE and HEAD are frozen;
2. hosted Linux Python 3.11/3.13 and Windows Python 3.13 CI pass;
3. the full accepted XLSX suite/benchmarks remain green;
4. the native PDF synthetic benchmark runs on every CI matrix target;
5. benchmark output remains aggregate-only and exposes no source paths/content;
6. no heavy OCR/layout dependency is introduced;
7. a fresh independent read-only exact-head semantic review returns `PASS` with zero surviving findings.

## Immediate next action

1. obtain hosted exact-head CI for PR #7 and record Linux/Windows resource evidence;
2. verify the accepted XLSX suite and benchmarks remain unchanged;
3. remediate only concrete findings/regressions, if any;
4. freeze final HEAD and run independent exact-head review;
5. merge only on `PASS`;
6. after acceptance, add procurement-line reconstruction/evaluation against synthetic visual gold before crediting Docling or OCR;
7. only then compare optional heavy providers against the same baseline/gold;
8. keep bounded `PRIVATE_VISUAL_CONTROL_0001` aggregate-only and outside GitHub raw-data publication.

## Stage 1A still open

Still required before Stage 1A completion:

- accepted PDF/JPG procurement-line extraction benchmark;
- human gold for visual extraction accuracy;
- line detection precision/recall and field accuracies across visual formats;
- document-perfect rate across visual formats;
- visual extraction error taxonomy;
- measured native-vs-layout/OCR comparison;
- accepted anonymized-real visual regression fixture, or a separately accepted reason to keep visual evaluation private-only;
- bounded resource evidence for any provider proposed as mandatory;
- selected minimal PDF/image extraction stack.

Stage 1B lifecycle linkage, Stage 2 normalization, Stage 3 matching and Stage 4 supplier discovery remain downstream.
