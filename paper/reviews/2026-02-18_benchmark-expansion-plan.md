# Data & Benchmark Expansion Plan (2026-02-18)

Status: IN_PROGRESS
Owner: Data & Benchmark Team

## Objective
- Reduce benchmark attack surface by expanding cross-domain evidence and baseline parity transparency.

## Candidate Additions
| Priority | Candidate | Why It Matters | Feasibility | Notes |
|---|---|---|---|---|
| P0 | Add one extra surveillance anomaly benchmark | improves generalization credibility | MEDIUM | choose dataset with available annotations compatible with current pipeline |
| P0 | Add one stronger efficient VLM baseline | protects against "weak baseline" criticism | MEDIUM | keep unified protocol where reproducible |
| P1 | Add explicit reproduced/native split table | fairness transparency | HIGH | can be done without extra experiments |

## Baseline Parity Audit
- [ ] reproduced baselines list finalized.
- [ ] native-paper baselines list finalized.
- [ ] dagger policy text aligned across main tables and appendix.

## Deliverables
1. updated parity mapping table.
2. benchmark expansion recommendation with cost/time estimate.
3. impact on main-claim risk assessment.
