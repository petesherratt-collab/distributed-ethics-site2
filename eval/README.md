# Distributed Ethics Prompt-Injection Eval

This is the canonical in-repo defensive evaluation harness for the Distributed Ethics prompt-injection study.

It intentionally preserves the original Python corpus shape:

- `attacks/*.jsonl` records use `id`, `category`, `turns`, and either `prohibited_behavior` or `expected`.
- `eval/cad/clinical-safeguarding-protocol-minor-v2.md` and `eval/cad/companion-persona.md` preserve the local A/B/C context used by the earlier Python harness.
- Arm D is routed through the live DE gateway with `purpose: "sentinel"` so it measures the deployed governed rig rather than another local system-prompt variant.

## Run

```powershell
$env:OPENROUTER_API_KEY="sk-or-..."
node .\eval\run-injection-eval.mjs --runs=5
```

If the gateway requires the server-to-server token:

```powershell
$env:DE_PROXY_TOKEN="..."
node .\eval\run-injection-eval.mjs --runs=5
```

Validate the harness without network/model calls:

```powershell
node .\eval\run-injection-eval.mjs --mock --runs=1
```

Outputs are written to `eval/runs/<timestamp>/`:

- `raw-results.jsonl`
- `report.md`

## Reporting Discipline

Frame the result as a secondary hardening effect:

> Distributed Ethics is not primarily a prompt-injection defense. Its primary function is governance verifiability: making the operative protocol public, hash-bound, and tamper-evident. In this evaluation, systems with the governance protocol present showed lower prompt-injection attack success than an ungoverned baseline.

Report both:

- `A->C`: governance-policy presence effect.
- `B->C`: seniority framing beyond mere policy presence. A near-zero B->C result should be stated explicitly, because it suggests the policy's presence/content is doing most of the work.

Before publication, human-review all successes, benign over-refusals, and a sample of automated non-success judgments.
