# Release & Risk Gate (2026-02-18, v13 refresh)

Status: IN_PROGRESS (server-unavailable mode)
Owner: Release & Risk Team

## Objective
- Define non-negotiable gate before promoting next paper version.

## P0 Gate Items
- [ ] headline claims tied to reproducible artifacts. (BLOCKED by server)
- [x] reviewer P0 findings resolved. (compile crash fixed)
- [x] no equation-interpretation ambiguity in method core. (v13 notation patch applied)

## P1 Gate Items
- [ ] benchmark fairness wording consistent across main and appendix.
- [ ] stress-test scope labeling explicit.
- [ ] claim-evidence traceability table current.

## Current Risk Register
| Risk ID | Severity | Description | Owner | Mitigation Status |
|---|---|---|---|---|
| R1 | P0 | multi-seed CI/significance not integrated in main tables yet | Experiment + Reviewer | OPEN (server blocked) |
| R2 | P1 | benchmark expansion not finalized | Data/Benchmark | OPEN |
| R3 | P1 | final abstract wording may need CI-aware update | Writing | OPEN |
| R4 | P0 | compile failure from sparse decoding equation (double subscript) | Method + Reviewer | CLOSED in v13 |
| R5 | P1 | overfull/underfull layout warnings remain in log | Writing | OPEN |

## Go/No-Go Rule
- No-go if any P0 remains OPEN (or BLOCKED without owner/date).
- Conditional go only when:
  - measured artifacts are generated and linked,
  - all P0 are CLOSED,
  - remaining P1 items have committed owner/date.
