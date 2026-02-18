# v15 Notes

Date: 2026-02-18

## What changed
- Merged the previous large Fig.3/Fig.4 content into one horizontal two-panel figure to reduce page usage.
- Implemented side-by-side layout using two `minipage` blocks:
  - (a) speed-quality frontier,
  - (b) token pruning + sparse decoding visualization.
- Removed the standalone qualitative figure float and updated references to `Fig.~X(a)` and `Fig.~X(b)`.

## Validation
- PASS: `bash scripts/build_paper.sh`
- Output: `/Users/shlee/codex/2026/eccv2026/paper/build/main.pdf`

## Scope note
- This version changes only figure layout and related references.
- No new experiments were executed (server remains unavailable).
