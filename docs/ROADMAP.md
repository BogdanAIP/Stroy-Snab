# Roadmap

Roadmap построен как последовательность измеримых стадий. Переход разрешается только после acceptance предыдущей стадии.

## Stage 0 — Project Foundation

Цель: определить продукт, архитектурные границы, правила данных, оценки, reuse и разработки.

Выход: governance/docs/skills без production domain implementation.

Gate: свежий независимый review foundation PR.

## Stage 1 — Document Intake & Lifecycle Benchmark

Цель: научиться воспроизводимо подготавливать, извлекать и связывать закупочные данные из **обезличенных производных реальных заявок, счетов, УПД, спецификаций и входного контроля материалов**, сохраняя реальные сложности layout и товарной номенклатуры без раскрытия названий и реквизитов компаний.

Сырые Library/ZIP/Drive-документы остаются вне GitHub; в репозиторий поступает только `anonymized-real` corpus после полного Anonymization Gate.

### Stage 1P — Anonymization pipeline

До OCR/extraction построить воспроизводимый format-aware pipeline подготовки публичных производных данных.

Минимальные требования:

- инвентаризация raw corpus без публикации исходных имён/реквизитов;
- стабильные нейтральные case/document ids;
- удаление/замена видимой identity и traceable identifiers;
- очистка metadata, hidden spreadsheet content, comments/formulas/links, revision data, embedded objects и PDF OCR/text layers/attachments согласно `docs/DATA_POLICY.md`;
- запрет overlay-only redaction;
- отдельный leak-check после преобразования;
- ручная выборочная проверка первых партий и каждого нового формата/шаблона;
- provenance manifest, не содержащий обратимого соответствия публичных ids исходным документам.

Предпочитать заново собранные sanitized derivatives исходным Office/PDF контейнерам, если нельзя уверенно доказать очистку всех внутренних частей.

Gate 1P: первая репозиторная партия `anonymized-real` проходит автоматический/format-aware leak-check + ручную выборочную проверку без известных `ANONYMIZATION_LEAK`.

### Stage 1A — Document extraction

Исследовать готовые PDF/image/spreadsheet/document extraction решения до собственного parser.

Минимальная каноническая строка:

`document_id, document_role, item_name_raw, unit_raw, quantity, source_locator`.

Опционально сохраняются безопасная дата, псевдоним роли стороны (`SUPPLIER_A`), технические токены и другие поля, прошедшие data policy. Реальное имя поставщика и исходный номер документа публичному benchmark не требуются.

### Stage 1B — Procurement lifecycle linkage

Построить gold-набор реальных связей между документами и строками без предположения 1:1.

Минимальные роли источников:

`REQUEST | SPECIFICATION | OFFER_OR_INVOICE | UPD_OR_DELIVERY | INCOMING_CONTROL`.

Должны поддерживаться one-to-one, one-to-many, many-to-one и many-to-many связи, включая частичную поставку, дозаказ, разбивку между документами, объединение строк, сверхпоставку и отсутствие доказанной связи.

На Stage 1 linkage опирается прежде всего на явные ссылки/метаданные и human gold. Семантическая похожесть может предложить candidate edge, но не доказывает техническую эквивалентность.

Расширение после измерения корпуса: артикул, цена, НДС, сумма, ГОСТ/ТУ/DIN tokens и другие поля, только если они нужны конкретной оценке и проходят data policy.

Gate Stage 1: принятый anonymization pipeline + проверенный anonymized-real dataset + extraction gold + lifecycle-link gold + benchmark + error taxonomy + выбранный минимальный extraction/linkage stack.

## Stage 2 — Canonical Item & Normalization

Цель: из `item_name_raw` получать структурированные признаки без ложной уверенности.

Кандидаты: ETIM/open dictionaries, Pint, RapidFuzz, multilingual embeddings; российские строительные источники — только после проверки лицензий.

Gate: attribute-level precision/recall на anonymized-real corpus и adversarial regression set.

## Stage 3 — Matching, Compatibility & Fulfilment

Цель: разделить `EXACT | EQUIVALENT | CANDIDATE | REJECT | UNKNOWN` и применить это к реальным request-to-procurement/delivery связям.

Сначала deterministic/hybrid matching; LLM — bounded evidence consumer, не единственный арбитр эквивалентности.

Отдельно измеряется fulfilment: какая доля заявленного количества подтверждённо закуплена/поставлена, где есть partial/split/merge/extra/unfulfilled, и где связь остаётся неизвестной.

Gate: отдельно измеренные exact-match precision/recall, lifecycle/line-link precision/recall, quantity fulfilment accuracy и false-equivalent rate. False-equivalent — критическая метрика.

## Stage 4 — Supplier & Offer Discovery

Цель: найти реальные предложения и привязать price/availability/delivery/vendor facts к evidence.

Приоритет: официальные API -> структурированные источники -> CAP generic browser. Site-specific adapters только при измеренном gap.

Gate: supplier/offer evidence completeness + precision + stale-data handling.

## Stage 5 — Procurement System Substrate

Цель: экспериментально выбрать business system, а не строить свою ERP.

Кандидаты первого сравнения: ERPNext/Frappe и OpenConstructionERP. При необходимости оценить Odoo/OCA.

Gate: реальный сценарий request -> RFQ/quotation -> decision -> PO-like record -> delivery/incoming-control linkage, API/agent ergonomics, auditability, deployment cost и schema fit.

## Stage 6 — CAP Read-only Composition

Цель: подключить Stroy-Snab к CAP для чтения файлов/веба/внешней системы и независимой проверки без consequence-bearing закупочных действий.

Gate: end-to-end read-only task с полным provenance/evidence и independent finish verification.

## Stage 7 — Bounded Procurement Actions

Цель: разрешить ограниченные действия: подготовка/отправка RFQ, создание draft/order-like record и другие явно принятые операции.

Каждая mutation: intent -> authorization -> expected effect -> one bounded action -> fresh observation -> PASS/FAIL/UNKNOWN -> reconciliation before retry.

Gate: fault injection + no-blind-retry + explicit human authority policy.

## Stage 8 — Pilot

Цель: ограниченный реальный пилот на строительных закупках.

Метрики: время на обработку, доля ручных исправлений, extraction/linkage/matching errors, false-equivalent, fulfilment accuracy, экономия/качество shortlist, action failures, evidence completeness.

## Отложено до доказанной необходимости

- собственная ERP/PIM;
- собственный generic browser agent;
- полная база текстов ГОСТ/ТУ/DIN;
- автономная оплата;
- безусловная техническая замена материалов;
- массовая интеграция с каждым сайтом отдельным адаптером.
