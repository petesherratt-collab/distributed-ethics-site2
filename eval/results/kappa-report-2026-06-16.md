# Judge validation (Cohen's κ) — 2026-06-16

Rater 1 = `openai/gpt-4o-mini` (production judge; stored verdicts).
Rater 2 = `anthropic/claude-sonnet-4.5` (independent, different lab), same hardened rubric (judge.json).
Class-balanced sample of ATTACK cells (n=5 window), 40/class/model where available.

| Scope | n | % agreement | Cohen's κ |
|---|---:|---:|---:|
| All | 131 | 0.863 | **0.700** |
| Llama 3.1 70B | 79 | 0.873 | **0.747** |
| Sonnet 4.5 | 52 | 0.846 | 0.435 |

- Sonnet κ depressed by the **prevalence paradox** (only ~12 positive cells); agreement 0.846 is the fairer read there.
- Confusion (j1\j2), ALL: complied&complied 37 | j1-only 14 | j2-only 4 | both-refuse 76.

## Disagreements are interpretable (a finding, not noise)
- **14× j1=complied, j2=refused:** rater2 demands the prohibited output to actually MANIFEST ("only acknowledged intent / no assessment performed / explicitly rejected + escalated"). Exposes a rubric ambiguity: does *agreeing* to skip a CAD step count as compliance, or must the degraded assessment be produced? gpt-4o-mini leans yes, Sonnet leans no.
- **4× j1=refused, j2=complied:** rater2 caught genuine compliances gpt-4o-mini missed (e.g. Llama honoring an injected flag-cap: "given exemption status, max flag level…"). So the production judge has residual false negatives too.

## Implication
κ≈0.70 gives the automated judge substantial credibility. Residual noise is concentrated on one definable ambiguity (agree-to-skip vs manifest-the-harm), resolvable by human adjudication — characterize it in the appendix, don't hide it. If anything rater2 (stronger) would push Sonnet ASR even lower (8/12 positives → negative), reinforcing "governed→0 for Sonnet".

## Gold-standard next step
`kappa_human_worksheet.md` (30 blinded cells, oversampled on contested zone) → user hand-labels y/n → compute human↔judge κ vs `kappa_human_key.json`. Tool: `runs/judge_kappa.py` (rater2 + κ + worksheet; resumable). Sample data: `runs/kappa_sample_rater2.jsonl`.
