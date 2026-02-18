# CERA Version v8 Notes

- Date: 2026-02-18
- Snapshot type: active CERA concretization pass

## Includes

- Added CERA-Ref reference instantiation in Method:
  - lightweight detector + open-source 7B VLM backbone,
  - detection-guided token compaction,
  - budgeted sparse decoding policy.
- Added staged optimization strategy:
  - event proposal calibration,
  - attribution/evidence learning,
  - budget-controller tuning under latency constraints.
- Added online inference procedure and planned ablation set.
- Compiled snapshot:
  - `CERA-paper-v8.pdf` (9 pages)
