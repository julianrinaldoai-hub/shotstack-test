# Version 4 — heutige Assets (14.10.2026), Edit-Logik von Version 3

**Status:** VORSCHLAG, wartet auf Freigabe. Keine Shotstack-Edit erstellt, nichts gerendert.
**Assets:** ausschließlich die 12 Uploads vom 14.10.2026 im Shotstack-Sandbox (stage): 11 Clips + 1 Musiktitel. Alle älteren Assets werden ignoriert.

## 1. Heutige Assets

Alle Clips: H.264, **1280×720** (= Ausgabeauflösung, also keine Hochskalierung mehr), 24 fps, 4,04s. Die Musik `zzz01m4x-bf6yy-…` (114,05s) ist byte-identisch mit dem Titel aus Version 3. Darum bleiben Beat-Raster, Sektionen und Musikschnitt aus Version 3 exakt gültig.

| C | Asset-ID | Inhalt | Kamerabewegung (gemessen) | Nutzbare Abschnitte |
|---|---|---|---|---|
| C1 | bf6he | Wohnbereich, Ringleuchte, Pampasgras im Vordergrund, grünes Sofa | Starker Push-in mit leichtem Tilt nach oben | 0–2,8 weit · 2,8–3,7 Sofa nah |
| C2 | bf6q3 | Bar mit Weinregal, warme Lichtstrahlen | **Statisch** (fest stehende Kamera, nur Lichtflackern) | Ganzer Clip, ohne Bewegung |
| C3 | bf6t0 | Fitness- und Spa-Raum mit Wanne | Langsam nach rechts, kommt zur Ruhe | 0–4 ruhig |
| C4 | bf6vs | Küche mit grüner Marmorinsel, Seeblick rechts | Fahrt nach **links**, beschleunigend, mit Push | 0–3,4 |
| C5 | bf705 | Wohnzimmer mit Panoramaverglasung, Terrasse, See | Fahrt nach **links** mit Push, gleichmäßig | Ganzer Clip (stärkster Clip) |
| C6 | bf70c | Helles Marmorbad, Holzwaschtisch | Langsamer Push | Ruhig, ganzer Clip |
| C7 | bf70n | Dunkles Steinbad, Bademantel, Dusche | Push mit Tilt | 0–1,6 Waschtisch weit · 2,0–4,0 Duschwand nah |
| C8 | bf70q | Begehbarer Kleiderschrank | Langsamer Push | Ganzer Clip |
| C9 | bf712 | Wohnbereich, Ringleuchte schwebt ins Bild, See links, Gemälde | Push mit Tilt nach oben | 0–2,4 weit · 2,4–3,3 näher |
| C10 | bf746 | Schlafzimmer mit Marmorwand, warmes Licht | **Enthält einen harten Schnitt bei 1,833s:** A = 0–1,79 (Fahrt nach rechts), B = 1,875–4,04 (Push aufs Bett) | A und B als zwei getrennte Einstellungen |
| C11 | bf774 | Dunkles Schlafzimmer, Wanne im Hintergrund | Fahrt nach **rechts**, beschleunigend | 0–1,4 · 1,5–3,0 |

Keiner der Clips ist eine Außenaufnahme.

## 2. Musik (unverändert aus Version 3)

- 74 BPM, Half-Time. Ein Beat = 0,811s, ein Takt = 3,243s.
- Musikschnitt: Takte 7–12, dann 17–18 (Breakdown + Lift 2), dann das echte Ende (Takt 34). Gesamtlänge **31,0s**.
- Lift 1 bei 6,50s · Breakdown bei 19,46s · Lift 2 bei 22,71s · Outro ab 25,96s.

## 3. Timeline

Gleiche Slots, Schnittzeiten und Speed-Ramps wie Version 3. Nur die Inhalte sind neu.

| Abschnitt | # | Video (s) | Clip (Quellbereich) | Speed | Rolle |
|---|---|---|---|---|---|
| **BUILD** | 1 | 0,000–3,250 | C2 Bar (0,00–2,11) | 0,65× + langsamer Push 1,00→1,04 (der Clip ist statisch) | Atmosphäre, Fade aus Schwarz |
| | 2 | 3,250–6,500 | C4 Küche (0,00–3,41) | **R1** 0,9→1,6× | Fahrt nach links, beschleunigt in Lift 1 |
| **WELLE 1** | 3 | **6,500**–9,750 | C9 Ringleuchte + See (0,00–2,34) | **R2** 1,4→0,6× | **HERO 1** auf Lift 1: Ringleuchte schwebt ins Bild |
| **MONTAGE A** | 4a | 9,750–10,542 | C7 Steinbad (0,00–0,79) | 1,0× | Beat 1 |
| | 4b | 10,542–11,333 | C8 Kleiderschrank (0,60–1,39) | 1,0× | Beat 2 |
| | 4c | 11,333–12,167 | C10-A Schlafzimmer (0,30–1,13) | 1,0× | Beat 3, Gegenbewegung nach rechts |
| | 4d | 12,167–12,958 | C3 Spa/Fitness (1,00–1,79) | 1,0× | Beat 4 |
| WELLE 1 | 5 | 12,958–16,208 | C1 Wohnbereich mit Pampasgras (0,00–2,77) | **R3** 0,7→1,5× | **HERO 2**, beschleunigt in Montage B |
| **MONTAGE B** | 6a | 16,208–17,042 | C7 Duschwand (2,20–2,80) | 0,72× | Beat 1 |
| | 6b | 17,042–17,833 | C2 Bar (2,40–3,19) | 1,0× (statisch) | Beat 2, ruhiger Akzent |
| | 6c | 17,833–19,458 | C11 dunkles Schlafzimmer (1,50–3,00) | **R4** 1,3→0,7× | Bremst in den Breakdown |
| **BREAKDOWN** | 7 | 19,458–22,708 | C6 helles Marmorbad (1,00–4,03) | **R5** 0,75→1,7× | Ruhig, beschleunigt in Lift 2 |
| **MONTAGE C** | 8a | **22,708**–23,500 | C9 Ringleuchte nah (2,45–3,24) | 1,0× | Lift 2 |
| | 8b | 23,500–24,333 | C10-B Bett nah (2,00–2,83) | 1,0× | Beat 2 |
| | 8c | 24,333–25,125 | C1 Sofa nah (2,85–3,64) | 1,0× | Beat 3 |
| **OUTRO** | 9 | 25,125–31,000 | **C5 Panorama mit See** (0,00–3,80) | **R6** 1,4→0,55× | Landung auf Beat 4, Fade ab 29,0 |

**Mehrfachnutzung:** C1, C2, C7 und C9 je 2×. C10 2× (beide Einstellungen getrennt). Alle anderen Clips 1×. Alle 11 Clips kommen vor, und kein Quellbild wird doppelt gezeigt.

**Grund für den Abschluss:** Es gibt keine Außenaufnahme. Deshalb landet das Ende auf C5, dem stärksten Seeblick-Clip, der dafür aufgespart wird. Die Fahrt nach links verlangsamt sich zum Schweben, dann folgt der Fade.

**Endgültige Quellbereiche:** werden im Builder mit den exakten Easing-Kurven von Studio nachgerechnet, wie bei Version 3.
