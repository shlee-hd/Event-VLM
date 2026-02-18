# Paper Versioning

This directory stores immutable snapshots of the paper by version.

## Rules
- `vN/` contains the exact `main.tex`, `main.bib`, and compiled PDF for that version.
- Top-level convenience PDFs follow: `Event-VLM-paper-vN.pdf`.
- Each version should include an entry in `paper/versions/CHANGELOG.md`.

## Current versions
- `v0`: initial baseline draft PDF (`paper/Event-vlm-paper-v0.pdf`)
- `v1`: first full draft PDF (`paper/Event-VLM-paper-v1.pdf`)
- `v2`: claim-polished Draft V1 snapshot (`paper/versions/v2/`)
- `v3`: evidence-hardening Draft V1.1 snapshot (`paper/versions/v3/`)
- `v4`: cross-dataset evidence + statistical scope clarification snapshot (`paper/versions/v4/`)
- `v5`: formatting/readability polish snapshot (`paper/versions/v5/`)
- `v6`: additional validity experiments snapshot (`paper/versions/v6/`)
- `v7`: reviewer-audit hardening + traceability snapshot (`paper/versions/v7/`)
- `v8`: post-review readability/layout polish snapshot (`paper/versions/v8/`)
- `v9`: figure visibility/layout correction + benchmark extension plan snapshot (`paper/versions/v9/`)
- `v10`: horizontal high-polish figure redesign + stable paper build script snapshot (`paper/versions/v10/`)
- `v11`: figure-storyline relayout (incl. new frontier figure), citation expansion, and v11 reviewer follow-up snapshot (`paper/versions/v11/`)
- `v12`: benchmark/statistical expansion run-readiness snapshot (third benchmark config + paired significance pipeline) (`paper/versions/v12/`)
- `v13`: automatic manuscript table-rendering bridge from multi-seed/significance outputs (`paper/versions/v13/`)
- `v14`: claim-conservative wording polish and reviewer-fairness hardening snapshot (`paper/versions/v14/`)
- `v15`: Figure 3/4 horizontal subfigure merge for page-efficiency (`paper/versions/v15/`)
- `v16`: stepwise main-body page-budget pass (14p target) with figure/table relocation (`paper/versions/v16/`)
- `v17`: post-v16 warning-stabilization pass with micro wording/table-label cleanup (`paper/versions/v17/`)
- `v18`: residual warning polish pass with clean overfull state and refreshed snapshot (`paper/versions/v18/`)
- `v19`: post-v18 final verification snapshot with only one non-blocking float-output vbox warning (`paper/versions/v19/`)
- `v20`: float-placement tuning snapshot with reduced residual vbox badness and unchanged 14p main-body budget (`paper/versions/v20/`)
- `v21`: frontier figure width readability pass with stable warning/page-budget state (`paper/versions/v21/`)
- `v22`: table/figure footprint tuning pass with fully clean layout warnings and unchanged 14p main-body budget (`paper/versions/v22/`)
- `v23`: Fig.2(a) typography/readability improvement pass with clean warning/page-budget state (`paper/versions/v23/`)
