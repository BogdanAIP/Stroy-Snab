# Roadmap

Roadmap построен как последовательность измеримых стадий. Переход разрешается только после acceptance предыдущей стадии.

## Stage 0 — Project Foundation

Цель: определить продукт, архитектурные границы, правила данных, оценки, reuse и разработки.

Выход: governance/docs/skills без production domain implementation.

Gate: свежий независимый review foundation PR.

## Stage 1 — Document Intake Benchmark

Цель: научиться воспроизводимо извлекать закупочные строки из **обезличенных производных реальных УПД, счетов и спецификаций**, сохраняя реальные сложности layout и товарной номенклатуры без раскрытия названий и реквизитов компаний.

Перед benchmark определить и проверить Anonymization Gate. Сырые Library-документы остаются вне GitHub; в репозиторий поступает `anonymized-real` corpus.

Исследовать готовые PDF/document extraction решения до собственного parser.

Минимальная каноническая строка:

`document_id, item_name_raw, unit_raw, quantity, source_locator`.

Опционально сохраняются безопасная дата, псевдоним роли стороны (`SUPPLIER_A`) и технические токены. Реальное имя поставщика и исходный номер документа публичному benchmark не требуются.

Расширение после измерения корпуса: артикул, цена, НДС, сумма, ГОСТ/ТУ/DIN tokens и другие поля, только если они нужны конкретной оценке и проходят data policy.

Gate: проверенный anonymized-real dataset + gold labels + benchmark + error taxonomy + отсутствие известных anonymization leaks + выбранный минимальный extraction stack.

## Stage 2 — Canonical Item & Normalization

Цель: из `item_name_raw` получать структурированные признаки без ложной уверенности.

Кандидаты: ETIM/open dictionaries, Pint, RapidFuzz, multilingual embeddings; российские строительные источники — только после проверки лицензий.

Gate: attribute-level precision/recall на anonymized-real corpus и adversarial regression set.

## Stage 3 — Matching & Compatibility

Цель: разделить `EXACT | EQUIVALENT | CANDIDATE | REJECT | UNKNOWN`.

Сначала deterministic/hybrid matching; LLM — bounded evidence consumer, не единственный арбитр эквивалентности.

Gate: отдельно измеренные exact-match precision/recall и false-equivalent rate. False-equivalent — критическая метрика.

## Stage 4 — Supplier & Offer Discovery

Цель: найти реальные предложения и привязать price/availability/delivery/vendor facts к evidence.

Приоритет: официальные API -> структурированные источники -> CAP generic browser. Site-specific adapters только при измеренном gap.

Gate: supplier/offer evidence completeness + precision + stale-data handling.

## Stage 5 — Procurement System Substrate

Цель: экспериментально выбрать business system, а не строить свою ERP.

Кандидаты первого сравнения: ERPNext/Frappe и OpenConstructionERP. При необходимости оценить Odoo/OCA.

Gate: реальный сценарий request -> RFQ/quotation -> decision -> PO-like record, API/agent ergonomics, auditability, deployment cost и schema fit.

## Stage 6 — CAP Read-only Composition

Цель: подключить Stroy-Snab к CAP для чтения файлов/веба/внешней системы и независимой проверки без consequence-bearing закупочных действий.

Gate: end-to-end read-only task с полным provenance/evidence и independent finish verification.

## Stage 7 — Bounded Procurement Actions

Цель: разрешить ограниченные действия: подготовка/отправка RFQ, создание draft/order-like record и другие явно принятые операции.

Каждая mutation: intent -> authorization -> expected effect -> one bounded action -> fresh observation -> PASS/FAIL/UNKNOWN -> reconciliation before retry.

Gate: fault injection + no-blind-retry + explicit human authority policy.

## Stage 8 — Pilot

Цель: ограниченный реальный пилот на строительных закупках.

Метрики: время на обработку, доля ручных исправлений, extraction/matching errors, false-equivalent, экономия/качество shortlist, action failures, evidence completeness.

## Отложено до доказанной необходимости

- собственная ERP/PIM;
- собственный generic browser agent;
- полная база текстов ГОСТ/ТУ/DIN;
- автономная оплата;
- безусловная техническая замена материалов;
- массовая интеграция с каждым сайтом отдельным адаптером.
