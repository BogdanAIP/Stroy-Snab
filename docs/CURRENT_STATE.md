# Current State

Дата состояния: 2026-09-17.

## Live repository state at research start

- default branch: `main`;
- accepted `main` HEAD: `98fa5258a66e141e3b643a736e0f14dc85982feb`;
- Stage 0 accepted via PR #1;
- Stage 1P anonymization accepted via PR #2;
- Stage 1A native XLSX baseline accepted via PR #3;
- Stage 1A XLSX evaluation harness accepted via PR #4;
- Stage 1A unlabeled-adjacent-unit remediation accepted via PR #5;
- active branch: `stage1a/pdf-image-extraction-research`;
- current roadmap stage: **Stage 1A — Document extraction/evaluation**.

Live GitHub state remains authoritative for current PR HEAD, CI and review status.

## Accepted XLSX Stage 1A state

PR #5 merged as:

`98fa5258a66e141e3b643a736e0f14dc85982feb`

Final reviewed PR #5 head:

`857b0bd2946fb20d78daffb317a991fa7419f64b`

Exact-head hosted workflow #114 passed Ubuntu Python 3.11/3.13 and Windows Python 3.13 with 91 tests per matrix. Final independent exact-head semantic review returned `PASS` with zero surviving findings.

Accepted private XLSX control `PRIVATE_CONTROL_0001`:

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

## Active Stage 1A PDF/image research

Research brief:

`docs/research/STAGE1A_PDF_IMAGE_EXTRACTION_RESEARCH.md`

Terminal research decision:

**NARROW**

Problem boundary:

- Stage 1A still lacks accepted PDF/JPG extraction;
- the mandatory normal-user runtime remains Windows 11 x64 / 16 GB RAM / CPU-first / no mandatory NVIDIA/CUDA;
- public repository currently has no accepted anonymized-real visual extraction fixture;
- Stage 1P intentionally kept real visual derivatives private-only until measured need and manual visual review.

Authorized experiment direction:

1. `pypdfium2` native text extraction is the mandatory low-cost baseline for digital PDFs;
2. Docling 2.128.x may be tested as an optional layout/table comparator, initially without mandatory OCR on digital PDFs;
3. PaddleOCR 3.7.x / PP-StructureV3 may be tested as an optional OCR/layout comparator for image-only PDF/JPG, using PP-OCRv5 Russian/East-Slavic/Cyrillic recognition rather than assuming PP-OCRv6 supports Russian;
4. OCRmyPDF 17.12.x + Tesseract 5.5.x is deferred as the primary path because of Windows native dependency friction and lack of table structure by itself;
5. all heavy providers must remain behind a provider-neutral experiment adapter and may not become mandatory dependencies without measured evidence and a later promotion decision.

Proposed private visual control id:

`PRIVATE_VISUAL_CONTROL_0001`

Private visual evidence may publish only aggregate metrics and opaque ids. Raw PDFs/images, filenames, company identities, document numbers, page text and reverse mappings remain outside GitHub.

## PR #6 independent review #1 — FAIL and remediation

Fresh independent read-only review of exact head:

`1059a3938b2ba52f55f9c8320f2dbb31127e1144`

returned `FAIL` with one P2 research-gate finding:

- the brief documented capabilities, releases, licenses and generic expected failure classes, but BASE `stage-research` v1.0 also requires candidate-specific tests/benchmarks plus issue/failure evidence and an explicit `Failure lessons` section;
- without that evidence dimension, the `NARROW` decision could not yet serve as complete authority for the next external-component experiment.

Remediation in the current branch:

- the brief now contains `Failure lessons / upstream tests, benchmarks and issue evidence`;
- pypdfium2 lessons cover existing Stage 1P cross-platform evidence, PDFium thread incompatibility, rotated geometry and native text-extraction failures;
- Docling lessons record upstream benchmark context plus concrete table-loss, row-mis-pairing, column-order, serializer-loss and hybrid native/OCR failure cases;
- PaddleOCR lessons record official component CPU/model benchmarks, PP-OCRv5 Russian/East-Slavic/Cyrillic recognition benchmarks, structured-output text-loss, unwarping, offline-model and engine failure evidence;
- OCRmyPDF/Tesseract lessons record concrete Windows external-dependency and OCR text-layer alignment failures;
- each lesson now changes the bounded experiment configuration or falsification plan: sequential native PDFium calls; pinned serial/no-OCR Docling digital configuration; structured rather than Markdown-only scoring; standard-engine/local-model/network-disabled Paddle execution with first-run unwarping disabled; and OCRmyPDF/Tesseract remaining deferred until a separate need is measured;
- one pypdfium2 issue marked upstream as `spam / ai` was explicitly excluded from research evidence rather than used to inflate the case.

Because remediation moved HEAD, the prior terminal review is stale for acceptance and a fresh exact-head independent review is required after hosted CI.

## Immediate next action

1. obtain exact-head hosted CI after the research remediation;
2. freeze the resulting PR #6 HEAD and run a fresh independent exact-head semantic review;
3. merge PR #6 only on `PASS` with zero surviving findings;
4. only after research-gate acceptance, implement experiment-only provider-neutral `DocumentPageEvidence` boundary;
5. establish pypdfium2 digital-PDF text baseline first;
6. create synthetic digital-PDF, image-only PDF and image regressions without private content;
7. compare Docling and PaddleOCR only against the same gold and baseline;
8. measure E1A quality plus runtime/RAM/temp-disk/model footprint;
9. run bounded `PRIVATE_VISUAL_CONTROL_0001` with aggregate-only evidence.

## Stage 1A still open

Still required before Stage 1A completion:

- accepted PDF/JPG extraction benchmark;
- human gold for visual extraction accuracy;
- line detection precision/recall and field accuracies across visual formats;
- document-perfect rate across visual formats;
- visual extraction error taxonomy;
- measured native-vs-layout/OCR comparison;
- accepted anonymized-real visual regression fixture, or a separately accepted reason to keep visual evaluation private-only;
- bounded resource evidence for any provider proposed as mandatory;
- selected minimal PDF/image extraction stack.

Stage 1B lifecycle linkage, Stage 2 normalization, Stage 3 matching and Stage 4 supplier discovery remain downstream and are not promoted by this research.
