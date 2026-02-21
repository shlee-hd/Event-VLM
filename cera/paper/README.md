# CERA Paper (Clean Start)

This directory is a clean-room start for the CERA paper.
No Event-VLM manuscript text is kept in the active `cera/paper/` draft.

## Build

From repository root:

```bash
cd cera/paper
make pdf
```

`make pdf` will:
- bootstrap `eccv.sty` and `eccvabbrv.sty` into `cera/paper/` if needed,
- compile into `cera/paper/build/`,
- use `latexmk` or `pdflatex`, with TinyTeX `pdftex -fmt=pdflatex` fallback.

## Draft policy

- Start from CERA-first framing only.
- Add sections incrementally from scratch.
- Avoid copying prose from archived seed drafts.
- Keep projected-vs-measured status explicit until external execution.

## Measured replacement handoff

Execution artifacts generated under `cera/experiments/results/` should be used to replace projected tables in `main.tex` blocks marked with `MEASURED_SWAP_START/END`.
The replacement run order and checklist are documented in:

- `cera/experiments/SERVER_RUNBOOK.md`
- `cera/experiments/D0_CHECKLIST.md`
