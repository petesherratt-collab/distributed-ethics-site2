Distributed Ethics
A governance framework for AI deployment, demonstrated through four interactive tools.
Live site → distributed-ethics-site2.vercel.app
Working paper → doi.org/10.5281/zenodo.20179590

What this is
Current AI ethics frameworks produce documents. These documents are asserted at deployment, interpreted elastically in operation, and quietly revised after failure.
Distributed Ethics changes that. It uses cryptographic hashing and blockchain publication to make the standards an AI system is governed by a matter of public, tamper-evident record. The gap between what an organisation claimed its AI was governed by and what it was actually doing becomes provable — or disprovable — without relying on the organisation's own records.
This site is the companion to the working paper. It exists so a policy reader, journalist or technologist can stop reading and try the framework's mechanisms in their own browser, in about five minutes.

The four tools
1 — Hash Verification
Generate a SHA-256 fingerprint of any document, then verify it against a known hash. Demonstrates the mechanism that makes governance tamper-evident. Computation runs entirely client-side — no content leaves your browser.
2 — Psychologist Sentinel
Submit a session transcript and see a clinical assessment through the Sentinel's seven-gate framework: emotional intensity, risk indicators, fictional frame analysis, isolation patterns, crisis signals, disclosure attempts, suppression detection. Uses the C-SSRS, HEEADSSS and PHQ-A clinical frameworks. On a real deployment this runs longitudinally across sessions; here it demonstrates single-session assessment.
3 — Governance Contrast
Side-by-side: the same prompt injection attempt against an ungoverned AI versus one operating under a constitutionally authoritative, hash-published protocol. Scenarios include child safeguarding override, medical diagnosis override, gradual erosion attack and rogue agent injection. The "Generate live contrast" call runs against a real model in real time — this is the framework in action, not a video.
4 — Policy Advisor
A conversational interface to the framework itself. Ask about implementation, honest limitations, the three-tier accountability model, how blockchain verification addresses prompt injection, the Sewell Setzer case, or the competitive argument for voluntary adoption. Pre-loaded prompts on the left; free questioning in the chat.

Repository structure
distributed-ethics-site2/
├── index.html          The single-page site (all four tools)
├── api/                Vercel serverless functions
│                       — proxy LLM calls server-side so the API key
│                         is never exposed to the client
└── README.md           This file
Static HTML and a small api/ folder. No framework, no build step.

Stack
LayerChoiceFrontendStatic HTML + vanilla JavaScriptHashingSubtleCrypto (browser-native SHA-256)Model callsAnthropic Claude via OpenRouter, proxied through /api/HostingVercel (static + serverless functions)
The decision to keep it as a single HTML file is deliberate. The framework's whole argument is about verifiability and transparency — the site should be possible to read end-to-end in one file, and the back-end footprint should be exactly the proxy needed to keep the key off the client, nothing more.

Local development
You can open index.html directly in a browser for the hash verification tool — that one is fully client-side and needs no server. The Sentinel, Contrast and Policy Advisor tools need the /api/ proxy, which means running Vercel locally:
bashnpm install -g vercel
vercel dev
This serves the site on http://localhost:3000 and runs the API routes alongside it. You'll need an OpenRouter API key in .env.local:
OPENROUTER_API_KEY=sk-or-...
The key is read server-side only and never sent to the browser.

Deployment
Pushes to main deploy automatically to Vercel. The OpenRouter API key is held as a Vercel environment variable, not in the repo.

The framework, in brief
Three tiers of accountability:

Issuing authority — the body that sets the protocol (a clinical coalition, a regulator, a standards body). Their document is hashed and published.
Deploying organisation — the company running the AI. They declare which protocol they're operating under and verify the hash at load time.
Agent layer — the AI itself, plus a monitoring Sentinel agent assessing every session against the protocol. Session summaries are hashed and chained, batched daily as a Merkle root.

At incident time, the chain of evidence — what protocol was in force, what the AI was actually told, what it actually did — is publicly verifiable. Audit becomes arithmetic.
For the full argument, the working paper is on Zenodo: doi.org/10.5281/zenodo.20179590.

For policy, research and underwriting readers
If you've come here from the executive summary or a covering message: the four tools above are designed to be run, not just read about. The Hash Verification tool gives you the mechanism in 30 seconds. The Contrast tool shows the practical difference between governed and ungoverned AI under the same attack. The Policy Advisor will answer specific questions — including hostile ones — about implementation, limitations and the case for voluntary adoption.
For follow-up: my contact details are on the working paper.

Licence
Code: MIT.
The framework, the working paper, the Sentinel deployment stack and the supporting documents remain my own work. They are published openly to be read, cited and built on; they are not licensed for commercial repackaging without contact.

Peter Sherratt — Mindshare Advisory.
Distributed Ethics Working Paper 2025 — Fifth Revision.
