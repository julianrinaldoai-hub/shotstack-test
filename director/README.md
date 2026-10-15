# Director Testcenter

Isolierte Testseite (claude.ai-Artifact) für KI-geplante Immobilien-Edits. Keine Production-Architektur.

## Bedienung

1. Seite in claude.ai öffnen. Der Shotstack-Connector muss verbunden sein.
2. **Assets:** Die Liste kommt aus der db der Seite. Der Filter „Nur heute hochgeladene“ ist standardmäßig aktiv.
   - Neue Uploads: im Chat „sync“ sagen.
   - Dann läuft `python3 tools/sync_assets.py --out director-assets.local.json`. Das ist ein kostenloser, lesender Aufruf der Ingest-API (stage).
   - Danach wird die Liste in die Collection `assets` geschrieben.
3. **Style:** Elegant, Dynamic oder Cinematic. Das ist nur eine kreative Richtung im Director-Prompt, keine Vorlage.
4. **Analyze & Plan** läuft in vier getrennten Phasen. Es wird nichts gerendert.
   - **Phase 1, Clips analysieren:**
     - Im Browser: Bewegung, harte Schnitte und sichtbares Detail pro 0,25s.
     - Ein Frame alle 0,25s über die ganze Clipdauer, mit Zeitstempel auf Kontaktbögen. Das sind etwa 16 Frames pro 4-s-Clip.
     - Claude (Stufe „complex“) beschreibt erst jeden Frame, dann den Verlauf in Abschnitten, dann Raum und Relevanz, zuletzt die Nutzung.
   - **Phase 2, Gewichten:** Der Code bildet aus den Werten der Analyse die Relevanz und die Rangfolge der Clips: `relevance = 0,45 × propertyImportance + 0,30 × visualStrength + 0,25 × viewerInterest`. Dazu schätzt er, wie viele Sekunden das starke Material trägt.
   - **Phase 3, Musikabschnitt:** Eigener Claude-Aufruf. Er wählt Startpunkt und Länge aus Material und Musik (typisch 23–32s), ohne Shots zu planen.
   - **Phase 4, Edit planen:** Der Director bekommt Rangliste, Clip-Details und den festen Musikabschnitt in Filmzeit.
     - Der Code-Validator prüft den Plan.
     - Bei Fehlern gibt es eine Korrekturrunde.
5. **Regenerate Plan:** Phasen 3 und 4 laufen neu.
   - Die letzten 2 Pläne gehen nur als schwache Referenz in den Prompt ein. Ähnlichkeit ist erlaubt, wenn sie zum besten Ergebnis führt.
   - Die Analysen kommen aus dem Cache.
6. **Render:**
   - Erst nach Bestätigung: `render_video` über den Connector.
   - Status: preparing → rendering → done/failed.
   - Video, URL, ID und erkannte Umgebung werden beim Plan gespeichert.

## Aufteilung kreativ / technisch

| Wer | Entscheidet |
|---|---|
| Director (Claude) | Reihenfolge, Shot-Längen, Mehrfachnutzung, Auslassungen, Hero-Shots, Montagen, Speed-Ramps, Transitions, Musik-Startpunkt und Videolänge |
| Code (`CORE`-Block in `index.html`, aus `tools/build_v4.py` portiert) | Frame-Snapping (24 fps), gültige In/Out-Punkte, Footage-Budget mit Studio-Easing-Kurven, Sperrbereiche (harte Schnitte im Clip), nutzbarer Bereich aus der Bildanalyse, keine überlappende Wiederverwendung, Shotstack-Edit-JSON |

## Director-Regeln (Prioritäten für Screentime)

1. Relevanz des Raums für die Immobilie
2. Visuelle Qualität des konkreten Clip-Bereichs
3. Zuschauerinteresse
4. Musik / Timing
5. Style
6. Vollständigkeit des Materials

| Regel | Im Prompt | Vom Code geprüft |
|---|---|---|
| Relevanz statt Gleichverteilung | Rangliste mit propertyImportance, viewerInterest, visualStrength, Hero/Nebenraum und empfohlener Screentime; kein Clip nur für Vollständigkeit | Fehler, wenn ein Nebenraum oder wenig relevanter Clip länger als seine empfohlene Maximalzeit (+0,3s) läuft oder Nebenräume zusammen mehr als 30% füllen; Hinweis ab 20% und wenn Hauptbereiche (Relevanz ≥ 8) unter 50% bleiben |
| Länge aus Material und Musik | Phase 3 wählt die Länge; Minimum 23s, typisch 23–32s, länger nur begründet | Fehler unter 23s, über 45s oder wenn der Edit nicht auf die gewählte Länge endet; Hinweis über 33s ohne Begründung und wenn der Edit länger ist als das starke Material trägt |
| Musik am Stück | Ein Startpunkt, kein Schnitt, kein Loop. Startkandidaten pro Länge werden aus Takten, Energie, Sektionen und Drops berechnet | Fehler bei mehreren Segmenten oder Ende nach Trackende; Hinweis bei Start neben dem Takt |
| Immobilien-Dramaturgie | Rollen von Opening bis Finale; Nebenräume später oder als Insert | Hinweis, wenn ein Nebenraum eröffnet |
| Nutzbarer Bereich zuerst | Erst Source-Bereich, dann Länge, dann Speed (`"auto"` = aus Source-Ende) | Fehler, wenn ein Shot Bilder außerhalb von `usableStart–usableEnd` zeigt |
| Wiederholung | Nur mit anderem Bereich, starkem Clip, musikalischem Sinn und anderer Funktion; nie für Länge; normal max. 2× | Fehler bei 3.+ Nutzung ohne `reuseReason`; Hinweise bei zwei fast gleich langen Nutzungen, gleicher Rolle oder mehrfach genutztem Nebenraum |
| Keine Formel | Struktur aus Musik, Material, Hero-Shots, Style und Kamerabewegung, nicht aus einer festen Raumfolge | – |
| Transitions je Style | Shot für Shot; Dynamic selten, Cinematic gezielt, Elegant etwas öfter, aber nicht überall | Hinweise bei zu vielen Dissolves für den Style, Dissolve in schneller Montage oder auf Drop/Anstieg, fehlender `transitionReason` |

## Datenmodell (db)

| Collection | Doc-ID | Inhalt |
|---|---|---|
| `assets` | Ingest-ID | filename, kind (video/music), duration, created, width, height, fps, filesize, url |
| `clipAnalysis` | Asset-ID | Bewegungsprofil, Detailkurve, Schnitte, Bildanalyse mit Frame-Notizen, Abschnitten, Relevanzwerten, nutzbaren Bereichen und Screentime (v:3) |
| `musicAnalysis` | Asset-ID | Ergebnis von `analyse_music` |
| `plans` | `p<timestamp>` | number, style, signature, selection, plan, musicPick (Start, Länge, Begründungen), validation (Shots, Musik, Screentime pro Clip, Clip-Rangliste), edit, render |

## Grenzen

- Die bisherigen Renders liefen über stage (kostenlos, Wasserzeichen). Die Seite erkennt die Umgebung bei jedem Render an der Render-URL.
- Die `sample`-Aufrufe laufen über das Claude-Konto des Viewers:
  - 1 pro Clip bei der ersten Analyse (Stufe „complex“, mit 4 Kontaktbögen)
  - 2–3 pro Plan (Musikabschnitt, Edit, eventuell Korrektur)
- Medienlinks stehen nur in der db und in git-ignorierten Dateien, nie im Repo.
