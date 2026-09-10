# Data

В этой директории находятся только данные, разрешённые для публичного репозитория.

Планируемая структура после Stage 1:

```text
data/
  fixtures/
    documents/
      anonymized-real/   # sanitized derivatives реальных заявок/счетов/УПД/спецификаций/входного контроля
      synthetic/         # полностью синтетические документы
      minimal-redacted/  # минимальные regression fragments
    expected/            # public gold outputs и lifecycle links без реальных реквизитов
  dictionaries/          # только данные с проверенной лицензией
  manifests/             # безопасные version/provenance manifests
```

Сырые реальные заявки/счета/УПД/КП/спецификации/входной контроль из ChatGPT Library, ZIP, Google Drive или локального корпуса сюда не копируются.

Реальные документы могут присутствовать только как `anonymized-real` после полного Anonymization Gate из `docs/DATA_POLICY.md`. Проверяется не только видимая страница: metadata, hidden spreadsheet content, comments/formulas/links, revisions, embedded objects, PDF OCR/text layers/attachments и исходные filenames также не должны сохранять реальную identity или traceable identifiers.

Визуальная заливка поверх исходного текста не считается безопасным обезличиванием. Предпочтительны заново собранные sanitized derivatives либо format-aware проверенные копии.

Идентичности сторон и документов заменяются нейтральными идентификаторами вроде `SUPPLIER_A`, `BUYER_A`, `REQUEST_001`, `INVOICE_001`. Обратная таблица соответствий в репозитории не хранится.

Товарные наименования, технические обозначения, единицы, количества, layout и many-to-many связи желательно сохранять максимально близко к исходным, если комбинация этих полей не создаёт существенного риска повторной идентификации.

Каждый fixture получает provenance label: `anonymized-real | synthetic | minimal-redacted | public-source`.
