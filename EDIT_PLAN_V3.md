# Version 3 — Editorial Cut (new source material)

**Status:** Approved. Built and opened in Shotstack Studio for preview. **Not rendered.** Files: `edit-plan-c.draft.json` (placeholders, committed), `edit-plan-c.stage.json` (real sandbox URLs, git-ignored), built by `tools/build_v3.py`. Small trim adjustments from exact easing-curve budgeting: #6a trim 3.42 at 0.72x, #6b trim 2.36, #7 trim 1.00.
**Source:** `testmaterial-7f245e5c.zip` (sha256 prefix `d260b9659a6f0f1f`), analysed from scratch. Previous material and plans are not used.
**Exact numbers:** `tools/plan_v3.py` computes every time, speed curve and source range below.

## 1. Source material

All clips: H.264 736×400, 24 fps, 4.04s, with clip audio (muted in the edit). There is no scene-03 in the ZIP.

| Clip | sha256 (first 16) | Content | Measured camera motion (0.5s windows) | Usable portions |
|---|---|---|---|---|
| 01 | d12cd91708f2b167 | Drone shot: chalet-style house, pool, mountains | Slow **pull-back** with slight drift right; steady | Whole clip |
| 02 | 3a9ac218f8dbfc48 | Open-plan living, dining and kitchen, oak table in front | Push in + left; **surge at 2.0–3.0s** | 0–2.0 slow wide · 2.0–3.0 surge · 3.0–4.04 closer living/kitchen |
| 04 | 7f88990633333620 | Dining room with lit **wood stove**, sliding window, kitchen behind | Steady push + left, a little faster after 3.0s | 0–2.1 wide · 2.1–3.0 stove + table · 3.0–4.04 candles close |
| 05 | a2b6441db75eb00a | Attic bedroom, **skylight**, pendant, walk-in closet | Push + left + **tilt down**; surge 1.5–3.0s; settles after 3.0s | 0–0.9 skylight · 1.0–2.5 surge · 3.0–4.04 bed close |
| 06 | dec4878a527984b0 | Bathroom: freestanding tub, stone wall | Slow move **right**, gentle push (calmest clip) | 0–1.0 · 1.0–4.04 |
| 07 | 3a36d21b923fbc4d | Home office, **olive tree** in front, mountain windows | Lateral left; **olive tree sweeps across frame 1.6–3.0s** (a natural foreground wipe); then push toward desk and window | 0–1.5 wide · 1.6–3.0 olive sweep · 3.0–4.04 desk + window |
| 08 | bec98a8e8c881d7b | Bedroom with lake + mountain window, pendant | Push + left, speeding up 1.5–3.5s | 0–2.7 wide · 2.8–4.04 bed + window close |
| 09 | 4780f880c4ddb4e3 | Small bathroom, **toilet dominant in frame** | Moves right | **Not used**: the toilet can't be framed out without a large digital zoom on 736px footage |

Movement pattern: almost all interiors move **left and forward** (02, 04, 05, 07, 08). This gives natural motion continuity across cuts. 06 (right) is used as a deliberate counter-move, and 01 (pull-back) as the ending motion.

## 2. Music analysis (music.mp3, 114.05s)

- **Tempo 74.0 BPM, half-time feel:** beat = 0.811s, bar = 3.243s. Kick on 1, snare backbeat on 3. In the main section, **every even bar hits all four beats** (onset strength 6–7 on each beat), which suits montage. Odd bars accent only beats 3–4.
- **Bar grid:** downbeat of bar n = 0.720 + (n−1) × 3.2432s. Confirmed by the second lift landing exactly on bar 18 (55.855s).

| Bars | Track time | Section | Character |
|---|---|---|---|
| 1–4 | 0.72–13.69 | Intro A | Sparse, quiet (RMS −25.5 dB) |
| 5–8 | 13.69–26.67 | **Buildup** | Snare enters on beat 3, bass up (low +3 dB) |
| **9** | **26.67** | **Energy lift 1** | Full drums, RMS +2.4 dB, highs +3.5 dB |
| 9–16 | 26.67–52.61 | Main section 1 | Strict 4-bar loop (bar 9≈13, 10≈14, 11≈15, 12≈16 at 0.99–1.00 similarity). **Even bars = 4 strong beats** |
| **17** | 52.61–55.86 | **Breakdown** | Drops to RMS −25.4 dB, bass out |
| **18** | **55.86** | **Energy lift 2** | Brighter (highs −12 dB); accents on beats 2, 3, 4 |
| 18–33 | 55.86–107.75 | Main section 2 | 4-bar loop; final chorus bars 26–33 brightest (highs −10 dB) |
| 34 | 107.75–112.8 | Outro | Soft decay with a swell at 110.79, silent by about 112.8 |

**Music edit used (bar-aligned):**
- Track 20.179 → 39.639 (bars 7–12: 2 build bars + 4 bars of main section 1).
- **Jump** to 52.612 → 59.098 (bars 17–18: breakdown + lift 2).
- **Jump** to 107.747 → 112.8 (bar 34: the real ending).

Total **31.0s**.

**Join checks:**
- **12 → 17:** bar 12 ≈ bar 16 (0.99); harmony continuity 0.95 (natural 16→17: 0.93); identical levels.
- **18 → 34:** harmony continuity 0.96 (natural 33→34: 0.95). The only transient there is a pickup hit 60ms before the bar line that's already in bar 18 (identical in the original 18→19), so the join adds nothing.

Why the music is cut down: each section is a 4-bar loop, so a full second wave back to the real ending would need at least 4 more bars, about 37–40s in total. That's more than the roughly 28s of usable footage can carry without showing the same frames twice.

## 3. Timeline

Video times are snapped to whole frames (24 fps). "Bar" means the music bar in the original track.

| Section | # | Video in → out | Length | Clip | Source used | Speed | Role / music |
|---|---|---|---|---|---|---|---|
| **BUILD** (calm) | 1 | 0.000 → 3.250 | 3.25 | 04 | 0.00 → 2.11 | 0.65× constant | Opener: fire, window, kitchen. Fade from black. Bar 7 |
| | 2 | 3.250 → 6.500 | 3.25 | 02 | 0.00 → 3.36 | **R1** | Open plan: holds, then **accelerates into the lift**. Bar 8 |
| **WAVE 1** | 3 | **6.500** → 9.750 | 3.25 | 07 | 0.00 → 2.30 | **R2** | **HERO 1 on lift 1** (bar 9): snaps in fast, then settles as the olive tree drifts across in slow motion |
| **MONTAGE A** (bar 10, 4 consecutive beats) | 4a | 9.750 → 10.542 | 0.79 | 04 | 2.15 → 2.94 | 1.0× | Stove + dining, beat 1 |
| | 4b | 10.542 → 11.333 | 0.79 | 05 | 0.10 → 0.89 | 1.0× | Skylight, tilt down, beat 2 |
| | 4c | 11.333 → 12.167 | 0.83 | 06 | 0.15 → 0.98 | 1.0× | Bathtub, counter-move right, beat 3 |
| | 4d | 12.167 → 12.958 | 0.79 | 07 | 3.20 → 3.99 | 1.0× | Desk + mountain window, beat 4 |
| WAVE 1 (breathe) | 5 | 12.958 → 16.208 | 3.25 | 08 | 0.00 → 2.72 | **R3** | **HERO 2** (bar 11): lake + mountain bedroom, calm, then **accelerates into montage B** |
| **MONTAGE B** (bar 12) | 6a | 16.208 → 17.042 | 0.83 | 02 | 3.40 → 4.03 | 0.75× constant | Living + kitchen close, beat 1 |
| | 6b | 17.042 → 17.833 | 0.79 | 07 | 2.33 → 3.12 | 1.0× | Olive tree leaving frame, beat 2 |
| | 6c | 17.833 → 19.458 | 1.63 | 05 | 1.00 → 2.46 | **R4** | Attic push, **brakes into the breakdown**, beats 3–4 |
| **BREAKDOWN** (calm) | 7 | 19.458 → 22.708 | 3.25 | 06 | 1.05 → 4.02 | **R5** | Bathtub breath (bar 17), then **accelerates into lift 2** |
| **MONTAGE C** (lift 2, bar 18) | 8a | **22.708** → 23.500 | 0.79 | 08 | 2.80 → 3.59 | 1.0× | Bed + lake window close, on the lift |
| | 8b | 23.500 → 24.333 | 0.83 | 04 | 3.05 → 3.88 | 1.0× | Candles + table close, beat 2 |
| | 8c | 24.333 → 25.125 | 0.79 | 05 | 3.10 → 3.89 | 1.0× | Attic bed close, beat 3 (strongest accent) |
| **OUTRO** | 9 | 25.125 → 31.000 | 5.88 | 01 | 0.00 → 3.74 | **R6** | **Exterior landing** on beat 4: house, pool, mountains. The pull-back slows from fast to a float as the music jumps to the outro at 25.96. Fade to black about 29.0 → 30.4 (from the outro swell); the music decays to silence at 31.0 |

**Shot lengths:**
- 9 long shots of 3.25–5.9s: build ×2, heroes ×2, breakdown, outro.
- 10 montage shots of 0.79–0.83s (one beat each), plus one 2-beat brake shot.

**Energy waves:** calm build → accel → **hero** → **montage** → hero → **montage** → brake → **calm breakdown** → accel → **montage climax** → landing → calm outro.

## 4. Source reuse map (no source frame appears twice)

| Clip | Portions used (source s) | Uses |
|---|---|---|
| 01 | [0.00–3.74] outro | 1 (saved for the ending) |
| 02 | [0.00–3.36] build accel · [3.40–4.03] montage B | 2 |
| 04 | [0.00–2.11] opener · [2.15–2.94] montage A · [3.05–3.88] montage C | **3** |
| 05 | [0.10–0.89] montage A · [1.00–2.46] montage B brake · [3.10–3.89] montage C | **3** |
| 06 | [0.15–0.98] montage A · [1.05–4.02] breakdown | 2 |
| 07 | [0.00–2.30] hero 1 · [2.33–3.12] montage B · [3.20–3.99] montage A | **3** |
| 08 | [0.00–2.72] hero 2 · [2.80–3.59] montage C | 2 |
| 09 | — | 0 (toilet dominant) |

That's 18 timeline shots from 7 source clips.

## 5. Speed ramps

All ramps last 1.3–1.8s. Before a ramp the clip holds its first speed; after it, its last speed.

| Ramp | Shot | Curve | Purpose |
|---|---|---|---|
| **R1** | #2 open plan | 0.9× for 1.40s → **0.9→1.6×** over 1.84s (ease-in) → cut | Momentum into **lift 1**; amplifies the clip's own surge at 2–3s |
| **R2** | #3 office hero | Starts **1.4×** on the cut → **1.4→0.6×** over 1.30s (ease-out) → 0.6× for 1.95s | Carries the build's speed across the cut, then lets the hero breathe |
| **R3** | #5 bedroom hero | 0.7× for 1.60s → **0.7→1.5×** over 1.64s (ease-in) → cut | Acceleration into **montage B** |
| **R4** | #6c attic push | **1.3→0.7×** over 1.62s (ease-out) | Brakes into the **breakdown** as the music drops away |
| **R5** | #7 bathtub | 0.75× for 1.60s → **0.75→1.7×** over 1.64s (ease-in) → cut | Momentum into **lift 2** |
| **R6** | #9 exterior | **1.4→0.55×** over 1.80s (ease-out) → 0.55× to the end | Lands the climax, then settles into the calm outro |

Constant speeds: #1 at 0.65×, #6a at 0.75×, and the montage shots at 1.0×.

**Caveat:** below about 0.7×, the 24 fps sources repeat frames (no interpolation in Shotstack). #1 (0.65×), R2's hold (0.6×) and R6's hold (0.55×) are on slow-moving shots where this shows least. Check them in the preview.

## 6. How the edit follows the music

- **Build (bars 7–8):** two long, calm shots over the sparse build. #2 accelerates through bar 8 so the cut to the hero lands exactly on the lift.
- **Lift 1 (bar 9):** the hero arrives fast and settles. Bar 9 only accents beats 3–4, so a held shot suits it.
- **Bar 10 (four strong beats):** **montage A**, four cuts on four consecutive beats.
- **Bar 11 (accents on beats 3–4 only):** hero 2 breathes, then accelerates into bar 12.
- **Bar 12 (four strong beats):** **montage B**, two beat cuts, then a two-beat brake into the music jump.
- **Bar 17 (breakdown):** one calm shot, accelerating into lift 2.
- **Bar 18 (lift 2):** **montage C**, three beat cuts (beats 1–3). Beat 4 brings the exterior, which rides across the jump into the outro.
- **Bar 34 (outro):** the exterior pull-back slows to a float; the picture fades out from the outro swell; the music decays naturally.

Not every cut is on a bar line: there are cuts on beats 2, 3 and 4. Montage B's last shot runs two beats, and the outro shot starts on beat 4 of the previous bar.

**Transitions:** fade from black at the start, fade to black at the end. Every other cut is hard: motion-matched (left-moving chain), speed-driven (R1, R3, R5), or braking (R4, R6). No dissolves.

## 7. Open choices

1. **Opener:** the plan opens on the fireplace interior and saves the exterior for the final landing (an inside → outside reveal). A conventional exterior-first open is possible, but the exterior can only appear once at full quality, so it would leave the ending on an interior.
2. **Length:** 31.0s. A second-wave extension to about 37–40s isn't recommended with this much footage.
