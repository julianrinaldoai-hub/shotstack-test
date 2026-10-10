# Premium Real-Estate Edit — Approved Plan A

**Status:** Plan A approved. No end card. **Nothing uploaded, created or rendered yet.**
**Blocked on:** making the source files reachable by Shotstack over HTTPS (see §7).
**Companion files:** `edit-plan-a.draft.json` (ready-to-fill Shotstack Edit JSON), `analysis/` (scripts used for the measurements below).

---

## 1. Brief

- 20–30 s premium real-estate edit from the supplied clips and music.
- Must feel intentionally edited and cinematic, not like AI clips placed one after another.
- Allowed: beat-synced cuts, changes in pacing, subtle speed ramps, 1–2 tasteful transitions, one hero shot, strategic trimming, subtle motion effects.
- Avoid: cheesy transitions, excessive effects, aggressive digital zooms, random motion, over-editing.
- Source files must not be modified. The owner does not want the media made public on GitHub.

## 2. Source material

Uploaded as `testmaterial-5ceed918.zip` (sha256 prefix `16af042f592c93e4`). The macOS `__MACOSX/` and `.DS_Store` entries are ignored. The analysis worked only on an extracted copy; the originals were not modified.

| File | Bytes | sha256 (first 16) | Format |
|---|---|---|---|
| scene-01.mp4 | 2,515,092 | 345f3b4bca4b0812 | H.264 736×400, 24 fps, 5.042 s, AAC stereo |
| scene-02.mp4 | 2,200,056 | 3efb6d3e284b5bdc | same |
| scene-03.mp4 | 1,930,134 | 09734545af92373e | same |
| scene-04.mp4 | 1,580,889 | 4ad2ecd502f152d4 | same |
| scene-05.mp4 | 1,155,094 | 67013531e9b7320b | same |
| scene-06.mp4 | 912,741 | 797588291809dc01 | same |
| scene-07.mp4 | 4,591,769 | 0ff2bd465145cc82 | same (highest bitrate, sharpest) |
| music.mp3 | 4,361,822 | 05ed2bfd09b83062 | MP3 44.1 kHz stereo, 136.31 s |

The clips carry their own audio (−17 to −26 dB mean). **All clip audio is muted in the edit.**

**Resolution caveat:** 736×400 (1.84:1) is low. Enlarged to 1280×720 that's about 1.8×; to 1080p about 2.7×, which looks soft. Decision: work at **1280×720** and keep any digital scale at ≤ 4 %. Higher-resolution masters should replace these for a real delivery.

## 3. Clip analysis

Camera motion was measured with phase correlation per frame quadrant at 368 px width over 4-frame steps. "dx" is how far the image content shifts sideways: negative means the camera slides right. "Push" is how much the quadrants spread apart: positive means the camera moves forward.

| Clip | Content | Measured motion | Usable range | Notes |
|---|---|---|---|---|
| **01** | Drone shot of a beige 4-storey apartment block above a lake, town and hills behind, lots of sky | Almost still: dx ±0.4, push ≈ 0 | Whole clip | Calmest shot. Shows the lake that the 02/04 interiors look out on. |
| **02** | Living/dining room, floor-to-ceiling sliding glass, lake-view terrace, bamboo plant in the foreground | Steady slide right (dx −2 to −3) + push in (+5 to +7) | 0.2–3.8 s | Strongest shot. The plant passing gives depth; it leaves frame around 2.5 s. **Hero.** |
| **03** | From the balcony looking back into a living room through an open sliding door (green curtains, table, sofa) | Slides left (dx +1 to +2.4) + push in (+3 to +6.6), speeds up mid-clip | 1.2–3.3 s | A threshold / reverse-angle shot. Different flat from 02/04. |
| **04** | Dark grey kitchen with wood board and appliances; reveals the dining area and lake windows | Slides right, **speeding up** (dx −3.4 → −5.0 at 2–4 s) + push in (+6 to +10) | 0.85–4.9 s | Most lateral energy; ends on the dining area and lake view. Same flat as 02. |
| **05** | Bedroom: fitted wardrobe, upholstered headboard, sunlight on the oak floor, green curtain | Slides left (dx +1.5 to +4.2) + push in (+4.5 to +6.3) | 0.15–2.2 s | After about 2.5 s the wardrobe fills the frame and the bed exits. Same flat as 03. |
| **06** | Marble-look bathroom: glass shower, white vanity, mirror, flush plate | Slight slide right (dx −1.2 to −1.9) + push in (+3 to +6.7), eases to a stop | 2.4–4.94 s | The vanity is centred late in the clip. The toilet lid is just visible at the bottom edge. Weakest clip, so it gets a short slot. |
| **07** | Drone shot of a grey terraced building on a hillside (forest, meadow) | Strong push in (+6 to +10) while circling: front-on at about 2.5–3.9 s, then keeps circling to show the right side (dx −2.4 at 4–5 s) | 0.0–4.1 s | Cinematic move; reaches a symmetrical front-on composition. **It does not settle at the end.** |

Full-resolution checks of every planned segment showed **no obvious AI artefacts** (warping, morphing).

**Property consistency (known, accepted for this test):** the clips show at least two properties. 01/02/04 are one (lake view), 03/05 are a second flat (green curtains), and 07 is a different building on a hillside. Plan B (rejected for now) would drop 07 for consistency.

## 4. Music analysis

Analysed with librosa 1.0 (beat tracking, onset strength, RMS loudness, low-band flux, agglomerative sectioning), then refined by fitting a grid to the onsets.

- **Tempo: 118.01 BPM.** Beat = 0.5084 s, bar (4/4) = 2.0337 s, 8-bar phrase = 16.27 s.
- **Downbeat grid (track time):** `1.177 + n × 2.0337` → 1.177, 3.211, 5.244, 7.278, **9.312**, 11.345, 13.379, 15.413, **17.447**, 19.480, 21.514, 23.548, 25.582, 27.615, 29.649, 31.683, 33.716, …

| Track time | Section | Evidence |
|---|---|---|
| 0.00–1.18 | Near-silent lead-in | RMS −25.7 dB |
| 1.18–17.45 | **Intro**, 8 bars, lighter percussion | RMS about −13 to −14 dB; hi-hat accents each bar |
| 9.31 | Halfway accent of the intro (bar 5) | Onset peak 9.320 s; loudest intro beat |
| **17.45** | **Lift**: bass enters, the strongest moment in the track | Onset 17.456 s; RMS jumps from −12.8 to −6.5 dB (about +6 dB) |
| 17.45–33.72 | Full section, 8 bars | RMS about −6.5 to −7 dB, strong low end |
| 32.20–33.72 | **One-bar breakdown** (beat 2 of bar 8): music strips back | RMS falls to −12.8 to −14.3 dB; onset 32.203 s |
| 33.72 | Full section returns | Onset 33.727 s |
| 33.7–66.3 | Full section continues | |
| 66.3–82.5 | Quieter breakdown | RMS about −13 to −15 dB |
| 82.5–130.0 | Full section | |
| 130.0–134.0 | Ending fade | RMS −11.8 → −43 dB |

**Music window used:** start at track **9.312 s** (intro bar 5). This gives 4 bars of build, the lift **8.135 s** into the video, and the breakdown **22.89 s** into the video, where the edit ends.

## 5. Approved edit — Plan A (24.42 s)

**Output:** MP4, 16:9, 1280×720 (`resolution: "hd"`), **24 fps** to match the source and avoid frame-rate stutter. Background black. All clip audio muted.
**Timing:** every cut sits on a bar line (video time = track time − 9.312), snapped to the nearest 1/24 s frame so clips meet without gaps.

| # | Video in → out (s) | Frames | Length | Clip | Source in → out | Speed | Treatment | Why |
|---|---|---|---|---|---|---|---|---|
| 1 | 0.0000 → 4.0833 | 0–98 | 4.083 (2 bars) | **07** drone arrival | 0.00 → 4.08 | 1.0 | Fade in from black over 0.6 s (opacity tween) | The push-in reaches the front-on view and I cut just after. Its ending rightward drift carries into the kitchen. |
| 2 | 4.0833 → 8.1250 | 98–195 | 4.042 (2 bars) | **04** kitchen | 0.85 → 4.89 | 1.0 | Hard cut | It speeds up on its own into the lift and ends on the dining area and lake. |
| 3 | **8.1250 → 12.2083** | 195–293 | 4.083 (2 bars) | ⭐ **02** living room (**HERO**) | 0.20 → ≈3.77 | **Ramp:** 1.0 held for 1.0 s, eased to 0.8 over 1.0 s (easeInOut), 0.8 to the end | Hard cut **on the lift** | The biggest musical moment. Same rightward move as the kitchen, so the two read as one continuous move. Then the camera floats so the lake view can sink in. |
| 4 | 12.2083 → 14.2500 | 293–342 | 2.042 (1 bar) | **03** balcony into living room | 1.20 → 3.24 | 1.0 | Hard cut | Reverse angle (the hero looks out, this looks back in). Pacing doubles here for the private rooms. |
| 5 | 14.2500 → 16.2500 | 342–390 | 2.000 (1 bar) | **05** bedroom | 0.15 → 2.15 | 1.0 | Hard cut | Same leftward move as 03 for continuity. Uses the sunlit part before the wardrobe dominates. |
| 6 | 16.2500 → 18.7917 | 390–451 | 2.542 (1 bar + 0.5 s under the dissolve) | **06** bathroom | 2.40 → 4.94 | 1.0 | Hard cut in; the closing shot dissolves over it | Vanity centred, the camera eases to a stop: a quiet beat before the ending. |
| 7 | 18.2917 → 24.4167 | 439–586 | 6.125 (about 3 bars) | **01** lake drone | 0.00 → ≈5.02 | 0.82 constant (a stretch, invisible on a near-still shot) | **Cross-dissolve in** over 0.5 s (12 frames, 1 beat) starting on the bar. **Slow push** scale 1.00 → 1.04 over the shot. **Fade to black** from 22.875 s to the end (opacity tween) | Stepping back out to show the setting. The fade starts exactly where the song strips down, so music and picture breathe out together. |

**Music clip:** `music.mp3`, trim 9.312, start 0, length 24.4167. Volume 0 → 1 over 0.15 s (prevents a click), held at 1, then 1 → 0 from 22.875 s to 24.4167 s (the breakdown). It reaches silence before the full section returns at track 33.716 s.

**Pacing:** 2 bars · 2 bars | HERO 2 bars on the lift | 1 bar · 1 bar · 1 bar | long closing shot of about 3 bars.

**Movement direction across cuts:** 07 (push, ends drifting right) → 04 R → 02 R | 03 L → 05 L → 06 R → 01 (still). The one deliberate reversal is at 12.21 s, marking the change of chapter.

### Effects, deliberately limited
- **Transitions:** one cross-dissolve (06 → 01), plus the opening fade from black and the closing fade to black. Every other cut is hard.
- **Speed ramps:** one, on the hero, never below 0.8. Clip 01's 0.82 is only a stretch on a near-still shot.
- **Added motion:** one 4 % slow push on clip 01, the only still shot. None on the moving clips, where it would look random.
- **Excluded:** whip pans, light leaks, flashes, glitches, digital punch-ins, Ken Burns `effect` presets on moving shots, text, and an end card.

## 6. Technical decisions for the Shotstack build

- **`fit: "crop"`**, not `"cover"`. According to the Shotstack guide, `cover` *stretches* and ignores aspect ratio, while `crop` fills the frame and crops the overflow. At 1.84:1 into 16:9 that crops about 3 % from the sides.
- **Fades and the dissolve use opacity tweens**, not `transition` presets, so their durations are exact (preset timings are fixed by the engine).
- **Track order** (`tracks[0]` is the top layer): `[0]` clip 01, which must sit above the bathroom for the dissolve · `[1]` clips 07 → 04 → 02 → 03 → 05 → 06 in sequence · `[2]` music.
- **The speed ramp uses a video `speed` tween array**, which the Shotstack guide confirms is supported. Playback starts at `trim`, and the clip `length` stays the same.
- Clip volume 0 on every video asset. Music is an `audio` asset on its own track (not the deprecated `timeline.soundtrack`).
- Workflow: open in the in-chat Shotstack editor (`studio`) for review. **Render only after explicit approval.**

## 7. Hosting / upload status (blocker)

Checked on 2026-10-10:
- The connected Shotstack MCP has **no Ingest or upload tool**. Its tools are the guide, the in-chat editor, the editor link, rendering, render status, template create/read/update/delete/render, and AI generation (list models, quote, generate, status). None takes a local file. It publishes no extra resources.
- The Shotstack guide requires **public HTTPS URLs** for every asset `src` (no local paths, no `data:` URIs, no signed URLs that expire mid-render).
- `api.shotstack.io/ingest/{stage,v1}` **can be reached** from the workspace (it returns 401 "Missing API key", so the network isn't blocking it).
- There's **no Shotstack API key** in the workspace environment.

Options (not decided yet; the owner rejected public GitHub hosting):
1. **Add `SHOTSTACK_API_KEY`** in the cloud environment settings (Network secrets, or an environment variable). A sandbox (stage) key is preferred. A new session picks it up, then: ingest signed upload URL → PUT each of the 8 files → poll the source until it's ready → use the hosted URLs.
2. **The owner uploads the 8 files** through the Shotstack dashboard and supplies the 8 URLs.

Not yet verified: Shotstack-hosted source URLs are thought to be unlisted (anyone with the exact link could fetch the file) rather than private.

**Note for a new session:** the extracted sources lived in session scratch space and the zip in the session upload folder. Both are temporary, so the zip will likely need to be uploaded again.

## 8. Alternatives considered (not chosen)

- **Plan B, one property only:** drop 07 and open and close on clip 01. More consistent, but loses the strongest drone move.
- **End card:** 2 s of quiet text over black (about 26.5 s total). **Off for this first test.**
- **Longer cut:** +2 bars on the hero and the closing shot (about 28.5 s).
- **Music edit onto the song's real ending** (track 130–134 s): possible at bar boundaries, but riskier. Fading on the 32.2 s breakdown was chosen instead.
- **Slowing clip 07 for a held ending:** rejected. The clip keeps circling past the front-on view, and slow motion on a 24 fps source risks stutter.

## 9. Next steps

1. Get hosted URLs for the 8 files (option 1 or 2 in §7).
2. Fill the `merge` values in `edit-plan-a.draft.json` with those URLs.
3. Open it in the in-chat Shotstack editor for review. Check sync on the lift (8.125 s), the speed ramp's smoothness, the dissolve, and the fade timing.
4. Render only after explicit approval (720p first).
