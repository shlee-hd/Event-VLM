# CERA Paper Workspace

## Scope

This folder contains the CERA paper draft cloned from the latest Event-VLM baseline and then migrated for CERA naming and framing.

## Build

From repository root:

```bash
cd paper
latexmk -pdf -interaction=nonstopmode main.tex
```

Note: style files (`eccv.sty`, `eccvabbrv.sty`) are currently managed under the legacy `paper/` workspace.

## Naming conventions

- Method name: `CERA`
- Expansion: `Causal Event Reasoning and Attribution`
- Internal shorthand: `CER`
- Variants: `CERA-Core`, `CERA-Full`

## Migration checklist

- [x] Rename primary method tokens in manuscript (`Event-VLM*` -> `CERA*`)
- [x] Introduce expanded acronym at first appearance in abstract
- [ ] Re-check figure captions and axis labels after figure regeneration
- [ ] Re-check table text for any legacy wording after experiment reruns
