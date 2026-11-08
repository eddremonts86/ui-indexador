#!/usr/bin/env python3
"""Embed the catalog for semantic search, with the local Ollama.

  .venv/bin/python embed-catalog.py [--ollama http://localhost:11434] [--model nomic-embed-text]

Writes data/embeddings.npy (float16, N x 256) and data/embeddings.json (the item ids and a hash of the text
each vector was made from). Rerunning only embeds items whose text changed or that are new, so a re-crawl
costs seconds, not the ~7 minutes of the first run. Icons and examples are left out: they are hidden from
searches by default and would be a third of the work.

nomic-embed-text is trained with Matryoshka dimensions, so the first 256 of its 768 dimensions, renormalised,
keep most of the quality at a third of the size. Needs numpy (requirements.txt).
"""

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np

DATA = Path(__file__).resolve().parent.parent / "data"
DIMS = 256
BATCH = 256


def text_of(r):
    return " ".join(x for x in (r["n"].replace("-", " "), r.get("ti", ""), r.get("d", ""), r["k"],
                                " ".join(r.get("c", []))) if x)


def embed(base, model, texts, prefix):
    body = json.dumps({"model": model, "input": [prefix + t for t in texts], "truncate": True}).encode()
    req = urllib.request.Request(f"{base}/api/embed", data=body, headers={"Content-Type": "application/json"})
    for attempt in range(3):  # the Ollama runner sometimes drops a request ("connection reset"); it recovers
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                v = np.asarray(json.load(r)["embeddings"], dtype=np.float32)[:, :DIMS]
            return v / np.linalg.norm(v, axis=1, keepdims=True)
        except (urllib.error.URLError, ConnectionError) as e:
            err = e.read()[:200] if isinstance(e, urllib.error.HTTPError) else e
            time.sleep(2 * (attempt + 1))
    if len(texts) == 1:  # one text the model will not take: leave it unembedded (keyword search still finds it)
        print(f"  skipped one item: {err!r}", file=sys.stderr)
        return np.zeros((1, DIMS), dtype=np.float32)
    half = len(texts) // 2
    return np.vstack([embed(base, model, texts[:half], prefix), embed(base, model, texts[half:], prefix)])


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ollama", default=os.environ.get("UI_INDEXER_OLLAMA", "http://localhost:11434"))
    ap.add_argument("--model", default=os.environ.get("UI_INDEXER_EMBED_MODEL", "nomic-embed-text"))
    a = ap.parse_args()

    items = [r for r in json.loads((DATA / "catalog.json").read_text())["items"]
             if r["k"] != "icon/logo" and r["t"] != "example"]
    ids = [f"{r['r']}/{r['n']}" for r in items]
    hashes = [hashlib.sha1(text_of(r).encode()).hexdigest()[:12] for r in items]

    old = {}
    if (DATA / "embeddings.json").exists() and (DATA / "embeddings.npy").exists():
        meta = json.loads((DATA / "embeddings.json").read_text())
        if meta.get("model") == a.model and meta.get("dims") == DIMS:
            vecs = np.load(DATA / "embeddings.npy")
            old = {(i, h): vecs[n] for n, (i, h) in enumerate(zip(meta["ids"], meta["hashes"]))}

    out = np.zeros((len(items), DIMS), dtype=np.float16)
    todo = []
    for n, key in enumerate(zip(ids, hashes)):
        if key in old:
            out[n] = old[key]
        else:
            todo.append(n)
    print(f"{len(items)} items, {len(items) - len(todo)} reused, {len(todo)} to embed", file=sys.stderr)
    for start in range(0, len(todo), BATCH):
        chunk = todo[start:start + BATCH]
        out[chunk] = embed(a.ollama, a.model, [text_of(items[n]) for n in chunk], "search_document: ")
        if start // BATCH % 20 == 0:
            print(f"  {start + len(chunk)}/{len(todo)}", file=sys.stderr, flush=True)

    np.save(DATA / "embeddings.npy", out)
    (DATA / "embeddings.json").write_text(json.dumps({"model": a.model, "dims": DIMS, "ids": ids, "hashes": hashes}))
    print(f"wrote {out.shape} -> data/embeddings.npy", file=sys.stderr)


if __name__ == "__main__":
    main()
