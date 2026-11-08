#!/usr/bin/env python3
"""Survey what the shadcn registries actually contain, for a given kind of page.

  survey-registries.py items     --out DIR [--min-score 0]   # every item, tagged by section kind
  survey-registries.py sitemaps  --out DIR                   # robots.txt -> sitemaps -> preview URLs
  survey-registries.py classify  --out DIR [--kinds hero,about]  # fetch each item's source, tag its layout
  survey-registries.py catalog   --out ../data [--deep]           # EVERY item -> catalog.json (what the API serves)

Run them in order; each step reads the previous step's JSON from DIR. Inputs: the ranked index in
../data/registries.json (rank-registries.py) and the live directory at ui.shadcn.com/r/registries.json.

Why three sources: a registry's registry.json says what it exports (name, description, categories);
its sitemap says where each block's preview page lives; each item's JSON carries the full source, so
the layout can be read from the code for every item, not only the ones someone screenshotted.
The code tags are heuristics (an avatar row reads as "person"): use them to narrow a shortlist, then
look at the blocks (render them, see apps/ui-indexador) before choosing.
Standard library only. Surveyed for a developer profile site on 2026-11-06: 14,775 items, 4,062 classified.
"""

import argparse
import concurrent.futures as cf
import json
import re
import sys
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
DIRECTORY = "https://ui.shadcn.com/r/registries.json"
UA = {"User-Agent": "Mozilla/5.0 (ui-indexador registry survey)"}
SKIP_TYPES = {"registry:style", "registry:theme", "registry:lib", "registry:hook", "registry:font"}
KINDS = [  # section kind by item name/title/description/categories; first match wins
    ("hero", r"hero"),
    ("portfolio/profile", r"portfolio|profile|personal|resume|\bcv\b|\bbio\b|about[-_ ]?me|developer[-_ ]?card"),
    ("about", r"\babout"), ("projects/showcase", r"project|showcase|case[-_ ]?stud|work[-_ ]?grid|gallery|bento"),
    ("timeline/experience", r"timeline|experience|career|journey|changelog"),
    ("testimonials", r"testimonial|review|quote"), ("pricing", r"pricing|plans?\b"),
    ("skills/logos", r"skill|tech[-_ ]?stack|logo[-_ ]?cloud|marquee|logos"), ("faq", r"\bfaq"),
    ("contact/cta", r"contact|cta|call[-_ ]?to[-_ ]?action|newsletter"), ("nav/header", r"navbar|header|nav[-_ ]?bar|navigation"),
    ("footer", r"footer"), ("stats", r"\bstats?\b|metric|counter"),
]
FEATURES = {  # code feature -> regex over the item's source
    "split": r"(?:md|lg|xl):grid-cols-(?:2|12)|(?:md|lg):flex-row|grid-cols-\[",
    "centered": r"\btext-center\b.*\bmx-auto\b|\bmx-auto\b.*\btext-center\b",
    "image": r"<img\b|<Image\b|\.(?:jpe?g|png|webp|avif)[\"']",
    "person": r"avatar|portrait|headshot|profile[-_ ]?(?:pic|photo|image)|Avatar",
    "video": r"<video\b|youtube|vimeo", "shader3d": r"three|@react-three|webgl|shader|<canvas|\bogl\b",
    "marquee": r"marquee|animate-scroll|infinite[-_ ]?scroll", "cards": r"(?:md|lg):grid-cols-(?:3|4)",
    "timeline": r"timeline|border-l\b.*before:", "bento": r"row-span-2|col-span-2",
    "glass": r"backdrop-blur", "gradtext": r"bg-clip-text|text-transparent",
    "wide": r"max-w-(?:6xl|7xl|screen-xl|screen-2xl)", "narrow": r"max-w-(?:xl|2xl|3xl|prose)\b",
    "motion": r"framer-motion|motion/react|gsap",
}
FEATURES = {k: re.compile(v, re.I | re.S) for k, v in FEATURES.items()}


def get(url, as_json=True, timeout=15):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        body = r.read().decode("utf-8", "replace")
    return json.loads(body) if as_json else body


def pool(fn, xs, n=24):
    with cf.ThreadPoolExecutor(n) as ex:
        return list(ex.map(fn, xs))


def sources():
    """name -> {url, ...}: the shadcn directory plus the hand-added registries (data/extra-registries.json)."""
    src = {r["name"]: r for r in get(DIRECTORY, timeout=30)}
    extra = HERE.parent / "data" / "extra-registries.json"
    for e in (json.loads(extra.read_text()) if extra.exists() else []):
        src.setdefault(e["name"], e)
    return src


def items(out, min_score):
    ranked = {r["name"]: r for r in json.loads((HERE.parent / "data" / "registries.json").read_text()) if r["score"] >= min_score}
    src = sources()

    def one(name):
        try:
            d = get(src[name]["url"].replace("{name}", "registry"))
        except Exception:
            return []
        rows = []
        for it in d.get("items", []):
            if it.get("type") in SKIP_TYPES:
                continue
            txt = " ".join([it.get("name", ""), it.get("title") or "", it.get("description") or "",
                            " ".join(it.get("categories") or [])]).lower()
            kind = next((k for k, pat in KINDS if re.search(pat, txt)), None)
            if kind:
                r = ranked[name]
                rows.append({"registry": name, "name": it.get("name"), "kind": kind, "type": it.get("type"),
                             "desc": (it.get("description") or it.get("title") or "")[:160], "url": src[name]["url"],
                             "stars": r["stars"], "license": r["license"], "homepage": r["homepage"]})
        return rows

    rows = [r for rs in pool(one, [n for n in ranked if n in src]) for r in rs]
    (out / "items.json").write_text(json.dumps(rows, indent=1))
    print(f"{len(rows)} section items in {len({r['registry'] for r in rows})} registries:", Counter(r["kind"] for r in rows).most_common())


def sitemaps(out):
    regs = {r["registry"]: r["homepage"] for r in json.loads((out / "items.json").read_text())}
    preview = re.compile(r"preview|/view/|/blocks?/|/r/|/demo", re.I)

    def walk(sm, seen):
        if sm in seen or len(seen) > 12:
            return []
        seen.add(sm)
        try:
            locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", get(sm, as_json=False))
        except Exception:
            return []
        return [u for loc in locs for u in (walk(loc, seen) if loc.endswith(".xml") else [loc])]

    def one(item):
        name, home = item
        base = "{0.scheme}://{0.netloc}".format(urllib.parse.urlparse(home))
        try:
            sms = re.findall(r"(?im)^\s*sitemap:\s*(\S+)", get(base + "/robots.txt", as_json=False))
        except Exception:
            sms = []
        urls = [u for s in (sms or [base + "/sitemap.xml"]) for u in walk(s, set())]
        return {"registry": name, "urls_total": len(urls), "preview_like": [u for u in urls if preview.search(u)][:2000]}

    res = pool(one, list(regs.items()), 20)
    (out / "sitemaps.json").write_text(json.dumps(res, indent=1))
    print(f"{sum(1 for r in res if r['urls_total'])}/{len(res)} registries have a sitemap; "
          f"{sum(len(r['preview_like']) for r in res)} preview-like URLs")


def classify(out, kinds):
    rows = [r for r in json.loads((out / "items.json").read_text()) if not kinds or r["kind"] in kinds]

    def one(r):
        try:
            d = get(r["url"].replace("{name}", r["name"]))
        except Exception:
            return None
        code = "\n".join(f.get("content") or "" for f in d.get("files", []))
        if not code:
            return None
        f = {k: bool(p.search(code)) for k, p in FEATURES.items()}
        if r["kind"] == "timeline/experience":
            lay = "timeline" if f["timeline"] else "card-grid" if f["cards"] else "list-rows"
        elif r["kind"] == "projects/showcase":
            lay = "bento-grid" if f["bento"] else "card-grid" if f["cards"] else "horizontal-strip" if f["marquee"] else "list-rows"
        elif f["shader3d"]:
            lay = "shader-or-3d-background"
        elif f["video"]:
            lay = "video"
        elif f["split"]:
            lay = "split-text-portrait" if f["person"] else "split-text-media" if f["image"] else "split-text-only"
        elif f["centered"]:
            lay = "centered-text" + ("+media" if f["image"] else "")
        else:
            lay = "text-only-left" if not f["image"] else "media-other"
        return {**r, "layout": lay, **f}

    res = [x for x in pool(one, rows, 32) if x]
    (out / "classified.json").write_text(json.dumps(res, indent=1))
    print(f"classified {len(res)}/{len(rows)}")
    for k in sorted({x["kind"] for x in res}):
        print(f"  {k}:", Counter(x["layout"] for x in res if x["kind"] == k).most_common())


# Every item, not only page sections: the taxonomy for the catalog. First match on name/title/description/categories.
CATALOG_KINDS = [
    ("hero", r"\bhero"), ("pricing", r"pricing|\bplans?\b"), ("testimonials", r"testimonial|review|quote"),
    ("faq", r"\bfaq"), ("features", r"\bfeatures?\b|benefit"), ("logos/marquee", r"logo|marquee|brand[-_ ]?cloud"),
    ("stats", r"\bstats?\b|metric|counter|kpi"), ("team", r"\bteam\b|member"), ("blog", r"\bblog|article|\bpost\b"),
    ("contact/cta", r"contact|\bcta\b|call[-_ ]?to[-_ ]?action|newsletter|waitlist|subscribe"),
    ("footer", r"footer"), ("nav/header", r"navbar|header|nav[-_ ]?bar|navigation|\bmenu|breadcrumb|\bdock\b"),
    ("auth", r"login|sign[-_ ]?in|sign[-_ ]?up|register|\bauth|\botp\b|password|forgot"),
    ("dashboard", r"dashboard|admin|analytics"), ("sidebar", r"sidebar"),
    ("table", r"\btable|data[-_ ]?grid|datatable"), ("chart", r"chart|graph|sparkline|heatmap"),
    ("calendar", r"calendar|scheduler|date[-_ ]?picker|\bevent"),
    ("ecommerce", r"product|\bcart\b|checkout|\bshop|\bstore\b|\border"),
    ("chat/ai", r"\bchat|message|\bai\b|prompt|assistant|conversation|\bllm"),
    ("editor", r"editor|markdown|rich[-_ ]?text|code[-_ ]?block|\bcode\b"),
    ("file/upload", r"upload|dropzone|\bfile"), ("kanban/board", r"kanban|\bboard\b|sortable|drag"),
    ("settings/account", r"settings|account|billing|preferences"),
    ("error/empty", r"\b404\b|\berror|not[-_ ]?found|maintenance|empty[-_ ]?state|coming[-_ ]?soon"),
    ("onboarding/steps", r"onboarding|stepper|wizard|\bsteps?\b"),
    ("portfolio/profile", r"portfolio|profile|personal|resume|\bcv\b|\bbio\b|developer"),
    ("about", r"\babout"), ("projects/showcase", r"project|showcase|case[-_ ]?stud|bento"),
    ("timeline/experience", r"timeline|experience|career|journey|changelog"),
    ("notification", r"toast|notification|\balert|banner|sonner"),
    ("overlay", r"dialog|modal|drawer|\bsheet|popover|tooltip|dropdown|command|context[-_ ]?menu|hover[-_ ]?card"),
    ("form", r"\bform|input|select|checkbox|radio|switch|slider|textarea|combobox|\bfield|\btag"),
    ("media", r"image|video|gallery|carousel|avatar|\baudio|player"), ("map", r"\bmap\b|globe|geo"),
    ("button", r"button|\bbtn"), ("card", r"\bcard"), ("navigation/tabs", r"\btabs?\b|pagination|accordion|collapsible|tree"),
    ("loader/skeleton", r"loader|loading|spinner|skeleton|progress"),
    ("text-effects", r"\btext|typing|typewriter|\bword|letter|heading|number|ticker"),
    ("background/effects", r"background|particle|aurora|grid[-_ ]?(?:pattern|background)|beam|spotlight|shader|gradient|noise|meteor|glow|ripple|\bdots?\b"),
]
CATALOG_KINDS = [(k, re.compile(p, re.I)) for k, p in CATALOG_KINDS]
ICON_ITEM = re.compile(r"\bicons?\b|\blogos?\b|.*-icon", re.I)
CATALOG_SKIP = SKIP_TYPES | {"registry:style", "registry:item", "registry:file", "registry:page", "registry:base", "registry:internal"}


def layout_of(kind, f):
    if kind == "timeline/experience":
        return "timeline" if f["timeline"] else "card-grid" if f["cards"] else "list-rows"
    if kind == "projects/showcase":
        return "bento-grid" if f["bento"] else "card-grid" if f["cards"] else "horizontal-strip" if f["marquee"] else "list-rows"
    if f["shader3d"]:
        return "shader-or-3d-background"
    if f["video"]:
        return "video"
    if f["split"]:
        return "split-text-portrait" if f["person"] else "split-text-media" if f["image"] else "split-text-only"
    if f["centered"]:
        return "centered-text" + ("+media" if f["image"] else "")
    if f["bento"]:
        return "bento-grid"
    if f["cards"]:
        return "card-grid"
    return "text-only-left" if not f["image"] else "media-other"


def catalog(out, min_score, deep, force=False):
    """Every installable item of every ranked registry -> out/catalog.json (metadata, no source code).
    --deep also fetches each block's source to tag its layout and visual features."""
    ranked = {r["name"]: r for r in json.loads((HERE.parent / "data" / "registries.json").read_text()) if r["score"] >= min_score}
    src = sources()

    def one(name):
        try:
            d = get(src[name]["url"].replace("{name}", "registry"), timeout=30)
        except Exception:
            return []
        rows, icon_registry = [], ranked[name].get("category") == "icons & logos"
        for it in d.get("items", []):
            typ = it.get("type") or ""
            if typ in CATALOG_SKIP or not it.get("name"):
                continue
            cats = it.get("categories") or []
            txt = " ".join([it["name"], it.get("title") or "", it.get("description") or "", " ".join(cats)])
            if icon_registry or ICON_ITEM.search(" ".join(cats)) or ICON_ITEM.fullmatch(it["name"]):
                kind = "icon/logo"  # hidden from searches unless asked for: icon sets would drown every query
            else:
                kind = next((k for k, pat in CATALOG_KINDS if pat.search(txt)), "block" if typ == "registry:block" else "component")
            # Compact on purpose (100k+ rows): registry facts (stars, licence, homepage, item URL) are joined from
            # registries.json at query time, and empty fields are left out.
            row = {"r": name, "n": it["name"], "t": typ.removeprefix("registry:"), "k": kind}
            title, desc = it.get("title") or "", (it.get("description") or "")[:140]
            if title and title.lower().replace(" ", "-") != it["name"]:
                row["ti"] = title
            if desc:
                row["d"] = desc
            if cats:
                row["c"] = cats[:5]
            if it.get("dependencies"):
                row["dep"] = it["dependencies"][:8]
            rows.append(row)
        return rows

    rows = [r for rs in pool(one, [n for n in ranked if n in src]) for r in rs]
    print(f"{len(rows)} items in {len({r['r'] for r in rows})} registries", file=sys.stderr)
    if deep:
        def classify_one(r):
            if r["t"] != "block":
                return r
            try:
                d = get(src[r["r"]]["url"].replace("{name}", r["n"]))
                code = "\n".join(f.get("content") or "" for f in d.get("files", []))
            except Exception:
                return r
            if code:
                f = {k: bool(p.search(code)) for k, p in FEATURES.items()}
                r["lay"], r["f"] = layout_of(r["k"], f), [k for k, v in f.items() if v]
            return r
        rows = pool(classify_one, rows, 32)
        print(f"layout tagged for {sum(1 for r in rows if 'lay' in r)}", file=sys.stderr)
    prev = out / "catalog.json"
    if prev.exists() and not force:
        before = len(json.loads(prev.read_text()).get("items", []))
        if len(rows) < 0.8 * before:  # a network blip or a dead directory must not wipe a good index overnight
            raise SystemExit(f"crawl found {len(rows)} items, fewer than 80% of the current {before}; "
                             "kept the old catalog (rerun with --force if the drop is real)")
    (out / "catalog.json").write_text(json.dumps({"built": __import__("datetime").date.today().isoformat(),
                                                  "items": rows}, ensure_ascii=False, separators=(",", ":")))
    print(Counter(r["k"] for r in rows).most_common(), file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("step", choices=["items", "sitemaps", "classify", "catalog"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--min-score", type=float, default=0)
    ap.add_argument("--force", action="store_true", help="catalog: write even if far fewer items were found")
    ap.add_argument("--deep", action="store_true", help="catalog: also fetch block sources to tag layouts")
    ap.add_argument("--kinds", default="", help="comma list of section kinds for classify (default: all)")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    {"items": lambda: items(out, a.min_score), "sitemaps": lambda: sitemaps(out),
     "classify": lambda: classify(out, set(filter(None, a.kinds.split(",")))),
     "catalog": lambda: catalog(out, a.min_score, a.deep, a.force)}[a.step]()


if __name__ == "__main__":
    main()
