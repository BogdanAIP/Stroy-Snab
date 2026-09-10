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
- Сырые реальные УПД/счета из пользовательской ChatGPT Library остаются вне GitHub.
- Реальные документы должны поступать в публичный репозиторий как `anonymized-real` fixtures после обязательного Anonymization Gate: без названий компаний и без их реквизитов/идентификаторов.
- Товарная часть, единицы, количества, технические обозначения и layout по возможности сохраняются реалистичными для benchmark.

## Stage 0 acceptance target

Должны быть приняты:

- product/non-goals;
- repository governance;
- architecture boundary;
- reuse-first baseline;
- data/privacy policy и Anonymization Gate;
- evaluation policy;
- staged roadmap;
- research/review skills;
- anonymized-real/public fixture policy.

## Следующее каноническое действие

Заморозить exact HEAD PR #1 и провести свежий независимый read-only semantic review foundation по `.agents/skills/code-review/SKILL.md` с bootstrap authority от исходного BASE.

Если review находит material finding, исправить его в PR #1 и повторить review на новом exact HEAD. Если review PASS и live identity не изменилась, перевести PR в Ready и принять Stage 0.

После принятия Stage 0 открыть `Stage 1 — Document Intake Benchmark`:

1. инвентаризировать исходный закрытый корпус реальных УПД/счетов;
2. определить и проверить процедуру обезличивания;
3. создать первую выборку `anonymized-real` документов без названий и реквизитов компаний;
4. определить каноническую схему строки документа;
5. создать gold labels для обезличенной выборки;
6. исследовать готовые parsers/extractors перед написанием собственного;
7. провести воспроизводимый benchmark на репозиторном anonymized-real corpus;
8. принять только минимальный extraction stack, доказавший качество на реальных документах.

До Stage 1 не выбирать окончательно ERPNext/OpenConstructionERP, ETIM matcher или supplier providers: эти решения должны опираться на измеренные требования, а не на предположения.
