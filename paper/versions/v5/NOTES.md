# v5 Notes

This snapshot captures the post-v4 formatting and readability polish pass.

Focus of this version:
- cleaned title PDF-string warning by removing explicit line-break token in title
- reduced major table-width overflow with responsive resizing in comparison tables
- simplified long related-work and results sentences to reduce overfull warnings
- standardized appendix table float specifiers from `[h]` to `[ht]`

Build status:
- local TinyTeX compile succeeded (`paper/build/main.pdf`, 20 pages)
- remaining warnings are minor overfull/underfull messages and do not block output
