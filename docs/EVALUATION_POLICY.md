# Evaluation Policy

Stroy-Snab развивается через измеримые evals, а не через впечатление от нескольких удачных ответов.

## Eval layers

### E1 — Document extraction

Метрики по полям: exact/normalized accuracy для безопасного document id/date, наименования, единицы, количества и технических токенов; line detection precision/recall; document-level perfect extraction rate. Supplier/buyer role оценивается через псевдонимы, когда это нужно для структуры документа; реальная identity компании не является публичной eval-целью.

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

Измеряются correctness и source coverage для supplier identity, item identity, price basis, VAT, availability, delivery terms/date и freshness. Публичные fixture-документы при этом используют псевдонимы компаний; реальные контрагенты могут появляться только как live/public supplier evidence на соответствующем этапе, а не как раскрытые реквизиты из исторических УПД.

### E5 — Procurement recommendation

Рекомендация оценивается только если входные evidence достаточно полны. Нельзя начислять успех за правильный выбор, полученный из недоказанных/галлюцинированных фактов.

### E6 — Action execution

Для consequence-bearing действий измеряются delivery ambiguity, duplicate-action rate, reconciliation success и verified expected effect. Слепой повтор после `UNKNOWN` считается критической ошибкой.

## Dataset separation

- `anonymized-real regression`: обезличенные производные реальных документов в репозитории после Anonymization Gate;
- `synthetic/minimal regression`: синтетические и минимально обезличенные fixtures;
- `raw private source`: исходные документы вне GitHub, используемые для подготовки обезличенных cases и закрытой контрольной проверки;
- `holdout`: обезличенные случаи, не использованные для настройки правил/промптов;
- `adversarial`: похожие товары с критическим несовпадением параметров.

Основной воспроизводимый benchmark должен постепенно опираться на `anonymized-real regression`, чтобы CI и независимое ревью могли видеть реальные сложности документов без раскрытия реквизитов компаний.

## Baseline first

Каждый новый компонент сравнивается минимум с простым baseline. Улучшение принимается только по заранее выбранным метрикам, а не потому что pipeline стал сложнее.

## Error taxonomy

Каждый значимый провал получает класс, например:

`DOC_LAYOUT | LINE_SPLIT | OCR_TEXT | UNIT | NUMBER | CATEGORY | ATTRIBUTE | STANDARD | MATCH_FALSE_POSITIVE | MATCH_FALSE_NEGATIVE | FALSE_EQUIVALENT | STALE_OFFER | SUPPLIER_IDENTITY | ACTION_AMBIGUITY | ANONYMIZATION_LEAK | OTHER`

`ANONYMIZATION_LEAK` — критическая ошибка data handling: реальный идентификатор/реквизит компании остался в public fixture или производном артефакте.

Новые классы добавляются только если существующие не описывают причину.

## Promotion

Экспериментальный pipeline не становится default, пока:

1. зафиксированы version/config/model/data identities;
2. есть результаты anonymized-real regression и требуемых дополнительных sets;
3. нет необъяснённой регрессии критических метрик;
4. известны failure modes;
5. нет известных `ANONYMIZATION_LEAK` в публикуемом корпусе;
6. обновлён `EVIDENCE_INDEX.md` при принятии.
