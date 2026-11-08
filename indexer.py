"""The queries behind both front doors (server.py = HTTP, mcp_server.py = MCP). Pure functions over data/.

Data files (see README for how each is made):
  catalog.json     every installable item of every ranked shadcn registry (scripts/survey-registries.py catalog)
  registries.json  the ranked registries (scripts/rank-registries.py)
  survey/*.csv     hand-classified blocks with a fit score (the 2026-11-06 surveys)
  sites/, blocks/  captured screenshots; INDEX.md the curated pattern notes
  themes.json      tweakcn theme presets with vibes (scripts/fetch-themes.py)
"""

import csv
import json
import os
import re
import urllib.request
from functools import lru_cache
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"
MAX_LIMIT = 500


def _mtime(name):
    p = DATA / name
    return p.stat().st_mtime if p.exists() else 0


@lru_cache(maxsize=4)
def _json(name, mtime):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def load(name):
    """A data file, re-read only when it changes on disk (a rebuilt catalog shows up without a restart)."""
    if not (DATA / name).exists():
        hint = {"catalog.json": "python3 scripts/survey-registries.py catalog --deep --out data",
                "themes.json": "python3 scripts/fetch-themes.py"}.get(name, "")
        raise FileNotFoundError(f"data/{name} is missing. Build it: {hint}".strip())
    return _json(name, _mtime(name))


def clamp(limit, default=50):
    try:
        return max(1, min(int(limit or default), MAX_LIMIT))
    except (TypeError, ValueError):
        return default


def _eq(value, wanted):
    return not wanted or str(value or "").lower() == str(wanted).lower()


def _words(q):
    return [w for w in str(q or "").lower().split() if w]


def _has_words(text, words):
    """Every query word starts a word in text ("air" finds "airline", "airline" does not find "hairline")."""
    return all(re.search(r"(?<![a-z0-9])" + re.escape(w), text) for w in words)


# ── registries ────────────────────────────────────────────────────────────────

def registries(category=None, q=None, limit=50):
    rows = [r for r in load("registries.json") if _eq(r.get("category"), category)
            and all(w in f"{r['name']} {r.get('description', '')} {r.get('category', '')}".lower() for w in _words(q))]
    rows.sort(key=lambda r: r.get("score", 0), reverse=True)
    return {"total": len(rows), "items": rows[:clamp(limit)]}


@lru_cache(maxsize=2)
def _registry_facts(mtime):
    return {r["name"]: r for r in load("registries.json")}


# ── the catalog: every item ───────────────────────────────────────────────────

def _expand(row):
    reg = _registry_facts(_mtime("registries.json")).get(row["r"], {})
    out = {"registry": row["r"], "name": row["n"], "type": row["t"], "kind": row["k"],
           "install": f"npx shadcn@latest add {row['r']}/{row['n']}"}
    for short, long in (("ti", "title"), ("d", "description"), ("c", "categories"), ("dep", "dependencies"),
                        ("lay", "layout"), ("f", "features")):
        if short in row:
            out[long] = row[short]
    out["framework"] = row.get("fw", "react")
    if "m" in row:  # republished by a mirror: its stars and licence describe the mirror, not the author
        out.update({"mirror_of": row["m"], "registry_stars": None, "license": None,
                    "license_note": f"republished by {row['r']}; check {row['m']}'s own licence before use",
                    "homepage": reg.get("homepage")})
    else:
        out.update({"registry_stars": reg.get("stars"), "license": reg.get("license") or None,
                    "homepage": reg.get("homepage")})
    return out


HIDDEN = lambda r: r["k"] == "icon/logo" or r["t"] == "example"  # noise unless asked for by kind/type/include_hidden
SEMANTIC_TOP = 300  # how many nearest items join the keyword hits in a semantic search
OLLAMA = os.environ.get("UI_INDEXER_OLLAMA", "http://localhost:11434")
EMBED_MODEL = os.environ.get("UI_INDEXER_EMBED_MODEL", "nomic-embed-text")


@lru_cache(maxsize=2)
def _vectors(mtime):
    import numpy as np
    meta = json.loads((DATA / "embeddings.json").read_text())
    return np.load(DATA / "embeddings.npy").astype("float32"), {i: n for n, i in enumerate(meta["ids"])}, meta


@lru_cache(maxsize=256)
def _query_vector(q):
    import numpy as np
    body = json.dumps({"model": EMBED_MODEL, "input": ["search_query: " + q], "truncate": True}).encode()
    req = urllib.request.Request(f"{OLLAMA}/api/embed", data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        v = np.asarray(json.load(r)["embeddings"][0], dtype="float32")
    dims = _vectors(_mtime("embeddings.npy"))[0].shape[1]
    v = v[:dims]
    return v / np.linalg.norm(v)


def _similarities(q):
    """{item id: cosine similarity} for every embedded item, or (None, why) when semantic search is unavailable."""
    if not (DATA / "embeddings.npy").exists():
        return None, "no data/embeddings.npy (run scripts/embed-catalog.py)"
    try:
        mat, index, _ = _vectors(_mtime("embeddings.npy"))
        sims = mat @ _query_vector(q.strip().lower())
    except ImportError:
        return None, "numpy is not installed for this Python (pip install -r requirements.txt)"
    except Exception as e:  # Ollama down, model missing: keyword search still works
        return None, f"embedding the query failed ({type(e).__name__}); is Ollama up at {OLLAMA}?"
    return {i: float(sims[n]) for i, n in index.items()}, None


OSI = {"MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "0BSD", "MPL-2.0", "Unlicense"}
MIRRORS = {"@registrydirectory"}  # registries that republish other registries' items as "<source>/<item>"
_FW_DEPS = [("react-native", re.compile(r"^react-native|^expo")), ("solid", re.compile(r"^solid-js|^lucide-solid|^@kobalte")),
            ("vue", re.compile(r"^vue$|^vue@|^@vueuse|^motion-v|/vue\b|^@hugeicons/vue")), ("svelte", re.compile(r"^svelte")),
            ("preact", re.compile(r"^preact")), ("lit", re.compile(r"^lit$|^lit@|^@lit/"))]
_FW_DESC = [("react-native", re.compile(r"react native|\bexpo\b", re.I)), ("vue", re.compile(r"\bvue\b", re.I)),
            ("svelte", re.compile(r"svelte", re.I)), ("solid", re.compile(r"\bsolid(js)?\b(?! colou?r)", re.I)),
            ("angular", re.compile(r"angular", re.I)), ("terminal", re.compile(r"opentui|terminal ui|\btui\b", re.I))]


def _registry_framework(reg):
    """react unless the registry says it is for something else (a list that includes React stays react)."""
    text = f"{reg.get('name', '')} {reg.get('description', '')}"
    if re.search(r"\breact\b(?! native)", text, re.I):
        return "react"
    return next((fw for fw, pat in _FW_DESC if pat.search(text)), "react")


@lru_cache(maxsize=2)
def _catalog(cat_mtime, reg_mtime):
    """The catalog as served: mirror copies of an indexed source item dropped, remaining mirrors flagged with
    their source ("m"), and a framework ("fw") from the item's dependencies, else from its registry."""
    cat = load("catalog.json")
    facts = _registry_facts(reg_mtime)
    present = {(r["r"], r["n"]) for r in cat["items"] if r["r"] not in MIRRORS}
    reg_fw = {name: _registry_framework(reg) for name, reg in facts.items()}
    rows = []
    for r in cat["items"]:
        r = dict(r)
        if r["r"] in MIRRORS and "/" in r["n"]:
            source, item = r["n"].split("/", 1)
            if (f"@{source}", item) in present:
                continue  # the same item is indexed under its own registry
            r["m"] = f"@{source}"
        deps = r.get("dep", [])
        r["fw"] = next((fw for fw, pat in _FW_DEPS if any(pat.search(d) for d in deps)),
                       reg_fw.get(r.get("m") or r["r"]) or reg_fw.get(r["r"], "react"))
        rows.append(r)
    return {**cat, "items": rows}


def catalog():
    return _catalog(_mtime("catalog.json"), _mtime("registries.json"))


def _licence(r, facts):
    """An OSI licence we can vouch for, or None. A mirror's registry licence is the mirror's, not the source's."""
    if "m" in r:
        return None
    lic = facts.get(r["r"], {}).get("license") or ""
    return lic if lic in OSI else None


def items(q=None, kind=None, type=None, registry=None, layout=None, feature=None, dep=None, limit=50, offset=0,
          mode="auto", include_hidden=False, framework="react", osi_only=False):
    """Search every indexed component and block. All filters are optional and combine (AND).

    mode: "auto" (semantic when available, else keyword), "semantic" or "keyword". Semantic search embeds q with
    the local Ollama and finds items by meaning ("buy flight tickets" finds booking, checkout, boarding pass);
    keyword search needs every word of q to start a word in the item's name, title, description or categories.
    Icons/logos and examples are hidden unless kind/type asks for them or include_hidden is set.
    framework: react (default), vue, svelte, solid, react-native, preact, lit, angular, terminal, or "any".
    osi_only: only items whose registry has an OSI licence (mirrors are excluded: their licence is unverified).
    Copies a mirror republishes of an item indexed under its own registry are not returned twice."""
    cat = catalog()
    facts = _registry_facts(_mtime("registries.json"))
    words = _words(q)
    show_hidden = include_hidden in (True, "1", "true", "yes") or kind == "icon/logo" or type == "example"
    sims, note = (None, None)
    if words and mode != "keyword":
        sims, note = _similarities(q)
        if sims is None and mode == "semantic":
            raise ValueError(f"semantic search unavailable: {note}")

    def relevance(r):  # a word in the name or kind counts more than one in the description
        return sum(3 * (w in r["n"].lower()) + 3 * (w in r["k"]) + 2 * (w in r.get("ti", "").lower()) for w in words)

    keyword_hits, nearest = [], []
    for r in cat["items"]:
        if not show_hidden and HIDDEN(r):
            continue
        if framework and framework != "any" and r.get("fw", "react") != framework:
            continue
        if osi_only in (True, "1", "true", "yes") and not _licence(r, facts):
            continue
        if not (_eq(r["k"], kind) and _eq(r["t"], type) and _eq(r["r"], registry) and _eq(r.get("lay"), layout)):
            continue
        if feature and feature.lower() not in r.get("f", []):
            continue
        if dep and not any(dep.lower() in d.lower() for d in r.get("dep", [])):
            continue
        if not words:
            keyword_hits.append(r)
            continue
        hay = f"{r['n']} {r.get('ti', '')} {r.get('d', '')} {' '.join(r.get('c', []))} {r['k']}".lower()
        if _has_words(hay, words):
            keyword_hits.append(r)
        elif sims is not None:
            nearest.append(r)

    if sims is None:
        hits = sorted(keyword_hits, key=lambda r: (-relevance(r), "m" in r, -(facts.get(r["r"], {}).get("score") or 0), r["n"]))
        used = "keyword"
    else:
        sim = lambda r: sims.get(f"{r['r']}/{r['n']}", 0.0)
        nearest = sorted(nearest, key=sim, reverse=True)[:SEMANTIC_TOP]
        # Meaning first; a literal keyword match and a strong registry break near-ties.
        rank = lambda r: 0 if "m" in r else (facts.get(r["r"], {}).get("score") or 0)  # a mirror's rank is not the author's
        score = lambda r, kw: (sim(r) + (0.06 if kw else 0) + 0.01 * relevance(r) + 0.0002 * rank(r)
                               - (0.03 if "m" in r else 0))
        ranked = [(score(r, True), r) for r in keyword_hits] + [(score(r, False), r) for r in nearest]
        hits = [r for _, r in sorted(ranked, key=lambda x: -x[0])]
        used = "semantic"
    start = max(0, int(offset or 0))
    out = {"total": len(hits), "mode": used, "built": cat.get("built"),
           "items": [_expand(r) | ({"similarity": round(sims.get(f"{r['r']}/{r['n']}", 0.0), 3)} if sims else {})
                     for r in hits[start:start + clamp(limit)]]}
    if note and words:
        out["note"] = note
    return out


def facets():
    """What the catalog can be filtered by, with counts: kinds, types, layouts, features."""
    from collections import Counter
    cat = catalog()["items"]
    count = lambda key: dict(Counter(r[key] for r in cat if key in r).most_common())
    return {"total": len(cat), "registries": len({r["r"] for r in cat}), "mirrored": sum(1 for r in cat if "m" in r),
            "frameworks": count("fw"), "kinds": count("k"), "types": count("t"),
            "layouts": count("lay"), "features": dict(Counter(f for r in cat for f in r.get("f", [])).most_common())}


# ── the curated layer: hand-scored blocks, captures, notes ───────────────────

@lru_cache(maxsize=2)
def _survey(stamp):
    rows = []
    for f in sorted((DATA / "survey").glob("*.csv")):
        with f.open(encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                try:
                    fit = int(r.get("fit") or 0)
                except ValueError:
                    fit = 0
                rows.append({"registry": r.get("registry", ""), "item": r.get("item") or r.get("item_or_label") or "",
                             "kind": r.get("kind", ""), "layout": r.get("layout", ""), "width": r.get("width", ""),
                             "media": r.get("media", ""), "tone": r.get("tone", ""), "fit": fit, "url": r.get("url", ""),
                             "survey": f.name})
    return rows


def blocks(kind=None, layout=None, tone=None, registry=None, min_fit=0, q=None, limit=100):
    """Hand-classified blocks from the surveys, with a 1-5 fit score (fit was judged for a developer profile)."""
    stamp = tuple(f.stat().st_mtime for f in sorted((DATA / "survey").glob("*.csv")))
    words = _words(q)
    rows = [r for r in _survey(stamp)
            if _eq(r["kind"], kind) and _eq(r["layout"], layout) and _eq(r["tone"], tone) and _eq(r["registry"], registry)
            and r["fit"] >= int(min_fit or 0) and all(w in f"{r['registry']} {r['item']} {r['layout']}".lower() for w in words)]
    rows.sort(key=lambda r: r["fit"], reverse=True)
    return {"total": len(rows), "items": rows[:clamp(limit, 100)]}


def captures(dir=None, kind=None, q=None, limit=MAX_LIMIT):
    """Captured screenshots (1440x900). url is a path on the HTTP server (/files/...)."""
    out = []
    for top in ("sites", "blocks"):
        if dir and dir != top:
            continue
        for p in sorted((DATA / top).rglob("*.jpg")):
            rel = p.relative_to(DATA)
            k = rel.parts[1] if len(rel.parts) > 2 else ("site" if top == "sites" else "unsorted")
            if _eq(k, kind) and all(w in p.stem.lower() for w in _words(q)):
                out.append({"dir": top, "kind": k, "name": p.stem, "url": f"/files/{rel.as_posix()}"})
    return {"total": len(out), "items": out[:clamp(limit, MAX_LIMIT)]}


def notes(name="index.md"):
    files = {"index.md": "INDEX.md", "registries.md": "registries.md"}
    if name not in files:
        raise FileNotFoundError(name)
    return (DATA / files[name]).read_text(encoding="utf-8")


# ── themes ────────────────────────────────────────────────────────────────────

def themes(q=None, vibe=None):
    """tweakcn presets, summarised. q matches name, label, description, keywords and vibes."""
    words = _words(q)
    out = []
    for t in load("themes.json")["themes"]:
        if vibe and vibe.lower() not in [v.lower() for v in t["vibes"]]:
            continue
        hay = f"{t['name']} {t['label']} {t['description']} {' '.join(t['keywords'])} {' '.join(t['vibes'])}".lower()
        if all(w in hay for w in words):
            out.append({k: t[k] for k in ("name", "label", "description", "vibes", "primary", "fonts", "radius")})
    return {"total": len(out), "items": out}


def theme(name):
    """One preset with its full light/dark tokens and ready-to-paste CSS variables."""
    t = next((t for t in load("themes.json")["themes"] if t["name"] == name), None)
    if not t:
        raise FileNotFoundError(f"no theme {name!r}")
    block = lambda sel, toks: sel + " {\n" + "".join(f"  --{k}: {v};\n" for k, v in toks.items()) + "}\n"
    return {**t, "css": block(":root", t["light"]) + block(".dark", t["dark"]),
            "source": load("themes.json")["source"]}


def health():
    out = {"ok": True}
    try:
        out["built"] = load("catalog.json").get("built")
    except FileNotFoundError:
        pass
    for name, fn in (("items", lambda: len(catalog()["items"])), ("registries", lambda: len(load("registries.json"))),
                     ("themes", lambda: len(load("themes.json")["themes"])), ("captures", lambda: captures()["total"])):
        try:
            out[name] = fn()
        except FileNotFoundError as e:
            out["ok"], out[name] = False, str(e)
    return out
