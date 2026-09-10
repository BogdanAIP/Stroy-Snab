# AGENTS.md

Этот файл управляет разработкой Stroy-Snab.

## Bootstrap для каждого нового чата

Перед любым изменением репозитория:

1. Независимо разрешить live GitHub state: default branch, текущий HEAD, активные PR, CI и review state.
2. Прочитать `docs/PRODUCT.md`.
3. Прочитать `docs/CURRENT_STATE.md`.
4. Прочитать `docs/ROADMAP.md`.
5. Прочитать релевантную часть `docs/ARCHITECTURE.md`.
6. Прочитать `docs/DEVELOPMENT_PROTOCOL.md`.
7. Для работы с данными/оценкой прочитать `docs/DATA_POLICY.md` и `docs/EVALUATION_POLICY.md`.
8. Для выбора или замены внешнего компонента прочитать `docs/REUSE_BASELINE.md`.
9. Перечислить `.agents/skills/*/SKILL.md` на текущем ref и загрузить все применимые навыки.

Предыдущий чат — только контекст. Авторитетны live repository state, принятые документы и воспроизводимые evidence.

## Product boundary

Stroy-Snab — предметный слой агента строительных закупок: документы, закупочные позиции, нормализация, сопоставление, поиск/оценка предложений и поставщиков, подготовка закупочных решений и их проверяемое исполнение.

Stroy-Snab не является форком CAP и не должен дублировать generic browser/desktop/session/runtime/verification primitives, уже принадлежащие CAP или зрелым внешним системам.

## Reuse-first

Перед реализацией новой существенной функции обязательно проверить зрелые OSS, открытые данные, официальные API и уже принятые возможности CAP. Для каждого кандидата фиксировать `KEEP / REUSE / ADAPT / REPLACE / DEFER / REJECT` и причину.

Новый собственный компонент допускается только после установленного функционального пробела.

## Research before implementation

Новый крупный stage, новая capability family, изменение модели товара/эквивалентности, новый внешний runtime/ERP/PIM/provider или новая consequence-bearing операция требуют `stage-research` до production implementation.

Research brief заканчивается только одним решением:

`PROCEED | NARROW | DEFER`

`DEFER` блокирует реализацию. `NARROW` разрешает только явно ограниченный scope.

## Data safety

Репозиторий публичный. Сырые пользовательские заявки, счета, УПД, спецификации, входной контроль, договоры, банковские/налоговые реквизиты, персональные данные, закрытые коммерческие данные и иные исходные реальные документы не коммитятся.

Raw-документы из ChatGPT Library, ZIP, Google Drive или локального корпуса используются только как source corpus. В репозиторий могут попадать реальные производные fixtures только как `anonymized-real` после полного Anonymization Gate из `docs/DATA_POLICY.md`; также разрешены `synthetic`, `minimal-redacted` и проверенные `public-source` fixtures.

Anonymization Gate относится ко всему файлу: metadata, скрытые листы/ячейки, comments, formulas/links, revisions, embedded objects, PDF OCR/text layers, attachments и другие невидимые части не могут сохранять реальные идентификаторы. Визуальная заливка поверх текста не считается удалением данных.

## Decision safety

Сходство товара не равно допустимости замены. Канонические terminal states сопоставления:

`EXACT | EQUIVALENT | CANDIDATE | REJECT | UNKNOWN`

`CANDIDATE` не может быть повышен до `EQUIVALENT` одним свободным суждением LLM без структурированных evidence и применимого compatibility rule/approval.

Для закупочных мутаций действует fail-closed: ambiguous delivery/outcome не разрешает слепой повтор.

## Development workflow

После bootstrap foundation (#1) вся работа идёт через ветки и PR.

Одна стадия/эксперимент — один ограниченный PR, если нет убедительной причины объединять scope. Не смешивать research-only и production изменения без явной acceptance authority.

Перед завершением значимой работы обновлять только канонические владельцы истины:

- код/тесты/CI;
- `docs/CURRENT_STATE.md` — если изменилось текущее положение;
- `docs/ROADMAP.md` — если изменился stage/gate;
- `docs/EVIDENCE_INDEX.md` — если появилось принятое evidence;
- архитектурный/политический документ — только если изменилось соответствующее решение.

Не создавать per-chat handoff, дневники и дублирующие status-файлы.

## PR acceptance

После Stage 0 terminal acceptance значимый PR должен иметь:

1. точный `BASE_SHA` и `HEAD_SHA`;
2. применимые тесты/evals;
3. требуемый hosted CI, если он определён текущей стадией;
4. свежий независимый read-only semantic review exact-head по `.agents/skills/code-review/SKILL.md`;
5. отсутствие unresolved confirmed findings;
6. повторный review после любого material fix, двигающего HEAD.

Политика из HEAD не может сама ослабить правила принятия PR, который её вводит. Для Stage 0 действует одноразовое bootstrap-исключение: BASE содержит только исходный README, а предложенная governance оценивается как target semantics и не самосертифицируется.
