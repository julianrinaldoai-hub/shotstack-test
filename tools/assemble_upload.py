"""Reassemble a file the Musik-Struktur page stored as base64 chunks in its database.

Input: the directory the chunk documents were exported to (one JSON file per chunk,
fields uploadId, i, data). Checks chunk count and byte size before writing.

Usage: python3 tools/assemble_upload.py <chunk-dir> <uploadId> <chunks> <size> <out-file>
"""
import base64
import glob
import json
import sys


def main():
    folder, upload_id, n, size, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    parts = {}
    for path in glob.glob(f"{folder}/*.json"):
        doc = json.load(open(path))
        if doc.get("uploadId") == upload_id:
            parts[int(doc["i"])] = base64.b64decode(doc["data"])
    missing = [i for i in range(n) if i not in parts]
    if missing:
        sys.exit(f"missing chunks: {missing[:10]}{' …' if len(missing) > 10 else ''}")
    blob = b"".join(parts[i] for i in range(n))
    if len(blob) != size:
        sys.exit(f"size mismatch: {len(blob)} bytes, expected {size}")
    open(out, "wb").write(blob)
    print(json.dumps({"file": out, "bytes": len(blob), "chunks": n}))


if __name__ == "__main__":
    main()
