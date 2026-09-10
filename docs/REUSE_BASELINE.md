# Reuse Baseline

Это research baseline, а не список принятых dependencies. Любой компонент перед production adoption проходит актуальный source/license/maintenance/fit review.

| Роль | Кандидат | Статус Stage 0 | Предварительное действие |
|---|---|---|---|
| trusted execution/verification | BogdanAIP/chat-agent-platform (CAP) | existing external project | `REUSE` later, не копировать |
| construction/technical classification | ETIM | open-data candidate | `RESEARCH` |
| construction/BIM dictionary bridge | buildingSMART bSDD | external API/data | `DEFER` до BIM/ontology need |
| units/conversion | Pint | mature OSS | `RESEARCH` Stage 2 |
| lexical fuzzy matching | RapidFuzz | mature OSS | `RESEARCH` Stage 2/3 |
| semantic embeddings/reranking | Sentence Transformers ecosystem | mature OSS | `RESEARCH` Stage 2/3 |
| large-scale entity resolution | Splink / comparable | mature OSS | `DEFER` пока каталог мал |
| procurement workflow/data plane | ERPNext/Frappe | mature OSS | `COMPARE` Stage 5 |
| agent-friendly Frappe access | frappectl | OSS candidate | `COMPARE` Stage 5 |
| construction ERP/BOQ/procurement | OpenConstructionERP | younger OSS | `COMPARE` Stage 5 |
| procurement reasoning templates | procurement-office/procurement-skills | OSS candidate | `RESEARCH` after Stage 1 |
| supplier discovery patterns | Spider-Qwen | OSS reference | `ADAPT IDEAS`, не второй runtime |
| Russian product classification | ОКПД2 / official data | official source | `RESEARCH` when mapping needed |
| standards status | Росстандарт official resources | official source | `RESEARCH` when standards stage starts |
| counterparty evidence | ФНС official resources | official source | `RESEARCH` Stage 4 |
| supplier products/orders | official supplier APIs where available | external | `RESEARCH` Stage 4 |
| generic supplier web | CAP browser path | existing external capability | `REUSE` Stage 4/6 |

## Explicit non-baseline dependencies

Следующие проекты не должны попадать в critical path только потому, что выглядят подходящими:

- ProductNormaliser — полезный design reference, но maturity/coverage должны быть доказаны;
- product-matcher-faiss — полезный reference pipeline, но не принятый production matcher;
- новый agent framework (LangGraph/CrewAI/Flowise/OpenAI Agents SDK и т.п.) — не добавлять без измеренного missing primitive;
- n8n — не default layer; только конкретный integration gap.

## Reuse decision record

Перед добавлением существенного компонента stage research должен ответить:

1. Какую точную роль он закрывает?
2. Какие альтернативы были проверены?
3. Лицензия совместима с предполагаемым использованием?
4. Жив ли проект и есть ли воспроизводимые тесты/API?
5. Какова blast radius зависимости?
6. Можно ли заменить его через узкий adapter?
7. Какие данные/секреты он получает?
8. Что остаётся нашей логикой после adoption?

Результат: `REUSE | ADAPT | REJECT | DEFER` с evidence.
