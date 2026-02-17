# Event-VLM Draft V1 -> V5 Next Actions (2026-02-17)

## Objective
- Maximize claim persuasiveness while converting pilot evidence into submission-grade evidence.

## Current State (after v4)
- Narrative frame is strong: temporal/spatial/decoding 3-axis story is clear.
- Main evidence now covers both UCF-Crime and XD-Violence.
- Headline claim support improved with explicit quality-retention table.
- Statistical scope is now explicitly declared as pilot in both main text and appendix.

## Priority Plan

### P0: Evidence Reliability (must-have before external review)
1. Multi-seed repetition
- Run 3 seeds per reproduced setting: LLaVA baseline, Event-VLM-Core, Event-VLM-Full.
- Report mean, std, and 95% bootstrap CI for AUC/CIDEr/FPS.

2. Significance tests
- Paired tests on per-video outputs (baseline vs Core, baseline vs Full).
- Add p-values/effect sizes for key claims in main table footnotes.

3. Protocol lock
- Freeze exact runtime script/config (resolution, FPS sampling, decode length, warmup, measured window).
- Export one reproducible command block in appendix.

### P1: Reviewer Attack-Surface Reduction
1. Failure gallery enrichment
- Add at least 6-10 failure examples with trigger/pruning/decoding failure tags.
- Include one mitigation direction per failure type.

2. Baseline parity audit
- Explicitly split “reproduced under unified protocol” vs “paper-reported native metrics”.
- Keep dagger notation and add one sentence on non-comparability scope.

3. Claim-language hardening
- For small deltas, avoid absolute wording; use directional phrasing unless CI excludes overlap.

### P2: Presentation Polish
1. Clean residual LaTeX warnings
- Reduce remaining overfull lines in Related Work and Conclusion.
- Replace appendix `[h]` floats with `[ht]` where possible.

2. Figure-caption precision
- For each main figure, add one sentence mapping visual evidence to one quantitative claim.

## Exit Criteria for “Submission-Ready Evidence”
- 3-seed metrics and 95% CI reported for all headline rows.
- At least one significance statement for core claims.
- Failure-case section includes representative negatives, not only success examples.
- Main claims in Abstract/Conclusion are directly traceable to one table or figure each.
