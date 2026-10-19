# Render Testcenter

Translates a finished Video Director plan (`video-director-plan@1`) into a Shotstack Edit and renders it on
**Shotstack stage**. It makes no creative decisions and repairs nothing: if the plan cannot be built exactly
as written, the page names the problem and the render stays locked.

## Workflow

1. **Load** the MP4 clips, the music file and the plan JSON exported by the Video Director.
2. **Asset matching**: every `sourceClip` and `music.filename` in the plan must match an uploaded file
   (MATCHED / MISSING / UNUSED). A different music filename can be matched by hand, which is reported.
3. **Pre-render validation** in seven groups: PLAN, FILES, SOURCE TIME, TIMELINE, MUSIC, TRANSITIONS,
   REVERSE. Any error disables the render button.
4. **Stage assets**: files that already exist on Shotstack stage (same byte size and duration) are reused.
   New files are stored by the page; saying **"sync"** in the chat uploads them through the Ingest API
   (`api.shotstack.io/ingest/stage`, `tools/assemble_upload.py` + `tools/ingest_upload.py`) and writes the
   source URL back.
5. **Shotstack JSON**: preview, copy, download. Deterministic: the same plan, assets and settings always
   give the same JSON and the same job hash.
6. **Render Stage Video** creates one render request, keyed by the SHA-256 of the edit, the asset mapping
   and the settings. It is submitted only when you say **"render"** in the chat
   (`tools/render_stage.py submit`, then `poll`). No automatic retry; a second identical job is refused by
   the page and by the tool's ledger (`render-jobs.local.json`, git-ignored).
7. **Result**: render id, status, render time, output URL, plan duration vs. measured duration (ffprobe);
   a difference above 2 frames is flagged. For the player the output is copied to the artifact's own
   storage, because the page cannot play media from other hosts.

## Builder

| Plan | Shotstack |
| --- | --- |
| Shot order | `shotNumber` |
| `builder.trim`, `builder.speed` (number) | `asset.trim`, `asset.speed`; clip `start` = `timelineStart`, `length` = `duration` |
| `builder.speed` (Tween array, reverse) | `asset.speed` as Tween array unchanged; negative speed plays backwards from the trim point |
| `fade-in`, `fade-out` | clip `opacity` tween over the plan's duration on a black background |
| `crossfade` (d) | incoming shot one track higher, starts d/2 early, opacity 0→1 over d; outgoing shot runs d/2 longer. The cut stays at the plan's time; the plan's source handles must cover the overlap |
| `dip-to-black` (d) | out-fade in the last d/2 of the outgoing shot, in-fade in the first d/2 of the incoming one, no overlap |
| `music.used` | one audio clip: `trim` = `trackStart`, `length` = `duration`; a volume fade only when the plan has `music.fadeOut`, with the last shot's fade-out duration |
| Video clips | `volume: 0`, `fit: crop` |
| Output | `mp4`, `1080`, plan fps (25), no text, no branding |

Shotstack's preset transitions (`fade`, `fadeFast`, …) have engine-defined durations, so they are not
used; every fade is an opacity tween with the plan's own duration.

Validation simulates the source position of every shot from trim and speed (including the zero
crossing of a turnaround) and checks it against the clip's real duration, the plan's `sourceEnd` and
`sourceRange`, the segments and the turnaround duration.

## Reverse status

Until a stage render containing a reverse shot has finished, the page shows **"Reverse not yet verified"**.
After one finishes it shows **"Reverse render technically successful"**, which says nothing yet about
how it looks.

## Requirements

- Stage only: `tools/render_stage.py` has the stage endpoint built in and no production switch.
- The session's network secret must cover `api.shotstack.io/edit/stage` (render) as well as
  `api.shotstack.io/ingest/stage` (sources). The key is never entered in the page or the chat.
- `render-jobs.local.json` and `director-assets.local.json` contain media URLs and stay out of git.
