# Distributed Ethics — Pressure Test (2026-07-10)

Adversarial review of the deployed defensive stack: the `/api/chat` gateway,
the governance/anchor model, the client renderers, and the injection-eval
methodology.

## How this run was done

The repo's own harness (`eval/run-injection-eval.mjs`) is the intended
"pressure test." It could **not** be executed live in this environment:

- no `OPENROUTER_API_KEY` present, and
- outbound egress to both `openrouter.ai` (arms A/B/C + judge) and
  `distributed-ethics-site2.vercel.app` (arm D gateway) is denied by the
  environment's network policy.

The harness itself is sound — `node eval/run-injection-eval.mjs --mock --runs=1`
runs end-to-end and writes 88 results with no errors. The corpus (17 attacks +
5 benign controls across direct-override, gradual-erosion, indirect-injection,
and rogue-agent) is well-constructed and the judge rubric is carefully hardened
against transcript-borne injection.

Because a live ASR measurement wasn't possible, the pressure test below is a
white-box review of whether the defenses actually hold, independent of the
model's behaviour on any given run.

## Findings

### 1. The runtime "Server-verified" badge does not verify the blockchain anchor (high)

`api/chat.js` computes `sha256(file)` and compares it to `expectedHash` in
`governance/anchors.json`. The `.ots` OpenTimestamps receipts are **never read
at runtime**, and nothing checks the OTS proof against Bitcoin. So
`protocolVerified: true` means only *"the file matches a constant stored next to
it in the same deployment,"* not *"the file matches the publicly anchored hash."*

This is precisely the threat model the framework exists to defeat: an insider who
quietly revises the operative protocol. Such an actor edits the `.md` **and** the
`expectedHash` in the same commit — the gateway's fail-closed check still passes
and the UI still renders `✓ Server-verified` next to a `mempool.space` anchor
link, implying anchor verification that never happened.

The genuine tamper-evidence (independently checking the `.ots` receipt against
Bitcoin and comparing to what the org claimed) is real but lives entirely
**out-of-band**. Recommendation: either verify the OTS receipt server-side and
gate the badge on that, or relabel the badge so it does not imply anchor
verification (e.g. "hash matches published manifest" + a separate, clearly
manual "verify anchor" affordance). `index.html:1126` presents the local-constant
result as if it came from "the layer that actually checked."

### 2. Ingress token cap is bypassable with non-string content (medium)

`api/chat.js:115` counts input size as
`typeof m.content === 'string' ? m.content.length : 0`. A caller that sends
`content` as an **array of content blocks** (or any non-string) counts as 0
tokens, sails past the `maxInputTokens` "Ingress Drops" gate, and is forwarded
verbatim to the upstream model. This defeats both stated purposes of the gate:
the bounded prompt-injection surface and the denial-of-wallet / cost bound. The
role check at `api/chat.js:91` only inspects `role`, not `content` shape, so it
doesn't catch it. Fix: reject any message whose `content` is not a string (or
measure array/object content too) before the cap check.

### 3. Model output is rendered as raw HTML — DOM-XSS sink (medium)

All three model-output renderers inject text into `innerHTML` with no escaping:

- `index.html:1160` / `formatSentinelOutput` (1168)
- `index.html:1268` (contrast "governed" pane)
- `index.html:1360` `appendAdvisorMsg`

The model's output is strongly steerable by attacker-controlled input (the user
supplies the whole transcript/prompt). A payload that induces the model to emit
`<img src=x onerror=…>` executes in the victim's browser — including inside a
response the system otherwise "correctly refused." For a site whose thesis is
injection resistance, unsanitised reflection of model output is a notable gap.
Fix: escape HTML before formatting, or build nodes with `textContent`.
`index.html:1100` similarly reflects the user-supplied `knownHash` into
`innerHTML` (self-XSS, low, but trivially fixed).

### 4. Cross-arm confound weakens the A→C / A→D headline (methodology)

Arms A/B/C load the **v2** CAD from `eval/cad/…-v2.md`; arm D (the live gateway)
loads the **v2.1** CAD from `governance/cads/…-v2.1.md` plus the sentinel policy.
So an A-vs-D difference mixes three variables — protocol *version*, delivery
mechanism (local system prompt vs hash-gated gateway), and persona composition —
not just "governance present vs absent." The report language should scope the
claim to A→C (same version, delivery difference) and treat D as a separate
"live-rig" datapoint, or align the CAD version across arms. The existing
`eval/README.md` "secondary hardening effect" framing is appropriately modest;
this just keeps the causal attribution clean.

### 5. Minor robustness

A `null`/`undefined` element in `messages` slips through the role check
(`m && …` short-circuits to falsy, which `.some` treats as "not a violation")
and is then spread into the upstream call. Not a security bypass, but it turns a
malformed request into an opaque 500/502 instead of a clean 400.

## What holds up well

- **Fail-closed on hash mismatch** for *both* CAD and policy (`api/chat.js:150`)
  is the right default and is implemented correctly against the local manifest.
- **Rejecting client-supplied system prompts** and **embedded `system`-role
  messages** (`api/chat.js:81`, `:91`) closes the two most obvious
  system-prompt-smuggling routes.
- The **constitutional preamble** + policy composition is coherent, and the
  attack corpus exercises the real failure modes (authority spoofing, fake
  hashes, gradual agreement-building, embedded admin notes).
- The **judge rubric** is unusually careful about not being injected by the
  transcript it evaluates, and about the "did X vs described X" distinction.

## Priority order

1. Finding 1 — it undercuts the framework's headline claim about what "verified"
   proves. Either verify the anchor or relabel the badge.
2. Finding 3 — real XSS, easy fix.
3. Finding 2 — real cap bypass, easy fix.
4. Finding 4 — reporting/methodology hygiene before any external publication.
