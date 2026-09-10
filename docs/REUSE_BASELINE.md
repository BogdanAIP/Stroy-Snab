# Reuse Baseline

Это research baseline, а не список принятых production dependencies. Любой компонент перед production adoption проходит актуальный source/license/maintenance/fit review.

| Роль | Кандидат | Статус | Предварительное действие |
|---|---|---|---|
| trusted execution/verification | BogdanAIP/chat-agent-platform (CAP) | existing external project | `REUSE` later, не копировать |
| XLSX read/inspection | openpyxl | Stage 1P experiment candidate | `ADAPT` |
| clean XLSX reconstruction | XlsxWriter | Stage 1P experiment candidate | `ADAPT` |
| PDF internals inspection/sanitize helpers | pikepdf | Stage 1P experiment candidate | `ADAPT` for inspection/defense-in-depth; not complete redaction authority |
| PDF page rendering | pypdfium2 / PDFium | Stage 1P experiment candidate | `ADAPT` |
| document understanding/extraction | Docling | Stage 1A candidate | `RESEARCH` after Stage 1P |
| OCR/layout extraction | PaddleOCR / PP-Structure family | Stage 1A candidate | `RESEARCH` after Stage 1P |
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
- pikepdf: MPL-2.0;
- pypdfium2 wrapper: Apache-2.0 OR BSD-3-Clause; bundled PDFium/third-party binary notices must be retained as applicable;
- PyMuPDF was considered but is dual AGPL/commercial and is not the preferred baseline while permissive alternatives cover the immediate Stage 1P roles.

Exact packaged dependency/license manifests remain required before merge/adoption of executable code.

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
