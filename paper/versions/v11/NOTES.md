# v11 Notes

Date: 2026-02-18

## What changed
- Reworked figure strategy around a four-figure narrative:
  - architecture overview (Fig.1),
  - speed-quality frontier (new Fig.4),
  - component details (Fig.2),
  - qualitative pruning/decoding evidence (Fig.3).
- Fixed the key figure layout issue by cropping `figure1_architecture.png` into a horizontal ratio to eliminate large embedded whitespace.
- Added and integrated `figure4_frontier.png` in the main experiment narrative.
- Applied reviewer-driven writing polish in title/abstract/intro/related-work phrasing.
- Expanded cited literature coverage from 46 to 61 unique citation keys in `main.tex`.
- Revalidated LaTeX build with `scripts/build_paper.sh` and regenerated PDF artifacts.

## Build status
- PASS: `/Users/shlee/codex/2026/eccv2026/scripts/build_paper.sh`
- Output: `/Users/shlee/codex/2026/eccv2026/paper/build/main.pdf`

## Open items
- Add one more external anomaly benchmark.
- Add multi-seed confidence intervals and paired significance tests.
- Final cosmetic reduction of remaining overfull text-line warnings.
