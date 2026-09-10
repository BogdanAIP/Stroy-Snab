# Evidence Index

Канонический индекс только принятых/релевантных доказательств. Не использовать как журнал чатов.

## Stage 0

До принятия foundation PR terminal evidence отсутствует.

Research inputs, которые должны быть независимо перепроверены перед adoption конкретного компонента:

- CAP как существующий внешний execution/verification project;
- ETIM как кандидат technical product classification;
- ERPNext/Frappe/frappectl как procurement/data-plane candidates;
- OpenConstructionERP как construction-specific candidate;
- Pint/RapidFuzz/Sentence Transformers/Splink как candidate primitives;
- официальные российские классификаторы/standards/counterparty/supplier APIs как future source providers.

Ни один пункт выше не является accepted production dependency только из-за присутствия в этом индексе.

## Evidence record format

Для принятого stage/experiment добавлять краткую запись:

- stage / experiment id;
- immutable code/ref identity;
- dataset identity (`public`, private opaque corpus id, holdout id);
- configuration/model/component versions;
- metric artifact/report locator;
- review/CI identity where applicable;
- decision (`PROCEED | NARROW | DEFER` или adoption result).

Private documents and confidential values never appear in this file.
