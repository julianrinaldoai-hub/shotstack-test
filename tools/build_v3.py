"""Build the Version 3 editorial cut (see EDIT_PLAN_V3.md).

Writes edit-plan-c.draft.json (placeholder URLs, safe to commit) and, when an
ingest manifest is passed, edit-plan-c.stage.json (real URLs, git-ignored).

Usage: python3 tools/build_v3.py [ingest-manifest.v3.stage.json]
"""
import json
import sys

FPS = 24
BEAT = 60 / 74.0
BAR = 4 * BEAT
GRID0 = 0.720                    # downbeat of bar 1 (track seconds)
SRC_LEN = 4.0417
XF = 0.03                        # micro-fade at each music join


def bs(n):
    """Track time of the downbeat of bar n."""
    return GRID0 + (n - 1) * BAR


# Music edit: bars 7-12, then bars 17-18, then the real outro (bar 34) to silence
SEGMENTS = [(bs(7), bs(13)), (bs(17), bs(19)), (bs(34), 112.8)]


def f(t):
    """Snap a time to the nearest frame."""
    return round(round(t * FPS) / FPS, 4)


def vt(bar_no, beat=0):
    """Video time of a beat in an original track bar, through the music edit."""
    off, x = 0.0, bs(bar_no) + beat * BEAT
    for a, b in SEGMENTS:
        if a - 1e-6 <= x < b + 1e-6:
            return f(off + x - a)
        off += b - a
    raise ValueError(bar_no)


END = f(sum(b - a for a, b in SEGMENTS))

# CSS-style easing curves, matching Studio's CurveInterpolator
CURVES = {"easeIn": (0.42, 0.0, 1.0, 1.0), "easeOut": (0.0, 0.0, 0.58, 1.0)}


def ease(name, x):
    if name is None:
        return x
    x1, y1, x2, y2 = CURVES[name]
    lo, hi = 0.0, 1.0
    for _ in range(40):          # solve bezier x(t) = x, then return y(t)
        t = (lo + hi) / 2
        bx = 3 * (1 - t) ** 2 * t * x1 + 3 * (1 - t) * t * t * x2 + t ** 3
        lo, hi = (t, hi) if bx < x else (lo, t)
    return 3 * (1 - t) ** 2 * t * y1 + 3 * (1 - t) * t * t * y2 + t ** 3


def speed_at(speed, t):
    if not isinstance(speed, list):
        return speed
    cur = speed[0]["from"]
    for k in speed:
        if t < k["start"]:
            return cur
        if t <= k["start"] + k["length"]:
            p = (t - k["start"]) / k["length"]
            return k["from"] + (k["to"] - k["from"]) * ease(k.get("easing"), p)
        cur = k["to"]
    return cur


def src_used(clip, step=0.001):
    sp, L = clip["asset"].get("speed", 1), clip["length"]
    n = int(L / step)
    return sum(speed_at(sp, (i + 0.5) * step) for i in range(n)) * step


def ramp(a, b, start, length, easing):
    return {"from": a, "to": b, "start": start, "length": length, "interpolation": "bezier", "easing": easing}


def shot(n, key, start, end, trim, speed=1.0, **extra):
    asset = {"type": "video", "src": "{{%s}}" % key, "trim": trim, "volume": 0}
    if speed != 1.0:
        asset["speed"] = speed
    clip = {"asset": asset, "start": start, "length": round(end - start, 4), "fit": "crop"}
    clip.update(extra)
    clip["_n"] = n
    return clip


S = {k: "SCENE_%s_URL" % k for k in ("01", "02", "04", "05", "06", "07", "08")}
FADE_OUT_AT = 29.0               # outro swell (track 110.79) -> picture fades to black

shots = [
    # BUILD
    shot("1", S["04"], vt(7), vt(8), 0.00, 0.65,
         opacity=[{"from": 0, "to": 1, "start": 0, "length": 1.0, "interpolation": "bezier", "easing": "easeOut"}]),
    shot("2", S["02"], vt(8), vt(9), 0.00, [ramp(0.9, 1.6, 1.40, 1.84, "easeIn")]),          # R1 into lift 1
    # WAVE 1
    shot("3", S["07"], vt(9), vt(10), 0.00, [ramp(1.4, 0.6, 0.0, 1.30, "easeOut")]),         # R2 hero 1
    shot("4a", S["04"], vt(10, 0), vt(10, 1), 2.15),                                          # MONTAGE A
    shot("4b", S["05"], vt(10, 1), vt(10, 2), 0.10),
    shot("4c", S["06"], vt(10, 2), vt(10, 3), 0.15),
    shot("4d", S["07"], vt(10, 3), vt(11), 3.20),
    shot("5", S["08"], vt(11), vt(12), 0.00, [ramp(0.7, 1.5, 1.60, 1.64, "easeIn")]),        # R3 hero 2
    shot("6a", S["02"], vt(12, 0), vt(12, 1), 3.42, 0.72),                                    # MONTAGE B
    shot("6b", S["07"], vt(12, 1), vt(12, 2), 2.36),
    shot("6c", S["05"], vt(12, 2), vt(17), 1.00, [ramp(1.3, 0.7, 0.0, 1.62, "easeOut")]),     # R4 brake
    # BREAKDOWN
    shot("7", S["06"], vt(17), vt(18), 1.00, [ramp(0.75, 1.7, 1.60, 1.64, "easeIn")]),       # R5 into lift 2
    # WAVE 2 - MONTAGE C
    shot("8a", S["08"], vt(18, 0), vt(18, 1), 2.80),
    shot("8b", S["04"], vt(18, 1), vt(18, 2), 3.05),
    shot("8c", S["05"], vt(18, 2), vt(18, 3), 3.10),
    # OUTRO
    shot("9", S["01"], vt(18, 3), END, 0.00, [ramp(1.4, 0.55, 0.0, 1.80, "easeOut")]),       # R6 landing
]
last = shots[-1]
last["opacity"] = [{"from": 1, "to": 0, "start": round(FADE_OUT_AT - last["start"], 4), "length": 1.4,
                    "interpolation": "bezier", "easing": "easeInOut"}]

# ---- checks: contiguity and source budgets (no frame shown twice) ----
uses = {}
for a, b in zip(shots, shots[1:]):
    assert abs(a["start"] + a["length"] - b["start"]) < 1e-3, (a["_n"], b["_n"])
for c in shots:
    key = c["asset"]["src"][2:-2]
    t0 = c["asset"]["trim"]
    t1 = t0 + src_used(c)
    assert t1 <= SRC_LEN, (c["_n"], t1)
    uses.setdefault(key, []).append((t0, t1, c["_n"]))
    sp = c["asset"].get("speed", 1.0)
    print(f'#{c["_n"]:3s} {key[6:8]}  {c["start"]:7.3f}-{c["start"] + c["length"]:7.3f}  src {t0:.2f}-{t1:.2f}'
          f'  speed {sp if not isinstance(sp, list) else "ramp " + str(sp[0]["from"]) + "->" + str(sp[0]["to"])}')
for key, r in uses.items():
    r.sort()
    for (a0, a1, an), (b0, b1, bn) in zip(r, r[1:]):
        assert a1 <= b0 + 1e-6, ("source overlap", key, an, bn)
print("total", END, "| lift1", vt(9), "| lift2", vt(18), "| outro", vt(34))

# contiguous clips chain with "auto" (avoids Studio's float overlap error)
for c in shots[1:]:
    c["start"] = "auto"
for c in shots:
    del c["_n"]

# ---- music: one audio clip per segment, micro-fades at the joins ----
music, off = [], 0.0
for i, (a, b) in enumerate(SEGMENTS):
    L = round(b - a, 4)
    vol = []
    vol.append({"from": 0, "to": 1, "start": 0, "length": 0.6 if i == 0 else 0.02})
    if i < len(SEGMENTS) - 1:
        vol.append({"from": 1, "to": 0, "start": round(L - XF, 4), "length": XF})
    else:
        vol.append({"from": 1, "to": 0, "start": round(L - 0.5, 4), "length": 0.5})
    music.append({"clips": [{"asset": {"type": "audio", "src": "{{MUSIC_URL}}", "trim": round(a, 3), "volume": vol},
                             "start": round(off, 4), "length": L}]})
    off += b - a

edit = {
    "timeline": {"background": "#000000", "tracks": [{"clips": shots}] + music},
    "output": {"format": "mp4", "resolution": "hd", "aspectRatio": "16:9", "fps": 24},
}
json.dump(edit, open("edit-plan-c.draft.json", "w"), indent=2)

if len(sys.argv) > 1:
    m = json.load(open(sys.argv[1]))["sources"]
    s = json.dumps(edit)
    for k in S.values():
        s = s.replace("{{%s}}" % k, m["scene-%s.mp4" % k[6:8]]["url"])
    s = s.replace("{{MUSIC_URL}}", m["music.mp3"]["url"])
    assert "{{" not in s
    json.dump(json.loads(s), open("edit-plan-c.stage.json", "w"), indent=2)
    print("wrote edit-plan-c.stage.json")
