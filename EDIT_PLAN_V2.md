# Premium Real-Estate Edit — Version 2 (cinematic cut)

**Status:** built and opened in Shotstack Studio for preview. **Not rendered.**
**Version 1 is unchanged** (`edit-plan-a.*`, see `EDIT_PLAN.md`) so the two can be compared.
**Files:** `edit-plan-b.draft.json` (placeholder URLs, committed) · `edit-plan-b.stage.json` (real sandbox URLs, git-ignored) · `tools/build_v2.py` (generates both from the bar grid; every timing below comes from it).

Source clips, upload status and the base music analysis are as documented in `EDIT_PLAN.md`.

## 1. Why Version 1 still feels like a standard edit

| Issue in V1 | Effect |
|---|---|
| **Cuts on a metronome.** Every cut falls on a bar line, in 2-bar → 2 → 2 → 1 → 1 → 1 → 3 blocks. There are no off-bar cuts and no cuts on individual beats. | It feels like a slideshow on a beat grid, not a cut performed to the music. |
| **Everything plays at almost native speed.** The one ramp (1.0 → 0.8) is barely visible. | The AI clips keep their uniform "AI glide": every move has the same speed and weight. |
| **There's no real fast/slow contrast.** Shots last 2.0–4.1s with similar energy. | There's no tension or release, so nothing feels special. |
| **The intro is just a fade into a drone shot.** The music starts at intro bar 5 with no build. | There's no opening moment. |
| **The hero just plays on the lift.** No anticipation is built before the drop and nothing happens on it. | The biggest musical moment is used passively. |
| **The outro fades out on a near-still shot.** | It ends rather than finishes. |
| **The structure is dictated by the song.** The 8-bar phrase forces about 6 bars of lesser shots between the hero and the ending. | Weaker material fills time, and the edit sags in the middle. |
| **Each clip is used once, in roughly its natural range.** | Clips are placed rather than edited. |

## 2. Version 2 changes

1. **Music edit for structure.** Analysis shows the full section is a strict 4-bar loop: A3 ≈ A7 (0.98 similarity) and A4 ≈ A8 (0.96). I cut from the end of A3 (track 23.548s) straight into A8 (31.683s), the bar with the breakdown. That keeps a 3-bar run after the lift, then the breath, then the return. I verified the join: loudness and transient profile match the song's natural A3→A4 and A7→A8 transitions. The music in-point moves earlier, to intro bar 3 (5.244s), giving a 6-bar cinematic intro.
2. **Rhythm with contrast.** Long intro shots (2 bars), 1-bar build shots, the hero (2 bars), **two 2-beat detail cuts**, the breath with a hold, and the outro (2 bars).
3. **Speed ramps that are visible but restrained:**
   - The drone approach floats at 0.7× and accelerates to 1.25×.
   - The kitchen speeds up to 1.5×, then **brakes to 0.25×** into the music's pre-drop suck-out (track 16.825–17.447s).
   - The hero **snaps in at 1.3× on the lift** and settles to a 0.6× float.
   - The breath ramps down to a **freeze** on the breakdown.
4. **A deliberate intro, hero and outro** (see §3).
5. **Continuity:** forward motion carries from the exterior push-in into the move through the balcony door. The kitchen moves right into the hero, which also moves right, as one continuous move. The interior lake view (freeze) is followed by the lake from above (outro).
6. **Strongest shots used deliberately:** the lake view (02) appears twice, as the hero and as the held breath. The lake drone (01) bookends the film. The weakest clips (05 bedroom, 06 bathroom) get 2 beats each.
7. **Reframing only where needed:** 06 is scaled ×1.08 and shifted down 3.5% to remove the toilet lid from the bottom edge. Digital scale stays ≤ 8% everywhere (≤ 4% on the pushes).
8. **Transitions (3):** fade from black, one cross-dissolve (lake → drone approach), fade to black. Everything else is a hard cut.

**Motion blur:** Shotstack has no motion-blur property. Its `blur` filter is a whole-frame Gaussian blur, which would look cheap here, so I didn't use it. The fastest moment (the kitchen at 1.5×) keeps the source's own motion blur. Real motion blur or optically interpolated slow motion would need pre-processing the clips (for example, ffmpeg `minterpolate`) and uploading the results as new assets. That's an option for later, not done.

## 3. Version 2 timeline (24.42 s, 24 fps)

Music bars count from the in-point, track 5.244s. Times are snapped to whole frames.

| # | Video in → out | Length | Music | Clip (source range) | Speed | Treatment | Role |
|---|---|---|---|---|---|---|---|
| 1 | 0.000 → 4.083 | 2 bars | Intro bars 3–4 | **01** lake drone (0.00 → 3.47) | 0.85 (invisible on a near-still shot) | Fade from black over 1.5 s; push 1.00 → 1.03 | **Intro, part 1:** the setting |
| 2 | 3.583 → 8.125 | 1 beat + 2 bars | Intro bars 5–6 | **07** drone approach (0.00 → 3.65) | 0.7 float for 2 s, then eases in to 1.25 | **Cross-dissolve** over 1 beat, complete on intro bar 5 | **Intro, part 2:** floats, then accelerates; cut just as it squares up to the façade |
| 3 | 8.125 → 10.167 | 1 bar | Intro bar 7 | **03** through the balcony door (1.20 → 3.24) | 1.0 | Hard cut | Arrival: forward motion carries from the drone into the move through the doorway |
| 4 | 10.167 → 12.208 | 1 bar | Intro bar 8 + suck-out | **04** kitchen (2.00 → 4.19) | 1.1 → **1.5** over 1.42 s, then **1.5 → 0.25** (ease-out) during the suck-out | Hard cut | Builds tension, then brakes to a near-hold on the dining area and lake window |
| 5 | **12.208 → 16.250** | 2 bars | **The lift**, A1–A2 | ⭐ **02** living room (0.15 → 3.07) | **Snaps in at 1.3**, eases out to 0.6 over 1.2 s, then floats at 0.6 | Hard cut **on the lift** | **Hero:** moves the same way as the kitchen, so one move continues into the drop |
| 6 | 16.250 → 17.250 | 2 beats | A3 beats 1–2 | **05** bedroom (0.20 → 1.20) | 1.0 | Hard cut | Fast detail |
| 7 | 17.250 → 18.292 | 2 beats | A3 beats 3–4 | **06** bathroom (3.00 → 4.04) | 1.0 | Reframe: scale 1.08, offset y −0.035 | Fast detail |
| 8 | 18.292 → 20.333 | 1 bar | **A8** (after the music jump): breakdown at 18.79, drum fill | **02** lake view (3.30 → **freeze at 3.86**) | 0.8, then **ramps to 0** (ease-out) from the breakdown over 0.6 s; held | Hard cut on the A8 downbeat; push 1.00 → 1.04 during the hold | **The breath:** back to the view and hold it while the music strips down |
| 9 | 20.333 → 24.417 | 2 bars | **Re-entry**, B1–B2 | **01** lake drone (2.95 → 4.99) | 0.5 (invisible on a near-still shot) | Hard cut **on the re-entry hit**; push 1.00 → 1.04; fade to black over the last 1.5 s | **Outro:** from the view inside to the setting outside; bookends the opening |

**Music:** two audio clips on separate tracks.
- **A:** trim 5.244, plays to 18.292 (track 23.536, 12 ms before the A4 downbeat). Fades in over 0.8 s and fades out over the last 30 ms.
- **B:** trim 31.683 (the A8 downbeat), starts at 18.292 with a 20 ms fade-in. Plays the breakdown and the re-entry, then fades out over B2 (22.367 → 24.417).

**Pacing:** 2 bars · 2 bars · 1 bar · 1 bar → **HERO 2 bars** → ½ bar · ½ bar → hold, 1 bar → outro 2 bars.

**Effects deliberately not used:** zoom punch-ins, whip pans, glitches, flashes, light leaks, social-media transitions, text.

## 4. Verification before opening in Studio

- I ran the edit through Shotstack's open-source Studio code (`@shotstack/shotstack-studio` 2.24.3) in headless Chromium and checked 15 frames at key moments. Fade-in, dissolve, every cut, the kitchen near-hold, the hero, the bathroom reframe, the freeze and the outro fade all render as planned. The duration resolves to 24.4167 s.
- That browser can't decode H.264, so this test used temporary local VP9 copies of the clips. The edit itself is the same file that was opened in Studio.
- Source budgets: every clip stays inside its 5.04 s source. Contiguous clips use `"start": "auto"` to avoid Studio's float-rounding overlap error, as in V1.

## 5. Risks to judge in the preview

- **0.25× / 0.6× / freeze on 24 fps sources:** without frame interpolation, slow sections repeat frames. The hero at 0.6× is the one to watch for judder.
- **The music jump** is analytically clean, but listen to the 18.29 s transition.
- **Frame 0 is black by design** (fade from black), the same as V1.
