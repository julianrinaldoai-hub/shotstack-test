"""Submit one Render Testcenter job to the Shotstack Edit API (stage only) and follow it.

The page stores each render request as a renderJobs document {hash, attempt, payload}; the
payload is the canonical JSON of the edit, its asset mapping and the settings, and the hash
is its SHA-256. This tool renders exactly that edit, nothing else:

  submit <job.json>    check the hash, refuse duplicates, POST once to /edit/stage/render
  poll <job-id> [--out <dir>]
                       GET the status every 5 s until done or failed; on done download the
                       MP4 and measure it with ffprobe

There is no retry: a failed POST or a failed render is recorded and reported, never resent.
Every submission is written to render-jobs.local.json (git-ignored, holds media URLs) before
polling starts, so the same job or the same hash can never be submitted twice from here.
The API key is injected by the environment's network proxy and never appears here.
"""
import hashlib
import json
import os
import subprocess
import sys
import time

API = "https://api.shotstack.io/edit/stage"  # stage only; there is deliberately no switch
LEDGER = os.environ.get("RENDER_LEDGER") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "render-jobs.local.json")
POLL_SECONDS, POLL_LIMIT = 5, 180


def load_ledger():
    return json.load(open(LEDGER)) if os.path.exists(LEDGER) else {}


def save_ledger(ledger):
    tmp = LEDGER + ".tmp"
    with open(tmp, "w") as f:
        json.dump(ledger, f, indent=2)
    os.replace(tmp, LEDGER)


def curl(*args):
    res = subprocess.run(["curl", "-sS", "-g", "-m", "60", "-w", "\n%{http_code}", *args], capture_output=True, text=True)
    if res.returncode:
        return 0, {"error": res.stderr.strip() or f"curl exit {res.returncode}"}
    body, _, code = res.stdout.rpartition("\n")
    try:
        return int(code), json.loads(body) if body.strip() else {}
    except json.JSONDecodeError:
        return int(code), {"error": body.strip()[:300]}


def fail(msg, **extra):
    print(json.dumps({"status": "failed", "error": msg, **extra}))
    sys.exit(1)


def check_job(job):
    payload, want = job.get("payload"), job.get("hash")
    if not isinstance(payload, str) or not want:
        fail("job has no payload or hash")
    got = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    if got != want:
        fail(f"hash mismatch: payload {got[:16]}…, job {want[:16]}…")
    data = json.loads(payload)
    if data.get("settings", {}).get("environment") != "stage":
        fail("job is not marked for the stage environment")
    edit = data["edit"]
    for t, track in enumerate(edit["timeline"]["tracks"]):
        for c, clip in enumerate(track["clips"]):
            src = clip["asset"].get("src", "")
            if not src.startswith("https://"):
                fail(f"track {t} clip {c}: asset src is not a public https URL ({src[:40]})")
    return edit


def submit(path):
    job = json.load(open(path))
    job_id = job.get("id") or f"{job['hash'][:24]}-{job.get('attempt', 1)}"
    edit = check_job(job)
    ledger = load_ledger()
    if job_id in ledger:
        fail(f"job {job_id} was already submitted (render {ledger[job_id].get('renderId')}); not sending it again")
    same = [k for k, v in ledger.items() if v["hash"] == job["hash"] and v["status"] != "failed"]
    if same:
        fail(f"an identical edit is already rendering or rendered as job {same[0]}; not sending it again")
    # record the attempt before the request, so a crash mid-request still blocks a resend
    ledger[job_id] = {"hash": job["hash"], "status": "submitting", "submittedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    save_ledger(ledger)
    code, res = curl("-X", "POST", "-H", "Content-Type: application/json", "-H", "Accept: application/json",
                     "--data-binary", json.dumps(edit), f"{API}/render")
    rid = (res.get("response") or {}).get("id")
    if code != 201 or not rid:
        msg = (res.get("response") or {}).get("message") or res.get("message") or res.get("error") or json.dumps(res)[:300]
        ledger[job_id].update(status="failed", error=f"HTTP {code}: {msg}")
        save_ledger(ledger)
        fail(f"Shotstack stage rejected the render (HTTP {code}): {msg}", jobId=job_id)
    ledger[job_id].update(status="queued", renderId=rid)
    save_ledger(ledger)
    print(json.dumps({"jobId": job_id, "status": "queued", "renderId": rid, "environment": "stage"}))


def ffprobe_duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height,r_frame_rate,nb_frames",
                          "-of", "json", path], capture_output=True, text=True).stdout
    info = json.loads(out or "{}")
    video = next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), {})
    return float(info.get("format", {}).get("duration", "nan")), video


def poll(job_id, out_dir):
    ledger = load_ledger()
    entry = ledger.get(job_id)
    if not entry or not entry.get("renderId"):
        fail(f"job {job_id} has no submitted render")
    rid, started, last = entry["renderId"], time.time(), None
    for _ in range(POLL_LIMIT):
        code, res = curl("-H", "Accept: application/json", f"{API}/render/{rid}")
        r = res.get("response") or {}
        status = r.get("status")
        if code != 200 or not status:
            fail(f"status request failed (HTTP {code}): {res.get('message') or res.get('error') or json.dumps(res)[:200]}", renderId=rid)
        if status != last:
            print(json.dumps({"renderId": rid, "status": status, "after": round(time.time() - started, 1)}), flush=True)
            last = status
        if status in ("done", "failed"):
            break
        time.sleep(POLL_SECONDS)
    else:
        fail(f"render {rid} did not finish within {POLL_SECONDS * POLL_LIMIT} s; still '{last}', not resubmitted", renderId=rid)
    result = {"jobId": job_id, "renderId": rid, "status": status, "environment": "stage", "url": r.get("url"),
              "renderTime": r.get("renderTime"), "error": r.get("error")}
    if status == "done" and r.get("url"):
        os.makedirs(out_dir, exist_ok=True)
        local = os.path.join(out_dir, f"{job_id}.mp4")
        subprocess.run(["curl", "-sS", "-g", "-m", "300", "-o", local, r["url"]], check=True)
        duration, video = ffprobe_duration(local)
        result.update(file=local, actualDuration=round(duration, 3), durationSource="ffprobe", video=video)
    entry.update({k: v for k, v in result.items() if k in ("status", "url", "renderTime", "error", "actualDuration")})
    save_ledger(ledger)
    print(json.dumps(result))


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("submit", "poll"):
        sys.exit(__doc__)
    if sys.argv[1] == "submit":
        submit(sys.argv[2])
    else:
        out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else "."
        poll(sys.argv[2], out)


if __name__ == "__main__":
    main()
