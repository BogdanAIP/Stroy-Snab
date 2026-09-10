# Evidence Index

Канонический индекс только принятых/релевантных доказательств. Не использовать как журнал чатов.

## Stage 0 — accepted

Foundation acceptance identity:

- bootstrap BASE: `2397b487a3e7b4a0c8b7599f69c72e600ee9f6c2`;
- reviewed HEAD: `a0f400409a37190e8621a2e59e2e1d02ed000a2b`;
- independent semantic review: `PASS`, surviving findings `0`, review skill v1.0;
- merge commit on `main`: `44610bd33eff346f21414fc5b4513195682cbb76`;
- hosted CI/status checks: none existed for the documentation-only bootstrap head.

The exact-head PASS was recorded in PR #1 conversation before merge without moving HEAD.

## Stage 1P — research

Research brief: `docs/research/STAGE1P_ANONYMIZATION_RESEARCH.md`.

Decision: `NARROW`.

Accepted research direction for experiment:

- allowlist reconstruction instead of generic in-place sanitization as default;
- dual derivative fixture shape (safe semantic data + sanitized visual/native derivative as needed);
- format-aware independent leak checking;
- `openpyxl` as XLSX read/inspection candidate;
- `XlsxWriter` as clean XLSX reconstruction candidate;
- `pikepdf` as PDF inspection/defense-in-depth candidate, not proof of complete redaction;
- `pypdfium2` as permissive PDF-rendering candidate;
- CPU-first local target: Windows 11 x64, 16 GB RAM, no mandatory CUDA/NVIDIA.

These component choices are authorized for Stage 1P experiment only; they are not yet accepted production dependencies until experiment evidence and PR acceptance.

## Future research inputs

The following must be independently rechecked before adoption in their stages:

- CAP as existing external execution/verification project;
- ETIM as candidate technical product classification;
- ERPNext/Frappe/frappectl as procurement/data-plane candidates;
- OpenConstructionERP as construction-specific candidate;
- Pint/RapidFuzz/Sentence Transformers/Splink as candidate primitives;
- Docling/PaddleOCR and other document-understanding systems for Stage 1A;
- official Russian classification/standards/counterparty/supplier sources for later stages.

## Evidence record format

For accepted stage/experiment evidence record:

- stage / experiment id;
- immutable code/ref identity;
- dataset identity (`public`, private opaque corpus id, holdout id);
- configuration/model/component versions;
- metric artifact/report locator;
- review/CI identity where applicable;
- decision (`PROCEED | NARROW | DEFER` or adoption result).

Private documents and confidential values never appear in this file.
