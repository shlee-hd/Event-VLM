# Event-VLM Reviewer Team Full Audit (v6, 2026-02-17)

## Verdict
- Narrative quality: strong.
- Evidence breadth: improved versus earlier drafts.
- Submission-grade robustness: not yet complete until multi-seed CI/significance results are integrated.

## Findings (Severity-Ordered)

### [P1] Stress-test protocol details are under-specified for reproducibility
- File: `/Users/shlee/codex/2026/eccv2026/paper/main.tex:540`
- File: `/Users/shlee/codex/2026/eccv2026/paper/main.tex:562`
- Why it matters: event-density and runtime-robustness tables are persuasive but currently under-documented (sampling mechanism, fixed seed policy, and exact capacity computation assumptions are implicit).
- Recommended fix: add explicit stress-test protocol subsection in experimental setup and define capacity computation formula.

### [P1] Decoding speedup equation currently reads as optimistic without boundary conditions
- File: `/Users/shlee/codex/2026/eccv2026/paper/main.tex:281`
- Why it matters: the approximation `d/F` can be interpreted as universal, while practical speedup depends on `N_{fac}` and current context length `t`.
- Recommended fix: provide exact rearranged form and practical regime condition in method or appendix.

### [P1] Claim-to-evidence mapping is present but not explicit enough for fast reviewer verification
- File: `/Users/shlee/codex/2026/eccv2026/paper/main.tex:52`
- File: `/Users/shlee/codex/2026/eccv2026/paper/main.tex:352`
- Why it matters: strong claims are distributed across abstract/introduction/conclusion, but there is no compact traceability table linking each headline claim to concrete figures/tables and scope labels.
- Recommended fix: add an appendix claim-evidence traceability table.

### [P2] Benchmark fairness language is good, but stress tables should be explicitly marked as internal scaling analyses
- File: `/Users/shlee/codex/2026/eccv2026/paper/main.tex:540`
- Why it matters: without explicit wording, reviewers may treat stress tables as full baseline-parity comparisons.
- Recommended fix: add a one-sentence scope note directly under relevant stress-test discussion.

### [P2] Abstract can be tightened with more concrete retention range language
- File: `/Users/shlee/codex/2026/eccv2026/paper/main.tex:52`
- Why it matters: “99% quality” is concise but less defensible than directly stating observed retention range.
- Recommended fix: replace with explicit CIDEr retention interval and robustness condition.

### [P2] Equation derivation rigor would benefit from a compact appendix derivation block
- File: `/Users/shlee/codex/2026/eccv2026/paper/main.tex:281`
- Why it matters: method novelty depends on clear complexity interpretation; concise derivation strengthens reviewer trust.
- Recommended fix: add “Decoding Complexity Derivation and Assumptions” subsection in appendix.

## Literature and Benchmark Notes
- Current related-work coverage is solid for VLM efficiency and sparse decoding.
- Before submission lock, reviewer team recommends one final pass for newly released VLM anomaly/surveillance papers and long-context inference papers close to ECCV 2026 deadline.

## Writing and Visual Notes
- Current page layout is stable (no critical overflow observed in latest build).
- Figure usage is coherent; captions are generally aligned with claims.

## Mathematical Soundness Notes
- Core equations are internally consistent.
- Remaining risk is not correctness but interpretation scope (approximation regimes), addressed by the P1/P2 fixes above.

## Impact Assessment Notes
- Claimed practical impact (multi-stream safety monitoring) is meaningful.
- Impact language should remain tied to current pilot-scope evidence until CI/significance release is completed.
