# Clip-Gewichtung (Testlabor)

Isolierte Testseite, ein claude.ai-Artifact. Sie prüft nur, wie gut Claude einzelne Immobilienclips versteht, zeitlich analysiert, bewertet und relativ zueinander gewichtet.

Nicht enthalten: Musik, Schnittplan, Timeline, Clip-Reihenfolge, Shotstack und Render.

## Ablauf

1. **Upload:**
   - MP4-Clips per Drag & Drop oder Dateiauswahl, mehrere gleichzeitig.
   - Pro Clip: Vorschau, Dateiname, Dauer, Größe.
   - Clips bis 20 MB landen in der Videoablage der Seite und sind beim nächsten Besuch noch da.
   - Ein **Set** steht für eine Immobilie; die relative Gewichtung gilt immer innerhalb eines Sets.
2. **Phase 1, Einzelanalyse:** Jeder Clip wird einzeln analysiert.
   - Im Browser, mit 12 Frames pro Sekunde:
     - Kamerabewegung pro 0,5 s
     - sichtbares Detail pro 0,25 s (fällt ab, wenn die Kamera zu nah an ein Objekt kommt)
     - Helligkeitssprünge (Flackern)
     - harte Schnitte
   - An Claude: ein Frame alle **0,25 s** über die ganze Dauer, bei 4 s also 17 Frames, mit Zeitstempel auf Kontaktbögen. So passen alle Frames ins Bildlimit eines Aufrufs.
   - Claude arbeitet in fünf Schritten:
     1. jeden Frame beschreiben
     2. den Verlauf in Abschnitte teilen
     3. nur tatsächlich sichtbare Probleme nennen
     4. Raum und Relevanz bewerten
     5. Nutzung und vorläufige Gewichtung festlegen
3. **Phase 2, Vergleich:** Claude bekommt alle Ergebnisse aus Phase 1 und ein Übersichtsbild mit je einem repräsentativen Frame pro Clip.
   - Er prüft ähnliche Räume, einzigartige Szenen, Verkaufsfaktoren und Clips, die technisch stark, aber inhaltlich nur Nebensache sind.
   - Erst danach setzt er die finalen Werte: `contentWeight`, `editingPriority`, `screenTimePriority`, `priorityClass` (A–E), `finalScore` und Screentime.
4. **Ergebnis:**
   - Oben stehen die Rangfolge und die Gruppen PRIMARY (A/B), SECONDARY (C), OPTIONAL (D) und AVOID (E).
   - Darunter folgt eine Karte pro Clip mit:
     - Werten aus Phase 1 und Phase 2
     - Zeitleiste mit nutzbarem und stärkstem Bereich
     - schwachen Bereichen, Rolle, Screentime, Playback und Problemen
     - Frame-Timeline mit Vorschaubildern
     - Debug-Angaben: analysierte Zeitpunkte, fehlende Frames, Zeitpunkt der Analyse, Vollständigkeit

## Plausibilitätsprüfung (Code, keine KI)

Jede Karte listet Widersprüche in Claudes Antwort, damit sich die Zuverlässigkeit beurteilen lässt:

- Bereiche außerhalb der Cliplänge
- stärkster Bereich außerhalb des nutzbaren Bereichs
- schwaches Ende innerhalb des nutzbaren Bereichs
- mehr empfohlene Screentime, als der nutzbare Bereich trägt (auch mit leichter Verlangsamung)
- Klasse und Gewicht passen nicht zusammen
- Nebenraum hoch gewichtet
- Gewicht folgt eher der Bildqualität als dem Inhalt
- Beschleunigung trotz schwachem Ende

## Speicherung

| Ort | Inhalt |
|---|---|
| Videoablage (`assets`) | die hochgeladenen Clips |
| `sets` | Name, Anlagedatum |
| `clips` | Set, Dateiname, Größe, Dauer, Auflösung, Verweis auf das Video |
| `analyses` | eine Version pro Analyse: Ergebnis von Phase 1, Messwerte, Debug |
| `frames` | Vorschaubilder der analysierten Frames und ein Schlüsselbild pro Analyse |
| `comparisons` | ein Eintrag pro Vergleich: Übersicht, Verkaufsfaktoren, ähnliche Clips, finale Werte und Rangfolge |

- **Analyze Clips** analysiert nur Clips ohne Ergebnis und vergleicht danach.
- **Re-analyze** (pro Clip) und **Re-analyze all** legen neue Versionen an. Ältere Versionen bleiben über die Auswahl auf der Karte abrufbar.

## Aufwand

Alle Aufrufe laufen über das Claude-Konto des Viewers, mit der stärksten Stufe (`complex`):

- 1 Aufruf pro Clip in Phase 1
- 1 Aufruf pro Vergleich in Phase 2

Shotstack wird nicht verwendet.
