# Release & Risk Gate (2026-02-18)

Status: IN_PROGRESS (updated after v9 figure audit)
Owner: Release & Risk Team

## Objective
- Define non-negotiable gate before promoting next paper version.

## P0 Gate Items
- [ ] headline claims tied to reproducible artifacts.
- [ ] reviewer P0 findings resolved.
- [ ] no equation-interpretation ambiguity in method core.

## P1 Gate Items
- [ ] benchmark fairness wording consistent across main and appendix.
- [ ] stress-test scope labeling explicit.
- [ ] claim-evidence traceability table current.

## Current Risk Register
| Risk ID | Severity | Description | Owner | Mitigation Status |
|---|---|---|---|---|
| R1 | P0 | multi-seed CI/significance not integrated in main tables yet | Experiment + Reviewer | OPEN |
| R2 | P1 | benchmark expansion not finalized | Data/Benchmark | OPEN |
| R3 | P1 | final abstract wording may need CI-aware update | Writing | OPEN |
| R4 | P0 | figure clipping/semantic mismatch from v8 visuals | Writing + Reviewer | CLOSED in v9 |

## Go/No-Go Rule
- No-go if any P0 remains OPEN.
- Conditional go if only P1 remains and mitigation date is committed.
