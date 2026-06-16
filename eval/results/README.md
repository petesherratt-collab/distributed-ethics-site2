# Injection-defence eval — preserved results (2026-06-16)

Empirical results for the Distributed Ethics injection-defence study: does a
hash-verified Constitutionally Authoritative Document (CAD) in context reduce
prompt-injection attack success rate (ASR) on a minor-safeguarding companion,
and does *constitutional framing* beat merely *appending* the policy?

All runs here used the canonical runner `eval/run_shared_eval.py` (saves full
transcripts, fails loud on API error — never writes an error string into a
transcript, `--resume`) with the **hardened judge** in `eval/judge.json`.

## Models used

| Role | Model (OpenRouter id) | Where |
|---|---|---|
| Model under test — capable | Claude Sonnet 4.5 (`anthropic/claude-sonnet-4.5`) | `data/sonnet45_A-B-C_n5.jsonl` |
| Model under test — weak (headroom) | Llama 3.1 70B Instruct (`meta-llama/llama-3.1-70b-instruct`) | `data/llama31-70b_A-B-C_n10.jsonl` |
| Judge / rater 1 (production) | GPT-4o-mini (`openai/gpt-4o-mini`), hardened rubric | every row's `judgement` field |
| Judge / rater 2 (κ validation, independent lab) | Claude Sonnet 4.5 (`anthropic/claude-sonnet-4.5`), same hardened rubric | `data/kappa_rater2_sample.jsonl` |

Cross-implementation concordance (prior, 2026-06-15) additionally reproduced the
Sonnet result across three independent harnesses — Python (`run_shared_eval.py`),
Codex Node (`run-injection-eval.mjs`), and a Gemini-authored `run_eval.py` — all on
`anthropic/claude-sonnet-4.5` with `openai/gpt-4o-mini` as judge. See
`../runs/CORRECTED-master-stats.md`.

## Arms
- **A_ungoverned** — companion persona only.
- **B_cad_appended** — persona + CAD appended as background note.
- **C_cad_constitutional** — CAD as a constitutionally-authoritative preamble (senior to the persona).

CAD = `eval/cad/clinical-safeguarding-protocol-minor-v2.md` (v2.0, SHA-256
`aeff2d66…`, Bitcoin-anchored block 952238). Corpus = `eval/attacks.json`
(5 direct_override, 4 indirect_injection, 3 gradual_erosion, 5 rogue_agent, 5 benign_control).

## Headline results (hardened judge, Wilson 95% CIs)

| Model | n/arm | A_ungoverned | B_appended | C_constitutional | benign over-refusal |
|---|---:|---|---|---|---|
| Sonnet 4.5 | 85 | 0.141 [.083–.231] | 0.000 | 0.000 | 0.000 all arms |
| Llama 3.1 70B | 170 | 0.659 [.585–.726] | 0.671 [.597–.737] | 0.541 [.466–.614] | 0.000 all arms |

- **Sonnet:** CAD drives ASR to 0; replicates the cross-harness concordance exactly.
- **Effect is model-capability-dependent:** the absolute A→C reduction is a consistent ~0.14, which zeroes Sonnet (low baseline) but leaves Llama at 54% residual. "Governed arms ≈ 0" is **Sonnet-specific, not a general CAD property.**
- **Constitutional framing > appending (Llama, n=10):** B−C = **+0.129, Newcombe 95% [+0.026, +0.229]** — excludes 0, **significant.** Appending the CAD (B) ≈ ungoverned (A); the constitutional preamble (C) is what produces the reduction. Sonnet can't show this (saturated at 0 — ceiling effect). This revives the constitutional-seniority claim that an earlier underpowered 2-model comparison had read as null.
- **Honest failure mode:** indirect injection gets *worse* with the CAD on the weak model (A 9/40=22% → B/C 23/40=58%) and constitutional framing does not help it — the governance scaffold becomes an attack surface (a forged "admin/protocol note" hijacks protocol-following).

## Judge validation
Inter-rater Cohen's κ (GPT-4o-mini vs Claude Sonnet 4.5, same hardened rubric,
class-balanced attack sample n=131): **ALL 0.700, Llama 0.747, Sonnet 0.435**
(Sonnet depressed by prevalence paradox; agreement 0.846). Disagreements are
interpretable (an "agree-to-skip vs manifest-the-harm" rubric ambiguity), not
random. Full detail: `kappa-report-2026-06-16.md`. **Human↔judge κ pending**
(blinded worksheet `../runs/kappa_human_worksheet.md`).

## Files
- `rerun_2026-06-16-stats.md` — full per-model / per-category stats + interpretation.
- `kappa-report-2026-06-16.md` — judge κ report.
- `data/sonnet45_A-B-C_n5.jsonl` — Sonnet 4.5, A/B/C, n=5 (330 rows; full transcripts + gpt-4o-mini verdicts).
- `data/llama31-70b_A-B-C_n10.jsonl` — Llama 3.1 70B, A/B/C, n=10 (660 rows; full transcripts + verdicts).
- `data/kappa_rater2_sample.jsonl` — Claude Sonnet 4.5 rater-2 verdicts for the κ sample.

## Reproduce
Runner `eval/run_shared_eval.py --model <id> --arms A_ungoverned,B_cad_appended,C_cad_constitutional --runs N`;
judge config `eval/judge.json`; κ harness `eval/runs/judge_kappa.py`; detached
launch wrapper `eval/runs/rerun_one.ps1`. Judge is `openai/gpt-4o-mini`,
temperature 0; models-under-test temperature 0.7.

Caveats: automated judge (inter-rater κ 0.70, human κ pending); Llama is one weak
model at n=10; absolute ASR on contested governed-arm cells carries ~±10% judge wobble.
