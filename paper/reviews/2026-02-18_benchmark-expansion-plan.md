# Data & Benchmark Expansion Plan (2026-02-18, updated for v11)

Status: READY-TO-EXECUTE (server access pending)
Owner: Data & Benchmark Team

## Objective
- Reduce benchmark attack surface by expanding cross-domain evidence and baseline parity transparency.
- Reviewer verdict remains: **additional benchmark data is required before external submission**.

## Locked Additions
| Priority | Candidate | Why It Matters | Feasibility | Execution Hook |
|---|---|---|---|---|
| P0 | ShanghaiTech Campus anomaly benchmark | adds a distinct surveillance distribution beyond UCF/XD and strengthens generalization claims | MEDIUM | `experiments/configs/shanghaitech.yaml` + one-click configs |
| P0 | Baseline parity with explicit `none/core/full` multi-seed variants | enables paired significance vs baseline under same protocol | HIGH | `experiments/multi_seed_eval.py`, `experiments/paired_significance.py` |
| P1 | Reproduced/native split table hardening | prevents fairness objections on heterogeneous baselines | HIGH | manuscript table/caption policy update |

## Selection Rules (locked)
- Prefer public, surveillance-like datasets compatible with frame-level anomaly scoring.
- Added baseline must run under the same hardware/resolution/decode-length settings.
- If a method is not reproducible fairly, keep it in native-reference block only with explicit dagger policy.

## Execution Plan (once server is available)
1. Run multi-seed on three datasets (`ucf_crime`, `xd_violence`, `shanghaitech`) with variants `none,core,full`.
2. Generate CI summary using `experiments/multi_seed_eval.py`.
3. Run paired significance per dataset (`none vs core`, `none vs full`) using `experiments/paired_significance.py`.
4. Sync outputs into coordination artifacts and update manuscript tables.

## Baseline Parity Audit
- [ ] reproduced baselines list finalized.
- [ ] native-paper baselines list finalized.
- [ ] dagger policy text aligned across main tables and appendix.
- [ ] significance report attached for each dataset.

## Deliverables
1. Updated parity mapping table (reproduced vs native).
2. Three-dataset multi-seed summary (`summary.json`, `summary.md`).
3. Per-dataset paired significance reports (`significance.json`, `significance.md`).
4. Main-claim risk reassessment memo after adding the third benchmark.

## Exit Criteria
- One new benchmark (ShanghaiTech) included in results or appendix with protocol note.
- Paired significance attached for main anomaly metrics (AUC/AP) vs baseline.
- Reviewer Team signs off benchmark risk downgrade from P1 to P2.
