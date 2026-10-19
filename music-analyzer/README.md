# Musik-Struktur (Testlabor)

Isolierte Testseite (claude.ai-Artifact), nur für Musik. Keine Clips, kein Schnittplan, keine Video-Timeline, kein Render.

## Rollen

| Quelle | Liefert | Kennzeichnung auf der Seite |
|---|---|---|
| Shotstack `analyse_music` (kostenlos) | alle Messwerte | `Shotstack` |
| Shotstack-Raster | Beats und Taktanfänge, exakt aus `beat`, `bar`, `bars.start` berechnet (nur bei `steady: true`, weil Shotstack dann keine Listen liefert) | `Shotstack-Raster` |
| Code | Energiesprünge, leise Bereiche, Energiespitzen, Kandidaten-Scores, Prüfung der Claude-Deutung | `Code` |
| Claude | Segmentierung, Key Moments, kurze Notizen zu den Kandidaten, Zusammenfassung; nur aus den Messwerten | `Claude` |

Der Code prüft jede Claude-Deutung gegen die Messwerte:

- Abschnittsgrenzen müssen auf Taktanfängen liegen.
- Die Abschnitte müssen den Track lückenlos abdecken.
- Das Label muss zur gemessenen Energie passen: „peak“ bei niedriger Energie wird markiert.
- Jeder Key Moment braucht einen Shotstack-Beleg (Section, Drop, Taktanfang oder Energiesprung).
- Ein „Drop“ ohne Shotstack-Drop wird markiert.

## Was Shotstack liefert (geprüft mit echten Tracks)

- **Immer:** `duration`, `bpm`, `steady`, `bars.start`, `bars.count`, `bars.energy` (ein Wert pro Takt), `sections[]` (rise/fall mit Takt) und `drops[]`.
- **Bei `steady: true`:** zusätzlich `meter`, `beat`, `bar`, `origin`, `downbeat.offset`, `downbeat.confidence` und `precision`. Listen mit `beats[]` und `downbeats[]` fehlen dann.
- **Bei `steady: false`:** `beats[]` und `downbeats[]` als Listen.
- **Nicht geliefert:** Beat-Stärke, Onsets, feine Lautheitskurve, Tempo-/Rhythmuswechsel und Stille. Die Seite zeigt diese Felder als „not available“ und nennt den abgeleiteten Ersatz.
- **Achtung, `origin`:** Laut Shotstack-Anleitung ist `origin` der erste Downbeat. In den echten Daten passen die `sections[].time` aber zu `bars.start + n × bar`, nicht zu `origin`. Die Seite rechnet deshalb mit `bars.start` und zeigt die Abweichung in der Feldtabelle an.

## Kontinuierliche Abschnitte

- **Form:** ein Startpunkt auf einem Taktanfang, Ende = Start + Länge. Kein Schnitt, kein Sprung, kein Loop.
- **Längen:** 23, 25, 27 und 30 s, dazu eine eigene Länge.
- **Teilwerte (0–10):**
  - Start (Section-Wechsel, Trackanfang, Luft nach oben)
  - Aufbau
  - Peak (Höhe und Lage)
  - Akzente (Drops, rise-Sections, Energiesprünge)
  - Ende (Taktgrenze, Section-Wechsel, Trackende, fallende Energie)
  - Variation
  - Energie passend zum Stil
- **Stile:** Neutral, Elegant, Dynamic und Cinematic ändern nur die Gewichtung der Teilwerte. Elegant bewertet zusätzlich einen ruhigen Fluss, Cinematic zusätzlich Release/Finale.
- **Taktraster:** Pro Länge zeigt die Seite, ob sie genau auf einem Takt endet. Bei 120 BPM enden 23, 25 und 27 s immer einen halben Takt daneben.

## Export

- **Bedienung:**
  - „Export JSON“ lädt den finalen Stand des gewählten Tracks als Datei herunter (`music-analysis-<track>-<datum>.json`).
  - „Copy JSON“ kopiert dieselbe Struktur in die Zwischenablage.
  - Beides geht, sobald eine Shotstack-Analyse vorliegt.
- **Nur lesend:** Der Export liest die gespeicherte Analyse und nutzt die unveränderten Funktionen der Seite (`modelOf`, `derive`, `checkInterpretation`, gespeicherte Kandidaten). Es wird nichts neu analysiert oder ergänzt.
- **Struktur** (`schema: music-analysis-export@1`):
  - **`meta`:** trackId, filename, duration, analysisVersion (= Zeitpunkt der Shotstack-Analyse), createdAt, interpretedAt, Shotstack-Job-ID, Bedeutung der Quellen-Kennzeichnung
  - **`track`:** Dateidaten und Asset-Referenz (Quelle, URL)
  - **`technical`:** nur Messwerte und daraus berechnete Werte, jeweils mit `source`
    - Shotstack: BPM, steady, meter, Beats, Downbeats, sections, drops, `bars.energy`, precision
    - finales Taktraster `bars.list` (Index, Start, Ende, Energie), berechnet nach `bars.start + n × bar` bzw. aus `downbeats[]`
    - Code: Energiesprünge, Energiespitzen, leise Bereiche
    - Nicht geliefert, daher `available: false`, `value: null`: onsets, strongBeats, peaks, loudness, rhythmDensity, tempoChanges, silence
    - `raw`: die unveränderten Shotstack-Rohdaten
  - **`structure`:** Claudes Abschnitte (type, start, end, Begründung) mit der Prüfung durch den Code. `confidence` ist `null`, weil Claude keine liefert.
  - **`keyMoments`:** getrennt in `technical` (Shotstack und Code) und `interpreted` (Claude, mit Beleg und Prüfhinweisen)
  - **`selectedSection`:**
    - der auf der Karte markierte Abschnitt (`selection: "marked-by-user"`)
    - sonst der beste Kandidat des aktuellen Stils (`"suggested-top-score"`)
    - Felder: usableStart, usableEnd, usableDuration; immer am Stück, ohne Schnitte, Loops oder Sprünge
  - **`candidates`:** alle Kandidaten (4 Stile × 23/25/27/30 s × 3, dazu die eigene Länge) mit start, end, duration, score, Teilwerten, Begründung des Codes und Claudes Notiz
- **Nicht enthalten:** Audio, Binärdaten und UI-Daten.

## Musik hochladen

- **Warum über den Chat:** `analyse_music` braucht eine öffentliche URL. Die Seite selbst kann weder die Shotstack-Ingest-API erreichen, noch sind Dateien in ihrer Ablage öffentlich (geprüft: 403 ohne Anmeldung). Deshalb läuft der Upload in zwei Schritten.
- **Schritt 1, in der Seite:** MP3, WAV oder M4A (bis 25 MB) per Drag & Drop. Die Seite speichert die Datei in Teilen zu 160 KB in `uploadChunks` und legt einen Eintrag in `uploads` mit Status `pending` an.
- **Schritt 2, im Chat „sync“ sagen.** Claude führt dann diese Schritte aus:
  1. die Teile auslesen und mit `tools/assemble_upload.py` zusammensetzen (Prüfung von Teilzahl und Bytegröße)
  2. die Datei mit `tools/ingest_upload.py` zu Shotstack (stage) hochladen
  3. den Track in `tracks` eintragen
  4. den Upload auf `done` setzen und die Teile löschen
- **Kein automatischer Anstoß:** Die Seite stößt die Übernahme nicht selbst an, sie geschieht nur auf deine Anweisung im Chat.

## Speicherung (db)

| Collection | Inhalt |
|---|---|
| `tracks` | Musik-Assets aus der Shotstack-Ingest-API (stage), per „sync“ im Chat eingetragen, oder per URL hinzugefügt |
| `uploads`, `uploadChunks` | in der Seite hochgeladene Dateien bis zur Übernahme zu Shotstack |
| `analyses/{trackId}` | Shotstack-Rohdaten, Job-ID, gelieferte Felder, Claude-Deutung, berechnete Kandidaten, Zeitpunkte |

- **Re-analyze:** führt Shotstack und Claude neu aus.
- **Clear analysis:** löscht die gespeicherte Analyse, nach einer Bestätigung auf der Seite.

## Aufwand

- Shotstack-Musikanalyse: kostenlos.
- Claude-Deutung: ein Aufruf pro Analyse (Stufe „complex“), über das Claude-Konto des Viewers.
