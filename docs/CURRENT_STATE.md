# Current State

Дата состояния: 2026-09-10.

## Текущий этап

`Stage 1P — Anonymization Pipeline`.

Stage 0 foundation принят после свежего независимого exact-head review `PASS` на HEAD `a0f400409a37190e8621a2e59e2e1d02ed000a2b` и слит в `main` merge-коммитом `44610bd33eff346f21414fc5b4513195682cbb76`.

Активная работа Stage 1P ведётся в ветке `stage1p/anonymization-research`. Production procurement logic по-прежнему не вводится.

## Текущая архитектурная позиция

- Stroy-Snab — отдельный domain product, не CAP fork.
- CAP остаётся будущим внешним trusted execution/verification provider.
- Реальный procurement lifecycle моделируется many-to-many через `ProcurementCaseGraph`.
- Lifecycle linkage не означает техническую эквивалентность товара.
- Raw заявки/счета/УПД/спецификации/входной контроль/Drive corpus остаются вне публичного GitHub.
- Публичные real-derived fixtures допускаются только как `anonymized-real` после полного Anonymization Gate.
- Для Stage 1P выбран research decision `NARROW`: allowlist reconstruction + dual derivative fixtures + независимый format-aware leak-check. Universal in-place Office/PDF redaction не является default path.
- Целевой локальный профиль: Windows 11 x64, **16 GB RAM, CPU-first, без обязательной NVIDIA/CUDA**; тяжёлые модели разрешены только как optional fallback.

## Доступный raw source corpus

На 2026-09-10 уже предоставлены:

- `Заявки.zip`: 127 файлов, включая 122 `.xlsx` заявки;
- `счета.zip`: 125 файлов счетов/сканов;
- `Входной контроль материалов.zip`: 19 файлов, включая таблицы входного контроля, спецификации и сводные поставки;
- УПД из пользовательской Library;
- расширенный corpus загружается в Google Drive.

Raw corpus не становится dataset автоматически. Он служит только частным источником для подготовки безопасных производных cases и закрытых контрольных проверок.

## Stage 1P research result

Canonical research brief: `docs/research/STAGE1P_ANONYMIZATION_RESEARCH.md`.

Decision: `NARROW`.

Разрешённый экспериментальный scope:

1. безопасная inventory/manifest модель без исходных реквизитов и обратимых ids;
2. XLSX: читать структуру нативно и собирать новый sanitized workbook только из allowlisted данных;
3. PDF/image: использовать rendered-pixel derivative и новый inert container вместо сохранения исходного PDF object graph как default;
4. отдельный leak-check видимого и внутреннего содержимого производного файла;
5. synthetic leak fixtures + bounded private sample;
6. измерять privacy blocking metrics, utility, RAM, disk и runtime на CPU-first 16 GB target.

Не разрешено этим research decision:

- универсальный in-place sanitizer исходных Office/PDF;
- публикация overlay-only redaction;
- heavy VLM/OCR как обязательный runtime;
- переход к Stage 1A extraction stack без завершения Stage 1P gate;
- ERP/PIM/supplier/action implementation.

## Следующее каноническое действие

Реализовать минимальный Stage 1P prototype в текущей ветке:

1. case-id / safe manifest contract;
2. synthetic fixtures с намеренными утечками для leak-check regression;
3. XLSX allowlist reconstruction prototype;
4. PDF/image inert visual derivative prototype;
5. format-aware leak checker;
6. bounded private smoke test без коммита raw данных;
7. зафиксировать runtime/peak-memory/temp-disk evidence;
8. после material stability заморозить exact HEAD и провести свежий независимый read-only review.

Stage 1A начинается только после принятия Stage 1P gate.
