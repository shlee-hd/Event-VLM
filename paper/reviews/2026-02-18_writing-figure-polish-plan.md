# Writing & Figure Polish Plan (2026-02-18)

Status: PARTIAL
Owner: Writing & Figure Team

## Objective
- Make argument flow and visual communication reviewer-friendly in first pass.

## Writing Tasks
- [ ] Abstract: keep single-sentence headline tightly bound to one table cluster.
- [ ] Introduction: ensure problem pressure and method necessity are explicit in first page.
- [ ] Conclusion: prevent scope creep beyond pilot evidence.

## Figure/Table Tasks
- [x] verify every caption states "what to read first" and "why it matters". (v9: Fig.2 caption-role corrected)
- [x] ensure each figure/table is referenced in adjacent text with claim linkage. (v9: component-analysis sentence aligned with Fig.2 role)
- [ ] ensure table density remains readable under printed two-column view. (pending final camera-ready pass)

## Layout Quality Gate
- [ ] no overflow warnings in `paper/build/main.log`. (text-level hbox warnings remain)
- [x] no ambiguous axis/unit labels.
- [x] no redundant visual elements. (Fig.2 duplicated in-image title conflict removed by trim policy)

## Deliverable
- concise change list with before/after snippets and file line references.

## v9 Change List (2026-02-18)
- `/Users/shlee/codex/2026/eccv2026/paper/main.tex:158`
  - Fig.1 switched to width-dominant scaling + safe trim (`0 130 0 20`) to avoid clipping and improve readability.
- `/Users/shlee/codex/2026/eccv2026/paper/main.tex:490`
  - Fig.2 trim updated (`0 12 0 90`) to remove in-image duplicate title while preserving side content.
- `/Users/shlee/codex/2026/eccv2026/paper/main.tex:491`
  - Fig.2 caption changed to hazard-aware component interpretation.
- `/Users/shlee/codex/2026/eccv2026/paper/main.tex:469`
  - component-analysis prose updated to reflect actual Fig.2 semantics.
