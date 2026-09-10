# Stroy-Snab

Evidence-driven construction procurement agent for Russian-language procurement practice.

Stroy-Snab is a separate domain product that may later consume CAP as a trusted execution and verification provider. It is not a CAP fork.

The project is intentionally developed from real procurement evidence rather than from a preselected software stack.

## Current stage

`Stage 0 — Project Foundation`

The current work establishes governance, architecture, data safety, reuse-first research rules and evaluation policy. Production procurement logic is intentionally not implemented before the foundation is independently reviewed and accepted.

## Real-data direction

The available private source corpus already includes real:

- procurement requests and follow-up orders;
- invoices and scanned commercial documents;
- UPD/delivery documents available in the user's Library;
- specifications and consolidated supply tables;
- incoming-control/material-accounting records.

Raw source files and archives never enter the public repository. Repository datasets use `anonymized-real` sanitized derivatives after the mandatory full-file Anonymization Gate: company identities, requisites, project-identifying information, traceable document identifiers and hidden/internal file data are removed or rebuilt while useful product names, technical tokens, units, quantities, document layout and lifecycle relationships are preserved when safe.

The procurement process is modelled as a many-to-many evidence graph, not as `one request line = one invoice line = one delivery line`.

```text
REQUEST / SPECIFICATION
        |
        v
OFFER / INVOICE
        |
        v
UPD / DELIVERY
        |
        v
INCOMING CONTROL / MATERIAL ACCOUNTING
```

One request may split into several purchases/deliveries; lines may be merged; quantities may be partial or excessive; follow-up orders and substitutions may appear; some links may remain uncertain.

## Planned sequence

```text
Stage 0   project foundation
Stage 1P  anonymization pipeline + leak check
Stage 1A  document extraction benchmark
Stage 1B  lifecycle linkage benchmark
Stage 2   canonical item normalization
Stage 3   matching + compatibility + fulfilment
Stage 4   supplier/offer discovery
Stage 5   procurement-system substrate experiment
Stage 6   CAP read-only composition
Stage 7   bounded procurement actions
Stage 8   real pilot
```

External technologies such as ERPNext/Frappe, OpenConstructionERP, ETIM, matching libraries and supplier providers are research candidates, not predetermined dependencies. Each must earn adoption through measured experiments on the real anonymized corpus.

See `AGENTS.md` and `docs/CURRENT_STATE.md` before development work.
