# Reviewer Full Audit (2026-02-18, v9)

Status: PARTIAL (non-experiment scope)
Owner: Reviewer Team

## Direct Answers (requested)
1. **Figure validation done?** **Yes.** v8 PDF figures were re-audited and v9 source updates were applied.
2. **Need more benchmark data?** **Yes.** At least one additional anomaly benchmark and one stronger efficient VLM baseline should be added before external submission.

## Severity Findings

### P0 (resolved in v9)
- **Issue**: Fig.1 and Fig.2 had clipping/semantic mismatch risk in v8 rendering (small visual scale for Fig.1, partial side truncation, and Fig.2 caption-role mismatch).
- **Evidence**:
  - `/Users/shlee/codex/2026/eccv2026/paper/main.tex:158` (Fig.1 includegraphics/trim)
  - `/Users/shlee/codex/2026/eccv2026/paper/main.tex:490` (Fig.2 includegraphics/trim)
  - `/Users/shlee/codex/2026/eccv2026/paper/main.tex:491` (Fig.2 caption)
  - `/Users/shlee/codex/2026/eccv2026/paper/main.tex:469` (text linking Fig.2 role)
- **Action**: corrected in v9:
  - Fig.1 trim set to `0 130 0 20` with width-based scaling.
  - Fig.2 trim set to `0 12 0 90` and caption revised to hazard-aware components.
  - method prose aligned with corrected Fig.2 semantics.
- **Result**: resolved for v9 source and rebuilt PDF.

### P1 (open)
- **Issue**: benchmark coverage is still vulnerable for broad generalization claims.
- **Evidence**:
  - claims and headline framing currently rely on two datasets (`UCF-Crime`, `XD-Violence`) at `/Users/shlee/codex/2026/eccv2026/paper/main.tex:55`, `/Users/shlee/codex/2026/eccv2026/paper/main.tex:316`, `/Users/shlee/codex/2026/eccv2026/paper/main.tex:94`.
- **Why it matters**: reviewers can challenge domain coverage and baseline hardness even if throughput gains are strong.
- **Required fix**:
  - add at least one extra public anomaly benchmark (priority: surveillance style, protocol-compatible),
  - add one stronger efficiency-oriented VLM baseline under unified protocol,
  - keep reproduced-vs-native split explicit in the main table and appendix.

### P1 (open)
- **Issue**: statistical scope disclaimer exists, but headline confidence still reads near-final.
- **Evidence**:
  - disclaimer: `/Users/shlee/codex/2026/eccv2026/paper/main.tex:595`
  - strong deployment claim: `/Users/shlee/codex/2026/eccv2026/paper/main.tex:55`
- **Required fix**:
  - keep current claims but append pilot-scope qualifier in abstract/conclusion sentence endings until multi-seed CI is integrated.

### P2 (open, cosmetic)
- **Issue**: minor overfull/underfull hbox warnings remain in narrative blocks.
- **Evidence**: `/Users/shlee/codex/2026/eccv2026/paper/build/main.log`.
- **Required fix**: sentence-level reflow only; no content-risk impact.

## Figure Aesthetic/Layout Verdict (v9)
- **Intuitiveness**: good (pipeline progression and component semantics are now consistent).
- **Aesthetic consistency**: good (caption roles now clearer; no duplicated in-figure title conflict for Fig.2).
- **Page ratio/scale**: acceptable for LNCS page geometry after v9 trim/width corrections.

## Reviewer Team Next Actions (non-experiment)
1. lock additional benchmark candidate and unified protocol deltas in `paper/reviews/2026-02-18_benchmark-expansion-plan.md`.
2. draft abstract/conclusion pilot-scope qualifier sentence options.
3. deliver final P0/P1 closure checklist to Release & Risk Team.
