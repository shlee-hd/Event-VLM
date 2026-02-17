# v9 Notes

This snapshot captures post-v8 figure verification and layout correction.

Focus of this version:
- fixed Fig.1 clipping/scale issue by removing height cap and using safe trim (`0 130 0 20`)
- corrected Fig.2 role/caption to hazard-aware components and removed in-image title overlap with top trim (`0 12 0 90`)
- applied conservative Fig.3 trim (`12 12 12 12`) for cleaner framing without content loss
- updated nearby method-analysis sentence so figure semantics and prose are consistent

Build status:
- local TinyTeX compile succeeded (`paper/build/main.pdf`, 23 pages)
- snapshot PDF exported to `paper/versions/v9/Event-VLM-paper-v9.pdf`
- convenience copy exported to `paper/Event-VLM-paper-v9.pdf`

Known warnings:
- minor overfull/underfull hbox lines remain in narrative text blocks (non-fatal)
- no fatal TeX errors; PDF output is complete
