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

## Speicherung (db)

| Collection | Inhalt |
|---|---|
| `tracks` | Musik-Assets aus der Shotstack-Ingest-API (stage), per „sync“ im Chat eingetragen, oder per URL hinzugefügt |
| `analyses/{trackId}` | Shotstack-Rohdaten, Job-ID, gelieferte Felder, Claude-Deutung, berechnete Kandidaten, Zeitpunkte |

- **Re-analyze:** führt Shotstack und Claude neu aus.
- **Clear analysis:** löscht die gespeicherte Analyse, nach einer Bestätigung auf der Seite.

## Aufwand

- Shotstack-Musikanalyse: kostenlos.
- Claude-Deutung: ein Aufruf pro Analyse (Stufe „complex“), über das Claude-Konto des Viewers.
