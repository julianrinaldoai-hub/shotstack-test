# Video Director (Testlabor)

Isolierte Testseite, ein claude.ai-Artifact. Sie baut aus zwei fertigen Analysen und einem Style einen detaillierten Schnittplan.

Nicht enthalten: eigene Clip- oder Musikanalyse, Shotstack-Edit-JSON, Render, Uploads.

```
Clip-Analyse JSON + Musik-Analyse JSON + Style  →  Claude Director  →  Code: normalisieren + prüfen (+ bis zu 2 Korrekturrunden)  →  Export Edit Plan JSON
```

## Eingaben

| Datei | Schema | Herkunft |
|---|---|---|
| Clip-Analyse | `clip-analysis-export@1` | „Clip-Gewichtung“ → Export JSON |
| Musik-Analyse | `music-analysis-export@1` | „Musik-Struktur“ → Export JSON |

- **Prüfung:** Die Seite prüft Schema und Pflichtfelder jeder Datei. Eine Datei im falschen Feld wird erkannt.
- **Speicherung:** Beide Dateien und der letzte Plan bleiben nur im Browser des Viewers (localStorage).

## Internes Input-Schema (aus den beiden Export-Schemas abgeleitet)

### `director-input/clips@1` (aus `clip-analysis-export@1`)

- **`source`:** Schema, exportedAt, setId, setName, comparisonId, comparedAt, analysisVersion, comparisonCoversLatestAnalyses
- **`overview`, `sellingPoints`, `similarGroups`:** aus `property`
- **`clips[]`:** in Rangfolge, mit der Kurz-ID `K1…Kn`, die Claude im Plan verwendet. Pro Clip:
  - **Identität:** `clipId`, `filename`, `rank`, `duration`, `roomType`, `sceneType`, `description`
  - **Finale Gewichte (Phase 2):** `priorityClass`, `group`, `finalScore`, `contentWeight`, `editingPriority`, `screenTimePriority`
  - **Einzelwerte:** `propertyImportance`, `viewerInterest`, `visualStrength`, `heroPotential`
  - **Bereiche:**
    - `usable` = [usableStart, usableEnd]
    - `strongest` = [strongestStart, strongestEnd], auf den sicheren Bereich begrenzt
    - `weakStart`, `weakEnd`
    - **`safe`** = usable minus schwacher Anfang und schwaches Ende. Das ist die harte Grenze für den Director: Wenn ein Clip laut Analyse ab 3,0 s schwächer wird, endet `safe` bei 3,0 s, auch wenn `usableEnd` 3,5 s ist.
  - **Probleme:** `problems[]` (Typ, Bereich, Schwere; `moderate` und schwerer gilt als hart), `hardCuts`, `movementGoodFrom`, `perspectiveWorseFrom`
  - **Empfehlungen:** `minScreen`, `maxScreen` (recommendedMin/MaxScreenTime), `playback`, `playbackReason`, `roles`, `preferredRole`
  - **Begründungen:** `segments`, `bestUse`, `screenTimeReason`, `weightReason`, `uniqueness`, `similarTo`, `relativeReason`

### `director-input/music@1` (aus `music-analysis-export@1`)

- **Track:** `trackId`, `filename`, `duration`, `bpm`, `steady`, `meter`, `beatLen`, `barLen`
- **Raster:** `beats`, `downbeats`, `bars[]` (Index, Start, Ende, Energie): das finale Taktraster aus `technical.bars.list`
- **Messwerte und Ableitungen:** `sections`, `drops`, `jumps` (energyJumps), `peaks` (abgeleitete Energiespitzen), `low` (lowEnergy)
- **Gedeutet:** `structure[]` (Typ, Start, Ende, Energie, Begründung), `summary`
- **Key Moments:** `kmTech` (gemessen) und `kmInt` (gedeutet), getrennt
- **Abschnitte:** `selected` (aus `selectedSection`: usableStart, usableEnd, Auswahlart) und `candidates[]`. Auf der Seite lässt sich statt der Auswahl ein anderer Kandidat aus derselben Analyse wählen.

Für den Plan rechnet der Code den gewählten Abschnitt in **Videozeit** um: Track-Zeit minus Abschnittsstart. Bars, Beats, Drops, Sections, Energiesprünge, Struktur und Key Moments liegen dann im Abschnitt.

## Ablauf

1. **Claude** (Stufe complex) bekommt beide Analysen, den Abschnitt in Videozeit und die Schnittregeln aus dem Briefing.
   - Zuerst schreibt Claude die Director-Analyse (die 7 Fragen).
   - Dann die kreative Erklärung (Opening, Build, Energy/Middle, Hero Moments, Finale).
   - Dann die Shots.
2. **Code normalisiert** den Plan und protokolliert jede Änderung:
   - Lücken und Überlappungen unter 0,1 s schließen.
   - Schnitte im Umkreis von 50 ms auf Beat, Downbeat, Drop oder Section legen.
   - `sourceEnd` aus Dauer × Speed bzw. aus der Speed-Ramp neu berechnen.
   - Den Source-Bereich um höchstens 0,3 s verschieben, wenn er sonst über den sicheren Bereich hinausliefe.
   - Weiche Übergänge auf beide Shots spiegeln.
   - Die Source-Handles der Übergänge berechnen.
3. **Code prüft** den Plan (Validation):
   - Source-Zeit innerhalb der Clipdauer
   - nur usableStart bis usableEnd, Übergangs-Handles eingeschlossen
   - kein schwacher Anfang oder schwaches Ende, keine harten Probleme, kein harter Schnitt im Clip; Hinweise bei leichten Problemen und `perspectiveWorseFrom`
   - Timeline lückenlos von 0 bis Videolänge, Shots mindestens 0,4 s
   - Musik am Stück, Video innerhalb des Abschnitts, 23–32 s
   - jeder Clip höchstens 2×; Hinweis bei gleichem Source-Bereich, wiederholten Nebenräumen oder demselben Clip direkt hintereinander
   - Nebenräume (C–E) nicht über ihrer empfohlenen Screentime und nicht länger als der schwächste genutzte A-Clip
   - A-Clips sind im Plan enthalten (Pflicht), B-Clips sollten es sein; beide haben genug Screentime
   - Speed-Rechnung stimmt, Speed bleibt in 0,5–2,0 und passt zu `recommendedPlayback`, Speed-Ramps sind begrenzt und begründet
   - Übergänge erlaubt, auf beiden Seiten gleich, höchstens 40 % der Shot-Länge, Anzahl passend zum Style
   - Musik-Sync: jeder Schnitt auf Beat, Downbeat, Drop oder Section-Wechsel
4. **Korrektur:** Bei Fehlern bekommt Claude die Fehler- und Hinweisliste und liefert einen korrigierten Plan. Das geht höchstens zweimal. Bleiben danach Fehler, ist der Plan als „nicht bestanden“ markiert.

**Regenerate Plan** gibt Claude den vorherigen Plan mit. Ein neuer Plan darf ähnlich sein, wenn der alte gut zur Musik passt.

## Export (`schema: video-director-plan@1`)

Dateiname: `edit-plan-<style>-<track>-<datum>.json`. „Copy JSON“ kopiert dasselbe.

- **`meta`:** Zeitpunkte, Regelversion, Korrekturrunden, Herkunft beider Eingaben
- **`music`:** Track, BPM, gewählter Abschnitt; genutzter Bereich `used.trackStart` bis `trackEnd`, `continuous: true`, keine Schnitte, Sprünge oder Loops
- **`style`:** id, Label, kreative Richtung
- **`timeline`:** fps (25), Dauer, Schnitte mit Video- und Track-Zeit und musikalischem Bezug
- **`shots[]`:**
  - Clip und Source-Bereich: `shotNumber`, `sourceClip`, `clipId`, `roomType`, `priorityClass`, `usageIndex`, `sourceStart`, `sourceEnd`
  - Timeline: `timelineStart`, `timelineEnd`, `duration`, `playbackSpeed`
  - **`speedRamp`:** Punkte `atSource` und `speed`, Begründung, `segments`. Die Segmente sind Teilstücke mit konstanter Geschwindigkeit, die ein Builder als einzelne Clips umsetzen kann.
  - Übergänge: `transitionIn`, `transitionOut` und ihre Dauern, `sourceHandleBefore`, `sourceHandleAfter`
  - Inhalt: `role`, `reason`
  - **`music`:** `absoluteTrackStart`, `absoluteTrackEnd`, `relativeVideoStart`, `relativeVideoEnd`, `alignedTo` (vom Code bestimmt), `musicalMoment` (Claudes Absicht)
- **`validation`:** passed, alle Prüfungen mit Einträgen, Rechenkorrekturen des Codes
- **`summary`:**
  - Style, Track, Abschnitt, Videolänge
  - Shots, genutzte, wiederholte und ausgelassene Clips (mit Begründung), Hero-Clips
  - Screentime pro Clip mit Empfehlung
  - Dramaturgie, Schnittkonzept, kreative Erklärung, Director-Analyse

Keine UI-Daten, keine Medien, keine Datei-Links.

## Aufwand

- Ein Claude-Aufruf pro Plan, dazu höchstens zwei Korrekturaufrufe. Sie laufen über das Claude-Konto des Viewers.
- Shotstack wird nicht verwendet.
