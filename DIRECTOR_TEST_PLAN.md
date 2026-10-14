# Shotstack Director Test: technischer Plan (Milestone 1)

Status: Vorschlag. Noch nichts umgesetzt, nichts gerendert, keine kostenpflichtigen Aufrufe.

## 1. Bestandsaufnahme

| Bereich | Heute | Bewertung |
|---|---|---|
| Testseite | Keine. Das Repo enthält nur Pläne (`EDIT_PLAN*.md`), Python-Builder (`tools/build_v2–v4.py`, `tools/plan_v3.py`), Analyse-Skripte (`analysis/*.py`) und Edit-JSONs | Neu zu bauen |
| Assets laden | Upload über die Shotstack **Ingest API** (stage). Der Key ist ein Netzwerk-Secret, das der Proxy in diesem Container einsetzt; er ist nie im Code. Die Asset-Liste kommt per `GET /ingest/stage/sources` mit `filename`, `duration`, `created`, `width/height`, `fps`. Die lokale Zuordnung steht in `ingest-manifest*.json` (git-ignoriert) | Weiterverwenden |
| Shotstack ansprechen | Studio-Vorschau, Render und Status über den **Shotstack-Connector** (MCP-Tools `studio`, `render_video`, `get_render_status`, `create_studio_link`). Neu und kostenlos verfügbar: `analyse_music` und `get_analysis_status` | Weiterverwenden, keine neue Render-Architektur |
| Edits bauen | `tools/build_v4.py`: Taktraster, Frame-Snapping auf 24 fps, Speed-Ramps mit den exakten Easing-Kurven von Studio, Prüfung des Footage-Budgets (kein Quellbild doppelt, kein Überlauf), Sperrbereiche (harter Schnitt in einem Clip), `"auto"`-Verkettung gegen Studios Float-Overlap-Fehler, Musikschnitt mit Micro-Fades | **Kern übernehmen:** Validierung und Edit-Erzeugung. Das feste Schnittmuster entfällt |
| Analyse | Python mit ffmpeg und librosa in diesem Container: Kamerabewegung, harte Schnitte, Beat-Raster, Sektionen, Takt-Ähnlichkeit | Bewegungs- und Schnitt-Erkennung im Browser nachbauen; die Musik übernimmt `analyse_music` |

Einschränkungen:
- Der Container ist für dich nicht erreichbar. Ein lokaler Server mit Web-UI scheidet aus.
- Eine Webseite darf den Shotstack-Key nicht enthalten.

## 2. Architektur

**Eine einzelne Testseite als claude.ai-Artifact** (privat, nur für dich), mit diesen Laufzeit-Funktionen:
- **`mcp` → Shotstack-Connector**, Aufrufe laufen mit deinen Rechten:
  - `analyse_music` und `get_analysis_status`: Musikanalyse, kostenlos
  - `render_video` und `get_render_status`: Render und Status
  - `create_studio_link`: optionale Vorschau, ebenfalls kostenlos
- **`sample` → Claude als Director:** bekommt Clip-Analyse, Musik-Karte und Style und liefert den Plan als JSON. Mit Bildern, damit Claude die Clips „sieht“.
- **`db`:** Asset-Liste, Analyse-Cache, alle Pläne und Renders. Damit kann ich Pläne später auch hier auslesen und vergleichen.

**Asset-Liste:** Der Shotstack-Connector hat kein Tool zum Auflisten. Deshalb liest ein kleines Skript in diesem Container die Ingest-API (kostenloses `GET`) und schreibt die Liste in die db der Seite. Für neue Uploads sagst du mir kurz „sync“.

## 3. Ablauf auf der Seite

1. **ASSETS:** Tabelle getrennt nach Video und Musik: Dateiname, Typ, Dauer, Upload-Zeitpunkt, Auflösung. Der Filter „nur heute“ ist standardmäßig aktiv, ältere Assets sind ausgegraut. Pro Asset gibt es eine Auswahl-Checkbox.
2. **STYLE:** ELEGANT / DYNAMIC / CINEMATIC als kreative Richtung im Director-Prompt, keine Vorlage.
3. **ANALYZE & PLAN:**
   - **Clips:** Die Seite lädt jeden Clip nacheinander, nicht 16 auf einmal, und tastet Einzelbilder per Canvas ab. Daraus misst sie Bewegungsrichtung, Push-in/out und Tempo pro 0,5s und erkennt harte Schnitte und Bildsprünge (portiert aus `analysis/motion.py` und der Schnitt-Erkennung). Zusätzlich gehen 3–4 Vorschaubilder pro Clip an Claude: Inhalt, Qualität, KI-Fehler wie deformierte Möbel, nutzbare Abschnitte. Ergebnisse werden pro Asset-ID zwischengespeichert.
   - **Musik:** `analyse_music` liefert Tempo, Beats, Downbeats, Takte, Energie pro Takt, Drops und Sektionen.
   - **Director:** Claude bekommt Clip-Steckbriefe, Musik-Karte, Style und die Regeln. Er entscheidet selbst über Reihenfolge, Auslassungen, Mehrfachnutzung, In/Out-Punkte, Hero-Shots, Montagen, Speed-Ramps, Transitions und Musikausschnitt. Es gibt **keine Vorlage und kein festes Muster**.
4. **Validierung (Code, kein LLM):** aus `build_v4.py` portiert. Die Seite schnappt alle Zeiten auf Frames, prüft das Footage-Budget mit den Easing-Kurven, Sperrbereiche, Clip-Längen und dass Cuts auf Beats liegen. Verstößt der Plan dagegen, schickt sie Claude einmal die konkrete Fehlerliste zur Korrektur; erst danach zeigt sie ihn an. Zum Schluss erzeugt sie die Shotstack-Edit-JSON.
5. **PLAN-ANZEIGE:**
   - Oben: Clip-Analyse, Musik-Analyse und Spannungsbogen.
   - Tabelle pro Shot: Source Clip, Source Start und End, Timeline Start und End, Speed bzw. Ramp-Kurve, Transition, Role, Begründung.
   - Dazu ein kleiner Zeitstrahl mit Shots über den Takten.
6. **REGENERATE PLAN:** gleiche Eingaben plus eine Kurzfassung der bisherigen Pläne mit der Vorgabe „deutlich anders, aber genauso sinnvoll“. Jeder Plan wird mit Nummer gespeichert und bleibt zum Vergleich aufrufbar.
7. **RENDER:** erst nach Bestätigungsdialog. `render_video` mit der validierten Edit-JSON.
8. **STATUS:** Die Shotstack-Status werden so angezeigt:
   - `queued` und `fetching` → **preparing**
   - `rendering` und `saving` → **rendering**
   - `done` → **done**
   - `failed` → **failed**

   Danach zeigt die Seite den Video-Player, die Render-URL und die Render-ID, gespeichert beim jeweiligen Plan.

## 4. Dateien

| Datei | Neu/geändert | Inhalt |
|---|---|---|
| `director/index.html` | neu | Die Testseite: UI, Browser-Analyse, Director-Aufruf, Validierung, Edit-Erzeugung, Render und Status. Eine einzige Datei ohne Build-Schritt |
| `director/README.md` | neu | Bedienung, Datenmodell in der db, Grenzen |
| `tools/sync_assets.py` | neu | Liest `GET /ingest/stage/sources` und gibt die Asset-Liste für die db aus. Nur lesende, kostenlose Aufrufe |
| `tools/editlib.py` | neu (optional) | Gemeinsame Validierung aus `build_v4.py` als Python-Modul, damit ich gespeicherte Pläne hier gegenprüfen kann |
| `.gitignore` | geändert | Lokale Sync-Ausgaben mit Medienlinks ausschließen |
| `tools/build_v*.py`, `EDIT_PLAN*.md`, `analysis/` | unverändert | Bleiben als Referenz |

## 5. Offene Punkte vor der Umsetzung

1. **Kosten beim Rendern:** Ob der Connector auf stage (Sandbox, kostenlos mit Wasserzeichen) oder auf v1 (Credits) rendert, kann ich nicht ohne Aufruf sehen. Die Seite zeigt deshalb vor jedem Render einen Bestätigungsdialog. Beim ersten Render prüfen wir das Ergebnis gemeinsam.
2. **Verbrauch:** `sample`-Aufrufe für Director und Bildanalyse laufen über dein Claude-Konto. Pro Analyze & Plan sind es etwa 2–3 Aufrufe; die Clip-Analyse wird zwischengespeichert.
3. **Voraussetzungen:** Der Shotstack-Connector muss in deinem claude.ai verbunden sein (ist er), und die Seite muss in claude.ai geöffnet werden.
