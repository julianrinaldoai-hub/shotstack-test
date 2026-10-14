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
   - Clip-Analyse im Browser: Bewegung und harte Schnitte.
   - Musikanalyse über `analyse_music`, kostenlos.
   - Pro Clip schickt die Seite bis zu 7 Bilder (Anfang, Mitte, Ende) an Claude. Zurück kommen Raumtyp, Wichtigkeit, nutzbarer und stärkster Bereich (`usableStart/End`, `strongestStart/End`) und warum Anfang oder Ende schwach sind.
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
| Director (Claude) | Reihenfolge, Shot-Längen, Mehrfachnutzung, Auslassungen, Hero-Shots, Montagen, Speed-Ramps, Transitions, Musik-Startpunkt und Videolänge |
| Code (`CORE`-Block in `index.html`, aus `tools/build_v4.py` portiert) | Frame-Snapping (24 fps), gültige In/Out-Punkte, Footage-Budget mit Studio-Easing-Kurven, Sperrbereiche (harte Schnitte im Clip), nutzbarer Bereich aus der Bildanalyse, keine überlappende Wiederverwendung, Shotstack-Edit-JSON |

## Director-Regeln (Prioritäten)

1. Visuell guter Clipbereich
2. Immobilien-Spannungsbogen
3. Musik-Sync
4. Style
5. Variation
6. Möglichst viele Clips

| Regel | Im Prompt | Vom Code geprüft |
|---|---|---|
| Musik am Stück | Ein Startpunkt, kein Schnitt, kein Loop. Startkandidaten pro Länge werden aus Takten, Energie, Sektionen und Drops berechnet | Fehler bei mehreren Segmenten oder Ende nach Trackende; Hinweis bei Start neben dem Takt |
| Immobilien-Dramaturgie | Rollen von Opening bis Finale; Nebenräume später oder als Insert | Hinweis, wenn ein Nebenraum eröffnet |
| Nutzbarer Bereich zuerst | Erst Source-Bereich, dann Länge, dann Speed (`"auto"` = aus Source-Ende) | Fehler, wenn ein Shot Bilder außerhalb von `usableStart–usableEnd` zeigt |
| Wiederholung | Normal max. 2×, verschieden lang, andere Rolle | Fehler bei 3.+ Nutzung ohne `reuseReason`; Hinweise bei zwei fast gleich langen Nutzungen oder gleicher Rolle |
| Transitions je Style | Shot für Shot; Dynamic selten, Cinematic gezielt, Elegant etwas öfter, aber nicht überall | Hinweise bei zu vielen Dissolves für den Style, Dissolve in schneller Montage oder auf Drop/Anstieg, fehlender `transitionReason` |

## Datenmodell (db)

| Collection | Doc-ID | Inhalt |
|---|---|---|
| `assets` | Ingest-ID | filename, kind (video/music), duration, created, width, height, fps, filesize, url |
| `clipAnalysis` | Asset-ID | Bewegungsprofil, Schnitte, Bildanalyse mit Raum und nutzbaren Bereichen (v:2) |
| `musicAnalysis` | Asset-ID | Ergebnis von `analyse_music` |
| `plans` | `p<timestamp>` | number, style, signature, selection, plan, validation (Shots, Musik-Start/-Ende, Clip-Tabelle), edit, render |

## Grenzen

- Die bisherigen Renders liefen über stage (kostenlos, Wasserzeichen). Die Seite erkennt die Umgebung bei jedem Render an der Render-URL.
- Die `sample`-Aufrufe laufen über das Claude-Konto des Viewers:
  - etwa 1 pro Clip bei der ersten Analyse
  - 1–2 pro Plan
- Medienlinks stehen nur in der db und in git-ignorierten Dateien, nie im Repo.
