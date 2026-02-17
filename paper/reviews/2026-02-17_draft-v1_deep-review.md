# Event-VLM Draft V1 Deep Review (2026-02-17)

## Verdict
- Claim narrative quality: **Strong** (clear 3-axis story: temporal/spatial/decoding).
- Evidence quality for top-tier review: **Not yet sufficient**.
- Current draft status is appropriate for pre-experiment claim design, but not yet submission-grade.

## Findings (Severity-Ordered)

### [P1] Submission metadata is still template/dummy and breaks reviewer trust immediately
- File: `/Users/shlee/codex/2026/eccv2026/paper/main.tex:8`
- File: `/Users/shlee/codex/2026/eccv2026/paper/main.tex:43`
- File: `/Users/shlee/codex/2026/eccv2026/paper/main.tex:49`
- Why it matters: `year=2024`, placeholder submission ID, dummy authors/affiliations/emails signal “template state”, which weakens perceived maturity regardless of technical content.
- Recommendation: finalize review-mode metadata block and real author block before external circulation.

### [P1] Main evidence table mixes non-comparable regimes without protocol guardrails
- File: `/Users/shlee/codex/2026/eccv2026/paper/main.tex:328`
- File: `/Users/shlee/codex/2026/eccv2026/paper/main.tex:338`
- File: `/Users/shlee/codex/2026/eccv2026/paper/main.tex:343`
- Why it matters: Traditional VAD, heavy VLM, and efficient variants appear in one table with FPS/GFLOPs, but measurement protocol is under-specified (resolution, decode length, batching, precision, warmup, exact hardware parity).
- Recommendation: add a strict “evaluation protocol” table and footnotes for any values taken from prior work vs re-measured.

### [P1] Core metric consistency is ambiguous between Main Results and Ablation final configuration
- File: `/Users/shlee/codex/2026/eccv2026/paper/main.tex:350`
- File: `/Users/shlee/codex/2026/eccv2026/paper/main.tex:373`
- Why it matters: Main table reports AUC 84.8 for “Event-VLM (Ours)”, but ablation final row reports AUC 85.6. The relationship between “official final model” and “ablation final config” is not explicitly defined.
- Recommendation: define canonical final configuration and align all headline metrics to that setting.

### [P1] Statistical reliability is missing from all key results
- File: `/Users/shlee/codex/2026/eccv2026/paper/main.tex:326`
- File: `/Users/shlee/codex/2026/eccv2026/paper/main.tex:358`
- Why it matters: no mean±std, CI, repeated runs, or significance analysis; reviewers may interpret gains as single-run variance.
- Recommendation: report repeated-run stats for AUC/CIDEr/FPS and include confidence intervals.

### [P2] Stage-3 notation has a minor inconsistency (`TopK` vs `TopK-I`)
- File: `/Users/shlee/codex/2026/eccv2026/paper/main.tex:251`
- File: `/Users/shlee/codex/2026/eccv2026/paper/main.tex:256`
- Why it matters: small but visible notation inconsistency in the key method section.
- Recommendation: unify to one operator definition and introduce it once.

### [P2] Figure asset usage is suboptimal (`figure2_components.png` is present but unused)
- File: `/Users/shlee/codex/2026/eccv2026/paper/figures/figure2_components.png`
- File: `/Users/shlee/codex/2026/eccv2026/paper/main.tex:156`
- File: `/Users/shlee/codex/2026/eccv2026/paper/main.tex:417`
- Why it matters: only two figures are used; the draft would benefit from one explicit “component-wise latency/memory breakdown” figure.
- Recommendation: either integrate Figure 2 with a concrete role or remove to avoid artifact clutter.

### [P2] Appendix is good in breadth, but lacks failure-case evidence and protocol reproducibility checklist
- File: `/Users/shlee/codex/2026/eccv2026/paper/main.tex:469`
- File: `/Users/shlee/codex/2026/eccv2026/paper/main.tex:521`
- Why it matters: qualitative examples only show wins; no hard negatives/failures.
- Recommendation: add failure gallery + error taxonomy + mitigation discussion.

### [P3] Build-level formatting warnings remain (non-fatal)
- File: `/Users/shlee/codex/2026/eccv2026/paper/build/main.log:668`
- File: `/Users/shlee/codex/2026/eccv2026/paper/build/main.log:676`
- Why it matters: hyperref PDF string warning and multiple overfull boxes are not blockers, but reduce polish.
- Recommendation: clean title PDF-string handling and long-line wraps in Related Work / Results paragraphs.

## Are the experiments sufficient?
- Short answer: **No (for submission)**.
- They are sufficient for **Draft V1 claim shaping**, but insufficient for a strong ECCV-level evidence bar.

## Required Reinforcement (Next Wave)
1. Protocol table: resolution, frame sampling, decode length, precision, warmup, repeated runs, token budget.
2. Fairness declaration: which baselines are re-implemented vs cited, and under what parity constraints.
3. Statistical confidence: mean±std/CI for core metrics.
4. Efficiency decomposition: temporal skip gain vs spatial pruning gain vs decoding sparsity gain.
5. Failure analysis: at least 6-10 negative examples with causal categorization.
6. Canonical final model definition: one row, one metric tuple, consistent across all tables/claims.

## Overall Recommendation
- Keep current narrative skeleton.
- Treat next version as **evidence-hardening release** focused on protocol rigor and statistical defensibility.
