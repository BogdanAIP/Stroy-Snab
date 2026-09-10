# Architecture

## Composition line

```text
USER
  |
  v
ordinary ChatGPT / future client
  |
  v
STROY-SNAB DOMAIN CORE
  |  document model
  |  item normalization
  |  matching/compatibility policy
  |  supplier/offer evidence
  |  procurement decision model
  |
  +--> External data/components
  |      ETIM / standards metadata / units / matchers
  |
  +--> Procurement system adapter
  |      ERPNext | OpenConstructionERP | other accepted substrate
  |
  +--> Supplier providers
  |      official APIs | structured sources | generic web
  |
  v
CAP ADAPTER (later stages)
  |
  v
CAP TRUST / EXECUTION / VERIFICATION
```

## Ownership

### Stroy-Snab owns

- domain schemas for procurement documents/items/offers/decisions;
- mapping from raw procurement language to structured evidence;
- matching state and compatibility policy;
- supplier/offer evidence semantics;
- construction-procurement evaluation datasets and metrics;
- adapters that translate accepted external systems into Stroy-Snab semantics.

### CAP owns

- generic execution authority;
- browser/desktop/session primitives already accepted there;
- ExpectedEffect and ambiguous-outcome reconciliation for CAP-executed mutations;
- generic verification/Finish Gate semantics;
- generic capability/session/runtime mechanics.

Stroy-Snab must not vendor-copy CAP internals to avoid integration work.

### External systems own native state

ERP/PIM/API native records remain native. Stroy-Snab keeps stable logical references/provenance rather than flattening every external field into a second database without need.

## Initial domain pipeline

```text
SourceDocument
 -> DocumentExtraction
 -> ProcurementLine(raw)
 -> NormalizedItemEvidence
 -> MatchCandidates
 -> CompatibilityDecision
 -> SupplierOffers
 -> ProcurementRecommendation
```

Every transformation should preserve a locator/provenance link to the input evidence.

## Matching safety invariant

Semantic similarity is candidate generation, not equivalence authority.

```text
raw candidate
 -> class/category evidence
 -> normalized units
 -> critical-property comparison
 -> standards/material evidence when applicable
 -> EXACT / EQUIVALENT / CANDIDATE / REJECT / UNKNOWN
```

Any unresolved critical property blocks `EXACT` and normally blocks `EQUIVALENT` unless a specific accepted rule says otherwise.

## Persistence

No custom production persistence is selected in Stage 0. Experiment outputs may use simple JSON/JSONL/CSV fixtures. Business-system persistence is selected only in Stage 5 after comparison.

## Model/runtime neutrality

Domain tests should separate deterministic normalization/matching from model-specific proposals. LLM output is treated as proposed structured data/evidence and must be validated before it becomes authoritative state.
