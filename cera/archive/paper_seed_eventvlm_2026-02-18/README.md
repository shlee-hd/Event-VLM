# CERA Paper Workspace

## Scope

This folder contains the CERA paper draft cloned from the latest Event-VLM baseline and then migrated for CERA naming and framing.

## Build

From repository root:

```bash
cd cera/paper
make pdf
```

`make pdf` first runs `bootstrap-style`:
- If `cera/paper/eccv.sty` and `cera/paper/eccvabbrv.sty` exist, it uses them.
- Otherwise, it copies them from `paper/` if available.
- Build output is generated in `cera/paper/build/`.
- Build engine preference: `latexmk` first, then `pdflatex` fallback.
- If neither is in PATH, it falls back to TinyTeX `pdftex -fmt=pdflatex` when available.
- Current figure source is linked via `cera/paper/figures -> ../../paper/figures`.

## Naming conventions

- Method name: `CERA`
- Expansion: `Causal Event Reasoning and Attribution`
- Internal shorthand: `CER` (use for objective/component-level terms, not as the paper title)
- Variants: `CERA-Core`, `CERA-Full`

## Migration checklist

- [x] Rename primary method tokens in manuscript (`Event-VLM*` -> `CERA*`)
- [x] Introduce expanded acronym at first appearance in abstract
- [ ] Re-check figure captions and axis labels after figure regeneration
- [ ] Re-check table text for any legacy wording after experiment reruns

## Guardrail

Run naming guard before paper commits:

```bash
bash cera/scripts/check_naming_guard.sh
```
