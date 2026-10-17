"""Build the Director Planner's input documents from the finished analysis modules (JSON only, no media).

Reads database exports (one JSON file per document, as written by an ArtifactData read with out_dir):
  <clip-dir>/sets, clips, analyses, comparisons   from "Clip-Gewichtung"
  <music-dir>/tracks, analyses                    from "Musik-Struktur"
Optionally matches clips to Shotstack stage sources by filename + byte size (for a later render).

Writes one file per planner document into <out-dir>/clipSets/<setId>.json and <out-dir>/tracks/<trackId>.json
and prints the list of written documents. Nothing is re-analysed.

Usage: python3 tools/sync_director_input.py <clip-dir> <music-dir> <out-dir> [--shotstack director-assets.local.json]
"""
import glob
import json
import os
import sys
from datetime import datetime, timezone

CLIP_URL = "https://claude.ai/artifact/WpNHWC3FN8Y7t93BWRAaYi"
MUSIC_URL = "https://claude.ai/artifact/6gLoRK4wghPMDhxk9E1LnM"
CLIP_FIELDS = ["sceneType", "roomType", "shortDescription", "propertyImportance", "viewerInterest", "visualStrength", "heroPotential",
               "recommendedRoles", "preferredRole", "usableStart", "usableEnd", "strongestStart", "strongestEnd", "weakStart", "weakEnd",
               "recommendedPlayback", "playbackReason", "cameraMovement", "movementGoodFrom", "perspectiveWorseFrom", "issues", "segments",
               "bestUseSummary", "weightReason", "screenTimeReason", "confidence", "uncertainties"]
FINAL_FIELDS = ["contentWeight", "editingPriority", "screenTimePriority", "priorityClass", "recommendedMinScreenTime", "recommendedMaxScreenTime"]


def docs(folder):
    out = {}
    for path in glob.glob(os.path.join(folder, "*.json")):
        out[os.path.basename(path)[:-5]] = json.load(open(path))
    return out


def main():
    clip_dir, music_dir, out_dir = sys.argv[1:4]
    stage = json.load(open(sys.argv[sys.argv.index("--shotstack") + 1])) if "--shotstack" in sys.argv else []
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    sets, clips, analyses, comps = (docs(os.path.join(clip_dir, c)) for c in ("sets", "clips", "analyses", "comparisons"))
    written = []
    for set_id, s in sets.items():
        set_clips = {cid: c for cid, c in clips.items() if c.get("setId") == set_id}
        cmp_list = sorted((c for c in comps.values() if c.get("setId") == set_id), key=lambda c: c.get("createdAt", ""))
        if not set_clips or not cmp_list:
            continue
        cmp_id = [k for k, v in comps.items() if v is cmp_list[-1]][0]
        cmp = cmp_list[-1]
        rows = []
        for rank, cid in enumerate(cmp.get("ranking", []), 1):
            c, aid = set_clips.get(cid), cmp.get("analysisIds", {}).get(cid)
            a, fin = analyses.get(aid), cmp.get("clips", {}).get(cid, {})
            if not c or not a or not a.get("result"):
                continue
            r = a["result"]
            match = [x for x in stage if x.get("kind") == "video" and x.get("filename") == c["filename"] and x.get("filesize") == c.get("size")]
            row = {"clipId": cid, "key": fin.get("key"), "rank": rank, "filename": c["filename"], "size": c.get("size"),
                   "duration": a.get("debug", {}).get("durationMeasured") or c.get("duration"),
                   "shotstackSourceId": match[-1]["id"] if match else None,
                   "analysisId": aid, "analysisVersion": a.get("version"), "analyzedAt": a.get("createdAt"), "analysisComplete": a.get("debug", {}).get("complete"),
                   "hardCuts": a.get("metrics", {}).get("cuts", []),
                   "finalScore": fin.get("finalScore"), "uniqueness": fin.get("uniqueness"), "similarTo": fin.get("similarTo", []),
                   "relativeReason": fin.get("relativeReason"), "phase1": {k: r.get(k) for k in FINAL_FIELDS}}
            row.update({k: r.get(k) for k in CLIP_FIELDS})
            # final weights from the comparison (phase 2) are the source of truth; phase 1 stays alongside for reference
            row.update({k: fin.get(k, r.get(k)) for k in FINAL_FIELDS})
            rows.append(row)
        newest = {cid: max((a for a in analyses.values() if a.get("clipId") == cid and a.get("result")), key=lambda a: a.get("version", 0), default=None) for cid in set_clips}
        fresh = all(newest[cid] is None or cmp.get("analysisIds", {}).get(cid) == f"a_{cid}_{newest[cid]['version']}" for cid in set_clips)
        doc = {"schema": "director-input/clipset@1", "syncedAt": now,
               "source": {"artifact": "Clip-Gewichtung", "url": CLIP_URL, "setId": set_id, "setName": s.get("name"), "comparisonId": cmp_id,
                          "comparedAt": cmp.get("createdAt"), "comparisonCoversLatestAnalyses": fresh},
               "overview": cmp.get("overview"), "sellingPoints": cmp.get("sellingPoints", []),
               "similarGroups": cmp.get("similarGroups", []), "clips": rows}
        path = os.path.join(out_dir, "clipSets", f"{set_id}.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        json.dump(doc, open(path, "w"))
        written.append({"collection": "clipSets", "doc_id": set_id, "file_path": path, "bytes": os.path.getsize(path), "clips": len(rows)})
    tracks, manal = docs(os.path.join(music_dir, "tracks")), docs(os.path.join(music_dir, "analyses"))
    for tid, a in manal.items():
        if not a.get("raw"):
            continue
        t = tracks.get(tid, {})
        it = a.get("interpretation") or {}
        doc = {"schema": "director-input/track@1", "syncedAt": now,
               "source": {"artifact": "Musik-Struktur", "url": MUSIC_URL, "trackId": tid, "analyzedAt": a.get("analyzedAt"),
                          "interpretedAt": a.get("interpretedAt"), "shotstackJobId": a.get("shotstackId")},
               "filename": t.get("filename") or a.get("filename"), "duration": a["raw"].get("duration"), "url": t.get("url") or a.get("url"),
               "raw": a["raw"], "interpretation": {k: it.get(k) for k in ("summary", "segments", "keyMoments", "caveats", "candidateNotes")},
               "candidates": a.get("candidates", {})}
        path = os.path.join(out_dir, "tracks", f"{tid}.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        json.dump(doc, open(path, "w"))
        written.append({"collection": "tracks", "doc_id": tid, "file_path": path, "bytes": os.path.getsize(path)})
    print(json.dumps(written, indent=1))


if __name__ == "__main__":
    main()
