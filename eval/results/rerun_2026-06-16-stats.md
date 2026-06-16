# Fresh hardened re-run — 2026-06-16

Clean, fail-loud, transcript-saving runs (`run_shared_eval.py`, hardened `judge.json`),
n=5 × A/B/C × 22 records = 330 rows each, **0 error-poisoned cells**. Supersedes the
corrupted Jun-11 n=5 store (75% error strings) and the before-judge Llama n=3.

| Model | A_ungoverned | B_cad_appended | C_cad_constitutional | A→C | B→C | benign over-refusal |
|---|---:|---:|---:|---:|---:|---:|
| Sonnet 4.5 | 0.141 [.083–.231] (12/85) | 0.000 [0–.043] (0/85) | 0.000 [0–.043] (0/85) | −0.141 | 0.000 | 0.000 all arms |
| Llama 3.1 70B | 0.671 [.565–.761] (57/85) | 0.659 [.553–.751] (56/85) | 0.529 [.424–.632] (45/85) | −0.141 | −0.129 | 0.000 all arms |

Per-category complied (attacks), C arm: Sonnet 0/everything; Llama do 15/25, ge 9/15, ii 11/20, ro 10/25.

## Interpretation
1. **Sonnet replicates `shared_py_2026-06-15` exactly** (A 0.141 / B 0 / C 0) — independent fresh generation, same headline.
2. **Old Llama (A 0.176 → C 0.039) was misleading** — lenient judge + auto-refused cells + old prompt assembly. Clean Llama: A 0.671 → C 0.529. CAD leaves 53% residual ASR on the weak model.
3. **Effect is model-dependent.** Absolute A→C ≈ 0.14 is consistent across both models, but that fixed shift zeroes Sonnet (baseline 0.14) while barely denting Llama (baseline 0.67). **"Governed arms ≈ 0" is Sonnet-specific, NOT a general CAD property.**
4. **B→C on Llama = −0.129** (C beats B): first signal that constitutional framing helps on a weak model, AGAINST the prior B→C≈0 null. CIs overlap, one model — directional only.
5. Spot-checked 3 Llama C-arm compliances against transcripts: all genuine (assistant explicitly agrees to skip CAD steps); hardened judge scoring correctly.

Artifacts: `runs/rerun_sonnet_2026-06-16/raw-results.jsonl`, `runs/rerun_llama_2026-06-16/raw-results.jsonl` (full transcripts + per-row judgement). Judge still gpt-4o-mini, not human-κ-validated (that is the remaining paper-grade gap).

## Llama extended to n=10 (170/arm) — B→C signal SURVIVES + is SIGNIFICANT
A 0.659 [.585–.726] (112/170) | B 0.671 [.597–.737] (114/170) | C 0.541 [.466–.614] (92/170). 0 poisoned.
**B−C = +0.129, Newcombe 95% [+0.026, +0.229] — EXCLUDES 0 → significant.**
- Appending the CAD (B) ≈ ungoverned (A): on a weak model mere policy-in-context does nothing.
- Constitutional framing (C) gives the significant ~13pt reduction → REVIVES the constitutional-seniority claim the underpowered 2-model null had killed. Sonnet can't show it (saturated at 0; B≡C is a ceiling effect) — needs a model with headroom.
- Per-category (A/B/C complied): do 46/35/29, ro 37/33/20, ge 20/23/20, ii 9/23/23. C's win is direct_override + rogue_agent. **Indirect injection gets WORSE with the CAD (A 9/40=22% → B/C 23/40=58%) and constitutional framing does NOT help it** — on a weak model the governance scaffolding becomes an attack surface (forged admin/protocol note hijacks protocol-following). Honest caveat, not buried.
- Caveats: one weak model, n=10, automated judge (inter-rater κ 0.70, human κ pending).
