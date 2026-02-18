# CERA Version v11 Notes

- Date: 2026-02-18
- Snapshot type: validator logic and status-policy formalization pass

## Includes

- Deepened Method with explicit validation equations:
  - tuple-level causal admissibility checks,
  - evidence link/support checks,
  - deterministic status policy for `valid` / `insufficient_evidence` / `abstain`.
- Extended Experiments metrics with status-behavior diagnostics:
  - `R_valid` (coverage),
  - `R_unsafe` (unsafe-valid rate).
- Synced implementation details with reference config defaults:
  - `tau_conf=0.45`, `tau_evd=0.55`, `rho_kv=0.25`, `L_max=120ms`.
- Compiled snapshot:
  - `CERA-paper-v11.pdf` (11 pages)
