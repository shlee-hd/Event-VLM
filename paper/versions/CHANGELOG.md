# Event-VLM Paper Changelog

## v8 (2026-02-17)
- Applied post-v7 readability/layout polish:
  - refined related-work and results prose for tighter reviewer readability,
  - simplified traceability table labels to reduce layout fragility,
  - recompiled and validated clean layout warning state in `build/main.log`.
- Snapshot artifacts:
  - `paper/versions/v8/main.tex`
  - `paper/versions/v8/main.bib`
  - `paper/versions/v8/Event-VLM-paper-v8.pdf`
  - `paper/Event-VLM-paper-v8.pdf`

## v7 (2026-02-17)
- Integrated reviewer-team full audit and applied targeted manuscript hardening:
  - added stress-test protocol details for event-density and runtime-shift analyses,
  - clarified decoding speedup equation with exact form and asymptotic interpretation,
  - added explicit stream-capacity computation formula in experiments,
  - added appendix derivation note for decoding complexity assumptions,
  - added claim-to-evidence traceability table for faster reviewer verification.
- Added reviewer audit report:
  - `paper/reviews/2026-02-17_reviewer-team_full-audit_v6.md`
- Snapshot artifacts:
  - `paper/versions/v7/main.tex`
  - `paper/versions/v7/main.bib`
  - `paper/versions/v7/Event-VLM-paper-v7.pdf`
  - `paper/Event-VLM-paper-v7.pdf`

## v6 (2026-02-17)
- Added more validity-focused experiments in main text and appendix:
  - latency decomposition + stream-capacity table,
  - event-density stress test table,
  - runtime robustness table across resolution/decode-length settings,
  - trigger-threshold sensitivity table,
  - calibration overhead/amortization table.
- Snapshot artifacts:
  - `paper/versions/v6/main.tex`
  - `paper/versions/v6/main.bib`
  - `paper/versions/v6/Event-VLM-paper-v6.pdf`
  - `paper/Event-VLM-paper-v6.pdf`

## v5 (2026-02-17)
- Applied post-v4 formatting and readability polish:
  - removed title line-break token that caused hyperref PDF-string warnings,
  - reduced major table-width overflow by resizing wide comparison tables,
  - simplified long Related Work / Results / Conclusion sentences to reduce overfull lines,
  - standardized appendix table float specifiers from `[h]` to `[ht]`.
- Snapshot artifacts:
  - `paper/versions/v5/main.tex`
  - `paper/versions/v5/main.bib`
  - `paper/versions/v5/Event-VLM-paper-v5.pdf`
  - `paper/Event-VLM-paper-v5.pdf`

## v4 (2026-02-17)
- Applied claim-beautification and evidence-coverage edits on top of v3:
  - added cross-dataset main-results table on XD-Violence under unified protocol,
  - added explicit quality-retention table quantifying near-99\% caption preservation with 9$\times$ throughput gains,
  - added statistical-sufficiency scope statement in experiments and final-release protocol in appendix,
  - resolved major table-width formatting issues and recompiled with local TinyTeX toolchain.
- Snapshot artifacts:
  - `paper/versions/v4/main.tex`
  - `paper/versions/v4/main.bib`
  - `paper/versions/v4/Event-VLM-paper-v4.pdf`
  - `paper/Event-VLM-paper-v4.pdf`

## v3 (2026-02-17)
- Applied evidence-hardening edits on top of v2:
  - anonymized review metadata block (year/alignment with ECCV 2026 review mode),
  - added explicit evaluation protocol and fairness subsection,
  - resolved main/ablation model-definition ambiguity via `Event-VLM-Core` and `Event-VLM-Full`,
  - integrated `figure2_components.png` into main text as component-wise efficiency breakdown,
  - unified Stage-3 operator notation (`TopK-I`),
  - added reproducibility checklist and failure-case taxonomy in appendix.
- Snapshot artifacts:
  - `paper/versions/v3/main.tex`
  - `paper/versions/v3/main.bib`
  - `paper/versions/v3/Event-VLM-paper-v3.pdf`
  - `paper/Event-VLM-paper-v3.pdf`

## v2 (2026-02-17)
- Reframed core narrative around three-axis compute allocation (when/where/which).
- Strengthened abstract, introduction, contributions, Stage-3 framing, and conclusion.
- Clarified adaptation module as optional quality booster.
- Fixed FC ratio consistency (`F=16` => `25% of d/2=64`).
- Updated method comparison label for FASA to `arXiv'26`.
- Snapshot artifacts:
  - `paper/versions/v2/main.tex`
  - `paper/versions/v2/main.bib`
  - `paper/versions/v2/Event-VLM-paper-v2.pdf`
  - `paper/Event-VLM-paper-v2.pdf`

## v1
- First full-draft PDF baseline.

## v0
- Initial early draft PDF.
