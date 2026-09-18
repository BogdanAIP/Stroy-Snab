# Reuse Baseline

Это research baseline, а не список принятых production dependencies. Любой компонент перед production adoption проходит актуальный source/license/maintenance/fit review.

| Роль | Кандидат | Статус | Предварительное действие |
|---|---|---|---|
| trusted execution/verification | BogdanAIP/chat-agent-platform (CAP) | existing external project | `REUSE` later, не копировать |
| XLSX read/inspection | openpyxl | accepted Stage 1A baseline | `KEEP + ADAPT` |
| clean XLSX reconstruction | XlsxWriter | accepted Stage 1P support | `KEEP + ADAPT` |
| PDF internals inspection/sanitize helpers | pikepdf | Stage 1P experiment candidate | `ADAPT` for inspection/defense-in-depth; not complete redaction authority |
| PDF page rendering | pypdfium2 / PDFium | accepted Stage 1P dependency | `KEEP + ADAPT` |
| digital PDF text baseline | pypdfium2 / PDFium | Stage 1A PDF/image experiment baseline | `KEEP + ADAPT`; native text first, no OCR by default |
| document understanding/layout | Docling 2.128.x | Stage 1A PDF/image experiment candidate | `ADAPT` behind provider-neutral adapter; optional until measured |
| OCR/layout extraction | PaddleOCR 3.7.x / PP-StructureV3 | Stage 1A PDF/image experiment candidate | `ADAPT` behind provider-neutral adapter; use PP-OCRv5 Russian/Cyrillic recognition for `ru` |
| classic OCR text-layer pipeline | OCRmyPDF 17.12.x + Tesseract 5.5.x | fallback/reference candidate | `DEFER` as primary path; Windows native dependencies and no table structure by itself |
| construction/technical classification | ETIM | open-data candidate | `RESEARCH` Stage 2 |
| construction/BIM dictionary bridge | buildingSMART bSDD | external API/data | `DEFER` до BIM/ontology need |
| units/conversion | Pint | mature OSS | `RESEARCH` Stage 2 |
| lexical fuzzy matching | RapidFuzz | mature OSS | `RESEARCH` Stage 2/3 |
| semantic embeddings/reranking | Sentence Transformers ecosystem | mature OSS | `RESEARCH` Stage 2/3 |
| large-scale entity resolution | Splink / comparable | mature OSS | `DEFER` пока каталог мал |
| procurement workflow/data plane | ERPNext/Frappe | mature OSS | `COMPARE` Stage 5 |
| agent-friendly Frappe access | frappectl | OSS candidate | `COMPARE` Stage 5 |
| construction ERP/BOQ/procurement | OpenConstructionERP | younger OSS | `COMPARE` Stage 5 |
| procurement reasoning templates | procurement-office/procurement-skills | OSS candidate | `RESEARCH` after Stage 1 |
| supplier discovery patterns | Spider-Qwen | OSS reference | `ADAPT IDEAS`, не второй runtime |
| Russian product classification | ОКПД2 / official data | official source | `RESEARCH` when mapping needed |
| standards status | Росстандарт official resources | official source | `RESEARCH` when standards stage starts |
| counterparty evidence | ФНС official resources | official source | `RESEARCH` Stage 4 |
| supplier products/orders | official supplier APIs where available | external | `RESEARCH` Stage 4 |
| generic supplier web | CAP browser path | existing external capability | `REUSE` Stage 4/6 |

## Stage 1P license notes

Research checked 2026-09-10:

- openpyxl: MIT/Expat;
- XlsxWriter: BSD-2-Clause;
- Pillow 12.3.0: MIT-CMU;
- pikepdf: MPL-2.0 (research/defense-in-depth candidate only; not a current mandatory dependency);
- pypdfium2 wrapper: Apache-2.0 OR BSD-3-Clause; bundled PDFium/third-party binary notices must be retained as applicable;
- PyMuPDF was considered but is dual AGPL/commercial and is not the preferred baseline while permissive alternatives cover the immediate Stage 1P roles.

The exact Stage 1P source-prototype dependency/license inventory is `docs/DEPENDENCY_LICENSE_MANIFEST_STAGE1P.md`. It records the concrete versions exercised by hosted CI and the PDFium redistribution obligation. A future packaged binary still requires the applicable license files from the exact bundled artifacts; this source manifest is not a substitute for those notices.

## Stage 1A PDF/image research notes

Research checked 2026-09-17:

- Docling latest checked release: `2.128.0` (2026-09-16), MIT; Windows is a supported platform; model-specific licenses must still be checked for selected optional models;
- PaddleOCR latest checked release: `3.7.0` (2026-06-11), Apache-2.0; PP-StructureV3 is the current document-structure pipeline;
- PP-OCRv6 current language list does not include Russian; Russian is supported by PP-OCRv5 multilingual/East-Slavic/Cyrillic recognition and must be explicitly selected for the Russian visual experiment;
- OCRmyPDF latest checked release: `17.12.1` (2026-09-16), MPL-2.0;
- Tesseract latest checked release: `5.5.3` (2026-07-24), Apache-2.0; Windows binary exists, but OCRmyPDF's native Windows path also requires external tooling and does not provide procurement table structure by itself.

Current decision authority is `docs/research/STAGE1A_PDF_IMAGE_EXTRACTION_RESEARCH.md`. Its terminal decision is `NARROW`: all heavy visual providers remain optional experiment candidates until measured against the native PDF baseline and the same gold.

## Explicit non-baseline dependencies

Следующие проекты не должны попадать в critical path только потому, что выглядят подходящими:

- universal in-place Office/PDF sanitizer — reject as default until a measured gap justifies preserving source containers;
- large local VLM/MinerU-like pipeline — not mandatory on the 16 GB CPU-first target;
- ProductNormaliser — useful design reference, but maturity/coverage must be proven;
- product-matcher-faiss — useful reference pipeline, not accepted production matcher;
- new agent framework (LangGraph/CrewAI/Flowise/OpenAI Agents SDK etc.) — do not add without a measured missing primitive;
- n8n — not a default layer; only for a concrete integration gap.

## Reuse decision record

Before adding a material component, stage research must answer:

1. What exact role does it close?
2. Which alternatives were checked?
3. Is the license compatible with intended use?
4. Is the project active and does it have reproducible tests/API?
5. What is the dependency blast radius?
6. Can it be replaced behind a narrow adapter?
7. Which data/secrets does it receive?
8. What logic remains ours after adoption?
9. Does it fit the CPU-first 16 GB local target if mandatory?

Result: `REUSE | ADAPT | REJECT | DEFER` with evidence.
