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
4. **Kreative Prüfung (Code, Regeln v2):** Wirkt der Schnitt wie von einem Menschen? Punkte mit „repair“ gehen zurück an Claude:
   - Taktraster: mindestens 60 % der Shots genau 1, 2 oder mehr Takte lang, sichtbar wiederkehrende Shot-Längen, oder fast jeder Taktanfang hat einen Schnitt
   - kein starker Selling Point in den ersten 6 s (Klasse A, Rang 1–2 oder starker B-Raum)
   - eine zweite Verwendung mit mehr als 40 % Source-Overlap, oder eine Wiederholung eines statischen Clips
   - Screentime: Nebenclips über recommendedMax; A/B mehr als 20 % darüber ohne Grund in `summary.screenTimeOverrides`, mehr als 50 % immer; Nebenclips über 25 % des Videos
   - Speed entgegen der Analyse: bei „normal“ über ±25 %, oder über ±10 % ohne `speedReason`
   - sichtbares Artefakt (artifact, morph, warp …) im genutzten Bereich; ein Clip, dessen Artefakt mindestens 70 % des nutzbaren Bereichs abdeckt und der nicht Klasse A ist, wird gar nicht verwendet (`artifact-clip`)
   - Füllstoff (`filler`): ein Clip aus der eigenen Liste `directorAnalysis.fillerClips`, oder ein C/D/E-Clip ohne Begründung in `summary.keptSecondary`. Nebenclips bleiben standardmäßig weg.
   - Video unter 22,5 s: Ziel sind etwa 23 s, keine Pflicht. Unvermeidbar, wenn das starke Material ohne Füllstoff nicht mehr trägt.
   - Reverse: mehr als eine Forward→Reverse-Sequenz ohne Begründung in `summary.secondReverseJustification` (höchstens zwei), mehr als 2 Reverse-Shots, mehr als ein Richtungswechsel pro Shot, Wechsel ohne Turnaround, ohne Begründung, oder auf Material, bei dem die Analyse Wasser, Menschen, Vorhänge oder Ähnliches nennt bzw. Artefakte oder Lichtprobleme meldet
5. **Reparatur (Regeln v3): PLAN V1 → Prüfung → PLAN V2 → Prüfung → PLAN V3**, höchstens 2 Reparaturrunden.
   - **Auslöser:** Hat ein Plan technische Fehler oder vermeidbare kreative Punkte, ist er nicht final.
   - **Was Claude bekommt:**
     - die komplette Liste: Fehler; kreative Punkte mit jeweils einem konkreten Ziel; Hinweise
     - das Material pro Clip: sicherer Bereich, Maximum, ob ein Turnaround passt, wie der Clip im alten Plan genutzt wurde
     - den Auftrag, den Edit **neu aufzubauen**: Shots entfernen, Clips weglassen, umstellen, Bereiche, Längen und Schnittpunkte ändern, Video kürzen, Wiederholungen streichen, Reverse einsetzen, Speed und Übergänge ändern
   - **Echte Änderung:** Der Code vergleicht jede Antwort mit der Vorversion.
     - Verglichen werden Shots, Bereiche, Timeline, Videolänge, ausgelassene Clips und Reverse.
     - Eine identische Antwort zählt nicht als neue Version: Claude bekommt sie als „identisch“ zurück und wird erneut gefragt.
     - Ungültiges JSON wird einmal neu angefordert.
     - Scheitert die Runde zweimal, ist sie verbraucht.
   - **Ergebnis:** Verwendet wird die beste Version (Fehler vor vermeidbaren vor allen kreativen Punkten vor Hinweisen).
   - **Versionen:** Die Seite zeigt jede Version mit ihrer Änderung zur Vorversion (z. B. „13 → 8 Shots · weggelassen: 5.mp4 · Video 27,00 → 20,80 s“) und die verworfenen Antworten.
6. **Status als Gate:**
   - **`final`:** keine Fehler, keine kreativen Punkte. Der Export ist frei.
   - **`needs-repair`:** Mindestens ein vermeidbarer Punkt ist offen, egal wie viele Runden gelaufen sind; oder der Plan stammt aus älteren Regeln. Vermeidbare Punkte werden nie akzeptiert.
     - Der Export ist gesperrt.
     - „Plan reparieren“ startet zwei weitere Runden ab der besten Version.
   - **`final-with-warnings`** („Final with unresolved creative warnings“): nur, wenn alle offenen Punkte unvermeidbar sind.
     - Jeder offene Punkt wird mit Begründung angezeigt: vermeidbar oder unvermeidbar, dazu Claudes Erklärung aus `summary.unresolved`.
     - Export erst nach ausdrücklicher Bestätigung (Checkbox). Im JSON stehen dann `meta.status` und `acceptedUnresolved: true`.
   - **`failed`:** technische Fehler. Der Export ist gesperrt.
   - **Unvermeidbar** ist nur die Videolänge, und nur wenn das starke Material ohne Füllstoff nicht reicht.
     - Gerechnet wird mit A/B-Clips ohne flächiges Artefakt, je höchstens recommendedMax +20 %, ohne Wiederholungen, mit einem Turnaround und mit Sicherheitsabstand: unter 23,5 s.
     - Wiederholungen, Überschreitungen und Artefakte lassen sich immer wegschneiden; der Preis ist ein kürzeres Video.

Die technische Prüfung (Schritt 3) ist gegenüber Regeln v1 unverändert. Sie liest den Source-Bereich jetzt aus allen Segmenten eines Shots, damit sie auch Reverse-Shots prüft.

**Regenerate Plan** gibt Claude den vorherigen Plan mit. Ein neuer Plan darf ähnlich sein, wenn der alte gut zur Musik passt.

## Schnittlogik (Regeln v2–v4)

Priorität: 1 Zuschauerinteresse, 2 starke Immobilie zeigen, 3 visueller Flow, 4 musikalischer Flow, 5 Style, 6 technisches Raster.

- **Marker statt Raster:** Musikmarker sind Orientierung. Ein Shot darf mitten im Takt auf einem Beat beginnen, mehrere Takte überspannen oder einen Marker überspringen.
- **Shot-Längen:** variieren natürlich, ohne erkennbares Muster.
- **Selling Point früh:** ein sehr starker Clip in den ersten 3–6 s.
- **Auslassen:** Nebenclips (C/D/E) bleiben standardmäßig weg. Behalten nur mit Begründung in `summary.keptSecondary`. Was der Director selbst Füllstoff nennt, fliegt raus.
- **Länge:** Etwa 23 s sind das Ziel, keine Pflicht. Qualität geht vor: Trägt das starke Material weniger, wird das Video kürzer, statt Füllstoff, Wiederholungen oder Reverse für Länge einzusetzen. Die Musik läuft am Stück und blendet am Videoende aus.
- **Wiederholung:** nur mit klar anderem Bereich (höchstens ca. 35–40 % Overlap), nie bei statischen oder Nebenclips.
- **Speed:** `recommendedPlayback` gilt. Abweichungen nur mit `speedReason`.
- **Reverse:** Forward→Reverse ist ein Spezialwerkzeug. Bei 20–30 s normalerweise höchstens eine prominente Sequenz; eine zweite nur, wenn sie visuell klar anders wirkt und die Musik sie stark trägt. Nie für Länge.
- **recommendedMax:** Ein Turnaround rechtfertigt keine Screentime weit darüber. Mehr als etwa 20 % darüber braucht einen starken Grund, sonst wird gekürzt.

### Reverse und Richtungswechsel

- **Reverse-Shot:** `playback: {direction: "reverse", speed}`; sourceStart liegt über sourceEnd.
- **Richtungswechsel:** `segments: [{sourceStart, sourceEnd, direction, speed, timelineStart, timelineEnd, turnaroundIn, turnaroundOut}]` und `turnaround: {enabled, type: "smooth-speed-ramp", minSpeed: 0, duration}`.
  - Beim Turnaround fällt die Geschwindigkeit linear auf 0 und steigt in Gegenrichtung wieder an, standardmäßig 0,25 s auf jeder Seite.
  - Fehlt die Angabe, setzt der Code den weichen Turnaround und protokolliert das.
- **Nur gute Bereiche:** Auch Reverse muss im sicheren Bereich bleiben. Es dreht am Ende des guten Bereichs und fährt nie erst in einen schlechten Bereich hinein.
- **Zeitrechnung:** Segmentdauer = |Span| / Speed + halbe Turnaround-Zeit je Seite. Der Code berechnet daraus das letzte Source-Ende.

### Technische Umsetzbarkeit (geprüft 19.10.2026)

- **Shotstack Edit API:** Das `speed` eines Video-Assets darf ein Tween-Array sein.
  - Laut Shotstack-Doku ändert sich die Geschwindigkeit zwischen Tweens linear, 0 friert das Bild ein, und ein negativer Wert spielt ab `trim` rückwärts.
  - Ein konstanter `speed` als Zahl ist auf 0–10 begrenzt; Reverse braucht deshalb immer das Array.
  - Ein Richtungswechsel mit Turnaround ist so in **einem** Clip abbildbar: 1 → 0 → −1.
- **Pro Shot im Export:** `builder: {trim, speed}` mit genau diesen Tweens. Für einen Reverse-Shot ist das `[{from: -1, to: -1, start: 0, length}]`.
  - Der Code hat geprüft, dass die Tweens über die Zeit integriert auf denselben Source-Frame führen wie der Plan.
- **Noch offen:**
  - Es gibt noch keinen Builder, der `video-director-plan@1` liest (`meta.playbackSupport.reverse.videoDirectorBuilder: "not implemented yet"`).
  - Reverse ist noch nicht durch einen Test-Render bestätigt (`verifiedByTestRender: false`).
  - Reverse wird nicht stillschweigend durch eine andere Bewegung ersetzt.

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
  - Wiedergabe: `playback` (direction, speed), `segments`, `turnaround`, `speedReason`, `builder` (Shotstack-trim und -speed), `sourceRange` (der insgesamt genutzte Bereich)
  - Inhalt: `role`, `reason`
  - **`music`:** `absoluteTrackStart`, `absoluteTrackEnd`, `relativeVideoStart`, `relativeVideoEnd`, `alignedTo` (vom Code bestimmt), `musicalMoment` (Claudes Absicht)
- **`validation`:** passed, alle technischen Prüfungen mit Einträgen, Rechenkorrekturen des Codes und `creativeReview` (ok, offene Punkte, Notizen)
- **`summary`:**
  - Style, Track, Abschnitt, Videolänge
  - Shots, genutzte, wiederholte und ausgelassene Clips (mit Begründung), Hero-Clips
  - Screentime pro Clip mit Empfehlung
  - Reverse-Shots, Shot-Längen, Zeitpunkt des ersten starken Selling Points
  - Dramaturgie, Schnittkonzept, Selbstkritik, kreative Erklärung, Director-Analyse

Keine UI-Daten, keine Medien, keine Datei-Links.

## Aufwand

- Ein Claude-Aufruf pro Plan, dazu höchstens zwei Reparaturrunden mit je bis zu zwei Anfragen (bei identischer oder ungültiger Antwort). Sie laufen über das Claude-Konto des Viewers.
- Shotstack wird nicht verwendet.
