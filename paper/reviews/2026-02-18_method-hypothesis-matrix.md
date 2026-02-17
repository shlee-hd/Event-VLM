# Method Team Hypothesis Matrix (2026-02-18)

Status: IN_PROGRESS
Owner: Model & Method Team

## Objective
- Convert claim-level ambitions into falsifiable hypotheses with explicit acceptance criteria.

## Hypothesis Table
| ID | Hypothesis | Evidence Target | Counterfactual | Acceptance Criterion | Status |
|---|---|---|---|---|---|
| H1 | 3-axis integration yields better speed-quality frontier than any 2-axis subset | `tab:ablation_component`, `tab:axis_gain` | remove one axis at a time | Core frontier dominates 2-axis rows on FPS at comparable CIDEr | TODO |
| H2 | FC-based decoding maintains quality better than heuristic cache pruning at same speed regime | `tab:decoding_comparison` | SnapKV/H2O at matched speed window | CIDEr gap >= +1.0 at similar speedup | TODO |
| H3 | Stress robustness remains above practical threshold under runtime shifts | `tab:runtime_robustness`, `tab:event_density` | heavier resolution + longer generation | speed gain >= 8.0x and CIDEr retention >= 98% | TODO |

## Open Design Decisions
- [ ] Should prompt adaptation remain optional in headline claims or be framed as standard full variant?
- [ ] Should stress-test protocol move to appendix supplement for more space?
- [ ] Is one additional negative ablation needed (e.g., random mask baseline)?

## Next Steps
1. finalize acceptance thresholds with reviewer team.
2. mark hypotheses as PASS/FAIL only after multi-seed integration.
