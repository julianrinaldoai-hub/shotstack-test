"""Build the Version 2 edit.

Writes edit-plan-b.draft.json (placeholder URLs, safe to commit) and, when an
ingest manifest is passed, edit-plan-b.stage.json (real URLs, git-ignored).

Usage: python3 tools/build_v2.py [ingest-manifest.stage.json]
"""
import json
import sys

FPS = 24
BEAT = 60 / 118.01
BAR = 4 * BEAT
GRID0 = 1.177                    # first downbeat of the track (s)
M0 = GRID0 + 2 * BAR             # music in-point: intro bar 3 (track 5.244)
SPLICE_OUT = GRID0 + 11 * BAR    # end of A3 (track 23.548)
SPLICE_IN = GRID0 + 15 * BAR     # start of A8 (track 31.683)
SUCK_OUT = 16.825                # near-silent gap before the lift (track time)
XF = 0.03                        # fade-out before the splice, so A4's downbeat never sounds


def f(t):
    """Snap a time to the nearest frame."""
    return round(round(t * FPS) / FPS, 4)


def bar(n):
    """Video time of bar n, counted from the music in-point."""
    return f(n * BAR)


def tw(a, b, start, length, easing="linear"):
    d = {"from": a, "to": b, "start": round(start, 4), "length": round(length, 4)}
    if easing != "linear":
        d.update(interpolation="bezier", easing=easing)
    return d


def video(key, start, end, trim, **extra):
    asset = {"type": "video", "src": "{{%s}}" % key, "trim": trim, "volume": 0}
    if "speed" in extra:
        asset["speed"] = extra.pop("speed")
    clip = {"asset": asset, "start": start, "length": round(end - start, 4), "fit": "crop"}
    clip.update(extra)
    return clip


def ease_avg(a, b, easing):
    # mean value of a tween, used only to budget source footage
    return {"linear": (a + b) / 2, "easeIn": a + (b - a) / 3,
            "easeOut": a + (b - a) * 2 / 3, "easeInOut": (a + b) / 2}[easing]


def src_used(clip):
    sp = clip["asset"].get("speed", 1)
    if not isinstance(sp, list):
        return sp * clip["length"]
    t, used, cur = 0.0, 0.0, sp[0]["from"]
    for k in sorted(sp, key=lambda x: x["start"]):
        used += cur * (k["start"] - t)
        used += ease_avg(k["from"], k["to"], k.get("easing", "linear")) * k["length"]
        t, cur = k["start"] + k["length"], k["to"]
    return used + cur * (clip["length"] - t)


# ---- key times (video seconds) ----
T_DISSOLVE = f(bar(2) - BEAT)            # 07 fades in over the last beat of intro bar 4
T_DROP = bar(6)                          # the lift (track 17.447)
T_SPLICE = bar(9)                        # music jumps A3 -> A8 here
T_BREAK = f(T_SPLICE + BEAT)             # breakdown, beat 2 of A8
T_REENTRY = bar(10)                      # full section returns (track 33.717)
T_END = bar(12)
T_SUCK = round(f(SUCK_OUT - M0) - bar(5), 4)   # suck-out, as clip time inside the kitchen shot

# Intro: lake (01) -> dissolve -> drone approach (07), slow float then accelerating
c01 = video("SCENE_01_URL", 0, bar(2), 0.0, speed=0.85,
            scale=[tw(1.0, 1.03, 0, bar(2))],
            opacity=[tw(0, 1, 0, 1.5, "easeOut")])
c07 = video("SCENE_07_URL", T_DISSOLVE, bar(4), 0.0,
            speed=[tw(0.7, 1.25, 2.0, round(bar(4) - T_DISSOLVE - 2.0, 4), "easeIn")],
            opacity=[tw(0, 1, 0, round(bar(2) - T_DISSOLVE, 4), "easeInOut")])
# Enter through the balcony door, then the kitchen whoosh that brakes into the suck-out
c03 = video("SCENE_03_URL", bar(4), bar(5), 1.2)
c04 = video("SCENE_04_URL", bar(5), T_DROP, 2.0,
            speed=[tw(1.1, 1.5, 0, T_SUCK), tw(1.5, 0.25, T_SUCK, 0.47, "easeOut")])
# HERO on the lift: snaps in fast, settles into a slow float
c02 = video("SCENE_02_URL", T_DROP, bar(8), 0.15,
            speed=[tw(1.3, 0.6, 0.3, 1.2, "easeOut")])
# Quick two-beat details
c05 = video("SCENE_05_URL", bar(8), f(bar(8) + 2 * BEAT), 0.2)
c06 = video("SCENE_06_URL", f(bar(8) + 2 * BEAT), T_SPLICE, 3.0,
            scale=1.08, offset={"x": 0, "y": -0.035})
# The breath: back to the lake view, braking to a hold on the breakdown
c02b = video("SCENE_02_URL", T_SPLICE, T_REENTRY, 3.3,
             speed=[tw(0.8, 0.0, round(T_BREAK - T_SPLICE, 4), 0.6, "easeOut")],
             scale=[tw(1.0, 1.04, 0, round(T_REENTRY - T_SPLICE, 4))])
# Outro on the re-entry hit: the lake from above, slow drift, fade to black
c01b = video("SCENE_01_URL", T_REENTRY, T_END, 2.95, speed=0.5,
             scale=[tw(1.0, 1.04, 0, round(T_END - T_REENTRY, 4))],
             opacity=[tw(1, 0, round(T_END - T_REENTRY - 1.5, 4), 1.5, "easeInOut")])

music_a = {"asset": {"type": "audio", "src": "{{MUSIC_URL}}", "trim": round(M0, 3),
                     "volume": [tw(0, 1, 0, 0.8), tw(1, 0, round(T_SPLICE - XF, 4), XF)]},
           "start": 0, "length": T_SPLICE}
music_b = {"asset": {"type": "audio", "src": "{{MUSIC_URL}}", "trim": round(SPLICE_IN, 3),
                     "volume": [tw(0, 1, 0, 0.02), tw(1, 0, round(T_REENTRY + BAR - T_SPLICE, 4),
                                                     round(T_END - T_REENTRY - BAR, 4), "easeIn")]},
           "start": T_SPLICE, "length": round(T_END - T_SPLICE, 4)}

main = [c01, c03, c04, c02, c05, c06, c02b, c01b]
edit = {
    "timeline": {
        "background": "#000000",
        "tracks": [
            {"clips": [c07]},          # top: dissolves over the end of 01
            {"clips": main},
            {"clips": [music_a]},
            {"clips": [music_b]},
        ],
    },
    "output": {"format": "mp4", "resolution": "hd", "aspectRatio": "16:9", "fps": 24},
}

# ---- checks ----
SRC_LEN = 5.0417
for c in main + [c07]:
    end = c["asset"]["trim"] + src_used(c)
    assert end <= SRC_LEN, (c["asset"]["src"], end)
    print(f'{c["asset"]["src"]:16s} {c["start"]:8.4f}-{c["start"] + c["length"]:8.4f} '
          f'({c["start"] * 24:6.1f}f) src {c["asset"]["trim"]:.2f}->{end:.2f}')
for a, b in zip(main, main[1:]):
    assert a["start"] + a["length"] <= b["start"] + 1e-9, ("overlap", a["asset"]["src"], b["asset"]["src"])
# Studio's overlap check trips on float noise; chain back-to-back clips with "auto"
ends = [c["start"] + c["length"] for c in main]
for prev_end, c in zip(ends, main[1:]):
    if abs(prev_end - c["start"]) < 1e-3:
        c["start"] = "auto"
print("total", T_END, "| drop", T_DROP, "| splice", T_SPLICE, "| break", T_BREAK, "| re-entry", T_REENTRY,
      "| suck-out at kitchen clip time", T_SUCK)

json.dump(edit, open("edit-plan-b.draft.json", "w"), indent=2)
if len(sys.argv) > 1:
    m = json.load(open(sys.argv[1]))["sources"]
    s = json.dumps(edit)
    for i in range(1, 8):
        s = s.replace("{{SCENE_0%d_URL}}" % i, m["scene-0%d.mp4" % i]["url"])
    s = s.replace("{{MUSIC_URL}}", m["music.mp3"]["url"])
    assert "{{" not in s
    json.dump(json.loads(s), open("edit-plan-b.stage.json", "w"), indent=2)
    print("wrote edit-plan-b.stage.json")
