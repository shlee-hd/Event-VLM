# v10 Notes

This snapshot captures horizontal figure redesign and stable LaTeX build routing.

Focus of this version:
- replaced Fig.1/Fig.2/Fig.3 with high-polish horizontal layouts tuned for paper page flow
- aligned figure visual tone (typography, palette, spacing) for a consistent presentation layer
- removed figure trim-heavy include policy in `main.tex` and switched to width-first placement
- added `scripts/build_paper.sh` to eliminate PATH-dependent LaTeX build failures

Build status:
- compile command: `bash scripts/build_paper.sh`
- result: success (`paper/build/main.pdf`, 23 pages)
- output PDF size: ~918 KB

Known warnings:
- minor text-level overfull/underfull hbox warnings remain in narrative sections (non-fatal)
