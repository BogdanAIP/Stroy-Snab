# Project Risks

Канонический реестр рисков, которые должны влиять на архитектуру и evals.

| Риск | Почему критичен | Базовая защита |
|---|---|---|
| `FALSE_EQUIVALENT` | покупка технически неподходящего материала | critical-property rules, evidence, `CANDIDATE/UNKNOWN` default, отдельная метрика |
| `DOCUMENT_EXTRACTION_ERROR` | неверное количество/единица/позиция попадает дальше по pipeline | gold labels, field/line metrics, provenance to source |
| `LIFECYCLE_LINK_ERROR` | заявка/счёт/поставка связываются неверно и искажают фактическое исполнение | explicit-reference evidence, human gold, candidate links fail closed, linkage precision/recall |
| `UNIT_NORMALIZATION_ERROR` | 10 шт/10 м/10 упаковок дают разный физический заказ | typed quantities, deterministic unit conversion, no silent inference |
| `STALE_OFFER` | цена/наличие/срок уже неактуальны | source timestamp/freshness, re-observation before decision/action |
| `SUPPLIER_IDENTITY_ERROR` | предложение/заказ связывается не с тем контрагентом | stable supplier identity + official evidence where applicable |
| `PRIVATE_DATA_LEAK` | публичный repo/CI раскрывает реальные документы, реквизиты, объект или коммерческие данные | raw corpus outside Git, full-file Anonymization Gate, sanitized derivatives, `.gitignore`, review checks |
| `HIDDEN_FILE_DATA_LEAK` | реквизиты остаются в metadata, hidden sheets, comments, formulas, OCR/text layers, attachments или embedded objects несмотря на визуальное обезличивание | format-aware internal inspection/rebuild; no overlay-only redaction; separate leak check before commit |
| `LEAK_REPORT_SELF_DISCLOSURE` | sanitizer/leak-check сам записывает найденный ИНН, email, имя или исходный filename в публичный log | findings используют только нейтральные kind/location и не повторяют matched private values; regression tests |
| `VISUAL_REDACTION_FALSE_PASS` | проверка контейнера не доказывает отсутствие видимых реквизитов на PNG/JPG/рендере | visual derivative fail-closed до отдельной visual review; OCR/VLM может помогать позже, но не выдаёт authority сам по себе |
| `REIDENTIFICATION` | безопасные по отдельности поля в комбинации позволяют сопоставить fixture с реальной закупкой | combination-risk review, pseudonymous ids, transform/drop rare identifying combinations |
| `SOURCE_CONTAINER_RESIDUE` | неизвестные части исходного Office/PDF контейнера переживают очистку | allowlist reconstruction/new derivative as default; in-place container preservation не считается безопасным baseline |
| `LICENSE_CONTAMINATION` | внешний dataset/code нельзя использовать в целевом режиме | license gate before adoption, source/version manifest |
| `LLM_OVERAUTHORITY` | модель превращает предположение в факт/эквивалентность | proposal vs authority separation, schema validation, evidence gates |
| `DUPLICATE_EXTERNAL_ACTION` | повторный RFQ/заказ после ambiguous outcome | CAP ExpectedEffect/reconciliation/no blind retry |
| `ERP_LOCK_IN` | domain model становится UI/schema конкретной ERP | narrow adapter, external native state ownership |
| `SITE_ADAPTER_SPRAWL` | десятки хрупких интеграций сайтов | official API first, generic CAP browser, adapter only for measured gap |
| `EVAL_CONTAMINATION` | система оптимизирована под известные документы и метрики лгут | holdout split, immutable case identities, baseline comparisons |
| `LOCAL_RESOURCE_OVERLOAD` | обязательный document stack делает обычный desktop непригодным для работы | CPU-first 16 GB target; per-document/small-batch processing; peak RAM/disk/runtime metrics; тяжёлые модели optional |
| `PREMATURE_PLATFORM` | время уходит на UI/DB/framework вместо качества закупок | Stage 1 data benchmark first, reuse-first, experiment-before-adoption |

Риск закрывается не документом, а тестом/eval/evidence или явным product limitation. При появлении нового material risk обновляется этот файл и применимые acceptance gates.
