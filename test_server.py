#!/usr/bin/env python3
"""Smoke test: start the HTTP API on a free port and hit every endpoint; list the MCP tools if `mcp` is installed.

  python3 test_server.py        (needs data/catalog.json: scripts/survey-registries.py catalog --out data)
"""

import json
import threading
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import urlopen

from server import Handler

srv = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{srv.server_address[1]}"


def get(path):
    with urlopen(base + path) as r:
        return r.status, r.headers.get("Content-Type"), r.read()


def js(path):
    return json.loads(get(path)[2])


h = js("/health")
assert h.get("built"), "health carries the crawl date"
status, ctype, _ = get("/")
assert status == 200 and (ctype.startswith("text/html") or ctype.startswith("application/json")), ctype
assert h["ok"] and h["items"] > 10000 and h["registries"] > 0 and h["themes"] > 0, h

heroes = js("/items?kind=hero&limit=5")
assert heroes["total"] > 100 and all(i["kind"] == "hero" and i["install"].startswith("npx shadcn@latest add @")
                                     for i in heroes["items"]), heroes["items"][:1]
login = js("/items?q=login+form&type=block")["items"]
assert login and all(i["type"] == "block" for i in login)
assert js("/items?dep=recharts&limit=3")["items"], "dep filter"
page2 = js("/items?kind=hero&limit=5&offset=5")["items"]
assert page2 and page2[0]["name"] != heroes["items"][0]["name"]

assert not any(i["kind"] == "icon/logo" or i["type"] == "example" for i in js("/items?q=seat&limit=50")["items"])
assert js("/items?kind=icon/logo&limit=1")["total"] > 1000, "icons reachable when asked"
assert js("/items?q=seat&include_hidden=1")["total"] > js("/items?q=seat")["total"]
kw = js("/items?q=pricing&mode=keyword&limit=3")
assert kw["mode"] == "keyword"
sem = js("/items?q=buy+flight+tickets&limit=10")
if sem["mode"] == "semantic":  # needs data/embeddings.npy, numpy and Ollama; otherwise it says why
    assert sem["items"] and all("similarity" in i for i in sem["items"]), sem
else:
    print(f"semantic not checked: {sem.get('note')}")

vue = js("/items?q=gradient+text&framework=vue&limit=5")["items"]
assert vue and all(i["framework"] == "vue" for i in vue)
assert all(i["framework"] == "react" for i in js("/items?q=gradient+text&limit=20")["items"]), "react by default"
osi = js("/items?q=faq&osi_only=1&limit=30")["items"]
assert osi and all(i["license"] in ("MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "0BSD", "MPL-2.0", "Unlicense")
                   and "mirror_of" not in i for i in osi)
mirrors = [i for i in js("/items?q=hero&limit=100")["items"] if "mirror_of" in i]
assert all(i["license"] is None and i["registry_stars"] is None for i in mirrors), "a mirror never shows its own licence"
seen = [(i["registry"], i["name"]) for i in js("/items?q=navbar&limit=200")["items"]]
assert not any(r == "@registrydirectory" and ("@" + n.split("/")[0], n.split("/", 1)[1]) in seen for r, n in seen), "no mirror copies"

f = js("/facets")
assert f["kinds"] and f["types"], f.keys()

regs = js("/registries?limit=5")["items"]
assert len(regs) == 5 and regs[0]["score"] >= regs[-1]["score"]

assert all(b["fit"] >= 4 for b in js("/blocks?kind=hero&min_fit=4")["items"])

caps = js("/captures?dir=blocks&kind=hero")["items"]
if caps:  # screenshots are local only (not in git); a fresh clone has none
    status, ctype, body = get(caps[0]["url"])
    assert status == 200 and ctype == "image/jpeg" and body[:2] == b"\xff\xd8"
else:
    print("no captures in data/: /captures and /files not checked")

minimal = js("/themes?vibe=minimal")["items"]
assert minimal and all("minimal" in t["vibes"] for t in minimal)
t = js(f"/themes/{minimal[0]['name']}")
assert t["css"].startswith(":root {") and ".dark {" in t["css"] and "--primary:" in t["css"]

assert get("/index.md")[1].startswith("text/markdown")

for bad in ("/files/../server.py", "/files/%2e%2e/server.py", "/files/..%2Fserver.py", "/themes/nope", "/nope",
            "/../server.py", "/..%2Fserver.py", "/%2e%2e/indexer.py", "/assets/../../server.py", "/assets/..%2F..%2Fserver.py"):
    try:
        get(bad)
        raise AssertionError(f"{bad} should be 404")
    except HTTPError as e:
        assert e.code == 404, (bad, e.code)

srv.shutdown()

try:
    import asyncio

    import mcp_server

    tools = {t.name for t in asyncio.run(mcp_server.mcp.list_tools())}
    assert {"search_items", "list_facets", "search_themes", "get_theme"} <= tools, tools
    print(f"mcp tools: {sorted(tools)}")
except ImportError:
    print("mcp not installed for this Python: MCP tools not checked")

print(f"ok: {h}")
