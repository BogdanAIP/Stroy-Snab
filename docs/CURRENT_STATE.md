# Current State

Дата состояния: 2026-09-10.

## Текущий этап

`Stage 0 — Project Foundation`.

Foundation разрабатывается в PR #1 `stage0/project-foundation`. Production-код закупочного агента ещё не принят и не должен появляться до принятия Stage 0.

## Текущая архитектурная позиция

- Stroy-Snab — отдельный domain product, не CAP fork.
- CAP рассматривается как будущий внешний trusted execution/verification provider.
- Выбор ERP/PIM/matching stack пока не принят.
- Предварительные кандидаты перечислены в `REUSE_BASELINE.md` и имеют research-only статус.
- Сырые реальные заявки/счета/УПД/входной контроль остаются вне GitHub.
- Реальные документы должны поступать в публичный репозиторий как `anonymized-real` fixtures после обязательного полного Anonymization Gate: без названий компаний, реквизитов/идентификаторов и без утечек через скрытые структуры файла.
- Товарная часть, единицы, количества, технические обозначения и layout по возможности сохраняются реалистичными для benchmark, если комбинация полей не создаёт существенного риска повторной идентификации.
- Реальный lifecycle моделируется many-to-many: нельзя предполагать `1 строка заявки = 1 строка счёта = 1 строка УПД/входного контроля`.

## Доступный raw source corpus для Stage 1

На 2026-09-10 предоставлены три дополнительных архива:

- `Заявки.zip`: 127 файлов, включая 122 `.xlsx` заявки;
- `счета.zip`: 125 файлов счетов/сканов (`jpg/pdf/jpeg` плюс один архивный контейнер);
- `Входной контроль материалов.zip`: 19 файлов, включая таблицы входного контроля, спецификации и сводные поставки.

В основной таблице входного контроля обнаружено 1432 непустых товарных строки. Для 628 строк заполнено поле ссылки на заявку, для 658 — поле ссылки на счёт; также присутствуют подрядчик и вид работ. Эти ссылки рассматриваются как ценный источник human-created linkage evidence, но перед публичным использованием все identity/requisites проходят Anonymization Gate.

Среди счетов есть отдельные файлы/папки, явно привязанные именованием к номерам заявок, что даёт дополнительный источник linkage gold. Имена/реквизиты реальных контрагентов не должны переноситься в публичные manifests.

Пользователь также загружает расширенный raw corpus в Google Drive. Он не считается частью публичного dataset автоматически и должен пройти тот же Stage 1P pipeline перед любым попаданием производных данных в GitHub.

## Stage 0 acceptance target

Должны быть приняты:

- product/non-goals;
- repository governance;
- architecture boundary;
- procurement lifecycle graph boundary;
- reuse-first baseline;
- data/privacy policy и full-file Anonymization Gate;
- evaluation policy;
- staged roadmap;
- research/review skills;
- anonymized-real/public fixture policy.

## Следующее каноническое действие

Заморозить exact HEAD PR #1 и провести свежий независимый read-only semantic review foundation по `.agents/skills/code-review/SKILL.md` с bootstrap authority от исходного BASE.

Если review находит material finding, исправить его в PR #1 и повторить review на новом exact HEAD. Если review PASS и live identity не изменилась, перевести PR в Ready и принять Stage 0.

После принятия Stage 0 открыть `Stage 1 — Document Intake & Lifecycle Benchmark` в порядке:

1. **Stage 1P** — инвентаризация raw corpus и исследование/реализация воспроизводимого format-aware anonymization pipeline;
2. создать первую партию `anonymized-real` и доказать отсутствие известных утечек видимых и скрытых данных;
3. **Stage 1A** — определить канонические `Document` / `ProcurementLine` schemas, extraction gold и сравнить готовые extractors;
4. **Stage 1B** — определить lifecycle-link schema, построить gold many-to-many связей и сравнить linkage approaches;
5. принять только минимальный anonymization/extraction/linkage stack, доказавший качество на реальных документах.

До Stage 1 не выбирать окончательно ERPNext/OpenConstructionERP, ETIM matcher или supplier providers: эти решения должны опираться на измеренные требования, а не на предположения.
