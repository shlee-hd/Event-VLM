# CERA Paper Versions

## Purpose

Keep frozen manuscript snapshots for CERA iterations independent of the legacy `paper/versions/` timeline.

## Convention

- Version path: `cera/paper/versions/vN/`
- Minimum files per snapshot:
  - `main.tex`
  - `main.bib`
  - `NOTES.md`
- Optional artifact:
  - `CERA-paper-vN.pdf`

## Current state

- `v1`: initial CERA seed derived from the latest Event-VLM manuscript and naming migration.
- `v2`: CER-first terminology pass + standalone CERA paper build workflow (`Makefile`) + compiled snapshot (`CERA-paper-v2.pdf`).
