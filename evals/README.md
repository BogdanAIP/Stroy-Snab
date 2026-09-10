# Evals

Evals — обязательная часть продукта, а не поздняя проверка.

Планируемая структура:

```text
evals/
  cases/              # anonymized-real + synthetic/minimal-redacted cases
  manifests/          # dataset/config identities
  gold/               # public expected structures and lifecycle links без реальных реквизитов
  reports/            # safe aggregate reports
```

Основной realistic benchmark должен по возможности работать на **обезличенных производных реальных документов, хранящихся в репозитории**. Сырые исходные документы остаются вне GitHub и используются только для подготовки/проверки обезличивания и при необходимости для закрытой контрольной оценки.

Любой `anonymized-real` case проходит Anonymization Gate из `docs/DATA_POLICY.md` до коммита. Тестовый корпус не должен содержать реальных названий компаний или их реквизитов.

## Stage 1A — extraction

Первый слой benchmark оценивает извлечение из заявок, счетов, УПД, спецификаций и входного контроля:

- document role;
- безопасного document id / document structure;
- line segmentation;
- raw item name;
- unit;
- quantity;
- technical tokens where present;
- source locator.

Supplier/buyer role может оцениваться через псевдонимы (`SUPPLIER_A`, `BUYER_A`), если это необходимо для проверки структуры документа. Реальная identity контрагента не является целью публичного benchmark.

## Stage 1B — lifecycle linkage

Второй слой проверяет реальные связи между документами и строками:

```text
REQUEST / SPECIFICATION
    -> OFFER_OR_INVOICE
    -> UPD_OR_DELIVERY
    -> INCOMING_CONTROL
```

Никакого предположения 1:1. Gold cases должны поддерживать one-to-many, many-to-one и many-to-many связи и включать split, merge, partial, extra, unfulfilled и unknown/candidate отношения, когда такие случаи присутствуют в исходных данных.

Явная ссылка/метаданные и human adjudication являются источником gold linkage. Семантическая похожесть сама по себе не доказывает связь или техническую эквивалентность.

Затем по roadmap добавляются normalization, compatibility/fulfilment matching, supplier evidence, procurement recommendation и action-execution evals.
