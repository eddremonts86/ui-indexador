#!/usr/bin/env python3
"""Rank the shadcn registry directory by proof of use, not by size.

  rank-registries.py [--out DIR] [--min-items 20] [--workers 12]

Reads https://ui.shadcn.com/r/registries.json (the index behind ui.shadcn.com/docs/directory),
keeps registries that are healthy, visible and have at least --min-items items, finds each one's
GitHub repository from its homepage, and adds stars, last push and licence through `gh api`.
Writes registries.json (all fields) and registries.md (per-category tables) to --out.

Why stars: shadcn's own ranking score tracks endpoint health (r=0.84) and item count (r=0.43)
and sits between 81 and 97 for most registries, so it cannot tell a proven library from a
new one. Stars are a rough proxy for use; the repo is auto-detected and can be wrong, so
every row links its homepage and the detected repo for a human to check.
Needs: `gh` logged in. Standard library only.
"""

import argparse
import concurrent.futures as cf
import json
import math
import re
import subprocess
import sys
import urllib.request
from collections import Counter
from pathlib import Path

INDEX = "https://ui.shadcn.com/r/registries.json"
UA = {"User-Agent": "ui-indexador/1.0"}
# Repos that sites link as credits, not as their own source.
NOT_OWN = {"shadcn-ui/ui", "shadcn/ui", "vercel/next.js", "tailwindlabs/tailwindcss", "radix-ui/primitives",
           "facebook/react", "lucide-icons/lucide", "motiondivision/motion", "framer/motion", "vercel/ai",
           "mui/base-ui", "adobe/react-spectrum", "tanstack/table", "recharts/recharts", "shadcn-ui/taxonomy"}
# Hand-checked categories for well-known registries the keyword rules misfile.
OVERRIDES = {"@plate": "editors & text", "@assistant-ui": "ai & chat", "@animate-ui": "motion & effects",
             "@astryx": "general components", "@supabase": "blocks, templates & landing", "@prosekit": "editors & text"}
REPO = re.compile(r"https?://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)")
CATEGORIES = [  # first match wins, order matters
    ("icons & logos", r"\bicons?\b|logos?\b|\bflags?\b|emoji"),
    ("charts, tables & dashboards", r"chart|graph|data ?vi|\btables?\b|dashboard|kpi|analytics"),
    ("ai & chat", r"\bai\b|chat|llm|agent|prompt|assistant"),
    ("editors & text", r"editor|rich text|markdown|wysiwyg"),
    ("forms & inputs", r"\bforms?\b|\binputs?\b|date ?picker|calendar|upload"),
    ("maps & geo", r"\bmaps?\b|geo"),
    ("3d, canvas & shaders", r"\b3d\b|three|webgl|shader|canvas"),
    ("audio & video", r"sound|audio|video|remotion"),
    ("motion & effects", r"animat|motion|transition|effect|micro-interaction|interactive"),
    ("blocks, templates & landing", r"block|template|section|landing|marketing|page"),
]


def get(url, timeout=12):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def category(desc):
    d = desc.lower()
    for name, pat in CATEGORIES:
        if re.search(pat, d):
            return name
    return "general components"


def find_repo(homepage):
    try:
        html = get(homepage)
    except Exception:
        return None
    counts = Counter()
    for owner, name in REPO.findall(html):
        name = re.sub(r"\.git$", "", name)
        slug = f"{owner}/{name}"
        if slug.lower() in NOT_OWN or owner.lower() in {"sponsors", "orgs", "features", "topics", "apps"}:
            continue
        counts[slug] += 1
    return counts.most_common(1)[0][0] if counts else None


def repo_facts(slug):
    p = subprocess.run(["gh", "api", f"repos/{slug}", "--jq",
                        "[.stargazers_count, .pushed_at, (.license.spdx_id // \"\"), .archived, .full_name] | @json"],
                       capture_output=True, text=True, timeout=30)
    if p.returncode != 0:
        return None
    stars, pushed, lic, archived, full = json.loads(p.stdout)
    return {"repo": full, "stars": stars, "pushed": pushed[:10], "license": lic, "archived": archived}


def extra_registries(known):
    """Registries added by hand (data/extra-registries.json, see add-registry.py) that the directory does not list.
    No directory health check exists for them, so health is what we measure now: 100 if the index answers."""
    path = Path(__file__).resolve().parent.parent / "data" / "extra-registries.json"
    rows = []
    for e in (json.loads(path.read_text()) if path.exists() else []):
        if e["name"] in known:
            continue
        try:
            n = len(json.loads(get(e["url"].replace("{name}", "registry"), timeout=20)).get("items", []))
        except Exception as err:
            print(f"extra registry {e['name']} did not answer ({err}); skipped this run", file=sys.stderr)
            continue
        rows.append({**e, "ranking": {"itemCount": n, "score": 0}, "health": {"score": 100}, "source": "manual"})
    if rows:
        print(f"{len(rows)} hand-added registries", file=sys.stderr)
    return rows


def enrich(r):
    out = {"name": r["name"], "homepage": r.get("homepage", ""), "description": r.get("description", ""),
           "items": r["ranking"]["itemCount"], "shadcn_rank": round(r["ranking"]["score"], 1),
           "health": round(r["health"]["score"], 1),
           "category": OVERRIDES.get(r["name"]) or category(r.get("description", "")),
           "source": r.get("source", "directory")}
    slug = find_repo(out["homepage"]) if out["homepage"] else None
    facts = repo_facts(slug) if slug else None
    out.update(facts or {"repo": "", "stars": 0, "pushed": "", "license": "", "archived": False})
    # Proof of use first (stars, log-scaled), then size, then health as the tie-breaker.
    out["score"] = round(math.log10(out["stars"] + 1) * 20 + math.log10(out["items"] + 1) * 5 + out["health"] / 20, 1)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=".")
    ap.add_argument("--min-items", type=int, default=20)
    ap.add_argument("--workers", type=int, default=12)
    a = ap.parse_args()
    reg = json.loads(get(INDEX, timeout=30))
    keep = [r for r in reg if r.get("ranking") and r.get("health")
            and r["health"].get("status") == "healthy" and not r["health"].get("hidden")
            and r["ranking"]["itemCount"] >= a.min_items]
    print(f"{len(reg)} registries in the directory, {len(keep)} healthy, visible, >= {a.min_items} items", file=sys.stderr)
    keep += extra_registries({r["name"] for r in reg})
    with cf.ThreadPoolExecutor(a.workers) as ex:
        rows = list(ex.map(enrich, keep))
    rows.sort(key=lambda x: -x["score"])
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "registries.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = ["# shadcn registries, ranked by proof of use", "",
             f"Generated by `scripts/rank-registries.py` from {INDEX}. {len(reg)} registries listed; "
             f"{len(keep)} kept (healthy, visible, at least {a.min_items} items). "
             "Score = 20 x log10(stars+1) + 5 x log10(items+1) + health/20. The GitHub repo is auto-detected "
             "from the homepage and can be wrong: check it before relying on the stars.", ""]
    by_cat = {}
    for r in rows:
        by_cat.setdefault(r["category"], []).append(r)
    for cat in sorted(by_cat, key=lambda c: -len(by_cat[c])):
        lines += [f"## {cat} ({len(by_cat[cat])})", "",
                  "| # | Registry | Stars | Items | Health | Licence | Last push | What it is |", "|---|---|---|---|---|---|---|---|"]
        for i, r in enumerate(by_cat[cat][:15], 1):
            repo = f"[{r['stars']:,}](https://github.com/{r['repo']})" if r["repo"] else "no repo found"
            desc = r["description"].replace("|", "/")[:110]
            lines.append(f"| {i} | [{r['name']}]({r['homepage']}) | {repo} | {r['items']} | {r['health']} | "
                         f"{r['license'] or '?'} | {r['pushed'] or '?'} | {desc} |")
        lines.append("")
    (out / "registries.md").write_text("\n".join(lines), encoding="utf-8")
    found = sum(1 for r in rows if r["repo"])
    print(f"repos found for {found}/{len(rows)}; wrote {out / 'registries.json'} and {out / 'registries.md'}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
