#!/usr/bin/env python3
"""Fetch the tweakcn theme presets and their search metadata into data/themes.json.

  python3 fetch-themes.py

Sources (attributed in the output):
  - tokens: github.com/jnsahaj/tweakcn utils/theme-presets.ts (Apache-2.0)
  - description, keywords, vibes: github.com/Jpisnice/shadcn-ui-mcp-server all_41_themes_metadata.json (MIT)
The presets file is TypeScript; it is a plain object literal, so it is turned into JSON by quoting bare keys and
single-quoted values and dropping trailing commas. Fails loudly if that stops holding.
"""

import json
import re
import urllib.request
from pathlib import Path

PRESETS = "https://raw.githubusercontent.com/jnsahaj/tweakcn/main/utils/theme-presets.ts"
META = ("https://raw.githubusercontent.com/Jpisnice/shadcn-ui-mcp-server/master/"
        "src/tools/tweakcn/assets_function/all_41_themes_metadata.json")
OUT = Path(__file__).resolve().parent.parent / "data" / "themes.json"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "ui-indexador"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def ts_object_to_json(ts):
    body = ts[ts.index("= {") + 2:ts.rstrip().rindex("}") + 1]
    body = re.sub(r"(?m)^\s*//[^\n]*", "", body)
    body = re.sub(r":\s*'((?:[^'\\]|\\.)*)'", lambda m: ": " + json.dumps(m.group(1)), body)
    body = re.sub(r'(?m)^(\s*)([A-Za-z_$][\w$]*)\s*:', r'\1"\2":', body)
    body = re.sub(r",(\s*[}\]])", r"\1", body)
    return json.loads(body)


def main():
    presets = ts_object_to_json(get(PRESETS))
    meta = json.loads(get(META)).get("themes", {})
    themes = []
    for slug, p in presets.items():
        m = meta.get(slug, {})
        light = p["styles"].get("light", {})
        themes.append({"name": slug, "label": p.get("label", slug), "description": m.get("description", ""),
                       "keywords": m.get("keywords", []), "vibes": m.get("vibes", []),
                       "primary": m.get("primaryColor") or light.get("primary", ""),
                       "fonts": {k: light[k] for k in ("font-sans", "font-serif", "font-mono") if light.get(k)},
                       "radius": light.get("radius", ""), "light": light, "dark": p["styles"].get("dark", {})})
    OUT.write_text(json.dumps({"source": {"tokens": f"{PRESETS} (Apache-2.0, tweakcn)",
                                          "metadata": f"{META} (MIT)"},
                               "themes": themes}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(themes)} themes ({sum(1 for t in themes if t['vibes'])} with vibes) -> {OUT}")


if __name__ == "__main__":
    main()
