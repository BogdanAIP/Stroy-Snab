# Stroy-Snab

Stroy-Snab — evidence-driven агент строительных закупок, который развивается как отдельный предметный продукт и позднее использует CAP для доверенного исполнения и проверки внешних действий.

## Цель

```text
УПД / счёт / заявка / спецификация
 -> структурированные закупочные позиции
 -> нормализация характеристик
 -> EXACT / EQUIVALENT / CANDIDATE / REJECT / UNKNOWN
 -> поиск поставщиков и предложений
 -> evidence-backed comparison
 -> закупочная рекомендация
 -> подтверждённое и проверяемое исполнение
```

Ключевой принцип: **сходство не равно технической эквивалентности**. Система должна предпочитать `CANDIDATE/UNKNOWN` ложному аналогу.

## Текущий статус

Проект находится на `Stage 0 — Project Foundation`.

Production-код ещё не принят. Сначала фиксируются границы продукта, reuse-first архитектура, политика закрытых данных, измеримые evals и процесс независимого принятия изменений.

Следующий этап после принятия Stage 0: **Document Intake Benchmark на реальном закрытом корпусе УПД/счетов из пользовательской Library** с публичными обезличенными regression fixtures.

## Архитектурная линия

```text
ordinary ChatGPT / client
        |
        v
Stroy-Snab domain core
  documents / items / matching / supplier evidence / decisions
        |
        +--> mature OSS + open/official data
        +--> ERP/procurement substrate
        +--> supplier APIs / web providers
        |
        v
CAP adapter (later)
        |
        v
CAP trusted execution / verification
```

Stroy-Snab не является форком CAP и не должен заново реализовывать generic browser/session/desktop/verification runtime.

## Reuse-first

Предварительно исследуются, но пока **не считаются принятыми production dependencies**: ETIM, Pint, RapidFuzz, Sentence Transformers, Splink, ERPNext/Frappe/frappectl, OpenConstructionERP, procurement skills, официальные российские классификаторы/standards/counterparty/supplier APIs и существующие возможности CAP.

См. `docs/REUSE_BASELINE.md`.

## Данные

Репозиторий публичный. Сырые реальные УПД, счета, КП, реквизиты и закрытые цены сюда не коммитятся.

Реальные документы используются как private evaluation corpus; в GitHub допускаются только synthetic/redacted-derived/public-source fixtures и безопасные агрегированные метрики.

См. `docs/DATA_POLICY.md`.

## Начало работы агента

Перед изменениями читать `AGENTS.md`, затем канонический набор:

1. `docs/PRODUCT.md`
2. `docs/CURRENT_STATE.md`
3. `docs/ROADMAP.md`
4. релевантный `docs/ARCHITECTURE.md`
5. `docs/DEVELOPMENT_PROTOCOL.md`
6. применимые `.agents/skills/*/SKILL.md`

Для простого продолжения проекта предусмотрен `.agents/skills/stroy-snab-run/SKILL.md`.
