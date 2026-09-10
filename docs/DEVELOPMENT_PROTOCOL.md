# Development Protocol

## 1. Resolve live state

Каждый development chat начинает с live repository/branch/PR/CI resolution. Документы не заменяют GitHub state.

## 2. Bootstrap

Следовать `AGENTS.md`; читать только канонический минимальный набор и применимые skills.

## 3. Define one bounded objective

До изменения кода записать:

- проблема;
- измеримый результат;
- текущий baseline;
- затрагиваемые роли/данные;
- acceptance gate;
- что явно вне scope.

## 4. Research when required

Для нового stage/major component/capability выполнить `stage-research`.

Research обязан сравнивать problem evidence и solution evidence. Наличие популярной библиотеки не является доказательством, что она нужна.

## 5. Experiment before adoption

Новая технология сначала попадает в ограниченный reproducible experiment. Эксперимент должен иметь dataset identity, configuration, metrics, output и failure notes.

Не менять одновременно parser, model, matcher и dataset так, чтобы стало невозможно установить причину улучшения/регрессии.

## 6. Production implementation

Production path открывается только после `PROCEED` или `NARROW` и подтверждённого experiment evidence.

Предпочитать узкие adapters и pure domain functions. Не привязывать core schemas к UI конкретного поставщика или ERP.

## 7. Tests/evals

Для deterministic logic — unit/property/regression tests.
Для document/ML/LLM components — public regression + private realistic eval.
Для external integrations — contract/integration tests.
Для consequence-bearing CAP actions — ExpectedEffect/reconciliation/fault tests по применимой CAP policy.

## 8. Review

Material PR проходит exact-head независимый semantic review. Review проверяет не только bugs, но и scope, evidence, data leakage, dependency justification, acceptance integrity и false-equivalent risk.

## 9. Durable continuation

Текущее положение хранится только в `CURRENT_STATE.md`; план — в `ROADMAP.md`; принятые доказательства — в `EVIDENCE_INDEX.md`.

Не создавать handoff-файлы на каждый чат.
