# Data & Benchmark Expansion Plan (2026-02-18)

Status: IN_PROGRESS (P0 open)
Owner: Data & Benchmark Team

## Objective
- Reduce benchmark attack surface by expanding cross-domain evidence and baseline parity transparency.
- Reviewer verdict: **additional benchmark data is required before external submission**.

## Candidate Additions
| Priority | Candidate | Why It Matters | Feasibility | Notes |
|---|---|---|---|---|
| P0 | Add one extra surveillance anomaly benchmark (e.g., ShanghaiTech or Avenue style) | improves generalization credibility beyond current two-dataset story | MEDIUM | keep same runtime protocol; if dense captions unavailable, report AUC/FPS and separate caption subset scope |
| P0 | Add one stronger efficient VLM baseline under unified runtime protocol | protects against "weak baseline" criticism | MEDIUM | prioritize reproducing one recent efficiency-oriented method with transparent constraints |
| P1 | Add explicit reproduced/native split table | fairness transparency | HIGH | can be done without extra experiments |

## Selection Rules (locked)
- prefer datasets that are public, surveillance-like, and compatible with current frame-level anomaly pipeline.
- baseline addition must be reproducible under the same hardware/resolution/decode-length settings.
- if a candidate cannot be reproduced fairly, include it in native-reference block only with explicit dagger policy.

## Baseline Parity Audit
- [ ] reproduced baselines list finalized.
- [ ] native-paper baselines list finalized.
- [ ] dagger policy text aligned across main tables and appendix.

## Deliverables
1. updated parity mapping table.
2. benchmark expansion recommendation with cost/time estimate.
3. impact on main-claim risk assessment.

## Exit Criteria
- one new benchmark added to main results or appendix with protocol note.
- one additional strong baseline added (reproduced or clearly-tagged native).
- Reviewer Team signs off that benchmark attack surface is reduced from P1 to P2.
