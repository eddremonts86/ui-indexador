#!/usr/bin/env python3
"""Add a shadcn registry the official directory does not list (yours, or a small one) to the index.

  add-registry.py @name https://site.com/r/{name}.json [--homepage URL] [--description TEXT]
  add-registry.py --list
  add-registry.py --remove @name

The URL is the registry's item template, the same shape as in components.json ("registries"):
{name} is replaced by "registry" for the index and by an item name for each item. The registry is checked
before it is saved: its index must answer with at least one item. It joins the index on the next
refresh (refresh.sh, or the daily schedule).
"""

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

EXTRA = Path(__file__).resolve().parent.parent / "data" / "extra-registries.json"


def load():
    return json.loads(EXTRA.read_text()) if EXTRA.exists() else []


def save(rows):
    EXTRA.write_text(json.dumps(sorted(rows, key=lambda r: r["name"]), indent=1, ensure_ascii=False) + "\n")


def check(url):
    """The registry index, or SystemExit with what is wrong."""
    req = urllib.request.Request(url.replace("{name}", "registry"), headers={"User-Agent": "ui-indexador"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read().decode("utf-8", "replace"))
    except Exception as e:
        raise SystemExit(f"{url.replace('{name}', 'registry')} did not answer with JSON: {e}")
    items = data.get("items") if isinstance(data, dict) else None
    if not items:
        raise SystemExit("the registry index has no items (expected a registry.json with an items list)")
    return data, items


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("name", nargs="?")
    ap.add_argument("url", nargs="?")
    ap.add_argument("--homepage", default="")
    ap.add_argument("--description", default="")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--remove", metavar="@name")
    a = ap.parse_args()
    rows = load()

    if a.list:
        for r in rows:
            print(f"{r['name']:<28} {r['url']}")
        print(f"{len(rows)} hand-added registries")
        return
    if a.remove:
        keep = [r for r in rows if r["name"] != a.remove]
        if len(keep) == len(rows):
            raise SystemExit(f"{a.remove} is not in {EXTRA.name}")
        save(keep)
        print(f"removed {a.remove}; it leaves the index on the next refresh")
        return
    if not (a.name and a.url):
        ap.error("give @name and the registry URL template, or --list / --remove")
    if not re.fullmatch(r"@[a-z0-9][a-z0-9._-]*", a.name):
        raise SystemExit("name must look like @my-registry (lowercase, starting with @)")
    if not re.fullmatch(r"https://[^\s]+\{name\}[^\s]*", a.url):
        raise SystemExit("url must be https and contain {name}, e.g. https://site.com/r/{name}.json")

    data, items = check(a.url)
    homepage = a.homepage or data.get("homepage") or re.match(r"https://[^/]+", a.url).group(0)
    entry = {"name": a.name, "url": a.url, "homepage": homepage,
             "description": a.description or data.get("description", "") or data.get("name", "")}
    rows = [r for r in rows if r["name"] != a.name] + [entry]
    save(rows)
    print(f"added {a.name}: {len(items)} items, homepage {homepage}. It joins the index on the next refresh "
          f"(bash refresh.sh).", file=sys.stderr)


if __name__ == "__main__":
    main()
