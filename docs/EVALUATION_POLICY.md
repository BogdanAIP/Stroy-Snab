# Evaluation Policy

Stroy-Snab развивается через измеримые evals, а не через впечатление от нескольких удачных ответов.

## Eval layers

### E1 — Document extraction

Метрики по полям: exact/normalized accuracy для даты, номера, поставщика, наименования, единицы, количества; line detection precision/recall; document-level perfect extraction rate.

### E2 — Normalization

Измеряются category/class accuracy и attribute precision/recall отдельно по типам атрибутов: размер, материал, марка, стандарт, исполнение, единица и т.д.

### E3 — Matching

Раздельно:

- exact-match precision/recall;
- candidate recall;
- reject precision;
- false-equivalent rate;
- unknown/escalation rate.

`false-equivalent` имеет более высокий штраф, чем лишний `CANDIDATE/UNKNOWN`.

### E4 — Supplier/offer evidence

Измеряются correctness и source coverage для supplier identity, item identity, price basis, VAT, availability, delivery terms/date и freshness.

### E5 — Procurement recommendation

Рекомендация оценивается только если входные evidence достаточно полны. Нельзя начислять успех за правильный выбор, полученный из недоказанных/галлюцинированных фактов.

### E6 — Action execution

Для consequence-bearing действий измеряются delivery ambiguity, duplicate-action rate, reconciliation success и verified expected effect. Слепой повтор после `UNKNOWN` считается критической ошибкой.

## Dataset separation

- `public regression`: обезличенные/синтетические fixtures в репозитории;
- `private realistic`: реальные документы из Library/локального корпуса;
- `holdout`: случаи, не использованные для настройки правил/промптов;
- `adversarial`: похожие товары с критическим несовпадением параметров.

## Baseline first

Каждый новый компонент сравнивается минимум с простым baseline. Улучшение принимается только по заранее выбранным метрикам, а не потому что pipeline стал сложнее.

## Error taxonomy

Каждый значимый провал получает класс, например:

`DOC_LAYOUT | LINE_SPLIT | OCR_TEXT | UNIT | NUMBER | CATEGORY | ATTRIBUTE | STANDARD | MATCH_FALSE_POSITIVE | MATCH_FALSE_NEGATIVE | FALSE_EQUIVALENT | STALE_OFFER | SUPPLIER_IDENTITY | ACTION_AMBIGUITY | OTHER`

Новые классы добавляются только если существующие не описывают причину.

## Promotion

Экспериментальный pipeline не становится default, пока:

1. зафиксированы version/config/model/data identities;
2. есть результаты public regression и private realistic set;
3. нет необъяснённой регрессии критических метрик;
4. известны failure modes;
5. обновлён `EVIDENCE_INDEX.md` при принятии.
