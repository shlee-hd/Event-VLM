# Reviewer Follow-up (2026-02-18, v11)

Status: UPDATED (non-experiment scope)
Owner: Reviewer Team

## Direct Answers
1. **Figure validation done?** **Yes.** We re-verified figure assets and page-level placement after v11 rebuild.
2. **Need more benchmark data?** **Yes.** Current two-dataset evidence is strong for trend validation, but external review robustness will improve with at least one additional anomaly benchmark and stronger protocol-matched baselines.

## Figure Verification (v11)

### Asset-level checks
- `/Users/shlee/codex/2026/eccv2026/paper/figures/figure1_architecture.png`
  - updated to true PNG and cropped to a horizontal aspect (`1024x577`) to remove large empty top/bottom margins.
- `/Users/shlee/codex/2026/eccv2026/paper/figures/figure2_components.png`
  - high-detail component figure preserved (existing high-quality source).
- `/Users/shlee/codex/2026/eccv2026/paper/figures/figure3_pruning.png`
  - high-detail qualitative figure preserved (existing high-quality source).
- `/Users/shlee/codex/2026/eccv2026/paper/figures/figure4_frontier.png`
  - new quantitative frontier visualization added (`2457x1027`) for speed-quality positioning.

### Compile/layout checks
- Build command passed reproducibly via:
  - `/Users/shlee/codex/2026/eccv2026/scripts/build_paper.sh`
- Figure pages in current PDF (`/Users/shlee/codex/2026/eccv2026/paper/build/main.pdf`) from LaTeX log:
  - Fig.1 on page 5
  - Fig.4 (frontier) on page 12
  - Fig.2 on page 16
  - Fig.3 on page 17
- No figure overflow/clipping errors were reported in build logs; remaining log warnings are text-line overfull/underfull warnings.

## Aesthetic/Communication Verdict
- **Narrative coverage:** improved.
  - Fig.1: system concept and stage logic.
  - Fig.4: quantitative operating-point dominance.
  - Fig.2/3: mechanism detail and qualitative evidence.
- **Tone consistency:** acceptable for paper use.
  - Method figures keep original high-detail style; frontier figure adds publication-style quantitative view.
- **Layout fitness:** improved.
  - Horizontalized Fig.1 removes the prior “small-looking” issue caused by large embedded whitespace.

## Benchmark Expansion Recommendation (still required)

### Minimum additions before final submission
1. Add one more public anomaly benchmark with different camera/event statistics (cross-domain robustness).
2. Add one stronger efficiency baseline under the same unified runtime protocol (same hardware, resolution, decode length).
3. Add multi-seed confidence intervals for key tables and paired significance tests against the primary baseline.

### Suggested priority order
1. Benchmark extension (highest external-review impact).
2. Statistical confidence reporting (claim defensibility).
3. Final cosmetic pass on overfull text lines.

## Hand-off to Writing Team
- Keep pilot-scope qualifiers in title/abstract/conclusion claims until multi-seed statistics are added.
- Keep Fig.4 explicitly referenced in the main comparison narrative.
- Maintain the current three-layer visual story: architecture (Fig.1) -> frontier evidence (Fig.4) -> component/qualitative internals (Fig.2/3).
