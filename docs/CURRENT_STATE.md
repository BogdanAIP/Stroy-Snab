# Current State

Дата состояния: 2026-09-10.

## Текущий этап

`Stage 0 — Project Foundation`.

Репозиторий только создан. Production-код закупочного агента ещё не принят и не должен появляться до принятия Stage 0.

## Текущая архитектурная позиция

- Stroy-Snab — отдельный domain product, не CAP fork.
- CAP рассматривается как будущий внешний trusted execution/verification provider.
- Выбор ERP/PIM/matching stack пока не принят.
- Предварительные кандидаты перечислены в `REUSE_BASELINE.md` и имеют research-only статус.
- Реальные УПД/счета из пользовательской ChatGPT Library рассматриваются как private evaluation corpus; сырые документы не входят в публичный репозиторий.

## Stage 0 acceptance target

Должны быть приняты:

- product/non-goals;
- repository governance;
- architecture boundary;
- reuse-first baseline;
- data/privacy policy;
- evaluation policy;
- staged roadmap;
- research/review skills;
- public fixture policy.

## Следующее каноническое действие

После принятия Stage 0 открыть `Stage 1 — Document Intake Benchmark`:

1. инвентаризировать закрытый корпус реальных УПД/счетов;
2. определить каноническую схему строки документа;
3. создать gold labels для ограниченной выборки;
4. исследовать готовые parsers/extractors перед написанием собственного;
5. провести воспроизводимый benchmark;
6. принять только минимальный extraction stack, доказавший качество на реальных документах.

До Stage 1 не выбирать окончательно ERPNext/OpenConstructionERP, ETIM matcher или supplier providers: эти решения должны опираться на измеренные требования, а не на предположения.
