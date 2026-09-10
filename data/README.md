# Data

В этой директории находятся только данные, разрешённые для публичного репозитория.

Планируемая структура после Stage 1:

```text
data/
  fixtures/
    documents/        # synthetic/redacted-derived inputs
    expected/         # public gold outputs
  dictionaries/       # только данные с проверенной лицензией
  manifests/          # безопасные version/provenance manifests
```

Сырые реальные УПД/счета/КП из ChatGPT Library или локального корпуса сюда не копируются.

Private cases получают непрозрачные ids (`priv_upd_0001` и т.п.). Публичные regression cases должны минимально воспроизводить layout/parser/matching failure без раскрытия исходного документа.
