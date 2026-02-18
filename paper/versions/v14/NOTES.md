# v14 Notes

Date: 2026-02-18

## What changed
- Captured a new manuscript snapshot after non-experiment remediation and command-center preparation.
- Manuscript updates include:
  - sparse decoding equation compile-blocker fix (double-subscript issue resolved),
  - stronger claim-to-evidence linkage via explicit figure/table references in main narrative,
  - notation clarifications for `\sigma_{\text{shape}}`, top-k index operator, and routing thresholds,
  - explicit draft-scope limitation section to prevent overclaim while server measurements are pending.
- Added cross-team command and execution-readiness docs in workspace:
  - team command board and review templates,
  - server restore run packet and coordination status updates.

## Validation
- LaTeX build passed: `bash scripts/build_paper.sh`.
- Output snapshot sources:
  - `paper/build/main.pdf` -> `paper/versions/v14/Event-VLM-paper-v14.pdf`
  - `paper/build/main.pdf` -> `paper/Event-VLM-paper-v14.pdf`

## Remaining blocker
- Server-side measured artifacts are still pending and required before replacing projected manuscript values.
