# Evals

Evals — обязательная часть продукта, а не поздняя проверка.

Планируемая структура:

```text
evals/
  cases/              # public synthetic/redacted cases
  manifests/          # dataset/config identities
  gold/               # public expected structures
  reports/            # safe aggregate reports
```

Private realistic corpus остаётся вне GitHub и подключается локально через явно заданный path/file references; код не должен предполагать конкретные имена реальных документов.

Первый benchmark Stage 1 оценивает извлечение из УПД/счетов/спецификаций:

- document date/number;
- supplier identity;
- line segmentation;
- raw item name;
- unit;
- quantity;
- source locator.

Затем по roadmap добавляются normalization, matching, supplier evidence, procurement recommendation и action-execution evals.
