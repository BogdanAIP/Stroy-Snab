# Evals

Evals — обязательная часть продукта, а не поздняя проверка.

Планируемая структура:

```text
evals/
  cases/              # anonymized-real + synthetic/minimal-redacted cases
  manifests/          # dataset/config identities
  gold/               # public expected structures без реальных реквизитов
  reports/            # safe aggregate reports
```

Основной realistic benchmark должен по возможности работать на **обезличенных производных реальных документов, хранящихся в репозитории**. Сырые исходные документы остаются вне GitHub и используются только для подготовки/проверки обезличивания и при необходимости для закрытой контрольной оценки.

Любой `anonymized-real` case проходит Anonymization Gate из `docs/DATA_POLICY.md` до коммита. Тестовый корпус не должен содержать реальных названий компаний или их реквизитов.

Первый benchmark Stage 1 оценивает извлечение из УПД/счетов/спецификаций:

- безопасного document id / document structure;
- line segmentation;
- raw item name;
- unit;
- quantity;
- technical tokens where present;
- source locator.

Supplier/buyer role может оцениваться через псевдонимы (`SUPPLIER_A`, `BUYER_A`), если это необходимо для проверки структуры документа. Реальная identity контрагента не является целью публичного benchmark.

Затем по roadmap добавляются normalization, matching, supplier evidence, procurement recommendation и action-execution evals.
