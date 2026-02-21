# Measured Replacement Checklist

Use this checklist when external-server results are available.

## 1) Inputs

- `cera/experiments/results/main/summary/main_summary.csv`
- `cera/experiments/results/ablation/summary/ablation_summary.csv`
- `cera/experiments/results/stats/significance/...`
- `cera/experiments/results/stats/paper_tables/paper_table_stub.tex`

## 2) Replace in `main.tex`

- Block `MEASURED_SWAP_START/END:main_results`
- Block `MEASURED_SWAP_START/END:ablation_results`
- Block `MEASURED_SWAP_START/END:error_breakdown`

## 3) Narrative updates

- Replace non-empirical notice with measured-run note.
- Update Conclusion from projected wording to measured findings.
- Add seed-count and significance outcomes from stats outputs.

## 4) Build and snapshot

- `make -C cera/paper pdf`
- Verify references/tables in PDF.
- Snapshot into `cera/paper/versions/vN/`.

