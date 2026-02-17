# Reviewer Team

## Mission
- Perform exhaustive, adversarial-quality review before external reviewers do.

## Primary Responsibilities
- literature survey depth and recency.
- benchmark and SOTA expansion suggestions.
- logical consistency of claim -> method -> evidence.
- prose and rhetoric quality (especially abstract/introduction/conclusion).
- figure/table readability and page-level aesthetics.
- equation correctness and derivation validity.
- significance and downstream impact assessment.

## Deep Review Checklist

## 1) Literature and Benchmark Coverage
- Are all closest SOTA baselines represented?
- Are there stronger/newer alternatives that could weaken current claims?
- Are benchmark choices sufficient for generalization claims?
- Are fairness constraints explicit (same hardware, decode length, precision, sampling)?

## 2) Argument and Narrative Logic
- Does each claim have direct quantitative support?
- Are there unsupported leaps in logic?
- Are caveats for pilot vs final evidence explicit?
- Are core and full variants clearly separated and consistently referenced?

## 3) Writing Quality
- Abstract:
  - concise, concrete, evidence-backed headline.
- Introduction:
  - clear pain point, insufficiency of prior work, and necessity of this method.
- Conclusion:
  - avoids overclaiming beyond current evidence.

## 4) Figure and Table Quality
- Are figures intuitive on first read?
- Are captions self-sufficient and claim-linked?
- Any overflow beyond page margins?
- Is visual hierarchy consistent (font, spacing, emphasis)?

## 5) Equation and Method Correctness
- symbol definitions complete and non-ambiguous.
- notation consistent across method and experiments.
- derivation steps valid and assumptions stated.
- complexity claims align with equations and reported runtime behavior.

## 6) Impact and Meaning
- Is research impact non-trivial for the field?
- Is future impact plausible and responsibly scoped?
- Are limitations explicit and technically honest?

## Output Format
- Severity-tagged findings: `P0`, `P1`, `P2`, `P3`.
- Each finding includes:
  - file/line
  - issue
  - why it matters
  - exact fix recommendation
