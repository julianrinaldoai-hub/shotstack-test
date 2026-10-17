# Director Planer (Testbaustein)

Isoliertes claude.ai-Artifact. Nur: **fertige Analysedaten → Director → validierter Schnittplan**.

Was der Baustein nicht macht:

- Videos oder Musik analysieren
- Frames lesen
- eigene Gewichtung
- alte Director-Analysen oder -Pläne lesen
- `buildEdit`, Shotstack-Edit-JSON oder Render

## Eingaben (Input-Schema)

Beide Dokumente erzeugt `tools/sync_director_input.py` aus den gespeicherten Ergebnissen der zwei Module. Es ist reines JSON, ohne Medien.

**`clipSets/{setId}`**: Schema `director-input/clipset@1`, Quelle „Clip-Gewichtung“

- `source`: setId, setName, comparisonId, comparedAt, `comparisonCoversLatestAnalyses`
- Zum Set: `overview`, `sellingPoints`, `similarGroups`
- **`clips[]`** in der finalen Rangfolge aus Phase 2:
  - **Identität:** `clipId`, `rank`, `filename`, `duration`, `size`, `shotstackSourceId` (über Dateiname und Bytegröße mit dem Shotstack-Upload verknüpft, für einen späteren Render)
  - **Analyse-Stand:** `analysisId`, `analysisVersion`, `analyzedAt`
  - **Inhalt:** `sceneType`, `roomType`, `shortDescription`, `propertyImportance`, `viewerInterest`, `visualStrength`
  - **Finale Gewichte (Phase 2, Source of Truth):** `contentWeight`, `editingPriority`, `screenTimePriority`, `priorityClass`, `finalScore`, `recommendedMin/MaxScreenTime`
  - **Vergleich:** `uniqueness`, `similarTo`, `relativeReason`; daneben `phase1` mit den Werten aus Phase 1
  - **Rollen:** `heroPotential`, `recommendedRoles`, `preferredRole`
  - **Bereiche:** `usableStart/End`, `strongestStart/End`, `weakStart/End`
  - **Bewegung:** `recommendedPlayback`, `playbackReason`, `cameraMovement`, `movementGoodFrom`, `perspectiveWorseFrom`
  - **Probleme und Verlauf:** `issues`, `segments` (zeitliche Analyse), `hardCuts`, `bestUseSummary`

**`tracks/{trackId}`**: Schema `director-input/track@1`, Quelle „Musik-Struktur“

- `source`: trackId, analyzedAt, shotstackJobId
- `filename`, `duration`, `url`
- `raw`: Shotstack-Rohdaten von `analyse_music`
- `interpretation`: Struktur, Key Moments, Notizen
- `candidates`: zusammenhängende Abschnitte je Stil und Länge (23, 25, 27, 30 s)

## Sync

Im Chat **„sync director“** sagen. Claude führt dann diese Schritte aus:

1. Er liest die gespeicherten Daten beider Module, nur lesend: `sets`, `clips`, `analyses`, `comparisons` sowie `tracks`, `analyses`.
2. Er baut mit `tools/sync_director_input.py` die beiden Dokumenttypen; die Clips werden dabei über `director-assets.local.json` mit den Shotstack-Uploads verknüpft.
3. Er schreibt die Dokumente in die Datenbank des Planers.

Videos werden weder kopiert noch analysiert.

## Ablauf auf der Seite

1. **Data Status:** Clip-Set, Track und Musikabschnitt wählen.
   - Beim Abschnitt gibt es zwei Möglichkeiten: „Director wählt“ aus den 12 Kandidaten des Stils, oder einen festen Kandidaten.
   - Die Musik läuft immer am Stück.
2. **Style:** Elegant, Dynamic oder Cinematic. Das ist eine Richtung im Prompt, keine Vorlage.
3. **Generate Plan:** ein Claude-Aufruf (Stufe complex). Danach prüft `validatePlan` den Plan; bei Fehlern gibt es eine Korrekturrunde.
4. **Plan:**
   - Summary
   - Timeline: Shots, verwendete Source-Bereiche, Speed, Dissolves, darunter Energie pro Takt, Takte, Sections, Drops und Key Moments
   - Shot-Liste und Validation
   - Debug: verwendete Analysen und Versionen, Musikdaten, Regel-Version, Zeitpunkte, Plan-JSON
5. **Regenerate Plan:** derselbe Input, ein neuer Versuch. Ähnliche Pläne sind erlaubt.
6. **Save Plan:** speichert den Entwurf in `plans`, zum Vergleichen von Varianten.

## Wiederverwendeter Code (unverändert kopiert)

- **Aus `director/index.html` (CORE):**
  - Frame-Raster, Easing-Kurven
  - `rampsOf`, `speedAt`, `srcUsed`, `speedLabel`, `nearest`
  - `validatePlan`: Kontinuität, Frame-Raster, Footage-Budget mit Ramps, nutzbare Bereiche, harte Schnitte, Wiederholungen, Screentime-Grenzen, Musik am Stück, Länge
- **Aus `music-analyzer/index.html` (CORE):** `modelOf`, das korrekte Taktraster für beide Shotstack-Formen.
- **Neu, nur als Adapter:** `musicCtx` und `clipCtx` übersetzen die synchronisierten Daten in den Kontext, den `validatePlan` erwartet. Sie gewichten nichts neu.

## Bekannte Eigenheit

Die Clip-Gewichtung empfiehlt für Set 1 zusammen höchstens etwa 21,7 s Screentime. Die Mindestlänge ist 23 s. Jeder Plan überschreitet deshalb bei einzelnen Hauptclips etwas die Empfehlung:

- bei Hauptbereichen bis +1 s als Hinweis
- bei Nebenräumen ab +0,3 s als Fehler
