"""Upload one local media file to Shotstack stage via the Ingest API and wait until it is ready.

The API key is injected by the environment's network proxy and never appears here.
Prints one JSON object (id, filename, duration, created, url, ...) on success.

Usage: python3 tools/ingest_upload.py <file> [--name original-filename.mp3]
       python3 tools/ingest_upload.py --delete <source-id>
"""
import json
import subprocess
import sys
import time

API = "https://api.shotstack.io/ingest/stage"


def curl(*args):
    out = subprocess.run(["curl", "-sS", "-g", "-m", "120", *args], capture_output=True, text=True, check=True).stdout
    return json.loads(out) if out.strip() else {}


def main():
    if sys.argv[1] == "--delete":
        subprocess.run(["curl", "-sS", "-g", "-m", "60", "-X", "DELETE", f"{API}/sources/{sys.argv[2]}"], check=True)
        print(json.dumps({"deleted": sys.argv[2]}))
        return
    path = sys.argv[1]
    name = sys.argv[sys.argv.index("--name") + 1] if "--name" in sys.argv else path.rsplit("/", 1)[-1]
    # 1) ask for a signed upload URL, 2) PUT the bytes to it, 3) poll the source until it is ready
    up = curl("-X", "POST", "-H", "Accept: application/json", f"{API}/upload")
    sid, put_url = up["data"]["id"], up["data"]["attributes"]["url"]
    subprocess.run(["curl", "-sS", "-g", "-m", "600", "-X", "PUT", "--upload-file", path, put_url], check=True, capture_output=True)
    for _ in range(60):
        src = curl("-H", "Accept: application/json", f"{API}/sources/{sid}")
        a = src.get("data", {}).get("attributes", {})
        if a.get("status") == "ready":
            print(json.dumps({"id": sid, "filename": name, "duration": a.get("duration"), "created": a.get("created"),
                              "url": a.get("source"), "filesize": a.get("filesize"), "extension": name.rsplit(".", 1)[-1].lower()}))
            return
        if a.get("status") == "failed":
            sys.exit(f"ingest failed for {sid}: {json.dumps(a)[:300]}")
        time.sleep(3)
    sys.exit(f"ingest for {sid} not ready after 3 minutes")


if __name__ == "__main__":
    main()
