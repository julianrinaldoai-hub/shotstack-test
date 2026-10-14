"""List Shotstack stage ingest sources for the director test page.

Read-only and free: GET /ingest/stage/sources (the API key is injected by the
environment's network proxy and never appears here). Prints one JSON object
per asset, ready to be written to the page's `assets` collection.

Usage: python3 tools/sync_assets.py [--out director-assets.local.json]
"""
import glob
import json
import subprocess
import sys

API = "https://api.shotstack.io/ingest/stage/sources"
AUDIO_EXT = {"mp3", "wav", "m4a", "aac", "ogg", "flac"}


def fetch(url):
    out = subprocess.run(["curl", "-sS", "-H", "Accept: application/json", url],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def main():
    items, url = [], API
    while url:
        page = fetch(url)
        items += page.get("data") or []
        nxt = (page.get("meta") or {}).get("next")
        url = nxt if nxt and nxt.startswith("http") else (API + "?next=" + nxt if nxt else None)

    # uploads made through signed URLs carry no filename: recover it from local manifests
    known = {}
    for path in sorted(glob.glob("ingest-manifest*.json")):
        for name, v in (json.load(open(path)).get("sources") or {}).items():
            if v.get("id") and "." in name:
                known[v["id"]] = name

    assets = []
    for it in items:
        a = it.get("attributes", {})
        if a.get("status") != "ready" or not a.get("source"):
            continue
        ext = (a.get("extension") or a["source"].rsplit(".", 1)[-1]).lower()
        kind = "music" if ext in AUDIO_EXT or not a.get("width") else "video"
        assets.append({
            "id": it["id"],
            "filename": a.get("filename") or known.get(it["id"]) or it["id"],
            "kind": kind,
            "duration": a.get("duration"),
            "created": a.get("created"),
            "width": a.get("width"),
            "height": a.get("height"),
            "fps": a.get("fps"),
            "filesize": a.get("filesize"),
            "url": a["source"],
        })
    assets.sort(key=lambda x: (x["created"] or "", x["filename"]))

    if "--out" in sys.argv:
        path = sys.argv[sys.argv.index("--out") + 1]
        json.dump(assets, open(path, "w"), indent=2)
        print(f"wrote {len(assets)} assets to {path}", file=sys.stderr)
    else:
        print(json.dumps(assets, indent=2))


if __name__ == "__main__":
    main()
