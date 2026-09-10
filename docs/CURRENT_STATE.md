# Current State

Дата состояния: 2026-09-10.

## Текущий этап

`Stage 1P — Anonymization Pipeline`.

Stage 0 foundation принят после свежего независимого exact-head review `PASS` на HEAD `a0f400409a37190e8621a2e59e2e1d02ed000a2b` и слит в `main` merge-коммитом `44610bd33eff346f21414fc5b4513195682cbb76`.

Активная работа Stage 1P ведётся в PR #2 / ветке `stage1p/anonymization-research`. Stage 1P ещё не принят; production procurement logic по-прежнему не вводится.

## Текущая архитектурная позиция

- Stroy-Snab — отдельный domain product, не CAP fork.
- CAP остаётся будущим внешним trusted execution/verification provider.
- Реальный procurement lifecycle моделируется many-to-many через `ProcurementCaseGraph`.
- Lifecycle linkage не означает техническую эквивалентность товара.
- Raw заявки/счета/УПД/спецификации/входной контроль/Drive corpus остаются вне публичного GitHub.
- Публичные real-derived fixtures допускаются только как `anonymized-real` после полного Anonymization Gate.
- Для Stage 1P выбран research decision `NARROW`: allowlist reconstruction + dual derivative model + независимый format-aware leak-check. Universal in-place Office/PDF redaction не является default path.
- Целевой локальный профиль: Windows 11 x64, **16 GB RAM, CPU-first, без обязательной NVIDIA/CUDA**; тяжёлые модели разрешены только как optional fallback.

## Доступный raw source corpus

На 2026-09-10 уже предоставлены:

- `Заявки.zip`: 127 файлов, включая 122 `.xlsx` заявки;
- `счета.zip`: 125 файлов счетов/сканов;
- `Входной контроль материалов.zip`: 19 файлов, включая таблицы входного контроля, спецификации и сводные поставки;
- УПД из пользовательской Library;
- расширенный corpus загружается в Google Drive.

Raw corpus не становится dataset автоматически. Он служит только частным источником для подготовки безопасных производных cases и закрытых контрольных проверок.

## Stage 1P prototype — implemented in PR #2

Реализованы:

1. нейтральные `CASE_*/REQUEST_*/INVOICE_*` ids: фиксированные 4-значные ordinal, выдаваемые внутренним allocator без caller-supplied ordinal; document ids идут плотной последовательностью по prefix, а Stage 1P real-derived publication ограничен `CASE_0001`, поэтому source-derived hashes/numbers/dates не могут быть переданы через ID API;
2. строгий public manifest contract: роли/форматы/пути согласованы, reverse/private fields запрещены;
3. XLSX allowlist reconstruction в новом контейнере через XlsxWriter;
4. fail-closed проверка ошибок записи/merge, чтобы sanitizer не терял данные молча;
5. строгий allowlist внутренних частей публичного XLSX, лимиты ZIP/XML и блокировка case-ambiguous container members;
6. checksum-aware поиск unlabeled ИНН/ОГРН плюс базовые реквизиты/email/phone/URL и private denylist;
7. one-shot/generator denylist материализуется до multi-part проверки;
8. leak reports не повторяют найденные приватные значения;
9. PDF -> последовательный pixel render -> новые PNG без исходного PDF object graph;
10. JPG/PNG -> новый RGB PNG без EXIF/metadata;
11. визуальные производные остаются fail-closed до отдельной visual review;
12. CI на Linux Python 3.11/3.13 и Windows Python 3.13;
13. воспроизводимый synthetic resource benchmark без GPU/CUDA;
14. public fixture CI сверяет manifest с точным набором файлов и блокирует неманифестированные производные.

## Bounded private experiment

Закрытый smoke sample доведён до research minimum:

- 4/4 XLSX успешно прочитаны/обработаны;
- 4/4 PDF с текстовым слоем успешно обработаны, 7 страниц отрендерены;
- 4/4 JPG успешно пересобраны в новые PNG-контейнеры;
- представлены как минимум `REQUEST`, `OFFER_OR_INVOICE`, `UPD_OR_DELIVERY`, `INCOMING_CONTROL`;
- никаких raw filenames, реквизитов, содержимого или reverse mapping в Git не записано.

В изолированном private Linux-прогоне наблюдалось примерно 2.7 s runtime, 258 MB process peak RSS и 17.5 MB временного дерева. Это aggregate engineering evidence, не публичный raw dataset.

## Public anonymized-real policy after experiment

Первый публичный real-derived case — минимальный rebuilt XLSX `CASE_0001 / REQUEST_0001`. CI проверяет его manifest, точный derivative set и внутренности XLSX.

Реальные визуальные производные PDF/JPG **на Stage 1P намеренно остаются private-only**. Публичные synthetic visual regressions проверяют механизм рендера/redaction/metadata stripping. Причина — real visual layout несёт существенно больший риск повторной идентификации, а до Stage 1A не доказано, что публикация такого layout необходима для benchmark. Если Stage 1A покажет измеримый gap, это решение пересматривается отдельным data-safety review.

## Resource evidence

Hosted CI подтверждает Windows-совместимость обязательных Stage 1P зависимостей без CUDA/NVIDIA. На синхронизированном head `69a63f91d89d5efb14b539496567c0ffe1f545ff` Windows Python 3.13 дал **38 tests PASS**; synthetic benchmark (5001 XLSX rows + 3 PDF pages + JPG path) показал 0.749 s, 109.9 MB peak working set и 0.6 MB временного дерева. Все три CI jobs этого head завершились SUCCESS.

Это подтверждает большой ресурсный запас относительно 16 GB target, но не подменяет будущий пользовательский smoke-run на конкретном Windows 11 компьютере.

## Development-side review state

Полный final-tree inventory проверен: в PR нет raw corpus, probe placeholder-файлов или production procurement logic. После независимого review `FAIL` история Stage 1P переписана в один commit поверх принятого BASE; GitHub PR commits endpoint подтверждает один reachable Stage 1P commit, поэтому прежние benign upload-probe placeholders больше не входят в reachable PR history. Self-review отдельно проверил manifest binding, XLSX container allowlist/resource limits, silent data-loss guards, denylist iterator semantics, leak-report self-disclosure, PDF/image inert derivative path, manual visual-review fail-closed rule, public fixture consistency и Windows CPU-first path.

Независимый review прежнего frozen head `ff3c252f2423af76abd647528debc57e87a848e8` вернул `FAIL`: P2 — public ID API допускал caller-supplied numeric ordinal; P3 — benign upload-probe placeholders оставались в reachable PR history. P2 исправлен allocator-owned dense numbering, fixed-width IDs и внутренними (не публично экспортируемыми) syntax helpers; P3 закрыт clean-history rewrite. Clean-history промежуточный head `06ec361133d3499f93fc74bdb63dbaccab6e7f74` прошёл hosted workflow `34510372197` SUCCESS: 40 tests на каждой матрице, включая Windows Python 3.13. После финальной канонической синхронизации требуется новый exact-head CI + fresh independent review.

## Следующее каноническое действие

1. дождаться SUCCESS всех hosted CI jobs на последнем candidate HEAD после финальной синхронизации документов;
2. больше не двигать HEAD и зафиксировать exact `BASE_SHA / HEAD_SHA`;
3. провести свежий независимый read-only semantic review PR #2 по принятому BASE skill `code-review` v1.0;
4. при `PASS` и неизменившемся live HEAD принять Stage 1P;
5. только после этого открыть Stage 1A Document Intake Benchmark и сравнивать Docling/PaddleOCR/другие extraction approaches.

Stage 1A не начинается до принятия Stage 1P.
