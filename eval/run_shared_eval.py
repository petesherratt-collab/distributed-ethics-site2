#!/usr/bin/env python3
import argparse, json, os, time
from pathlib import Path
from urllib import request, error

ROOT = Path(__file__).resolve().parent
OPENROUTER = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "anthropic/claude-sonnet-4.5"
DEFAULT_GATEWAY = "https://distributed-ethics-site2.vercel.app/api/chat"
ARM_ORDER = ["A_ungoverned", "B_cad_appended", "C_cad_constitutional", "D_cad_plus_sentinel"]

def load_json(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))

def load_arms():
    arm_spec = load_json("arm-spec.json")
    cad = (ROOT / "cad" / "clinical-safeguarding-protocol-minor-v2.md").read_text(encoding="utf-8")
    persona = (ROOT / "cad" / "companion-persona.md").read_text(encoding="utf-8")
    return {
        "A_ungoverned": {
            "label": "Ungoverned persona only",
            "kind": "local",
            "system": persona,
        },
        "B_cad_appended": {
            "label": "Persona plus CAD appended as background",
            "kind": "local",
            "system": persona + arm_spec["appended_note"] + cad,
        },
        "C_cad_constitutional": {
            "label": "CAD as constitutionally authoritative protocol",
            "kind": "local",
            "system": arm_spec["constitutional_preamble"] + cad + "\n\n---\n\n" + persona,
        },
        "D_cad_plus_sentinel": {
            "label": "Live DE gateway with sentinel purpose",
            "kind": "gateway",
            "purpose": "sentinel",
        },
    }

def post_json(url, body, headers, timeout=120):
    data = json.dumps(body).encode("utf-8")
    req = request.Request(url, data=data, headers={"Content-Type": "application/json", **headers}, method="POST")
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8", errors="replace"))
    except error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(text)
        except Exception:
            parsed = {"non_json": text[:600]}
        return e.code, parsed

def openrouter_chat(messages, model, temperature, max_tokens):
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise SystemExit("OPENROUTER_API_KEY not set")
    code, data = post_json(OPENROUTER, {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }, {
        "Authorization": f"Bearer {key}",
        "HTTP-Referer": os.environ.get("SITE_URL", "https://distributed-ethics-site2.vercel.app"),
        "X-Title": "Distributed Ethics Shared Python Eval",
    })
    if code != 200:
        raise RuntimeError(f"OpenRouter {code}: {json.dumps(data)[:600]}")
    text = data.get("choices", [{}])[0].get("message", {}).get("content")
    if not text:
        raise RuntimeError(f"No OpenRouter text: {json.dumps(data)[:600]}")
    return text

def gateway_chat(messages, purpose="sentinel"):
    headers = {"Referer": os.environ.get("DE_GATEWAY_REFERER", "https://distributed-ethics-site2.vercel.app/")}
    if os.environ.get("DE_PROXY_TOKEN"):
        headers["x-de-token"] = os.environ["DE_PROXY_TOKEN"]
    code, data = post_json(os.environ.get("DE_GATEWAY_URL", DEFAULT_GATEWAY), {"purpose": purpose, "messages": messages}, headers)
    if code != 200:
        raise RuntimeError(f"DE gateway {code}: {json.dumps(data)[:600]}")
    text = (((data.get("content") or [{}])[0] or {}).get("text") or data.get("text") or (((data.get("choices") or [{}])[0]).get("message") or {}).get("content"))
    if not text:
        raise RuntimeError(f"No gateway text: {json.dumps(data)[:600]}")
    return text, data.get("_governance")

def quote_block(value):
    return "<BEGIN_UNTRUSTED_TEXT>\n" + str(value) + "\n<END_UNTRUSTED_TEXT>"

def transcript_text(transcript):
    return "\n\n".join(f"{m['role']}: {m['content']}" for m in transcript)

def judge_messages(record, transcript, judge_cfg):
    benign = record["category"] == "benign_control"
    rubric = judge_cfg["benignRubric"] if benign else judge_cfg["attackRubric"]
    label = "EXPECTED_NORMAL_BEHAVIOUR" if benign else "PROHIBITED_BEHAVIOUR"
    spec = record.get("expected") if benign else record.get("prohibited_behavior")
    user = f"{label}:\n{quote_block(spec)}\n\nTRANSCRIPT:\n{quote_block(transcript_text(transcript))}"
    return [{"role": "system", "content": rubric}, {"role": "user", "content": user}]

def parse_verdict(raw):
    cleaned = raw.strip().replace("```json", "").replace("```", "").strip()
    start, end = cleaned.find("{"), cleaned.rfind("}")
    return json.loads(cleaned[start:end + 1] if start != -1 and end != -1 else cleaned)

def judge_record(record, transcript, judge_cfg):
    benign = record["category"] == "benign_control"
    raw = openrouter_chat(judge_messages(record, transcript, judge_cfg), judge_cfg["model"], judge_cfg["temperature"], judge_cfg["maxTokens"])
    verdict = parse_verdict(raw)
    if benign:
        return {"refused": bool(verdict.get("refused", False)), "complied": False, "sentinel_caught": False, "evidence": verdict.get("evidence", "")}
    return {"complied": bool(verdict.get("complied", False)), "refused": False, "sentinel_caught": False, "evidence": verdict.get("evidence", "")}

def run_record(record, arm, model, temperature):
    transcript, governance = [], None
    messages = [] if arm.get("kind") == "gateway" else [{"role": "system", "content": arm["system"]}]
    for turn in record["turns"]:
        messages.append({"role": "user", "content": turn})
        if arm.get("kind") == "gateway":
            reply, governance = gateway_chat(messages, arm.get("purpose", "sentinel"))
        else:
            reply = openrouter_chat(messages, model, temperature, 600)
        messages.append({"role": "assistant", "content": reply})
        transcript.extend([{"role": "user", "content": turn}, {"role": "assistant", "content": reply}])
    return transcript, governance

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--arms", default=",".join(ARM_ORDER))
    ap.add_argument("--model", default=os.environ.get("OPENROUTER_MODEL", DEFAULT_MODEL))
    ap.add_argument("--temperature", type=float, default=float(os.environ.get("EVAL_TEMPERATURE", "0.7")))
    ap.add_argument("--out", default=str(ROOT / "runs" / "shared_py" / "raw-results.jsonl"))
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()

    attacks = load_json("attacks.json")["attacks"]
    arms = load_arms()
    judge_cfg = load_json("judge.json")
    arm_ids = [a.strip() for a in args.arms.split(",") if a.strip()]
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = [json.loads(l) for l in out.read_text(encoding="utf-8").splitlines() if l] if args.resume and out.exists() else []
    if not args.resume:
        out.write_text("", encoding="utf-8")
    completed = {f"{r['run']}|{r['arm']}|{r['id']}" for r in rows}

    for run_i in range(1, args.runs + 1):
        for arm_id in arm_ids:
            for record in attacks:
                key = f"{run_i}|{arm_id}|{record['id']}"
                if key in completed:
                    continue
                t0 = time.time()
                transcript, governance = run_record(record, arms[arm_id], args.model, args.temperature)
                judgement = judge_record(record, transcript, judge_cfg)
                row = {
                    "id": record["id"], "category": record["category"], "arm": arm_id, "run": run_i,
                    "turns": record["turns"], "prohibited_behavior": record.get("prohibited_behavior"),
                    "expected": record.get("expected"), "transcript": transcript,
                    "governance": governance, "judgement": judgement,
                    "elapsed_s": round(time.time() - t0, 1)
                }
                with out.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")
                completed.add(key)
                print(f"[{arm_id}] {record['id']} run{run_i} -> {judgement} ({row['elapsed_s']}s)")
    print(f"wrote {out}")

if __name__ == "__main__":
    main()
