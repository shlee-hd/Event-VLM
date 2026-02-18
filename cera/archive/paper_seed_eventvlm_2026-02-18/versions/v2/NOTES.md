# CERA Version v2 Notes

- Date: 2026-02-18
- Snapshot type: Naming/terminology stabilization pass

## Includes

- Updated `main.tex` wording to be CER-first in method framing:
  - reduced `VLM`-centric phrasing where it referred to our method itself
  - preserved `VLM` terminology where it refers to baseline families or prior literature
- Added explicit naming rule in main text:
  - `CERA` = full method name
  - `CER` = internal shorthand for causal event reasoning objective
- Added CERA paper workspace build support:
  - `cera/paper/Makefile` with style bootstrap + engine fallback logic
  - `cera/paper/.gitignore`
  - updated `cera/paper/README.md` build instructions
- Compiled snapshot artifact:
  - `cera/paper/versions/v2/CERA-paper-v2.pdf` (26 pages)

## Intent

This snapshot serves as a stable writing baseline before deeper experimental narrative edits and figure/table regeneration.
