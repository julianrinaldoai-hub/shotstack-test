# Director Testcenter

Isolierte Testseite (claude.ai-Artifact) für KI-geplante Immobilien-Edits. Keine Production-Architektur.

## Bedienung

1. Seite in claude.ai öffnen. Der Shotstack-Connector muss verbunden sein.
2. **Assets:** Die Liste kommt aus der db der Seite. Der Filter „Nur heute hochgeladene“ ist standardmäßig aktiv.
   - Neue Uploads: im Chat „sync“ sagen.
   - Dann läuft `python3 tools/sync_assets.py --out director-assets.local.json`. Das ist ein kostenloser, lesender Aufruf der Ingest-API (stage).
   - Danach wird die Liste in die Collection `assets` geschrieben.
3. **Style:** Elegant, Dynamic oder Cinematic. Das ist nur eine kreative Richtung im Director-Prompt, keine Vorlage.
4. **Analyze & Plan:**
   - Clip-Analyse im Browser: Bewegung, harte Schnitte, 4 Vorschaubilder an Claude.
   - Musikanalyse über `analyse_music`, kostenlos.
   - Danach plant der Director; der Code-Validator prüft den Plan, und bei Fehlern gibt es eine Korrekturrunde.
   - Es wird nichts gerendert.
5. **Regenerate Plan:** Neuer Director-Aufruf. Die bisherigen Pläne gehen als „nicht wiederholen“ in den Prompt ein. Die Analysen kommen aus dem Cache.
6. **Render:**
   - Erst nach Bestätigung: `render_video` über den Connector.
   - Status: preparing → rendering → done/failed.
   - Video, URL, ID und erkannte Umgebung werden beim Plan gespeichert.

## Aufteilung kreativ / technisch

| Wer | Entscheidet |
|---|---|
| Director (Claude) | Reihenfolge, Shot-Längen, Mehrfachnutzung, Auslassungen, Hero-Shots, Montagen, Speed-Ramps, Transitions, Musikausschnitt |
| Code (`CORE`-Block in `index.html`, aus `tools/build_v4.py` portiert) | Frame-Snapping (24 fps), gültige In/Out-Punkte, Footage-Budget mit Studio-Easing-Kurven, Sperrbereiche (harte Schnitte im Clip), keine überlappende Wiederverwendung, Musikschnitt auf Downbeats mit Micro-Fades, Shotstack-Edit-JSON |

## Datenmodell (db)

| Collection | Doc-ID | Inhalt |
|---|---|---|
| `assets` | Ingest-ID | filename, kind (video/music), duration, created, width, height, fps, filesize, url |
| `clipAnalysis` | Asset-ID | Bewegungsprofil, Schnitte, Vorschau-Bewertung (v:1) |
| `musicAnalysis` | Asset-ID | Ergebnis von `analyse_music` |
| `plans` | `p<timestamp>` | number, style, signature, selection, plan, validation, edit, render |

## Grenzen

- Ob der Connector auf stage (kostenlos, Wasserzeichen) oder v1 (Credits) rendert, zeigt erst die Render-URL.
- Die `sample`-Aufrufe laufen über das Claude-Konto des Viewers:
  - etwa 1 pro Clip bei der ersten Analyse
  - 1–2 pro Plan
- Medienlinks stehen nur in der db und in git-ignorierten Dateien, nie im Repo.
